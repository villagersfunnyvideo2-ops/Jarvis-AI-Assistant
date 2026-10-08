import datetime
import os
import time
import threading
import webbrowser

import customtkinter as ctk
from PIL import Image, ImageTk
import speech_recognition as sr
import pyttsx3
import ollama
import pywhatkit
import pyautogui

# Optional browser automation
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except Exception:
    SELENIUM_AVAILABLE = False


# ============================================================
# JARVIS UI
# ============================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class JarvisUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("J.A.R.V.I.S — Ultimate AI Assistant")
        self.geometry("1180x720")
        self.minsize(1000, 650)
        self.configure(fg_color="#050811")

        self.running = True
        self.pulse_up = True
        self.angle = 0
        self.status_color = "#00d9ff"

        # Window layout
        self.grid_columnconfigure(0, weight=5)
        self.grid_columnconfigure(1, weight=7)
        self.grid_rowconfigure(0, weight=1)

        # ---------------- LEFT / CORE ----------------
        self.left_frame = ctk.CTkFrame(
            self, fg_color="#080d18", corner_radius=24,
            border_width=1, border_color="#12334a"
        )
        self.left_frame.grid(row=0, column=0, padx=(18, 9), pady=18, sticky="nsew")

        self.left_frame.grid_rowconfigure(2, weight=1)

        self.title_label = ctk.CTkLabel(
            self.left_frame,
            text="J.A.R.V.I.S",
            font=ctk.CTkFont(family="Arial", size=34, weight="bold"),
            text_color="#00d9ff"
        )
        self.title_label.grid(row=0, column=0, pady=(28, 2))

        self.subtitle_label = ctk.CTkLabel(
            self.left_frame,
            text="PERSONAL AI • LOCAL BRAIN • VOICE CONTROL",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#4f7185"
        )
        self.subtitle_label.grid(row=1, column=0, pady=(0, 4))

        self.canvas = ctk.CTkCanvas(
            self.left_frame, width=360, height=360,
            bg="#080d18", highlightthickness=0
        )
        self.canvas.grid(row=2, column=0, padx=10, pady=5)

        # Reactor rings
        self.ring_outer = self.canvas.create_oval(
            45, 45, 315, 315, outline="#073b55", width=3
        )
        self.ring_mid = self.canvas.create_oval(
            70, 70, 290, 290, outline="#007aa3", width=4
        )
        self.ring_inner = self.canvas.create_oval(
            100, 100, 260, 260, outline="#00d9ff", width=7
        )
        self.core = self.canvas.create_oval(
            137, 137, 223, 223, fill="#dffbff",
            outline="#00d9ff", width=4
        )
        self.core2 = self.canvas.create_oval(
            153, 153, 207, 207, fill="#ffffff",
            outline=""
        )

        # Decorative reactor lines
        for i in range(8):
            import math
            a = math.radians(i * 45)
            x1 = 180 + math.cos(a) * 112
            y1 = 180 + math.sin(a) * 112
            x2 = 180 + math.cos(a) * 145
            y2 = 180 + math.sin(a) * 145
            self.canvas.create_line(
                x1, y1, x2, y2, fill="#12617d", width=2
            )

        self.status_label = ctk.CTkLabel(
            self.left_frame,
            text="●  STANDBY",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#00d9ff"
        )
        self.status_label.grid(row=3, column=0, pady=(4, 4))

        self.mode_label = ctk.CTkLabel(
            self.left_frame,
            text="SYSTEM ONLINE",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#507080"
        )
        self.mode_label.grid(row=4, column=0, pady=(0, 12))

        self.power_button = ctk.CTkButton(
            self.left_frame,
            text="⏻  EXIT JARVIS",
            width=190, height=38,
            corner_radius=18,
            fg_color="#121a28",
            hover_color="#202b3d",
            border_width=1,
            border_color="#284052",
            command=self.close_app
        )
        self.power_button.grid(row=5, column=0, pady=(0, 24))

        # ---------------- RIGHT / DASHBOARD ----------------
        self.right_frame = ctk.CTkFrame(
            self, fg_color="#0b111e", corner_radius=24,
            border_width=1, border_color="#12334a"
        )
        self.right_frame.grid(row=0, column=1, padx=(9, 18), pady=18, sticky="nsew")

        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(3, weight=1)

        top = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        top.grid(row=0, column=0, padx=22, pady=(22, 5), sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top, text="COMMAND CENTER",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#e8f8ff"
        ).grid(row=0, column=0, sticky="w")

        self.online_badge = ctk.CTkLabel(
            top, text="● ONLINE",
            width=105, height=30,
            corner_radius=15,
            fg_color="#09271f",
            text_color="#31f5a2",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.online_badge.grid(row=0, column=1, sticky="e")

        # Stats cards
        stats = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        stats.grid(row=1, column=0, padx=22, pady=12, sticky="ew")
        for i in range(3):
            stats.grid_columnconfigure(i, weight=1)

        self.stat_status = self._card(stats, 0, "STATUS", "READY")
        self.stat_brain = self._card(stats, 1, "AI BRAIN", "OLLAMA")
        self.stat_voice = self._card(stats, 2, "VOICE", "EN-IN")

        # Command display
        command_box = ctk.CTkFrame(
            self.right_frame, fg_color="#070b14",
            corner_radius=15, border_width=1, border_color="#152b3b"
        )
        command_box.grid(row=2, column=0, padx=22, pady=8, sticky="ew")

        ctk.CTkLabel(
            command_box, text="LAST COMMAND",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#527487"
        ).pack(anchor="w", padx=15, pady=(10, 0))

        self.command_label = ctk.CTkLabel(
            command_box, text="Waiting for your command…",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#d9f7ff",
            anchor="w"
        )
        self.command_label.pack(fill="x", padx=15, pady=(2, 12))

        # Logs
        logs_header = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        logs_header.grid(row=3, column=0, padx=22, pady=(12, 0), sticky="ew")
        logs_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            logs_header, text="SYSTEM LOGS",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#8ca9b8"
        ).grid(row=0, column=0, sticky="w")

        self.log_state = ctk.CTkLabel(
            logs_header, text="LIVE",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#31f5a2"
        )
        self.log_state.grid(row=0, column=1, sticky="e")

        self.console_box = ctk.CTkTextbox(
            self.right_frame,
            fg_color="#050810",
            text_color="#67f7d4",
            border_width=1,
            border_color="#102735",
            corner_radius=14,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="word"
        )
        self.console_box.grid(
            row=4, column=0, padx=22, pady=(6, 22), sticky="nsew"
        )
        self.right_frame.grid_rowconfigure(4, weight=1)

        self.log_message("J.A.R.V.I.S interface initialized.")
        self.log_message("Local Ollama brain: ready.")
        self.log_message("Voice engine: ready.")
        self.log_message("Waiting for Boss command...")

        self.protocol("WM_DELETE_WINDOW", self.close_app)
        self.animate_core()

    def _card(self, parent, col, title, value):
        card = ctk.CTkFrame(
            parent, fg_color="#0a1521",
            corner_radius=14, border_width=1, border_color="#153447"
        )
        card.grid(row=0, column=col, padx=4, sticky="ew")
        ctk.CTkLabel(
            card, text=title,
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color="#557384"
        ).pack(anchor="w", padx=12, pady=(9, 0))
        label = ctk.CTkLabel(
            card, text=value,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#ccefff"
        )
        label.pack(anchor="w", padx=12, pady=(1, 9))
        return label

    def update_status(self, status_text, color="#00d9ff"):
        self.after(0, lambda: self._update_status(status_text, color))

    def _update_status(self, status_text, color):
        self.status_label.configure(text=f"●  {status_text.upper()}", text_color=color)
        self.stat_status.configure(text=status_text.upper(), text_color=color)

    def update_command(self, command):
        self.after(0, lambda: self.command_label.configure(
            text=command[:100] if command else "Waiting for your command…"
        ))

    def log_message(self, message):
        def _log():
            self.console_box.configure(state="normal")
            now = datetime.datetime.now().strftime("%H:%M:%S")
            self.console_box.insert("end", f"[{now}]  {message}\n")
            self.console_box.see("end")
            self.console_box.configure(state="disabled")
        self.after(0, _log)

    def animate_core(self):
        if not self.running:
            return

        try:
            width = float(self.canvas.itemcget(self.ring_inner, "width"))
            if self.pulse_up:
                width += 0.45
                if width >= 10:
                    self.pulse_up = False
            else:
                width -= 0.45
                if width <= 4:
                    self.pulse_up = True

            self.canvas.itemconfig(self.ring_inner, width=width)

            # Small breathing effect on the core
            size = 43 + int(width * 0.7)
            center = 180
            self.canvas.coords(
                self.core,
                center-size, center-size,
                center+size, center+size
            )
            self.canvas.coords(
                self.core2,
                center-size//2, center-size//2,
                center+size//2, center+size//2
            )

            self.after(45, self.animate_core)
        except Exception:
            pass

    def close_app(self):
        self.running = False
        self.destroy()


