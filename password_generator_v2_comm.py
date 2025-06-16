import tkinter as tk  # Импорт библиотеки для создания графического интерфейса
# Импорт модулей для диалоговых окон и работы с файлами
from tkinter import messagebox, filedialog
import random  # Импорт модуля для генерации случайных чисел
import string  # Импорт модуля для работы со строками
import tempfile  # Импорт модуля для создания временных файлов
import os  # Импорт модуля для работы с операционной системой
import csv  # Импорт модуля для работы с CSV-файлами

# --- Темы оформления (цветовые схемы интерфейса) ---
THEMES = {
    "dark": {  # Тёмная тема
        "bg": "#2e2e2e", "fg": "#ffffff",  # Фон и текст
        "entry_bg": "#3c3c3c", "btn_bg": "#505050",  # Фон полей ввода и кнопок
        "btn_fg": "#ffffff", "highlight": "#888888",  # Текст кнопок и подсветка
        "check_bg": "#4B4B4B", "check_fg": "#000000"  # Фон и текст чекбоксов
    },
    "light": {  # Светлая тема
        "bg": "#f0f0f0", "fg": "#000000",  # Фон и текст
        "entry_bg": "#ffffff", "btn_bg": "#e0e0e0",  # Фон полей ввода и кнопок
        "btn_fg": "#000000", "highlight": "#cccccc",  # Текст кнопок и подсветка
        "check_bg": "#f0f0f0", "check_fg": "#000000"  # Фон и текст чекбоксов
    },
}


