import json
import csv
import datetime
import os


class LogEntry:
    """
    Esindab ühte IT-hoolduse logikirjet.
    """

    def __init__(self, title: str, description: str, status: str = "OPEN", created_at: str = None):
        self.created_at = created_at if created_at else datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        # Puhastame sisendi (eemaldame tühikud otstest, kui on string)
        title = title.strip() if title else ""
        description = description.strip() if description else ""
        status = status.strip().upper() if status else "OPEN"

        # Valideerimine
        if len(title) < 4:
            raise ValueError(f"Pealkiri '{title}' on liiga lühike (min 4 märki).")
        if len(description) < 10:
            raise ValueError(f"Kirjeldus on liiga lühike (min 10 märki).")
        if status not in ["OPEN", "DONE"]:
            raise ValueError(f"Staatus '{status}' on vigane. Lubatud on 'OPEN' või 'DONE'.")

        self.title = title
        self.description = description
        self.status = status

    def to_dict(self):
        """Muudab objekti sõnastikuks JSON-i salvestamise jaoks."""
        return {
            "created_at": self.created_at,
            "title": self.title,
            "description": self.description,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data):
        """Loob sõnastikust uue LogEntry objekti."""
        # Kasutame .get(), et vältida kohest KeyErrori - las __init__ tegeleb valideerimisega
        return cls(
            title=data.get("title"),
            description=data.get("description"),
            status=data.get("status", "OPEN"),
            created_at=data.get("created_at")
        )

    def __str__(self):
        """Tagastab kirje konsoolis kuvatava kuju."""
        return f"{self.created_at} | [{self.status}] | {self.title} | {self.description}"


class LogBook:
    """
    Haldab logikirjete kogumikku (lisamine, kustutamine, salvestamine).
    """

    def __init__(self, filepath="logbook.json"):
        self.filepath = filepath
        self.entries = []
        self.load_data()

    def add_entry(self, title: str, description: str):
        """Lisab uue kirje logiraamatusse."""
        new_entry = LogEntry(title, description)
        self.entries.append(new_entry)

    def remove_entry(self, created_at: str):
        """Kustutab kirje unikaalse ajahetke (created_at) järgi."""
        initial_count = len(self.entries)
        self.entries = [e for e in self.entries if e.created_at != created_at]
        return len(self.entries) < initial_count

    def change_status(self, created_at: str):
        """Muudab kirje staatust (OPEN <-> DONE)."""
        for entry in self.entries:
            if entry.created_at == created_at:
                entry.status = "DONE" if entry.status == "OPEN" else "OPEN"
                return True
        return False

    def search_entries(self, keyword: str):
        """Otsib kirjeid pealkirja või kirjelduse järgi."""
        keyword = keyword.lower()
        return [e for e in self.entries if keyword in e.title.lower() or keyword in e.description.lower()]

    def filter_by_status(self, status: str):
        """Filtreerib kirjeid staatuse järgi."""
        return [e for e in self.entries if e.status == status]

    def save_data(self):
        """Salvestab kõik kirjed JSON faili."""
        data = [entry.to_dict() for entry in self.entries]
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Viga salvestamisel: {e}")

    def load_data(self):
        """Laeb kirjed JSON failist käivitamisel."""
        if not os.path.exists(self.filepath):
            print("Logiraamatu faili ei leitud. Alustan tühja nimekirjaga.")
            return

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.entries = [LogEntry.from_dict(item) for item in data]
            print(f"Laeti {len(self.entries)} kirjet failist.")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Viga andmete laadimisel või fail on tühi: {e}")
            self.entries = []

    def import_from_file(self, import_filepath):
        """
        Importib andmeid välisest failist (JSON või CSV).
        Raporteerib õnnestumiste ja vigade arvu ning salvestab vead faili.
        """
        if not os.path.exists(import_filepath):
            print(f"Faili '{import_filepath}' ei leitud.")
            return

        success_count = 0
        error_log = []
        raw_data = []

        try:
            # --- 1. Faili lugemine ---
            if import_filepath.lower().endswith(".csv"):
                # CSV LUGEMINE
                with open(import_filepath, "r", encoding="utf-8") as f:
                    # Proovime automaatselt tuvastada, kas eraldaja on koma või semikoolon
                    sample = f.read(1024)
                    f.seek(0)
                    try:
                        dialect = csv.Sniffer().sniff(sample)
                    except csv.Error:
                        dialect = 'excel'  # Vaikimisi

                    # DictReader loeb faili nii, et iga rida on sõnastik (võtmed päisereast)
                    reader = csv.DictReader(f, dialect=dialect)

                    # Puhastame veerupäised (juhul kui ' title' vs 'title')
                    reader.fieldnames = [name.strip() for name in reader.fieldnames] if reader.fieldnames else []

                    for row in reader:
                        # Puhastame väärtused tühikutest
                        clean_row = {k: v.strip() for k, v in row.items() if k}
                        raw_data.append(clean_row)
            else:
                # JSON LUGEMINE (vaikimisi)
                with open(import_filepath, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                    if not isinstance(raw_data, list):
                        print("Viga: JSON faili sisu peab olema nimekiri (list).")
                        return

            # --- 2. Andmete töötlemine ---
            print(f"Alustan {len(raw_data)} kirje töötlemist...")

            for i, item in enumerate(raw_data):
                try:
                    # Loome uue LogEntry objekti (see teeb ka valideerimise)
                    new_entry = LogEntry.from_dict(item)
                    self.entries.append(new_entry)
                    success_count += 1
                except (ValueError, KeyError, TypeError, AttributeError) as e:
                    # Vormindame veateate
                    row_identifier = item.get('title', f"Rida nr {i + 1}")
                    error_msg = f"Rida {i + 1} ('{row_identifier}'): {e}"
                    error_log.append(error_msg)

            # --- 3. Raporteerimine ---
            print("\n" + "=" * 30)
            print(f"IMPORT LÕPETATUD")
            print("=" * 30)
            print(f"Edukaid kirjad : {success_count}")
            print(f"Vigaseid kirjad: {len(error_log)}")
            print("-" * 30)

            # --- 4. Vigade salvestamine ---
            if error_log:
                with open("import_errors.log", "w", encoding="utf-8") as err_f:
                    err_f.write(f"Importimise aeg: {datetime.datetime.now()}\n")
                    err_f.write(f"Fail: {import_filepath}\n")
                    err_f.write("-" * 50 + "\n")
                    for line in error_log:
                        err_f.write(line + "\n")
                print(f"(!) Vigased read on salvestatud faili 'import_errors.log'.")
            else:
                print("Suurepärane! Kõik read imporditi vigadeta.")

        except Exception as e:
            print(f"\nKRIITILINE VIGA faili lugemisel: {e}")