# ============================================================
# GLOBAL UI
# ============================================================

app = None
engine = None


def ui_status(text, color="#00d9ff"):
    if app:
        app.update_status(text, color)


def ui_log(text):
    if app:
        app.log_message(text)


def ui_command(text):
    if app:
        app.update_command(text)


# ============================================================
# VOICE AND SPEECH
# ============================================================

def init_voice():
    global engine
    try:
        engine = pyttsx3.init("sapi5")
        voices = engine.getProperty("voices")
        if voices:
            engine.setProperty("voice", voices[0].id)
        engine.setProperty("rate", 175)
        engine.setProperty("volume", 1.0)
    except Exception as e:
        engine = pyttsx3.init()
        ui_log(f"Voice fallback active: {e}")


def speak(text):
    print(f"Jarvis: {text}")
    ui_log(f"JARVIS: {text}")
    ui_status("SPEAKING", "#00d9ff")

    try:
        if engine:
            engine.say(text)
            engine.runAndWait()
    except Exception as e:
        ui_log(f"Speech error: {e}")

    ui_status("STANDBY", "#00d9ff")


def wish_me():
    hour = datetime.datetime.now().hour
    if 6 <= hour < 12:
        speak("Good Morning Boss!")
    elif 12 <= hour < 18:
        speak("Good Afternoon Boss!")
    else:
        speak("Good Evening and Good Night Boss!")
    speak("Main taiyaar hu. Aapko kya madad chahiye?")


