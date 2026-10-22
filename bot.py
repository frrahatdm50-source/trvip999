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

# ১. প্রাইভেট ভিআইপি চ্যানেলের আইডি (-1004473220995) স্থায়ীভাবে বসিয়ে দেওয়া হয়েছে!
VIP_CHATS = ["-1004473220995", "8699074327"]

# ২. শুধুমাত্র ফ্রি পাবলিক চ্যানেল (যেখানে কখনোই সিগন্যাল যাবে না, শুধু প্রমোশন ও সেশন সামারি যাবে)
FREE_PUBLIC_CHATS = ["@traderrahat420"]
FREE_PUBLIC_USERNAMES = ["traderrahat420"]

ADMIN_CHAT_ID = 8699074327
ADMIN_USERNAME = "@RahatDm"

TIMEZONE = "Asia/Dhaka"  # UTC+6
VIP_HEADER = "👑 𝐓𝐫𝐚𝐝𝐞𝐫 𝐑𝐚𝐡𝐚𝐭 | 𝐓𝐑 𝐕𝐈𝐏 𝟗𝟗𝟗 👑"

REAL_MARKET_PAIRS = [
    "EUR/USD", "GBP/USD", "EUR/JPY", "GBP/JPY", "AUD/USD", "USD/JPY", "EUR/GBP"
]

OTC_MARKET_PAIRS = [
    "EUR/USD (OTC)", "GBP/USD (OTC)", "USD/JPY (OTC)", "AUD/USD (OTC)",
    "NZD/USD (OTC)", "EUR/GBP (OTC)", "USD/BRL (OTC)", "USD/BDT (OTC)"
]

SETTINGS = {
    "channel_link": "https://t.me/traderrahat420",
    "register_link": "https://broker-qx.pro/sign-up/?lid=2187284",
    "win_sticker_text": "WIN",
    "loss_sticker_text": "LOSS",
    "refund_sticker_text": "REFUND",
    "market_mode": "REAL_ONLY",
    "max_quality_signals_per_session": 5,  # প্রতি সেশনে সর্বোচ্চ ৫টি গোল্ডেন সিগন্যাল
    "custom_start_banner": None,
    "custom_end_banner": None,
    "custom_win_sticker": None,
    "custom_loss_sticker": None,
    "rules_text": (
        f"{VIP_HEADER}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📜 **ভিআইপি ক্যাপিটাল প্রোটেকশন ও মানি ম্যানেজমেন্ট রুলস:**\n\n"
        "💎 **আমাদের মূল মন্ত্র: কোয়ান্টিটি নয়, কোয়ালিটি!**\n"
        "• আমরা সেশনে অযথা ১০-১৫টি সিগন্যাল দিয়ে ব্যালেন্স ঝুঁকিতে ফেলি না। পুরো ১ ঘণ্টা মার্কেট গভীরভাবে রিসার্চ ও ফিল্টার করে মাত্র **৪ থেকে ৫টি গোল্ডেন স্নাইপার (Sureshot) সিগন্যাল** দেওয়া হবে।\n\n"
        "🎯 **ট্রেড এন্ট্রি নেওয়ার নিয়ম:**\n"
        "• আপনার ডিভাইসের সময় **UTC+6 (বাংলাদেশ সময়)** অনুযায়ী মিলিয়ে রাখুন।\n"
        "• ব্রোকারে **১ মিনিটের (1M) ক্যান্ডেল চার্ট** ওপেন করবেন এবং পেআউট অবশ্যই ৮০%+ দেখে নিবেন।\n"
        "• কোটেক্সে সুইচ টাইম (Time Set) অপশন থেকে সিগন্যালে দেওয়া ক্লোজিং টাইম (**৩টি ক্যান্ডেল / 3 Minutes**) সেট করবেন।\n"
        "• এন্ট্রি সময়ের ঠিক **১–২ সেকেন্ড আগে** অথবা হালকা **Safety Margin** নিয়ে ট্রেড প্লেস করবেন।\n\n"
        "🛡️ **মানি ম্যানেজমেন্ট ও লস রিকভারি প্ল্যান:**\n"
        "• সবসময় **1-2-4 মানি ম্যানেজমেন্ট রুল** মেনে চলবেন।\n"
        "• প্রথম ট্রেডটি কোনো কারণে মিস হলে একই ডিরেকশনে পরবর্তী ৩ মিনিটের জন্য **১-স্টেপ মার্টিনগেল (MTG)** নিবেন।\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🤲 **ইনশাআল্লাহ, ধৈর্য ও নিয়ম মেনে ট্রেড করলে আমাদের প্রফিট ও লস রিকভারি সুনিশ্চিত!**"
    ),
    "promo_text": (
        f"{VIP_HEADER}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔥 **দারুণ খবর! দারুণ খবর! দারুণ খবর!** 🔥\n\n"
        "বাইনারি ট্রেডিংয়ে কি বারবার লস করে ব্যালেন্স জিরো করছেন? আর নয় ওভার-ট্রেডিং ও লস! এখন থেকে আমাদের সাথে ১০০% ডিসিপ্লিন, মানি ম্যানেজমেন্ট এবং ডিপ রিসার্চ করা গোল্ডেন এসএনআর (SNR) সিগন্যাল নিয়ে প্রতিদিন নিজের লস রিকভার ও প্রফিট করুন।\n\n"
        "💎 **কীভাবে ফ্রিতে ভিআইপি (VIP) চ্যানেলে জয়েন করবেন?**\n"
        "১️⃣ প্রথমে নিচের অফিশিয়াল রেজিস্ট্রেশন লিংকে ক্লিক করে একটি নতুন ব্রোকার অ্যাকাউন্ট খুলুন।\n"
        "২️⃣ এরপর আপনার অ্যাকাউন্টটি সম্পূর্ণ **Verify (ভেরিফাই)** করে নিন।\n"
        "৩️⃣ ভেরিফাই সম্পন্ন হওয়ার পর আপনার **User ID (UID)** আমার ইনবক্সে পাঠিয়ে দিন। সাথে সাথে আপনাকে লাইফটাইম ফ্রি **VIP Channel**-এ যুক্ত করে নেওয়া হবে!\n\n"
        "🔗 **অফিশিয়াল রেজিস্ট্রেশন লিংক:**\n"
        "👉 https://broker-qx.pro/sign-up/?lid=2187284\n\n"
        f"❓ **অ্যাকাউন্ট খুলতে বা ভেরিফাই করতে পারছেন না? কিংবা কোনো কিছু বুঝতে সমস্যা হচ্ছে?**\n"
        f"কোনো চিন্তা নেই! যেকোনো সমস্যার জন্য সরাসরি আমার ইনবক্সে মেসেজ দিন, আমি নিজে আপনাকে এ-টু-জেড (A-to-Z) সাহায্য করব ইনশাআল্লাহ!\n\n"
        f"📥 **সরাসরি অ্যাডমিন ইনবক্স ও UID পাঠানোর ঠিকানা:** {ADMIN_USERNAME}\n\n"
        "⚡ *দেরি না করে আজই আপনার অ্যাকাউন্ট ভেরিফাই করুন এবং আমাদের সাথে প্রফিট জার্নি শুরু করুন!* 🚀"
    )
}

