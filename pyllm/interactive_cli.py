from pyllm import models

MENU_OPTIONS = [
    ("Wyświetl dostępne modele", "list"),
    ("Wyświetl domyślny model", "default"),
    ("Wyświetl zainstalowane modele", "installed"),
    ("Zainstaluj model (wybierz z listy)", "wybierz-model"),
    ("Ustaw domyślny model (wybierz z listy)", "wybierz-default"),
    ("Aktualizuj listę modeli z ollama.com", "update"),
    ("Test domyślnego modelu", "test"),
    ("Wyjdź", "exit")
]

INTRO = """
Tryb interaktywny pyllm
Wybierz numer akcji z menu lub wpisz komendę (np. list, install <model>, ...)
"""

def choose_model(action_desc, callback):
    models_list = models.get_models()
    print(f"\nDostępne modele do {action_desc}:")
    for idx, m in enumerate(models_list):
        print(f"  [{idx+1}] {m.get('name', '-'):<25} {m.get('size','') or m.get('size_b','')}  {m.get('desc','')}")
    try:
        num = int(input(f"Podaj numer modelu do {action_desc}: "))
        if 1 <= num <= len(models_list):
            model_name = models_list[num-1]['name']
            callback(model_name)
        else:
            print("Nieprawidłowy numer.")
    except (ValueError, KeyboardInterrupt, EOFError):
        print("Przerwano wybór.")

def print_menu():
    print("\n=== MENU ===")
    for i, (desc, _) in enumerate(MENU_OPTIONS, 1):
        print(f"  [{i}] {desc}")
    print("Wybierz numer lub wpisz komendę:")

def interactive_shell():
    print(INTRO)
    while True:
        print_menu()
        try:
            cmd = input("pyllm> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nWyjście z trybu interaktywnego.")
            break
        if not cmd:
            continue
        # Obsługa wyboru numeru z menu
        if cmd.isdigit():
            idx = int(cmd) - 1
            if 0 <= idx < len(MENU_OPTIONS):
                cmd = MENU_OPTIONS[idx][1]
            else:
                print("Nieprawidłowy numer.")
                continue
        args = cmd.split()
        if args[0] == "exit" or args[0] == "quit": 
            print("Wyjście z trybu interaktywnego.")
            break
        elif args[0] == "list":
            models_list = models.get_models()
            print("\nDostępne modele:")
            for m in models_list:
                print(f"  {m.get('name', '-'):<25} {m.get('size','') or m.get('size_b','')}  {m.get('desc','')}")
        elif args[0] == "install" and len(args) > 1:
            models.install_model(args[1])
        elif args[0] == "installed":
            models.list_installed_models()
        elif args[0] == "set-default" and len(args) > 1:
            models.set_default_model(args[1])
        elif args[0] == "default":
            print("Domyślny model:", models.get_default_model())
        elif args[0] == "update":
            models.update_models_from_ollama()
        elif args[0] == "test":
            default = models.get_default_model()
            print(f"Test domyślnego modelu: {default}")
            if default:
                print("OK: Domyślny model jest ustawiony.")
            else:
                print("BŁĄD: Domyślny model NIE jest ustawiony!")
        elif args[0] == "wybierz-model":
            choose_model("pobrania", models.install_model)
        elif args[0] == "wybierz-default":
            choose_model("ustawienia jako domyślny", models.set_default_model)
        else:
            print("Nieznana komenda. Dostępne: list, install <model>, installed, set-default <model>, default, update, test, wybierz-model, wybierz-default, exit")

if __name__ == "__main__":
    interactive_shell()