def take_command():
    r = sr.Recognizer()
    r.pause_threshold = 1

    ui_status("LISTENING", "#00ff99")
    ui_log("Microphone active. Listening...")

    try:
        with sr.Microphone() as source:
            audio = r.listen(source)
        ui_status("PROCESSING", "#ffd166")
        ui_log("Voice captured. Recognizing...")

        query = r.recognize_google(audio, language="en-in")
        query = query.lower()

        print(f"User ne kaha: {query}")
        ui_command(query)
        ui_log(f"USER: {query}")
        ui_status("STANDBY", "#00d9ff")
        return query

    except Exception as e:
        ui_log("Could not understand voice command.")
        ui_status("STANDBY", "#00d9ff")
        return "none"


# ============================================================
# FILE / FOLDER MANAGEMENT
# ============================================================

def create_folder(folder_name):
    path = os.path.join(os.path.expanduser("~"), "Desktop", folder_name)
    if not os.path.exists(path):
        os.makedirs(path)
        speak(f"Boss, aapka folder {folder_name} desktop par ban gaya hai.")
    else:
        speak("Yeh folder pehle se bana hua hai.")


def create_secret_folder(folder_name):
    path = os.path.join(os.path.expanduser("~"), "Desktop", folder_name)
    if not os.path.exists(path):
        os.makedirs(path)
        os.system(f'attrib +h "{path}"')
        speak(f"Boss, aapka secret private folder {folder_name} banakar hide kar diya hai.")
    else:
        speak("Yeh private folder pehle se hi maujood hai.")


def manage_files(action, filename):
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    file_path = os.path.join(desktop_path, filename)

    if action == "create":
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Created by Jarvis AI")
        speak(f"Boss, {filename} file bana di gayi hai.")

    elif action == "delete":
        if os.path.exists(file_path):
            os.remove(file_path)
            speak(f"Boss, {filename} file delete kar di gayi hai.")
        else:
            speak("File nahi mili.")


def hide_photo(photo_name):
    path = os.path.join(os.path.expanduser("~"), "Desktop", photo_name)
    if os.path.exists(path):
        os.system(f'attrib +h "{path}"')
        speak(f"Boss, {photo_name} ko maine hide kar diya hai.")
    else:
        speak("Boss, desktop par is naam ki koi photo nahi mili.")


def delete_photo(photo_name):
    path = os.path.join(os.path.expanduser("~"), "Desktop", photo_name)
    if os.path.exists(path):
        os.remove(path)
        speak(f"Boss, {photo_name} ko hamesha ke liye delete kar diya gaya hai.")
    else:
        speak("Boss, desktop par is naam ki koi photo nahi mili.")


# ============================================================
# WEB / MUSIC / CALL / WHATSAPP
# ============================================================

def open_website(url):
    speak(f"Khol raha hu {url}")
    webbrowser.open(f"https://{url}")


def play_music(song_name):
    speak(f"YouTube par {song_name} chala raha hu.")
    pywhatkit.playonyt(song_name)


