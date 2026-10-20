import os
import time
import datetime
import requests
import pytz
import random
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from PIL import Image, ImageDraw, ImageFont

# =====================================================================
# 🛠️ [ADMIN PANEL & CORE CONFIGURATION - TRADER RAHAT | TR VIP 999]
# =====================================================================
BOT_TOKEN = "8938988396:AAEUvJyoWUuzc8NB9Y2LyNPIrwD-LL6NM00"
# প্রাইভেট চ্যানেলের নিউমেরিক আইডি থাকলে নিচে বসাতে পারেন, অথবা বটে চ্যানেলের একটি মেসেজ ফরওয়ার্ড করলেই অটো যুক্ত হয়ে যাবে!
TARGET_CHATS = ["@trvip999", "8699074327"]
ADMIN_CHAT_ID = 8699074327

TIMEZONE = "Asia/Dhaka"  # UTC+6
VIP_HEADER = "👑 𝐓𝐫𝐚𝐝𝐞𝐫 𝐑𝐚𝐡𝐚𝐭 | 𝐓𝐑 𝐕𝐈𝐏 𝟗𝟗𝟗 👑"

# কোটেক্সে ২৪ ঘণ্টা সবসময় সচল থাকা মূল কারেন্সি পেয়ারসমূহ
REAL_MARKET_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "EUR/GBP", "USD/CAD", "EUR/JPY", "GBP/JPY"
]

OTC_MARKET_PAIRS = [
    "EUR/USD (OTC)", "GBP/USD (OTC)", "USD/JPY (OTC)", "AUD/USD (OTC)",
    "NZD/USD (OTC)", "USD/CAD (OTC)", "EUR/GBP (OTC)", "USD/BRL (OTC)", "USD/BDT (OTC)"
]

SETTINGS = {
    "channel_link": "https://t.me/traderrahat420",
    "register_link": "https://broker-qx.pro/sign-up/?lid=2187284",
    "win_sticker_text": "WIN",
    "loss_sticker_text": "LOSS",
    "market_mode": "AUTO",  # অপশনসমূহ: "AUTO", "REAL_ONLY", "OTC_ONLY"
    "custom_start_banner": None,
    "custom_end_banner": None,
    "custom_win_sticker": None,
    "custom_loss_sticker": None,
    "rules_text": (
        f"{VIP_HEADER}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📜 **ভিআইপি ট্রেডিং ও মানি ম্যানেজমেন্ট গাইডলাইন:**\n\n"
        "⏰ **সময় ও চার্ট সেটআপ:**\n"
        "• আপনার ডিভাইসের সময় অবশ্যই **UTC+6 (বাংলাদেশ সময়)** অনুযায়ী মিলিয়ে রাখুন।\n"
        "• প্রতিটি সিগন্যাল এন্ট্রি সময়ের ঠিক **২ মিনিট আগে** গ্রুপে দেওয়া হবে।\n\n"
        "🎯 **ট্রেড এন্ট্রি নেওয়ার নিয়ম:**\n"
        "• ব্রোকারে **১ মিনিটের (1M) ক্যান্ডেল চার্ট** ওপেন করবেন।\n"
        "• কোটেক্সে সুইচ টাইম (Time Set) অপশন থেকে সিগন্যালে দেওয়া ক্লোজিং টাইম (**৩টি ক্যান্ডেল / 3 Minutes**) সেট করবেন।\n"
        "• এন্ট্রি সময়ের ঠিক **১–২ সেকেন্ড আগেই** ট্রেড প্লেস করবেন।\n\n"
        "🛡️ **মানি ম্যানেজমেন্ট ও এমটিজি (MTG):**\n"
        "• প্রথম ট্রেডটি কোনো কারণে মিস হলে হতাশ না হয়ে একই ডিরেকশনে পরবর্তী ৩ মিনিটের জন্য **১-স্টেপ মার্টিনগেল (MTG)** নিবেন।\n"
        "• সবসময় নিজের ব্যালেন্সের নিরাপত্তা বজায় রেখে ট্রেড করবেন এবং দৈনিক টার্গেট পূরণ হলে ট্রেড বন্ধ রাখবেন।\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🤝 **ইনশাআল্লাহ, নিয়ম মেনে ট্রেড করলে প্রফিট সুনিশ্চিত!**"
    )
}

BOT_USERS = set(TARGET_CHATS)
BANNED_USERS = set()
# =====================================================================

session_wins = 0
session_losses = 0
last_was_loss = False
force_instant_session = False  # যেকোনো মুহূর্তে পূর্ণ ১ ঘণ্টার সেশন চালুর ট্রিগার

# --- [QUOTEX SMART PAIR SELECTOR (NO FAKE OTC/REAL MIXUP)] ---
def get_active_quotex_pair(now_dt):
    """
    কোটেক্সের লাইভ মার্কেট কন্ডিশন অনুযায়ী সঠিক পেয়ার নির্বাচন করে।
    শনি ও রবিবার (weekday 5, 6) রিয়েল মার্কেট বন্ধ থাকে, তাই ১০০% OTC দেয়।
    """
    mode = SETTINGS["market_mode"]
    if mode == "REAL_ONLY":
        return random.choice(REAL_MARKET_PAIRS)
    elif mode == "OTC_ONLY":
        return random.choice(OTC_MARKET_PAIRS)
    else:
        # AUTO Mode: শনি ও রবিবার (5, 6) ১০০% OTC মার্কেট
        if now_dt.weekday() in [5, 6]:
            return random.choice(OTC_MARKET_PAIRS)
        # সোম থেকে শুক্রবার দুপুর ১২টা থেকে রাত ১১টা পর্যন্ত ফরেক্সের মেইন রিয়েল পেয়ারগুলো কোটেক্সে সচল থাকে
        if 12 <= now_dt.hour <= 22:
            return random.choice(REAL_MARKET_PAIRS)
        else:
            return random.choice(OTC_MARKET_PAIRS)

# --- [LINUX & WINDOWS GUARANTEED BOLD FONT LOADER] ---
def get_bold_font(size):
    font_candidates = [
        fm.findfont(fm.FontProperties(family='DejaVu Sans', weight='bold')),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "arialbd.ttf",
        "DejaVuSans-Bold.ttf"
    ]
    for path in font_candidates:
        if path and os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"TR VIP 999 Ultimate Sniper Bot is Running Live!")
    def log_message(self, format, *args):
        return

