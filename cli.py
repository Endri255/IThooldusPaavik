from models import LogBook


def format_entry_short(entry):
    """Abifunktsioon: kärbib kirjelduse 15 märgini ja lisab '...' vajadusel"""
    desc = entry.description
    if len(desc) > 15:
        desc = desc[:15] + "..."
    # Tagastab vormindatud stringi, sarnaselt LogEntry __str__ meetodile, aga lühendatud kirjeldusega
    return f"{entry.created_at} | [{entry.status}] | {entry.title} | {desc}"


def run_cli():
    logbook = LogBook()

    while True:
        print("\n--- IT HOOLDUSPÄEVIK ---")
        print("Tere!")
        print("1. Lisa uus logikirje")
        print("2. Kuva kõik logikirjed")
        print("3. Otsi kirjeid")
        print("4. Filtreeri staatuse järgi")
        print("5. Muuda kirje staatust")
        print("6. Kustuta kirje")
        print("7. Välju")
        print("8. Impordi failist")

        choice = input("\nVali tegevus (1-8): ").strip()

        if choice == "7":
            logbook.save_data()
            print("Head aega!")
            break

        if choice == "1":
            title = input("Sisesta pealkiri (min 4 märki): ").strip()
            desc = input("Sisesta kirjeldus (min 10 märki): ").strip()
            try:
                logbook.add_entry(title, desc)
                logbook.save_data()  # Automaatne salvestus
                print("Kirje lisatud ja salvestatud!")
            except ValueError as e:
                print(f"Viga lisamisel: {e}")

        elif choice == "2":
            if not logbook.entries:
                print("Logiraamat on tühi.")
            for entry in logbook.entries:
                print(format_entry_short(entry))

        elif choice == "3":
            while True:
                keyword = input("Sisesta otsingusõna (min 2 märki, ENTER tühistamiseks): ").strip()

                if keyword == "":
                    print("Otsing tühistatud.")
                    break  # Väljub otsingu loopist tagasi menüüsse

                if len(keyword) < 2:
                    print("(miinimum kaks tähemärki)")
                    continue  # Küsib uuesti, ei lähe menüüsse

                results = logbook.search_entries(keyword)
                if results:
                    for entry in results:
                        print(format_entry_short(entry))
                else:
                    print("Ei leitud ühtegi vastet.")
                break

        elif choice == "4":
            status = input("Sisesta staatus (OPEN / DONE): ").strip().upper()
            results = logbook.filter_by_status(status)
            for entry in results:
                print(format_entry_short(entry))

        elif choice == "5":
            uid = input("Sisesta kirje loomise aeg (DD.MM.YYYY HH:MM:SS) mida muuta: ").strip()
            if logbook.change_status(uid):
                logbook.save_data()  # Automaatne salvestus
                print("Staatus muudetud ja salvestatud!")
            else:
                print("Sellise ajaga kirjet ei leitud.")

        elif choice == "6":
            uid = input("Sisesta kirje loomise aeg (DD.MM.YYYY HH:MM:SS) mida kustutada: ").strip()
            if logbook.remove_entry(uid):
                logbook.save_data()  # Automaatne salvestus
                print("Kirje kustutatud ja salvestatud!")
            else:
                print("Sellise ajaga kirjet ei leitud.")

        elif choice == "8":
            fname = input("Sisesta failinimi (nt vigane_data.json): ").strip()
            logbook.import_from_file(fname)
            logbook.save_data()

        else:
            print("Tundmatu valik, proovi uuesti.")

        # Paus enne uuesti menüü kuvamist
        if choice != "3":
            input("\nVajuta ENTER, et jätkata...")
        elif choice == "3" and keyword != "":
            input("\nVajuta ENTER, et jätkata...")