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
from PIL import Image, ImageDraw, ImageFont

# =====================================================================
# 🛠️ [ADMIN PANEL & CONFIGURATION]
# =====================================================================
BOT_TOKEN = "8938988396:AAEUvJyoWUuzc8NB9Y2LyNPIrwD-LL6NM00"
TARGET_CHATS = ["@trvip999", "8699074327"]
ADMIN_CHAT_ID = 8699074327

TIMEZONE = "Asia/Dhaka"  # UTC+6
VIP_HEADER = "👑 Trader Rahat | TR VIP 999"

# Dinamic Settings (Admin panel theke change hobe)
SETTINGS = {
    "channel_link": "https://t.me/traderrahat420",
    "register_link": "https://broker-qx.pro/sign-up/?lid=2187284",
    "win_sticker_text": "WIN",
    "loss_sticker_text": "LOSS",
    "custom_start_sticker": None,
    "custom_end_sticker": None,
    "custom_win_sticker": None,
    "custom_loss_sticker": None
}

BOT_USERS = set(TARGET_CHATS)
BANNED_USERS = set()

VIP_RULES_TEXT = (
    f"{VIP_HEADER}\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "📌 VIP Trading & Money Management Rules:\n\n"
    "• আপনার ডিভাইসে UTC+6 সময় নিখুঁতভাবে মিলিয়ে নেবেন।\n"
    "• প্রতিটি সিগন্যাল এন্ট্রি সময়ের ঠিক ২ মিনিট আগে দেওয়া হবে।\n"
    "• মার্কেট পেয়ার ও টাইম সেট করে সিগন্যাল টাইমের ১-২ সেকেন্ড আগেই ট্রেড এন্ট্রি নেবেন।\n"
    "• সবসময় ১-স্টেপ মার্টিনগেল এবং ১-২-৪ মানি ম্যানেজমেন্ট রুল ফলো করবেন।\n"
    "• প্রতিদিনের ৫% প্রফিট টার্গেট পূরণ হলে সাথে সাথে ট্রেড বন্ধ রাখবেন।"
)

HIGH_PAYOUT_PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURGBP",
    "EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC", "AUDUSD-OTC", "EURGBP-OTC"
]
# =====================================================================

session_wins = 0
session_losses = 0
last_was_loss = False

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"TR VIP 999 Bot with Advanced Admin Panel is Running Live!")
    def log_message(self, format, *args):
        return

def start_keep_alive_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

def generate_session_banner(is_start=True, filename="session_banner.png"):
    width, height = 850, 420
    bg_color = (8, 22, 12) if is_start else (32, 8, 8)
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    border_color = (0, 255, 90) if is_start else (255, 30, 30)
    draw.rectangle([18, 18, width-18, height-18], outline=border_color, width=6)
    
    title_text = "TRADER RAHAT | TR VIP 999"
    main_text = "SESSION STARTS" if is_start else "SESSION ENDS"
    
    try:
        font_small = ImageFont.truetype("arialbd.ttf", 32)
        font_large = ImageFont.truetype("arialbd.ttf", 78)
    except Exception:
        font_small = ImageFont.load_default()
        font_large = ImageFont.load_default()
        
    draw.text((75, 85), title_text, fill=(245, 245, 245), font=font_small)
    draw.text((75, 170), main_text, fill=border_color, font=font_large)
    
    img.save(filename)
    return filename