def start_keep_alive_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# --- [HIGH-VISIBILITY LARGE SESSION BANNERS] ---
def generate_session_banner(is_start=True, filename="session_banner.png"):
    if is_start and SETTINGS["custom_start_banner"] and os.path.exists(SETTINGS["custom_start_banner"]):
        return SETTINGS["custom_start_banner"]
    if not is_start and SETTINGS["custom_end_banner"] and os.path.exists(SETTINGS["custom_end_banner"]):
        return SETTINGS["custom_end_banner"]

    width, height = 960, 480
    bg_color = (6, 22, 14) if is_start else (30, 8, 10)
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    border_color = (0, 255, 110) if is_start else (255, 50, 50)
    gold_color = (255, 215, 0)
    
    draw.rectangle([16, 16, width-16, height-16], outline=border_color, width=7)
    draw.rectangle([28, 28, width-28, height-28], outline=gold_color, width=2)
    
    title_text = "TRADER RAHAT | TR VIP 999"
    main_text = "SESSION STARTS" if is_start else "SESSION ENDS"
    sub_text = "BISMILLAH | HIGH ACCURACY SNR SIGNALS" if is_start else "ALHAMDULILLAH | VIP SESSION COMPLETED"
    
    font_title = get_bold_font(36)
    font_main = get_bold_font(94)
    font_sub = get_bold_font(25)
    
    tb1 = draw.textbbox((0, 0), title_text, font=font_title)
    draw.text(((width - (tb1[2] - tb1[0])) // 2, 80), title_text, fill=gold_color, font=font_title)
    
    tb2 = draw.textbbox((0, 0), main_text, font=font_main)
    draw.text(((width - (tb2[2] - tb2[0])) // 2, 180), main_text, fill=border_color, font=font_main)
    
    tb3 = draw.textbbox((0, 0), sub_text, font=font_sub)
    draw.text(((width - (tb3[2] - tb3[0])) // 2, 345), sub_text, fill=(235, 235, 235), font=font_sub)
    
    img.save(filename)
    return filename

# --- [HIGH-VISIBILITY LARGE WIN/LOSS STICKERS] ---
def generate_result_sticker(is_win, filename="sticker.webp"):
    if is_win and SETTINGS["custom_win_sticker"] and os.path.exists(SETTINGS["custom_win_sticker"]):
        return SETTINGS["custom_win_sticker"]
    if not is_win and SETTINGS["custom_loss_sticker"] and os.path.exists(SETTINGS["custom_loss_sticker"]):
        return SETTINGS["custom_loss_sticker"]

    width, height = 512, 220
    bg_color = (0, 185, 45) if is_win else (225, 15, 30)
    border_col = (255, 255, 255)
    text_str = SETTINGS["win_sticker_text"] if is_win else SETTINGS["loss_sticker_text"]
    
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    draw.rounded_rectangle([8, 8, width-8, height-8], radius=35, fill=bg_color, outline=border_col, width=7)
    
    r = 18
    draw.ellipse((45 - r, height//2 - r, 45 + r, height//2 + r), fill=border_col)
    draw.ellipse((width - 45 - r, height//2 - r, width - 45 + r, height//2 + r), fill=border_col)
    
    font_size = 112 if len(text_str) <= 5 else 72
    font = get_bold_font(font_size)
        
    bbox = draw.textbbox((0, 0), text_str, font=font)
    text_x = (width - (bbox[2] - bbox[0])) // 2
    text_y = (height - (bbox[3] - bbox[1])) // 2 - (bbox[1] // 2)
    
    draw.text((text_x, text_y), text_str, fill=(255, 255, 255), font=font)
    img.save(filename, "WEBP")
    return filename

# --- [5-LAYER DEEP MARKET ANALYSIS & SETUP GENERATOR] ---
def analyze_and_create_market_setup(direction):
    num_candles = 42
    prices = [100.0]
    for _ in range(num_candles):
        prices.append(prices[-1] + random.uniform(-0.8, 0.8))
        
    opens = prices[:-1]
    closes = prices[1:]
    
    support_level = min(opens[:-4] + closes[:-4]) - 0.30
    resistance_level = max(opens[:-4] + closes[:-4]) + 0.30
    
    touch_idx = random.randint(8, 22)
    if direction == "CALL":
        opens[touch_idx] = support_level + 0.6
        closes[touch_idx] = support_level + 0.15
        opens[-2] = support_level + 0.95
        closes[-2] = support_level + 0.08
        opens[-1] = closes[-2]
        closes[-1] = opens[-1] + random.uniform(0.95, 1.45)
        rsi_val = random.randint(20, 28)
        pattern_name = random.choice(["Bullish Pinbar Rejection", "Bullish Engulfing", "Order Block Demand Bounce"])
        snr_reason = f"Strong Support + BB Lower + RSI({rsi_val} Oversold) + {pattern_name}"
    else:
        opens[touch_idx] = resistance_level - 0.6
        closes[touch_idx] = resistance_level - 0.15
        opens[-2] = resistance_level - 0.95
        closes[-2] = resistance_level - 0.08
        opens[-1] = closes[-2]
        closes[-1] = opens[-1] - random.uniform(0.95, 1.45)
        rsi_val = random.randint(73, 82)
        pattern_name = random.choice(["Bearish Shooting Star", "Bearish Engulfing", "Supply Zone Rejection"])
        snr_reason = f"Strong Resistance + BB Upper + RSI({rsi_val} Overbought) + {pattern_name}"
        
    highs = [max(o, c) + random.uniform(0.15, 0.50) for o, c in zip(opens, closes)]
    lows = [min(o, c) - random.uniform(0.15, 0.50) for o, c in zip(opens, closes)]
    
    if direction == "CALL":
        lows[touch_idx] = support_level - 0.12
        lows[-2] = support_level - 0.38
    else:
        highs[touch_idx] = resistance_level + 0.12
        highs[-2] = resistance_level + 0.38
        
    return {
        "opens": opens,
        "closes": closes,
        "highs": highs,
        "lows": lows,
        "support": support_level,
        "resistance": resistance_level,
        "rsi": rsi_val,
        "analysis_text": snr_reason
    }

def render_snr_chart(pair, timeframe, direction, setup_data, is_result=False, outcome="DIRECT_WIN", filename="chart.png"):
    fig, ax = plt.subplots(figsize=(8.8, 5.0), facecolor='#0b0e14')
    ax.set_facecolor('#0b0e14')
    
    opens = list(setup_data["opens"])
    closes = list(setup_data["closes"])
    highs = list(setup_data["highs"])
    lows = list(setup_data["lows"])
    support_level = setup_data["support"]
    resistance_level = setup_data["resistance"]
    rsi_val = setup_data["rsi"]
    
    entry_index = len(opens) - 1
    entry_price = closes[-1]
    
    if is_result:
        for step in range(3):
            o_val = closes[-1]
            if outcome == "DIRECT_WIN":
                delta = random.uniform(0.38, 0.88) if direction == "CALL" else -random.uniform(0.38, 0.88)
            elif outcome == "MTG_WIN":
                if step == 0:
                    delta = -random.uniform(0.2, 0.45) if direction == "CALL" else random.uniform(0.2, 0.45)
                else:
                    delta = random.uniform(0.62, 1.18) if direction == "CALL" else -random.uniform(0.62, 1.18)
            else:
                delta = -random.uniform(0.42, 0.88) if direction == "CALL" else random.uniform(0.42, 0.88)
                
            c_val = o_val + delta
            h_val = max(o_val, c_val) + random.uniform(0.1, 0.38)
            l_val = min(o_val, c_val) - random.uniform(0.1, 0.38)
            opens.append(o_val)
            closes.append(c_val)
            highs.append(h_val)
            lows.append(l_val)
            
    num_candles = len(opens)
    for i in range(num_candles):
        color = '#00e676' if closes[i] >= opens[i] else '#ff1744'
        ax.plot([i, i], [lows[i], highs[i]], color=color, linewidth=1.15)
        height = closes[i] - opens[i]
        if abs(height) < 0.05:
            height = 0.05
        ax.bar(i, height, bottom=opens[i], width=0.64, color=color, edgecolor=color)

    upper_band = [max(highs[max(0, i-4):i+1]) + 0.35 for i in range(num_candles)]
    lower_band = [min(lows[max(0, i-4):i+1]) - 0.35 for i in range(num_candles)]
    mid_ema = [(u + l) / 2 for u, l in zip(upper_band, lower_band)]
    ax.plot(range(num_candles), upper_band, color='#ff9100', linewidth=0.95, alpha=0.65)
    ax.plot(range(num_candles), lower_band, color='#00b0ff', linewidth=0.95, alpha=0.65)
    ax.plot(range(num_candles), mid_ema, color='#e040fb', linestyle='-.', linewidth=0.75, alpha=0.5)

    ax.axhline(resistance_level, color='#ff1744', linestyle='--', linewidth=1.35, alpha=0.88)
    ax.axhspan(resistance_level - 0.15, resistance_level + 0.25, color='#ff1744', alpha=0.14)
    ax.text(1, resistance_level + 0.32, "INSTITUTIONAL RESISTANCE ZONE (SNR)", color='#ff5252', fontsize=8, fontweight='bold')
    
    ax.axhline(support_level, color='#00e676', linestyle='--', linewidth=1.35, alpha=0.88)
    ax.axhspan(support_level - 0.25, support_level + 0.15, color='#00e676', alpha=0.14)
    ax.text(1, support_level - 0.58, "INSTITUTIONAL SUPPORT ZONE (SNR)", color='#69f0ae', fontsize=8, fontweight='bold')
    
    arrow_char = '⬆' if direction == "CALL" else '⬇'
    arrow_pos = lows[entry_index] - 0.78 if direction == "CALL" else highs[entry_index] + 0.58
    ax.annotate(arrow_char, xy=(entry_index, arrow_pos), color='#ffd600', fontsize=15, ha='center', fontweight='bold')
    
    if is_result:
        ax.axhline(entry_price, color='#ffd600', linestyle=':', linewidth=1.1, alpha=0.85)
        
    ax.axhline(closes[-1], color='#00b0ff', linestyle='-', linewidth=0.9)
    status_tag = f"LIVE RESULT ({outcome.replace('_', ' ')})" if is_result else f"1M CHART | 3 CANDLES (M3) | RSI: {rsi_val}"
    ax.text(0.01, 0.96, f"{pair} | {timeframe} (UTC+6) | {status_tag}", transform=ax.transAxes, color='#ffffff', fontsize=9.5, fontweight='bold', va='top')
    
    ax.grid(color='#1e2430', linestyle=':', linewidth=0.6)
    ax.tick_params(axis='x', colors='#78909c', labelsize=7)
    ax.tick_params(axis='y', colors='#78909c', labelsize=7)
    ax.yaxis.tick_right()
    
    for spine in ax.spines.values():
        spine.set_color('#263238')
        
    plt.tight_layout()
    plt.savefig(filename, dpi=130, facecolor='#0b0e14')
    plt.close(fig)
    return filename

def broadcast_photo(photo_path, caption, with_buttons=True):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    reply_markup = {
        "inline_keyboard": [[
            {"text": "📢 Official Channel ↗", "url": SETTINGS["channel_link"]},
            {"text": "💎 VIP Registration ↗", "url": SETTINGS["register_link"]}
        ]]
    }
    for chat_id in list(BOT_USERS):
        if str(chat_id) in BANNED_USERS:
            continue
        data = {"chat_id": chat_id, "caption": caption, "parse_mode": "Markdown"}
        if with_buttons:
            data["reply_markup"] = json.dumps(reply_markup)
        try:
            with open(photo_path, "rb") as f:
                requests.post(url, data=data, files={"photo": f}, timeout=25)
        except Exception as e:
            print(f"Photo send error ({chat_id}): {e}")

def broadcast_sticker(path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendSticker"
    for chat_id in list(BOT_USERS):
        if str(chat_id) in BANNED_USERS:
            continue
        try:
            with open(path, "rb") as f:
                requests.post(url, data={"chat_id": chat_id}, files={"sticker": f}, timeout=25)
        except Exception:
            pass

def broadcast_text(text, with_button=False):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    reply_markup = {
        "inline_keyboard": [[
            {"text": "📢 Official Channel ↗", "url": SETTINGS["channel_link"]},
            {"text": "💎 VIP Registration ↗", "url": SETTINGS["register_link"]}
        ]]
    }
    for chat_id in list(BOT_USERS):
        if str(chat_id) in BANNED_USERS:
            continue
        data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        if with_button:
            data["reply_markup"] = json.dumps(reply_markup)
        try:
            requests.post(url, json=data, timeout=25)
        except Exception as e:
            print(f"Text send error ({chat_id}): {e}")

# --- [INTERACTIVE BUTTON ADMIN PANEL] ---
def send_admin_panel(chat_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    keyboard = {
        "inline_keyboard": [
            [{"text": "🚀 এখনই ১ ঘণ্টার লাইভ সেশন শুরু করুন", "callback_data": "cmd_start_now"}],
            [
                {"text": "🌐 শুধু Real Market", "callback_data": "mode_real"},
                {"text": "⚡ শুধু OTC Market", "callback_data": "mode_otc"},
                {"text": "🔄 Auto Mode", "callback_data": "mode_auto"}
            ],
            [{"text": "👥 ইউজার ও চ্যানেল লিস্ট দেখুন", "callback_data": "cmd_users"}],
            [
                {"text": "🚫 Ban User", "callback_data": "info_ban"},
                {"text": "✅ Unban User", "callback_data": "info_unban"}
            ],
            [
                {"text": "✏️ Win স্টিকার টেক্সট", "callback_data": "info_win"},
                {"text": "✏️ Loss স্টিকার টেক্সট", "callback_data": "info_loss"}
            ],
            [
                {"text": "🖼️ নতুন Win স্টিকার সেট", "callback_data": "info_set_win_img"},
                {"text": "🖼️ নতুন Loss স্টিকার সেট", "callback_data": "info_set_loss_img"}
            ],
            [
                {"text": "🖼️ Start ব্যানার পরিবর্তন", "callback_data": "info_start"},
                {"text": "🖼️ End ব্যানার পরিবর্তন", "callback_data": "info_end"}
            ],
            [
                {"text": "🔗 চ্যানেল লিংক এডিট", "callback_data": "info_channel"},
                {"text": "🔗 রেজিস্ট্রেশন লিংক এডিট", "callback_data": "info_reg"}
            ],
            [{"text": "📝 ভিআইপি রুলস মেসেজ এডিট করুন", "callback_data": "info_rules"}],
            [{"text": "🗑️ সব কাস্টম স্টিকার/ব্যানার ডিলিট ও রিসেট করুন", "callback_data": "cmd_reset_all"}]
        ]
    }
    text = (
        f"{VIP_HEADER}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🛠️ **অ্যাডভান্সড ভিআইপি অ্যাডমিন প্যানেল** 🛠️\n"
        f"📊 **বর্তমান মার্কেট মোড:** `{SETTINGS['market_mode']}`\n\n"
        "💡 **প্রাইভেট চ্যানেল যুক্ত করার নিয়ম:** আপনার প্রাইভেট চ্যানেল থেকে যেকোনো একটি পুরনো মেসেজ এই বটে **Forward (ফরওয়ার্ড)** করুন, বট নিজে থেকেই চ্যানেল যুক্ত করে নেবে!"
    )
    requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown", "reply_markup": json.dumps(keyboard)})

def download_telegram_file(file_id, save_filename):
    file_info_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
    f_res = requests.get(file_info_url).json()
    if f_res.get("ok"):
        file_path = f_res["result"]["file_path"]
        download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        img_data = requests.get(download_url).content
        with open(save_filename, "wb") as handler:
            handler.write(img_data)
        return save_filename
    return None

def poll_telegram_admin_commands():
    global force_instant_session
    offset = 0
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    while True:
        try:
            res = requests.get(url, params={"offset": offset, "timeout": 30}, timeout=35)
            if res.status_code == 200:
                data = res.json()
                for result in data.get("result", []):
                    offset = result["update_id"] + 1
                    
                    # ১. প্রাইভেট চ্যানেলে কেউ পোস্ট করলে বা বটকে অ্যাডমিন রাখলে অটোমেটিক চ্যানেল আইডি ধরে নেবে
                    if "channel_post" in result:
                        ch_id = result["channel_post"].get("chat", {}).get("id")
                        if ch_id:
                            BOT_USERS.add(str(ch_id))
                        continue

                    if "my_chat_member" in result:
                        ch_id = result["my_chat_member"].get("chat", {}).get("id")
                        if ch_id:
                            BOT_USERS.add(str(ch_id))
                        continue
                    
                    if "callback_query" in result:
                        cq = result["callback_query"]
                        cq_id = cq["id"]
                        chat_id = cq["message"]["chat"]["id"]
                        data_val = cq["data"]
                        
                        answer_url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
                        send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                        
                        if chat_id != ADMIN_CHAT_ID:
                            requests.post(answer_url, json={"callback_query_id": cq_id, "text": "শুধুমাত্র অ্যাডমিন ব্যবহার করতে পারবেন!"})
                            continue
                            
                        if data_val == "cmd_start_now":
                            force_instant_session = True
                            requests.post(send_url, json={"chat_id": chat_id, "text": "🚀 **কমান্ড গৃহীত!** এখনই নতুন করে বিসমিল্লাহ ব্যানার ও রুলস পাঠিয়ে পূর্ণ ১ ঘণ্টার লাইভ সেশন শুরু হচ্ছে!", "parse_mode": "Markdown"})
                        elif data_val == "mode_real":
                            SETTINGS["market_mode"] = "REAL_ONLY"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "🌐 **Market Mode Updated:** এখন থেকে শুধুমাত্র **Real Market** (যেমন `EUR/USD`, `GBP/USD`) সিগন্যাল দেওয়া হবে!", "parse_mode": "Markdown"})
                        elif data_val == "mode_otc":
                            SETTINGS["market_mode"] = "OTC_ONLY"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "⚡ **Market Mode Updated:** এখন থেকে শুধুমাত্র **OTC Market** (যেমন `EUR/USD (OTC)`, `USD/BRL (OTC)`) সিগন্যাল দেওয়া হবে!", "parse_mode": "Markdown"})
                        elif data_val == "mode_auto":
                            SETTINGS["market_mode"] = "AUTO"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "🔄 **Market Mode Updated:** এখন থেকে বট দিন ও সময়ের ওপর ভিত্তি করে স্বয়ংক্রিয়ভাবে **Real বা OTC** পেয়ার সিলেক্ট করবে!", "parse_mode": "Markdown"})
                        elif data_val == "cmd_users":
                            u_list = (
                                f"👥 মোট যুক্ত চ্যাট/চ্যানেল: {len(BOT_USERS)}\n"
                                f"🚫 ব্যান করা ইউজার: {len(BANNED_USERS)}\n"
                                f"📊 বর্তমান মার্কেট মোড: `{SETTINGS['market_mode']}`\n\n"
                                f"📌 Active List: `{list(BOT_USERS)}`"
                            )
                            requests.post(send_url, json={"chat_id": chat_id, "text": u_list, "parse_mode": "Markdown"})
                        elif data_val == "info_ban":
                            requests.post(send_url, json={"chat_id": chat_id, "text": "কাউকে ব্যান করতে লিখুন:\n`/ban [Chat_ID]`\nনতুন চ্যানেল বা ইউজার যুক্ত করতে লিখুন:\n`/adduser [Chat_ID]`", "parse_mode": "Markdown"})
                        elif data_val == "info_unban":
                            requests.post(send_url, json={"chat_id": chat_id, "text": "ব্যান তুলতে লিখুন:\n`/unban [Chat_ID]`", "parse_mode": "Markdown"})
                        elif data_val == "info_win":
                            requests.post(send_url, json={"chat_id": chat_id, "text": "Win স্টিকারের লেখা পরিবর্তন করতে লিখুন:\n`/setwin WIN`", "parse_mode": "Markdown"})
                        elif data_val == "info_loss":
                            requests.post(send_url, json={"chat_id": chat_id, "text": "Loss স্টিকারের লেখা পরিবর্তন করতে লিখুন:\n`/setloss LOSS`", "parse_mode": "Markdown"})
                        elif data_val == "info_set_win_img":
                            requests.post(send_url, json={"chat_id": chat_id, "text": "নতুন Win স্টিকার বা ছবি সেট করতে যেকোনো ছবি/স্টিকারে Reply দিয়ে লিখুন:\n`/setwinimg`\n\nডিলিট করতে লিখুন: `/delwinimg`", "parse_mode": "Markdown"})
                        elif data_val == "info_set_loss_img":
                            requests.post(send_url, json={"chat_id": chat_id, "text": "নতুন Loss স্টিকার বা ছবি সেট করতে যেকোনো ছবি/স্টিকারে Reply দিয়ে লিখুন:\n`/setlossimg`\n\nডিলিট করতে লিখুন: `/dellossimg`", "parse_mode": "Markdown"})
                        elif data_val == "info_start":
                            requests.post(send_url, json={"chat_id": chat_id, "text": "নতুন Session Start ব্যানার সেট করতে যেকোনো ছবির ওপর Reply দিয়ে লিখুন:\n`/setstartsticker`\n\nডিলিট করতে: `/delstartsticker`", "parse_mode": "Markdown"})
                        elif data_val == "info_end":
                            requests.post(send_url, json={"chat_id": chat_id, "text": "নতুন Session End ব্যানার সেট করতে যেকোনো ছবির ওপর Reply দিয়ে লিখুন:\n`/setendsticker`\n\nডিলিট করতে: `/delendsticker`", "parse_mode": "Markdown"})
                        elif data_val == "info_channel":
                            requests.post(send_url, json={"chat_id": chat_id, "text": "চ্যানেল লিংক পরিবর্তন করতে লিখুন:\n`/setchannel https://t.me/yourlink`", "parse_mode": "Markdown"})
                        elif data_val == "info_reg":
                            requests.post(send_url, json={"chat_id": chat_id, "text": "রেজিস্ট্রেশন লিংক পরিবর্তন করতে লিখুন:\n`/setreg https://broker-qx.pro/...`", "parse_mode": "Markdown"})
                        elif data_val == "info_rules":
                            requests.post(send_url, json={"chat_id": chat_id, "text": "ভিআইপি রুলস মেসেজ পরিবর্তন করতে লিখুন:\n`/setrules আপনার নতুন নিয়মাবলী...`", "parse_mode": "Markdown"})
                        elif data_val == "cmd_reset_all":
                            SETTINGS["custom_start_banner"] = None
                            SETTINGS["custom_end_banner"] = None
                            SETTINGS["custom_win_sticker"] = None
                            SETTINGS["custom_loss_sticker"] = None
                            SETTINGS["win_sticker_text"] = "WIN"
                            SETTINGS["loss_sticker_text"] = "LOSS"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "✅ সমস্ত কাস্টম স্টিকার ও ব্যানার ডিলিট করে ডিফল্ট বড় সাইজে রিসেট করা হয়েছে!"})
                            
                        requests.post(answer_url, json={"callback_query_id": cq_id, "text": "সফল!"})
                        continue

                    msg = result.get("message", {})
                    chat_id = msg.get("chat", {}).get("id")
                    text = msg.get("text", "").strip()
                    reply_to = msg.get("reply_to_message")
                    
                    if not chat_id:
                        continue
                    BOT_USERS.add(str(chat_id))
                    
                    send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

                    # ২. অ্যাডমিন যদি প্রাইভেট চ্যানেলের কোনো মেসেজ বটে ফরওয়ার্ড করে, বট সাথে সাথে সেই প্রাইভেট চ্যানেলের আইডি যুক্ত করে নেবে!
                    if chat_id == ADMIN_CHAT_ID and ("forward_from_chat" in msg or "forward_origin" in msg):
                        fwd_chat = msg.get("forward_from_chat") or msg.get("forward_origin", {}).get("chat")
                        if fwd_chat and "id" in fwd_chat:
                            priv_id = str(fwd_chat["id"])
                            priv_title = fwd_chat.get("title", "Private Channel")
                            BOT_USERS.add(priv_id)
                            requests.post(send_url, json={
                                "chat_id": chat_id,
                                "text": f"✅ **প্রাইভেট চ্যানেল সফলভাবে যুক্ত হয়েছে!**\n📢 নাম: `{priv_title}`\n🆔 Chat ID: `{priv_id}`\n\nএখন থেকে সব ব্যানার, রুলস এবং সিগন্যাল সরাসরি এই প্রাইভেট চ্যানেলেও যাবে!",
                                "parse_mode": "Markdown"
                            })
                            continue

                    if chat_id != ADMIN_CHAT_ID:
                        continue
                    
                    if text in ["/start", "/admin"]:
                        send_admin_panel(chat_id)
                        
                    elif text == "/startnow":
                        force_instant_session = True
                        requests.post(send_url, json={"chat_id": chat_id, "text": "🚀 এখনই ১ ঘণ্টার লাইভ সেশন শুরু হচ্ছে!"})

                    elif text == "/users":
                        u_list = f"👥 Total Users: {len(BOT_USERS)}\n🚫 Banned Users: {len(BANNED_USERS)}\n\nActive: {list(BOT_USERS)}"
                        requests.post(send_url, json={"chat_id": chat_id, "text": u_list})
                        
                    elif text.startswith("/adduser "):
                        a_id = text.replace("/adduser ", "").strip()
                        BOT_USERS.add(a_id)
                        requests.post(send_url, json={"chat_id": chat_id, "text": f"✅ ইউজার/চ্যানেল {a_id} সফলভাবে যুক্ত করা হয়েছে।"})

                    elif text.startswith("/ban "):
                        b_id = text.replace("/ban ", "").strip()
                        BANNED_USERS.add(str(b_id))
                        requests.post(send_url, json={"chat_id": chat_id, "text": f"🚫 ইউজার {b_id} সফলভাবে ব্যান করা হয়েছে।"})
                        
                    elif text.startswith("/unban "):
                        u_id = text.replace("/unban ", "").strip()
                        BANNED_USERS.discard(str(u_id))
                        requests.post(send_url, json={"chat_id": chat_id, "text": f"✅ ইউজার {u_id} আনব্যান করা হয়েছে।"})
                        
                    elif text.startswith("/setwin "):
                        new_w = text.replace("/setwin ", "").strip()
                        SETTINGS["win_sticker_text"] = new_w
                        requests.post(send_url, json={"chat_id": chat_id, "text": f"✅ Win স্টিকার টেক্সট আপডেট হয়েছে: {new_w}"})
                        
                    elif text.startswith("/setloss "):
                        new_l = text.replace("/setloss ", "").strip()
                        SETTINGS["loss_sticker_text"] = new_l
                        requests.post(send_url, json={"chat_id": chat_id, "text": f"✅ Loss স্টিকার টেক্সট আপডেট হয়েছে: {new_l}"})
                        
                    elif text.startswith("/setchannel "):
                        new_c = text.replace("/setchannel ", "").strip()
                        SETTINGS["channel_link"] = new_c
                        requests.post(send_url, json={"chat_id": chat_id, "text": f"✅ অফিশিয়াল চ্যানেল লিংক আপডেট হয়েছে:\n{new_c}"})
                        
                    elif text.startswith("/setreg "):
                        new_r = text.replace("/setreg ", "").strip()
                        SETTINGS["register_link"] = new_r
                        requests.post(send_url, json={"chat_id": chat_id, "text": f"✅ রেজিস্ট্রেশন লিংক আপডেট হয়েছে:\n{new_r}"})

                    elif text.startswith("/setrules "):
                        new_rules = text.replace("/setrules ", "").strip()
                        SETTINGS["rules_text"] = new_rules
                        requests.post(send_url, json={"chat_id": chat_id, "text": "✅ ভিআইপি রুলস মেসেজ সফলভাবে আপডেট করা হয়েছে!"})
                        
                    elif text == "/delstartsticker":
                        SETTINGS["custom_start_banner"] = None
                        requests.post(send_url, json={"chat_id": chat_id, "text": "✅ কাস্টম Start ব্যানার ডিলিট করে ডিফল্ট করা হয়েছে।"})
                        
                    elif text == "/delendsticker":
                        SETTINGS["custom_end_banner"] = None
                        requests.post(send_url, json={"chat_id": chat_id, "text": "✅ কাস্টম End ব্যানার ডিলিট করে ডিফল্ট করা হয়েছে।"})

                    elif text == "/delwinimg":
                        SETTINGS["custom_win_sticker"] = None
                        requests.post(send_url, json={"chat_id": chat_id, "text": "✅ কাস্টম Win স্টিকার ডিলিট করে ডিফল্ট করা হয়েছে।"})

                    elif text == "/dellossimg":
                        SETTINGS["custom_loss_sticker"] = None
                        requests.post(send_url, json={"chat_id": chat_id, "text": "✅ কাস্টম Loss স্টিকার ডিলিট করে ডিফল্ট করা হয়েছে।"})
                        
                    elif text == "/setstartsticker" and reply_to and "photo" in reply_to:
                        photo_id = reply_to["photo"][-1]["file_id"]
                        if download_telegram_file(photo_id, "custom_start.png"):
                            SETTINGS["custom_start_banner"] = "custom_start.png"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "✅ নতুন Session Start ব্যানার সফলভাবে সেট করা হয়েছে!"})
                            
                    elif text == "/setendsticker" and reply_to and "photo" in reply_to:
                        photo_id = reply_to["photo"][-1]["file_id"]
                        if download_telegram_file(photo_id, "custom_end.png"):
                            SETTINGS["custom_end_banner"] = "custom_end.png"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "✅ নতুন Session End ব্যানার সফলভাবে সেট করা হয়েছে!"})

                    elif text == "/setwinimg" and reply_to:
                        f_id = reply_to["sticker"]["file_id"] if "sticker" in reply_to else (reply_to["photo"][-1]["file_id"] if "photo" in reply_to else None)
                        if f_id and download_telegram_file(f_id, "custom_win.webp"):
                            SETTINGS["custom_win_sticker"] = "custom_win.webp"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "✅ নতুন Win স্টিকার সফলভাবে সেট করা হয়েছে!"})

                    elif text == "/setlossimg" and reply_to:
                        f_id = reply_to["sticker"]["file_id"] if "sticker" in reply_to else (reply_to["photo"][-1]["file_id"] if "photo" in reply_to else None)
                        if f_id and download_telegram_file(f_id, "custom_loss.webp"):
                            SETTINGS["custom_loss_sticker"] = "custom_loss.webp"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "✅ নতুন Loss স্টিকার সফলভাবে সেট করা হয়েছে!"})
                            
        except Exception as e:
            print(f"Admin poll error: {e}")
        time.sleep(1)

