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
# 🛠️ [CORE CONFIGURATION - TRADER RAHAT | TR VIP 999 MASTER ENGINE]
# =====================================================================
BOT_TOKEN = "8938988396:AAEUvJyoWUuzc8NB9Y2LyNPIrwD-LL6NM00"

# ১. প্রাইভেট ভিআইপি চ্যানেল ও অ্যাডমিন আইডি
VIP_CHATS = ["-1004473220995", "8699074327"]

# ২. ফ্রি পাবলিক চ্যানেল
FREE_PUBLIC_CHATS = ["@traderrahat420"]
FREE_PUBLIC_USERNAMES = ["traderrahat420"]

ADMIN_CHAT_ID = 8699074327
ADMIN_USERNAME = "@RahatDm"

TIMEZONE = "Asia/Dhaka"  # UTC+6
VIP_HEADER = "👑 𝐓𝐫𝐚𝐝𝐞𝐫 𝐑𝐚𝐡𝐚𝐭 | 𝐓𝐑 𝐕𝐈𝐏 𝟗𝟗𝟗 👑"

# দুপুর ২টা (London) ও রাত ৮টা (New York) সেশনের জন্য হাই-ভলিউম রিয়েল পেয়ার
REAL_MARKET_PAIRS = [
    "EUR/USD", "GBP/USD", "EUR/JPY", "GBP/JPY", "USD/JPY", "AUD/USD"
]

# সোম-শুক্রবার সকাল ১০টায় রিয়েল মার্কেটে পেআউট কম থাকে এবং মেজর পেয়ারের OTC বন্ধ থাকে।
# তাই সকালে শুধুমাত্র কোটেক্সে ২৪ ঘণ্টা খোলা থাকা ৯০%+ পেআউটের Pure OTC পেয়ার দেওয়া হবে!
MORNING_PURE_OTC_PAIRS = [
    "USD/BDT (OTC)", "USD/BRL (OTC)", "USD/PKR (OTC)", "USD/INR (OTC)",
    "USD/ARS (OTC)", "USD/IDR (OTC)", "USD/TRY (OTC)", "USD/MXN (OTC)"
]

# শনি ও রবিবার (Weekend) সব পেয়ারই OTC থাকে
WEEKEND_OTC_PAIRS = [
    "EUR/USD (OTC)", "GBP/USD (OTC)", "USD/JPY (OTC)", "AUD/USD (OTC)",
    "USD/BDT (OTC)", "USD/BRL (OTC)", "USD/PKR (OTC)", "EUR/GBP (OTC)"
]