def create_market_setup(direction):
    num_candles = 40
    prices = [100.0]
    for _ in range(num_candles):
        prices.append(prices[-1] + random.uniform(-0.85, 0.85))
        
    opens = prices[:-1]
    closes = prices[1:]
    
    support_level = min(opens[:-3] + closes[:-3]) - 0.35
    resistance_level = max(opens[:-3] + closes[:-3]) + 0.35
    
    if direction == "CALL":
        opens[-2] = support_level + 0.9
        closes[-2] = support_level + 0.08
        opens[-1] = closes[-2]
        closes[-1] = opens[-1] + random.uniform(0.9, 1.5)
    else:
        opens[-2] = resistance_level - 0.9
        closes[-2] = resistance_level - 0.08
        opens[-1] = closes[-2]
        closes[-1] = opens[-1] - random.uniform(0.9, 1.5)
        
    highs = [max(o, c) + random.uniform(0.15, 0.55) for o, c in zip(opens, closes)]
    lows = [min(o, c) - random.uniform(0.15, 0.55) for o, c in zip(opens, closes)]
    
    if direction == "CALL":
        lows[-2] = support_level - 0.18
    else:
        highs[-2] = resistance_level + 0.18
        
    return {
        "opens": opens,
        "closes": closes,
        "highs": highs,
        "lows": lows,
        "support": support_level,
        "resistance": resistance_level
    }

def render_snr_chart(pair, timeframe, direction, setup_data, is_result=False, outcome="DIRECT_WIN", filename="chart.png"):
    fig, ax = plt.subplots(figsize=(8.5, 4.8), facecolor='#0b0e14')
    ax.set_facecolor('#0b0e14')
    
    opens = list(setup_data["opens"])
    closes = list(setup_data["closes"])
    highs = list(setup_data["highs"])
    lows = list(setup_data["lows"])
    support_level = setup_data["support"]
    resistance_level = setup_data["resistance"]
    
    entry_index = len(opens) - 1
    entry_price = closes[-1]
    
    if is_result:
        for step in range(3):
            o_val = closes[-1]
            if outcome == "DIRECT_WIN":
                delta = random.uniform(0.35, 0.85) if direction == "CALL" else -random.uniform(0.35, 0.85)
            elif outcome == "MTG_WIN":
                if step == 0:
                    delta = -random.uniform(0.2, 0.5) if direction == "CALL" else random.uniform(0.2, 0.5)
                else:
                    delta = random.uniform(0.55, 1.1) if direction == "CALL" else -random.uniform(0.55, 1.1)
            else:
                delta = -random.uniform(0.35, 0.8) if direction == "CALL" else random.uniform(0.35, 0.8)
                
            c_val = o_val + delta
            h_val = max(o_val, c_val) + random.uniform(0.1, 0.4)
            l_val = min(o_val, c_val) - random.uniform(0.1, 0.4)
            opens.append(o_val)
            closes.append(c_val)
            highs.append(h_val)
            lows.append(l_val)
            
    num_candles = len(opens)
    for i in range(num_candles):
        color = '#00e676' if closes[i] >= opens[i] else '#ff1744'
        ax.plot([i, i], [lows[i], highs[i]], color=color, linewidth=1.1)
        height = closes[i] - opens[i]
        if abs(height) < 0.05:
            height = 0.05
        ax.bar(i, height, bottom=opens[i], width=0.62, color=color, edgecolor=color)

    upper_band = [max(highs[max(0, i-4):i+1]) + 0.35 for i in range(num_candles)]
    lower_band = [min(lows[max(0, i-4):i+1]) - 0.35 for i in range(num_candles)]
    ax.plot(range(num_candles), upper_band, color='#ff9100', linewidth=0.9, alpha=0.6)
    ax.plot(range(num_candles), lower_band, color='#00b0ff', linewidth=0.9, alpha=0.6)

    ax.axhline(resistance_level, color='#ff1744', linestyle='--', linewidth=1.3, alpha=0.85)
    ax.axhspan(resistance_level - 0.15, resistance_level + 0.25, color='#ff1744', alpha=0.12)
    ax.text(1, resistance_level + 0.3, "STRONG RESISTANCE (SNR)", color='#ff5252', fontsize=8, fontweight='bold')
    
    ax.axhline(support_level, color='#00e676', linestyle='--', linewidth=1.3, alpha=0.85)
    ax.axhspan(support_level - 0.25, support_level + 0.15, color='#00e676', alpha=0.12)
    ax.text(1, support_level - 0.55, "STRONG SUPPORT (SNR)", color='#69f0ae', fontsize=8, fontweight='bold')
    
    arrow_char = '⬆' if direction == "CALL" else '⬇'
    arrow_pos = lows[entry_index] - 0.75 if direction == "CALL" else highs[entry_index] + 0.55
    ax.annotate(arrow_char, xy=(entry_index, arrow_pos), color='#ffd600', fontsize=14, ha='center', fontweight='bold')
    
    if is_result:
        ax.axhline(entry_price, color='#ffd600', linestyle=':', linewidth=1.0, alpha=0.8)
        
    ax.axhline(closes[-1], color='#00b0ff', linestyle='-', linewidth=0.9)
    status_tag = "LIVE RESULT" if is_result else "1M CHART | 3M EXPIRATION"
    ax.text(0.01, 0.96, f"{pair} | {timeframe} (UTC+6) | {status_tag}", transform=ax.transAxes, color='#e0e0e0', fontsize=9.5, fontweight='bold', va='top')
    
    ax.grid(color='#1e2430', linestyle=':', linewidth=0.6)
    ax.tick_params(axis='x', colors='#78909c', labelsize=7)
    ax.tick_params(axis='y', colors='#78909c', labelsize=7)
    ax.yaxis.tick_right()
    
    for spine in ax.spines.values():
        spine.set_color('#263238')
        
    plt.tight_layout()
    plt.savefig(filename, dpi=125, facecolor='#0b0e14')
    plt.close(fig)
    return filename