def make_call(phone_number):
    speak(f"Number {phone_number} par call laga raha hu.")
    os.system(f"adb shell am start -a android.intent.action.CALL -d tel:{phone_number}")


def send_whatsapp_message(number, message):
    speak("WhatsApp par message bheja ja raha hai.")
    pywhatkit.sendwhatmsg_instantly(
        f"+91{number}", message, wait_time=15, tab_close=True
    )
    speak("Message send kar diya gaya hai boss.")


# ============================================================
# LIVE WEBSITE CONTROL
# ============================================================

def live_amazon_control():
    speak("Live Website Voice Control mode chalu ho gaya hai.")
    while True:
        command = take_command()

        if "click" in command:
            pyautogui.click()
            speak("Click kar diya boss.")
        elif "double click" in command:
            pyautogui.doubleClick()
            speak("Double click kar diya.")
        elif "scroll down" in command or "niche karo" in command:
            pyautogui.scroll(-5)
            speak("Niche scroll kar diya.")
        elif "scroll up" in command or "uper karo" in command:
            pyautogui.scroll(5)
            speak("Uper scroll kar diya.")
        elif "type" in command or "likho" in command:
            text = command.replace("type", "").replace("likho", "").strip()
            pyautogui.write(text, interval=0.05)
            speak(f"{text} type kar diya hai.")
        elif "enter" in command:
            pyautogui.press("enter")
            speak("Enter dabaya.")
        elif "tab" in command:
            pyautogui.press("tab")
            speak("Agla field selected.")
        elif "backspace" in command or "hatao" in command:
            pyautogui.press("backspace")
        elif "stop" in command or "bas" in command or "exit" in command:
            speak("Live control mode band kar diya gaya hai.")
            break


def fill_live_form():
    speak("Live form filling start ho rahi hai.")
    time.sleep(2)

    while True:
        speak("Is box me kya type karna hai boss? Ya stop boliye.")
        text_to_type = take_command()

        if "stop" in text_to_type or text_to_type == "none":
            speak("Form filling rok di gayi hai.")
            break

        pyautogui.write(text_to_type, interval=0.05)
        pyautogui.press("tab")
        speak("Type kar diya hai aur agle box par move ho gaya hu.")


# ============================================================
# AMAZON AUTOMATION
# ============================================================

def amazon_order_bot():
    if not SELENIUM_AVAILABLE:
        speak("Selenium available nahi hai. Pehle required packages install kijiye.")
        return

    speak("Boss, aap Amazon par kya order karna chahte hain?")
    item_name = take_command()

    if item_name == "none" or not item_name:
        speak("Item ka naam samajh nahi aaya. Process cancel kar raha hu.")
        return

    speak(f"Thik hai boss, Amazon par {item_name} search kar raha hu.")

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        driver.get("https://www.amazon.in")
        wait = WebDriverWait(driver, 15)

        search_box = wait.until(
            EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
        )
        search_box.send_keys(item_name)
        search_box.submit()

        first_product = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@data-component-type='s-search-result']//h2/a")
            )
        )

        speak("Pehla item mil gaya hai, ise open kar raha hu.")
        first_product.click()

        driver.switch_to.window(driver.window_handles[-1])

        try:
            buy_now_btn = wait.until(
                EC.element_to_be_clickable((By.ID, "buy-now-button"))
            )
            buy_now_btn.click()
        except Exception:
            add_cart_btn = wait.until(
                EC.element_to_be_clickable((By.ID, "add-to-cart-button"))
            )
            add_cart_btn.click()
            speak("Item cart me dal diya hai.")
            driver.get("https://www.amazon.in/gp/cart/view.html")

            checkout_btn = wait.until(
                EC.element_to_be_clickable(
                    (By.NAME, "proceedToRetailCheckout")
                )
            )
            checkout_btn.click()

        speak("Login ki zarurat ho to browser me manually login kijiye.")
        speak("Security ke liye final payment aap khud karein.")

    except Exception:
        speak("Amazon UI change ya error ke karan automation fail hua.")
        speak("Live Voice Control Mode start kar raha hu.")
        live_amazon_control()


# ============================================================
# SYSTEM CONTROL
# ============================================================

