"""
╔══════════════════════════════════════════════════════════════════════╗
║          JOLLIBEE KIOSK POS SYSTEM — Python Tkinter GUI             ║
║  Requirements: Python 3.8+  |  pip install pillow requests reportlab ║
╚══════════════════════════════════════════════════════════════════════╝

HOW TO RUN:
  1. Install dependencies:
       pip install pillow requests reportlab
  2. Run:
       python jollibee_kiosk.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import io
import datetime
import threading
import urllib.request
import base64
import sqlite3
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ─────────────────────────────────────────────────────────────────────────────
# FOOD IMAGE URLs — using direct Jollibee/food CDN images
# ─────────────────────────────────────────────────────────────────────────────
FOOD_IMAGES = {
    "chickenjoy":  "https://www.jollibee.com.ph/wp-content/uploads/2021/05/chickenjoy-solo.png",
    "burger":      "https://www.jollibee.com.ph/wp-content/uploads/2021/05/yumburger.png",
    "spaghetti":   "https://www.jollibee.com.ph/wp-content/uploads/2021/05/jolly-spaghetti.png",
    "burgersteak": "https://www.jollibee.com.ph/wp-content/uploads/2021/05/burger-steak.png",
    "fries":       "https://www.jollibee.com.ph/wp-content/uploads/2021/05/fries.png",
    "nuggets":     "https://www.jollibee.com.ph/wp-content/uploads/2021/05/chicken-nuggets.png",
    "sandwich":    "https://www.jollibee.com.ph/wp-content/uploads/2021/05/chicken-sandwich.png",
    "breakfast":   "https://www.jollibee.com.ph/wp-content/uploads/2021/05/longganisa.png",
    "dessert":     "https://www.jollibee.com.ph/wp-content/uploads/2021/05/peach-mango-pie.png",
    "drinks":      "https://www.jollibee.com.ph/wp-content/uploads/2021/05/drinks.png",
}

# Fallback: colored food emoji rendered as image
CAT_EMOJI_COLOR = {
    "chickenjoy":  ("#8B0000", "🍗"),
    "burger":      ("#B8430A", "🍔"),
    "spaghetti":   ("#B5190D", "🍝"),
    "burgersteak": ("#6B3A2A", "🥩"),
    "fries":       ("#C08000", "🍟"),
    "nuggets":     ("#8B5E00", "🍗"),
    "sandwich":    ("#1A6B3C", "🥪"),
    "breakfast":   ("#6B4200", "🥞"),
    "dessert":     ("#8B1A6B", "🍮"),
    "drinks":      ("#1A4A8B", "🥤"),
}

# ─────────────────────────────────────────────────────────────────────────────
# MENU DATA
# ─────────────────────────────────────────────────────────────────────────────
MENU = {
    "🍗 Chickenjoy": {
        "img_key": "chickenjoy",
        "items": [
            {"id": "CJ01", "name": "1-pc Chickenjoy Solo",            "price": 98},
            {"id": "CJ02", "name": "1-pc Chickenjoy w/ Drink",        "price": 107},
            {"id": "CJ03", "name": "1-pc Chickenjoy w/ Fries",        "price": 137},
            {"id": "CJ04", "name": "1-pc Chickenjoy w/ Fries & Drink","price": 167},
            {"id": "CJ05", "name": "2-pc Chickenjoy Solo",            "price": 176},
            {"id": "CJ06", "name": "2-pc Chickenjoy w/ Drink",        "price": 205},
            {"id": "CJ07", "name": "6-pc Chickenjoy Bucket",          "price": 505},
            {"id": "CJ08", "name": "8-pc Chickenjoy Bucket",          "price": 619},
        ]
    },
    "🍔 Burgers": {
        "img_key": "burger",
        "items": [
            {"id": "BG01", "name": "Yumburger",                       "price": 60},
            {"id": "BG02", "name": "Cheesy Yumburger",                "price": 80},
            {"id": "BG03", "name": "Yumburger w/ Drink",              "price": 99},
            {"id": "BG04", "name": "Cheesy Yumburger w/ Drink",       "price": 115},
            {"id": "BG05", "name": "Yumburger Meal",                  "price": 130},
            {"id": "BG06", "name": "Champ Burger",                    "price": 179},
            {"id": "BG07", "name": "Champ Burger w/ Fries & Drink",           "price": 215},
            {"id": "BG08", "name": "Amazing Aloha Champ",             "price": 189},
        ]
    },
    "🍝 Spaghetti": {
        "img_key": "spaghetti",
        "items": [
            {"id": "SP01", "name": "Jolly Spaghetti Solo",            "price": 75},
            {"id": "SP02", "name": "Jolly Spaghetti w/ Drink",        "price": 102},
            {"id": "SP03", "name": "Jolly Spaghetti Family Pan",      "price": 261},
            {"id": "SP04", "name": "Palabok Solo",                    "price": 115},
            {"id": "SP05", "name": "Palabok w/ Drink",                "price": 145},
            {"id": "SP06", "name": "Palabok Family Pan",              "price": 502},
            {"id": "SP07", "name": "Jolly Spaghetti w/ Yumburger w/ Drink",              "price": 140},
        ]
    },
    "🥩 Burger Steak": {
        "img_key": "burgersteak",
        "items": [
            {"id": "BS01", "name": "Burger Steak Solo",               "price": 80},
            {"id": "BS02", "name": "Burger Steak w/ Drink",           "price": 107},
            {"id": "BS03", "name": "2-pc Burger Steak Solo",          "price": 130},
            {"id": "BS04", "name": "2-pc Burger Steak w/ Drink",      "price": 160},
            {"id": "BS05", "name": "6-pc Burger Steak Family Pan",    "price": 384},
        ]
    },
    "🍟 Fries & Sides": {
        "img_key": "fries",
        "items": [
            {"id": "FS01", "name": "Regular Fries",                   "price": 55},
            {"id": "FS02", "name": "Large Fries",                     "price": 75},
            {"id": "FS03", "name": "Medium Fries",              "price": 65},
            {"id": "FS04", "name": "Gravy (2.5oz)",                   "price": 27},
            {"id": "FS05", "name": "Rice",                 "price": 45},
        ]
    },
    "🍗 Chicken Nuggets": {
        "img_key": "nuggets",
        "items": [
            {"id": "NG01", "name": "6-pc Chicken Nuggets",            "price": 119},
            {"id": "NG02", "name": "6-pc Nuggets w/ Fries & Drink",           "price": 188},
            {"id": "NG03", "name": "10-pc Chicken Nuggets",           "price": 210},
        ]
    },
    "🥪 Sandwiches": {
        "img_key": "sandwich",
        "items": [
            {"id": "SW01", "name": "Crunchy Chicken Sandwich",        "price": 89},
            {"id": "SW02", "name": "Crunchy Chicken Sandwich w/ Drink","price": 115},
            {"id": "SW03", "name": "Cheesey Classic Jolly Hotdog",             "price": 80},
            {"id": "SW04", "name": "Jolly Hotdog w/ Fries & Drink",           "price": 166},
        ]
    },
    "🥞 Breakfast": {
        "img_key": "breakfast",
        "items": [
            {"id": "BF02", "name": "Longganisa w/ Drink",             "price": 171},
            {"id": "BF03", "name": "2-pc Pancakes w/ Drink",             "price": 118},
            {"id": "BF04", "name": "Beef Tapa w/ Drink",              "price": 181},
            {"id": "BF05", "name": "Corned Beef W/ Drink",                "price": 152},
            {"id": "BF06", "name": "Breakfast Burger Steak w/ Drink",          "price": 145},
            {"id": "BF07", "name": "Breakfast Chickenjoy w/ Drink",              "price": 168},
            {"id": "BF08", "name": "Breakfast Hotdog w/ Drink",           "price": 130},
        ]
    },
    "🍮 Desserts & Pies": {
        "img_key": "dessert",
        "items": [
            {"id": "DS01", "name": "Peach Mango Pie",                 "price": 49},
            {"id": "DS02", "name": "Chocolate Sundae",                "price": 55},
            {"id": "DS03", "name": "Strawberry Burst Choco Sundae",               "price": 69},
            {"id": "DS04", "name": "Peach Mango 3 Pies To-Go",        "price": 226},
        ]
    },
    "🥤 Beverages": {
        "img_key": "drinks",
        "items": [
            {"id": "BV03", "name": "Coke Float",                      "price": 65},
            {"id": "BV04", "name": "Pepsi Float",                     "price": 65},
            {"id": "BV05", "name": "Orange Juice",                    "price": 50},
            {"id": "BV06", "name": "Brewed Coffee",                   "price": 55},
            {"id": "BV07", "name": "Hot Chocolate",                   "price": 60},
            {"id": "BV08", "name": "Coke",                               "price": 45},
        ]
    },
}

# Colors
RED       = "#D8202E"
YELLOW    = "#FFC412"
DARK_RED  = "#A01520"
CREAM     = "#FFF8EC"
LIGHT_BG  = "#FFF3E0"
CARD_BG   = "#FFFFFF"
TEXT_DARK = "#1A1A1A"
TEXT_MID  = "#555555"
TEXT_LITE = "#999999"
BORDER    = "#E0C9A0"
GREEN     = "#28A745"

DISCOUNT_RATES = {
    "None":           0.00,
    "Senior Citizen": 0.20,
    "PWD":            0.20,
}

_img_cache: dict = {}

# Custom item images: drop image files in the same folder as this script.
ITEM_IMAGES = {
    "CJ01": "CJ01.png", "CJ02": "CJ02.png", "CJ03": "CJ03.png", "CJ04": "CJ04.png",
    "CJ05": "CJ05.png", "CJ06": "CJ06.png", "CJ07": "CJ07.png", "CJ08": "CJ08.png",
    "BG01": "BG01.png", "BG02": "BG02.png", "BG03": "BG03.png", "BG04": "BG04.png",
    "BG05": "BG05.png", "BG06": "BG06.png", "BG07": "BG07.png", "BG08": "BG08.png",
    "SP01": "SP01.png", "SP02": "SP02.png", "SP03": "SP03.png", "SP04": "SP04.png",
    "SP05": "SP05.png", "SP06": "SP06.png", "SP07": "SP07.png", "FS01": "FS01.png",
    "FS02": "FS02.png", "FS03": "FS03.png", "FS04": "FS04.png", "FS05": "FS05.png",
    "BS01": "BS01.png", "BS02": "BS02.png", "BS03": "BS03.png", "BS04": "BS04.png",
    "BS05": "BS05.png", "NG01": "NG01.png", "NG02": "NG02.png", "NG03": "NG03.png",
    "SW01": "SW01.png", "SW02": "SW02.png", "SW03": "SW03.png", "SW04": "SW04.png",
    "DS01": "DS01.png", "DS02": "DS02.png", "DS03": "DS03.png", "DS04": "DS04.png",
    "BV05": "BV05.png", "BV04": "BV04.png", "BV03": "BV03.png", "BV06": "BV06.png",
    "BV07": "BV07.png", "BF02": "BF02.png", "BF03": "BF03.png", "BF04": "BF04.png",
    "BF05": "BF05.png", "BF06": "BF06.png", "BF07": "BF07.png", "BF08": "BF08.png",
    "BV08": "BV08.png",
}

RELIABLE_URLS = {
    "chickenjoy":  [
        "https://images.unsplash.com/photo-1626645738196-c2a7c87a8f58?w=200&h=150&fit=crop",
        "https://images.unsplash.com/photo-1569058242567-93de6f36f8ec?w=200&h=150&fit=crop",
    ],
    "burger":      [
        "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=200&h=150&fit=crop",
        "https://images.unsplash.com/photo-1551615593-ef5fe247e8f7?w=200&h=150&fit=crop",
    ],
    "spaghetti":   [
        "https://images.unsplash.com/photo-1555949258-eb67b1ef0ceb?w=200&h=150&fit=crop",
        "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=200&h=150&fit=crop",
    ],
    "burgersteak": [
        "https://images.unsplash.com/photo-1544025162-d76694265947?w=200&h=150&fit=crop",
        "https://images.unsplash.com/photo-1558030006-450675393462?w=200&h=150&fit=crop",
    ],
    "fries":       [
        "https://images.unsplash.com/photo-1630384060421-cb20d0e0649d?w=200&h=150&fit=crop",
        "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=200&h=150&fit=crop",
    ],
    "nuggets":     [
        "https://images.unsplash.com/photo-1562967914-608f82629710?w=200&h=150&fit=crop",
        "https://images.unsplash.com/photo-1615361200141-f45040f367be?w=200&h=150&fit=crop",
    ],
    "sandwich":    [
        "https://images.unsplash.com/photo-1606755962773-d324e0a13086?w=200&h=150&fit=crop",
        "https://images.unsplash.com/photo-1553909489-cd47e0907980?w=200&h=150&fit=crop",
    ],
    "breakfast":   [
        "https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=200&h=150&fit=crop",
        "https://images.unsplash.com/photo-1504754524776-8f4f37790ca0?w=200&h=150&fit=crop",
    ],
    "dessert":     [
        "https://images.unsplash.com/photo-1621303837174-89787a7d4729?w=200&h=150&fit=crop",
        "https://images.unsplash.com/photo-1559181567-c3190ca9959b?w=200&h=150&fit=crop",
    ],
    "drinks":      [
        "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=200&h=150&fit=crop",
        "https://images.unsplash.com/photo-1437418747212-8d9709afab22?w=200&h=150&fit=crop",
    ],
}

def init_database():
    conn = sqlite3.connect("kiosk_system.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ref_num TEXT UNIQUE,
            timestamp TEXT,
            order_type TEXT,
            discount_type TEXT,
            subtotal REAL,
            discount REAL,
            vat REAL,
            grand_total REAL,
            payment REAL,
            change_due REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ref_num TEXT,
            item_id TEXT,
            item_name TEXT,
            price REAL,
            qty INTEGER,
            subtotal REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            item_id TEXT PRIMARY KEY,
            item_name TEXT,
            stock_level INTEGER
        )
    """)
    for category, content in MENU.items():
        for item in content["items"]:
            cursor.execute("""
                INSERT OR IGNORE INTO inventory (item_id, item_name, stock_level)
                VALUES (?, ?, ?)
            """, (item["id"], item["name"], 100))
    conn.commit()
    conn.close()

