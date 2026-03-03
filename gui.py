import tkinter as tk
from tkinter import messagebox, ttk
from models import LogBook


class LogBookApp:
    def __init__(self, root):
        self.logbook = LogBook()
        self.root = root
        self.root.title("IT Hoolduspäevik")
        self.root.geometry("800x600")

        # Ülemine osa: Sisestusväljad
        input_frame = tk.LabelFrame(root, text="Lisa uus kirje", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(input_frame, text="Pealkiri:").grid(row=0, column=0, sticky="w")
        self.entry_title = tk.Entry(input_frame, width=40)
        self.entry_title.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Kirjeldus:").grid(row=1, column=0, sticky="w")
        self.entry_desc = tk.Entry(input_frame, width=40)
        self.entry_desc.grid(row=1, column=1, padx=5)

        tk.Button(input_frame, text="Lisa kirje", command=self.add_entry_gui).grid(row=2, column=1, sticky="e", pady=5)

        # Keskmine osa: Filtrid ja otsing
        control_frame = tk.Frame(root, padx=10, pady=5)
        control_frame.pack(fill="x")

        tk.Label(control_frame, text="Otsing:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_list)  # Uuendab automaatselt kirjutades
        tk.Entry(control_frame, textvariable=self.search_var).pack(side="left", padx=5)

        tk.Button(control_frame, text="Muuda staatust", command=self.toggle_status_gui).pack(side="right", padx=5)
        tk.Button(control_frame, text="Kustuta valitud", command=self.delete_entry_gui).pack(side="right", padx=5)

        # Alumine osa: Tabel (Treeview)
        list_frame = tk.Frame(root, padx=10, pady=10)
        list_frame.pack(fill="both", expand=True)

        columns = ("created_at", "status", "title", "description")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")

        self.tree.heading("created_at", text="Aeg")
        self.tree.heading("status", text="Staatus")
        self.tree.heading("title", text="Pealkiri")
        self.tree.heading("description", text="Kirjeldus")

        self.tree.column("created_at", width=120)
        self.tree.column("status", width=60)
        self.tree.column("title", width=150)
        self.tree.column("description", width=300)

        self.tree.pack(fill="both", expand=True)

        # Lae andmed
        self.update_list()

        # Sulgemisel salvesta
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_list(self, *args):
        # Tühjenda tabel
        for i in self.tree.get_children():
            self.tree.delete(i)

        search_term = self.search_var.get().lower()

        for entry in self.logbook.entries:
            if search_term in entry.title.lower() or search_term in entry.description.lower():
                self.tree.insert("", "end", values=(entry.created_at, entry.status, entry.title, entry.description))

    def add_entry_gui(self):
        title = self.entry_title.get()
        desc = self.entry_desc.get()
        try:
            self.logbook.add_entry(title, desc)
            self.entry_title.delete(0, "end")
            self.entry_desc.delete(0, "end")
            self.update_list()
        except ValueError as e:
            messagebox.showerror("Viga", str(e))

    def toggle_status_gui(self):
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        created_at = item["values"][0]  # Esimene tulp on ID

        self.logbook.change_status(created_at)
        self.update_list()

    def delete_entry_gui(self):
        selected = self.tree.selection()
        if not selected:
            return

        if messagebox.askyesno("Kinnita", "Kas oled kindel, et soovid kirje kustutada?"):
            item = self.tree.item(selected[0])
            created_at = item["values"][0]
            self.logbook.remove_entry(created_at)
            self.update_list()

    def on_closing(self):
        self.logbook.save_data()
        self.root.destroy()


def run_gui():
    root = tk.Tk()
    app = LogBookApp(root)
    root.mainloop()