def system_control(command):
    if "volume up" in command or "aawaz badhao" in command:
        pyautogui.press("volumeup", presses=5)
        speak("Aawaz badha di hai.")

    elif "volume down" in command or "aawaz kam karo" in command:
        pyautogui.press("volumedown", presses=5)
        speak("Aawaz kam kar di hai.")

    elif "mute" in command or "aawaz band karo" in command:
        pyautogui.press("volumemute")
        speak("Audio mute kar diya gaya hai.")

    elif "screenshot" in command or "photo lo" in command:
        desktop_path = os.path.join(
            os.path.expanduser("~"), "Desktop", "Jarvis_Screenshot.png"
        )
        pyautogui.screenshot(desktop_path)
        speak("Screen ka screenshot desktop par save kar diya hai.")

    elif "lock system" in command or "computer lock karo" in command:
        speak("System lock kar raha hu boss.")
        os.system("rundll32.exe user32.dll,LockWorkStation")


def quick_web_search():
    speak("Aap Google par kya search karna chahte hain boss?")
    search_query = take_command()

    if search_query != "none" and search_query:
        speak(f"Google par {search_query} search kar raha hu.")
        pywhatkit.search(search_query)


# ============================================================
# OLLAMA LOCAL BRAIN
# ============================================================

def ask_ollama(user_prompt):
    system_instruction = (
        "You are Jarvis, a powerful desktop AI assistant. "
        "Keep responses short, direct, and helpful."
    )

    ui_status("THINKING", "#b980ff")
    ui_log("Sending request to local Ollama brain...")

    try:
        response = ollama.chat(
            model="llama3",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ]
        )
        ui_status("STANDBY", "#00d9ff")
        return response["message"]["content"]

    except Exception:
        ui_status("STANDBY", "#00d9ff")
        return "Sorry Boss, Ollama local model abhi connect nahi ho pa raha hai."


# ============================================================
# MAIN COMMAND ENGINE
# ============================================================

def jarvis_loop():
    try:
        init_voice()
        wish_me()

        while app and app.running:
            query = take_command()

            if query == "none":
                continue

            if "bye" in query or "quit" in query or "so jao" in query:
                speak("Good night boss, take care!")
                break

            elif "live mode" in query or "live control" in query or "live amazon" in query:
                live_amazon_control()

            elif "whatsapp message" in query or "whatsapp karo" in query:
                speak("Kisko message bhejna hai? Number boliye.")
                num = take_command().replace(" ", "")
                if num != "none":
                    speak("Kya message bhejna hai boss?")
                    msg = take_command()
                    if msg != "none":
                        send_whatsapp_message(num, msg)

            elif "fill form" in query or "form bharo" in query:
                fill_live_form()

            elif "amazon order" in query or "order kardo" in query:
                amazon_order_bot()

            elif any(k in query for k in [
                "volume", "aawaz", "mute", "screenshot", "lock system"
            ]):
                system_control(query)

            elif "search google" in query or "google par khojo" in query:
                quick_web_search()

            elif "hide photo" in query or "photo chupao" in query:
                speak("Desktop ki kaun si photo hide karni hai?")
                p_name = take_command().replace(" ", "")
                if p_name != "none":
                    hide_photo(p_name)

            elif "delete photo" in query or "photo hatao" in query:
                speak("Kaun si photo delete karni hai?")
                p_name = take_command().replace(" ", "")
                if p_name != "none":
                    delete_photo(p_name)

            elif "play" in query or "gana bajao" in query:
                song = query.replace("play", "").replace("gana bajao", "").strip()
                if song:
                    play_music(song)
                else:
                    speak("Kaun sa gana bajana hai boss?")

            elif "secret folder" in query or "private folder" in query:
                speak("Secret folder ka kya naam rakhu?")
                name = take_command()
                if name != "none":
                    create_secret_folder(name)

            elif "create folder" in query or "folder banao" in query:
                speak("Folder ka naam kya hona chahiye?")
                name = take_command()
                if name != "none":
                    create_folder(name)

            elif "create file" in query:
                speak("File ka kya naam rakhu extension ke sath?")
                fname = take_command()
                if fname != "none":
                    manage_files("create", fname)

            elif query.startswith("open ") or " open " in query:
                domain = query.replace("open ", "").strip()
                if "." not in domain:
                    domain += ".com"
                open_website(domain)

            elif "call" in query or "phone lagao" in query:
                speak("Kisko call milana hai? Kripya number boliye.")
                number = take_command().replace(" ", "")
                if number != "none":
                    make_call(number)

            else:
                reply = ask_ollama(query)
                speak(reply)

    except Exception as e:
        ui_log(f"MAIN ENGINE ERROR: {e}")
        ui_status("ERROR", "#ff5577")


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    app = JarvisUI()

    # Important: Voice/AI engine runs outside Tkinter main loop.
    worker = threading.Thread(target=jarvis_loop, daemon=True)
    worker.start()

    app.mainloop()
