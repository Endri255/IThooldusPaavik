import sys
from cli import run_cli
from gui import run_gui

if __name__ == "__main__":
    print("Vali käivitusviis:")
    print("1. Konsool (CLI)")
    print("2. Graafiline liides (GUI)")

    valik = input("Sinu valik (1/2): ").strip()

    if valik == "2":
        run_gui()
    else:
        # Vaikimisi CLI
        run_cli()