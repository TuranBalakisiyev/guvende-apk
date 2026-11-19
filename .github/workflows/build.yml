import json
import os
import smtplib
import sqlite3
import threading
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.utils import platform

DB_NAME = "guvende_pro.db"
CACHED_LOCATION = None


def get_location():
    global CACHED_LOCATION
    if platform == "android":
        try:
            from plyer import gps
        except Exception:
            pass

    try:
        req = urllib.request.Request("https://ipwho.is/", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("success"):
                lat, lng = data["latitude"], data["longitude"]
                city = data.get("city", "")
                CACHED_LOCATION = (f"https://www.google.com/maps?q={lat},{lng}", f"{lat}, {lng} ({city})")
                return CACHED_LOCATION
    except Exception:
        pass

    if CACHED_LOCATION:
        return CACHED_LOCATION
    return ("https://www.google.com/maps?q=40.4093,49.8671", "40.4093, 49.8671 (Standart)")


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY, email TEXT, app_password TEXT, pin TEXT, child_name TEXT)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, email TEXT)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, status TEXT, time TEXT, details TEXT)"
    )

    cursor.execute("SELECT COUNT(*) FROM settings")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO settings (email, app_password, pin, child_name) VALUES (?, ?, ?, ?)",
            ("valideyn@gmail.com", "", "1234", "Övladım"),
        )

    cursor.execute("SELECT COUNT(*) FROM contacts")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)",
            ("Ana / Ata", "994501234567", "valideyn@gmail.com"),
        )

    conn.commit()
    conn.close()


def get_settings():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT email, app_password, pin, child_name FROM settings WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return {"email": row[0], "app_password": row[1], "pin": row[2], "child_name": row[3]}


def get_all_contacts():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, phone, email FROM contacts")
    rows = cursor.fetchall()
    conn.close()
    return rows


def save_history(status, details):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO history (status, time, details) VALUES (?, ?, ?)", (status, now, details))
    conn.commit()
    conn.close()


def send_to_all_emails(contacts, subject, body):
    settings = get_settings()
    sender = settings["email"]
    pwd = settings["app_password"]
    sent_count = 0

    if pwd and sender and sender != "valideyn@gmail.com":
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587, timeout=8)
            server.starttls()
            server.login(sender, pwd)

            receivers = set()
            if sender:
                receivers.add(sender)
            for c in contacts:
                if c[3] and "@" in c[3]:
                    receivers.add(c[3].strip())

            for r_email in receivers:
                msg = MIMEMultipart()
                msg["From"] = sender
                msg["To"] = r_email
                msg["Subject"] = subject
                msg.attach(MIMEText(body, "plain", "utf-8"))
                server.sendmail(sender, r_email, msg.as_string())
                sent_count += 1
            server.quit()
        except Exception:
            pass
    return sent_count


class GuvendeRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=14, spacing=10, **kwargs)
        init_db()
        self.settings = get_settings()
        self.contacts = get_all_contacts()
        self.tracking_active = False

        self.title_label = Label(
            text="GÜVƏNDƏ PRO (Mobil Test)",
            font_size="20sp",
            bold=True,
            size_hint_y=None,
            height=38,
        )
        self.add_widget(self.title_label)

        self.sub_label = Label(
            text=self._get_subtitle(),
            font_size="13sp",
            size_hint_y=None,
            height=28,
        )
        self.add_widget(self.sub_label)

        btn_row = BoxLayout(orientation="horizontal", spacing=12, size_hint_y=None, height=110)
        self.safe_btn = Button(text="MƏN\nYAXŞIYAM", font_size="16sp", bold=True)
        self.safe_btn.bind(on_press=lambda *_: self.trigger_alert("YAXŞIYAM"))
        btn_row.add_widget(self.safe_btn)

        self.sos_btn = Button(text="TƏCİLİ\nSOS", font_size="16sp", bold=True)
        self.sos_btn.bind(on_press=lambda *_: self.trigger_alert("SOS"))
        btn_row.add_widget(self.sos_btn)
        self.add_widget(btn_row)

        self.status_label = Label(
            text="Hazırdır",
            font_size="13sp",
            size_hint_y=None,
            height=32,
        )
        self.add_widget(self.status_label)

        self.stop_btn = Button(
            text="8 Saatlıq Canlı İzləməni Dayandır",
            size_hint_y=None,
            height=42,
            disabled=True,
        )
        self.stop_btn.bind(on_press=lambda *_: self.stop_tracking())
        self.add_widget(self.stop_btn)

        action_row = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=44)
        wa_btn = Button(text="WhatsApp Linki Aç")
        wa_btn.bind(on_press=lambda *_: self.open_whatsapp_link())
        action_row.add_widget(wa_btn)

        map_btn = Button(text="Cari Məkan")
        map_btn.bind(on_press=lambda *_: self.open_map_link())
        action_row.add_widget(map_btn)
        self.add_widget(action_row)

        self.history_label = Label(
            text="",
            font_size="12sp",
            halign="left",
            valign="top",
            size_hint_y=None,
        )
        self.history_label.bind(texture_size=self._update_history_height)

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.history_label)
        self.add_widget(scroll)
        self.refresh_history()

        pin_row = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=44)
        self.pin_input = TextInput(hint_text="PIN (1234)", password=True, multiline=False)
        pin_row.add_widget(self.pin_input)

        settings_btn = Button(text="Ayarlar & Nömrələr")
        settings_btn.bind(on_press=lambda *_: self.open_settings_popup())
        pin_row.add_widget(settings_btn)
        self.add_widget(pin_row)

        threading.Thread(target=get_location, daemon=True).start()

    def _update_history_height(self, instance, value):
        instance.height = max(value[1] + 10, 120)

    def _get_subtitle(self):
        self.contacts = get_all_contacts()
        count = len(self.contacts)
        first_phone = f"+{self.contacts[0][2]}" if count > 0 else "Nömrə yoxdur"
        return f"İzlənən: {self.settings['child_name']} | {count} nəfər ({first_phone})"

    def show_msg(self, title, text):
        box = BoxLayout(orientation="vertical", padding=10, spacing=10)
        lbl = Label(text=text)
        box.add_widget(lbl)
        ok_btn = Button(text="Bağla", size_hint_y=None, height=42)
        popup = Popup(title=title, content=box, size_hint=(0.85, 0.4))
        ok_btn.bind(on_press=popup.dismiss)
        box.add_widget(ok_btn)
        popup.open()

    def trigger_alert(self, action_type):
        self.contacts = get_all_contacts()
        if not self.contacts:
            self.show_msg("Diqqət", "Əlaqə nömrəsi əlavə edilməyib.")
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        map_url, coords = get_location()

        if action_type == "SOS":
            subject = "TƏCİLİ SOS - GÜVƏNDƏ"
            body = f"TƏCİLİ SOS! {self.settings['child_name']} | Vaxt: {timestamp} | Məkan: {map_url}"
            status_text = "SOS + 8S KONUM"
            Clock.schedule_once(lambda *_: setattr(self.status_label, "text", "SOS göndərilir və 8s izləmə başlayır..."))
        else:
            subject = "Mən Yaxşıyam - GÜVƏNDƏ"
            body = f"{self.settings['child_name']} yaxşıdır. Vaxt: {timestamp} | Məkan: {map_url}"
            status_text = "MƏN YAXŞIYAM"
            Clock.schedule_once(lambda *_: setattr(self.status_label, "text", "Məlumat göndərilir..."))

        def worker():
            sent = send_to_all_emails(self.contacts, subject, body)
            save_history(status_text, f"{coords} | Mail: {sent}")
            Clock.schedule_once(lambda *_: self.refresh_history())
            Clock.schedule_once(lambda *_: setattr(self.status_label, "text", f"{status_text} qeydə alındı (Mail: {sent})"))

            if action_type == "SOS" and not self.tracking_active:
                self.tracking_active = True
                Clock.schedule_once(lambda *_: setattr(self.stop_btn, "disabled", False))
                self._run_8hour_tracking()

        threading.Thread(target=worker, daemon=True).start()

    def _run_8hour_tracking(self):
        end_time = datetime.now() + timedelta(hours=8)
        first_cycle = True
        while self.tracking_active and datetime.now() < end_time:
            wait_secs = 60 if first_cycle else 300
            first_cycle = False
            for _ in range(wait_secs):
                if not self.tracking_active or datetime.now() >= end_time:
                    break
                rem_mins = int((end_time - datetime.now()).total_seconds() // 60)
                Clock.schedule_once(lambda *_, m=rem_mins: setattr(self.stop_btn, "text", f"İzləməni Dayandır ({m} dəq qalıb)"))
                time.sleep(1)

            if not self.tracking_active or datetime.now() >= end_time:
                break

            now_str = datetime.now().strftime("%H:%M:%S")
            map_url, coords = get_location()
            current_contacts = get_all_contacts()
            msg = f"Canlı Məkan ({now_str}) - {self.settings['child_name']}: {map_url}"
            sent = send_to_all_emails(current_contacts, f"Canlı Məkan ({now_str})", msg)
            save_history("8S CANLI KONUM", f"{coords} | Mail: {sent}")
            Clock.schedule_once(lambda *_: self.refresh_history())

        self.tracking_active = False
        Clock.schedule_once(
            lambda *_: (
                setattr(self.stop_btn, "disabled", True),
                setattr(self.stop_btn, "text", "8 Saatlıq Canlı İzləməni Dayandır"),
            )
        )

    def stop_tracking(self):
        self.tracking_active = False
        self.stop_btn.disabled = True
        self.stop_btn.text = "8 Saatlıq Canlı İzləməni Dayandır"
        self.status_label.text = "8 saatlıq canlı izləmə dayandırıldı."

    def open_whatsapp_link(self):
        contacts = get_all_contacts()
        if not contacts:
            self.show_msg("Xəta", "Nömrə yoxdur.")
            return
        phone = contacts[0][2].replace("+", "").replace(" ", "")
        map_url, _ = get_location()
        text = urllib.parse.quote(f"{self.settings['child_name']} - Məkan: {map_url}")
        url = f"https://wa.me/{phone}?text={text}"
        self._open_url(url)

    def open_map_link(self):
        map_url, _ = get_location()
        self._open_url(map_url)

    def _open_url(self, url):
        try:
            if platform == "android":
                from jnius import autoclass, cast
                Intent = autoclass("android.content.Intent")
                Uri = autoclass("android.net.Uri")
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                currentActivity = cast("android.app.Activity", PythonActivity.mActivity)
                currentActivity.startActivity(intent)
            else:
                import webbrowser
                webbrowser.open(url)
        except Exception as exc:
            self.show_msg("Xəta", f"Link açıla bilmədi: {exc}")

    def refresh_history(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT status, time, details FROM history ORDER BY id DESC LIMIT 12")
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            self.history_label.text = "Tarixçə boşdur."
        else:
            self.history_label.text = "\n".join([f"[{r[1]}] {r[0]} ({r[2]})" for r in rows])

    def open_settings_popup(self):
        entered = self.pin_input.text.strip()
        self.pin_input.text = ""
        if entered != self.settings["pin"]:
            self.show_msg("Xəta", "Yanlış PIN kod!")
            return

        box = BoxLayout(orientation="vertical", padding=10, spacing=8)
        email_in = TextInput(text=self.settings["email"], hint_text="Göndərən Gmail", multiline=False, size_hint_y=None, height=40)
        pass_in = TextInput(text=self.settings["app_password"], hint_text="Gmail App Şifrəsi", password=True, multiline=False, size_hint_y=None, height=40)
        name_in = TextInput(text=self.settings["child_name"], hint_text="Ad", multiline=False, size_hint_y=None, height=40)
        pin_in = TextInput(text=self.settings["pin"], hint_text="Yeni PIN", password=True, multiline=False, size_hint_y=None, height=40)

        c_name_in = TextInput(hint_text="Yeni şəxs adı (məs: Ata)", multiline=False, size_hint_y=None, height=38)
        c_phone_in = TextInput(hint_text="Telefon (məs: 99450...)", multiline=False, size_hint_y=None, height=38)
        c_mail_in = TextInput(hint_text="E-poçt (istəyə bağlı)", multiline=False, size_hint_y=None, height=38)

        info_lbl = Label(text="", size_hint_y=None, height=30)

        box.add_widget(email_in)
        box.add_widget(pass_in)
        box.add_widget(name_in)
        box.add_widget(pin_in)
        box.add_widget(c_name_in)
        box.add_widget(c_phone_in)
        box.add_widget(c_mail_in)
        box.add_widget(info_lbl)

        popup = Popup(title="Ayarlar & Yeni Əlaqə", content=box, size_hint=(0.92, 0.85))

        def save_all(*_):
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute(
                "UPDATE settings SET email=?, app_password=?, child_name=?, pin=? WHERE id=1",
                (email_in.text.strip(), pass_in.text.strip(), name_in.text.strip(), pin_in.text.strip()),
            )
            nm = c_name_in.text.strip()
            ph = c_phone_in.text.strip().replace("+", "").replace(" ", "")
            em = c_mail_in.text.strip()
            if nm and ph:
                c.execute("INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)", (nm, ph, em))
            conn.commit()
            conn.close()
            self.settings = get_settings()
            self.sub_label.text = self._get_subtitle()
            info_lbl.text = "Yadda saxlanıldı!"

        save_btn = Button(text="Yadda Saxla", size_hint_y=None, height=42)
        save_btn.bind(on_press=save_all)
        box.add_widget(save_btn)

        close_btn = Button(text="Bağla", size_hint_y=None, height=40)
        close_btn.bind(on_press=popup.dismiss)
        box.add_widget(close_btn)

        popup.open()


class GuvendeMobileApp(App):
    def build(self):
        self.title = "GÜVƏNDƏ PRO"
        return GuvendeRoot()


if __name__ == "__main__":
    os.environ.setdefault("KIVY_NO_ARGS", "1")
    GuvendeMobileApp().run()
