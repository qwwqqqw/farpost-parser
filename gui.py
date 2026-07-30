import os

import sys

if getattr(sys, 'frozen', False):

    BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

else:

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:

    sys.path.insert(0, BASE_DIR)

import threading

import customtkinter as ctk

from dotenv import load_dotenv, set_key

from loguru import logger

from src.scheduler.jobs import ParserScheduler

from src.config import get_settings

ENV_FILE = ".env"

load_dotenv(ENV_FILE)

ctk.set_appearance_mode("dark")

ctk.set_default_color_theme("green")

class App(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Farpost Parser GUI")

        self.geometry("700x700")

        self.grid_rowconfigure(0, weight=1)

        self.grid_columnconfigure(0, weight=1)

        self.scrollable_frame = ctk.CTkScrollableFrame(self)

        self.scrollable_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.frame_url = ctk.CTkFrame(self.scrollable_frame)

        self.frame_url.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        self.frame_url.grid_columnconfigure(0, weight=1)

        self.label_url = ctk.CTkLabel(self.frame_url, text="Ссылка Farpost", font=ctk.CTkFont(size=16, weight="bold"))

        self.label_url.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.url_input_frame = ctk.CTkFrame(self.frame_url, fg_color="transparent")

        self.url_input_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.url_input_frame.grid_columnconfigure(0, weight=1)

        self.entry_url = ctk.CTkEntry(self.url_input_frame, placeholder_text="https://www.farpost.ru/...")

        self.entry_url.grid(row=0, column=0, padx=(0, 0), sticky="ew")

        self.entry_url.insert(0, os.getenv("FARPOST_URL", ""))

        self._fix_paste(self.entry_url)

        self.frame_settings = ctk.CTkFrame(self.scrollable_frame)

        self.frame_settings.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="ew")

        self.frame_settings.grid_columnconfigure((0, 1), weight=1)

        self.label_settings = ctk.CTkLabel(self.frame_settings, text="Поведение парсера", font=ctk.CTkFont(size=16, weight="bold"))

        self.label_settings.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        self.label_interval = ctk.CTkLabel(self.frame_settings, text="Интервал (мин):")

        self.label_interval.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")

        self.entry_interval = ctk.CTkEntry(self.frame_settings)

        self.entry_interval.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.entry_interval.insert(0, os.getenv("PARSER_INTERVAL_MINUTES", "15"))

        self._fix_paste(self.entry_interval)

        self.label_max_listings = ctk.CTkLabel(self.frame_settings, text="Макс объявлений за раз:")

        self.label_max_listings.grid(row=1, column=1, padx=10, pady=(0, 5), sticky="w")

        self.entry_max_listings = ctk.CTkEntry(self.frame_settings)

        self.entry_max_listings.grid(row=2, column=1, padx=10, pady=(0, 10), sticky="ew")

        self.entry_max_listings.insert(0, os.getenv("MAX_LISTINGS_PER_RUN", "50"))

        self._fix_paste(self.entry_max_listings)

        self.frame_telegram = ctk.CTkFrame(self.scrollable_frame)

        self.frame_telegram.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="ew")

        self.frame_telegram.grid_columnconfigure(0, weight=1)

        self.label_telegram = ctk.CTkLabel(self.frame_telegram, text="Telegram", font=ctk.CTkFont(size=16, weight="bold"))

        self.label_telegram.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.label_token = ctk.CTkLabel(self.frame_telegram, text="Bot Token:")

        self.label_token.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")

        self.token_frame = ctk.CTkFrame(self.frame_telegram, fg_color="transparent")

        self.token_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.token_frame.grid_columnconfigure(0, weight=1)

        self.entry_token = ctk.CTkEntry(self.token_frame, show="*")

        self.entry_token.grid(row=0, column=0, sticky="ew")

        self.btn_toggle_token = ctk.CTkButton(self.token_frame, text="👁", width=30, command=lambda: self.toggle_visibility(self.entry_token, self.btn_toggle_token))

        self.btn_toggle_token.grid(row=0, column=1, padx=(5, 0))

        self.entry_token.insert(0, os.getenv("TELEGRAM_BOT_TOKEN", ""))

        self._fix_paste(self.entry_token)

        self.label_chat_id = ctk.CTkLabel(self.frame_telegram, text="Chat ID:")

        self.label_chat_id.grid(row=3, column=0, padx=10, pady=(0, 5), sticky="w")

        self.chat_id_frame = ctk.CTkFrame(self.frame_telegram, fg_color="transparent")

        self.chat_id_frame.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.chat_id_frame.grid_columnconfigure(0, weight=1)

        self.entry_chat_id = ctk.CTkEntry(self.chat_id_frame, show="*")

        self.entry_chat_id.grid(row=0, column=0, sticky="ew")

        self.btn_toggle_chat_id = ctk.CTkButton(self.chat_id_frame, text="👁", width=30, command=lambda: self.toggle_visibility(self.entry_chat_id, self.btn_toggle_chat_id))

        self.btn_toggle_chat_id.grid(row=0, column=1, padx=(5, 0))

        self.entry_chat_id.insert(0, os.getenv("TELEGRAM_CHAT_ID", ""))

        self._fix_paste(self.entry_chat_id)

        self.frame_proxy = ctk.CTkFrame(self.scrollable_frame)

        self.frame_proxy.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="ew")

        self.frame_proxy.grid_columnconfigure(0, weight=1)

        self.label_proxy = ctk.CTkLabel(self.frame_proxy, text="Прокси", font=ctk.CTkFont(size=16, weight="bold"))

        self.label_proxy.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.use_proxy_var = ctk.StringVar(value=os.getenv("USE_PROXY", "false").lower())

        self.checkbox_proxy = ctk.CTkCheckBox(self.frame_proxy, text="Использовать прокси", variable=self.use_proxy_var, onvalue="true", offvalue="false")

        self.checkbox_proxy.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")

        self.label_proxy_url = ctk.CTkLabel(self.frame_proxy, text="Proxy URL:")

        self.label_proxy_url.grid(row=2, column=0, padx=10, pady=(0, 5), sticky="w")

        self.proxy_frame = ctk.CTkFrame(self.frame_proxy, fg_color="transparent")

        self.proxy_frame.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.proxy_frame.grid_columnconfigure(0, weight=1)

        self.entry_proxy_url = ctk.CTkEntry(self.proxy_frame, show="*")

        self.entry_proxy_url.grid(row=0, column=0, sticky="ew")

        self.btn_toggle_proxy = ctk.CTkButton(self.proxy_frame, text="👁", width=30, command=lambda: self.toggle_visibility(self.entry_proxy_url, self.btn_toggle_proxy))

        self.btn_toggle_proxy.grid(row=0, column=1, padx=(5, 0))

        self.entry_proxy_url.insert(0, os.getenv("PROXY_URL", ""))

        self._fix_paste(self.entry_proxy_url)

        self.frame_run = ctk.CTkFrame(self.scrollable_frame)

        self.frame_run.grid(row=4, column=0, padx=10, pady=(20, 10), sticky="ew")

        self.frame_run.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.btn_save = ctk.CTkButton(self.frame_run, text="Сохранить", command=self.save_settings, fg_color="gray")

        self.btn_save.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.btn_run_once = ctk.CTkButton(self.frame_run, text="Запуск (Один раз)", command=self.run_once)

        self.btn_run_once.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.btn_run_start = ctk.CTkButton(self.frame_run, text="Запуск (Фон 24/7)", command=self.run_start)

        self.btn_run_start.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        self.btn_stop = ctk.CTkButton(self.frame_run, text="Стоп", command=self.stop_parser, fg_color="#c93434", hover_color="#a32a2a", state="disabled")

        self.btn_stop.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

        self.label_status = ctk.CTkLabel(self.scrollable_frame, text="Готов к запуску.", text_color="gray")

        self.label_status.grid(row=5, column=0, padx=10, pady=10)

        self.frame_logs = ctk.CTkFrame(self.scrollable_frame)

        self.frame_logs.grid(row=6, column=0, padx=10, pady=(10, 20), sticky="nsew")

        self.frame_logs.grid_columnconfigure(0, weight=1)

        self.label_logs = ctk.CTkLabel(self.frame_logs, text="Логи работы", font=ctk.CTkFont(size=14, weight="bold"))

        self.label_logs.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        self.textbox_logs = ctk.CTkTextbox(self.frame_logs, height=200, state="disabled")

        self.textbox_logs.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        logger.add(self.gui_log_sink, format="{time:HH:mm:ss} | {level} | {message}")

    def gui_log_sink(self, message):

        def append_text():

            self.textbox_logs.configure(state="normal")

            is_error = hasattr(message, "record") and message.record["level"].name in ("ERROR", "CRITICAL")

            is_warn = hasattr(message, "record") and message.record["level"].name == "WARNING"

            if is_error:

                self.textbox_logs.insert("end", message, "error")

                self.textbox_logs.tag_config("error", foreground="#ff4d4d")

            elif is_warn:

                self.textbox_logs.insert("end", message, "warning")

                self.textbox_logs.tag_config("warning", foreground="#ffcc00")

            else:

                self.textbox_logs.insert("end", message)

            self.textbox_logs.see("end")

            self.textbox_logs.configure(state="disabled")

        self.after(0, append_text)

    def _fix_paste(self, entry: ctk.CTkEntry):

        """Bind Ctrl+V paste directly to the underlying tk.Entry so it works
        regardless of the keyboard layout (including Russian)."""

        inner = entry._entry                                            

        def do_paste(event=None):

            try:

                text = entry.clipboard_get()

                try:

                    inner.delete("sel.first", "sel.last")

                except Exception:

                    pass

                inner.insert("insert", text)

            except Exception:

                pass

            return "break"

        inner.bind("<Control-KeyPress>", lambda e: do_paste() if e.keycode == 86 else None)

        inner.bind("<Control-v>", do_paste)

        inner.bind("<Control-V>", do_paste)

    def save_settings(self):

        env_dict = {

            "FARPOST_URL": self.entry_url.get().strip(),

            "PARSER_INTERVAL_MINUTES": self.entry_interval.get().strip(),

            "MAX_LISTINGS_PER_RUN": self.entry_max_listings.get().strip(),

            "TELEGRAM_BOT_TOKEN": self.entry_token.get().strip(),

            "TELEGRAM_CHAT_ID": self.entry_chat_id.get().strip(),

            "USE_PROXY": self.use_proxy_var.get(),

            "PROXY_URL": self.entry_proxy_url.get().strip(),

            "FARPOST_ENABLED": "true"

        }

        if not os.path.exists(ENV_FILE):

            open(ENV_FILE, 'w').close()

        for key, value in env_dict.items():

            set_key(ENV_FILE, key, value)

            os.environ[key] = value

        self.label_status.configure(text="Настройки успешно сохранены в .env", text_color="green")

    def execute_parser(self, mode):

        self.btn_run_once.configure(state="disabled")

        self.btn_run_start.configure(state="disabled")

        self.btn_stop.configure(state="normal")

        self.label_status.configure(text="Парсер запущен...", text_color="yellow")

        try:

            self.save_settings()

            load_dotenv(ENV_FILE, override=True)

            settings = get_settings()

            self.scheduler = ParserScheduler(settings=settings)

            if mode == "once":

                self.scheduler.parse_and_notify_job()

                self.label_status.configure(text="Парсинг (один раз) завершен!", text_color="green")

            elif mode == "start":

                self.label_status.configure(text="Парсер работает в фоновом режиме. Окно можно свернуть.", text_color="yellow")

                self.scheduler.start()

        except Exception as e:

            self.label_status.configure(text=f"Ошибка: {str(e)}", text_color="red")

            logger.error(f"GUI Execution error: {e}")

        finally:

            if mode == "once":

                self.btn_run_once.configure(state="normal")

                self.btn_run_start.configure(state="normal")

                self.btn_stop.configure(state="disabled")

    def stop_parser(self):

        if hasattr(self, 'scheduler') and self.scheduler:

            self.scheduler.stop()

            self.label_status.configure(text="Парсер остановлен.", text_color="red")

            self.btn_run_once.configure(state="normal")

            self.btn_run_start.configure(state="normal")

            self.btn_stop.configure(state="disabled")

    def run_once(self):

        thread = threading.Thread(target=self.execute_parser, args=("once",))

        thread.daemon = True

        thread.start()

    def toggle_visibility(self, entry: ctk.CTkEntry, button: ctk.CTkButton):

        if entry.cget("show") == "*":

            entry.configure(show="")

            button.configure(text="🔒")

        else:

            entry.configure(show="*")

            button.configure(text="👁")

    def run_start(self):

        thread = threading.Thread(target=self.execute_parser, args=("start",))

        thread.daemon = True

        thread.start()

if __name__ == "__main__":

    app = App()

    app.mainloop()
