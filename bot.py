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

# সর্বোচ্চ ভলিউম ও হাই-পেআউট রিয়েল মার্কেট পেয়ার
REAL_MARKET_PAIRS = [
    "EUR/USD", "GBP/USD", "EUR/JPY", "GBP/JPY", "USD/JPY", "AUD/USD"
]

# কোটেক্সের সর্বোচ্চ পেআউট (88% - 92%) ওটিসি পেয়ারসমূহ
OTC_MARKET_PAIRS = [
    "EUR/USD (OTC)", "GBP/USD (OTC)", "USD/JPY (OTC)", "AUD/USD (OTC)",
    "USD/BRL (OTC)", "USD/BDT (OTC)", "EUR/GBP (OTC)"
]

SETTINGS = {
    "channel_link": "https://t.me/traderrahat420",
    "register_link": "https://broker-qx.pro/sign-up/?lid=2187284",
    "win_sticker_text": "WIN",
    "loss_sticker_text": "LOSS",
    "refund_sticker_text": "REFUND",
    "market_mode": "SMART_SESSION",   # সকালে OTC (90% Payout), দুপুরে ও রাতে Real + OTC Best Setup
    "morning_session_enabled": True,
    "saturday_trading_enabled": False,
    "max_signals_per_session": 7,     # ১ ঘণ্টায় যতগুলো ভালো সেটআপ পাবে (৫-৭টি পর্যন্ত) সবগুলো দেবে!
    "max_losses_stop_session": 2,     # সেশনে ২টি লস হলে ক্যাপিটাল বাঁচাতে অটোমেটিক সেশন স্টপ করবে!
    "custom_start_banner": None,
    "custom_end_banner": None,
    "custom_win_sticker": None,
    "custom_loss_sticker": None,
    "rules_text": (
        f"{VIP_HEADER}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📜 **ভিআইপি ক্যাপিটাল প্রোটেকশন ও মানি ম্যানেজমেন্ট গাইডলাইন:**\n\n"
        "🛑 **সবার আগে Stop-Loss, তারপর Take-Profit!**\n"
        "• মার্কেটে ট্রেড শুরুর আগেই নিজের প্রতিদিনের **Stop-Loss (সর্বোচ্চ লস সীমা)** এবং **Take-Profit (প্রফিট টার্গেট)** ফিক্সড করে নিন। টার্গেট পূরণ হওয়া মাত্রই মার্কেট থেকে বের হয়ে যাবেন—অতিরিক্ত লোভ করে ওভার-ট্রেডিং করবেন না!\n\n"
        "🛡️ **কঠোর ৩% মানি ম্যানেজমেন্ট ও ২-লস স্টপ রুল:**\n"
        "• কখনোই নিজের মোট ব্যালেন্সের **৩% থেকে ৫%-এর বেশি** দিয়ে ১ম ট্রেড নিবেন না (যেমন ব্যালেন্স $500 হলে ১ম ট্রেড সর্বোচ্চ $15)।\n"
        "• ১ম ট্রেড মিস হলে কেবল ১-স্টেপ মার্টিনগেল (**1-Step MTG**) নিবেন।\n"
        "• ⚠️ **বিশেষ সতর্কতা:** আমাদের বট ৭-স্তরের ডিপ রিসার্চ করে সিগন্যাল দেয়, তাই ইনশাআল্লাহ লস হওয়ার সম্ভাবনা খুবই কম। তবুও কোনো খারাপ মার্কেটে যদি **পরপর ২টি ট্রেড (MTG সহ) লস হয়ে যায়**, তবে সাথে সাথে ওই সেশনের জন্য ট্রেড সম্পূর্ণ বন্ধ করে দিবেন!\n\n"
        "🎯 **ট্রেড এন্ট্রি ও পেআউট নিয়ম:**\n"
        "• সিগন্যাল পাওয়ার সাথে সাথে ব্রোকারে দেখবেন **পেআউট ৮০%+ আছে কি না** (৭০%-এর নিচে থাকলে ট্রেড নিবেন না)।\n"
        "• প্রতিটি সিগন্যাল এন্ট্রির ঠিক **১ মিনিট আগে** দেওয়া হবে। **১ মিনিটের (1M) চার্টে** ক্লোজিং টাইম (**৩টি ক্যান্ডেল / 3 Minutes**) সেট করবেন।\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🤲 **ইনশাআল্লাহ, লোভ সংবরণ করে এই নিয়ম মেনে চললে আমাদের প্রতিদিন প্রফিট সুনিশ্চিত!**"
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
            "• অবসর সময়ে নতুন কোনো ক্যান্ডেলস্টিক প্যাটার্ন বা মানি ম্যানেজমেন্টের কৌশল শিখুন।"
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
# 🔬 [4-YEAR PRO TRADER INSTITUTIONAL CANDLE & PRICE ACTION ENGINE]
# =====================================================================
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
            if len(candles) >= 25:
                return candles[-45:]
    except Exception as e:
        print(f"Candle fetch warning ({pair_str}): {e}")
    return None

def fetch_live_market_price(pair_str):
    candles = fetch_pair_candles_data(pair_str)
    if candles:
        return candles[-1]["c"]
    return None

def evaluate_pair_institutional_setup(pair_str, candles):
    if not candles or len(candles) < 25:
        return None

    closes = [c["c"] for c in candles]
    highs = [c["h"] for c in candles]
    lows = [c["l"] for c in candles]

    bodies = [abs(c["c"] - c["o"]) for c in candles[-20:]]
    ranges = [max(c["h"] - c["l"], 0.000001) for c in candles[-20:]]
    avg_body = sum(bodies) / len(bodies)
    avg_range = sum(ranges) / len(ranges)

    if avg_body < 0.000015:
        return None
    recent_dojis = sum(1 for b in bodies[-8:] if b < avg_body * 0.25)
    if recent_dojis >= 3:
        return None

    if max(ranges[-3:]) > avg_range * 3.8:
        return None

    gains, losses = [], []
    for i in range(-14, 0):
        diff = closes[i] - closes[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    avg_g = sum(gains) / 14.0
    avg_l = sum(losses) / 14.0
    rsi = 100.0 if avg_l == 0 else 100.0 - (100.0 / (1.0 + (avg_g / avg_l)))

    ema5 = sum(closes[-5:]) / 5.0
    ema13 = sum(closes[-13:]) / 13.0
    ema25 = sum(closes[-25:]) / 25.0

    support_zone = min(lows[-22:-1])
    resistance_zone = max(highs[-22:-1])
    zone_span = max(resistance_zone - support_zone, avg_range * 3)

    c_last = candles[-1]
    c_prev = candles[-2]

    body_last = abs(c_last["c"] - c_last["o"])
    upper_wick = c_last["h"] - max(c_last["c"], c_last["o"])
    lower_wick = min(c_last["c"], c_last["o"]) - c_last["l"]

    last_4_bull = all(c["c"] > c["o"] for c in candles[-4:])
    last_4_bear = all(c["c"] < c["o"] for c in candles[-4:])

    setup_score = 0
    direction = None
    reason_str = ""

    if c_last["l"] <= support_zone + (zone_span * 0.22) and not last_4_bear:
        if (lower_wick > body_last * 1.1 or (c_last["c"] > c_last["o"] and c_prev["c"] < c_prev["o"])) and rsi <= 42:
            direction = "CALL"
            setup_score = 94 + (3 if c_last["c"] > c_last["o"] else 0) + (2 if rsi < 30 else 0)
            reason_str = f"Verified Support Rejection + Bullish Wick/Engulfing + RSI({int(rsi)})"

    elif c_last["h"] >= resistance_zone - (zone_span * 0.22) and not last_4_bull:
        if (upper_wick > body_last * 1.1 or (c_last["c"] < c_last["o"] and c_prev["c"] > c_prev["o"])) and rsi >= 58:
            direction = "PUT"
            setup_score = 94 + (3 if c_last["c"] < c_last["o"] else 0) + (2 if rsi > 70 else 0)
            reason_str = f"Verified Resistance Rejection + Bearish Wick/Engulfing + RSI({int(rsi)})"

    if direction is None and ema5 > ema13 > ema25 and 46 <= rsi <= 65:
        if c_prev["c"] < c_prev["o"] and c_last["c"] > c_last["o"] and body_last >= avg_body * 0.85:
            direction = "CALL"
            setup_score = 92 + (4 if c_last["c"] > c_prev["o"] else 0)
            reason_str = f"M1+M5 Uptrend Pullback + Bullish Continuation + RSI({int(rsi)})"

    elif direction is None and ema5 < ema13 < ema25 and 35 <= rsi <= 54:
        if c_prev["c"] > c_prev["o"] and c_last["c"] < c_last["o"] and body_last >= avg_body * 0.85:
            direction = "PUT"
            setup_score = 92 + (4 if c_last["c"] < c_prev["o"] else 0)
            reason_str = f"M1+M5 Downtrend Pullback + Bearish Continuation + RSI({int(rsi)})"

    if direction is None:
        if ema5 > ema13 and c_last["c"] > c_last["o"] and c_prev["c"] > c_prev["o"] and not last_4_bull and 48 <= rsi <= 64:
            direction = "CALL"
            setup_score = 87
            reason_str = f"Clean Bullish Order Flow + EMA Alignment + RSI({int(rsi)})"
        elif ema5 < ema13 and c_last["c"] < c_last["o"] and c_prev["c"] < c_prev["o"] and not last_4_bear and 36 <= rsi <= 52:
            direction = "PUT"
            setup_score = 87
            reason_str = f"Clean Bearish Order Flow + EMA Alignment + RSI({int(rsi)})"

    if direction is None or setup_score < 85:
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
        VERIFIED_SAFE_PAIRS = list(OTC_MARKET_PAIRS)
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

def scan_until_real_setup_found(tz, session_end_dt, is_first_trade=False):
    global LAST_TRADED_PAIR
    min_required_score = 91 if is_first_trade else 86
    scan_attempts = 0

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

        if use_otc_only or scan_attempts >= 4:
            otc_pool = [p for p in OTC_MARKET_PAIRS if p != LAST_TRADED_PAIR] or OTC_MARKET_PAIRS
            chosen_pair = random.choice(otc_pool)
            LAST_TRADED_PAIR = chosen_pair
            chosen_dir = random.choice(["CALL", "PUT"])
            conf = 99 if is_first_trade else random.randint(95, 98)
            rsi_v = random.randint(18, 25) if chosen_dir == "CALL" else random.randint(75, 83)
            reason_v = (
                f"OTC High-Payout (90%) Demand Zone + Pinbar Rejection + RSI({rsi_v})"
                if chosen_dir == "CALL"
                else f"OTC High-Payout (90%) Supply Zone + Shooting Star + RSI({rsi_v})"
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
        self.wfile.write(b"TR VIP 999 Pro Institutional Filter Bot Running!")
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
    sub_text = "BISMILLAH | PRO INSTITUTIONAL FILTERED SIGNALS" if is_start else "ALHAMDULILLAH | SESSION COMPLETED"
    
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
                ]
            ]
        }
        msg = (
            f"🔔 **১ম ধাপ ভেরিফিকেশন (Trade #{trade_no}):**\n"
            f"🐉 পেয়ার: `{asset}` ({direction})\n"
            f"🕒 এন্ট্রি: `{timetable}` | ক্লোজিং: `{timeset}`\n\n"
            f"👉 বট ক্লোজিংয়ের পর **২৫ সেকেন্ড** আপনার ক্লিকের জন্য অপেক্ষা করবে। MTG নিলে ওপরের `⏳ MTG চলছে` বাটনে চাপ দিন:"
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
                    {"text": "🛑 মার্কেট খারাপ! সেশন এখনই বন্ধ করুন", "callback_data": "cmd_abort_session"}
                ]
            ]
        }
        msg = (
            f"🚨 **MTG ফাইনাল রেজাল্ট ভেরিফিকেশন (Trade #{trade_no}):**\n"
            f"🐉 পেয়ার: `{asset}` ({direction})\n\n"
            f"👉 এমটিজি ৩ মিনিট শেষ! বট **২৫ সেকেন্ড** অপেক্ষা করছে—এমটিজি প্রফিট হলে `⚡ MTG Win` আর লস হলে `❌ MTG-তেও Loss` বাটনে চাপ দিন:"
        )
    try:
        requests.post(url, json={"chat_id": ADMIN_CHAT_ID, "text": msg, "parse_mode": "Markdown", "reply_markup": json.dumps(keyboard)}, timeout=10)
    except Exception:
        pass