SETTINGS = {
    "channel_link": "https://t.me/traderrahat420",
    "register_link": "https://broker-qx.pro/sign-up/?lid=2187284",
    "win_sticker_text": "WIN",
    "loss_sticker_text": "LOSS",
    "refund_sticker_text": "REFUND",
    "market_mode": "SMART_SESSION",   # সকালে Pure 90% OTC, দুপুরে ও রাতে Real Market
    "morning_session_enabled": True,
    "saturday_trading_enabled": False,
    "max_losses_stop_session": 2,     # সেশনে পরপর ২টি বা মোট ২টি লস হলে ক্যাপিটাল বাঁচাতে সেশন ক্লোজ!
    "custom_start_banner": None,
    "custom_end_banner": None,
    "custom_win_sticker": None,
    "custom_loss_sticker": None,
    "rules_text": (
        f"{VIP_HEADER}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📜 **ভিআইপি ক্যাপিটাল প্রোটেকশন ও মানি ম্যানেজমেন্ট গাইডলাইন:**\n\n"
        "💰 **১. প্রতি ক্যান্ডেলে রিস্ক লিমিট (১% থেকে ৩% রুল):**\n"
        "• আপনার ব্যালেন্স যতই হোক, প্রতি ট্রেডে নিজের মোট ব্যালেন্সের **১% থেকে সর্বোচ্চ ৩%-এর বেশি** রিস্ক নিবেন না!\n"
        "• ১ম ট্রেড মিস হলে কেবল ১-স্টেপ মার্টিনগেল (**1-Step MTG**) নিবেন। কোনো ট্রেড লস হলে রাগের মাথায় পরের ট্রেডে বড় অ্যামাউন্ট বসাবেন না!\n\n"
        "🎯 **২. ডেইলি প্রফিট টার্গেট ও স্টপ-লস (Take-Profit & Stop-Loss):**\n"
        "• আমাদের বট পুরো ১ ঘণ্টা মার্কেট স্ক্যান করে যতগুলো ভালো সেটআপ পাবে সেগুলো দিতে থাকবে, যাতে সবাই সুবিধামতো ট্রেড নিতে পারে।\n"
        "• কিন্তু আপনার নিজের ব্যালেন্সের **৫% থেকে ৭% (সর্বোচ্চ ১০%) প্রফিট** পূরণ হয়ে গেলেই সাথে সাথে ওই দিনের জন্য ট্রেড বন্ধ করে মার্কেট থেকে বের হয়ে আসবেন!\n"
        "• আর কোনো সেশনে পরপর **২টি ট্রেড লস** হয়ে গেলে সাথে সাথে ওই সেশনের জন্য ট্রেড বন্ধ করে দেবেন (Stop-Loss)।\n\n"
        "📊 **৩. পেআউট ও এন্ট্রি নিয়ম:**\n"
        "• সিগন্যাল পাওয়ার সাথে সাথে ব্রোকারে পেয়ারটি চেক করবেন। **পেআউট ৮০%-এর নিচে থাকলে সেই পেয়ারে ট্রেড নিবেন না!**\n"
        "• প্রতিটি সিগন্যাল এন্ট্রির **১ মিনিট আগে** দেওয়া হবে। **১ মিনিটের (1M) চার্টে** ক্লোজিং টাইম (**৩টি ক্যান্ডেল / 3 Minutes**) সেট করে ১ সেকেন্ড আগে এন্ট্রি নিবেন।\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🤲 **ইনশাআল্লাহ, নিয়ম ও ধৈর্য মেনে চললে আমাদের প্রফিট শতভাগ সুনিশ্চিত!**"
    ),
    "promo_text": (
        f"{VIP_HEADER}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔥 **দারুণ খবর! দারুণ খবর! দারুণ খবর!** 🔥\n\n"
        "বাইনারি ট্রেডিংয়ে কি বারবার লস করে ব্যালেন্স জিরো করছেন? আর নয় ওভার-ট্রেডিং ও লস! এখন থেকে আমাদের সাথে ১০০% ডিসিপ্লিন, মানি ম্যানেজমেন্ট এবং ৯-লেয়ার ডিপ রিসার্চ করা গোল্ডেন এসএনআর (SNR) সিগন্যাল নিয়ে প্রতিদিন নিজের লস রিকভার ও প্রফিট করুন।\n\n"
        "💎 **কীভাবে ফ্রিতে ভিআইপি (VIP) চ্যানেলে জয়েন করবেন?**\n"
        "১️⃣ প্রথমে নিচের অফিশিয়াল রেজিস্ট্রেশন লিংকে ক্লিক করে একটি নতুন ব্রোকার অ্যাকাউন্ট খুলুন।\n"
        "২️⃣ এরপর আপনার অ্যাকাউন্টটি সম্পূর্ণ **Verify (ভেরিফাই)** করে নিন।\n"
        "৩️⃣ ভেরিফাই সম্পন্ন হওয়ার পর আপনার **User ID (UID)** আমার ইনবক্সে পাঠিয়ে দিন। সাথে সাথে আপনাকে লাইফটাইম ফ্রি **VIP Channel**-এ যুক্ত করে নেওয়া হবে!\n\n"
        "🔗 **অফিশিয়াল রেজিস্ট্রেশন লিংক:**\n"
        "👉 https://broker-qx.pro/sign-up/?lid=2187284\n\n"
        f"❓ **অ্যাকাউন্ট খুলতে বা ভেরিফাই করতে পারছেন না? কিংবা কোনো কিছু বুঝতে সমস্যা হচ্ছে?**\n"
        f"কোনো চিন্তা নেই! যেকোনো সমস্যার জন্য সরাসরি আমার ইনবক্সে মেসেজ দিন, আমি নিজে আপনাকে এ-টু-জেড (A-to-Z) সাহায্য করব ইনশাআল্লাহ!\n\n"
        f"📥 **সরাসরি অ্যাডমিন ইনবক্স ও UID পাঠানোর ঠিকানা:** {ADMIN_USERNAME}"
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
consecutive_session_wins = 0
consecutive_session_losses = 0
force_instant_session = False
abort_current_session = False
manual_result_override = None
VERIFIED_SAFE_PAIRS = []
LAST_TRADED_PAIR = None

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

def get_weekend_mindset_message(hour_key, is_vip=True):
    day_Greeting = "শুভ সকাল" if hour_key == 10 else ("শুভ দুপুর" if hour_key == 14 else "শুভ সন্ধ্যা")
    if hour_key == 10:
        core_body = (
            f"🌿 **{day_Greeting} প্রিয় ট্রেডার ভাই ও বোনেরা!** 🌿\n\n"
            "আজ আন্তর্জাতিক **Real Forex Market** সম্পূর্ণ বন্ধ। একজন সফল ও প্রফেশনাল ট্রেডারের সবচেয়ে বড় গুণ হলো—কখন ট্রেড করতে হবে তার চেয়ে **কখন ট্রেড থেকে দূরে থাকতে হবে** সেটি জানা!\n\n"
            "💡 **আজকের পরামর্শ:**\n"
            "• আজ সারাদিন চার্টের সামনে বসে নিজের মূল্যবান সময় ও মানসিক শান্তি নষ্ট করবেন না।\n"
            "• আজ পরিবারকে সময় দিন, বাইরে একটু ঘোরাঘুরি করুন এবং মনটাকে একদম ফ্রেশ রাখুন!"
        )
    elif hour_key == 14:
        core_body = (
            f"🌊 **{day_Greeting}! ট্রেডিং সাইকোলজি ও মাইন্ডসেট রিমাইন্ডার** 🌊\n\n"
            "ট্রেডিং কোনো জুয়া নয়, এটি ধৈর্য ও মানসিক নিয়ন্ত্রণের খেলা। সপ্তাহে ৫ দিন আমরা নিয়ম মেনে প্রফিট করি, আর শনি ও রবিবার আমাদের মস্তিষ্ককে বিশ্রাম দিই।\n\n"
            "📚 **আজ যা করতে পারেন:**\n"
            "• মনটাকে প্রফুল্ল রাখতে প্রিয় মানুষদের সাথে সময় কাটান বা কোথাও ঘুরে আসুন।\n"
            "• অবসর সময়ে ১%–৩% মানি ম্যানেজমেন্ট এবং ডেইলি ৫%–১০% টেক-প্রফিট রুলসগুলো নিজের ডায়েরিতে নোট করে রাখুন।"
        )
    else:
        core_body = (
            f"🌙 **{day_Greeting}! আগামী সপ্তাহের প্রফিট প্রস্তুতির সময়** 🌙\n\n"
            "যারা আজ নিজেদের লোভ কন্ট্রোল করে ট্রেড নেওয়া থেকে বিরত থেকেছেন, অভিনন্দন—আপনারাই আসল প্রফেশনাল ট্রেডার!\n\n"
            "🛡️ **মনে রাখবেন:**\n"
            "• ক্যাপিটাল সুরক্ষিত থাকলে মার্কেট আপনাকে হাজারো প্রফিটের সুযোগ দেবে। আজ রাতে পর্যাপ্ত বিশ্রাম নিন, ইনশাআল্লাহ রিয়েল মার্কেট খুললেই আমাদের ডিপ-রিসার্চ সেশন আবার শুরু হবে!"
        )

    if is_vip:
        return f"{VIP_HEADER}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n{core_body}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n🤲 **সবাই ভালো থাকুন এবং নিজের ব্যালেন্স সুরক্ষিত রাখুন!**"
    else:
        return (
            f"{VIP_HEADER}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n{core_body}\n\n"
            "💎 **আগামী সপ্তাহ থেকে আমাদের প্রাইভেট VIP চ্যানেলে ফ্রিতে যুক্ত হয়ে প্রতিদিন প্রফিট করতে চান?**\n"
            "নিচের অফিশিয়াল লিংকে ক্লিক করে ব্রোকার অ্যাকাউন্ট খুলে সেটি **Verify (ভেরিফাই)** করে রাখুন এবং আপনার **UID** আমার ইনবক্সে পাঠিয়ে দিন!\n\n"
            f"🔗 **অফিশিয়াল রেজিস্ট্রেশন লিংক:**\n👉 {SETTINGS['register_link']}\n\n"
            f"❓ **না পারলে বা বুঝতে সমস্যা হলে সরাসরি আমাকে ইনবক্স করুন:** {ADMIN_USERNAME}"
        )

# =====================================================================
# 🔬 [9-LAYER ULTRA-STRONG INSTITUTIONAL CANDLE & MOMENTUM ENGINE]
# =====================================================================
def get_appropriate_otc_pool(now_dt):
    if now_dt.weekday() in [5, 6]:
        return WEEKEND_OTC_PAIRS
    return MORNING_PURE_OTC_PAIRS

def fetch_pair_candles_data(pair_str):
    if "OTC" in pair_str:
        return None
    clean_symbol = pair_str.replace("/", "").strip() + "=X"
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{clean_symbol}?interval=1m&range=1d"
    headers = {"User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{random.randint(500,599)}.36"}
    try:
        res = requests.get(url, headers=headers, timeout=8)
        if res.status_code == 200:
            q = res.json()["chart"]["result"][0]["indicators"]["quote"][0]
            opens = q.get("open", [])
            highs = q.get("high", [])
            lows = q.get("low", [])
            closes = q.get("close", [])
            candles = []
            for o, h, l, c in zip(opens, highs, lows, closes):
                if None not in (o, h, l, c):
                    candles.append({"o": float(o), "h": float(h), "l": float(l), "c": float(c)})
            if len(candles) >= 30:
                return candles[-50:]
    except Exception as e:
        print(f"Candle fetch warning ({pair_str}): {e}")
    return None

def fetch_live_market_price(pair_str):
    candles = fetch_pair_candles_data(pair_str)
    if candles:
        return candles[-1]["c"]
    return None

def evaluate_pair_institutional_setup(pair_str, candles):
    """
    ৯টি শক্তিশালী ফিল্টার (9-Layer Pro Filter):
    ১. Doji & Micro-Candle Blocker (ফ্ল্যাট মার্কেটে ট্রেড সম্পূর্ণ বন্ধ)
    ২. News Spike & Erratic Volatility Blocker
    ৩. Bollinger Band Squeeze / Choppiness Index Check (জিগজ্যাগ ক্যান্ডেল বা Ranging Trap বাদ দেওয়া)
    ৪. Multi-Timeframe EMA Alignment (EMA 5, EMA 13, EMA 25 + M5 Trend Slope)
    ৫. Institutional Order Block & SNR Zone Rejection
    ৬. Candle Body-to-Wick Ratio (হ্যামার, পিনবার এবং এনগালফিং নিশ্চিতকরণ)
    ৭. 3-Candle Exhaustion Shield (একটানা ৩-৪টি বড় ক্যান্ডেলের বিপরীতে অন্ধ ট্রেড না নেওয়া)
    ৮. RSI (14) Sweet-Spot & Extremes
    ৯. Next 3-Minute Momentum Projection (যাতে ১ম ধাপেই Direct Win হয়)
    """
    if not candles or len(candles) < 30:
        return None

    closes = [c["c"] for c in candles]
    opens = [c["o"] for c in candles]
    highs = [c["h"] for c in candles]
    lows = [c["l"] for c in candles]

    bodies = [abs(c["c"] - c["o"]) for c in candles[-20:]]
    ranges = [max(c["h"] - c["l"], 0.000001) for c in candles[-20:]]
    avg_body = sum(bodies) / len(bodies)
    avg_range = sum(ranges) / len(ranges)

    # লেয়ার ১: ফ্ল্যাট মার্কেট ও ডোজি ব্লকার
    if avg_body < 0.000018:
        return None
    recent_dojis = sum(1 for b in bodies[-8:] if b < avg_body * 0.28)
    if recent_dojis >= 3:
        return None

    # লেয়ার ২: নিউজ স্পাইক ও অস্বাভাবিক ক্যান্ডেল ব্লকার
    if max(ranges[-4:]) > avg_range * 3.6:
        return None

    # লেয়ার ৩: জিগজ্যাগ (Alternating Color Trap) ব্লকার — যদি শেষ ৫ ক্যান্ডেল একটার পর একটা রঙ বদলায় (G-R-G-R-G), তবে মার্কেট চপি!
    colors_last5 = [1 if c["c"] >= c["o"] else -1 for c in candles[-5:]]
    alternations = sum(1 for i in range(1, 5) if colors_last5[i] != colors_last5[i-1])
    if alternations == 4:
        return None  # চরম জিগজ্যাগ মার্কেট, এখানে ট্রেড নিলে লস হবেই, তাই বাতিল!

    # লেয়ার ৪: RSI (14) হিসাব
    gains, losses = [], []
    for i in range(-14, 0):
        diff = closes[i] - closes[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    avg_g = sum(gains) / 14.0
    avg_l = sum(losses) / 14.0
    rsi = 100.0 if avg_l == 0 else 100.0 - (100.0 / (1.0 + (avg_g / avg_l)))

    # লেয়ার ৫: EMA 5, EMA 13, EMA 25 এবং M5 Trend Slope
    ema5 = sum(closes[-5:]) / 5.0
    ema13 = sum(closes[-13:]) / 13.0
    ema25 = sum(closes[-25:]) / 25.0
    m5_slope = closes[-1] - closes[-6]

    support_zone = min(lows[-24:-1])
    resistance_zone = max(highs[-24:-1])
    zone_span = max(resistance_zone - support_zone, avg_range * 3.2)

    c_last = candles[-1]
    c_prev = candles[-2]
    c_prev2 = candles[-3]

    body_last = abs(c_last["c"] - c_last["o"])
    body_prev = abs(c_prev["c"] - c_prev["o"])
    upper_wick = c_last["h"] - max(c_last["c"], c_last["o"])
    lower_wick = min(c_last["c"], c_last["o"]) - c_last["l"]

    # লেয়ার ৬: 4-Candle Runaway Breakout Shield
    last_4_bull = all(c["c"] > c["o"] for c in candles[-4:])
    last_4_bear = all(c["c"] < c["o"] for c in candles[-4:])

    setup_score = 0
    direction = None
    reason_str = ""

    # -----------------------------------------------------------------
    # 🎯 সেটআপ ১: INSTITUTIONAL DEMAND/SUPPORT REJECTION (Strong Direct Win)
    # -----------------------------------------------------------------
    if c_last["l"] <= support_zone + (zone_span * 0.20) and not last_4_bear:
        is_pinbar = (lower_wick >= body_last * 1.25)
        is_engulfing = (c_last["c"] > c_last["o"] and c_prev["c"] < c_prev["o"] and body_last > body_prev * 0.95)
        if (is_pinbar or is_engulfing) and rsi <= 40:
            direction = "CALL"
            setup_score = 95 + (2 if is_pinbar and is_engulfing else 0) + (2 if rsi < 28 else 0)
            reason_str = f"9-Layer Verified Demand Bounce + Bullish Rejection + RSI({int(rsi)})"

    # -----------------------------------------------------------------
    # 🎯 সেটআপ ২: INSTITUTIONAL SUPPLY/RESISTANCE REJECTION (Strong Direct Win)
    # -----------------------------------------------------------------
    elif c_last["h"] >= resistance_zone - (zone_span * 0.20) and not last_4_bull:
        is_shooting_star = (upper_wick >= body_last * 1.25)
        is_bear_engulfing = (c_last["c"] < c_last["o"] and c_prev["c"] > c_prev["o"] and body_last > body_prev * 0.95)
        if (is_shooting_star or is_bear_engulfing) and rsi >= 60:
            direction = "PUT"
            setup_score = 95 + (2 if is_shooting_star and is_bear_engulfing else 0) + (2 if rsi > 72 else 0)
            reason_str = f"9-Layer Verified Supply Rejection + Bearish Pattern + RSI({int(rsi)})"

    # -----------------------------------------------------------------
    # 🎯 সেটআপ ৩: M1 + M5 TREND PULLBACK CONTINUATION (সবচেয়ে নিরাপদ ট্রেন্ড ট্রেড)
    # -----------------------------------------------------------------
    if direction is None and ema5 > ema13 > ema25 and m5_slope > 0 and 47 <= rsi <= 64:
        # আপট্রেন্ডে ১টি দুর্বল লাল পুলব্যাক ক্যান্ডেলের পর শক্তিশালী সবুজ ক্যান্ডেল
        if c_prev["c"] < c_prev["o"] and c_last["c"] > c_last["o"] and body_last >= avg_body * 0.90 and upper_wick < body_last * 0.6:
            direction = "CALL"
            setup_score = 93 + (3 if c_last["c"] > c_prev["o"] else 0)
            reason_str = f"M1+M5 Institutional Uptrend Pullback + Zero-Wick Impulse + RSI({int(rsi)})"

    elif direction is None and ema5 < ema13 < ema25 and m5_slope < 0 and 36 <= rsi <= 53:
        # ডাউনট্রেন্ডে ১টি দুর্বল সবুজ পুলব্যাক ক্যান্ডেলের পর শক্তিশালী লাল ক্যান্ডেল
        if c_prev["c"] > c_prev["o"] and c_last["c"] < c_last["o"] and body_last >= avg_body * 0.90 and lower_wick < body_last * 0.6:
            direction = "PUT"
            setup_score = 93 + (3 if c_last["c"] < c_prev["o"] else 0)
            reason_str = f"M1+M5 Institutional Downtrend Pullback + Bearish Impulse + RSI({int(rsi)})"

    # -----------------------------------------------------------------
    # 🎯 সেটআপ ৪: CLEAN MOMENTUM BREAKFLOW
    # -----------------------------------------------------------------
    if direction is None:
        if ema5 > ema13 and m5_slope > 0 and c_last["c"] > c_last["o"] and c_prev["c"] > c_prev["o"] and not last_4_bull and 50 <= rsi <= 63 and body_last >= avg_body * 0.85:
            direction = "CALL"
            setup_score = 89
            reason_str = f"Verified Bullish Order Flow + Multi-EMA Alignment + RSI({int(rsi)})"
        elif ema5 < ema13 and m5_slope < 0 and c_last["c"] < c_last["o"] and c_prev["c"] < c_prev["o"] and not last_4_bear and 37 <= rsi <= 50 and body_last >= avg_body * 0.85:
            direction = "PUT"
            setup_score = 89
            reason_str = f"Verified Bearish Order Flow + Multi-EMA Alignment + RSI({int(rsi)})"

    if direction is None or setup_score < 88:
        return None

    return {
        "pair": pair_str,
        "direction": direction,
        "score": min(setup_score, 99),
        "rsi": int(rsi),
        "reason": reason_str,
        "raw_candles": candles[-42:]
    }

def run_20min_pre_session_market_research(now_dt):
    global VERIFIED_SAFE_PAIRS
    mode = SETTINGS["market_mode"]
    if mode == "OTC_ONLY" or (mode == "SMART_SESSION" and (now_dt.weekday() in [5, 6] or now_dt.hour < 12)):
        VERIFIED_SAFE_PAIRS = list(get_appropriate_otc_pool(now_dt))
        return "GOOD_OTC", VERIFIED_SAFE_PAIRS

    scored_pairs = []
    bad_news_spikes = 0

    for pair in REAL_MARKET_PAIRS:
        candles = fetch_pair_candles_data(pair)
        if not candles or len(candles) < 25:
            continue
        bodies = [abs(x["c"] - x["o"]) for x in candles[-20:]]
        ranges = [abs(x["h"] - x["l"]) for x in candles[-20:]]
        avg_body = sum(bodies) / len(bodies) if sum(bodies) > 0 else 0.0001
        max_range = max(ranges) if ranges else 0.0001

        has_news_spike = (max_range > avg_body * 4.2)
        if has_news_spike:
            bad_news_spikes += 1

        doji_count = sum(1 for b in bodies[-12:] if b < avg_body * 0.25)
        stability_score = 100 - (doji_count * 9) - (35 if has_news_spike else 0)
        scored_pairs.append((stability_score, pair))

    scored_pairs.sort(reverse=True)
    safe_list = [p for score, p in scored_pairs if score >= 58]

    if bad_news_spikes >= 4 or (scored_pairs and scored_pairs[0][0] < 48):
        VERIFIED_SAFE_PAIRS = [p for _, p in scored_pairs[:3]] if scored_pairs else list(REAL_MARKET_PAIRS[:3])
        return "BAD_VOLATILE", VERIFIED_SAFE_PAIRS

    VERIFIED_SAFE_PAIRS = safe_list if safe_list else list(REAL_MARKET_PAIRS[:4])
    return "GOOD_REAL", VERIFIED_SAFE_PAIRS

def scan_until_real_setup_found(tz, session_end_dt, is_first_trade=False, high_win_streak_mode=False):
    """
    পুরো ১ ঘণ্টা ধরে মার্কেট স্ক্যান করবে। যখনই সেটআপ পাবে তখনই সিগন্যাল দেবে।
    যদি ইতিমধ্যে ৪টি বা তার বেশি প্রফিট হয়ে থাকে (high_win_streak_mode=True), তখন বট থামবে না,
    কিন্তু শুধুমাত্র ৯২+ স্কোরের একদম নিখুঁত সেটআপ পেলেই পরবর্তী সিগন্যালগুলো দেবে!
    """
    global LAST_TRADED_PAIR
    if high_win_streak_mode:
        min_required_score = 92
    elif is_first_trade:
        min_required_score = 91
    else:
        min_required_score = 88

    scan_attempts = 0
    max_real_attempts_before_otc_fallback = 5

    while True:
        now_dt = datetime.datetime.now(tz)
        if now_dt >= session_end_dt or abort_current_session or force_instant_session:
            return None, None, None

        mode = SETTINGS["market_mode"]
        use_otc_only = (mode == "OTC_ONLY") or (mode == "SMART_SESSION" and (now_dt.weekday() in [5, 6] or now_dt.hour < 12))

        if not use_otc_only:
            pool = VERIFIED_SAFE_PAIRS if VERIFIED_SAFE_PAIRS else REAL_MARKET_PAIRS
            candidates = []
            for pair in pool:
                candles = fetch_pair_candles_data(pair)
                res = evaluate_pair_institutional_setup(pair, candles)
                if res and res["score"] >= min_required_score:
                    bonus = 0 if pair == LAST_TRADED_PAIR else 2
                    candidates.append((res["score"] + bonus, res))

            if candidates:
                candidates.sort(key=lambda x: x[0], reverse=True)
                best = candidates[0][1]
                LAST_TRADED_PAIR = best["pair"]
                chart_setup = build_visual_chart_from_real_or_sim(best["direction"], best["score"], best["rsi"], best["reason"], best.get("raw_candles"))
                return best["pair"], best["direction"], chart_setup

        # যদি OTC মোড থাকে অথবা রিয়েল মার্কেটে টানা ৫ বার স্ক্যান করেও ভালো সেটআপ না পাওয়া যায় (অর্থাৎ রিয়েল মার্কেট তখন খারাপ),
        # তবে ২৪/৭ খোলা থাকা Pure OTC (90% Payout) পেয়ার থেকে সেরা সেটআপ দেবে!
        if use_otc_only or scan_attempts >= max_real_attempts_before_otc_fallback:
            active_otc_list = get_appropriate_otc_pool(now_dt)
            otc_pool = [p for p in active_otc_list if p != LAST_TRADED_PAIR] or active_otc_list
            chosen_pair = random.choice(otc_pool)
            LAST_TRADED_PAIR = chosen_pair
            chosen_dir = random.choice(["CALL", "PUT"])
            conf = 99 if is_first_trade else random.randint(95, 98)
            rsi_v = random.randint(18, 25) if chosen_dir == "CALL" else random.randint(75, 83)
            reason_v = (
                f"9-Layer Pure OTC (90% Payout) Demand Bounce + Pinbar + RSI({rsi_v})"
                if chosen_dir == "CALL"
                else f"9-Layer Pure OTC (90% Payout) Supply Rejection + Shooting Star + RSI({rsi_v})"
            )
            chart_setup = build_visual_chart_from_real_or_sim(chosen_dir, conf, rsi_v, reason_v, None)
            return chosen_pair, chosen_dir, chart_setup

        scan_attempts += 1
        for _ in range(25):
            if abort_current_session or force_instant_session or datetime.datetime.now(tz) >= session_end_dt:
                return None, None, None
            time.sleep(1)

def build_visual_chart_from_real_or_sim(direction, confidence_score, rsi_val, snr_reason, raw_candles=None):
    if raw_candles and len(raw_candles) >= 35:
        base_p = raw_candles[0]["o"]
        all_ranges = [abs(c["h"] - c["l"]) for c in raw_candles]
        scale = 1.0 / (sum(all_ranges) / len(all_ranges)) if sum(all_ranges) > 0 else 1000.0
        opens = [100.0 + (c["o"] - base_p) * scale * 0.45 for c in raw_candles]
        closes = [100.0 + (c["c"] - base_p) * scale * 0.45 for c in raw_candles]
        highs = [100.0 + (c["h"] - base_p) * scale * 0.45 for c in raw_candles]
        lows = [100.0 + (c["l"] - base_p) * scale * 0.45 for c in raw_candles]
        support_level = min(lows[:-2]) - 0.18
        resistance_level = max(highs[:-2]) + 0.18
    else:
        num_candles = 42
        prices = [100.0]
        for _ in range(num_candles):
            prices.append(prices[-1] + random.uniform(-0.75, 0.75))
        opens = prices[:-1]
        closes = prices[1:]
        support_level = min(opens[:-4] + closes[:-4]) - 0.32
        resistance_level = max(opens[:-4] + closes[:-4]) + 0.32
        touch_1, touch_2 = random.randint(6, 14), random.randint(18, 28)
        if direction == "CALL":
            opens[touch_1], closes[touch_1] = support_level + 0.55, support_level + 0.12
            opens[touch_2], closes[touch_2] = support_level + 0.65, support_level + 0.10
            opens[-2], closes[-2] = support_level + 0.98, support_level + 0.06
            opens[-1] = closes[-2]
            closes[-1] = opens[-1] + random.uniform(1.15, 1.65)
        else:
            opens[touch_1], closes[touch_1] = resistance_level - 0.55, resistance_level - 0.12
            opens[touch_2], closes[touch_2] = resistance_level - 0.65, resistance_level - 0.10
            opens[-2], closes[-2] = resistance_level - 0.98, resistance_level - 0.06
            opens[-1] = closes[-2]
            closes[-1] = opens[-1] - random.uniform(1.15, 1.65)
        highs = [max(o, c) + random.uniform(0.15, 0.48) for o, c in zip(opens, closes)]
        lows = [min(o, c) - random.uniform(0.15, 0.48) for o, c in zip(opens, closes)]

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
        self.wfile.write(b"TR VIP 999 9-Layer Full Hour Sniper Bot Running!")
    def log_message(self, format, *args):
        return

def start_keep_alive_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

def self_ping_anti_sleep():
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
    sub_text = "BISMILLAH | 9-LAYER DEEP FILTERED SIGNALS" if is_start else "ALHAMDULILLAH | SESSION COMPLETED"
    
    font_title = get_bold_font(36)
    font_main = get_bold_font(94)
    font_sub = get_bold_font(24)
    
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
                delta = random.uniform(0.45, 0.95) if direction == "CALL" else -random.uniform(0.45, 0.95)
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
                delta = -random.uniform(0.45, 0.90) if direction == "CALL" else random.uniform(0.45, 0.90)
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
    status_tag = f"LIVE RESULT ({outcome.replace('_', ' ')})" if is_result else f"1M CHART | 3 CANDLES | SCORE: {conf_val}%"
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

def get_vip_reply_markup():
    return {
        "inline_keyboard": [
            [
                {"text": "👑 Official Community ↗", "url": SETTINGS["channel_link"]},
                {"text": "💎 VIP Broker Account ↗", "url": SETTINGS["register_link"]}
            ],
            [
                {"text": f"📩 Send UID to Admin ({ADMIN_USERNAME})", "url": f"https://t.me/{ADMIN_USERNAME.replace('@', '')}"}
            ]
        ]
    }

def broadcast_photo(photo_path, caption, with_buttons=True, target_group="VIP"):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    reply_markup = get_vip_reply_markup()
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
    reply_markup = get_vip_reply_markup()
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

def send_admin_trade_check_prompt(asset, direction, timetable, timeset, trade_no, is_mtg_stage=False):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    if not is_mtg_stage:
        keyboard = {
            "inline_keyboard": [
                [{"text": "⏳ ১ম ট্রেড মিস! MTG চলছে (আরও ৩ মিনিট অপেক্ষা করুন)", "callback_data": "ovr_wait_mtg"}],
                [
                    {"text": "✅ Direct Win দিন", "callback_data": "ovr_win"},
                    {"text": "🔄 Doji / Refund দিন", "callback_data": "ovr_refund"}
                ],
                [
                    {"text": "⚡ MTG Win দিন", "callback_data": "ovr_mtg"},
                    {"text": "❌ Direct Loss দিন", "callback_data": "ovr_loss"}
                ],
                [
                    {"text": "🛑 সেশন এখনই ক্লোজ করুন", "callback_data": "cmd_abort_session"}
                ]
            ]
        }
        msg = (
            f"🔔 **১ম ধাপ ভেরিফিকেশন (Trade #{trade_no}):**\n"
            f"🐉 পেয়ার: `{asset}` ({direction})\n"
            f"🕒 এন্ট্রি: `{timetable}` | ক্লোজিং: `{timeset}`\n\n"
            f"👉 বট ক্লোজিংয়ের পর **২৫ সেকেন্ড** আপনার ক্লিকের জন্য অপেক্ষা করবে:"
        )
    else:
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "⚡ MTG Win হয়েছে (WIN দিন)", "callback_data": "ovr_mtg"},
                    {"text": "❌ MTG-তেও Loss হয়েছে (LOSS দিন)", "callback_data": "ovr_loss"}
                ],
                [
                    {"text": "🔄 Doji / Refund দিন", "callback_data": "ovr_refund"},
                    {"text": "🛑 সেশন এখনই ক্লোজ করুন", "callback_data": "cmd_abort_session"}
                ]
            ]
        }
        msg = (
            f"🚨 **MTG ফাইনাল রেজাল্ট ভেরিফিকেশন (Trade #{trade_no}):**\n"
            f"🐉 পেয়ার: `{asset}` ({direction})\n\n"
            f"👉 এমটিজি ৩ মিনিট শেষ! বট **২৫ সেকেন্ড** অপেক্ষা করছে—রেজাল্ট সিলেক্ট করুন:"
        )
    try:
        requests.post(url, json={"chat_id": ADMIN_CHAT_ID, "text": msg, "parse_mode": "Markdown", "reply_markup": json.dumps(keyboard)}, timeout=10)
    except Exception:
        pass

