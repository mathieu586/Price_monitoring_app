import json
import time
import threading
from pathlib import Path

import customtkinter as ctk
from tkinter import ttk, filedialog
import logging
from src.file_security import check_readable
from src.stores import StoreRegistry
from src.repository import JsonRepository
from src.scraper import Scraper
from src.models import Product, PriceRecord
from CTkMessagebox import CTkMessagebox
from monitor import PriceMonitor

logger = logging.getLogger(__name__)

class Main_window(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Price Monitor")
        self.geometry("1600x700")

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=12)

        self.grid_columnconfigure(0, weight=4, uniform="a")
        self.grid_columnconfigure(1, weight=3, uniform="a")

        try:
            self.repo = JsonRepository("product_data.json")
            self.store_registry = StoreRegistry("stores.json")
        except PermissionError as e:
            CTkMessagebox(title="Błąd dostępu", message=f"Nie można otworzyć pliku danych:\n{e}")
        self.scraper = Scraper()
        self.monitor = PriceMonitor(self.repo, self.scraper)

        self.make_button_rows()
        self.make_product_panel()
        self.make_notification_panel()
        self.refresh_product_entries()


    def make_button_rows(self):
        # PRZYCISKI AKCJI
        self.action_buttons_frame = ctk.CTkFrame(self)
        self.action_buttons_frame.grid(row=2, column=0, sticky="nesw", columnspan=2)

        self.add_button = ctk.CTkButton(master=self.action_buttons_frame, text="Dodaj", height=28, width=40, command=self.open_add_window)
        self.add_button.pack(padx=5, side="left")

        self.edit_button = ctk.CTkButton(master=self.action_buttons_frame, text="Edytuj", height=28, width=40, command=self.open_edit_window)
        self.edit_button.pack(padx=5, side="left")

        self.delete_button = ctk.CTkButton(master=self.action_buttons_frame, text="Usuń", height=28, width=40, command=self.delete_selected_product)
        self.delete_button.pack(padx=5, side="left")

        self.history_button = ctk.CTkButton(master=self.action_buttons_frame, text="Historia", height=28, width=40, command=self.open_history_window)
        self.history_button.pack(padx=5, side="left")

        self.stores_button = ctk.CTkButton(master=self.action_buttons_frame, text="Sklepy", height=28, width=40, command=self.open_stores_window)
        self.stores_button.pack(padx=5, side="left")

        self.check_single_button = ctk.CTkButton(master=self.action_buttons_frame, text="Sprawdź cene", height=28, width=60, command=self.check_single_product)
        self.check_single_button.pack(padx=5, side="left")

        self.export_button = ctk.CTkButton(master=self.action_buttons_frame, text ="Eksport", height=28, width=40, command=self.export_data)
        self.export_button.pack(padx=5, side="left")

        self.import_button = ctk.CTkButton(master=self.action_buttons_frame, text="Import", height=28, width=40,command=self.import_data)
        self.import_button.pack(padx=5, side="left")
        # FILTRY
        self.filter_frame = ctk.CTkFrame(self)
        self.filter_frame.grid(row=1, column=0, columnspan=2, sticky="nesw")

        self.sort_label = ctk.CTkLabel(master=self.filter_frame, text="Sortuj według:")
        self.sort_label.pack(side="left", padx=10)

        self.filter_var = ctk.StringVar(value="date")

        self.filter_date = ctk.CTkRadioButton(master=self.filter_frame, variable=self.filter_var, value="date", text="Data dodania", command=self.refresh_product_entries)
        self.filter_date.pack(side="left")

        self.filter_name = ctk.CTkRadioButton(master=self.filter_frame, variable=self.filter_var, value="name",text="Nazwa", command=self.refresh_product_entries)
        self.filter_name.pack(side="left")

        self.filter_price = ctk.CTkRadioButton(master=self.filter_frame, variable=self.filter_var, value="price", text="Cena", command=self.refresh_product_entries)
        self.filter_price.pack(side="left")

        self.filter_store = ctk.CTkRadioButton(master=self.filter_frame, variable=self.filter_var, value="store", text="Sklep", command=self.refresh_product_entries)
        self.filter_store.pack(side="left")

        self.filter_change = ctk.CTkRadioButton(master=self.filter_frame, variable=self.filter_var, value="change", text="Termin zmiany", command=self.refresh_product_entries)
        self.filter_change.pack(side="left")

        # GŁÓWNE PRZYCISKI
        self.main_buttons_frame = ctk.CTkFrame(self)
        self.main_buttons_frame.grid(row=0, column=0, columnspan=2, sticky="nesw")

        self.start_button = ctk.CTkButton(master=self.main_buttons_frame, text="Start", height=28, width=40, command=self.start_checking_loop)
        self.start_button.pack(side="right", padx=5)

        self.check_all_button = ctk.CTkButton(master=self.main_buttons_frame, text="Sprawdź wszystkie", height=28, width=40, command=lambda: threading.Thread(target=self.check_all_products, daemon=True).start())
        self.check_all_button.pack(side="right", padx=5)

        self.interval_entry = ctk.CTkEntry(master=self.main_buttons_frame, width=60)
        self.interval_entry.pack(side="right", padx=5)

        self.interval_label = ctk.CTkLabel(master=self.main_buttons_frame, text="Interwał [s]:")
        self.interval_label.pack(side="right")

    def make_product_panel(self):
        style = ttk.Style()
        style.theme_use("default")

        style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=25,
                        fieldbackground="#2b2b2b", bordercolor="#343638", borderwidth=0)

        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")

        style.map("Treeview", background=[('selected', '#1f538d')])

        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=3, column=0, sticky="nesw")

        colums = ("Produkt", "Sklep", "Cena", "Najlepsza", "Zmiana_%", "Srednia_cena", "Ilosc_sprawdzen", "Status", "Ostatnie_sprawdzenie")

        self.product_tree = ttk.Treeview(master=self.left_frame, columns=colums, show="headings")
        self.scroll_tree = ctk.CTkScrollbar(master=self.left_frame, command=self.product_tree.yview, bg_color="DARK GREY")
        self.scroll_tree.pack(side="right", fill="y")
        self.product_tree.configure(yscrollcommand=self.scroll_tree.set)
        self.product_tree.pack(expand=True, fill="both")

        self.product_tree.heading("Produkt", text="Produkt")
        self.product_tree.heading("Sklep", text="Sklep")
        self.product_tree.heading("Cena", text="Cena")
        self.product_tree.heading("Najlepsza", text="Najlepsza")
        self.product_tree.heading("Zmiana_%", text="Zmiana %")
        self.product_tree.heading("Srednia_cena", text="Śr. cena")
        self.product_tree.heading("Ilosc_sprawdzen", text="Sprawdzeń")
        self.product_tree.heading("Status", text="Status")
        self.product_tree.heading("Ostatnie_sprawdzenie", text="Ostatnie sprawdzenie")

        self.product_tree.column("Produkt", width=150, anchor="w")
        self.product_tree.column("Sklep", width=90, anchor="center")
        self.product_tree.column("Cena", width=80, anchor="center")
        self.product_tree.column("Najlepsza", width=80, anchor="center")
        self.product_tree.column("Zmiana_%", width=80, anchor="center")
        self.product_tree.column("Srednia_cena", width=90, anchor="center")
        self.product_tree.column("Ilosc_sprawdzen", width=100, anchor="center")
        self.product_tree.column("Status", width=100, anchor="center")
        self.product_tree.column("Ostatnie_sprawdzenie", width=130, anchor="center")

    def add_product_entry(self, product):
        self.product_tree.insert(parent="", index="end", iid=product.id, values=product.get_table_row())

    def clear_product_entries(self):
        for product in self.product_tree.get_children():
            self.product_tree.delete(product)

    def refresh_product_entries(self):
        self.after(0, self.safe_refresh_product_entries)

    def safe_refresh_product_entries(self):
        self.clear_product_entries()
        all_products = self.repo.get_all_products()
        sort_mode = self.filter_var.get()


        if sort_mode == "date":
            all_products.sort(key=lambda x: x.add_time, reverse=True)
        elif sort_mode == "name":
            all_products.sort(key=lambda x: x.name.lower())
        elif sort_mode == "price":
            all_products.sort(key=lambda x: x.price_history[-1].price if x.price_history else float("inf"))
        elif sort_mode == "store":
            all_products.sort(key=lambda x: x.store)
        elif sort_mode == "change":
            all_products.sort(key=lambda x: x.price_history[-1].timestamp if x.price_history else x.add_time, reverse=True)

        for product in all_products:
            self.add_product_entry(product)

    def make_notification_panel(self):
        self.notif_frame = ctk.CTkFrame(self)
        self.notif_frame.grid(row=3, column=1, sticky="nesw")

        self.notif_frame.rowconfigure(0, weight=0)
        self.notif_frame.rowconfigure(1, weight=1)

        self.notif_frame.columnconfigure(0, weight=1)
        self.notif_frame.columnconfigure(1, weight=1)

        self.notif_label = ctk.CTkLabel(master=self.notif_frame, text="Powiadomienia", padx=12, pady=5, font=("Arial", 20))
        self.notif_label.grid(row=0, column=0, sticky="w")

        self.clear_button = ctk.CTkButton(master=self.notif_frame, text="Wyczyść", command=self.clear_notifications)
        self.clear_button.grid(row=0, column=1, sticky="e", padx=5)

        self.notif_box = ctk.CTkTextbox(master=self.notif_frame, state="disabled")
        self.notif_box.grid(row=1, sticky="nesw", columnspan=2, padx=5, pady=5)

    def add_notif_entry(self, notif_content):
        self.after(0, lambda: self.safe_add_notif_entry(notif_content))

    def safe_add_notif_entry(self, notif_content):
        self.notif_box.configure(state="normal")

        self.notif_box.insert(index="end", text=(notif_content+"\n"))

        self.notif_box.see("end")
        self.notif_box.configure(state="disabled")

    def clear_notifications(self):
        self.notif_box.configure(state="normal")
        self.notif_box.delete("1.0", "end")
        self.notif_box.configure(state="disabled")

    def open_add_window(self):
        self.add_window = ctk.CTkToplevel(master=self)
        self.add_window.title("Dodawanie Produktu")
        self.add_window.geometry("520x200")

        self.add_window.transient(self)
        self.add_window.grab_set()
        self.add_window.focus()

       # self.add_window.rowconfigure(0, weight=1)
       # self.add_window.rowconfigure(1, weight=1)
       # self.add_window.rowconfigure(2, weight=1)
       # self.add_window.rowconfigure(3, weight=1)

       # self.add_window.columnconfigure(0, weight=1)
       # self.add_window.columnconfigure(1, weight=1)

        name_label = ctk.CTkLabel(master=self.add_window, text="Nazwa:")
        name_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.name_entry = ctk.CTkEntry(master=self.add_window, width=100)
        self.name_entry.grid(row=0, column=1, sticky="w", pady=10)

        url_label = ctk.CTkLabel(master=self.add_window, text="Link (URL):")
        url_label.grid(row=1, column=0, sticky="w", padx=10, pady=10)

        self.url_entry = ctk.CTkEntry(master=self.add_window, width=350)
        self.url_entry.grid(row=1, column=1, sticky="w", pady=10)

        threshold_label = ctk.CTkLabel(master=self.add_window, text="Próg alarmowy:")
        threshold_label.grid(row=2, column=0, sticky="w", padx=10, pady=10)

        self.threshold_entry = ctk.CTkEntry(master=self.add_window, width=100)
        self.threshold_entry.grid(row=2, column=1, sticky="w", pady=10)

        self.save_product_button = ctk.CTkButton(master=self.add_window, text="Dodaj Produkt", command=self.save_new_product)
        self.save_product_button.grid(row=3, column=0, columnspan=2, pady=20)

    def save_new_product(self):
        name = self.name_entry.get()
        url = self.url_entry.get()
        threshold = self.threshold_entry.get()

        store_config = self.store_registry.detect_store_from_url(url)

        if not url:
            CTkMessagebox(title="Błędne dane", message="Pole URL jest wymagane!")
            return

        if not store_config:
            CTkMessagebox(title="Błąd", message="Nie rozpoznano sklepu dla podanego URL")
            return

        new_product = Product(id=Product.generate_id(), name=name, url=url, store=store_config.name, selector=store_config.selector,
                              check_interval=3600, alert_threshold=float(threshold) if threshold else 0.0)    # check_interval -------------------------------------------

        self.repo.save_product(new_product)
        self.add_product_entry(new_product)
        self.add_notif_entry(f"[SYSTEM] Dodano produkt: {name}")

        self.add_window.destroy()


    def open_edit_window(self):
        selected_product_entry = self.product_tree.selection()

        if not selected_product_entry:
            CTkMessagebox(title="Wybierz produkt", message="Nie zaznaczono produktu do edycji!")
            return

        self.editing_product_id = selected_product_entry[0]
        product = self.repo.get_product_by_id(self.editing_product_id)
        product_name = product.name
        url = product.url
        threshold = product.alert_threshold


        self.edit_window = ctk.CTkToplevel(self)
        self.edit_window.title("Edytowanie Produktu")
        self.edit_window.geometry("520x200")

        self.edit_window.transient(self)
        self.edit_window.grab_set()
        self.edit_window.focus()

        name_label = ctk.CTkLabel(master=self.edit_window, text="Nazwa produktu:")
        name_label.grid(row=0, column=0, sticky="e", padx=10, pady=10)

        self.edit_name_entry = ctk.CTkEntry(master=self.edit_window, width=200)
        self.edit_name_entry.insert(0, product_name)
        self.edit_name_entry.grid(row=0, column=1, sticky="w")

        threshold_label = ctk.CTkLabel(master=self.edit_window, text="Próg alarmowy:")
        threshold_label.grid(row=1, column=0, sticky="e", padx=10, pady=10)

        self.edit_threshold_entry = ctk.CTkEntry(master=self.edit_window, width=200)
        self.edit_threshold_entry.insert(0, threshold)
        self.edit_threshold_entry.grid(row=1, column=1, sticky="w")

        url_label = ctk.CTkLabel(master=self.edit_window, text="URL:")
        url_label.grid(row=2, column=0, sticky="e", padx=10, pady=10)

        self.edit_url_entry = ctk.CTkEntry(master=self.edit_window, width=400)
        self.edit_url_entry.insert(0, url)
        self.edit_url_entry.grid(row=2, column=1, sticky="w")

        self.save_edited_product_button = ctk.CTkButton(master=self.edit_window, text="Zapisz", command=self.save_edited_product)
        self.save_edited_product_button.grid(row=3, columnspan=2)

    def save_edited_product(self):
        new_name = self.edit_name_entry.get()
        new_threshold = self.edit_threshold_entry.get()
        new_url = self.edit_url_entry.get()

        if not new_url:
            CTkMessagebox(title="Błędne dane", message="Pole URL nie może być puste!")
            return

        store_config = self.store_registry.detect_store_from_url(new_url)
        if not store_config:
            CTkMessagebox(title="Błąd rozpoznania sklepu", message="Nie rozpoznano sklepu dla podanego URL!")
            return

        old_product = self.repo.get_product_by_id(self.editing_product_id)
        if not old_product:
            CTkMessagebox(title="Produkt nie istnieje", message="Edytowany produkt nie istnieje w bazie danych!")
            return

        edited_product = Product(
            id=old_product.id,
            name=new_name,
            url=new_url,
            store=store_config.name,
            selector=store_config.selector,
            check_interval=old_product.check_interval,
            alert_threshold=float(new_threshold) if new_threshold else 0.0,
            add_time=old_product.add_time,
            price_history=old_product.price_history
        )

        self.repo.save_product(edited_product)
        self.refresh_product_entries()

        logger.info(f"Pomyślnie zaktualizowano produkt (ID: {old_product.id}, Nazwa: {edited_product.name})")

        self.edit_window.destroy()


    def delete_selected_product(self):
        selected_product_entry = self.product_tree.selection()

        if selected_product_entry:
            product_id = selected_product_entry[0]
            product_name = self.product_tree.item(product_id, "values")[0]

            if self.repo.delete_product(product_id):
                self.product_tree.delete(product_id)

                logger.info(f"Pomyślnie usunięto produkt: {product_name} | id: {product_id}")
                self.add_notif_entry(f"[SYSTEM] Usunięto produkt {product_name}.")
            else:
                logger.info(f"Niepowodzenie przy próbie usunięcia produktu: {product_name} | id: {product_id}")
                CTkMessagebox(title="Błąd", message=f"Nie udało się usunąć produktu:\n{product_name}")
        else:
            CTkMessagebox(title="Nie wybrano produktu", message="Nie wybrano żadnego produktu do usunięcia!")

    def check_single_product(self):
        selected_product_entry = self.product_tree.selection()

        if selected_product_entry:
            product_id = selected_product_entry[0]
            product = self.repo.get_product_by_id(product_id)

            self.monitor.check_product(product, notif_func=self.add_notif_entry)
            self.add_notif_entry(f"[SYSTEM] Sprawdzono produkt {product.name}.")
            self.refresh_product_entries()
        else:
            CTkMessagebox(title="Wybierz produkt", message="Nie wybrano żadnego produktu!")
            return

    def check_all_products(self):
        products = self.repo.get_all_products()
        if not products:
            CTkMessagebox(title="Błąd", message="Brak produktów do sprawdzenia!")
            return

        self.monitor.check_all_products(notif_func=self.add_notif_entry)
        self.add_notif_entry(f"[SYSTEM] Sprawdzono wszystkie produkty")
        self.refresh_product_entries()

    def start_checking_loop(self):
        check_interval = self.interval_entry.get().strip()

        if not check_interval:
            CTkMessagebox(title="Brakujące dane", message="Nie podano wartości interwału")
            return

        try:
            check_interval = float(check_interval)

            if check_interval <= 0:
                CTkMessagebox(title="Błęde dane", message="Wartość interwału musi być dodatnia")
                return
        except ValueError:
            CTkMessagebox(title="Błędne dane", message="Wartość interwału musi być liczbą dodatnią")
            return

        if hasattr(self, "is_monitoring") and self.is_monitoring:
            self.is_monitoring = False
            self.start_button.configure(text="Start", fg_color=["#3a7ebf", "#1f538d"])
            return

        self.is_monitoring = True
        self.start_button.configure(text="Stop", fg_color="crimson")

        def worker_loop():
            while self.is_monitoring:
                self.check_all_products()
                time.sleep(check_interval)

        threading.Thread(target=worker_loop, daemon=True).start()


    def open_history_window(self):
        selected_product_entry = self.product_tree.selection()

        if not selected_product_entry:
            CTkMessagebox(title="Wybierz produkt", message="Nie zaznaczono produktu!")
            return

        product_id = selected_product_entry[0]
        product = self.repo.get_product_by_id(product_id)
        if not product:
            CTkMessagebox(title="Błąd", message="Nie znaleziono produktu")
            return

        self.history_window = ctk.CTkToplevel(self)
        self.history_window.title(f"Historia cen - {product.name}")
        self.history_window.geometry("800x600")

        self.history_window.transient(self)
        self.history_window.grab_set()
        self.history_window.focus()

        self.history_window.rowconfigure(1, weight=1)
        self.history_window.columnconfigure(0, weight=1)

        header = ctk.CTkLabel(self.history_window, text = f"{product.name} | {product.store} | {product.url}", wraplength=680, anchor="w", padx = 10, pady=6)
        header.grid(row=0, column=0, sticky="ew")

        frame = ctk.CTkFrame(self.history_window)
        frame.grid(row=1, column=0, sticky="nesw", padx=8,pady=8)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        cols = ("Data", "Cena", "Waluta", "Dostępność", "Status")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        scroll = ctk.CTkScrollbar(frame, command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)

        tree.heading("Data", text="Data")
        tree.heading("Cena", text="Cena")
        tree.heading("Waluta", text="Waluta")
        tree.heading("Dostępność", text="Dostępność")
        tree.heading("Status", text="Status")

        tree.column("Data", width=150,anchor="center")
        tree.column("Cena", width=100,anchor="center")
        tree.column("Waluta", width=70,anchor="center")
        tree.column("Dostępność", width=90,anchor="center")
        tree.column("Status", width=120,anchor="center")

        for record in reversed(product.price_history):
            if record is None:
                continue
            tree.insert("", "end", values=(record.timestamp.strftime("%Y-%m-%d %H:%M"), record.price, record.currency, "Tak" if record.available else "Nie", record.status.value))

        scroll.pack(side="right", fill="y")
        tree.pack(expand=True, fill="both")


    def open_stores_window(self):
        self.stores_window = ctk.CTkToplevel(self)
        self.stores_window.title("Zarządzanie sklepami")
        self.stores_window.geometry("800x480")
        self.stores_window.transient(self)
        self.stores_window.grab_set()
        self.stores_window.focus()

        self.stores_window.rowconfigure(1, weight=1)
        self.stores_window.columnconfigure(0, weight=1)

        toolbar = ctk.CTkFrame(self.stores_window)
        toolbar.grid(row=0, column=0, sticky="ew", padx=8, pady=(8,0))

        add_store_button = ctk.CTkButton(toolbar, text = "Dodaj", width=80, command=lambda: self.open_store_form(self.stores_window, stores_tree, None))
        edit_store_button = ctk.CTkButton(toolbar, text = "Edytuj", width=80, command=lambda: self.edit_selected_store(self.stores_window, stores_tree))
        del_store_button = ctk.CTkButton(toolbar, text = "Usuń", width=80, command=lambda: self.delete_selected_store(stores_tree))

        add_store_button.pack(side="left", padx = 4)
        edit_store_button.pack(side="left", padx = 4)
        del_store_button.pack(side="left", padx = 4)

        info_builtin = ctk.CTkLabel(toolbar, text="Nie można edytować ani usuwać wbudowanych sklepów.", text_color="gray")
        info_builtin.pack(side="top")

        frame = ctk.CTkFrame(self.stores_window)
        frame.grid(row=1, column=0, sticky="nesw", padx=8, pady=8)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        cols = ("Nazwa", "Domena", "Waluta", "Selektor", "Typ")
        stores_tree = ttk.Treeview(frame, columns=cols, show="headings")
        scroll = ctk.CTkScrollbar(frame, command=stores_tree.yview)
        stores_tree.configure(yscrollcommand=scroll.set)

        stores_tree.heading("Nazwa", text="Nazwa")
        stores_tree.heading("Domena", text="Domena")
        stores_tree.heading("Waluta", text="Waluta")
        stores_tree.heading("Selektor", text="Selektor")
        stores_tree.heading("Typ", text="Typ")

        stores_tree.column("Nazwa", width=120,anchor="w")
        stores_tree.column("Domena", width=150,anchor="w")
        stores_tree.column("Waluta", width=60,anchor="center")
        stores_tree.column("Selektor", width=320,anchor="w")
        stores_tree.column("Typ", width=80,anchor="center")

        scroll.pack(side="right", fill="y")
        stores_tree.pack(expand=True, fill="both")

        self.stores_refresh(stores_tree)

    def stores_refresh(self, tree):
        for item in tree.get_children():
            tree.delete(item)
        for store in self.store_registry.get_all():
            typ = "wbudowany" if store.builtin else "własny"
            tree.insert("", "end", iid = store.name, values=(store.name, store.domain, store.currency, store.selector if store.selector else "domyślny", typ))

    def edit_selected_store(self, win, tree):
        selected = tree.selection()
        if not selected:
            CTkMessagebox(title="Nie wybrano sklepu", message="Nie wybrano żadnego sklepu do edycji!")
            return
        store = self.store_registry.get_by_name(selected[0])
        if store and store.builtin:
            CTkMessagebox(title="Brak dostępu", message="Nie można edytować wbudowanych sklepów")
            return
        self.open_store_form(win, tree, store)

    def delete_selected_store(self, tree):
        selected = tree.selection()
        if not selected:
            CTkMessagebox(title="Nie wybrano sklepu", message="Nie wybrano żadnego sklepu do usunięcia")
            return
        store = self.store_registry.get_by_name(selected[0])
        if store and store.builtin:
            CTkMessagebox(title="Brak dostępu", message="Nie można usuwać wbudowanych sklepów")
            return
        if self.store_registry.delete_custom(selected[0]):
            tree.delete(selected[0])
            self.add_notif_entry(f"[SYSTEM] Usunięto sklep {store.name}.")
        else:
            CTkMessagebox(title="Błąd", message="Nie udało się usunąć sklepu")

    def open_store_form(self, parent_win, tree, store):
        is_edit = store is not None
        form = ctk.CTkToplevel(parent_win)
        form.title("Edytuj sklep" if is_edit else "Dodaj sklep")
        form.geometry("480x300")
        form.transient(parent_win)
        form.grab_set()
        form.focus()

        fields = [("Nazwa:", 80), ("Domena:", 80), ("Waluta:", 80), ("Selektor CSS:", 320), ("Uwagi:", 80)]
        entries = {}

        defaults = {
            "Nazwa": store.name if is_edit else "",
            "Domena": store.domain if is_edit else "",
            "Waluta": store.currency if is_edit else "",
            "Selektor CSS": store.selector if (is_edit and store.selector) else "",
            "Uwagi": store.notes if is_edit else "",
        }

        for i, (label, width) in enumerate(fields):
            ctk.CTkLabel(form, text=label, anchor="e", width=100).grid(row=i, column = 0, sticky="e",padx=8,pady=6)
            e = ctk.CTkEntry(form, width = width if  width > 100 else 200)
            e.insert(0, defaults[label.rstrip(":")])
            e.grid(row=i, column = 1, sticky="w", pady=6)
            entries[label.rstrip(":")] = e

        hint = ctk.CTkLabel(form, text="Jeśli pole 'Selektor CSS' pozostanie puste, wykorzystane zostaną domyślne selektory. Nie gwarantują one poprawności działania.", wraplength=370, text_color="red", anchor="w", justify="left")
        hint.grid(row = len(fields), column=0, columnspan=2, sticky="w", padx=(0,10),pady=(0,6))

        def save():
            from stores import StoreConfig
            name = entries["Nazwa"].get().strip()
            domain = entries["Domena"].get().strip()
            currency = entries["Waluta"].get().strip() or "PLN"
            selector = entries["Selektor CSS"].get().strip() or None
            notes = entries["Uwagi"].get().strip()

            if not name or not domain:
                CTkMessagebox(title="Błąd", message="Nazwa i domena są wymagane.")
                return
            new_store = StoreConfig(name, domain, selector, currency, notes, builtin=False)

            if is_edit:
                self.store_registry.update_custom(new_store)
            else:
                self.store_registry.add_custom(new_store)
                self.add_notif_entry("[SYSTEM] Dodano nowy sklep.")

            self.stores_refresh(tree)
            form.destroy()
        ctk.CTkButton(form, text="Zapisz", command=save).grid(row=len(fields) + 1, column = 0, columnspan=2, pady=14)

    def export_data(self):
        path = filedialog.asksaveasfilename(title="Eksportuj dane", defaultextension=".json",
                                            filetypes=[("Plik JSON", "*.json"), ("Wszystkie pliki", "*.*")],
                                            initialfile="price_monitor_export.json")
        if not path:
            return
        try:
            products = [p.to_dict() for p in self.repo.get_all_products()]
            custom_stores = [s.to_dict() for s in self.store_registry.custom.values()]

            export_dict = {
                "products": products,
                "custom_stores": custom_stores,
            }

            with open(path, "w", encoding="utf-8") as f:
                json.dump(export_dict, f, ensure_ascii=False, indent=4)

            total = len(products)
            total_stores = len(custom_stores)

            self.add_notif_entry(f"[SYSTEM] Wyeksportowano {total} produktów oraz {total_stores} sklepów do: {path}")
            CTkMessagebox(title="Eksport zakończony",
                          message=f"Pomyślnie wykesportowano {total} produktów oraz {total_stores} sklepów")
        except Exception as e:
            logger.error(f"Błąd eksportu: {e}")
            CTkMessagebox(title="Błąd eksportu", message="Nie udało się wyeksportować danych.")

    def import_data(self):
        path = filedialog.askopenfilename(title="Importuj dane",
                                          filetypes=[("Plik JSON", "*.json"), ("Wszystkie pliki", "*.*")])
        if not path:
            return
        path_check = Path(path)
        ok, msg = check_readable(path_check)
        if not ok:
            CTkMessagebox(title="Błąd importu", message=msg)
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            CTkMessagebox(title="Błąd odczytu", message="Nie udało się wczytać pliku z danymi.")
            return
        raw_products = data.get("products", [])
        raw_stores = data.get("custom_stores", [])

        if not raw_products and not raw_stores:
            CTkMessagebox(title="Pusty plik", message="Brak danych do importu w podanym pliku")
            return

        mode_win = ctk.CTkToplevel(self)
        mode_win.title("Opcje importu")
        mode_win.geometry("480x300")
        mode_win.transient(self)
        mode_win.grab_set()
        mode_win.focus()
        ctk.CTkLabel(mode_win,
                     text=f"Znaleziono {len(raw_products)} produktów oraz {len(raw_stores)} sklepów. Wybierz opcje importu.",
                     wraplength=480, pady=10).pack()
        merge_var = ctk.StringVar(value="merge")
        ctk.CTkRadioButton(mode_win, text="Scal z istniejącymi danymi.", variable=merge_var, value="merge").pack(
            anchor="w", padx=20, pady=4)
        ctk.CTkRadioButton(mode_win, text="Zastąp istniejące dane", variable=merge_var, value="replace").pack(
            anchor="w", padx=20, pady=4)

        def do_import():
            mode = merge_var.get()
            mode_win.destroy()
            self.apply_import(raw_products, raw_stores, mode)

        ctk.CTkButton(mode_win, text="Importuj", command=do_import).pack(pady=14)

    def apply_import(self, raw_products, raw_stores, mode):
        from stores import StoreConfig

        imported_products = 0
        skipped_products = 0
        imported_stores = 0

        try:
            if mode == "replace":
                for p in self.repo.get_all_products():
                    self.repo.delete_product(p.id)
                for s in list(self.store_registry.custom.keys()):
                    self.store_registry.delete_custom(s)

            for s_data in raw_stores:
                store = StoreConfig.from_dict(s_data)
                store.builtin = False
                existing = self.store_registry.get_by_name(store.name)
                if mode == "merge" and existing and not existing.builtin:
                    pass
                else:
                    self.store_registry.custom[store.name] = store
                    imported_stores += 1
            if raw_stores:
                self.store_registry.save_to_json()

            for p_data in raw_products:
                product = Product.from_dict(p_data)
                existing = self.repo.get_product_by_id(product.id)
                if mode == "merge" and existing:
                    skipped_products += 1
                    continue
                self.repo.save_product(product)
                imported_products += 1
            self.refresh_product_entries()
            self.add_notif_entry(
                f"[SYSTEM] Zaimportowano {imported_products} produktów ({skipped_products} pominięto) oraz {imported_stores} sklepów własnych.")
            CTkMessagebox(title="Import zakończony",
                          message=f"Zaimportowano {imported_products} produktów ({skipped_products} pominięto) oraz {imported_stores} sklepów własnych.")
        except Exception as e:
            logger.error(f"Błąd importu: {e}")
            CTkMessagebox(title="Błąd importu", message="Nie udało się zaimportować danych")


if __name__ == "__main__":
    main_wind = Main_window()

    main_wind.mainloop()

