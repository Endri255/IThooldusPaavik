import json
import os
import csv
import datetime
from models import LogEntry

class LogBook:
    def __init__(self, filename="logbook.json"):
        self.filename = filename
        self.entries = []
        self.load_from_json()

    def get_next_id(self):
        if not self.entries: return 1
        return max(e.entry_id for e in self.entries) + 1

    def add_entry(self, title, description):
        new_id = self.get_next_id()
        new_entry = LogEntry(new_id, title, description)
        self.entries.append(new_entry)
        self.save_to_json()  # AUTOSAVE
        return new_entry

    def delete_entry(self, entry_id):
        self.entries = [e for e in self.entries if e.entry_id != int(entry_id)]
        self.save_to_json()  # AUTOSAVE

    def change_status(self, entry_id):
        for e in self.entries:
            if e.entry_id == int(entry_id):
                e.status = "DONE" if e.status == "OPEN" else "OPEN"
                self.save_to_json()  # AUTOSAVE
                return True
        return False

    def save_to_json(self):
        data = [e.to_dict() for e in self.entries]
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def load_from_json(self):
        if not os.path.exists(self.filename): return
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.entries = [LogEntry(item['id'], item['title'], item['description'], item['status'], item['created_at']) for item in data]
        except:
            self.entries = []

    def import_from_csv(self, file_path):
        if not os.path.exists(file_path):
            return "VIGA: Faili ei leitud!"

        error_logs = []
        added_count = 0

        with open(file_path, 'r', encoding='utf-8') as f:
            # Kasutame semikoolonit eraldajana nagu näidises
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                if not row or len(row) < 4: continue

                d_str, title, desc, status = row[0], row[1], row[2], row[3]

                # Valideerime
                is_valid, msg = LogEntry.validate_import(d_str, title, desc, status)

                if is_valid:
                    # Muudame kuupäeva YYYY-MM-DD -> DD.MM.YYYY süsteemi jaoks
                    dt = datetime.datetime.strptime(d_str, "%Y-%m-%d %H:%M:%S")
                    new_date = dt.strftime("%d.%m.%Y %H:%M:%S")

                    new_id = self.get_next_id()
                    self.entries.append(LogEntry(new_id, title, desc, status.upper(), new_date))
                    added_count += 1
                else:
                    error_logs.append(f"RIDA: {row} | VIGA: {msg}\n")

        # Salvestame vead
        if error_logs:
            with open("import_errors.log", "w", encoding='utf-8') as ef:
                ef.writelines(error_logs)

        self.save_to_json()
        return f"Import valmis! Lisati {added_count} kirjet. Vigade logi: import_errors.log"