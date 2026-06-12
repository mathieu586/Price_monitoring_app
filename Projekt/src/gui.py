import customtkinter as ctk
from tkinter import ttk

from Projekt.src.stores import StoreRegistry
from repository import JsonRepository
from scraper import Scraper
from models import Product, PriceRecord

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

        self.make_button_rows()
        self.make_product_panel()
        self.make_notification_panel()

        self.repo = JsonRepository("product_data.json")
        self.scraper = Scraper()
        self.store_registry = StoreRegistry("stores.json")

    def make_button_rows(self):
        # PRZYCISKI AKCJI
        self.action_buttons_frame = ctk.CTkFrame(self)
        self.action_buttons_frame.grid(row=2, column=0, sticky="nesw", columnspan=2)

        self.add_button = ctk.CTkButton(master=self.action_buttons_frame, text="Dodaj", height=28, width=40, command=self.open_add_window)
        self.add_button.pack(padx=5, side="left")

        self.edit_button = ctk.CTkButton(master=self.action_buttons_frame, text="Edytuj", height=28, width=40)
        self.edit_button.pack(padx=5, side="left")

        self.delete_button = ctk.CTkButton(master=self.action_buttons_frame, text="Usuń", height=28, width=40)
        self.delete_button.pack(padx=5, side="left")

        self.history_button = ctk.CTkButton(master=self.action_buttons_frame, text="Historia", height=28, width=40)
        self.history_button.pack(padx=5, side="left")

        self.shops_button = ctk.CTkButton(master=self.action_buttons_frame, text="Sklepy", height=28, width=40)
        self.shops_button.pack(padx=5, side="left")

        # FILTRY
        self.filter_frame = ctk.CTkFrame(self)
        self.filter_frame.grid(row=1, column=0, columnspan=2, sticky="nesw")

        self.sort_label = ctk.CTkLabel(master=self.filter_frame, text="Sortuj według:")
        self.sort_label.pack(side="left", padx=10)

        self.filter_var = ctk.StringVar(value="date")

        self.filter_date = ctk.CTkRadioButton(master=self.filter_frame, variable=self.filter_var, value="date", text="Data")
        self.filter_date.pack(side="left")

        self.filter_name = ctk.CTkRadioButton(master=self.filter_frame, variable=self.filter_var, value="name",text="Nazwa")
        self.filter_name.pack(side="left")

        self.filter_price = ctk.CTkRadioButton(master=self.filter_frame, variable=self.filter_var, value="price", text="Cena")
        self.filter_price.pack(side="left")

        self.filter_store = ctk.CTkRadioButton(master=self.filter_frame, variable=self.filter_var, value="store", text="Sklep")
        self.filter_store.pack(side="left")

        self.filter_change = ctk.CTkRadioButton(master=self.filter_frame, variable=self.filter_var, value="change", text="Termin zmiany")
        self.filter_change.pack(side="left")

        # GŁÓWNE PRZYCISKI
        self.main_buttons_frame = ctk.CTkFrame(self)
        self.main_buttons_frame.grid(row=0, column=0, columnspan=2, sticky="nesw")

        self.start_button = ctk.CTkButton(master=self.main_buttons_frame, text="Start", height=28, width=40)
        self.start_button.pack(side="right", padx=5)

        self.check_all_button = ctk.CTkButton(master=self.main_buttons_frame, text="Sprawdź wszystkie", height=28, width=40)
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

    def add_product_entry(self, product_data):
        self.product_tree.insert(parent="", index="end", values=product_data)

    def clear_product_entries(self):
        for product in self.product_tree.get_children():
            self.product_tree.delete(product)

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
        self.notif_box.configure(state="normal")

        self.notif_box.insert(index="end", text=(notif_content+"\n"))

        self.notif_box.see("end")
        self.notif_box.configure(state="disabled")

    def refresh_product_panel(self):
        pass

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

        name_label = ctk.CTkLabel(master=self.add_window, text="Nazwa")
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
            self.add_notif_entry("[BŁĄD] Pole URL nie może być puste")
            return

        if not store_config:
            self.add_notif_entry("[BŁĄD] Nie rozpoznano sklepu dla podanego URL")
            return

        new_product = Product(id=Product.generate_id(), name=name, url=url, store=store_config.name, selector=store_config.selector,
                              check_interval=3600, alert_threshold=float(threshold) if threshold else 0.0)    # check_interval -------------------------------------------

        self.repo.save_product(new_product)
        self.add_product_entry(new_product.get_table_row())
        self.add_notif_entry(f"[SYSTEM] Dodano produkt: {name}")

        self.add_window.destroy()


if __name__ == "__main__":
    main_wind = Main_window()

    main_wind.mainloop()

