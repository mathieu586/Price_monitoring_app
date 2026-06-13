import time
import threading
import customtkinter as ctk
from tkinter import ttk
import logging
from Projekt.src.stores import StoreRegistry
from repository import JsonRepository
from scraper import Scraper
from models import Product, PriceRecord
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

        self.repo = JsonRepository("product_data.json")
        self.scraper = Scraper()
        self.store_registry = StoreRegistry("stores.json")
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

        self.shops_button = ctk.CTkButton(master=self.action_buttons_frame, text="Sklepy", height=28, width=40)
        self.shops_button.pack(padx=5, side="left")

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

        self.clear_button = ctk.CTkButton(master=self.notif_frame, text="Wyczyść")
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
            else:
                logger.info(f"Niepowodzenie przy próbie usunięcia produktu: {product_name} | id: {product_id}")
                CTkMessagebox(title="Błąd", message=f"Nie udało się usunąć produktu:\n{product_name}")
        else:
            CTkMessagebox(title="Nie wybrano produktu", message="Nie wybrano żadnego produktu do usunięcia!")

    def check_all_products(self):
        products = self.repo.get_all_products()
        if not products:
            CTkMessagebox(title="Błąd", message="Brak produktów do sprawdzenia!")
            return

        self.monitor.check_all_products(notif_func=self.add_notif_entry)
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
            CTkMessagebox(title="Wybierz produkt", message="Nie zaznaczono produktu do edycji!")
            return

        product_id = selected_product_entry[0]
        product = self.repo.get_product_by_id(product_id)
        if not product:
            CTkMessagebox(title="Błąd", message="Nie znaleziono produktu")
            return

        self.history_window = ctk.CTkToplevel(self)
        self.history_window.title(f"Historia cen - {product.name}")
        self.history_window.geometry("520x200")

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
            tree.insert("", "end", values=(record.timestamp.strftime("%Y-%m-%d %H:%M"), record.price, record.currency, "Tak" if record.available else "Nie", record.status.value))

        scroll.pack(side="right", fill="y")
        tree.pack(expand=True, fill="both")


if __name__ == "__main__":
    main_wind = Main_window()

    main_wind.mainloop()