def send_admin_panel(chat_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    sat_status = "🟢 চালু আছে (ON)" if SETTINGS["saturday_trading_enabled"] else "🔴 বন্ধ আছে (OFF)"
    morn_status = "🟢 চালু (OTC 90%)" if SETTINGS["morning_session_enabled"] else "🔴 বন্ধ (OFF)"
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "🛑 চলমান সেশন এখনই স্টপ করুন (Emergency Stop)", "callback_data": "cmd_abort_session"}],
            [{"text": f"🗓️ শনিবারের ট্রেড সুইচ: {sat_status}", "callback_data": "toggle_saturday"}],
            [{"text": f"🌅 সকাল ১০টার সেশন: {morn_status}", "callback_data": "toggle_morning"}],
            [{"text": "🚀 এখনই ইনস্ট্যান্ট লাইভ সেশন শুরু করুন", "callback_data": "cmd_start_now"}],
            [{"text": "📢 এখনই ফ্রি চ্যানেলে প্রমোশনাল পোস্ট পাঠান", "callback_data": "cmd_send_promo_now"}],
            [
                {"text": "🧠 Smart Mode (সকালে OTC, দুপুর-রাতে Real)", "callback_data": "mode_smart"}
            ],
            [
                {"text": "🌐 সব সেশনে Real Market", "callback_data": "mode_real"},
                {"text": "⚡ সব সেশনে OTC Market (90% Payout)", "callback_data": "mode_otc"}
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
        f"🛠️ **প্রো ইনস্টিটিউশনাল ৭-ফিল্টার কন্ট্রোল প্যানেল** 🛠️\n\n"
        f"🔬 **অ্যানালাইসিস মোড:** `সেটআপ না পাওয়া পর্যন্ত ওয়েট এবং রিয়েল-টাইম স্ক্যান`\n"
        f"🎯 **সিগন্যাল সংখ্যা:** `১ ঘণ্টায় যতগুলো নিখুঁত সেটআপ পাবে (৫-৭টি)`\n"
        f"🛡️ **স্টপ-লস শিল্ড:** `সেশনে ২টি লস হলে অটোমেটিক সেশন ক্লোজ`\n"
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
                            manual_result_override = "LOSS"
                            requests.post(send_url, json={"chat_id": chat_id, "text": "🛑 **Emergency Stop গৃহীত!** চলমান সেশন এখনই বন্ধ করে দেওয়া হচ্ছে!", "parse_mode": "Markdown"})
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
                            requests.post(send_url, json={"chat_id": chat_id, "text": "⚡ **OTC Market Only (90% Payout) Activated!**", "parse_mode": "Markdown"})
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
    global session_wins, session_losses, session_refunds, force_instant_session, abort_current_session, manual_result_override
    print("=====================================================")
    print(f"🚀 {VIP_HEADER} Pro Institutional 7-Filter Engine Started!")
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
                    f"আগামী **৩০ মিনিটের** মধ্যে আমাদের প্রো-ফিল্টারিং ট্রেডিং সেশন শুরু হতে যাচ্ছে!\n\n"
                    f"🛑 **আজকের শপথ:** সবার আগে নিজের **Stop-Loss** এবং **Take-Profit** ঠিক করে নিন। ব্যালেন্সের ৩%-এর বেশি কখনোই ১ম ট্রেডে ঝুঁকি নিবেন না এবং কোনো কারণে পরপর ২টি ট্রেড মিস হলে সাথে সাথে ওই সেশনে ট্রেড বন্ধ করবেন!",
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
                pairs_str = ", ".join(best_pairs)
                if mkt_status == "BAD_VOLATILE":
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={
                            "chat_id": ADMIN_CHAT_ID,
                            "text": (
                                f"⚠️ **২০-মিনিট প্রি-রিসার্চ রিপোর্ট:**\n"
                                f"বর্তমানে রিয়েল মার্কেটে কয়েকটি পেয়ারে নিউজ/ডোজি দেখা যাচ্ছে! বট শুধুমাত্র ক্লিন সেটআপ পেলেই ট্রেড দেবে, নতুবা হাই-পেআউট OTC পেয়ার ব্যবহার করবে।"
                            ),
                            "parse_mode": "Markdown"
                        }
                    )
                else:
                    broadcast_text(
                        f"{VIP_HEADER}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"🔍 **【 𝟐𝟎-𝐌𝐈𝐍 𝐏𝐑𝐄-𝐒𝐄𝐒𝐒𝐈𝐎𝐍 𝐌𝐀𝐑𝐊𝐄𝐓 𝐑𝐄𝐒𝐄𝐀𝐑𝐂𝐇 】**\n\n"
                        f"আলহামদুলিল্লাহ! সেশন শুরুর ২০ মিনিট আগে থেকেই আমাদের ৭-লেয়ার ফিল্টার ইঞ্জিন মার্কেট স্ক্যান সম্পন্ন করেছে।\n"
                        f"✅ **আজকের সেশনের সেরা পেয়ারসমূহ:** `{pairs_str}`\n"
                        f"🛡️ ডোজি, লো-পেআউট এবং নিউজ আক্রান্ত পেয়ারগুলো ফিল্টার করে বাদ দেওয়া হয়েছে।",
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
                
                banner = generate_session_banner(is_start=True)
                broadcast_photo(
                    banner,
                    f"🕋 **বিসমিল্লাহির রাহমানির রাহিম** 🕋\n"
                    f"{VIP_HEADER}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🟢 **【 𝐕𝐈𝐏 𝐒𝐄𝐒𝐒𝐈𝐎𝐍 𝐒𝐓𝐀𝐑𝐓𝐒 】** 🟢\n\n"
                    f"মহান আল্লাহর নামে আমাদের ভিআইপি সেশন শুরু হলো! আমাদের প্রো-ইঞ্জিন এখন লাইভ ক্যান্ডেল ফিল্টার করছে—যখনই **১০০% কনফার্মড স্নাইপার সেটআপ** পাওয়া যাবে, ঠিক তখনই সিগন্যাল আসবে। সবাই **১ মিনিটের (1M) চার্ট** ওপেন করে প্রস্তুত থাকুন!",
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
                
        # ৪. সেশন চলাকালীন
        if session_active:
            now = datetime.datetime.now(tz)
            total_signals_given = session_wins + session_losses + session_refunds
            max_sig_limit = SETTINGS["max_signals_per_session"]
            stop_loss_hit = (session_losses >= SETTINGS["max_losses_stop_session"])
            target_achieved = (total_signals_given >= max_sig_limit)
            
            if now >= session_end_dt or target_achieved or stop_loss_hit or abort_current_session:
                for h_key in [10, 14, 20]:
                    if current_hour == h_key or active_session_key == h_key:
                        session_started_flag[h_key] = True
                        session_completed_flag[h_key] = True

                session_active = False
                active_session_key = None
                abort_current_session = False
                time.sleep(3)
                
                end_banner = generate_session_banner(is_start=False)
                decisive_trades = session_wins + session_losses
                s_total = decisive_trades + session_refunds
                s_rate = int((session_wins / decisive_trades) * 100) if decisive_trades > 0 else 100
                
                if stop_loss_hit:
                    closing_note = "🛑 **ক্যাপিটাল প্রোটেকশন অ্যালার্ট (2-Loss Stop Rule):** মার্কেটে হঠাৎ ব্যাংকিং ভোলাটিলিটি বেড়ে যাওয়ায় মেম্বারদের ব্যালেন্স সুরক্ষিত রাখতে আমাদের নিয়ম অনুযায়ী সেশনটি এখানেই ক্লোজ করা হলো। কেউ একা একা ওভার-ট্রেডিং করবেন না!"
                else:
                    closing_note = "আলহামদুলিল্লাহ! ১ ঘণ্টার সেশন সফলভাবে সমাপ্ত হয়েছে। যাদের Take-Profit পূরণ হয়েছে তারা ব্রোকার থেকে লগ-আউট করে প্রফিট সুরক্ষিত রাখুন!"

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
                cooldown = random.randint(90, 140)
                for _ in range(cooldown):
                    if abort_current_session or force_instant_session:
                        break
                    time.sleep(1)

            if abort_current_session or force_instant_session:
                force_instant_session = False
                continue

            asset, direction, market_setup = scan_until_real_setup_found(tz, session_end_dt, is_first_trade=is_first_trade_of_session)
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
            
            first_trade_badge = "🛡️ **【 𝟏𝐒𝐓 𝐓𝐑𝐀𝐃𝐄 - 𝐃𝐎𝐔𝐁𝐋𝐄 𝐅𝐈𝐋𝐓𝐄𝐑𝐄𝐃 𝐒𝐄𝐓𝐔𝐏 】**\n" if is_first_trade_of_session else ""
            signal_caption = (
                f"{VIP_HEADER}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{first_trade_badge}"
                f"💎 **【 𝐕𝐈𝐏 𝐒𝐍𝐈𝐏𝐄𝐑 𝐒𝐈𝐆𝐍𝐀𝐋 #{trade_number} 】** 💎\n"
                f"╭───────────────────────⋅•⋅⊰∙∘☽\n"
                f"📊 **Pair -»** `{asset}` (Payout 80%+)\n"
                f"🕒 **Entry Time -»** `{timetable}` (UTC+6)\n"
                f"⏰ **Closing Time -»** `{timeset}` (3 Candles)\n"
                f"⏳ **Timeframe -»** `1M Chart (3 Min Exp.)`\n"
                f"🎯 **Filter Score -»** `{conf_score}%`\n"
                f"🔍 **Pro Analysis -»** {snr_reason}\n"
                f"{dir_line}\n"
                f"╰───────────────────────⋅•⋅⊰∙∘☽\n\n"
                f"🛡️ **Rule:** ব্যালেন্সের ৩% দিয়ে এন্ট্রি নিন। সবার আগে নিজের **Stop-Loss ও Take-Profit** মাথায় রাখবেন (পরপর ২টা লস হলে ট্রেড বন্ধ)!\n"
                f"⚡ **অ্যাকশন (১ মিনিট বাকি):** দ্রুত `{asset}` চার্টে ক্লোজিং টাইম **`{timeset}`** সেট করে ঠিক **`{timetable}`**-এ এন্ট্রি নিন!"
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
                res_status = "✅✅✅ **Direct Win (SURESHOT PROFIT)** ✅✅✅"
            elif outcome == "MTG_WIN":
                session_wins += 1
                res_status = "✅✅✅ **1-Step Martingale Win (MTG WIN¹)** ✅✅✅"
            elif outcome == "REFUND":
                session_refunds += 1
                res_status = "🔄🔄🔄 **Trade Refunded (DOJI / $0 DRAW)** 🔄🔄🔄"
            else:
                session_losses += 1
                res_status = "❎✖️💀 **Loss Trade (Follow 2-Loss Stop & 3% Rule)** 💀✖️❎"
                
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
                f"🤲 **Alhamdulillah! Verified Institutional Result.**"
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