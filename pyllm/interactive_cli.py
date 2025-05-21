from pyllm import models

INTRO = """
Tryb interaktywny pyllm
Dostępne komendy: list, install <model>, installed, set-default <model>, default, update, test, exit
"""

def interactive_shell():
    print(INTRO)
    while True:
        try:
            cmd = input("pyllm> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nWyjście z trybu interaktywnego.")
            break
        if not cmd:
            continue
        if cmd in ("exit", "quit"): 
            print("Wyjście z trybu interaktywnego.")
            break
        args = cmd.split()
        if args[0] == "list":
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
        else:
            print("Nieznana komenda. Dostępne: list, install <model>, installed, set-default <model>, default, update, test, exit")

if __name__ == "__main__":
    interactive_shell()