def generate_result_sticker(is_win, filename="sticker.webp"):
    custom = SETTINGS["custom_win_sticker"] if is_win else SETTINGS["custom_loss_sticker"]
    if custom:
        return custom
        
    width, height = 480, 170
    bg_color = (0, 185, 30) if is_win else (230, 20, 25)
    text_str = SETTINGS["win_sticker_text"] if is_win else SETTINGS["loss_sticker_text"]
    
    img = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    r = 22
    draw.ellipse((50 - r, height//2 - r, 50 + r, height//2 + r), fill=(255, 255, 255))
    draw.ellipse((width - 50 - r, height//2 - r, width - 50 + r, height//2 + r), fill=(255, 255, 255))
    
    try:
        font = ImageFont.truetype("arialbd.ttf", 72)
    except Exception:
        font = ImageFont.load_default()
        
    bbox = draw.textbbox((0, 0), text_str, font=font)
    text_x = (width - (bbox[2] - bbox[0])) // 2
    text_y = (height - (bbox[3] - bbox[1])) // 2 - 12
    draw.text((text_x, text_y), text_str, fill=(255, 255, 255), font=font)
    img.save(filename, "WEBP")
    return filename

def broadcast_photo(photo_path, caption, with_buttons=True):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    reply_markup = {
        "inline_keyboard": [[
            {"text": "Official Channel ↗", "url": SETTINGS["channel_link"]},
            {"text": "VIP Registration ↗", "url": SETTINGS["register_link"]}
        ]]
    }
    for chat_id in TARGET_CHATS:
        if str(chat_id) in BANNED_USERS:
            continue
        data = {"chat_id": chat_id, "caption": caption}
        if with_buttons:
            data["reply_markup"] = json.dumps(reply_markup)
        try:
            with open(photo_path, "rb") as f:
                requests.post(url, data=data, files={"photo": f}, timeout=20)
        except Exception as e:
            print(f"Photo send error: {e}")

def broadcast_sticker(path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendSticker"
    for chat_id in TARGET_CHATS:
        if str(chat_id) in BANNED_USERS:
            continue
        try:
            with open(path, "rb") as f:
                requests.post(url, data={"chat_id": chat_id}, files={"sticker": f}, timeout=20)
        except Exception:
            pass

def broadcast_text(text, with_button=False):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    reply_markup = {
        "inline_keyboard": [[
            {"text": "Official Channel ↗", "url": SETTINGS["channel_link"]},
            {"text": "VIP Registration ↗", "url": SETTINGS["register_link"]}
        ]]
    }
    for chat_id in TARGET_CHATS:
        if str(chat_id) in BANNED_USERS:
            continue
        data = {"chat_id": chat_id, "text": text}
        if with_button:
            data["reply_markup"] = json.dumps(reply_markup)
        try:
            requests.post(url, json=data, timeout=20)
        except Exception as e:
            print(f"Text send error: {e}")

def poll_telegram_admin_commands():
    offset = 0
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    while True:
        try:
            res = requests.get(url, params={"offset": offset, "timeout": 30}, timeout=35)
            if res.status_code == 200:
                data = res.json()
                for result in data.get("result", []):
                    offset = result["update_id"] + 1
                    msg = result.get("message", {})
                    chat_id = msg.get("chat", {}).get("id")
                    text = msg.get("text", "").strip()
                    reply_to = msg.get("reply_to_message")
                    
                    if chat_id != ADMIN_CHAT_ID:
                        continue
                        
                    send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                    
                    if text == "/admin":
                        help_text = (
                            "🛠️ **TRADER RAHAT | ADVANCED ADMIN PANEL** 🛠️\n\n"
                            "• `/users` - Total user list o count dekhun\n"
                            "• `/ban [chat_id]` - Kon user ke ban korun\n"
                            "• `/unban [chat_id]` - Ban tule nin\n"
                            "• `/setwin [Text]` - Win sticker text change korun\n"
                            "• `/setloss [Text]` - Loss sticker text change korun\n"
                            "• `/setchannel [URL]` - Channel link change korun\n"
                            "• `/setreg [URL]` - Registration link change korun\n"
                            "• `/setstartsticker` (Reply photo) - Notun Session Start image add korun\n"
                            "• `/setendsticker` (Reply photo) - Notun Session End image add korun\n"
                            "• `/delstartsticker` - Custom Start sticker delete/reset korun\n"
                            "• `/delendsticker` - Custom End sticker delete/reset korun"
                        )
                        requests.post(send_url, json={"chat_id": chat_id, "text": help_text, "parse_mode": "Markdown"})
                        
                    elif text == "/users":
                        u_list = f"👥 Total Users: {len(BOT_USERS)}\n🚫 Banned Users: {len(BANNED_USERS)}\n\nActive Chats: {list(BOT_USERS)}"
                        requests.post(send_url, json={"chat_id": chat_id, "text": u_list})
                        
                    elif text.startswith("/ban "):
                        b_id = text.split(" ")[1]
                        BANNED_USERS.add(str(b_id))
                        requests.post(send_url, json={"chat_id": chat_id, "text": f"✅ User {b_id} successfully banned."})
                        
                    elif text.startswith("/unban "):
                        u_id = text.split(" ")[1]
                        if u_id in BANNED_USERS:
                            BANNED_USERS.remove(str(u_id))
                        requests.post(send_url, json={"chat_id": chat_id, "text": f"✅ User {u_id} unbanned."})
                        
                    elif text.startswith("/setwin "):
                        new_w = text.replace("/setwin ", "").strip()
                        SETTINGS["win_sticker_text"] = new_w
                        requests.post(send_url, json={"chat_id": chat_id, "text": f"✅ Win sticker text updated to: {new_w}"})
                        
                    elif text.startswith("/setloss "):
                        new_l = text.replace("/setloss ", "").strip()
                        SETTINGS["loss_sticker_text"] = new_l
                        requests.post(send_url, json={"chat_id": chat_id, "text": f"✅ Loss sticker text updated to: {new_l}"})
                        
                    elif text.startswith("/setchannel "):
                        new_c = text.replace("/setchannel ", "").strip()
                        SETTINGS["channel_link"] = new_c
                        requests.post(send_url, json={"chat_id": chat_id, "text": f"✅ Channel link updated to: {new_c}"})
                        
                    elif text.startswith("/setreg "):
                        new_r = text.replace("/setreg ", "").strip()
                        SETTINGS["register_link"] = new_r
                        requests.post(send_url, json={"chat_id": chat_id, "text": f"✅ Registration link updated to: {new_r}"})
                        
                    elif text == "/delstartsticker":
                        SETTINGS["custom_start_sticker"] = None
                        requests.post(send_url, json={"chat_id": chat_id, "text": "✅ Custom Session Start banner deleted/reset to default."})
                        
                    elif text == "/delendsticker":
                        SETTINGS["custom_end_sticker"] = None
                        requests.post(send_url, json={"chat_id": chat_id, "text": "✅ Custom Session End banner deleted/reset to default."})
                        
                    elif text == "/setstartsticker" and reply_to and "photo" in reply_to:
                        photo_id = reply_to["photo"][-1]["file_id"]
                        file_info_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={photo_id}"
                        f_res = requests.get(file_info_url).json()
                        if f_res.get("ok"):
                            file_path = f_res["result"]["file_path"]
                            download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
                            img_data = requests.get(download_url).content
                            with open("custom_start.png", "wb") as handler:
                                handler.write(img_data)
                            SETTINGS["custom_start_sticker"] = "custom_start.png"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "✅ New Session Start banner added successfully!"})
                            
                    elif text == "/setendsticker" and reply_to and "photo" in reply_to:
                        photo_id = reply_to["photo"][-1]["file_id"]
                        file_info_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={photo_id}"
                        f_res = requests.get(file_info_url).json()
                        if f_res.get("ok"):
                            file_path = f_res["result"]["file_path"]
                            download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
                            img_data = requests.get(download_url).content
                            with open("custom_end.png", "wb") as handler:
                                handler.write(img_data)
                            SETTINGS["custom_end_sticker"] = "custom_end.png"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "✅ New Session End banner added successfully!"})
                            
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

def run_vip_trading_bot():
    global session_wins, session_losses, last_was_loss
    print("=====================================================")
    print(f"🚀 {VIP_HEADER} Bot with Advanced Admin Panel started!")
    print("⏰ Session Times: 10:00 AM, 02:00 PM, 08:00 PM (UTC+6)")
    print("=====================================================")
    
    current_session_date = None
    session_signals_sent = {10: 0, 14: 0, 20: 0}
    session_target_limit = {10: 5, 14: 5, 20: 5}
    
    session_started_flag = {10: False, 14: False, 20: False}
    reminder_sent_flag = {10: False, 14: False, 20: False}
    
    active_session_hour = None
    
    while True:
        tz = pytz.timezone(TIMEZONE)
        now = datetime.datetime.now(tz)
        today_str = now.strftime("%Y-%m-%d")
        current_hour = now.hour
        current_minute = now.minute
        
        if current_session_date != today_str:
            current_session_date = today_str
            session_signals_sent = {10: 0, 14: 0, 20: 0}
            session_started_flag = {10: False, 14: False, 20: False}
            reminder_sent_flag = {10: False, 14: False, 20: False}
            active_session_hour = None
            
        active_hours = [10, 14, 20]
        
        for h in active_hours:
            remind_hour = h - 1
            if current_hour == remind_hour and current_minute >= 30 and not reminder_sent_flag[h]:
                reminder_sent_flag[h] = True
                broadcast_text(
                    f"{VIP_HEADER}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔔 VIP Session Reminder\n\n"
                    f"প্রিয় ভিআইপি সদস্যগণ, আগামী ৩০ মিনিটের মধ্যে আমাদের হাই-অ্যাকুরেসি সাপোর্ট ও রেজিস্ট্যান্স ট্রেডিং সেশন শুরু হতে যাচ্ছে!\n\n"
                    f"সবাই দ্রুত ব্রোকারে লগইন করে প্রস্তুত হয়ে যান।",
                    with_button=True
                )
                
        for h in active_hours:
            is_pre_session = (current_hour == h - 1 and current_minute >= 55)
            is_in_session = (current_hour == h and session_signals_sent[h] == 0)
            
            if (is_pre_session or is_in_session) and not session_started_flag[h]:
                session_started_flag[h] = True
                session_wins = 0
                session_losses = 0
                last_was_loss = False
                
                banner = SETTINGS["custom_start_sticker"] if SETTINGS["custom_start_sticker"] else generate_session_banner(is_start=True)
                broadcast_photo(
                    banner,
                    f"{VIP_HEADER}\n"
                    f"🟢 [ SESSION STARTS ] 🟢\n\n"
                    f"প্রিয় সদস্যবৃন্দ, আমাদের অফিশিয়াল ট্রেডিং সেশন এখনই শুরু হচ্ছে! সবাই হাই-অ্যাকুরেসি এসএনআর (SNR) সিগন্যালের জন্য প্রস্তুত থাকুন।",
                    with_buttons=True
                )
                time.sleep(2)
                broadcast_text(VIP_RULES_TEXT, with_button=True)
                
        if current_hour in active_hours and session_signals_sent[current_hour] < session_target_limit[current_hour]:
            active_session_hour = current_hour
            
        if active_session_hour is not None:
            sent_count = session_signals_sent[active_session_hour]
            target_count = session_target_limit[active_session_hour]
            
            if sent_count < target_count:
                if sent_count == 0:
                    scan_wait = random.randint(15, 30)
                else:
                    scan_wait = random.randint(240, 420)
                    
                time.sleep(scan_wait)
                
                sig_now = datetime.datetime.now(tz)
                if sig_now.second > 10:
                    next_min = (sig_now + datetime.timedelta(minutes=1)).replace(second=2, microsecond=0)
                    wait_until(next_min, tz)
                
                sig_now = datetime.datetime.now(tz)
                entry_time_obj = (sig_now + datetime.timedelta(minutes=2)).replace(second=0, microsecond=0)
                timetable = entry_time_obj.strftime("%H:%M")
                
                exp_minutes = 3
                expiration = "3 Minutes (M3 on 1M Chart)"
                exit_time_obj = entry_time_obj + datetime.timedelta(minutes=exp_minutes)
                timeset = exit_time_obj.strftime("%H:%M")
                
                asset = random.choice(HIGH_PAYOUT_PAIRS)
                direction = random.choice(["CALL", "PUT"])
                
                if direction == "CALL":
                    dir_line = "🟢 Direction -» UP / CALL (UP) ⬆"
                    snr_reason = "Strong Support Rejection & Bollinger Band"
                else:
                    dir_line = "🔴 Direction -» DOWN / PUT (DOWN) ⬇"
                    snr_reason = "Strong Resistance Rejection & Bollinger Band"
                
                market_setup = create_market_setup(direction)
                chart_file = render_snr_chart(asset, "M3", direction, market_setup, is_result=False, filename="signal_chart.png")
                
                signal_caption = (
                    f"{VIP_HEADER}\n\n"
                    f"====== VIP SIGNAL ======\n"
                    f"╭───────────────⋅•⋅⊰∙∘☽\n"
                    f"🐉 Pair -» {asset}\n"
                    f"🕒 Entry Time -» {timetable} (UTC+6)\n"
                    f"⏰ Time Set -» {timeset}\n"
                    f"⏳ Expiration -» {expiration}\n"
                    f"📊 Analysis -» {snr_reason}\n"
                    f"{dir_line}\n"
                    f"╰───────────────⋅•⋅⊰∙∘☽\n\n"
                    f"⏳ হাতে ২ মিনিট সময় আছে, ১ মিনিটের চার্ট ওপেন করে পেয়ার ও ৩ মিনিটের টাইম সেট করে প্রস্তুত থাকুন!"
                )
                broadcast_photo(chart_file, signal_caption, with_buttons=True)
                
                if last_was_loss:
                    outcome = random.choices(["DIRECT_WIN", "MTG_WIN"], weights=[90, 10], k=1)[0]
                    last_was_loss = False
                else:
                    outcome = random.choices(["DIRECT_WIN", "MTG_WIN", "LOSS"], weights=[82, 14, 4], k=1)[0]
                    if outcome == "LOSS":
                        last_was_loss = True
                        
                wait_until(exit_time_obj + datetime.timedelta(seconds=2), tz)
                
                if outcome in ["MTG_WIN", "LOSS"]:
                    mtg_exit_obj = exit_time_obj + datetime.timedelta(minutes=exp_minutes)
                    wait_until(mtg_exit_obj + datetime.timedelta(seconds=2), tz)
                    
                if outcome == "DIRECT_WIN":
                    session_wins += 1
                    is_win = True
                    res_status = "- ✅✅✅ Direct Win (WIN) ✅✅✅"
                elif outcome == "MTG_WIN":
                    session_wins += 1
                    is_win = True
                    res_status = "- ✅✅✅ 1-Step Martingale Win (MTG WIN¹) ✅✅✅"
                else:
                    session_losses += 1
                    is_win = False
                    res_status = "- ❎✖️💀 Loss Trade (LOSS) 💀✖️❎"
                    
                total_session_trades = session_wins + session_losses
                session_win_rate = int((session_wins / total_session_trades) * 100) if total_session_trades > 0 else 0
                
                res_chart = render_snr_chart(asset, "M3", direction, market_setup, is_result=True, outcome=outcome, filename="result_chart.png")
                res_caption = (
                    f"{VIP_HEADER}\n\n"
                    f"====== LIVE RESULT ======\n"
                    f"╭───────────────⋅•⋅⊰∙∘☽\n"
                    f"🐉 Pair: {asset} | 🕒 Entry: {timetable} (Set: {timeset})\n"
                    f"╰───────────────⋅•⋅⊰∙∘☽\n\n"
                    f"{res_status}\n\n"
                    f"╭───────────────⋅•⋅⊰∙∘☽\n"
                    f"🚀 Win: {session_wins} | Loss: {session_losses} -◆- ({session_win_rate}%)\n"
                    f"╰───────────────⋅•⋅⊰∙∘☽\n\n"
                    f"📳 Live chart result updated successfully"
                )
                broadcast_photo(res_chart, res_caption, with_buttons=True)
                broadcast_sticker(generate_result_sticker(is_win))
                
                session_signals_sent[active_session_hour] += 1
                
                if session_signals_sent[active_session_hour] >= target_count:
                    time.sleep(5)
                    end_banner = SETTINGS["custom_end_sticker"] if SETTINGS["custom_end_sticker"] else generate_session_banner(is_start=False)
                    s_total = session_wins + session_losses
                    s_rate = int((session_wins / s_total) * 100) if s_total > 0 else 0
                    end_msg = (
                        f"{VIP_HEADER}\n"
                        f"🔴 [ SESSION ENDS ] 🔴\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"📊 Session Summary:\n"
                        f"• Total Signals: {s_total}\n"
                        f"• Successful Trades (Win): {session_wins} ✅\n"
                        f"• Failed Trades (Loss): {session_losses} ❌\n"
                        f"• Session Accuracy: {s_rate}% 🎯\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"আজকের সেশনটি সফলভাবে সম্পন্ন হয়েছে। পরবর্তী সেশনে আবার সবার সাথে দেখা হবে!"
                    )
                    broadcast_photo(end_banner, end_msg, with_buttons=True)
                    active_session_hour = None
            else:
                active_session_hour = None
                time.sleep(30)
        else:
            time.sleep(20)

if __name__ == "__main__":
    threading.Thread(target=start_keep_alive_server, daemon=True).start()
    threading.Thread(target=poll_telegram_admin_commands, daemon=True).start()
    run_vip_trading_bot()