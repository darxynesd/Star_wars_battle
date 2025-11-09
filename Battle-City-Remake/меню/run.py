
import os
import sys
import main

MAIN_FILE = "main.py"

def main():

    if not os.path.exists(MAIN_FILE):
        print(f"Ошибка: Файл '{MAIN_FILE}' не найден.")
        sys.exit(1)


    try:
        main.run()
    except KeyboardInterrupt:
        print("Выход...")
        sys.exit(0)

if __name__ == "__main__":
    main()