class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root  # Основное окно приложения
        self.current_theme = "dark"  # Текущая тема (по умолчанию тёмная)
        self.all_widgets = []  # Список для хранения всех виджетов

        # --- Переменные состояния интерфейса ---
        self.difficulty_var = tk.StringVar(
            value="3")  # Уровень сложности пароля
        self.auto_level_var = tk.BooleanVar(
            value=False)  # Автоматический выбор сложности
        # Генерация уникальных паролей
        self.unique_var = tk.BooleanVar(value=False)
        self.exclude_similar_var = tk.BooleanVar(
            value=False)  # Исключение похожих символов
        # Пользовательские исключения символов
        self.excluded_chars_var = tk.StringVar(value="")

        self.length_entry = None  # Поле ввода длины пароля
        self.count_entry = None  # Поле ввода количества паролей
        self.result_text = None  # Текстовое поле для вывода результатов

        # --- Инициализация интерфейса ---
        self.create_widgets()  # Создание виджетов
        self.apply_theme(self.current_theme)  # Применение темы
        self.show_help_message()  # Показ справки при запуске

    # --- Вспомогательное окно со справкой ---
    def show_help_message(self):
        help_text = (
            "Добро пожаловать в Генератор паролей!\n\n"
            "Основные функции:\n"
            "- Задайте длину и количество паролей.\n"
            "- Выберите уровень сложности (1-3) или включите автовыбор.\n"
            "- Опция 'Уникальные пароли' — исключает дублирование.\n"
            "- Можно исключить похожие символы и задать свои.\n"
            "- Кнопки: Сгенерировать, Копировать, Сохранить, Печать.\n"
            "- Смена темы оформления.\n"
            "- Сброс всех настроек к значениям по умолчанию.\n"
            "- Горячие клавиши: Ctrl+G (Сгенерировать), Ctrl+C (Копировать), Ctrl+S (Сохранить),\n"
            "  Ctrl+P (Печать), Ctrl+R (Сброс настроек).\n"
        )
        # Отображение справки в диалоговом окне
        messagebox.showinfo("Справка", help_text)
        self.root.focus_force()  # Возвращение фокуса на глваное окно

    # --- Применение темы оформления ---
    def apply_theme(self, theme):
        colors = THEMES[theme]  # Получение цветовой схемы для выбранной темы
        self.root.configure(bg=colors["bg"])  # Установка фона главного окна
        for widget in self.all_widgets:  # Применение темы ко всем виджетам
            cls = widget.__class__.__name__  # Получение имени класса виджета
            config = {}  # Конфигурация для виджета
            if cls == "Label":  # Настройка для Label
                config = {"bg": colors["bg"], "fg": colors["fg"]}
            elif cls == "Checkbutton":  # Настройка для Checkbutton
                config = {"bg": colors["bg"], "fg": colors["fg"], "selectcolor": colors["check_bg"],
                          "activebackground": colors["bg"], "activeforeground": colors["fg"]}
            elif cls == "Entry":  # Настройка для Entry
                config = {"bg": colors["entry_bg"], "fg": colors["fg"],
                          "insertbackground": colors["fg"], "highlightbackground": colors["highlight"]}
            elif cls == "Text":  # Настройка для Text
                config = {"bg": colors["entry_bg"], "fg": colors["fg"],
                          "insertbackground": colors["fg"]}
            elif cls == "Button":  # Настройка для Button
                config = {"bg": colors["btn_bg"], "fg": colors["btn_fg"],
                          "activebackground": colors["highlight"], "activeforeground": colors["fg"]}
            elif cls == "OptionMenu":  # Настройка для OptionMenu
                config = {"bg": colors["btn_bg"], "fg": colors["btn_fg"],
                          "highlightbackground": colors["highlight"]}
            widget.configure(**config)  # Применение конфигурации к виджету

    # --- Переключение между светлой и тёмной темой ---
    def toggle_theme(self):
        # Переключение темы
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme(self.current_theme)  # Применение новой темы

    # --- Генерация одного пароля на основе настроек ---
    def generate_password(self, length, level):
        letters = string.ascii_letters  # Все буквы (A-Z, a-z)
        digits = string.digits  # Все цифры (0-9)
        symbols = string.punctuation  # Все спецсимволы
        similar_chars = "il1LoO0"  # Похожие символы для исключения
        excluded_chars = self.excluded_chars_var.get()  # Пользовательские исключения

        if self.exclude_similar_var.get():  # Исключение похожих символов, если включено
            letters = ''.join(c for c in letters if c not in similar_chars)
            digits = ''.join(c for c in digits if c not in similar_chars)
            symbols = ''.join(c for c in symbols if c not in similar_chars)

        # Исключение пользовательских символов
        letters = ''.join(c for c in letters if c not in excluded_chars)
        digits = ''.join(c for c in digits if c not in excluded_chars)
        symbols = ''.join(c for c in symbols if c not in excluded_chars)

        required, pool = [], ""  # Обязательные символы и общий пул символов
        if level == 1:  # Уровень 1: только буквы
            required = [random.choice(letters)]
            pool = letters
        elif level == 2:  # Уровень 2: буквы и цифры
            required = [random.choice(letters), random.choice(digits)]
            pool = letters + digits
        elif level == 3:  # Уровень 3: буквы, цифры и спецсимволы
            required = [random.choice(letters), random.choice(
                digits), random.choice(symbols)]
            pool = letters + digits + symbols
        else:
            raise ValueError("Неверный уровень сложности")

        if length < len(required):  # Проверка минимальной длины пароля
            raise ValueError(
                f"Минимальная длина для уровня {level} — {len(required)} символа(ов).")
        if not pool:  # Проверка наличия допустимых символов
            raise ValueError(
                "Набор допустимых символов пуст. Проверьте исключения.")

        # Создание и перемешивание пароля
        pwd = required + [random.choice(pool)
                          for _ in range(length - len(required))]
        random.shuffle(pwd)
        return ''.join(pwd)

    # --- Автоматическое определение уровня сложности по длине ---
    def auto_level(self, length):
        # Уровень 1: <6, Уровень 2: 6-9, Уровень 3: >=10
        return 1 if length < 6 else 2 if length < 10 else 3

    # --- Обработка кнопки "Сгенерировать" ---
    def on_generate(self):
        try:
            length = int(self.length_entry.get())  # Получение длины пароля
            count = int(self.count_entry.get())  # Получение количества паролей
            if count < 1:  # Проверка корректности количества
                raise ValueError("Количество паролей должно быть ≥ 1")

            # Получение уровня сложности
            level = int(self.difficulty_var.get())
            if self.auto_level_var.get():  # Автоматический выбор уровня, если включено
                level = self.auto_level(length)
                self.difficulty_var.set(str(level))

            # Использование set для уникальных паролей
            passwords = set() if self.unique_var.get() else []
            while len(passwords) < count:  # Генерация паролей
                pwd = self.generate_password(length, level)
                if self.unique_var.get():
                    passwords.add(pwd)  # Добавление в set
                else:
                    passwords.append(pwd)  # Добавление в list

            self.result_text.delete("1.0", tk.END)  # Очистка текстового поля
            for pwd in passwords:  # Вывод паролей
                self.result_text.insert(tk.END, pwd + "\n")
        except ValueError as e:
            # Вывод ошибки в диалоговом окне
            messagebox.showerror("Ошибка", str(e))

    # --- Обработка кнопки "Копировать" ---
    def on_copy(self):
        # Получение содержимого текстового поля
        content = self.result_text.get("1.0", tk.END).strip()
        if not content:  # Проверка на пустое содержимое
            messagebox.showwarning("Нечего копировать",
                                   "Сначала сгенерируйте пароли.")
            return
        self.root.clipboard_clear()  # Очистка буфера обмена
        self.root.clipboard_append(content)  # Добавление содержимого в буфер
        self.root.update()  # Обновление буфера
        messagebox.showinfo(
            "Скопировано", "Пароли скопированы в буфер обмена.")  # Уведомление

    # --- Обработка кнопки "Сохранить" ---
    def on_save(self):
        content = self.result_text.get(
            "1.0", tk.END).strip()  # Получение содержимого
        if not content:  # Проверка на пустое содержимое
            messagebox.showwarning(
                "Нечего сохранять", "Сначала сгенерируйте пароли.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".txt",  # Диалог сохранения файла
                                            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv")])
        if path:
            try:
                with open(path, 'w', newline='', encoding='utf-8') as f:
                    if path.endswith(".csv"):  # Сохранение в CSV
                        writer = csv.writer(f)
                        writer.writerow(["Пароль", "Сложность"])
                        for line in content.splitlines():
                            writer.writerow(
                                [line.strip(), self.difficulty_var.get()])
                    else:  # Сохранение в TXT
                        f.write("Сгенерированные пароли:\n" + content)
                messagebox.showinfo(
                    "Успешно", "Пароли сохранены.")  # Уведомление
            except Exception as e:
                # Ошибка сохранения
                messagebox.showerror(
                    "Ошибка", f"Не удалось сохранить файл: {e}")

    # --- Обработка кнопки "Печать" ---
    def on_print(self):
        content = self.result_text.get(
            "1.0", tk.END).strip()  # Получение содержимого
        if not content:  # Проверка на пустое содержимое
            messagebox.showwarning(
                "Нечего печатать", "Сначала сгенерируйте пароли.")
            return
        # Создание временного файла
        with tempfile.NamedTemporaryFile('w', delete=False, suffix=".txt") as f:
            f.write("Сгенерированные пароли:\n" + content)
            path = f.name
        try:
            os.startfile(path, "print")  # Печать файла
        except Exception as e:
            messagebox.showerror("Ошибка печати", str(e))  # Ошибка печати

    # --- Сброс всех настроек к значениям по умолчанию ---
    def reset_settings(self):
        self.length_entry.delete(0, tk.END)  # Сброс длины пароля
        self.length_entry.insert(0, "12")
        self.count_entry.delete(0, tk.END)  # Сброс количества паролей
        self.count_entry.insert(0, "5")
        self.difficulty_var.set("3")  # Сброс уровня сложности
        self.auto_level_var.set(False)  # Сброс автовыбора
        self.unique_var.set(False)  # Сброс уникальности
        # Сброс исключения похожих символов
        self.exclude_similar_var.set(False)
        self.excluded_chars_var.set("")  # Сброс пользовательских исключений
        self.result_text.delete("1.0", tk.END)  # Очистка текстового поля

    # --- Создание всех элементов интерфейса ---
    def create_widgets(self):
        def add(widget):  # Вспомогательная функция для добавления виджета в список
            self.all_widgets.append(widget)
            return widget

        # Поля и кнопки управления
        add(tk.Label(self.root, text="Длина пароля:")).grid(
            row=0, column=0, sticky='e', padx=5, pady=5)  # Метка
        self.length_entry = add(tk.Entry(self.root))  # Поле ввода длины
        self.length_entry.insert(0, "12")  # Значение по умолчанию
        self.length_entry.grid(row=0, column=1, sticky='we', padx=5, pady=5)

        add(tk.Label(self.root, text="Сложность:")).grid(
            row=1, column=0, sticky='e', padx=5)  # Метка
        add(tk.OptionMenu(self.root, self.difficulty_var, "1", "2", "3")).grid(
            row=1, column=1, sticky='we', padx=5, pady=5)  # Выпадающий список
        add(tk.Checkbutton(self.root, text="Автовыбор сложности", variable=self.auto_level_var)).grid(
            row=1, column=2, columnspan=2, sticky='w')  # Чекбокс

        add(tk.Label(self.root, text="Кол-во паролей:")
            ).grid(row=2, column=0, sticky='e', padx=5)  # Метка
        self.count_entry = add(tk.Entry(self.root))  # Поле ввода количества
        self.count_entry.insert(0, "5")  # Значение по умолчанию
        self.count_entry.grid(row=2, column=1, sticky='we', padx=5, pady=5)

        add(tk.Checkbutton(self.root, text="Уникальные пароли", variable=self.unique_var)).grid(
            row=2, column=2, columnspan=2, sticky='w')  # Чекбокс

        # Основные действия
        add(tk.Button(self.root, text="Сгенерировать", command=self.on_generate)).grid(
            row=3, column=0, sticky='we', padx=5, pady=5)  # Кнопка генерации
        add(tk.Button(self.root, text="Копировать", command=self.on_copy)).grid(
            row=3, column=1, sticky='we', padx=5, pady=5)  # Кнопка копирования
        add(tk.Button(self.root, text="Сохранить", command=self.on_save)).grid(
            row=3, column=2, sticky='we', padx=5, pady=5)  # Кнопка сохранения
        add(tk.Button(self.root, text="Печать", command=self.on_print)).grid(
            row=3, column=3, sticky='we', padx=5, pady=5)  # Кнопка печати

        add(tk.Button(self.root, text="Сменить тему", command=self.toggle_theme)).grid(
            row=4, column=0, columnspan=4, sticky='we', padx=5, pady=5)  # Кнопка смены темы

        # Дополнительные настройки
        add(tk.Checkbutton(self.root, text="Избегать похожих символов", variable=self.exclude_similar_var)).grid(
            row=6, column=0, columnspan=2, sticky='w', padx=5)  # Чекбокс
        add(tk.Label(self.root, text="Исключить символы:")).grid(
            row=6, column=2, sticky='e', padx=5)  # Метка
        add(tk.Entry(self.root, textvariable=self.excluded_chars_var)).grid(
            row=6, column=3, sticky='we', padx=5)  # Поле ввода исключений

        add(tk.Button(self.root, text="Сбросить настройки", command=self.reset_settings)).grid(
            row=7, column=0, columnspan=4, sticky='we', padx=5, pady=5)  # Кнопка сброса

        # Вывод результата
        # Текстовое поле для вывода
        self.result_text = add(tk.Text(self.root, wrap='word'))
        self.result_text.grid(row=5, column=0, columnspan=4,
                              sticky='nsew', padx=5, pady=5)

        # Горячие клавиши
        def handle_ctrl_shortcuts(event):
            if (event.state & 0x4) == 0:  # Проверка нажатия Ctrl
                return
            actions = {
                71: self.on_generate,   # G / П
                67: self.on_copy,       # C / С
                83: self.on_save,       # S / Ы
                80: self.on_print,      # P / З
                82: self.reset_settings  # R / К
            }
            # Получение функции по коду клавиши
            func = actions.get(event.keycode)
            if func:
                func()  # Вызов функции
                return "break"

        # Привязка обработчика клавиш
        self.root.bind_all("<KeyPress>", handle_ctrl_shortcuts)


# --- Точка входа в приложение ---
if __name__ == "__main__":
    root = tk.Tk()  # Создание главного окна
    root.title("Генератор паролей")  # Заголовок окна
    root.geometry("700x480")  # Размер окна
    root.minsize(600, 300)  # Минимальный размер окна
    root.columnconfigure([0, 1, 2, 3], weight=1)  # Настройка столбцов
    root.rowconfigure(5, weight=1)  # Настройка строки
    app = PasswordGeneratorApp(root)  # Создание экземпляра приложения
    root.mainloop()  # Запуск основного цикла