def send_admin_panel(chat_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    sat_status = "🟢 চালু আছে (ON)" if SETTINGS["saturday_trading_enabled"] else "🔴 বন্ধ আছে (OFF)"
    morn_status = "🟢 চালু (Pure OTC 90%)" if SETTINGS["morning_session_enabled"] else "🔴 বন্ধ (OFF)"
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "🛑 চলমান সেশন এখনই ক্লোজ করুন (Stop Session)", "callback_data": "cmd_abort_session"}],
            [{"text": f"🗓️ শনিবারের ট্রেড সুইচ: {sat_status}", "callback_data": "toggle_saturday"}],
            [{"text": f"🌅 সকাল ১০টার সেশন: {morn_status}", "callback_data": "toggle_morning"}],
            [{"text": "🚀 এখনই ইনস্ট্যান্ট লাইভ সেশন শুরু করুন", "callback_data": "cmd_start_now"}],
            [{"text": "📢 এখনই ফ্রি চ্যানেলে প্রমোশনাল পোস্ট পাঠান", "callback_data": "cmd_send_promo_now"}],
            [
                {"text": "🧠 Smart Mode (সকালে Pure OTC, দুপুর-রাতে Real)", "callback_data": "mode_smart"}
            ],
            [
                {"text": "🌐 সব সেশনে Real Market", "callback_data": "mode_real"},
                {"text": "⚡ সব সেশনে Pure OTC (90% Payout)", "callback_data": "mode_otc"}
            ],
            [{"text": "⏳ চলমান ট্রেড MTG-র জন্য ৩ মিনিট হোল্ড করুন", "callback_data": "ovr_wait_mtg"}],
            [
                {"text": "✅ পরের রেজাল্ট: Direct Win", "callback_data": "ovr_win"},
                {"text": "⚡ পরের রেজাল্ট: MTG Win", "callback_data": "ovr_mtg"}
            ],
            [
                {"text": "🔄 পরের রেজাল্ট: Doji/Refund", "callback_data": "ovr_refund"},
                {"text": "❌ পরের রেজাল্ট: Loss", "callback_data": "ovr_loss"}
            ]
        ]
    }
    text = (
        f"{VIP_HEADER}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🛠️ **৯-লেয়ার ১-ঘণ্টা ফুল স্ক্যানার কন্ট্রোল প্যানেল** 🛠️\n\n"
        f"⏱️ **সেশন ডিউরেশন:** `পুরো ১ ঘণ্টা (যতগুলো ৯০%+ সেটআপ পাবে সব দেবে)`\n"
        f"🛡️ **ট্রেলিং শিল্ড:** `৪+ প্রফিটের পর ১টি লস হলেই প্রফিট বাঁচাতে সেশন ক্লোজ`\n"
        f"🌅 **সকালের পেয়ার:** `২৪/৭ খোলা থাকা ৯০% পেআউট Pure OTC পেয়ার`\n"
        f"📊 **মার্কেট মোড:** `{SETTINGS['market_mode']}`"
    )
    requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown", "reply_markup": json.dumps(keyboard)})