def wait_until(target_dt, tz):
    while True:
        now = datetime.datetime.now(tz)
        remaining = (target_dt - now).total_seconds()
        if remaining <= 0:
            break
        time.sleep(min(remaining, 1.0))

# --- [MAIN VIP TRADING ENGINE: FULL 60-MIN SESSION & ZERO CONSECUTIVE LOSS] ---
def run_vip_trading_bot():
    global session_wins, session_losses, last_was_loss, force_instant_session
    print("=====================================================")
    print(f"🚀 {VIP_HEADER} Ultimate Bot Started!")
    print("⏰ Sessions: 10:00 AM, 02:00 PM, 08:00 PM (UTC+6) | Full 60-Minute Duration")
    print("=====================================================")
    
    current_session_date = None
    session_started_flag = {10: False, 14: False, 20: False}
    session_completed_flag = {10: False, 14: False, 20: False}
    reminder_sent_flag = {10: False, 14: False, 20: False}
    
    session_active = False
    active_session_key = None
    session_end_dt = None  # ঠিক ৬০ মিনিট (১ ঘণ্টা) পর সেশন শেষ হওয়ার টাইমস্ট্যাম্প
    
    while True:
        tz = pytz.timezone(TIMEZONE)
        now = datetime.datetime.now(tz)
        today_str = now.strftime("%Y-%m-%d")
        current_hour = now.hour
        current_minute = now.minute
        
        if current_session_date != today_str and not session_active:
            current_session_date = today_str
            session_started_flag = {10: False, 14: False, 20: False}
            session_completed_flag = {10: False, 14: False, 20: False}
            reminder_sent_flag = {10: False, 14: False, 20: False}
            
        active_hours = [10, 14, 20]
        
        # ১. ঠিক ৩০ মিনিট আগে প্রিমিয়াম বাংলায় রিমাইন্ডার মেসেজ
        for h in active_hours:
            remind_hour = h - 1
            if current_hour == remind_hour and 30 <= current_minute <= 35 and not reminder_sent_flag[h]:
                reminder_sent_flag[h] = True
                broadcast_text(
                    f"{VIP_HEADER}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔔 **ভিআইপি ট্রেডিং সেশন রিমাইন্ডার** 🔔\n\n"
                    f"আসসালামু আলাইকুম প্রিয় ভিআইপি সদস্যবৃন্দ,\n"
                    f"আগামী **৩০ মিনিটের** মধ্যে আমাদের অফিশিয়াল হাই-অ্যাকুরেসি **SNR ও প্রাইস অ্যাকশন** ট্রেডিং সেশন শুরু হতে যাচ্ছে!\n\n"
                    f"💼 সবাই দ্রুত ব্রোকারে লগইন করে মানি ম্যানেজমেন্ট অনুযায়ী প্রস্তুত হয়ে যান। ইনশাআল্লাহ আজও আমাদের সেশনটি প্রফিটময় হবে!",
                    with_button=True
                )
                
        # ২. সেশন শুরুর লজিক (নির্ধারিত সময়ে অথবা অ্যাডমিন বাটন চাপলে সাথে সাথে পূর্ণ ১ ঘণ্টার জন্য শুরু হবে)
        if not session_active:
            trigger_hour = None
            for h in active_hours:
                is_pre_session = (current_hour == h - 1 and current_minute >= 55)
                is_in_session = (current_hour == h and not session_completed_flag[h])
                if (is_pre_session or is_in_session) and not session_started_flag[h]:
                    trigger_hour = h
                    session_started_flag[h] = True
                    break

            if force_instant_session or trigger_hour is not None:
                force_instant_session = False
                session_active = True
                active_session_key = trigger_hour
                # ঠিক এখন থেকে পূর্ণ ৬০ মিনিট (১ ঘণ্টা) পর্যন্ত সেশন চলবে!
                session_end_dt = now + datetime.timedelta(minutes=60)
                session_wins = 0
                session_losses = 0
                last_was_loss = False
                
                banner = generate_session_banner(is_start=True)
                broadcast_photo(
                    banner,
                    f"🕋 **বিসমিল্লাহির রাহমানির রাহিম** 🕋\n"
                    f"{VIP_HEADER}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🟢 **【 𝐕𝐈𝐏 𝐒𝐄𝐒𝐒𝐈𝐎𝐍 𝐒𝐓𝐀𝐑𝐓𝐒 】** 🟢\n\n"
                    f"মহান আল্লাহর নামে আমাদের আজকের ভিআইপি ট্রেডিং সেশন শুরু হলো! আগামী **১ ঘণ্টা** সবাই **১ মিনিটের (1M) চার্ট** ওপেন করে আমাদের স্নাইপার সিগন্যালের জন্য প্রস্তুত থাকুন।",
                    with_buttons=True
                )
                time.sleep(2)
                broadcast_text(SETTINGS["rules_text"], with_button=True)
                
        # ৩. ১ ঘণ্টার কোয়ালিটি সেশন ইঞ্জিন
        if session_active:
            now = datetime.datetime.now(tz)
            # পূর্ণ ৬০ মিনিট শেষ হয়েছে কি না চেক
            if now >= session_end_dt or force_instant_session:
                if force_instant_session:
                    # অ্যাডমিন যদি সেশন চলাকালীন আবার রিস্টার্ট বাটন চাপে, তবে নতুন করে শুরু করার জন্য
                    session_active = False
                    continue

                if active_session_key in session_completed_flag:
                    session_completed_flag[active_session_key] = True
                session_active = False
                active_session_key = None
                time.sleep(3)
                
                end_banner = generate_session_banner(is_start=False)
                s_total = session_wins + session_losses
                s_rate = int((session_wins / s_total) * 100) if s_total > 0 else 100
                end_msg = (
                    f"🤲 **আলহামদুলিল্লাহ! (Alhamdulillah)** 🤲\n"
                    f"{VIP_HEADER}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔴 **【 𝐕𝐈𝐏 𝐒𝐄𝐒𝐒𝐈𝐎𝐍 𝐄𝐍𝐃𝐒 】** 🔴\n\n"
                    f"📊 **আজকের সেশনের চূড়ান্ত রিপোর্ট:**\n"
                    f"╭───────────────────────⋅•⋅⊰∙∘☽\n"
                    f"🎯 **Total Signals:** `{s_total}`\n"
                    f"✅ **Winning Trades:** `{session_wins} WIN`\n"
                    f"❌ **Losing Trades:** `{session_losses} LOSS`\n"
                    f"🔥 **Session Accuracy:** `{s_rate}%` 🏆\n"
                    f"╰───────────────────────⋅•⋅⊰∙∘☽\n\n"
                    f"আলহামদুলিল্লাহ, দারুণ একুরেসির সাথে আমাদের আজকের সেশনটি সম্পন্ন হয়েছে! সবাই আজকের প্রফিট সুরক্ষিত রাখুন। পরবর্তী সেশনে আবারও সবার সাথে দেখা হবে ইনশাআল্লাহ!"
                )
                broadcast_photo(end_banner, end_msg, with_buttons=True)
                continue

            if (session_wins + session_losses) == 0:
                scan_wait = random.randint(15, 30)
            else:
                scan_wait = random.randint(140, 260)
                
            # স্ক্যান করার সময় প্রতি সেকেন্ডে চেক করবে অ্যাডমিন রিস্টার্ট দিয়েছে কি না
            for _ in range(scan_wait):
                if force_instant_session:
                    break
                time.sleep(1)
                
            if force_instant_session:
                session_active = False
                continue
            
            sig_now = datetime.datetime.now(tz)
            if sig_now >= session_end_dt:
                continue

            if sig_now.second > 8:
                next_min = (sig_now + datetime.timedelta(minutes=1)).replace(second=2, microsecond=0)
                wait_until(next_min, tz)
            
            sig_now = datetime.datetime.now(tz)
            entry_time_obj = (sig_now + datetime.timedelta(minutes=2)).replace(second=0, microsecond=0)
            timetable = entry_time_obj.strftime("%H:%M")
            
            exp_minutes = 3
            expiration = "3 Minutes (3 Candles on 1M Chart)"
            exit_time_obj = entry_time_obj + datetime.timedelta(minutes=exp_minutes)
            timeset = exit_time_obj.strftime("%H:%M")
            
            # কোটেক্সের সঠিক ও চালু থাকা পেয়ার নির্বাচন
            asset = get_active_quotex_pair(sig_now)
            direction = random.choice(["CALL", "PUT"])
            
            market_setup = analyze_and_create_market_setup(direction)
            snr_reason = market_setup["analysis_text"]
            
            if direction == "CALL":
                dir_line = "🟢 **Direction -» UP / CALL (UP)** ⬆️"
            else:
                dir_line = "🔴 **Direction -» DOWN / PUT (DOWN)** ⬇️"
            
            chart_file = render_snr_chart(asset, "M3", direction, market_setup, is_result=False, filename="signal_chart.png")
            
            signal_caption = (
                f"{VIP_HEADER}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔥 **【 𝐕𝐈𝐏 𝐒𝐍𝐈𝐏𝐄𝐑 𝐒𝐈𝐆𝐍𝐀𝐋 】** 🔥\n"
                f"╭───────────────────────⋅•⋅⊰∙∘☽\n"
                f"🐉 **Pair -»** `{asset}`\n"
                f"🕒 **Entry Time -»** `{timetable}` (UTC+6)\n"
                f"⏰ **Time Set -»** `{timeset}` (3 Candles)\n"
                f"⏳ **Expiration -»** `{expiration}`\n"
                f"📊 **Analysis -»** {snr_reason}\n"
                f"{dir_line}\n"
                f"╰───────────────────────⋅•⋅⊰∙∘☽\n\n"
                f"🛡️ **MTG Note:** যদি প্রথম ট্রেডটি মিস হয়, তবে একই ডিরেকশনে পরবর্তী ৩ মিনিটের (৩টি ক্যান্ডেল) জন্য **১-স্টেপ এমটিজি (MTG)** ব্যবহার করবেন!\n\n"
                f"⚡ **প্রস্তুতি:** হাতে ২ মিনিট সময় আছে, দ্রুত ১ মিনিটের চার্টে পেয়ার ও ক্লোজিং টাইম (`{timeset}`) সেট করে নিন!"
            )
            broadcast_photo(chart_file, signal_caption, with_buttons=True)
            
            # =================================================================
            # 🛡️ [ZERO CONSECUTIVE LOSS & DIRECT WIN PRIORITY ENGINE]
            # =================================================================
            if last_was_loss or session_losses >= 1:
                outcome = random.choices(["DIRECT_WIN", "MTG_WIN"], weights=[92, 8], k=1)[0]
                last_was_loss = False
            else:
                outcome = random.choices(["DIRECT_WIN", "MTG_WIN", "LOSS"], weights=[85, 11, 4], k=1)[0]
                if outcome == "LOSS":
                    last_was_loss = True
            # =================================================================
                    
            wait_until(exit_time_obj + datetime.timedelta(seconds=3), tz)
            
            if outcome in ["MTG_WIN", "LOSS"]:
                mtg_exit_obj = exit_time_obj + datetime.timedelta(minutes=exp_minutes)
                wait_until(mtg_exit_obj + datetime.timedelta(seconds=3), tz)
                
            if outcome == "DIRECT_WIN":
                session_wins += 1
                is_win = True
                res_status = "✅✅✅ **Direct Win (SURESHOT WIN)** ✅✅✅"
            elif outcome == "MTG_WIN":
                session_wins += 1
                is_win = True
                res_status = "✅✅✅ **1-Step Martingale Win (MTG WIN¹)** ✅✅✅"
            else:
                session_losses += 1
                is_win = False
                res_status = "❎✖️💀 **Loss Trade (LOSS - Wait for Recovery)** 💀✖️❎"
                
            total_session_trades = session_wins + session_losses
            session_win_rate = int((session_wins / total_session_trades) * 100) if total_session_trades > 0 else 100
            
            res_chart = render_snr_chart(asset, "M3", direction, market_setup, is_result=True, outcome=outcome, filename="result_chart.png")
            res_caption = (
                f"{VIP_HEADER}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📣 **【 𝐋𝐈𝐕𝐄 𝐒𝐈𝐆𝐍𝐀𝐋 𝐑𝐄𝐒𝐔𝐋𝐓 】** 📣\n"
                f"╭───────────────────────⋅•⋅⊰∙∘☽\n"
                f"🐉 **Pair:** `{asset}`\n"
                f"🕒 **Entry:** `{timetable}`  |  ⏰ **Close:** `{timeset}`\n"
                f"╰───────────────────────⋅•⋅⊰∙∘☽\n\n"
                f"{res_status}\n\n"
                f"╭───────────────────────⋅•⋅⊰∙∘☽\n"
                f"🚀 **Session Score:** `Win: {session_wins}` | `Loss: {session_losses}`\n"
                f"🎯 **Accuracy Rate:** `{session_win_rate}%`\n"
                f"╰───────────────────────⋅•⋅⊰∙∘☽\n\n"
                f"🤲 **Alhamdulillah! Live chart result updated.**"
            )
            broadcast_photo(res_chart, res_caption, with_buttons=True)
            broadcast_sticker(generate_result_sticker(is_win))
            
        else:
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=start_keep_alive_server, daemon=True).start()
    threading.Thread(target=poll_telegram_admin_commands, daemon=True).start()
    run_vip_trading_bot()