def _make_emoji_image(emoji: str, color: str, size=(200, 150)) -> "ImageTk.PhotoImage | None":
    if not PIL_AVAILABLE:
        return None
    img = Image.new("RGB", size, color)
    draw = ImageDraw.Draw(img)
    for y in range(size[1]):
        alpha = int(30 * (1 - y / size[1]))
        draw.line([(0, y), (size[0], y)], fill=(255, 255, 255))
    img2 = Image.new("RGB", size, color)
    for y in range(size[1]):
        for x in range(size[0]):
            r, g, b = img2.getpixel((x, y))
            blend = int(255 * 0.08 * (1 - y / size[1]))
            img2.putpixel((x, y), (min(r + blend, 255), min(g + blend, 255), min(b + blend, 255)))
    draw2 = ImageDraw.Draw(img2)
    try:
        font = ImageFont.truetype("seguiemj.ttf", 64)
    except Exception:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 64)
        except Exception:
            font = ImageFont.load_default()
    draw2.text((size[0]//2, size[1]//2), emoji, anchor="mm", font=font, fill="white")
    return ImageTk.PhotoImage(img2)


def _load_image_async(img_key: str, label: tk.Label):
    if not PIL_AVAILABLE:
        return

    cache_key = img_key
    if cache_key in _img_cache:
        photo = _img_cache[cache_key]
        try:
            label.after(0, lambda: _apply_image(label, photo))
        except Exception:
            pass
        return

    def worker():
        urls = RELIABLE_URLS.get(img_key, [])
        for url in urls:
            try:
                req = urllib.request.Request(
                    url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Accept": "image/*,*/*"
                    }
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    data = resp.read()
                if len(data) < 500:
                    continue
                img = Image.open(io.BytesIO(data)).convert("RGB")
                img = img.resize((200, 150), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                _img_cache[cache_key] = photo
                try:
                    label.after(0, lambda p=photo: _apply_image(label, p))
                except Exception:
                    pass
                return
            except Exception:
                continue

        _, emoji = CAT_EMOJI_COLOR.get(img_key, ("#555555", "🍽️"))
        color = "#8B0000"   # same dark red behind every food image
        photo = _make_emoji_image(emoji, color)
        if photo:
            _img_cache[cache_key] = photo
            try:
                label.after(0, lambda p=photo: _apply_image(label, p))
            except Exception:
                pass

    threading.Thread(target=worker, daemon=True).start()


def _apply_image(label: tk.Label, photo):
    try:
        if label.winfo_exists():
            label.configure(image=photo)
            label._img_ref = photo
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────
class JollibeeKiosk(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🍗 Jollibee Self-Service Kiosk")
        self.state('zoomed')
        self.configure(bg=CREAM)

        self.cart: list[dict] = []
        self.current_category = list(MENU.keys())[0]
        self.discount_type = tk.StringVar(value="None")
        self.order_type = tk.StringVar(value="Dine-In")
        
        self.delivery_name = ""
        self.delivery_phone = ""
        self.delivery_address_val = ""

        self._build_ui()
        self._select_category(self.current_category)
        self._show_welcome_page()

    def _show_welcome_page(self):
        self._welcome_frame = tk.Frame(self, bg=RED)
        self._welcome_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._bg_label = tk.Label(self._welcome_frame, bg=RED)
        self._bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        if PIL_AVAILABLE:
            img_path = "jollibee-not-writing-china-off-despite-slowing-mainland-economy-6-1280x720.png"
            if os.path.exists(img_path):
                self._orig_bg_img = Image.open(img_path)
                
                def resize_bg(event):
                    w, h = event.width, event.height
                    if w > 0 and h > 0:
                        resized = self._orig_bg_img.resize((w, h), Image.LANCZOS)
                        self._welcome_bg_photo = ImageTk.PhotoImage(resized)
                        self._bg_label.configure(image=self._welcome_bg_photo)
                
                self._welcome_frame.bind("<Configure>", resize_bg)

        start_btn = tk.Button(
            self._welcome_frame,
            text="TAP TO BEGIN YOUR JOLLIBEE EXPERIENCE",
            font=("Segoe UI", 18, "bold"),
            bg=YELLOW,
            fg=DARK_RED,
            activebackground="#FFD84D",
            activeforeground=DARK_RED,
            relief="raised",
            bd=4,
            padx=28,
            pady=14,
            cursor="hand2",
            command=self._dismiss_welcome_page
        )
        start_btn.place(relx=0.5, rely=0.86, anchor="center")
        
        self._welcome_frame.bind("<Button-1>", lambda e: self._dismiss_welcome_page())
        self._bg_label.bind("<Button-1>", lambda e: self._dismiss_welcome_page())

    def _dismiss_welcome_page(self):
        if hasattr(self, '_welcome_frame') and self._welcome_frame.winfo_exists():
            self._welcome_frame.destroy()
        self._show_order_type_page()

    def _show_order_type_page(self):
        self._order_frame = tk.Frame(self, bg=CREAM)
        self._order_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        banner = tk.Frame(self._order_frame, bg=RED, height=120)
        banner.pack(fill="x")
        banner.pack_propagate(False)

        tk.Label(
            banner,
            text=" Choose Your Order Type",
            font=("Georgia", 28, "bold"),
            bg=RED,
            fg=YELLOW
        ).pack(pady=(20,5))

        tk.Label(
            banner,
            text="Select how you'd like to enjoy your Jollibee meal",
            font=("Segoe UI", 12, "italic"),
            bg=RED,
            fg="white"
        ).pack()

        content = tk.Frame(self._order_frame, bg=CREAM)
        content.pack(expand=True)

        def select_type(order_type):
            self.order_type.set(order_type)
            self._order_frame.destroy()
            self._status.configure(text=f"Order Type Selected: {order_type}")

        dine_card = tk.Frame(content, bg="white", bd=3, relief="ridge", padx=30, pady=30)
        dine_card.grid(row=0, column=0, padx=40, pady=40)

        tk.Label(dine_card, text="🍽️", font=("Segoe UI Emoji", 60), bg="white").pack()
        tk.Label(dine_card, text="DINE-IN", font=("Georgia", 18, "bold"), bg="white", fg=RED).pack(pady=5)
        tk.Label(dine_card, text="Enjoy your meal inside the restaurant.", font=("Segoe UI", 10), bg="white").pack()
        tk.Button(dine_card, text="TAP HERE", bg=YELLOW, fg=DARK_RED,
                  font=("Segoe UI", 11, "bold"), activebackground="#FFD84D",
                  activeforeground=DARK_RED, relief="raised", bd=4,
                  padx=14, pady=6,
                  command=lambda: select_type("Dine-In")).pack(pady=15)

        take_card = tk.Frame(content, bg="white", bd=3, relief="ridge", padx=30, pady=30)
        take_card.grid(row=0, column=1, padx=40, pady=40)

        tk.Label(take_card, text="🥡", font=("Segoe UI Emoji", 60), bg="white").pack()
        tk.Label(take_card, text="TAKE-OUT", font=("Georgia", 18, "bold"), bg="white", fg=RED).pack(pady=5)
        tk.Label(take_card, text="Take your meal with you wherever you go.", font=("Segoe UI", 10), bg="white").pack()
        tk.Button(take_card, text="TAP HERE", bg=YELLOW, fg=DARK_RED,
                  font=("Segoe UI", 11, "bold"), activebackground="#FFD84D",
                  activeforeground=DARK_RED, relief="raised", bd=4,
                  padx=14, pady=6,
                  command=lambda: select_type("Take-Out")).pack(pady=15)

    def _open_admin_login(self):
        login_win = tk.Toplevel(self)
        login_win.title("Admin Authentication")
        login_win.geometry("350x220")
        login_win.resizable(False, False)
        login_win.configure(bg=CREAM)
        login_win.transient(self)
        login_win.grab_set()

        tk.Label(login_win, text="🔑 System Admin Access", font=("Georgia", 13, "bold"), bg=RED, fg=YELLOW, pady=8).pack(fill="x")
        
        frame = tk.Frame(login_win, bg=CREAM, pady=10)
        frame.pack()

        tk.Label(frame, text="Username:", font=("Segoe UI", 10, "bold"), bg=CREAM, fg=TEXT_DARK).grid(row=0, column=0, sticky="e", pady=6)
        user_ent = tk.Entry(frame, font=("Segoe UI", 10), width=18)
        user_ent.grid(row=0, column=1, pady=6, padx=6)
        user_ent.focus_set()

        tk.Label(frame, text="Password:", font=("Segoe UI", 10, "bold"), bg=CREAM, fg=TEXT_DARK).grid(row=1, column=0, sticky="e", pady=6)
        pass_ent = tk.Entry(frame, font=("Segoe UI", 10), width=18, show="*")
        pass_ent.grid(row=1, column=1, pady=6, padx=6)

        def auth():
            if user_ent.get() == "admin" and pass_ent.get() == "admin123":
                login_win.destroy()
                self._open_admin_dashboard()
            else:
                messagebox.showerror("Access Denied", "Incorrect Admin credentials provided.", parent=login_win)

        tk.Button(login_win, text="Authenticate", font=("Segoe UI", 10, "bold"), bg=GREEN, fg="white", relief="flat", padx=14, pady=6, command=auth).pack(pady=5)

    def _open_admin_dashboard(self):
        dash = tk.Toplevel(self)
        dash.title("⚙️ Kiosk Control & Administration Panel")
        dash.geometry("850x600")
        dash.configure(bg=CREAM)
        dash.grab_set()

        tabs = ttk.Notebook(dash)
        tabs.pack(fill="both", expand=True, padx=10, pady=10)

        inv_tab = tk.Frame(tabs, bg=CARD_BG)
        sales_tab = tk.Frame(tabs, bg=CARD_BG)
        tabs.add(inv_tab, text=" Stock Levels ")
        tabs.add(sales_tab, text=" Financial Sales Ledger ")

        def exit_admin_panel():
            dash.destroy()

        # INVENTORY MANAGEMENT SUB-SYSTEM
        inv_top = tk.Frame(inv_tab, bg=LIGHT_BG, pady=8, padx=10)
        inv_top.pack(fill="x")
        tk.Label(inv_top, text="Product Inventory Bookkeeping", font=("Georgia", 12, "bold"), bg=LIGHT_BG, fg=DARK_RED).pack(side="left")

        inv_tree_frame = tk.Frame(inv_tab, bg=CARD_BG)
        inv_tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        inv_sb = ttk.Scrollbar(inv_tree_frame, orient="vertical")
        inv_sb.pack(side="right", fill="y")

        inv_tree = ttk.Treeview(inv_tree_frame, columns=("id", "name", "stock"), show="headings", yscrollcommand=inv_sb.set)
        inv_sb.config(command=inv_tree.yview)
        inv_tree.heading("id", text="Item ID", anchor="w")
        inv_tree.heading("name", text="Product Name", anchor="w")
        inv_tree.heading("stock", text="Remaining Stock Units", anchor="center")
        inv_tree.column("id", width=100, anchor="w")
        inv_tree.column("name", width=350, anchor="w")
        inv_tree.column("stock", width=150, anchor="center")
        inv_tree.pack(fill="both", expand=True)

        def reload_inv():
            inv_tree.delete(*inv_tree.get_children())
            conn = sqlite3.connect("kiosk_system.db")
            res = conn.execute("SELECT item_id, item_name, stock_level FROM inventory").fetchall()
            conn.close()
            for idx, row_data in enumerate(res):
                tag = "odd" if idx % 2 else "even"
                inv_tree.insert("", "end", values=row_data, tags=(tag,))
        
        inv_tree.tag_configure("odd", background="#FFFBF0")
        inv_tree.tag_configure("even", background=CARD_BG)

        def restock_item():
            sel = inv_tree.selection()
            if not sel:
                messagebox.showinfo("Select Product", "Choose a product record from the grid to restock.", parent=dash)
                return
            item_id = inv_tree.item(sel[0], "values")[0]
            curr_stock = inv_tree.item(sel[0], "values")[2]
            add_units = simpledialog.askinteger("Restock Supply", f"Add inventory volume units to {item_id}:", initialvalue=50, minvalue=1, maxvalue=1000, parent=dash)
            if add_units:
                conn = sqlite3.connect("kiosk_system.db")
                conn.execute("UPDATE inventory SET stock_level = stock_level + ? WHERE item_id = ?", (add_units, item_id))
                conn.commit()
                conn.close()
                reload_inv()

        tk.Button(inv_top, text="🔄 Refresh Levels", font=("Segoe UI", 9, "bold"), bg=RED, fg="white", relief="flat", padx=8, pady=3, command=reload_inv).pack(side="right", padx=5)
        tk.Button(inv_top, text="➕ Replenish Stock", font=("Segoe UI", 9, "bold"), bg=GREEN, fg="white", relief="flat", padx=8, pady=3, command=restock_item).pack(side="right", padx=5)
        tk.Button(inv_top, text="↩️ Exit to Menu", font=("Segoe UI", 9, "bold"), bg=GREEN, fg="white", relief="flat", padx=8, pady=3, command=exit_admin_panel).pack(side="right", padx=5)

        # FINANCIAL REPORTING SUB-SYSTEM
        sales_top = tk.Frame(sales_tab, bg=LIGHT_BG, pady=8, padx=10)
        sales_top.pack(fill="x")
        
        summary_label = tk.Label(sales_top, font=("Segoe UI", 11, "bold"), bg=LIGHT_BG, fg=TEXT_DARK, text="Gross Revenue Accumulation: ₱0.00")
        summary_label.pack(side="left")

        sales_tree_frame = tk.Frame(sales_tab, bg=CARD_BG)
        sales_tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        sales_sb = ttk.Scrollbar(sales_tree_frame, orient="vertical")
        sales_sb.pack(side="right", fill="y")

        sales_tree = ttk.Treeview(sales_tree_frame, columns=("ref", "time", "type", "sub", "disc", "grand"), show="headings", yscrollcommand=sales_sb.set)
        sales_sb.config(command=sales_tree.yview)
        sales_tree.heading("ref", text="Reference ID", anchor="w")
        sales_tree.heading("time", text="Timestamp", anchor="w")
        sales_tree.heading("type", text="Type", anchor="center")
        sales_tree.heading("sub", text="Subtotal", anchor="e")
        sales_tree.heading("disc", text="Discount", anchor="e")
        sales_tree.heading("grand", text="Grand Total", anchor="e")
        
        sales_tree.column("ref", width=120, anchor="w")
        sales_tree.column("time", width=160, anchor="w")
        sales_tree.column("type", width=90, anchor="center")
        sales_tree.column("sub", width=100, anchor="e")
        sales_tree.column("disc", width=90, anchor="e")
        sales_tree.column("grand", width=110, anchor="e")
        sales_tree.pack(fill="both", expand=True)

        sales_tree.tag_configure("odd", background="#FFFBF0")
        sales_tree.tag_configure("even", background=CARD_BG)

        def reload_sales():
            sales_tree.delete(*sales_tree.get_children())
            conn = sqlite3.connect("kiosk_system.db")
            res = conn.execute("SELECT ref_num, timestamp, order_type, subtotal, discount, grand_total FROM sales ORDER BY id DESC").fetchall()
            total_sum = conn.execute("SELECT SUM(grand_total) FROM sales").fetchone()[0] or 0.0
            conn.close()
            
            summary_label.config(text=f"Gross Revenue Accumulation: ₱{total_sum:,.2f}")
            for idx, row_data in enumerate(res):
                tag = "odd" if idx % 2 else "even"
                formatted = (row_data[0], row_data[1], row_data[2], f"₱{row_data[3]:,.2f}", f"₱{row_data[4]:,.2f}", f"₱{row_data[5]:,.2f}")
                sales_tree.insert("", "end", values=formatted, tags=(tag,))

        def clear_all_sales():
            confirm = messagebox.askyesno("Clear Sales Records", "Are you sure you want to clear ALL sales records? This action cannot be undone.", parent=dash)
            if confirm:
                conn = sqlite3.connect("kiosk_system.db")
                conn.execute("DELETE FROM sales")
                conn.commit()
                conn.close()
                reload_sales()
                messagebox.showinfo("Sales Cleared", "All sales records have been cleared.", parent=dash)

        tk.Button(sales_top, text="🔄 Refresh Financials", font=("Segoe UI", 9, "bold"), bg=RED, fg="white", relief="flat", padx=8, pady=3, command=reload_sales).pack(side="right")
        tk.Button(sales_top, text="🗑️ Clear All Sales", font=("Segoe UI", 9, "bold"), bg=DARK_RED, fg="white", relief="flat", padx=8, pady=3, command=clear_all_sales).pack(side="right", padx=5)
        tk.Button(sales_top, text="↩️ Exit to Menu", font=("Segoe UI", 9, "bold"), bg=GREEN, fg="white", relief="flat", padx=8, pady=3, command=exit_admin_panel).pack(side="right", padx=5)

        reload_inv()
        reload_sales()

    def _build_ui(self):
        header = tk.Frame(self, bg=RED, height=68)
        header.pack(fill="x")
        header.pack_propagate(False)

        if PIL_AVAILABLE and os.path.exists("jabi logo.png"):
            try:
                logo_img = Image.open("jabi logo.png").convert("RGBA")
                logo_img = logo_img.resize((130, 50), Image.LANCZOS)
                self._header_logo = ImageTk.PhotoImage(logo_img)
                tk.Label(header, image=self._header_logo, bg=RED).pack(side="left", padx=12, pady=6)
            except Exception:
                tk.Label(header, text="Jollibee", font=("Georgia", 24, "bold"),
                         bg=RED, fg=YELLOW).pack(side="left", padx=18, pady=10)
        
        self._datetime_label = tk.Label(
            header,
            font=("Segoe UI", 11, "bold"),
            bg=RED,
            fg="white"
        )
        self._datetime_label.pack(side="right", padx=15)

        def update_datetime():
            now = datetime.datetime.now()
            self._datetime_label.config(
                text=now.strftime("%B %d, %Y | %I:%M:%S %p")
            )
            self.after(1000, update_datetime)

        update_datetime()

        tk.Button(
            header,
            text="✖ Exit",
            font=("Segoe UI", 13, "bold"),
            bg=RED,
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.destroy
        ).pack(side="right", padx=12, pady=12)

        # ADMIN ACCESS INTEGRATION POINT
        tk.Button(
            header,
            text="⚙️ Admin Login",
            font=("Segoe UI", 11, "bold"),
            bg=YELLOW,
            fg=RED,
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._open_admin_login
        ).pack(side="right", padx=10, pady=12)

        body = tk.Frame(self, bg=CREAM)
        body.pack(fill="both", expand=True)

        sidebar = tk.Frame(body, bg=DARK_RED, width=162)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="MENU", font=("Georgia", 14, "bold"),
                 bg=DARK_RED, fg=YELLOW, pady=10).pack(fill="x")

        self._cat_btns: dict[str, tk.Button] = {}
        for cat in MENU:
            btn = tk.Button(sidebar, text=cat,
                            font=("Segoe UI", 11, "bold"),
                            bg=DARK_RED, fg="white",
                            activebackground=RED, activeforeground=YELLOW,
                            relief="flat", anchor="w", padx=10, pady=7,
                            wraplength=140, cursor="hand2",
                            command=lambda c=cat: self._select_category(c))
            btn.pack(fill="x", padx=3, pady=1)
            self._cat_btns[cat] = btn

        center = tk.Frame(body, bg=CREAM)
        center.pack(side="left", fill="both", expand=True)

        self._cat_label = tk.Label(center, text="", font=("Georgia", 18, "bold"),
                                   bg=RED, fg=YELLOW, pady=8, padx=16, anchor="w")
        self._cat_label.pack(fill="x")

        grid_outer = tk.Frame(center, bg=CREAM)
        grid_outer.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(grid_outer, bg=CREAM, highlightthickness=0)
        vsb = ttk.Scrollbar(grid_outer, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._grid_frame = tk.Frame(self._canvas, bg=CREAM)
        self._cw = self._canvas.create_window((0, 0), window=self._grid_frame, anchor="nw")
        self._grid_frame.bind("<Configure>", lambda e: self._update_scrollregion())
        self._canvas.bind("<Configure>", lambda e: self._canvas.itemconfig(self._cw, width=e.width))
        self._canvas.bind_all("<MouseWheel>", self._on_menu_wheel)

        cart_panel = tk.Frame(body, bg=CARD_BG, width=320)
        cart_panel.pack(side="right", fill="y")
        cart_panel.pack_propagate(False)

        cart_hdr = tk.Frame(cart_panel, bg=YELLOW, height=44)
        cart_hdr.pack(fill="x")
        cart_hdr.pack_propagate(False)
        tk.Label(cart_hdr, text="🛒  YOUR ORDER", font=("Georgia", 15, "bold"),
                 bg=YELLOW, fg=DARK_RED).pack(expand=True)

        disc_bar = tk.Frame(cart_panel, bg=LIGHT_BG, pady=6)
        disc_bar.pack(fill="x")
        tk.Label(disc_bar, text="Discount:", font=("Segoe UI", 11, "bold"),
                 bg=LIGHT_BG, fg=TEXT_MID).pack(side="left", padx=8)
        disc = ttk.Combobox(disc_bar, textvariable=self.discount_type,
                            values=list(DISCOUNT_RATES.keys()),
                            width=17, state="readonly", font=("Segoe UI", 11))
        disc.pack(side="left")
        disc.bind("<<ComboboxSelected>>", lambda e: self._refresh_totals())

        cart_list = tk.Frame(cart_panel, bg=CARD_BG)
        cart_list.pack(fill="both", expand=True)
        cart_vsb = ttk.Scrollbar(cart_list, orient="vertical")
        cart_vsb.pack(side="right", fill="y")

        self._cart_tree = ttk.Treeview(cart_list, columns=("item","qty","price"),
                                        show="headings", yscrollcommand=cart_vsb.set,
                                        selectmode="browse")
        cart_vsb.config(command=self._cart_tree.yview)
        self._cart_tree.heading("item",  text="Item",     anchor="w")
        self._cart_tree.heading("qty",   text="Qty",      anchor="center")
        self._cart_tree.heading("price", text="Subtotal", anchor="e")
        self._cart_tree.column("item",  width=155, anchor="w")
        self._cart_tree.column("qty",   width=38,  anchor="center")
        self._cart_tree.column("price", width=80,  anchor="e")
        self._cart_tree.pack(fill="both", expand=True)
        self._cart_tree.tag_configure("odd",  background="#FFFBF0")
        self._cart_tree.tag_configure("even", background=CARD_BG)
        self._cart_tree.bind("<Double-1>", lambda e: self._edit_selected_qty())

        act = tk.Frame(cart_panel, bg=LIGHT_BG, pady=4)
        act.pack(fill="x")
        for txt, clr, cmd in [
            ("✏️ Edit Qty",  "#E87800", self._edit_selected_qty),
            ("🗑 Remove",    "#CC2233", self._remove_selected),
            ("🗑 Clear All", "#777777", self._clear_cart),
        ]:
            tk.Button(act, text=txt, font=("Segoe UI", 9, "bold"),
                      bg=clr, fg="white", relief="flat", padx=7, pady=3,
                      cursor="hand2", command=cmd).pack(side="left" if txt != "🗑 Clear All" else "right",
                                                        padx=4)

        tots = tk.Frame(cart_panel, bg=CARD_BG, pady=4)
        tots.pack(fill="x")

        def tot_row(ltext, attr, fg=TEXT_DARK, bold=False):
            f = tk.Frame(tots, bg=CARD_BG); f.pack(fill="x", padx=10, pady=1)
            fn = ("Segoe UI", 10, "bold" if bold else "normal")
            tk.Label(f, text=ltext, font=fn, bg=CARD_BG, fg=TEXT_MID).pack(side="left")
            lbl = tk.Label(f, text="₱0.00", font=fn, bg=CARD_BG, fg=fg)
            lbl.pack(side="right")
            setattr(self, attr, lbl)

        tot_row("Subtotal:",    "_lbl_sub")
        tot_row("Discount:",    "_lbl_disc", fg=GREEN)
        tot_row("Total:",       "_lbl_tot")
        tot_row("VAT (12%):",   "_lbl_vat",  fg=TEXT_MID)
        tk.Frame(tots, bg=BORDER, height=1).pack(fill="x", padx=8, pady=4)
        tot_row("GRAND TOTAL:", "_lbl_grand", fg=RED, bold=True)

        tk.Button(cart_panel, text="💳  CHECKOUT",
                  font=("Georgia", 14, "bold"), bg=RED, fg=YELLOW,
                  activebackground=DARK_RED, relief="flat", pady=12,
                  cursor="hand2", command=self._checkout).pack(fill="x", padx=10, pady=8)

        self._status = tk.Label(self, bg=YELLOW, fg=DARK_RED, anchor="w", padx=12, pady=4,
                                font=("Segoe UI", 9), text="Welcome to Jollibee! Tap any item to add it to your order.")
        self._status.pack(fill="x", side="bottom")

    def _update_scrollregion(self):
        """Scroll region is never smaller than the viewport, so short menus can't scroll."""
        try:
            bbox = self._canvas.bbox("all")
            if not bbox:
                return
            content_h = bbox[3] - bbox[1]
            view_h = self._canvas.winfo_height()
            self._canvas.configure(scrollregion=(0, 0, bbox[2], max(content_h, view_h)))
            if content_h <= view_h:
                self._canvas.yview_moveto(0)
        except tk.TclError:
            pass

    def _on_menu_wheel(self, event):
        try:
            bbox = self._canvas.bbox("all")
            if bbox and (bbox[3] - bbox[1]) > self._canvas.winfo_height():
                self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except tk.TclError:
            pass  # canvas doesn't exist (e.g. wheel used in another window)

    def _select_category(self, cat: str):
        self.current_category = cat
        for c, btn in self._cat_btns.items():
            btn.configure(bg=RED if c == cat else DARK_RED, fg=YELLOW if c == cat else "white")
        self._cat_label.configure(text=f"  {cat}")
        self._build_menu_grid(cat)
        self.update_idletasks()
        self._update_scrollregion()
        self._canvas.yview_moveto(0)   # always start at the top of the new category

    def _build_menu_grid(self, cat: str):
        for w in self._grid_frame.winfo_children():
            w.destroy()

        data = MENU[cat]
        img_key = data["img_key"]
        items = data["items"]
        cols = 3

        _, emoji = CAT_EMOJI_COLOR.get(img_key, ("#555555", "🍽️"))
        color = "#8B0000"   # same dark red behind every food image

        for idx, item in enumerate(items):
            row_idx, col_idx = divmod(idx, cols)
            self._grid_frame.columnconfigure(col_idx, weight=1)

            card = tk.Frame(self._grid_frame, bg=CARD_BG, bd=1, relief="groove", cursor="hand2", height=340)
            card.grid(row=row_idx, column=col_idx, padx=8, pady=8, sticky="nsew")
            card.grid_propagate(False)

            img_frame = tk.Frame(card, bg=color, height=130)
            img_frame.pack(fill="x")
            img_frame.pack_propagate(False)

            img_lbl = tk.Label(img_frame, bg=color, text=emoji, font=("Segoe UI Emoji", 36))
            img_lbl.pack(expand=True)

            if PIL_AVAILABLE and item["id"] in ITEM_IMAGES:
                try:
                    filename = ITEM_IMAGES[item["id"]]
                    if os.path.exists(filename):
                        custom_img = Image.open(filename).convert("RGB")
                        custom_img = custom_img.resize((200, 150), Image.LANCZOS)
                        photo = ImageTk.PhotoImage(custom_img)
                        img_lbl.configure(image=photo, text="")
                        img_lbl.image = photo
                    else:
                        raise FileNotFoundError(filename)
                except Exception as e:
                    cache_key = img_key
                    if cache_key in _img_cache:
                        _apply_image(img_lbl, _img_cache[cache_key])
                    else:
                        _load_image_async(img_key, img_lbl)
            else:
                cache_key = img_key
                if PIL_AVAILABLE:
                    if cache_key in _img_cache:
                        _apply_image(img_lbl, _img_cache[cache_key])
                    else:
                        _load_image_async(img_key, img_lbl)

            tk.Label(card, text=item["id"], font=("Consolas", 10, "bold"),
                     bg=color, fg="white", padx=5, pady=1).pack(anchor="w", padx=6, pady=(5, 0))

            tk.Label(card, text=item["name"], font=("Segoe UI", 11, "bold"),
                     bg=CARD_BG, fg=TEXT_DARK, wraplength=150, justify="left", anchor="w", height=3).pack(fill="x", padx=6, pady=(2, 0))

            tk.Label(card, text=f"₱{item['price']:,}", font=("Georgia", 13, "bold"),
                     bg=CARD_BG, fg=RED).pack(anchor="w", padx=6)

            tk.Frame(card, bg=CARD_BG).pack(expand=True, fill="both")

            add_btn = tk.Button(card, text="＋ Add to Order", font=("Segoe UI", 11, "bold"),
                                bg=YELLOW, fg=DARK_RED, relief="flat",
                                activebackground=RED, activeforeground=YELLOW, cursor="hand2",
                                command=lambda i=item: self._add_to_cart(i))
            add_btn.pack(fill="x", padx=6, pady=(2, 6))

    def _add_to_cart(self, item: dict, qty: int = 1):
        conn = sqlite3.connect("kiosk_system.db")
        stock = conn.execute("SELECT stock_level FROM inventory WHERE item_id = ?", (item["id"],)).fetchone()[0]
        conn.close()

        req_qty = qty
        for e in self.cart:
            if e["id"] == item["id"]:
                req_qty += e["qty"]

        if req_qty > stock:
            messagebox.showwarning("Out of Stock", f"Order failed. Only {stock} units remain for {item['name']}.", parent=self)
            return

        for e in self.cart:
            if e["id"] == item["id"]:
                e["qty"] += qty
                e["subtotal"] = e["qty"] * e["price"]
                self._refresh_cart_ui()
                self._status.configure(text=f"✅ {item['name']} updated (qty: {e['qty']})")
                return

        self.cart.append({
            "id": item["id"], "name": item["name"], "price": item["price"],
            "qty": qty, "subtotal": qty * item["price"]
        })
        self._refresh_cart_ui()
        self._status.configure(text=f"✅ Added: {item['name']} ₱{item['price']:,}")

    def _remove_selected(self):
        sel = self._cart_tree.selection()
        if not sel: return
        del self.cart[self._cart_tree.index(sel[0])]
        self._refresh_cart_ui()

    def _edit_selected_qty(self):
        sel = self._cart_tree.selection()
        if not sel:
            messagebox.showinfo("Select Item", "Please select an item in the cart first.", parent=self)
            return
        idx = self._cart_tree.index(sel[0])
        entry = self.cart[idx]
        
        conn = sqlite3.connect("kiosk_system.db")
        stock = conn.execute("SELECT stock_level FROM inventory WHERE item_id = ?", (entry["id"],)).fetchone()[0]
        conn.close()

        nq = simpledialog.askinteger("Edit Quantity", f"New quantity for:\n{entry['name']}\n(Current Stock: {stock})",
                                     initialvalue=entry["qty"], minvalue=1, maxvalue=99, parent=self)
        if nq:
            if nq > stock:
                messagebox.showwarning("Out of Stock", f"Requested volume adjustments reject. Limit: {stock}.", parent=self)
                return
            entry["qty"] = nq
            entry["subtotal"] = nq * entry["price"]
            self._refresh_cart_ui()

    def _clear_cart(self):
        if self.cart and messagebox.askyesno("Clear Cart", "Remove all items?", parent=self):
            self.cart.clear()
            self._refresh_cart_ui()

    def _refresh_cart_ui(self):
        self._cart_tree.delete(*self._cart_tree.get_children())
        for i, e in enumerate(self.cart):
            self._cart_tree.insert("", "end", values=(e["name"], e["qty"], f"₱{e['subtotal']:,.2f}"),
                                   tags=("odd" if i % 2 else "even",))
        self._refresh_totals()

    def _refresh_totals(self):
        sub = sum(e["subtotal"] for e in self.cart)
        rate = DISCOUNT_RATES[self.discount_type.get()]
        disc = sub * rate
        total = sub - disc
        vat = total * 0.12
        grand = total + vat

        self._lbl_sub.configure(text=f"₱{sub:,.2f}")
        self._lbl_disc.configure(text=f"-₱{disc:,.2f}")
        self._lbl_tot.configure(text=f"₱{total:,.2f}")
        self._lbl_vat.configure(text=f"₱{vat:,.2f}")
        self._lbl_grand.configure(text=f"₱{grand:,.2f}", fg=RED if grand > 0 else TEXT_MID)

    def _checkout(self):
        if not self.cart:
            messagebox.showwarning("Empty Order", "Please add items to your order first.", parent=self)
            return

        sub = sum(e["subtotal"] for e in self.cart)
        rate = DISCOUNT_RATES[self.discount_type.get()]
        disc = sub * rate
        total = sub - disc
        vat = total * 0.12
        grand = total + vat

        pay_win = tk.Toplevel(self)
        pay_win.title("Select Payment Method")
        pay_win.geometry("380x320")
        pay_win.resizable(False, False)
        pay_win.configure(bg=CREAM)
        pay_win.transient(self)
        pay_win.grab_set()

        selected_method = tk.StringVar(value="")

        tk.Label(pay_win, text="💳 Choose Payment Type", font=("Georgia", 14, "bold"), bg=RED, fg=YELLOW, pady=10).pack(fill="x")
        tk.Label(pay_win, text=f"Amount Due: ₱{grand:,.2f}", font=("Segoe UI", 12, "bold"), bg=CREAM, fg=DARK_RED, pady=10).pack()

        methods_frame = tk.Frame(pay_win, bg=CREAM)
        methods_frame.pack(pady=5)

        pay_options = [
            ("💵 Cash / Counter", "Cash")
        ]

        for text, val in pay_options:
            rb = tk.Radiobutton(methods_frame, text=text, variable=selected_method, value=val,
                                font=("Segoe UI", 10), bg=CREAM, fg=TEXT_DARK, 
                                activebackground=CREAM, anchor="w", width=30)
            rb.pack(anchor="w", pady=4)

        def proceed_payment():
            if not selected_method.get():
                messagebox.showwarning("Payment", "Please select a payment method first.", parent=pay_win)
                return
            pay_win.destroy()
            self._complete_checkout_flow(grand, selected_method.get(), sub, disc, total, vat)

        tk.Button(pay_win, text="Proceed ➔", font=("Segoe UI", 11, "bold"), bg=GREEN, fg="white",
                  relief="flat", padx=20, pady=8, cursor="hand2", command=proceed_payment).pack(pady=15)

    def _get_numeric_input(self, title, prompt):
        while True:
            val = simpledialog.askstring(title, prompt, parent=self)
            if val is None:
                return None
            clean = val.replace(" ", "").replace("-", "")
            if clean.isdigit():
                return val
            else:
                messagebox.showerror("Invalid Input", "Characters rejected. Please enter numbers only.", parent=self)

    def _large_cash_input(self, grand):
        result = {"value": None}

        win = tk.Toplevel(self)
        win.title("Cash Payment")
        win.geometry("600x300")
        win.configure(bg=CREAM)
        win.transient(self)
        win.grab_set()

        tk.Label(
            win,
            text=f"Grand Total: ₱{grand:,.2f}",
            font=("Segoe UI", 20, "bold"),
            bg=CREAM,
            fg=DARK_RED
        ).pack(pady=(20,10))

        tk.Label(
            win,
            text="Enter Cash Payment Amount (₱)",
            font=("Segoe UI", 16),
            bg=CREAM
        ).pack()

        entry = tk.Entry(win, font=("Segoe UI", 20), justify="center")
        entry.pack(padx=30, pady=15, fill="x")

        def ok():
            result["value"] = entry.get()
            win.destroy()

        def cancel():
            win.destroy()

        btns = tk.Frame(win, bg=CREAM)
        btns.pack(pady=15)

        tk.Button(btns, text="OK", font=("Segoe UI", 14, "bold"),
                  width=10, command=ok).pack(side="left", padx=10)
        tk.Button(btns, text="Cancel", font=("Segoe UI", 14),
                  width=10, command=cancel).pack(side="left", padx=10)

        entry.focus_set()
        self.wait_window(win)
        return result["value"]

    def _complete_checkout_flow(self, grand, method_type, sub, disc, total, vat):
        if method_type == "Cash":
            while True:
                pay_str = self._large_cash_input(grand)
                if pay_str is None:
                    return
                try:
                    payment = float(pay_str.replace(",", "").replace("₱", "").strip())
                except ValueError:
                    messagebox.showerror("Invalid Amount", "Please enter a valid numeric value.", parent=self)
                    continue
                if payment < grand:
                    messagebox.showerror("Insufficient Payment", f"₱{payment:,.2f} is less than total ₱{grand:,.2f}.", parent=self)
                    continue
                break
            change = payment - grand
            ref_num = f"CSH-{int(datetime.datetime.now().timestamp())}"
            
            # DB PERSISTENCE SYSTEM COMMITMENT
            conn = sqlite3.connect("kiosk_system.db")
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO sales (ref_num, timestamp, order_type, discount_type, subtotal, discount, vat, grand_total, payment, change_due)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (ref_num, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.order_type.get(), self.discount_type.get(), sub, disc, vat, grand, payment, change))
                
                for item in self.cart:
                    cursor.execute("""
                        INSERT INTO sales_items (ref_num, item_id, item_name, price, qty, subtotal)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (ref_num, item["id"], item["name"], item["price"], item["qty"], item["subtotal"]))
                    
                    cursor.execute("""
                        UPDATE inventory SET stock_level = stock_level - ? WHERE item_id = ?
                    """, (item["qty"], item["id"]))
                conn.commit()
            except sqlite3.Error as e:
                messagebox.showerror("Database Transaction Error", f"Failed to log entry safely: {str(e)}", parent=self)
            finally:
                conn.close()

            self._show_receipt(sub, disc, total, vat, grand, payment, change, method_type, ref_num)

    def _show_receipt(self, sub, disc, total, vat, grand, payment, change, method, ref_num, account=""):
        now = datetime.datetime.now()

        win = tk.Toplevel(self)
        win.title("🧾 Receipt")
        win.configure(bg=CREAM)
        win.geometry("500x700")
        win.grab_set()

        outer = tk.Frame(win, bg=CREAM)
        outer.pack(fill="both", expand=True, padx=20, pady=14)

        c = tk.Canvas(outer, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
        sb = ttk.Scrollbar(outer, orient="vertical", command=c.yview)
        c.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        c.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(c, bg=CARD_BG, padx=28, pady=18)
        c.create_window(0, 0, anchor="nw", window=inner)
        inner.bind("<Configure>", lambda e: c.configure(scrollregion=c.bbox("all")))

        def row(left, right, lft_font=None, rgt_font=None, lc=TEXT_MID, rc=TEXT_DARK):
            f = tk.Frame(inner, bg=CARD_BG); f.pack(fill="x", pady=1)
            tk.Label(f, text=left, font=lft_font or ("Segoe UI",9), bg=CARD_BG, fg=lc).pack(side="left")
            tk.Label(f, text=right, font=rgt_font or ("Segoe UI",9,"bold"), bg=CARD_BG, fg=rc).pack(side="right")

        def divider(color=BORDER, h=1, pady=6):
            tk.Frame(inner, bg=color, height=h).pack(fill="x", pady=pady)

        tk.Label(inner, text="JOLLIBEE", font=("Georgia",22,"bold"), bg=CARD_BG, fg=RED).pack()
        tk.Label(inner, text="Self-Service Kiosk", font=("Segoe UI",10), bg=CARD_BG, fg=TEXT_MID).pack()
        divider(BORDER, 1, 8)

        row("Order No.",   ref_num)
        row("Date",        now.strftime("%B %d, %Y"))
        row("Time",        now.strftime("%I:%M:%S %p"))
        row("Order Type",  self.order_type.get())
        row("Payment via", f"{method} {('*' + account[-4:]) if account else ''}")

        if self.discount_type.get() != "None":
            row("Discount Applied", f"{self.discount_type.get()} ({int(DISCOUNT_RATES[self.discount_type.get()]*100)}%)", rc=GREEN)

        divider(BORDER, 1, 8)
        tk.Label(inner, text="ORDERED ITEMS", font=("Segoe UI",9,"bold"), bg=CARD_BG, fg=TEXT_MID).pack(anchor="w")
        divider(BORDER, 1, 2)

        for e in self.cart:
            row(f"{e['name']}  ×{e['qty']}", f"₱{e['subtotal']:,.2f}")

        divider(BORDER, 1, 8)
        row("Subtotal",          f"₱{sub:,.2f}")
        if disc > 0:
            row("Discount",      f"-₱{disc:,.2f}", rc=GREEN)
        row("Total (ex. VAT)",   f"₱{total:,.2f}")
        row("VAT (12%)",         f"₱{vat:,.2f}", rc=TEXT_MID)
        divider(RED, 2, 4)

        f = tk.Frame(inner, bg=CARD_BG); f.pack(fill="x", pady=2)
        tk.Label(f, text="GRAND TOTAL", font=("Georgia",14,"bold"), bg=CARD_BG, fg=RED).pack(side="left")
        tk.Label(f, text=f"₱{grand:,.2f}", font=("Georgia",14,"bold"), bg=CARD_BG, fg=RED).pack(side="right")

        divider(RED, 2, 4)
        row("Amount Tendered",  f"₱{payment:,.2f}", rc=TEXT_DARK)
        row("Change Due",       f"₱{change:,.2f}", rc=GREEN)
        divider(BORDER, 1, 12)
        
        tk.Label(inner, text="Thank you for choosing Jollibee! ", font=("Georgia",11,"italic"), bg=CARD_BG, fg=RED).pack()
        tk.Label(inner, text="Be happy. Be Jollibee. ", font=("Segoe UI",9), bg=CARD_BG, fg=TEXT_LITE).pack(pady=(0,12))

        btn_row = tk.Frame(win, bg=CREAM)
        btn_row.pack(fill="x", padx=20, pady=(0,14))

        # ─────────────────────────────────────────────────────────────────────
        # REFACTORED REPORTLAB PDF EXPORT (FIXED LEFT ALIGNMENT)
        # ─────────────────────────────────────────────────────────────────────
        def save_receipt():
            try:
                pdf_name = f"receipt_{ref_num}.pdf"
                width = 80 * mm
                
                # Dynamic height calculation based on item count to avoid visual cutoffs
                base_height = 180 * mm
                item_height = len(self.cart) * 6 * mm
                height = base_height + item_height
                
                cpdf = canvas.Canvas(pdf_name, pagesize=(width, height))
                
                # Starting high y boundary setup
                y = height - 12 * mm
                
                # 1. Header Banner Branding
                cpdf.setFont("Helvetica-Bold", 14)
                cpdf.setFillColorRGB(0.847, 0.125, 0.180) # Jollibee Red
                cpdf.drawCentredString(width / 2, y, "JOLLIBEE")
                
                y -= 4 * mm
                cpdf.setFont("Helvetica", 8)
                cpdf.setFillColorRGB(0.33, 0.33, 0.33)
                cpdf.drawCentredString(width / 2, y, "Self-Service Kiosk Terminal Copy")
                
                # Line Divider
                y -= 4 * mm
                cpdf.setStrokeColorRGB(0.87, 0.78, 0.62) # Light sand border color
                cpdf.setLineWidth(0.5)
                cpdf.line(5 * mm, y, width - 5 * mm, y)
                
                # 2. Metadata Context Informational Block
                y -= 5 * mm
                cpdf.setFont("Helvetica-Bold", 8)
                cpdf.setFillColorRGB(0.1, 0.1, 0.1)
                cpdf.drawString(6 * mm, y, "Order No:")
                cpdf.drawRightString(width - 6 * mm, y, ref_num)
                
                y -= 4 * mm
                cpdf.setFont("Helvetica", 7.5)
                cpdf.drawString(6 * mm, y, "Time:")
                cpdf.drawRightString(width - 6 * mm, y, now.strftime("%b %d, %Y | %I:%M:%S %p"))
                
                y -= 4 * mm
                cpdf.drawString(6 * mm, y, "Order Type:")
                cpdf.drawRightString(width - 6 * mm, y, self.order_type.get())
                
                y -= 4 * mm
                cpdf.drawString(6 * mm, y, "Payment via:")
                cpdf.drawRightString(width - 6 * mm, y, method)
                
                # Line Divider
                y -= 4 * mm
                cpdf.line(5 * mm, y, width - 5 * mm, y)
                
                # 3. Itemized Structured Grid Table Layout
                y -= 5 * mm
                cpdf.setFont("Helvetica-Bold", 8)
                cpdf.drawString(6 * mm, y, "ORDERED ITEMS")
                
                y -= 3 * mm
                cpdf.line(5 * mm, y, width - 5 * mm, y)
                
                y -= 4 * mm
                cpdf.setFont("Helvetica", 8)
                for item in self.cart:
                    # Column definitions: Qty / Description / Subtotal Price
                    qty_string = f"{item['qty']}x"
                    name_string = item['name']
                    price_string = f"{item['subtotal']:,.2f}"
                    
                    cpdf.setFont("Helvetica-Bold", 8)
                    cpdf.drawString(6 * mm, y, qty_string)
                    cpdf.setFont("Helvetica", 8)
                    cpdf.drawString(13 * mm, y, name_string[:24]) # Crop safety boundary layout 
                    cpdf.drawRightString(width - 6 * mm, y, price_string)
                    y -= 5 * mm
                
                # Line Divider
                y -= 1 * mm
                cpdf.line(5 * mm, y, width - 5 * mm, y)
                
                # 4. Right Aligned Accounting Financial Ledger Block
                y -= 5 * mm
                cpdf.drawString(6 * mm, y, "Subtotal Price:")
                cpdf.drawRightString(width - 6 * mm, y, f"{sub:,.2f}")
                
                if disc > 0:
                    y -= 4 * mm
                    cpdf.drawString(6 * mm, y, f"Discount ({self.discount_type.get()}):")
                    cpdf.drawRightString(width - 6 * mm, y, f"-{disc:,.2f}")
                    
                y -= 4 * mm
                cpdf.drawString(6 * mm, y, "Tax Allocation (VAT 12%):")
                cpdf.drawRightString(width - 6 * mm, y, f"{vat:,.2f}")
                
                # Grand Total Double Bold Highlight Separation lines
                y -= 3 * mm
                cpdf.setStrokeColorRGB(0.847, 0.125, 0.180)
                cpdf.setLineWidth(1)
                cpdf.line(6 * mm, y, width - 5 * mm, y)
                
                y -= 4 * mm
                cpdf.setFont("Helvetica-Bold", 10)
                cpdf.setFillColorRGB(0.847, 0.125, 0.180)
                cpdf.drawString(6 * mm, y, "GRAND TOTAL:")
                cpdf.drawRightString(width - 6 * mm, y, f"PHP {grand:,.2f}")
                
                y -= 2 * mm
                cpdf.line(6 * mm, y, width - 5 * mm, y)
                
                # Tender details bookkeeping tracking elements
                y -= 5 * mm
                cpdf.setFont("Helvetica", 8)
                cpdf.setFillColorRGB(0.1, 0.1, 0.1)
                cpdf.drawString(6 * mm, y, "Amount Tendered:")
                cpdf.drawRightString(width - 6 * mm, y, f"{payment:,.2f}")
                
                y -= 4 * mm
                cpdf.drawString(6 * mm, y, "Change Due:")
                cpdf.drawRightString(width - 6 * mm, y, f"{change:,.2f}")
                
                # Footer Signoff branding elements context layout structures
                y -= 10 * mm
                cpdf.setStrokeColorRGB(0.87, 0.78, 0.62)
                cpdf.setLineWidth(0.5)
                cpdf.line(5 * mm, y, width - 5 * mm, y)
                
                y -= 5 * mm
                cpdf.setFont("Helvetica-Oblique", 9)
                cpdf.setFillColorRGB(0.847, 0.125, 0.180)
                cpdf.drawCentredString(width / 2, y, "Thank you for choosing Jollibee! 🍗")
                
                y -= 4 * mm
                cpdf.setFont("Helvetica", 7.5)
                cpdf.setFillColorRGB(0.5, 0.5, 0.5)
                cpdf.drawCentredString(width / 2, y, "Be happy. Be Jollibee. ✨")
                
                cpdf.showPage()
                cpdf.save()
                messagebox.showinfo("Saved", f"Receipt saved as PDF:\n{pdf_name}", parent=win)
            except Exception as ex:
                messagebox.showerror("Error Saving", str(ex), parent=win)

        def new_order():
            self.cart.clear()
            self._refresh_cart_ui()
            self.discount_type.set("None")
            self.delivery_name = ""
            self.delivery_phone = ""
            self.delivery_address_val = ""
            win.destroy()
            self._status.configure(text="✅  Order complete! Thank you. Start a new order anytime.")

        tk.Button(btn_row, text="💾 Save Receipt", font=("Segoe UI",10,"bold"),
                  bg=DARK_RED, fg="white", relief="flat", padx=12, pady=6,
                  cursor="hand2", command=save_receipt).pack(side="left", padx=(0,8))
        tk.Button(btn_row, text="🆕 New Order", font=("Segoe UI",10,"bold"),
                  bg=RED, fg=YELLOW, relief="flat", padx=12, pady=6,
                  cursor="hand2", command=new_order).pack(side="left")
        tk.Button(btn_row, text="✖ Close", font=("Segoe UI",10),
                  bg="#888", fg="white", relief="flat", padx=10, pady=6,
                  cursor="hand2", command=win.destroy).pack(side="right")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_database()
    if not PIL_AVAILABLE:
        root = tk.Tk(); root.withdraw()
        from tkinter import messagebox as mb
        mb.showwarning(
            "Pillow Not Installed",
            "Food photos require Pillow.\n\nTo enable them, run:\n\n"
            "   pip install pillow requests\n\n"
            "The app will work fine without it — items will show colored emoji icons instead."
        )
        root.destroy()

    app = JollibeeKiosk()
    app.mainloop()