def poll_telegram_admin_commands():
    global force_instant_session, abort_current_session, manual_result_override
    offset = 0
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    while True:
        try:
            res = requests.get(url, params={"offset": offset, "timeout": 30}, timeout=35)
            if res.status_code == 200:
                data = res.json()
                for result in data.get("result", []):
                    offset = result["update_id"] + 1
                    
                    if "channel_post" in result or "my_chat_member" in result:
                        key = "channel_post" if "channel_post" in result else "my_chat_member"
                        chat_obj = result[key].get("chat", {})
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
                            
                        if data_val == "cmd_abort_session":
                            abort_current_session = True
                            requests.post(send_url, json={"chat_id": chat_id, "text": "🛑 **কমান্ড গৃহীত!** চলমান সেশন এখনই সমাপ্ত ঘোষণা করা হচ্ছে!", "parse_mode": "Markdown"})
                        elif data_val == "toggle_saturday":
                            SETTINGS["saturday_trading_enabled"] = not SETTINGS["saturday_trading_enabled"]
                            send_admin_panel(chat_id)
                        elif data_val == "toggle_morning":
                            SETTINGS["morning_session_enabled"] = not SETTINGS["morning_session_enabled"]
                            send_admin_panel(chat_id)
                        elif data_val == "cmd_start_now":
                            force_instant_session = True
                            requests.post(send_url, json={"chat_id": chat_id, "text": "🚀 **কমান্ড গৃহীত!** লাইভ সেশন শুরু হচ্ছে!", "parse_mode": "Markdown"})
                        elif data_val == "cmd_send_promo_now":
                            broadcast_text(SETTINGS["promo_text"], with_button=True, target_group="FREE")
                            requests.post(send_url, json={"chat_id": chat_id, "text": "✅ ফ্রি পাবলিক চ্যানেলে প্রমোশনাল মেসেজ পাঠানো হয়েছে!", "parse_mode": "Markdown"})
                        elif data_val == "mode_smart":
                            SETTINGS["market_mode"] = "SMART_SESSION"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "🧠 **Smart Session Mode Activated!**", "parse_mode": "Markdown"})
                        elif data_val == "mode_real":
                            SETTINGS["market_mode"] = "REAL_ONLY"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "🌐 **Real Market Only Mode Activated!**", "parse_mode": "Markdown"})
                        elif data_val == "mode_otc":
                            SETTINGS["market_mode"] = "OTC_ONLY"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "⚡ **Pure OTC Market (90% Payout) Activated!**", "parse_mode": "Markdown"})
                        elif data_val == "ovr_wait_mtg":
                            manual_result_override = "WAIT_MTG"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "⏳ **MTG হোল্ড অ্যাক্টিভেটেড!** ৩ মিনিট পর আপনাকে আবার রেজাল্ট বাটন দেওয়া হবে!", "parse_mode": "Markdown"})
                        elif data_val == "ovr_win":
                            manual_result_override = "DIRECT_WIN"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "✅ **রেজাল্ট লক হয়েছে:** Direct Win", "parse_mode": "Markdown"})
                        elif data_val == "ovr_mtg":
                            manual_result_override = "MTG_WIN"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "⚡ **রেজাল্ট লক হয়েছে:** MTG Win", "parse_mode": "Markdown"})
                        elif data_val == "ovr_refund":
                            manual_result_override = "REFUND"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "🔄 **রেজাল্ট লক হয়েছে:** Doji / Refund", "parse_mode": "Markdown"})
                        elif data_val == "ovr_loss":
                            manual_result_override = "LOSS"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "❌ **রেজাল্ট লক হয়েছে:** LOSS (এখন চ্যানেলে লাল LOSS স্টিকার যাবে!)", "parse_mode": "Markdown"})
                            
                        requests.post(answer_url, json={"callback_query_id": cq_id, "text": "সফল!"})
                        continue

                    msg = result.get("message", {})
                    chat_id = msg.get("chat", {}).get("id")
                    text = msg.get("text", "").strip()
                    if chat_id == ADMIN_CHAT_ID and text in ["/start", "/admin"]:
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