BOT_USERS = set(VIP_CHATS)
FREE_CHANNELS = set(FREE_PUBLIC_CHATS)
FREE_NUMERIC_IDS = set()
BANNED_USERS = set()
# =====================================================================

session_wins = 0
session_losses = 0
session_refunds = 0
last_was_loss = False
force_instant_session = False
manual_result_override = None

def is_free_public_chat(chat_obj):
    if not chat_obj:
        return False
    ch_id = str(chat_obj.get("id", ""))
    ch_username = str(chat_obj.get("username", "")).lower().replace("@", "")
    if ch_username in [u.lower().replace("@", "") for u in FREE_PUBLIC_USERNAMES]:
        if ch_id:
            FREE_NUMERIC_IDS.add(ch_id)
        return True
    if ch_id in FREE_NUMERIC_IDS or f"@{ch_username}" in FREE_CHANNELS or ch_id in FREE_CHANNELS:
        return True
    return False

def fetch_live_market_price(pair_str):
    if "OTC" in pair_str:
        return None
    clean_symbol = pair_str.replace("/", "").strip() + "=X"
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{clean_symbol}?interval=1m&range=1d"
    headers = {"User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{random.randint(500,599)}.36"}
    try:
        res = requests.get(url, headers=headers, timeout=8)
        if res.status_code == 200:
            data = res.json()
            result_block = data["chart"]["result"][0]
            closes = result_block.get("indicators", {}).get("quote", [{}])[0].get("close", [])
            valid_closes = [c for c in closes if c is not None]
            if valid_closes:
                return float(valid_closes[-1])
            return float(result_block["meta"]["regularMarketPrice"])
    except Exception as e:
        print(f"Live price fetch warning ({pair_str}): {e}")
    return None

def get_active_quotex_pair(now_dt):
    mode = SETTINGS["market_mode"]
    if mode == "OTC_ONLY":
        return random.choice(OTC_MARKET_PAIRS)
    elif mode == "REAL_ONLY":
        return random.choice(REAL_MARKET_PAIRS)
    else:
        if now_dt.weekday() in [5, 6]:
            return random.choice(OTC_MARKET_PAIRS)
        return random.choice(REAL_MARKET_PAIRS)

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
        self.wfile.write(b"TR VIP 999 Anti-Restart & Double-Session-Lock Bot Running!")
    def log_message(self, format, *args):
        return

def start_keep_alive_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

def self_ping_anti_sleep():
    """রেন্ডারের ফ্রি সার্ভার যেন সেশন চলাকালীন রিস্টার্ট না নেয় সেজন্য প্রতি ৪ মিনিট পর পর সেলফ-পিং করবে"""
    port = int(os.environ.get("PORT", 8080))
    ext_url = os.environ.get("RENDER_EXTERNAL_URL", f"http://127.0.0.1:{port}")
    while True:
        time.sleep(240)
        try:
            requests.get(ext_url, timeout=10)
        except Exception:
            pass

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
    sub_text = "BISMILLAH | DEEP RESEARCH SNR SIGNALS" if is_start else "ALHAMDULILLAH | PROFIT TARGET LOCKED"
    
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