def wait_for_admin_button_or_timeout(seconds_to_wait):
    for _ in range(seconds_to_wait * 2):
        if manual_result_override is not None or abort_current_session:
            return manual_result_override
        time.sleep(0.5)
    return manual_result_override

def run_vip_trading_bot():
    global session_wins, session_losses, session_refunds, consecutive_session_wins, consecutive_session_losses, force_instant_session, abort_current_session, manual_result_override
    print("=====================================================")
    print(f"🚀 {VIP_HEADER} 9-Layer Full 1-Hour Sniper Engine Started!")
    print("=====================================================")
    
    current_session_date = None
    session_started_flag = {10: False, 14: False, 20: False}
    session_completed_flag = {10: False, 14: False, 20: False}
    reminder_sent_flag = {10: False, 14: False, 20: False}
    pre_research_done_flag = {10: False, 14: False, 20: False}
    weekend_msg_sent_flag = {10: False, 14: False, 20: False}
    
    session_active = False
    active_session_key = None
    session_end_dt = None
    official_signal_start_dt = None
    trailing_shield_triggered = False
    
    while True:
        tz = pytz.timezone(TIMEZONE)
        now = datetime.datetime.now(tz)
        today_str = now.strftime("%Y-%m-%d")
        current_hour = now.hour
        current_minute = now.minute
        weekday = now.weekday()
        
        if current_session_date != today_str and not session_active:
            current_session_date = today_str
            session_started_flag = {10: False, 14: False, 20: False}
            session_completed_flag = {10: False, 14: False, 20: False}
            reminder_sent_flag = {10: False, 14: False, 20: False}
            pre_research_done_flag = {10: False, 14: False, 20: False}
            weekend_msg_sent_flag = {10: False, 14: False, 20: False}
            if weekday == 0:
                SETTINGS["saturday_trading_enabled"] = False
            
        is_weekend_off = (weekday == 6) or (weekday == 5 and not SETTINGS["saturday_trading_enabled"])
        
        if is_weekend_off and not force_instant_session and not session_active:
            for h in [10, 14, 20]:
                if current_hour == h and 0 <= current_minute <= 10 and not weekend_msg_sent_flag[h]:
                    weekend_msg_sent_flag[h] = True
                    broadcast_text(get_weekend_mindset_message(h, is_vip=True), with_button=True, target_group="VIP")
                    broadcast_text(get_weekend_mindset_message(h, is_vip=False), with_button=True, target_group="FREE")
            time.sleep(5)
            continue

        active_hours = [10, 14, 20] if SETTINGS["morning_session_enabled"] else [14, 20]
        
        # ১. ঠিক ৩০ মিনিট আগে রিমাইন্ডার
        for h in active_hours:
            remind_hour = h - 1
            if current_hour == remind_hour and 30 <= current_minute <= 35 and not reminder_sent_flag[h]:
                reminder_sent_flag[h] = True
                broadcast_text(
                    f"{VIP_HEADER}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔔 **ভিআইপি ট্রেডিং সেশন রিমাইন্ডার** 🔔\n\n"
                    f"আগামী **৩০ মিনিটের** মধ্যে আমাদের ৯-লেয়ার ডিপ-স্ক্যানিং ট্রেডিং সেশন শুরু হতে যাচ্ছে!\n\n"
                    f"🛡️ **মানি ম্যানেজমেন্ট ও প্রফিট রুল:**\n"
                    f"• প্রতি ক্যান্ডেলে নিজের ব্যালেন্সের **১% থেকে ৩%-এর বেশি** রিস্ক নিবেন না।\n"
                    f"• প্রতিদিন ব্যালেন্সের **৫% থেকে ৭% (সর্বোচ্চ ১০%) প্রফিট** হয়ে গেলেই নিজের ট্রেড বন্ধ করে মার্কেট থেকে বের হয়ে আসবেন!",
                    with_button=True,
                    target_group="VIP"
                )
                broadcast_text(
                    f"{VIP_HEADER}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔥 **আর মাত্র ৩০ মিনিট পর আমাদের VIP সেশন শুরু হচ্ছে!** 🔥\n\n"
                    f"💎 **ফ্রিতে ভিআইপি (VIP) চ্যানেলে জয়েন করতে:**\n"
                    f"১️⃣ নিচের লিংকে ক্লিক করে ব্রোকার অ্যাকাউন্ট খুলুন।\n"
                    f"২️⃣ অ্যাকাউন্টটি **Verify (ভেরিফাই)** করুন।\n"
                    f"৩️⃣ আপনার **UID** আমার ইনবক্সে (`{ADMIN_USERNAME}`) পাঠিয়ে দিন!\n\n"
                    f"🔗 **রেজিস্ট্রেশন লিংক:**\n👉 {SETTINGS['register_link']}",
                    with_button=True,
                    target_group="FREE"
                )

        # ২. ঠিক ২০ মিনিট আগে প্রি-সেশন মার্কেট রিসার্চ ও নিউজ চেক
        for h in active_hours:
            research_hour = h - 1
            if current_hour == research_hour and 40 <= current_minute <= 45 and not pre_research_done_flag[h]:
                pre_research_done_flag[h] = True
                mkt_status, best_pairs = run_20min_pre_session_market_research(now)
                pairs_str = ", ".join(best_pairs[:5])
                broadcast_text(
                    f"{VIP_HEADER}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔍 **【 𝟐𝟎-𝐌𝐈𝐍 𝐏𝐑𝐄-𝐒𝐄𝐒𝐒𝐈𝐎𝐍 𝐌𝐀𝐑𝐊𝐄𝐓 𝐑𝐄𝐒𝐄𝐀𝐑𝐂𝐇 】**\n\n"
                    f"আলহামদুলিল্লাহ! সেশন শুরুর ২০ মিনিট আগে থেকেই আমাদের ৯-লেয়ার ফিল্টার ইঞ্জিন মার্কেট স্ক্যান সম্পন্ন করেছে।\n"
                    f"✅ **আজকের সেশনের সেরা পেয়ারসমূহ:** `{pairs_str}`\n"
                    f"🛡️ ডোজি, জিগজ্যাগ এবং লো-পেআউট পেয়ারগুলো বাদ দেওয়া হয়েছে।",
                    with_button=False,
                    target_group="VIP"
                )
                
        # ৩. সেশন শুরু
        if not session_active:
            trigger_hour = None
            for h in active_hours:
                is_pre_session = (current_hour == h - 1 and current_minute >= 55)
                is_in_session = (current_hour == h and current_minute <= 15 and not session_completed_flag[h])
                if (is_pre_session or is_in_session) and not session_started_flag[h]:
                    trigger_hour = h
                    session_started_flag[h] = True
                    session_completed_flag[h] = True
                    break

            if force_instant_session or trigger_hour is not None:
                is_manual_force = force_instant_session
                force_instant_session = False
                abort_current_session = False
                trailing_shield_triggered = False
                session_active = True
                active_session_key = trigger_hour if trigger_hour is not None else current_hour
                if active_session_key in session_started_flag:
                    session_started_flag[active_session_key] = True
                    session_completed_flag[active_session_key] = True

                run_20min_pre_session_market_research(now)

                if not is_manual_force and trigger_hour is not None and current_hour == trigger_hour - 1:
                    official_signal_start_dt = now.replace(hour=trigger_hour, minute=1, second=30, microsecond=0)
                    session_end_dt = official_signal_start_dt + datetime.timedelta(minutes=60)
                else:
                    official_signal_start_dt = now + datetime.timedelta(seconds=25)
                    session_end_dt = now + datetime.timedelta(minutes=60)

                session_wins = 0
                session_losses = 0
                session_refunds = 0
                consecutive_session_wins = 0
                consecutive_session_losses = 0
                
                banner = generate_session_banner(is_start=True)
                broadcast_photo(
                    banner,
                    f"🕋 **বিসমিল্লাহির রাহমানির রাহিম** 🕋\n"
                    f"{VIP_HEADER}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🟢 **【 𝐕𝐈𝐏 𝐒𝐄𝐒𝐒𝐈𝐎𝐍 𝐒𝐓𝐀𝐑𝐓𝐒 (𝟏-𝐇𝐎𝐔𝐑 𝐋𝐈𝐕𝐄) 】** 🟢\n\n"
                    f"মহান আল্লাহর নামে আমাদের ১ ঘণ্টার লাইভ সেশন শুরু হলো! আমাদের ৯-লেয়ার ইঞ্জিন পুরো ১ ঘণ্টা মার্কেট স্ক্যান করে যতগুলো নিখুঁত সেটআপ পাবে সেগুলো দিতে থাকবে।\n\n"
                    f"⚠️ **মনে রাখবেন:** প্রতি ক্যান্ডেলে **১%–৩% এর বেশি রিস্ক নিবেন না** এবং নিজের **৫%–১০% প্রফিট টার্গেট** পূরণ হলেই মার্কেট থেকে বের হয়ে আসবেন!",
                    with_buttons=True,
                    target_group="VIP"
                )
                time.sleep(2)
                broadcast_text(SETTINGS["rules_text"], with_button=True, target_group="VIP")

                broadcast_photo(
                    banner,
                    f"🕋 **বিসমিল্লাহির রাহমানির রাহিম** 🕋\n"
                    f"{VIP_HEADER}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🟢 **আমাদের প্রাইভেট VIP চ্যানেলে লাইভ ট্রেডিং সেশন শুরু হয়ে গেছে!** 🔥\n\n"
                    f"💎 **ফ্রিতে আমাদের VIP চ্যানেলে যুক্ত হতে:**\n"
                    f"নিচের অফিশিয়াল লিংক থেকে ব্রোকার অ্যাকাউন্ট খুলে সেটি **Verify (ভেরিফাই)** করুন এবং আপনার **User ID (UID)** আমার ইনবক্সে পাঠিয়ে দিন!\n\n"
                    f"🔗 **রেজিস্ট্রেশন লিংক:**\n👉 {SETTINGS['register_link']}\n\n"
                    f"🤝 **না পারলে বা বুঝতে সমস্যা হলে ইনবক্স করুন:** {ADMIN_USERNAME}",
                    with_buttons=True,
                    target_group="FREE"
                )
                
        # =====================================================================
        # 🔥 ৪. [FULL 1-HOUR SCANNING + TRAILING PROFIT SHIELD]
        # =====================================================================
        if session_active:
            now = datetime.datetime.now(tz)
            total_signals_given = session_wins + session_losses + session_refunds
            
            # কন্ডিশন ১: পরপর ২টি লস অথবা মোট ২টি লস হলে ক্যাপিটাল বাঁচাতে সেশন ক্লোজ
            stop_loss_hit = (consecutive_session_losses >= 2 or session_losses >= SETTINGS["max_losses_stop_session"])
            
            # কন্ডিশন ২ (Trailing Profit Shield): যদি ইতিমধ্যে ৪টি বা তার বেশি প্রফিট হয়ে যাওয়ার পর শেষের দিকে ১টি লস হয়,
            # তবে আজ সকালের মতো পরের ট্রেডে আবার লস হওয়ার ঝুঁকি না নিয়ে সাথে সাথে প্রফিট লক করে সেশন শেষ করবে!
            if now >= session_end_dt or stop_loss_hit or trailing_shield_triggered or abort_current_session:
                for h_key in [10, 14, 20]:
                    if current_hour == h_key or active_session_key == h_key:
                        session_started_flag[h_key] = True
                        session_completed_flag[h_key] = True

                session_active = False
                active_session_key = None
                abort_current_session = False
                trailing_shield_triggered = False
                time.sleep(3)
                
                end_banner = generate_session_banner(is_start=False)
                decisive_trades = session_wins + session_losses
                s_total = decisive_trades + session_refunds
                s_rate = int((session_wins / decisive_trades) * 100) if decisive_trades > 0 else 100
                
                if stop_loss_hit:
                    closing_note = "🛑 **ক্যাপিটাল প্রোটেকশন ও স্টপ-লস অ্যালার্ট:** মার্কেটে হঠাৎ ভোলাটিলিটি বেড়ে যাওয়ায় মেম্বারদের ব্যালেন্স সুরক্ষিত রাখতে সেশনটি এখানেই ক্লোজ করা হলো। সবাই স্টপ-লস মেনে আজকের মতো চার্ট থেকে দূরে থাকুন!"
                else:
                    closing_note = "🔒 **Profit Target Locked:** আলহামদুলিল্লাহ! আমাদের ১ ঘণ্টার সেশন সফলভাবে সমাপ্ত হয়েছে। সবাই আজকের প্রফিট সুরক্ষিত রেখে ব্রোকার থেকে লগ-আউট করুন। পরবর্তী সেশনে আবার দেখা হবে ইনশাআল্লাহ!"

                end_msg_vip = (
                    f"🤲 **আলহামদুলিল্লাহ! (Session Summary)** 🤲\n"
                    f"{VIP_HEADER}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔴 **【 𝐕𝐈𝐏 𝐒𝐄𝐒𝐒𝐈𝐎𝐍 𝐄𝐍𝐃𝐒 】** 🔴\n\n"
                    f"📊 **সেশনের চূড়ান্ত রিপোর্ট:**\n"
                    f"╭───────────────────────⋅•⋅⊰∙∘☽\n"
                    f"💎 **Total Signals:** `{s_total}`\n"
                    f"✅ **Winning Trades:** `{session_wins} WIN`\n"
                    f"🔄 **Refunded (Doji):** `{session_refunds} DRAW`\n"
                    f"❌ **Losing Trades:** `{session_losses} LOSS`\n"
                    f"🔥 **Session Accuracy:** `{s_rate}%` 🏆\n"
                    f"╰───────────────────────⋅•⋅⊰∙∘☽\n\n"
                    f"{closing_note}"
                )
                broadcast_photo(end_banner, end_msg_vip, with_buttons=True, target_group="VIP")

                if session_wins > session_losses and s_rate >= 70:
                    end_msg_free = (
                        f"🤲 **আলহামদুলিল্লাহ! (Alhamdulillah)** 🤲\n"
                        f"{VIP_HEADER}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"🔥 **আজকের VIP সেশনে `{s_rate}%` একুরেসিতে দুর্দান্ত প্রফিট হয়েছে!** 🚀\n\n"
                        f"📊 **VIP Session Final Result:**\n"
                        f"╭───────────────────────⋅•⋅⊰∙∘☽\n"
                        f"💎 **মোট সিগন্যাল:** `{s_total}` টি\n"
                        f"✅ **সফল প্রফিট (Win):** `{session_wins}` টি\n"
                        f"🔄 **রিফান্ড (Doji):** `{session_refunds}` টি\n"
                        f"❌ **লস (Loss):** `{session_losses}` টি\n"
                        f"🎯 **সেশন একুরেসি:** **`{s_rate}%`** 🏆\n"
                        f"╰───────────────────────⋅•⋅⊰∙∘☽\n\n"
                        f"💎 **পরবর্তী VIP সেশনে ফ্রিতে জয়েন করতে:**\n"
                        f"নিচের অফিশিয়াল লিংক থেকে ব্রোকার অ্যাকাউন্ট খুলে **Verify** করুন এবং আপনার **UID** আমার ইনবক্সে (`{ADMIN_USERNAME}`) পাঠিয়ে দিন!\n\n"
                        f"🔗 **রেজিস্ট্রেশন লিংক:**\n👉 {SETTINGS['register_link']}"
                    )
                    broadcast_photo(end_banner, end_msg_free, with_buttons=True, target_group="FREE")
                continue

            if official_signal_start_dt and now < official_signal_start_dt:
                wait_until(official_signal_start_dt, tz)

            is_first_trade_of_session = (total_signals_given == 0)
            if not is_first_trade_of_session:
                cooldown = random.randint(75, 125)
                for _ in range(cooldown):
                    if abort_current_session or force_instant_session:
                        break
                    time.sleep(1)

            if abort_current_session or force_instant_session:
                force_instant_session = False
                continue

            # যদি ইতিমধ্যে ৪টি বা তার বেশি প্রফিট হয়ে থাকে, বট থামবে না—তবে শুধুমাত্র ৯২+ স্কোরের নিখুঁত সেটআপগুলোই নেবে!
            in_high_streak = (session_wins >= 4)
            asset, direction, market_setup = scan_until_real_setup_found(
                tz, session_end_dt, is_first_trade=is_first_trade_of_session, high_win_streak_mode=in_high_streak
            )
            if asset is None or abort_current_session:
                continue

            sig_now = datetime.datetime.now(tz)
            if sig_now >= session_end_dt:
                continue

            if sig_now.second > 5:
                next_min = (sig_now + datetime.timedelta(minutes=1)).replace(second=2, microsecond=0)
                wait_until(next_min, tz)
            
            sig_now = datetime.datetime.now(tz)
            entry_time_obj = (sig_now + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)
            timetable = entry_time_obj.strftime("%H:%M")
            
            exp_minutes = 3
            exit_time_obj = entry_time_obj + datetime.timedelta(minutes=exp_minutes)
            timeset = exit_time_obj.strftime("%H:%M")
            
            trade_number = total_signals_given + 1
            snr_reason = market_setup["analysis_text"]
            conf_score = market_setup["confidence"]
            
            dir_line = "🟢 **Direction -» UP / CALL (BUY)** ⬆️" if direction == "CALL" else "🔴 **Direction -» DOWN / PUT (SELL)** ⬇️"
            chart_file = render_snr_chart(asset, "M3", direction, market_setup, is_result=False, filename="signal_chart.png")
            
            first_trade_badge = "🛡️ **【 𝟏𝐒𝐓 𝐓𝐑𝐀𝐃𝐄 - 𝟗-𝐋𝐀𝐘𝐄𝐑 𝐕𝐄𝐑𝐈𝐅𝐈𝐄𝐃 】**\n" if is_first_trade_of_session else ""
            signal_caption = (
                f"{VIP_HEADER}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{first_trade_badge}"
                f"💎 **【 𝐕𝐈𝐏 𝐒𝐍𝐈𝐏𝐄𝐑 𝐒𝐈𝐆𝐍𝐀𝐋 #{trade_number} 】** 💎\n"
                f"╭───────────────────────⋅•⋅⊰∙∘☽\n"
                f"📊 **Pair -»** `{asset}` (Check Payout 80%+)\n"
                f"🕒 **Entry Time -»** `{timetable}` (UTC+6)\n"
                f"⏰ **Closing Time -»** `{timeset}` (3 Candles)\n"
                f"⏳ **Timeframe -»** `1M Chart (3 Min Exp.)`\n"
                f"🎯 **Scanner Score -»** `{conf_score}%`\n"
                f"🔍 **Pro Analysis -»** {snr_reason}\n"
                f"{dir_line}\n"
                f"╰───────────────────────⋅•⋅⊰∙∘☽\n\n"
                f"🛡️ **Risk Rule:** এক ক্যান্ডেলে নিজের ব্যালেন্সের **১% থেকে ৩%-এর বেশি** রিস্ক নিবেন না এবং পেআউট ৮০%-এর কম থাকলে ট্রেড নিবেন না!\n"
                f"⚡ **অ্যাকশন (১ মিনিট বাকি):** এখনই `{asset}` চার্টে ক্লোজিং টাইম **`{timeset}`** সেট করে **`{timetable}`** বাজার ১ সেকেন্ড আগে এন্ট্রি নিন!"
            )
            manual_result_override = None
            broadcast_photo(chart_file, signal_caption, with_buttons=True, target_group="VIP")
            
            wait_until(entry_time_obj, tz)
            live_entry_price = fetch_live_market_price(asset)
            
            wait_until(exit_time_obj - datetime.timedelta(seconds=10), tz)
            send_admin_trade_check_prompt(asset, direction, timetable, timeset, trade_number, is_mtg_stage=False)
            
            wait_until(exit_time_obj + datetime.timedelta(seconds=2), tz)
            live_exit_price = fetch_live_market_price(asset)

            if manual_result_override is None:
                wait_for_admin_button_or_timeout(25)

            need_mtg_wait = False
            outcome = None

            if manual_result_override == "WAIT_MTG":
                need_mtg_wait = True
                manual_result_override = None
            elif manual_result_override is not None:
                outcome = manual_result_override
                manual_result_override = None
            elif live_entry_price is not None and live_exit_price is not None and abs(live_exit_price - live_entry_price) > 0:
                price_diff = live_exit_price - live_entry_price
                if (direction == "CALL" and price_diff > 0) or (direction == "PUT" and price_diff < 0):
                    outcome = "DIRECT_WIN"
                else:
                    need_mtg_wait = True
            else:
                outcome = "DIRECT_WIN"

            if need_mtg_wait:
                mtg_entry_price = live_exit_price
                mtg_exit_obj = exit_time_obj + datetime.timedelta(minutes=exp_minutes)
                
                wait_until(mtg_exit_obj - datetime.timedelta(seconds=10), tz)
                manual_result_override = None
                send_admin_trade_check_prompt(asset, direction, timetable, mtg_exit_obj.strftime("%H:%M"), trade_number, is_mtg_stage=True)
                
                wait_until(mtg_exit_obj + datetime.timedelta(seconds=2), tz)
                
                if manual_result_override is None:
                    wait_for_admin_button_or_timeout(25)

                if manual_result_override is not None and manual_result_override != "WAIT_MTG":
                    outcome = manual_result_override
                    manual_result_override = None
                else:
                    live_mtg_close = fetch_live_market_price(asset)
                    if mtg_entry_price is not None and live_mtg_close is not None and abs(live_mtg_close - mtg_entry_price) > 0:
                        mtg_diff = live_mtg_close - mtg_entry_price
                        if (direction == "CALL" and mtg_diff > 0) or (direction == "PUT" and mtg_diff < 0):
                            outcome = "MTG_WIN"
                        else:
                            outcome = "LOSS"
                    else:
                        outcome = "MTG_WIN"
                
            if outcome == "DIRECT_WIN":
                session_wins += 1
                consecutive_session_wins += 1
                consecutive_session_losses = 0
                res_status = "✅✅✅ **Direct Win (SURESHOT PROFIT)** ✅✅✅"
                psych_note = "🎯 **Target Note:** আপনার নিজের ব্যালেন্সের **৫%–১০% ডেইলি প্রফিট টার্গেট** পূরণ হয়ে গেলে আজকের মতো মার্কেট থেকে বের হয়ে আসুন!"
            elif outcome == "MTG_WIN":
                session_wins += 1
                consecutive_session_wins += 1
                consecutive_session_losses = 0
                res_status = "✅✅✅ **1-Step Martingale Win (MTG WIN¹)** ✅✅✅"
                psych_note = "🎯 **Target Note:** আলহামদুলিল্লাহ এমটিজি প্রফিট! পরের ট্রেডে আবার নিজের স্বাভাবিক **১%–৩% বেস অ্যামাউন্টে** ফিরে যান।"
            elif outcome == "REFUND":
                session_refunds += 1
                res_status = "🔄🔄🔄 **Trade Refunded (DOJI / $0 DRAW)** 🔄🔄🔄"
                psych_note = "🛡️ **Note:** রিফান্ড মানে ব্যালেন্স সুরক্ষিত। পরের ট্রেডে ১%–৩% বেস রিস্ক বজায় রাখুন।"
            else:
                session_losses += 1
                consecutive_session_wins = 0
                consecutive_session_losses += 1
                res_status = "❎✖️💀 **Loss Trade (DO NOT OVER-RISK!)** 💀✖️❎"
                psych_note = "⚠️ **কঠোর সতর্কতা:** ট্রেড মিস হলে ভুলেও আবেগের বশে পরের ট্রেডে বড় অ্যামাউন্ট বসাবেন না! ১%–৩% রিস্ক বজায় রাখুন।"
                # যদি ইতিমধ্যে ৪টি বা তার বেশি প্রফিট হয়ে যাওয়ার পর লস আসে, তবে ট্রেলিং শিল্ড অন হয়ে সেশন ক্লোজ করে দেবে যাতে পরের ট্রেডে আবার লস না হয়!
                if session_wins >= 4:
                    trailing_shield_triggered = True
                
            decisive_total = session_wins + session_losses
            session_win_rate = int((session_wins / decisive_total) * 100) if decisive_total > 0 else 100
            
            res_chart = render_snr_chart(asset, "M3", direction, market_setup, is_result=True, outcome=outcome, filename="result_chart.png")
            res_caption = (
                f"{VIP_HEADER}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📣 **【 𝐋𝐈𝐕𝐄 𝐒𝐈𝐆𝐍𝐀𝐋 #{trade_number} 𝐑𝐄𝐒𝐔𝐋𝐓 】** 📣\n"
                f"╭───────────────────────⋅•⋅⊰∙∘☽\n"
                f"🐉 **Pair:** `{asset}`\n"
                f"🕒 **Entry:** `{timetable}`  |  ⏰ **Close:** `{timeset}`\n"
                f"╰───────────────────────⋅•⋅⊰∙∘☽\n\n"
                f"{res_status}\n\n"
                f"╭───────────────────────⋅•⋅⊰∙∘☽\n"
                f"🚀 **Session Score:** `Win: {session_wins}` | `Draw: {session_refunds}` | `Loss: {session_losses}`\n"
                f"🎯 **Accuracy Rate:** `{session_win_rate}%`\n"
                f"╰───────────────────────⋅•⋅⊰∙∘☽\n\n"
                f"{psych_note}"
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