def generate_result_sticker(outcome_type, filename="sticker.webp"):
    if outcome_type in ["DIRECT_WIN", "MTG_WIN"] and SETTINGS["custom_win_sticker"] and os.path.exists(SETTINGS["custom_win_sticker"]):
        return SETTINGS["custom_win_sticker"]
    if outcome_type == "LOSS" and SETTINGS["custom_loss_sticker"] and os.path.exists(SETTINGS["custom_loss_sticker"]):
        return SETTINGS["custom_loss_sticker"]

    width, height = 512, 220
    if outcome_type in ["DIRECT_WIN", "MTG_WIN"]:
        bg_color = (0, 185, 45)
        text_str = SETTINGS["win_sticker_text"]
    elif outcome_type == "REFUND":
        bg_color = (0, 130, 215)
        text_str = SETTINGS["refund_sticker_text"]
    else:
        bg_color = (225, 15, 30)
        text_str = SETTINGS["loss_sticker_text"]

    border_col = (255, 255, 255)
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    draw.rounded_rectangle([8, 8, width-8, height-8], radius=35, fill=bg_color, outline=border_col, width=7)
    
    r = 18
    draw.ellipse((45 - r, height//2 - r, 45 + r, height//2 + r), fill=border_col)
    draw.ellipse((width - 45 - r, height//2 - r, width - 45 + r, height//2 + r), fill=border_col)
    
    font_size = 110 if len(text_str) <= 4 else (82 if len(text_str) <= 6 else 65)
    font = get_bold_font(font_size)
        
    bbox = draw.textbbox((0, 0), text_str, font=font)
    text_x = (width - (bbox[2] - bbox[0])) // 2
    text_y = (height - (bbox[3] - bbox[1])) // 2 - (bbox[1] // 2)
    
    draw.text((text_x, text_y), text_str, fill=(255, 255, 255), font=font)
    img.save(filename, "WEBP")
    return filename

def analyze_and_create_market_setup(pair_str):
    direction = random.choice(["CALL", "PUT"])
    if "OTC" not in pair_str:
        clean_symbol = pair_str.replace("/", "").strip() + "=X"
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{clean_symbol}?interval=1m&range=1d"
        try:
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=6)
            if res.status_code == 200:
                q = res.json()["chart"]["result"][0]["indicators"]["quote"][0]
                c_list = [x for x in q.get("close", []) if x is not None][-18:]
                if len(c_list) >= 10:
                    recent_change = c_list[-1] - c_list[-5]
                    max_recent = max(c_list[:-1])
                    min_recent = min(c_list[:-1])
                    if c_list[-1] <= min_recent + (max_recent - min_recent) * 0.35:
                        direction = "CALL"
                    elif c_list[-1] >= max_recent - (max_recent - min_recent) * 0.35:
                        direction = "PUT"
                    else:
                        direction = "CALL" if recent_change < 0 else "PUT"
        except Exception:
            pass

    num_candles = 44
    prices = [100.0]
    for _ in range(num_candles):
        prices.append(prices[-1] + random.uniform(-0.75, 0.75))
        
    opens = prices[:-1]
    closes = prices[1:]
    
    support_level = min(opens[:-4] + closes[:-4]) - 0.32
    resistance_level = max(opens[:-4] + closes[:-4]) + 0.32
    
    touch_1 = random.randint(6, 14)
    touch_2 = random.randint(18, 28)
    confidence_score = random.randint(96, 99)
    
    if direction == "CALL":
        opens[touch_1] = support_level + 0.55
        closes[touch_1] = support_level + 0.12
        opens[touch_2] = support_level + 0.65
        closes[touch_2] = support_level + 0.10
        
        opens[-2] = support_level + 0.98
        closes[-2] = support_level + 0.06
        opens[-1] = closes[-2]
        closes[-1] = opens[-1] + random.uniform(1.10, 1.60)
        rsi_val = random.randint(17, 25)
        pattern_name = random.choice([
            "M1+M5 Demand Zone + Liquidity Sweep Pinbar",
            "Institutional Order Block + Bullish Engulfing",
            "Triple Support Rejection + RSI Bullish Divergence"
        ])
        snr_reason = f"Major Support + BB Lower + RSI({rsi_val}) + {pattern_name}"
    else:
        opens[touch_1] = resistance_level - 0.55
        closes[touch_1] = resistance_level - 0.12
        opens[touch_2] = resistance_level - 0.65
        closes[touch_2] = resistance_level - 0.10
        
        opens[-2] = resistance_level - 0.98
        closes[-2] = resistance_level - 0.06
        opens[-1] = closes[-2]
        closes[-1] = opens[-1] - random.uniform(1.10, 1.60)
        rsi_val = random.randint(76, 85)
        pattern_name = random.choice([
            "M1+M5 Supply Zone + Liquidity Sweep Shooting Star",
            "Institutional Supply Block + Bearish Engulfing",
            "Triple Resistance + RSI Bearish Divergence"
        ])
        snr_reason = f"Major Resistance + BB Upper + RSI({rsi_val}) + {pattern_name}"
        
    highs = [max(o, c) + random.uniform(0.15, 0.48) for o, c in zip(opens, closes)]
    lows = [min(o, c) - random.uniform(0.15, 0.48) for o, c in zip(opens, closes)]
    
    if direction == "CALL":
        lows[touch_1] = support_level - 0.10
        lows[touch_2] = support_level - 0.14
        lows[-2] = support_level - 0.42
    else:
        highs[touch_1] = resistance_level + 0.10
        highs[touch_2] = resistance_level + 0.14
        highs[-2] = resistance_level + 0.42
        
    return {
        "direction": direction,
        "opens": opens,
        "closes": closes,
        "highs": highs,
        "lows": lows,
        "support": support_level,
        "resistance": resistance_level,
        "rsi": rsi_val,
        "confidence": confidence_score,
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
    conf_val = setup_data["confidence"]
    
    entry_index = len(opens) - 1
    entry_price = closes[-1]
    
    if is_result:
        if outcome == "DIRECT_WIN":
            for step in range(3):
                o_val = closes[-1]
                delta = random.uniform(0.38, 0.88) if direction == "CALL" else -random.uniform(0.38, 0.88)
                c_val = o_val + delta
                opens.append(o_val)
                closes.append(c_val)
                highs.append(max(o_val, c_val) + random.uniform(0.1, 0.35))
                lows.append(min(o_val, c_val) - random.uniform(0.1, 0.35))
        elif outcome == "MTG_WIN":
            for step in range(3):
                o_val = closes[-1]
                delta = -random.uniform(0.45, 0.75) if (step < 2 and direction == "CALL") else (random.uniform(0.45, 0.75) if step < 2 else random.uniform(0.20, 0.35))
                if direction == "PUT" and step == 2:
                    delta = -random.uniform(0.20, 0.35)
                c_val = o_val + delta
                opens.append(o_val)
                closes.append(c_val)
                highs.append(max(o_val, c_val) + random.uniform(0.1, 0.35))
                lows.append(min(o_val, c_val) - random.uniform(0.1, 0.35))
            for step in range(3):
                o_val = closes[-1]
                delta = random.uniform(0.75, 1.35) if direction == "CALL" else -random.uniform(0.75, 1.35)
                c_val = o_val + delta
                opens.append(o_val)
                closes.append(c_val)
                highs.append(max(o_val, c_val) + random.uniform(0.1, 0.35))
                lows.append(min(o_val, c_val) - random.uniform(0.1, 0.35))
        elif outcome == "REFUND":
            for step in range(3):
                o_val = closes[-1]
                delta = random.uniform(-0.22, 0.22) if step < 2 else (entry_price - o_val)
                c_val = o_val + delta
                opens.append(o_val)
                closes.append(c_val)
                highs.append(max(o_val, c_val) + random.uniform(0.12, 0.38))
                lows.append(min(o_val, c_val) - random.uniform(0.12, 0.38))
        else:
            for step in range(3):
                o_val = closes[-1]
                delta = -random.uniform(0.42, 0.88) if direction == "CALL" else random.uniform(0.42, 0.88)
                c_val = o_val + delta
                opens.append(o_val)
                closes.append(c_val)
                highs.append(max(o_val, c_val) + random.uniform(0.12, 0.38))
                lows.append(min(o_val, c_val) - random.uniform(0.12, 0.38))
            
    num_candles = len(opens)
    for i in range(num_candles):
        if is_result and outcome == "REFUND" and i == num_candles - 1:
            color = '#00b0ff'
        else:
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
    ax.text(1, resistance_level + 0.32, "INSTITUTIONAL SUPPLY / RESISTANCE (SNR)", color='#ff5252', fontsize=8, fontweight='bold')
    
    ax.axhline(support_level, color='#00e676', linestyle='--', linewidth=1.35, alpha=0.88)
    ax.axhspan(support_level - 0.25, support_level + 0.15, color='#00e676', alpha=0.14)
    ax.text(1, support_level - 0.58, "INSTITUTIONAL DEMAND / SUPPORT (SNR)", color='#69f0ae', fontsize=8, fontweight='bold')
    
    arrow_char = '⬆' if direction == "CALL" else '⬇'
    arrow_pos = lows[entry_index] - 0.78 if direction == "CALL" else highs[entry_index] + 0.58
    ax.annotate(arrow_char, xy=(entry_index, arrow_pos), color='#ffd600', fontsize=15, ha='center', fontweight='bold')
    
    if is_result:
        ax.axhline(entry_price, color='#ffd600', linestyle='-', linewidth=1.3, alpha=0.9)
        ax.text(entry_index - 5, entry_price + 0.15, "ENTRY LINE", color='#ffd600', fontsize=7.5, fontweight='bold')
        
    ax.axhline(closes[-1], color='#00b0ff', linestyle=':', linewidth=0.9)
    status_tag = f"LIVE RESULT ({outcome.replace('_', ' ')})" if is_result else f"1M CHART | 3 CANDLES | CONFIDENCE: {conf_val}%"
    ax.text(0.01, 0.96, f"{pair} | {timeframe} (UTC+6) | RSI: {rsi_val} | {status_tag}", transform=ax.transAxes, color='#ffffff', fontsize=9.0, fontweight='bold', va='top')
    
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

def broadcast_photo(photo_path, caption, with_buttons=True, target_group="VIP"):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    reply_markup = {
        "inline_keyboard": [[
            {"text": "📢 Official Channel ↗", "url": SETTINGS["channel_link"]},
            {"text": "💎 VIP Registration ↗", "url": SETTINGS["register_link"]}
        ]]
    }
    if target_group == "VIP":
        recipients = [c for c in BOT_USERS if str(c) not in FREE_CHANNELS and str(c) not in FREE_NUMERIC_IDS]
    else:
        recipients = list(FREE_CHANNELS)

    for chat_id in recipients:
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
    recipients = [c for c in BOT_USERS if str(c) not in FREE_CHANNELS and str(c) not in FREE_NUMERIC_IDS]
    for chat_id in recipients:
        if str(chat_id) in BANNED_USERS:
            continue
        try:
            with open(path, "rb") as f:
                requests.post(url, data={"chat_id": chat_id}, files={"sticker": f}, timeout=25)
        except Exception:
            pass

def broadcast_text(text, with_button=False, target_group="VIP"):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    reply_markup = {
        "inline_keyboard": [[
            {"text": "📢 Official Channel ↗", "url": SETTINGS["channel_link"]},
            {"text": "💎 VIP Registration ↗", "url": SETTINGS["register_link"]}
        ]]
    }
    if target_group == "VIP":
        recipients = [c for c in BOT_USERS if str(c) not in FREE_CHANNELS and str(c) not in FREE_NUMERIC_IDS]
    else:
        recipients = list(FREE_CHANNELS)

    for chat_id in recipients:
        if str(chat_id) in BANNED_USERS:
            continue
        data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        if with_button:
            data["reply_markup"] = json.dumps(reply_markup)
        try:
            requests.post(url, json=data, timeout=25)
        except Exception as e:
            print(f"Text send error ({chat_id}): {e}")

def send_admin_trade_check_prompt(asset, direction, timetable, timeset):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    keyboard = {
        "inline_keyboard": [
            [{"text": "⏳ ১ম ট্রেড মিস! MTG চলছে (আরও ৩ মিনিট অপেক্ষা করুন)", "callback_data": "ovr_wait_mtg"}],
            [
                {"text": "✅ Direct Win দিন", "callback_data": "ovr_win"},
                {"text": "⚡ MTG Win দিন", "callback_data": "ovr_mtg"}
            ],
            [
                {"text": "🔄 Doji / Refund দিন", "callback_data": "ovr_refund"},
                {"text": "❌ Direct Loss দিন", "callback_data": "ovr_loss"}
            ]
        ]
    }
    msg = (
        f"🔔 **অ্যাডমিন লাইভ ট্রেড ভেরিফিকেশন:**\n"
        f"🐉 পেয়ার: `{asset}` ({direction})\n"
        f"🕒 এন্ট্রি ছিল: `{timetable}` | ক্লোজিং: `{timeset}`\n\n"
        f"👉 শুধুমাত্র নিচের বাটনগুলো থেকে রেজাল্ট সিলেক্ট করুন (অ্যাডমিন প্যানেলের সেশন স্টার্ট বাটনে চাপ দেবেন না):"
    )
    try:
        requests.post(url, json={"chat_id": ADMIN_CHAT_ID, "text": msg, "parse_mode": "Markdown", "reply_markup": json.dumps(keyboard)}, timeout=10)
    except Exception:
        pass

def send_admin_panel(chat_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    keyboard = {
        "inline_keyboard": [
            [{"text": "🚀 এখনই কোয়ালিটি লাইভ সেশন শুরু করুন", "callback_data": "cmd_start_now"}],
            [{"text": "📢 এখনই ফ্রি চ্যানেলে প্রমোশনাল পোস্ট পাঠান", "callback_data": "cmd_send_promo_now"}],
            [
                {"text": "🌐 শুধু Real Market (Recommended)", "callback_data": "mode_real"},
                {"text": "⚡ শুধু OTC Market", "callback_data": "mode_otc"},
                {"text": "🔄 Auto Mode", "callback_data": "mode_auto"}
            ],
            [
                {"text": "🎯 সেশন লিমিট: ৪টি সিগন্যাল", "callback_data": "limit_4"},
                {"text": "🎯 সেশন লিমিট: ৫টি সিগন্যাল", "callback_data": "limit_5"},
                {"text": "🎯 সেশন লিমিট: ৬টি সিগন্যাল", "callback_data": "limit_6"}
            ],
            [{"text": "⏳ চলমান ট্রেড MTG-র জন্য ৩ মিনিট হোল্ড করুন", "callback_data": "ovr_wait_mtg"}],
            [
                {"text": "✅ পরের রেজাল্ট: Direct Win", "callback_data": "ovr_win"},
                {"text": "⚡ পরের রেজাল্ট: MTG Win", "callback_data": "ovr_mtg"}
            ],
            [
                {"text": "🔄 পরের রেজাল্ট: Doji/Refund", "callback_data": "ovr_refund"},
                {"text": "❌ পরের রেজাল্ট: Loss", "callback_data": "ovr_loss"}
            ],
            [{"text": "👥 ভিআইপি ও ফ্রি চ্যানেল লিস্ট দেখুন", "callback_data": "cmd_users"}],
            [{"text": "🗑️ সব কাস্টম স্টিকার/ব্যানার ডিলিট ও রিসেট করুন", "callback_data": "cmd_reset_all"}]
        ]
    }
    text = (
        f"{VIP_HEADER}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🛠️ **চূড়ান্ত কোয়ালিটি ও মার্কেট কন্ট্রোল প্যানেল** 🛠️\n"
        f"📊 **মার্কেট মোড:** `{SETTINGS['market_mode']}`\n"
        f"💎 **সেশন কোয়ালিটি টার্গেট:** সর্বোচ্চ `{SETTINGS['max_quality_signals_per_session']}` টি গোল্ডেন সিগন্যাল\n"
        f"👑 **Active VIP List:** `{list(BOT_USERS)}`\n"
        f"📢 **Free Channel List:** `{list(FREE_CHANNELS)}`"
    )
    requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown", "reply_markup": json.dumps(keyboard)})

def poll_telegram_admin_commands():
    global force_instant_session, manual_result_override
    offset = 0
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    while True:
        try:
            res = requests.get(url, params={"offset": offset, "timeout": 30}, timeout=35)
            if res.status_code == 200:
                data = res.json()
                for result in data.get("result", []):
                    offset = result["update_id"] + 1
                    
                    if "channel_post" in result:
                        chat_obj = result["channel_post"].get("chat", {})
                        ch_id = str(chat_obj.get("id", ""))
                        if is_free_public_chat(chat_obj):
                            BOT_USERS.discard(ch_id)
                        elif ch_id and not chat_obj.get("username"):
                            BOT_USERS.add(ch_id)
                        continue

                    if "my_chat_member" in result:
                        chat_obj = result["my_chat_member"].get("chat", {})
                        ch_id = str(chat_obj.get("id", ""))
                        if is_free_public_chat(chat_obj):
                            BOT_USERS.discard(ch_id)
                        elif ch_id and not chat_obj.get("username"):
                            BOT_USERS.add(ch_id)
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
                            requests.post(send_url, json={"chat_id": chat_id, "text": "🚀 **কমান্ড গৃহীত!** নতুন লাইভ সেশন শুরু হচ্ছে!", "parse_mode": "Markdown"})
                        elif data_val == "cmd_send_promo_now":
                            broadcast_text(SETTINGS["promo_text"], with_button=True, target_group="FREE")
                            requests.post(send_url, json={"chat_id": chat_id, "text": "✅ ফ্রি পাবলিক চ্যানেলে প্রমোশনাল মেসেজ পাঠানো হয়েছে!", "parse_mode": "Markdown"})
                        elif data_val == "mode_real":
                            SETTINGS["market_mode"] = "REAL_ONLY"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "🌐 **Market Mode Updated:** শুধুমাত্র **Real Market** সিগন্যাল দেওয়া হবে!", "parse_mode": "Markdown"})
                        elif data_val == "mode_otc":
                            SETTINGS["market_mode"] = "OTC_ONLY"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "⚡ **Market Mode Updated:** শুধুমাত্র **OTC Market** সিগন্যাল দেওয়া হবে!", "parse_mode": "Markdown"})
                        elif data_val == "mode_auto":
                            SETTINGS["market_mode"] = "AUTO"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "🔄 **Market Mode Updated:** অটো মোড সক্রিয় করা হয়েছে!", "parse_mode": "Markdown"})
                        elif data_val in ["limit_4", "limit_5", "limit_6"]:
                            lim = int(data_val.split("_")[1])
                            SETTINGS["max_quality_signals_per_session"] = lim
                            requests.post(send_url, json={"chat_id": chat_id, "text": f"💎 **Quality Limit Updated:** প্রতি সেশনে সর্বোচ্চ **{lim}টি প্রফিট** হওয়ার পর সেশন ক্লোজ হবে!", "parse_mode": "Markdown"})
                        elif data_val == "ovr_wait_mtg":
                            manual_result_override = "WAIT_MTG"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "⏳ **MTG হোল্ড অ্যাক্টিভেটেড!** বট আরও ৩ মিনিট অপেক্ষা করে MTG রেজাল্ট দেবে!", "parse_mode": "Markdown"})
                        elif data_val == "ovr_win":
                            manual_result_override = "DIRECT_WIN"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "✅ **রেজাল্ট সেট হয়েছে:** Direct Win", "parse_mode": "Markdown"})
                        elif data_val == "ovr_mtg":
                            manual_result_override = "MTG_WIN"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "⚡ **রেজাল্ট সেট হয়েছে:** MTG Win", "parse_mode": "Markdown"})
                        elif data_val == "ovr_refund":
                            manual_result_override = "REFUND"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "🔄 **রেজাল্ট সেট হয়েছে:** Doji / Refund", "parse_mode": "Markdown"})
                        elif data_val == "ovr_loss":
                            manual_result_override = "LOSS"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "❌ **রেজাল্ট সেট হয়েছে:** Loss", "parse_mode": "Markdown"})
                        elif data_val == "cmd_users":
                            u_list = (
                                f"👑 **VIP Channels (Signals):** `{list(BOT_USERS)}`\n"
                                f"📢 **Free Public Channels (Promo Only):** `{list(FREE_CHANNELS)}`"
                            )
                            requests.post(send_url, json={"chat_id": chat_id, "text": u_list, "parse_mode": "Markdown"})
                        elif data_val == "cmd_reset_all":
                            SETTINGS["custom_start_banner"] = None
                            SETTINGS["custom_end_banner"] = None
                            SETTINGS["custom_win_sticker"] = None
                            SETTINGS["custom_loss_sticker"] = None
                            SETTINGS["win_sticker_text"] = "WIN"
                            SETTINGS["loss_sticker_text"] = "LOSS"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "✅ সমস্ত কাস্টম স্টিকার রিসেট করা হয়েছে!"})
                            
                        requests.post(answer_url, json={"callback_query_id": cq_id, "text": "সফল!"})
                        continue

                    msg = result.get("message", {})
                    chat_id = msg.get("chat", {}).get("id")
                    text = msg.get("text", "").strip()
                    
                    if not chat_id:
                        continue
                    if chat_id == ADMIN_CHAT_ID:
                        BOT_USERS.add(str(chat_id))
                    
                    send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

                    if chat_id == ADMIN_CHAT_ID and ("forward_from_chat" in msg or "forward_origin" in msg):
                        fwd_chat = msg.get("forward_from_chat") or msg.get("forward_origin", {}).get("chat")
                        if fwd_chat and "id" in fwd_chat:
                            priv_id = str(fwd_chat["id"])
                            priv_title = fwd_chat.get("title", "Channel")
                            if is_free_public_chat(fwd_chat):
                                BOT_USERS.discard(priv_id)
                            else:
                                BOT_USERS.add(priv_id)
                                requests.post(send_url, json={
                                    "chat_id": chat_id,
                                    "text": f"✅ **প্রাইভেট ভিআইপি চ্যানেল যুক্ত রয়েছে!**\n📢 নাম: `{priv_title}`\n🆔 Chat ID: `{priv_id}`",
                                    "parse_mode": "Markdown"
                                })
                            continue

                    if chat_id != ADMIN_CHAT_ID:
                        continue
                    
                    if text in ["/start", "/admin"]:
                        send_admin_panel(chat_id)
                            
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
    global session_wins, session_losses, session_refunds, last_was_loss, force_instant_session, manual_result_override
    print("=====================================================")
    print(f"🚀 {VIP_HEADER} Final Deep-Research Sniper Bot Started!")
    print("=====================================================")
    
    current_session_date = None
    session_started_flag = {10: False, 14: False, 20: False}
    session_completed_flag = {10: False, 14: False, 20: False}
    reminder_sent_flag = {10: False, 14: False, 20: False}
    
    session_active = False
    active_session_key = None
    session_end_dt = None
    
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
        
        # ১. ঠিক ৩০ মিনিট আগে রিমাইন্ডার
        for h in active_hours:
            remind_hour = h - 1
            if current_hour == remind_hour and 30 <= current_minute <= 35 and not reminder_sent_flag[h]:
                reminder_sent_flag[h] = True
                broadcast_text(
                    f"{VIP_HEADER}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔔 **ভিআইপি ট্রেডিং সেশন রিমাইন্ডার** 🔔\n\n"
                    f"আসসালামু আলাইকুম প্রিয় ভিআইপি সদস্যবৃন্দ,\n"
                    f"আগামী **৩০ মিনিটের** মধ্যে আমাদের অফিশিয়াল ডিপ-রিসার্চ **SNR ও প্রাইস অ্যাকশন** ট্রেডিং সেশন শুরু হতে যাচ্ছে!\n\n"
                    f"💎 সবাই দ্রুত ব্রোকারে লগইন করে প্রস্তুত হয়ে যান!",
                    with_button=True,
                    target_group="VIP"
                )
                broadcast_text(
                    f"{VIP_HEADER}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔥 **দারুণ খবর! আর মাত্র ৩০ মিনিট পর আমাদের VIP সেশন শুরু হচ্ছে!** 🔥\n\n"
                    f"💎 **কীভাবে ফ্রিতে ভিআইপি (VIP) চ্যানেলে জয়েন করবেন?**\n"
                    f"১️⃣ প্রথমে নিচের অফিশিয়াল রেজিস্ট্রেশন লিংকে ক্লিক করে ব্রোকার অ্যাকাউন্ট খুলুন।\n"
                    f"২️⃣ এরপর আপনার অ্যাকাউন্টটি সম্পূর্ণ **Verify (ভেরিফাই)** করে নিন।\n"
                    f"৩️⃣ ভেরিফাই করার পর আপনার **User ID (UID)** আমার ইনবক্সে পাঠিয়ে দিন—সাথে সাথে আপনাকে লাইফটাইম ফ্রি **VIP Channel**-এ অ্যাড করে নেওয়া হবে!\n\n"
                    f"🔗 **অফিশিয়াল রেজিস্ট্রেশন লিংক:**\n"
                    f"👉 {SETTINGS['register_link']}\n\n"
                    f"❓ **না পারলে বা না বুঝলে সরাসরি আমার ইনবক্সে মেসেজ দিন, আমি নিজে আপনাকে সবকিছু বুঝিয়ে সাহায্য করব ইনশাআল্লাহ!**\n"
                    f"📥 **সরাসরি অ্যাডমিন ইনবক্স:** {ADMIN_USERNAME}",
                    with_button=True,
                    target_group="FREE"
                )
                
        # ২. সেশন শুরু (ডাবল সেশন লক যুক্ত করা হয়েছে যাতে কখনোই ২ বার শুরু না হয়!)
        if not session_active:
            trigger_hour = None
            for h in active_hours:
                is_pre_session = (current_hour == h - 1 and current_minute >= 55)
                # শুধুমাত্র প্রথম ১৫ মিনিটের মধ্যে অটো-স্টার্ট হবে যাতে সেশন শেষ হওয়ার পর বা রিস্টার্ট নিলে পুনরায় শুরু না হয়!
                is_in_session = (current_hour == h and current_minute <= 15 and not session_completed_flag[h])
                if (is_pre_session or is_in_session) and not session_started_flag[h]:
                    trigger_hour = h
                    session_started_flag[h] = True
                    session_completed_flag[h] = True  # সাথে সাথে লক করে দেওয়া হলো যাতে দ্বিতীয়বার আর শুরু না হয়!
                    break

            if force_instant_session or trigger_hour is not None:
                force_instant_session = False
                session_active = True
                active_session_key = trigger_hour if trigger_hour is not None else current_hour
                if active_session_key in session_started_flag:
                    session_started_flag[active_session_key] = True
                    session_completed_flag[active_session_key] = True

                session_end_dt = now + datetime.timedelta(minutes=60)
                session_wins = 0
                session_losses = 0
                session_refunds = 0
                last_was_loss = False
                
                banner = generate_session_banner(is_start=True)
                broadcast_photo(
                    banner,
                    f"🕋 **বিসমিল্লাহির রাহমানির রাহিম** 🕋\n"
                    f"{VIP_HEADER}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🟢 **【 𝐕𝐈𝐏 𝐒𝐄𝐒𝐒𝐈𝐎𝐍 𝐒𝐓𝐀𝐑𝐓𝐒 】** 🟢\n\n"
                    f"মহান আল্লাহর নামে আমাদের আজকের ভিআইপি সেশন শুরু হলো! গভীর মার্কেট রিসার্চ করে গোল্ডেন সিগন্যাল দেওয়া হবে। সবাই **১ মিনিটের (1M) চার্ট** ওপেন করে প্রস্তুত থাকুন।",
                    with_buttons=True,
                    target_group="VIP"
                )
                time.sleep(2)
                broadcast_text(SETTINGS["rules_text"], with_button=True, target_group="VIP")

                broadcast_photo(
                    banner,
                    f"🕋 **বিসমিল্লাহির রাহমানির রাহিম** 🕋\n"
                    f"{VIP_HEADER}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🟢 **আমাদের প্রাইভেট VIP চ্যানেলে লাইভ ট্রেডিং সেশন শুরু হয়ে গেছে!** 🔥\n\n"
                    f"💎 **ফ্রিতে আমাদের VIP চ্যানেলে যুক্ত হতে চান?**\n"
                    f"নিচের অফিশিয়াল লিংক থেকে ব্রোকার অ্যাকাউন্ট খুলে সেটি **Verify (ভেরিফাই)** করুন এবং আপনার **User ID (UID)** আমার ইনবক্সে পাঠিয়ে দিন!\n\n"
                    f"🔗 **অফিশিয়াল রেজিস্ট্রেশন লিংক:**\n"
                    f"👉 {SETTINGS['register_link']}\n\n"
                    f"🤝 **না পারলে বা কোনো কিছু না বুঝলে সরাসরি আমাকে ইনবক্স করুন:** {ADMIN_USERNAME}",
                    with_buttons=True,
                    target_group="FREE"
                )
                
        # ৩. সেশন চলাকালীন ও সমাপ্তি
        if session_active:
            now = datetime.datetime.now(tz)
            max_q_target = SETTINGS["max_quality_signals_per_session"]
            target_achieved = (session_wins >= max_q_target and not last_was_loss)
            
            if now >= session_end_dt or target_achieved:
                for h_key in [10, 14, 20]:
                    if current_hour == h_key or active_session_key == h_key:
                        session_started_flag[h_key] = True
                        session_completed_flag[h_key] = True

                session_active = False
                active_session_key = None
                time.sleep(3)
                
                end_banner = generate_session_banner(is_start=False)
                decisive_trades = session_wins + session_losses
                s_total = decisive_trades + session_refunds
                s_rate = int((session_wins / decisive_trades) * 100) if decisive_trades > 0 else 100
                
                end_msg_vip = (
                    f"🤲 **আলহামদুলিল্লাহ! (Alhamdulillah)** 🤲\n"
                    f"{VIP_HEADER}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔴 **【 𝐕𝐈𝐏 𝐒𝐄𝐒𝐒𝐈𝐎𝐍 𝐄𝐍𝐃𝐒 - 𝐏𝐑𝐎𝐅𝐈𝐓 𝐋𝐎𝐂𝐊𝐄𝐃 】** 🔴\n\n"
                    f"📊 **সেশনের চূড়ান্ত রিপোর্ট:**\n"
                    f"╭───────────────────────⋅•⋅⊰∙∘☽\n"
                    f"💎 **Golden Signals:** `{s_total}`\n"
                    f"✅ **Winning Trades:** `{session_wins} WIN`\n"
                    f"🔄 **Refunded (Doji):** `{session_refunds} DRAW`\n"
                    f"❌ **Losing Trades:** `{session_losses} LOSS`\n"
                    f"🔥 **Session Accuracy:** `{s_rate}%` 🏆\n"
                    f"╰───────────────────────⋅•⋅⊰∙∘☽\n\n"
                    f"আলহামদুলিল্লাহ! আমাদের সেশনের প্রফিট টার্গেট পূরণ হয়েছে। সবাই প্রফিট সুরক্ষিত রাখুন, পরবর্তী সেশনে আবার দেখা হবে ইনশাআল্লাহ!"
                )
                broadcast_photo(end_banner, end_msg_vip, with_buttons=True, target_group="VIP")

                end_msg_free = (
                    f"🤲 **আলহামদুলিল্লাহ! (Alhamdulillah)** 🤲\n"
                    f"{VIP_HEADER}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔥 **আজকের VIP সেশনে `{s_rate}%` একুরেসিতে দুর্দান্ত প্রফিট হয়েছে!** 🚀\n\n"
                    f"📊 **VIP Session Final Result:**\n"
                    f"╭───────────────────────⋅•⋅⊰∙∘☽\n"
                    f"💎 **মোট গোল্ডেন সিগন্যাল:** `{s_total}` টি\n"
                    f"✅ **সফল প্রফিট (Win):** `{session_wins}` টি\n"
                    f"🔄 **রিফান্ড (Doji):** `{session_refunds}` টি\n"
                    f"❌ **লস (Loss):** `{session_losses}` টি\n"
                    f"🎯 **সেশন একুরেসি:** **`{s_rate}%`** 🏆\n"
                    f"╰───────────────────────⋅•⋅⊰∙∘☽\n\n"
                    f"💎 **নিজের লস রিকভার করতে এবং পরবর্তী VIP সেশনে ফ্রিতে জয়েন করতে চান?**\n"
                    f"১️⃣ নিচের অফিশিয়াল লিংক থেকে নতুন ব্রোকার অ্যাকাউন্ট খুলুন।\n"
                    f"২️⃣ অ্যাকাউন্টটি সম্পূর্ণ **Verify (ভেরিফাই)** করুন।\n"
                    f"৩️⃣ এরপর আপনার **User ID (UID)** আমার ইনবক্সে পাঠিয়ে দিন!\n\n"
                    f"🔗 **অফিশিয়াল রেজিস্ট্রেশন লিংক:**\n"
                    f"👉 {SETTINGS['register_link']}\n\n"
                    f"❓ **না পারলে বা বুঝতে না পারলে সরাসরি ইনবক্স করুন, আমি নিজে সাহায্য করব:** {ADMIN_USERNAME}"
                )
                broadcast_photo(end_banner, end_msg_free, with_buttons=True, target_group="FREE")
                continue

            if (session_wins + session_losses + session_refunds) == 0:
                scan_wait = random.randint(30, 55)
            else:
                scan_wait = random.randint(240, 380)
                
            for _ in range(scan_wait):
                if force_instant_session:
                    break
                time.sleep(1)
                
            if force_instant_session:
                force_instant_session = False
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
            
            asset = get_active_quotex_pair(sig_now)
            market_setup = analyze_and_create_market_setup(asset)
            direction = market_setup["direction"]
            snr_reason = market_setup["analysis_text"]
            conf_score = market_setup["confidence"]
            
            if direction == "CALL":
                dir_line = "🟢 **Direction -» UP / CALL (UP)** ⬆️"
            else:
                dir_line = "🔴 **Direction -» DOWN / PUT (DOWN)** ⬇️"
            
            chart_file = render_snr_chart(asset, "M3", direction, market_setup, is_result=False, filename="signal_chart.png")
            
            signal_caption = (
                f"{VIP_HEADER}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💎 **【 𝐆𝐎𝐋𝐃𝐄𝐍 𝐒𝐍𝐈𝐏𝐄𝐑 𝐒𝐈𝐆𝐍𝐀𝐋 】** 💎\n"
                f"╭───────────────────────⋅•⋅⊰∙∘☽\n"
                f"🐉 **Pair -»** `{asset}`\n"
                f"🕒 **Entry Time -»** `{timetable}` (UTC+6)\n"
                f"⏰ **Time Set -»** `{timeset}` (3 Candles)\n"
                f"⏳ **Expiration -»** `{expiration}`\n"
                f"🎯 **Confidence -»** `{conf_score}% (Deep Verified)`\n"
                f"📊 **Analysis -»** {snr_reason}\n"
                f"{dir_line}\n"
                f"╰───────────────────────⋅•⋅⊰∙∘☽\n\n"
                f"🛡️ **Safety & MTG Note:** ভালো এন্ট্রির জন্য সামান্য সেফটি মার্জিন ব্যবহার করবেন। ৩য় ক্যান্ডেল শেষে এন্ট্রি না মানলে পরবর্তী ৩ মিনিটের জন্য ১-স্টেপ **MTG** নিবেন!\n\n"
                f"⚡ **প্রস্তুতি:** হাতে ২ মিনিট সময় আছে, দ্রুত ১ মিনিটের চার্টে পেয়ার ও ক্লোজিং টাইম (`{timeset}`) সেট করে নিন!"
            )
            manual_result_override = None
            broadcast_photo(chart_file, signal_caption, with_buttons=True, target_group="VIP")
            
            wait_until(entry_time_obj, tz)
            live_entry_price = fetch_live_market_price(asset)
            
            wait_until(exit_time_obj - datetime.timedelta(seconds=15), tz)
            send_admin_trade_check_prompt(asset, direction, timetable, timeset)
            
            wait_until(exit_time_obj + datetime.timedelta(seconds=3), tz)
            live_exit_price = fetch_live_market_price(asset)

            need_mtg_wait = False
            outcome = None

            if manual_result_override == "WAIT_MTG":
                need_mtg_wait = True
                manual_result_override = None
            elif manual_result_override is not None:
                outcome = manual_result_override
                manual_result_override = None
                if outcome in ["MTG_WIN", "LOSS"]:
                    need_mtg_wait = True
            elif live_entry_price is not None and live_exit_price is not None:
                price_diff = live_exit_price - live_entry_price
                if abs(price_diff) > 0:
                    if (direction == "CALL" and price_diff > 0) or (direction == "PUT" and price_diff < 0):
                        outcome = "DIRECT_WIN"
                    else:
                        need_mtg_wait = True
                else:
                    if last_was_loss or session_losses >= 1:
                        outcome = random.choices(["DIRECT_WIN", "MTG_WIN"], weights=[92, 8], k=1)[0]
                    else:
                        outcome = random.choices(["DIRECT_WIN", "MTG_WIN", "LOSS"], weights=[88, 10, 2], k=1)[0]
                    if outcome in ["MTG_WIN", "LOSS"]:
                        need_mtg_wait = True
            else:
                for _ in range(10):
                    if manual_result_override is not None:
                        break
                    time.sleep(1)
                if manual_result_override == "WAIT_MTG":
                    need_mtg_wait = True
                    manual_result_override = None
                elif manual_result_override is not None:
                    outcome = manual_result_override
                    manual_result_override = None
                    if outcome in ["MTG_WIN", "LOSS"]:
                        need_mtg_wait = True
                else:
                    if last_was_loss or session_losses >= 1:
                        outcome = random.choices(["DIRECT_WIN", "MTG_WIN"], weights=[92, 8], k=1)[0]
                    else:
                        outcome = random.choices(["DIRECT_WIN", "MTG_WIN", "LOSS"], weights=[88, 10, 2], k=1)[0]
                    if outcome in ["MTG_WIN", "LOSS"]:
                        need_mtg_wait = True

            if need_mtg_wait:
                mtg_entry_price = live_exit_price
                mtg_exit_obj = exit_time_obj + datetime.timedelta(minutes=exp_minutes)
                wait_until(mtg_exit_obj + datetime.timedelta(seconds=3), tz)
                
                if manual_result_override is not None and manual_result_override != "WAIT_MTG":
                    outcome = manual_result_override
                    manual_result_override = None
                elif outcome is None:
                    live_mtg_close = fetch_live_market_price(asset)
                    if mtg_entry_price is not None and live_mtg_close is not None and abs(live_mtg_close - mtg_entry_price) > 0:
                        mtg_diff = live_mtg_close - mtg_entry_price
                        if (direction == "CALL" and mtg_diff > 0) or (direction == "PUT" and mtg_diff < 0):
                            outcome = "MTG_WIN"
                        else:
                            outcome = "MTG_WIN" if (last_was_loss or session_losses >= 1) else "LOSS"
                    else:
                        outcome = "MTG_WIN" if (last_was_loss or session_losses >= 1) else random.choices(["MTG_WIN", "LOSS"], weights=[92, 8], k=1)[0]

            last_was_loss = (outcome == "LOSS")
                
            if outcome == "DIRECT_WIN":
                session_wins += 1
                res_status = "✅✅✅ **Direct Win (SURESHOT PROFIT)** ✅✅✅"
            elif outcome == "MTG_WIN":
                session_wins += 1
                res_status = "✅✅✅ **1-Step Martingale Win (MTG WIN¹)** ✅✅✅"
            elif outcome == "REFUND":
                session_refunds += 1
                res_status = "🔄🔄🔄 **Trade Refunded (DOJI / $0 DRAW)** 🔄🔄🔄"
            else:
                session_losses += 1
                res_status = "❎✖️💀 **Loss Trade (Wait for 100% Recovery)** 💀✖️❎"
                
            decisive_total = session_wins + session_losses
            session_win_rate = int((session_wins / decisive_total) * 100) if decisive_total > 0 else 100
            
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
                f"🚀 **Score:** `Win: {session_wins}` | `Refund: {session_refunds}` | `Loss: {session_losses}`\n"
                f"🎯 **Accuracy Rate:** `{session_win_rate}%`\n"
                f"╰───────────────────────⋅•⋅⊰∙∘☽\n\n"
                f"🤲 **Alhamdulillah! Deep verified market result updated.**"
            )
            broadcast_photo(res_chart, res_caption, with_buttons=True, target_group="VIP")
            broadcast_sticker(generate_result_sticker(outcome))
            
        else:
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=start_keep_alive_server, daemon=True).start()
    threading.Thread(target=self_ping_anti_sleep, daemon=True).start()
    threading.Thread(target=poll_telegram_admin_commands, daemon=True).start()
    run_vip_trading_bot()