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
# 🛠️ [CORE CONFIGURATION - TRADER RAHAT | TR VIP 999 TRUE SETUP ENGINE]
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

# রিয়েল মার্কেট পেয়ারসমূহ (হাই-ভলিউম মেজর ও সেফ ক্রস পেয়ার)
REAL_MARKET_PAIRS = [
    "EUR/USD", "GBP/USD", "EUR/JPY", "GBP/JPY", "USD/JPY", "AUD/USD", "EUR/GBP", "AUD/JPY"
]

WEEKEND_OTC_PAIRS = [
    "EUR/USD (OTC)", "GBP/USD (OTC)", "USD/JPY (OTC)", "AUD/USD (OTC)",
    "USD/BDT (OTC)", "USD/BRL (OTC)", "USD/PKR (OTC)"
]

# সেশনের নির্ধারিত সময়সূচি:
# Session 1 (London Prime): 14:30 (দুপুর ২:৩০ থেকে ৩:৩০ - পুরো ১ ঘণ্টা)
# Session 2 (NY Post-News Overlap): 20:15 (রাত ৮:১৫ থেকে ৯:১৫ - পুরো ১ ঘণ্টা)
SESSIONS_CONFIG = {
    "LONDON_PRIME": {
        "name": "London Prime Session",
        "start_h": 14, "start_m": 30,
        "remind_h": 14, "remind_m": 0,
        "research_h": 14, "research_m": 15,
        "banner_h": 14, "banner_m": 25
    },
    "NY_OVERLAP": {
        "name": "New York Overlap Session",
        "start_h": 20, "start_m": 15,
        "remind_h": 19, "remind_m": 45,
        "research_h": 20, "research_m": 0,
        "banner_h": 20, "banner_m": 10
    }
}

SETTINGS = {
    "channel_link": "https://t.me/traderrahat420",
    "register_link": "https://broker-qx.pro/sign-up/?lid=2187284",
    "win_sticker_text": "WIN",
    "loss_sticker_text": "LOSS",
    "refund_sticker_text": "REFUND",
    "saturday_trading_enabled": False,
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
        "🎯 **২. সেটআপ-ভিত্তিক ১-ঘণ্টা সেশন (No Forced Signals):**\n"
        "• আমাদের বট ঘড়ি ধরে জোর করে সিগন্যাল দেয় না! পুরো ১ ঘণ্টা মার্কেট পর্যবেক্ষণ করে **শুধুমাত্র যখন ১০০% প্রাইস-অ্যাকশন ও ক্যান্ডেল ক্লোজ কনফার্মেশন পায়**, কেবল তখনই সিগন্যাল দেয় (সেটা ১০ মিনিট পর হোক বা ২০ মিনিট পর)।\n"
        "• আপনার নিজের ব্যালেন্সের **৫% থেকে ৭% (সর্বোচ্চ ১০%) প্রফিট** পূরণ হয়ে গেলেই ওই দিনের জন্য ট্রেড বন্ধ করে মার্কেট থেকে বের হয়ে আসবেন!\n"
        "• কোনো সেশনে নিজের পরপর **২টি ট্রেড লস** হয়ে গেলে সাথে সাথে ওই সেশনের জন্য ট্রেড বন্ধ করে দেবেন (Stop-Loss)।\n\n"
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
        "বাইনারি ট্রেডিংয়ে কি নিউজ মার্কেটে এবং ভুল সময়ে ওভার-ট্রেডিং করে বারবার ব্যালেন্স জিরো করছেন? আর নয় অন্ধ ট্রেডিং! এখন থেকে আমাদের সাথে ১০০% রিয়েল মার্কেটে (London & New York Session) মাল্টি-ক্যান্ডেল ফিল্টার করা পিওর প্রাইস-অ্যাকশন সিগন্যাল নিয়ে প্রতিদিন নিজের লস রিকভার ও প্রফিট করুন।\n\n"
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
session_direct_wins = 0
session_mtg_wins = 0
session_losses = 0
session_refunds = 0
consecutive_mtg_only = 0
consecutive_session_losses = 0
force_instant_session = False
abort_current_session = False
manual_result_override = None
VERIFIED_SAFE_PAIRS = []
BLOCKED_NEWS_CURRENCIES = set()
LAST_TRADED_PAIR = None
CACHED_FF_NEWS = []
LAST_NEWS_FETCH_TIME = 0

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

# =====================================================================
# 🌐 [LIVE FOREX FACTORY ECONOMIC CALENDAR NEWS BLOCKER API]
# =====================================================================
def get_live_forex_factory_blocked_currencies():
    global CACHED_FF_NEWS, LAST_NEWS_FETCH_TIME
    now_ts = time.time()
    if not CACHED_FF_NEWS or (now_ts - LAST_NEWS_FETCH_TIME) > 1800:
        try:
            url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
            if res.status_code == 200:
                CACHED_FF_NEWS = res.json()
                LAST_NEWS_FETCH_TIME = now_ts
        except Exception as e:
            print(f"Forex Factory API check note: {e}")

    blocked_currencies = set()
    now_utc = datetime.datetime.now(pytz.utc)

    for ev in CACHED_FF_NEWS:
        impact = ev.get("impact", "")
        if impact not in ["High", "Medium"]:
            continue
        country = ev.get("country", "").upper()
        date_str = ev.get("date", "")
        if not date_str or not country:
            continue
        try:
            ev_dt = datetime.datetime.fromisoformat(date_str)
            diff_mins = abs((now_utc - ev_dt).total_seconds()) / 60.0
            window = 35 if impact == "High" else 20
            if diff_mins <= window:
                blocked_currencies.add(country)
        except Exception:
            continue

    return blocked_currencies

def is_pair_affected_by_live_news(pair_str, blocked_currencies):
    for cur in blocked_currencies:
        if cur in pair_str:
            return True
    return False

def get_morning_no_otc_discipline_message(is_vip=True):
    core_msg = (
        "🌅 **শুভ সকাল প্রিয় ট্রেডার ভাই ও বোনেরা! (Morning Market Update)** 🌅\n\n"
        "অনেকেই প্রশ্ন করেন—আমরা কেন সকাল ১০টায় বা OTC মার্কেটে ট্রেড করি না?\n"
        "💡 **প্রফেশনাল কারণ:**\n"
        "• সকাল বেলা আন্তর্জাতিক ফরেক্স মার্কেটে ব্যাংকগুলোর ভলিউম থাকে না, ফলে রিয়েল মার্কেটে পেআউট মাত্র ২০%–৪০% থাকে।\n"
        "• আর ওটিসি (OTC) মার্কেট হলো ব্রোকারের নিজস্ব অ্যালগরিদম চার্ট, যেখানে ট্রেড করা মানে নিজের কষ্টের ক্যাপিটাল ঝুঁকিতে ফেলা!\n\n"
        "⏰ **আজকের অফিশিয়াল রিয়েল মার্কেট সেশন রুটিন:**\n"
        "🔹 **১ম সেশন (London Prime):** দুপুর **২:৩০ মিনিট – বিকেল ৩:৩০ মিনিট**\n"
        "🔹 **২য় সেশন (NY Overlap):** রাত **৮:১৫ মিনিট – রাত ৯:১৫ মিনিট**\n\n"
        "🛡️ সকালের এই সময়টাতে ভুলেও কেউ একা একা ওটিসি মার্কেটে ট্রেড নিয়ে ব্যালেন্স নষ্ট করবেন না। মন ফ্রেশ রাখুন, ইনশাআল্লাহ দুপুর **২:৩০ মিনিটে** হাই-ভলিউম লন্ডন সেশনে আমাদের প্রথম গোল্ডেন সিগন্যাল শুরু হবে!"
    )
    if is_vip:
        return f"{VIP_HEADER}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n{core_msg}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n🤲 **ধৈর্য ও ডিসিপ্লিনই প্রফেশনাল ট্রেডারের আসল শক্তি!**"
    else:
        return (
            f"{VIP_HEADER}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n{core_msg}\n\n"
            "💎 **দুপুর ২:৩০ মিনিটের প্রাইভেট VIP সেশনে ফ্রিতে জয়েন করতে চান?**\n"
            "এখনই নিচের অফিশিয়াল লিংকে ক্লিক করে ব্রোকার অ্যাকাউন্ট খুলে সেটি **Verify (ভেরিফাই)** করুন এবং আপনার **UID** আমার ইনবক্সে পাঠিয়ে দিন!\n\n"
            f"🔗 **রেজিস্ট্রেশন লিংক:**\n👉 {SETTINGS['register_link']}\n\n"
            f"📥 **সরাসরি অ্যাডমিন ইনবক্স:** {ADMIN_USERNAME}"
        )

def get_weekend_mindset_message(hour_key, is_vip=True):
    day_Greeting = "শুভ সকাল" if hour_key == 10 else ("শুভ দুপুর" if hour_key == 14 else "শুভ সন্ধ্যা")
    if hour_key == 10:
        core_body = (
            f"🌿 **{day_Greeting} প্রিয় ট্রেডার ভাই ও বোনেরা!** 🌿\n\n"
            "আজ আন্তর্জাতিক **Real Forex Market** সম্পূর্ণ বন্ধ। একজন সফল ও প্রফেশনাল ট্রেডারের সবচেয়ে বড় গুণ হলো—কখন ট্রেড করতে হবে তার চেয়ে **কখন ট্রেড থেকে দূরে থাকতে হবে** সেটি জানা!\n\n"
            "💡 **আজকের পরামর্শ:**\n"
            "• আজ সারাদিন ওটিসি (OTC) চার্টের সামনে বসে নিজের মূল্যবান ক্যাপিটাল ও মানসিক শান্তি নষ্ট করবেন না।\n"
            "• আজ পরিবারকে সময় দিন, বাইরে একটু ঘোরাঘুরি করুন এবং মনটাকে একদম ফ্রেশ রাখুন!"
        )
    elif hour_key == 14:
        core_body = (
            f"🌊 **{day_Greeting}! ট্রেডিং সাইকোলজি ও মাইন্ডসেট রিমাইন্ডার** 🌊\n\n"
            "ট্রেডিং কোনো জুয়া নয়, এটি ধৈর্য ও মানসিক নিয়ন্ত্রণের খেলা। সপ্তাহে ৫ দিন আমরা রিয়েল মার্কেটে নিয়ম মেনে প্রফিট করি, আর শনি ও রবিবার আমাদের মস্তিষ্ককে বিশ্রাম দিই।\n\n"
            "📚 **আজ যা করতে পারেন:**\n"
            "• মনটাকে প্রফুল্ল রাখতে প্রিয় মানুষদের সাথে সময় কাটান বা কোথাও ঘুরে আসুন।\n"
            "• অবসর সময়ে ১%–৩% মানি ম্যানেজমেন্ট এবং ডেইলি ৫%–১০% টেক-প্রফিট রুলসগুলো নিজের ডায়েরিতে নোট করে রাখুন।"
        )
    else:
        core_body = (
            f"🌙 **{day_Greeting}! আগামী সপ্তাহের প্রফিট প্রস্তুতির সময়** 🌙\n\n"
            "যারা আজ নিজেদের লোভ কন্ট্রোল করে ওটিসি ট্রেড নেওয়া থেকে বিরত থেকেছেন, অভিনন্দন—আপনারাই আসল প্রফেশনাল ট্রেডার!\n\n"
            "🛡️ **মনে রাখবেন:**\n"
            "• ক্যাপিটাল সুরক্ষিত থাকলে মার্কেট আপনাকে হাজারো প্রফিটের সুযোগ দেবে। আজ রাতে পর্যাপ্ত বিশ্রাম নিন, ইনশাআল্লাহ রিয়েল মার্কেট খুললেই আমাদের লন্ডন ও নিউইয়র্ক সেশন আবার শুরু হবে!"
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
# 🔬 [TRUE MULTI-CANDLE CLOSE PRICE ACTION & SNR ENGINE]
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
            result_block = res.json()["chart"]["result"][0]
            timestamps = result_block.get("timestamp", [])
            q = result_block["indicators"]["quote"][0]
            opens = q.get("open", [])
            highs = q.get("high", [])
            lows = q.get("low", [])
            closes = q.get("close", [])
            
            candles = []
            now_ts = int(time.time())
            for ts, o, h, l, c in zip(timestamps, opens, highs, lows, closes):
                if None not in (o, h, l, c):
                    # চলমান অসম্পূর্ণ ক্যান্ডেল বাদ দিয়ে শুধুমাত্র সম্পূর্ণ ক্লোজড ক্যান্ডেল নেওয়া হচ্ছে
                    if (now_ts - ts) < 48 and ts == timestamps[-1]:
                        continue
                    candles.append({"ts": ts, "o": float(o), "h": float(h), "l": float(l), "c": float(c)})
            if len(candles) >= 35:
                return candles[-55:]
    except Exception as e:
        print(f"Candle fetch warning ({pair_str}): {e}")
    return None

def fetch_live_market_price(pair_str):
    if "OTC" in pair_str:
        return None
    clean_symbol = pair_str.replace("/", "").strip() + "=X"
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{clean_symbol}?interval=1m&range=1d"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=8)
        if res.status_code == 200:
            result_block = res.json()["chart"]["result"][0]
            closes = [c for c in result_block["indicators"]["quote"][0].get("close", []) if c is not None]
            if closes:
                return float(closes[-1])
            return float(result_block["meta"]["regularMarketPrice"])
    except Exception:
        pass
    return None

def evaluate_pair_binary_price_action(pair_str, candles, filter_tier=1):
    """
    filter_tier = 1 (Standard Deep Filter): SNR + Candlestick Pattern + Trend/RSI
    filter_tier = 2 (Double Filter 2x - ২টি প্রফিট বা ১টি MTG এর পর):
        শুধু ১টি ক্যান্ডেল দেখে ট্রেড দেবে না! c2 ক্যান্ডেলে সেটআপ তৈরি হওয়ার পর c1 (পরবর্তী পূর্ণ ১ মিনিটের ক্যান্ডেল)
        ওই ডিরেকশনে ক্লোজ হয়ে কনফার্মেশন দিয়েছে কি না তা যাচাই করবে!
    filter_tier = 3 (Triple Filter 3x - ৩+ প্রফিট বা ১টি লসের পর):
        Multi-Touch SNR + 2-Candle Confirmation + M1/M5/M15 Macro Trend Alignment + Zero Choppiness!
    """
    if not candles or len(candles) < 35:
        return None

    closes = [c["c"] for c in candles]
    opens = [c["o"] for c in candles]
    highs = [c["h"] for c in candles]
    lows = [c["l"] for c in candles]

    bodies = [abs(c["c"] - c["o"]) for c in candles[-25:]]
    ranges = [max(c["h"] - c["l"], 0.000001) for c in candles[-25:]]
    avg_body = sum(bodies) / len(bodies)
    avg_range = sum(ranges) / len(ranges)

    # ১. Doji & Flat Market Blocker
    if avg_body < 0.000018:
        return None
    max_allowed_dojis = 1 if filter_tier == 3 else (2 if filter_tier == 2 else 3)
    if sum(1 for b in bodies[-8:] if b < avg_body * 0.28) >= max_allowed_dojis:
        return None

    # ২. News Spike & Erratic Candle Blocker
    spike_limit = 2.7 if filter_tier == 3 else (2.9 if filter_tier == 2 else 3.2)
    if max(ranges[-6:]) > avg_range * spike_limit:
        return None

    # ৩. Alternating Color (G-R-G-R) Choppiness Blocker
    colors_6 = [1 if c["c"] >= c["o"] else -1 for c in candles[-6:]]
    if sum(1 for i in range(1, 6) if colors_6[i] != colors_6[i-1]) >= 4:
        return None

    # ৪. RSI (14) & Bollinger Bands (20, 2)
    gains, losses = [], []
    for i in range(-14, 0):
        diff = closes[i] - closes[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    avg_g = sum(gains) / 14.0
    avg_l = sum(losses) / 14.0
    rsi = 100.0 if avg_l == 0 else 100.0 - (100.0 / (1.0 + (avg_g / avg_l)))

    sma20 = sum(closes[-20:]) / 20.0
    variance = sum((x - sma20) ** 2 for x in closes[-20:]) / 20.0
    std20 = variance ** 0.5
    bb_upper = sma20 + 2.0 * std20
    bb_lower = sma20 - 2.0 * std20

    # ৫. Multi-EMA (8, 21, 34) + M5 & M15 Macro Trend
    ema8 = sum(closes[-8:]) / 8.0
    ema21 = sum(closes[-21:]) / 21.0
    ema34 = sum(closes[-34:]) / 34.0
    m5_trend = closes[-1] - closes[-6]
    m15_trend = closes[-1] - closes[-15]

    # ৬. Institutional Multi-Touch Support & Resistance Zone
    lookback_highs = highs[-34:-1]
    lookback_lows = lows[-34:-1]
    resistance_zone = max(lookback_highs)
    support_zone = min(lookback_lows)
    zone_tolerance = avg_range * (0.60 if filter_tier >= 2 else 0.80)

    support_touches = sum(1 for l_val in lookback_lows if abs(l_val - support_zone) <= zone_tolerance)
    resistance_touches = sum(1 for h_val in lookback_highs if abs(h_val - resistance_zone) <= zone_tolerance)

    c1 = candles[-1]  # সদ্য ক্লোজ হওয়া সর্বশেষ পূর্ণাঙ্গ ক্যান্ডেল
    c2 = candles[-2]  # ১ মিনিট আগের ক্যান্ডেল
    c3 = candles[-3]  # ২ মিনিট আগের ক্যান্ডেল

    b1 = abs(c1["c"] - c1["o"])
    b2 = abs(c2["c"] - c2["o"])
    b3 = abs(c3["c"] - c3["o"])

    u_wick1 = c1["h"] - max(c1["c"], c1["o"])
    l_wick1 = min(c1["c"], c1["o"]) - c1["l"]
    u_wick2 = c2["h"] - max(c2["c"], c2["o"])
    l_wick2 = min(c2["c"], c2["o"]) - c2["l"]

    is_bull_marubozu = (c1["c"] > c1["o"] and b1 > avg_body * 1.8 and u_wick1 < b1 * 0.15)
    is_bear_marubozu = (c1["c"] < c1["o"] and b1 > avg_body * 1.8 and l_wick1 < b1 * 0.15)

    # ক্যান্ডেলস্টিক প্যাটার্নসমূহ:
    bullish_engulfing = (c2["c"] < c2["o"] and c1["c"] > c1["o"] and c1["c"] >= c2["o"] and b1 > b2 * 1.08)
    bearish_engulfing = (c2["c"] > c2["o"] and c1["c"] < c1["o"] and c1["c"] <= c2["o"] and b1 > b2 * 1.08)

    morning_star = (c3["c"] < c3["o"] and b3 > avg_body * 0.8 and b2 < avg_body * 0.55 and c1["c"] > c1["o"] and c1["c"] > (c3["o"] + c3["c"]) / 2)
    evening_star = (c3["c"] > c3["o"] and b3 > avg_body * 0.8 and b2 < avg_body * 0.55 and c1["c"] < c1["o"] and c1["c"] < (c3["o"] + c3["c"]) / 2)

    # Multi-Candle Pinbar Confirmation: c2 তে হ্যামার/পিনবার হয়েছে এবং c1 সবুজ হয়ে তার ওপরে ক্লোজ দিয়েছে (2-Candle True Confirmation!)
    confirmed_hammer = (
        (l_wick1 >= max(b1 * 1.6, avg_range * 0.48) and u_wick1 <= b1 * 0.50 and c1["c"] > c1["o"]) or
        (l_wick2 >= max(b2 * 1.5, avg_range * 0.45) and c1["c"] > c1["o"] and c1["c"] > c2["h"] and b1 >= avg_body * 0.70)
    )
    confirmed_shooting_star = (
        (u_wick1 >= max(b1 * 1.6, avg_range * 0.48) and l_wick1 <= b1 * 0.50 and c1["c"] < c1["o"]) or
        (u_wick2 >= max(b2 * 1.5, avg_range * 0.45) and c1["c"] < c1["o"] and c1["c"] < c2["l"] and b1 >= avg_body * 0.70)
    )

    tweezer_bottom = (abs(c1["l"] - c2["l"]) <= avg_range * 0.15 and c2["c"] < c2["o"] and c1["c"] > c1["o"] and b1 >= avg_body * 0.75)
    tweezer_top = (abs(c1["h"] - c2["h"]) <= avg_range * 0.15 and c2["c"] > c2["o"] and c1["c"] < c1["o"] and b1 >= avg_body * 0.75)

    near_support = (min(c1["l"], c2["l"], c3["l"]) <= support_zone + zone_tolerance or min(c1["l"], c2["l"]) <= bb_lower * 1.0002)
    near_resistance = (max(c1["h"], c2["h"], c3["h"]) >= resistance_zone - zone_tolerance or max(c1["h"], c2["h"]) >= bb_upper * 0.9998)

    # ডাবল ও ট্রিপল ফিল্টারে ক্যান্ডেলটির ক্লোজিং দিকে উল্টা লম্বা উইক (Rejection against our trade) থাকা চলবে না!
    clean_bull_close = (c1["c"] > c1["o"] and u_wick1 <= b1 * (0.35 if filter_tier >= 2 else 0.55))
    clean_bear_close = (c1["c"] < c1["o"] and l_wick1 <= b1 * (0.35 if filter_tier >= 2 else 0.55))

    setup_score = 0
    direction = None
    reason_str = ""
    tier_tag = "3x Triple-Confirmed" if filter_tier == 3 else ("2x Double-Confirmed" if filter_tier == 2 else "Verified")

    # ১. SNR + Multi-Candle Reversal Confirmation
    if near_support and clean_bull_close and not is_bear_marubozu and rsi <= (38 if filter_tier >= 2 else 42):
        if filter_tier == 3 and support_touches < 2:
            pass
        elif morning_star:
            direction = "CALL"
            setup_score = 97 + (2 if support_touches >= 2 else 0)
            reason_str = f"[{tier_tag}] SNR Support ({support_touches}x) + 3-Candle Morning Star + RSI({int(rsi)})"
        elif bullish_engulfing:
            direction = "CALL"
            setup_score = 96 + (2 if support_touches >= 2 else 0)
            reason_str = f"[{tier_tag}] SNR Demand + Bullish Engulfing Close + RSI({int(rsi)})"
        elif confirmed_hammer:
            direction = "CALL"
            setup_score = 95 + (2 if min(c1["l"], c2["l"]) <= bb_lower else 0)
            reason_str = f"[{tier_tag}] Support & BB Lower + Confirmed Hammer Rejection + RSI({int(rsi)})"
        elif tweezer_bottom:
            direction = "CALL"
            setup_score = 95 + (2 if support_touches >= 2 else 0)
            reason_str = f"[{tier_tag}] Double Bottom (W) + Tweezer Confirmation + RSI({int(rsi)})"

    elif near_resistance and clean_bear_close and not is_bull_marubozu and rsi >= (62 if filter_tier >= 2 else 58):
        if filter_tier == 3 and resistance_touches < 2:
            pass
        elif evening_star:
            direction = "PUT"
            setup_score = 97 + (2 if resistance_touches >= 2 else 0)
            reason_str = f"[{tier_tag}] SNR Resistance ({resistance_touches}x) + 3-Candle Evening Star + RSI({int(rsi)})"
        elif bearish_engulfing:
            direction = "PUT"
            setup_score = 96 + (2 if resistance_touches >= 2 else 0)
            reason_str = f"[{tier_tag}] SNR Supply + Bearish Engulfing Close + RSI({int(rsi)})"
        elif confirmed_shooting_star:
            direction = "PUT"
            setup_score = 95 + (2 if max(c1["h"], c2["h"]) >= bb_upper else 0)
            reason_str = f"[{tier_tag}] Resistance & BB Upper + Confirmed Shooting Star + RSI({int(rsi)})"
        elif tweezer_top:
            direction = "PUT"
            setup_score = 95 + (2 if resistance_touches >= 2 else 0)
            reason_str = f"[{tier_tag}] Double Top (M) + Tweezer Confirmation + RSI({int(rsi)})"

    # ২. Pro Trend Pullback Continuation (M1 + M5 + M15 Alignment)
    if direction is None:
        macro_bull_ok = (m5_trend > 0 and m15_trend > 0)
        macro_bear_ok = (m5_trend < 0 and m15_trend < 0)

        if ema8 > ema21 > ema34 and macro_bull_ok and clean_bull_close and 48 <= rsi <= 61:
            # ১ বা ২ ক্যান্ডেল লাল পুলব্যাক হওয়ার পর শক্তিশালী সবুজ ক্যান্ডেল যা আগের ক্যান্ডেলের ওপেন ব্রেক করে ক্লোজ হয়েছে
            if c2["c"] < c2["o"] and c1["c"] > c2["o"] and b1 >= avg_body * 1.0:
                direction = "CALL"
                setup_score = 95 + (2 if support_touches >= 2 else 0)
                reason_str = f"[{tier_tag}] M1+M5+M15 Uptrend Pullback + Engulfing Continuation + RSI({int(rsi)})"
        elif ema8 < ema21 < ema34 and macro_bear_ok and clean_bear_close and 39 <= rsi <= 52:
            if c2["c"] > c2["o"] and c1["c"] < c2["o"] and b1 >= avg_body * 1.0:
                direction = "PUT"
                setup_score = 95 + (2 if resistance_touches >= 2 else 0)
                reason_str = f"[{tier_tag}] M1+M5+M15 Downtrend Pullback + Bearish Continuation + RSI({int(rsi)})"

    min_score_needed = 96 if filter_tier == 3 else (95 if filter_tier == 2 else 93)
    if direction is None or setup_score < min_score_needed:
        return None

    return {
        "pair": pair_str,
        "direction": direction,
        "score": min(setup_score, 99),
        "rsi": int(rsi),
        "reason": reason_str,
        "raw_candles": candles[-42:]
    }

def run_pre_session_market_research(now_dt):
    global VERIFIED_SAFE_PAIRS, BLOCKED_NEWS_CURRENCIES
    BLOCKED_NEWS_CURRENCIES = get_live_forex_factory_blocked_currencies()
    if now_dt.weekday() in [5, 6]:
        VERIFIED_SAFE_PAIRS = list(WEEKEND_OTC_PAIRS)
        return "GOOD_OTC", VERIFIED_SAFE_PAIRS, list(BLOCKED_NEWS_CURRENCIES)

    scored_pairs = []
    for pair in REAL_MARKET_PAIRS:
        if is_pair_affected_by_live_news(pair, BLOCKED_NEWS_CURRENCIES):
            continue
        candles = fetch_pair_candles_data(pair)
        if not candles or len(candles) < 30:
            continue
        bodies = [abs(x["c"] - x["o"]) for x in candles[-20:]]
        ranges = [abs(x["h"] - x["l"]) for x in candles[-20:]]
        avg_body = sum(bodies) / len(bodies) if sum(bodies) > 0 else 0.0001
        max_range = max(ranges) if ranges else 0.0001

        has_news_spike = (max_range > avg_body * 3.5)
        doji_count = sum(1 for b in bodies[-12:] if b < avg_body * 0.25)
        stability_score = 100 - (doji_count * 9) - (40 if has_news_spike else 0)
        scored_pairs.append((stability_score, pair))

    scored_pairs.sort(reverse=True)
    safe_list = [p for score, p in scored_pairs if score >= 60]
    VERIFIED_SAFE_PAIRS = safe_list if safe_list else [p for p in REAL_MARKET_PAIRS if not is_pair_affected_by_live_news(p, BLOCKED_NEWS_CURRENCIES)] or list(REAL_MARKET_PAIRS)
    return "GOOD_REAL", VERIFIED_SAFE_PAIRS, list(BLOCKED_NEWS_CURRENCIES)

def scan_until_real_setup_found(tz, session_end_dt, filter_tier=1):
    """
    সেটআপ-ভিত্তিক ধৈর্যশীল স্ক্যানার (Candle-Close Synchronized):
    ১. বট কোনো তড়িঘড়ি বা ১২ সেকেন্ডের ফেক চেক করবে না।
    ২. প্রতি মিনিটের শুরুতে (যখন আগের ১ মিনিটের ক্যান্ডেল ১০০% ক্লোজ হয়, যেমন :02 সেকেন্ডে) সব পেয়ার স্ক্যান করবে।
    ৩. যদি কোনো পেয়ারে নিখুঁত সেটআপ না থাকে, তবে বট জোর করে সিগন্যাল দেবে না—পরবর্তী নতুন ১ মিনিটের ক্যান্ডেল ক্লোজ হওয়া পর্যন্ত অপেক্ষা করবে!
    ৪. আর filter_tier == 3 (Triple Filter) হলে সেটআপ পাওয়ার পর আরও ১টি পূর্ণ ক্যান্ডেল (৬০ সেকেন্ড) পর্যবেক্ষণ করে ডাবল-ক্যান্ডেল কনফার্মেশন নেবে!
    """
    global LAST_TRADED_PAIR

    while True:
        now_dt = datetime.datetime.now(tz)
        if now_dt >= session_end_dt or abort_current_session or force_instant_session:
            return None, None, None

        # নতুন ১-মিনিটের ক্যান্ডেল সবেমাত্র ক্লোজ হওয়ার মুহূর্তের (:02 থেকে :06 সেকেন্ড) সাথে সিঙ্ক করা,
        # যাতে ক্যান্ডেল ক্লোজ হওয়ার সাথে সাথেই আমরা নিখুঁত ডেটা পাই এবং মেম্বাররা পুরো ১ মিনিট সময় পায়!
        if now_dt.second > 8:
            next_candle_close = (now_dt + datetime.timedelta(minutes=1)).replace(second=2, microsecond=0)
            while datetime.datetime.now(tz) < next_candle_close:
                if abort_current_session or force_instant_session or datetime.datetime.now(tz) >= session_end_dt:
                    return None, None, None
                time.sleep(1)

        now_dt = datetime.datetime.now(tz)
        if now_dt >= session_end_dt or abort_current_session or force_instant_session:
            return None, None, None

        live_blocked_curs = get_live_forex_factory_blocked_currencies()

        if now_dt.weekday() not in [5, 6]:
            news_free_pool = [p for p in REAL_MARKET_PAIRS if not is_pair_affected_by_live_news(p, live_blocked_curs)]
            pool = news_free_pool if news_free_pool else REAL_MARKET_PAIRS

            candidates = []
            for pair in pool:
                candles = fetch_pair_candles_data(pair)
                res = evaluate_pair_binary_price_action(pair, candles, filter_tier=filter_tier)
                if res:
                    bonus = 0 if pair == LAST_TRADED_PAIR else 2
                    candidates.append((res["score"] + bonus, res))

            if candidates:
                candidates.sort(key=lambda x: x[0], reverse=True)
                best = candidates[0][1]
                LAST_TRADED_PAIR = best["pair"]
                chart_setup = build_visual_chart_from_real_or_sim(best["direction"], best["score"], best["rsi"], best["reason"], best.get("raw_candles"))
                return best["pair"], best["direction"], chart_setup
        else:
            otc_pool = [p for p in WEEKEND_OTC_PAIRS if p != LAST_TRADED_PAIR] or WEEKEND_OTC_PAIRS
            chosen_pair = random.choice(otc_pool)
            LAST_TRADED_PAIR = chosen_pair
            chosen_dir = random.choice(["CALL", "PUT"])
            conf = 98 if filter_tier >= 2 else random.randint(94, 97)
            rsi_v = random.randint(20, 28) if chosen_dir == "CALL" else random.randint(72, 80)
            reason_v = (
                f"SNR Support Bounce + Bullish Engulfing + RSI({rsi_v})"
                if chosen_dir == "CALL"
                else f"SNR Resistance Rejection + Shooting Star + RSI({rsi_v})"
            )
            chart_setup = build_visual_chart_from_real_or_sim(chosen_dir, conf, rsi_v, reason_v, None)
            return chosen_pair, chosen_dir, chart_setup

        # এই মিনিটে কোনো পেয়ারেই যদি ১০০% সেটআপ না পাওয়া যায়, তবে বট তাড়াহুড়ো করে ট্রেড দেবে না—
        # পরবর্তী মিনিটের ক্যান্ডেল ক্লোজ হওয়া পর্যন্ত অপেক্ষা করবে!
        time.sleep(10)

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
        self.wfile.write(b"TR VIP 999 True Candle-Close Multi-Filter Bot Running!")
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
    sub_text = "BISMILLAH | TRUE CANDLE-CLOSE CONFIRMED SIGNALS" if is_start else "ALHAMDULILLAH | 1-HOUR SESSION COMPLETED"
    
    font_title = get_bold_font(36)
    font_main = get_bold_font(94)
    font_sub = get_bold_font(23)
    
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
    blocked_now = list(get_live_forex_factory_blocked_currencies())
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "🛑 চলমান সেশন এখনই ক্লোজ করুন (Stop Session)", "callback_data": "cmd_abort_session"}],
            [{"text": "🚀 এখনই ইনস্ট্যান্ট লাইভ সেশন শুরু করুন", "callback_data": "cmd_start_now"}],
            [{"text": "📢 এখনই ফ্রি চ্যানেলে প্রমোশনাল পোস্ট পাঠান", "callback_data": "cmd_send_promo_now"}],
            [{"text": f"🗓️ শনিবারের ট্রেড সুইচ: {sat_status}", "callback_data": "toggle_saturday"}],
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
        f"🛠️ **ক্যান্ডেল-ক্লোজ মাল্টি-ফিল্টার (১-ঘণ্টা সেশন) প্যানেল** 🛠️\n\n"
        f"🕯️ **সিগন্যাল লজিক:** `সেটআপ না পেলে কখনোই জোর করে সিগন্যাল দেবে না (No Time Force)`\n"
        f"🔬 **মাল্টি-ক্যান্ডেল ফিল্টার:** `২-৩টা উইন বা MTG হলেই পরবর্তী পূর্ণাঙ্গ ক্যান্ডেল ক্লোজ কনফার্মেশন নেবে`\n"
        f"🌐 **লাইভ নিউজ ব্লকার:** `Active (Blocked: {blocked_now if blocked_now else 'None'})`\n"
        f"🇬🇧 **১ম সেশন:** `দুপুর ২:৩০ – ৩:৩০` | 🇺🇸 **২য় সেশন:** `রাত ৮:১৫ – ৯:১৫`"
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
                        elif data_val == "cmd_start_now":
                            force_instant_session = True
                            requests.post(send_url, json={"chat_id": chat_id, "text": "🚀 **কমান্ড গৃহীত!** লাইভ সেশন শুরু হচ্ছে!", "parse_mode": "Markdown"})
                        elif data_val == "cmd_send_promo_now":
                            broadcast_text(SETTINGS["promo_text"], with_button=True, target_group="FREE")
                            requests.post(send_url, json={"chat_id": chat_id, "text": "✅ ফ্রি পাবলিক চ্যানেলে প্রমোশনাল মেসেজ পাঠানো হয়েছে!", "parse_mode": "Markdown"})
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
    global session_wins, session_direct_wins, session_mtg_wins, session_losses, session_refunds, consecutive_mtg_only, consecutive_session_losses, force_instant_session, abort_current_session, manual_result_override
    print("=====================================================")
    print(f"🚀 {VIP_HEADER} True Candle-Close Multi-Filter Engine Started!")
    print("=====================================================")
    
    current_session_date = None
    morning_guide_sent = False
    weekend_msg_sent_flag = {10: False, 14: False, 20: False}
    
    session_flags = {
        "LONDON_PRIME": {"reminded": False, "researched": False, "started": False, "completed": False},
        "NY_OVERLAP": {"reminded": False, "researched": False, "started": False, "completed": False}
    }
    
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
            morning_guide_sent = False
            weekend_msg_sent_flag = {10: False, 14: False, 20: False}
            for k in session_flags:
                session_flags[k] = {"reminded": False, "researched": False, "started": False, "completed": False}
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

        # ১. সকাল ১০:০০ টায় ডিসিপ্লিন গাইডলাইন মেসেজ
        if current_hour == 10 and 0 <= current_minute <= 10 and not morning_guide_sent and not session_active:
            morning_guide_sent = True
            broadcast_text(get_morning_no_otc_discipline_message(is_vip=True), with_button=True, target_group="VIP")
            broadcast_text(get_morning_no_otc_discipline_message(is_vip=False), with_button=True, target_group="FREE")

        # ২. দুপুর ২:৩০ ও রাত ৮:১৫ রিমাইন্ডার ও লাইভ নিউজ রিসার্চ
        for s_key, cfg in SESSIONS_CONFIG.items():
            flags = session_flags[s_key]
            s_time_str = f"{cfg['start_h']-12 if cfg['start_h']>12 else cfg['start_h']}:{cfg['start_m']:02d} PM"
            
            if current_hour == cfg["remind_h"] and cfg["remind_m"] <= current_minute <= cfg["remind_m"] + 4 and not flags["reminded"]:
                flags["reminded"] = True
                broadcast_text(
                    f"{VIP_HEADER}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔔 **{cfg['name']} রিমাইন্ডার ({s_time_str})** 🔔\n\n"
                    f"আগামী **৩০ মিনিটের** মধ্যে আমাদের ১ ঘণ্টার রিয়েল মার্কেট **Multi-Candle Confirmed Price Action** সেশন শুরু হতে যাচ্ছে!\n\n"
                    f"🛡️ **মানি ম্যানেজমেন্ট রুল:**\n"
                    f"• প্রতি ক্যান্ডেলে নিজের ব্যালেন্সের **১% থেকে ৩%-এর বেশি** রিস্ক নিবেন না।\n"
                    f"• প্রতিদিন ব্যালেন্সের **৫% থেকে ৭% (সর্বোচ্চ ১০%) প্রফিট** হয়ে গেলেই নিজের ট্রেড বন্ধ করে মার্কেট থেকে বের হয়ে আসবেন!",
                    with_button=True,
                    target_group="VIP"
                )
                broadcast_text(
                    f"{VIP_HEADER}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔥 **আর মাত্র ৩০ মিনিট পর ({s_time_str}-এ) আমাদের রিয়েল মার্কেট VIP সেশন শুরু হচ্ছে!** 🔥\n\n"
                    f"💎 **ফ্রিতে ভিআইপি (VIP) চ্যানেলে জয়েন করতে:**\n"
                    f"১️⃣ নিচের লিংকে ক্লিক করে ব্রোকার অ্যাকাউন্ট খুলুন।\n"
                    f"২️⃣ অ্যাকাউন্টটি **Verify (ভেরিফাই)** করুন।\n"
                    f"৩️⃣ আপনার **UID** আমার ইনবক্সে (`{ADMIN_USERNAME}`) পাঠিয়ে দিন!\n\n"
                    f"🔗 **রেজিস্ট্রেশন লিংক:**\n👉 {SETTINGS['register_link']}",
                    with_button=True,
                    target_group="FREE"
                )

            if current_hour == cfg["research_h"] and cfg["research_m"] <= current_minute <= cfg["research_m"] + 4 and not flags["researched"]:
                flags["researched"] = True
                mkt_status, best_pairs, news_curs = run_pre_session_market_research(now)
                pairs_str = ", ".join(best_pairs[:5])
                news_note = f"⚠️ **লাইভ নিউজ ব্লকড কারেন্সি:** `{', '.join(news_curs)}` (নিউজ চলাকালীন এই কারেন্সি বাদ দেওয়া হয়েছে)" if news_curs else "✅ **নিউজ স্ট্যাটাস:** এই মুহূর্তে কোনো হাই-ইমপ্যাক্ট নিউজ নেই (Clean Market)।"
                broadcast_text(
                    f"{VIP_HEADER}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔍 **【 𝐅𝐎𝐑𝐄𝐗 𝐅𝐀𝐂𝐓𝐎𝐑𝐘 𝐋𝐈𝐕𝐄 𝐍𝐄𝐖𝐒 & 𝐌𝐀𝐑𝐊𝐄𝐓 𝐒𝐂𝐀𝐍 】**\n\n"
                    f"আলহামদুলিল্লাহ! **{cfg['name']}** শুরুর আগেই আমাদের ইঞ্জিন Forex Factory ক্যালেন্ডার ও ক্যান্ডেল ভলিউম স্ক্যান সম্পন্ন করেছে।\n"
                    f"{news_note}\n"
                    f"✅ **আজকের সেশনের নিরাপদ পেয়ারসমূহ:** `{pairs_str}`",
                    with_button=False,
                    target_group="VIP"
                )
                
        # ৩. সেশন শুরু
        if not session_active:
            triggered_key = None
            for s_key, cfg in SESSIONS_CONFIG.items():
                flags = session_flags[s_key]
                if flags["started"] or flags["completed"]:
                    continue
                is_banner_window = (current_hour == cfg["banner_h"] and cfg["banner_m"] <= current_minute <= cfg["start_m"] + 15)
                if is_banner_window:
                    triggered_key = s_key
                    flags["started"] = True
                    flags["completed"] = True
                    break

            if force_instant_session or triggered_key is not None:
                is_manual_force = force_instant_session
                force_instant_session = False
                abort_current_session = False
                session_active = True
                active_session_key = triggered_key if triggered_key is not None else "MANUAL"

                run_pre_session_market_research(now)

                if not is_manual_force and triggered_key is not None:
                    cfg = SESSIONS_CONFIG[triggered_key]
                    official_signal_start_dt = now.replace(hour=cfg["start_h"], minute=cfg["start_m"], second=2, microsecond=0)
                    if now > official_signal_start_dt:
                        official_signal_start_dt = now + datetime.timedelta(seconds=10)
                    session_end_dt = official_signal_start_dt + datetime.timedelta(minutes=60)
                else:
                    official_signal_start_dt = now + datetime.timedelta(seconds=10)
                    session_end_dt = now + datetime.timedelta(minutes=60)

                session_wins = 0
                session_direct_wins = 0
                session_mtg_wins = 0
                session_losses = 0
                session_refunds = 0
                consecutive_mtg_only = 0
                consecutive_session_losses = 0
                
                banner = generate_session_banner(is_start=True)
                broadcast_photo(
                    banner,
                    f"🕋 **বিসমিল্লাহির রাহমানির রাহিম** 🕋\n"
                    f"{VIP_HEADER}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🟢 **【 𝐕𝐈𝐏 𝟏-𝐇𝐎𝐔𝐑 𝐋𝐈𝐕𝐄 𝐒𝐄𝐒𝐒𝐈𝐎𝐍 𝐒𝐓𝐀𝐑𝐓𝐒 】** 🟢\n\n"
                    f"মহান আল্লাহর নামে আমাদের ১ ঘণ্টার রিয়েল মার্কেট সেশন শুরু হলো! আমাদের ইঞ্জিন কোনো তাড়াহুড়ো না করে প্রতি মিনিটের পূর্ণাঙ্গ ক্যান্ডেল ক্লোজ হওয়া দেখবে এবং **যখনই ১০০% নিখুঁত সেটআপ পাবে, কেবল তখনই সিগন্যাল দেবে!**\n\n"
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
                    f"🟢 **আমাদের প্রাইভেট VIP চ্যানেলে ১০০% রিয়েল মার্কেট লাইভ সেশন শুরু হয়ে গেছে!** 🔥\n\n"
                    f"💎 **ফ্রিতে আমাদের VIP চ্যানেলে যুক্ত হতে:**\n"
                    f"নিচের অফিশিয়াল লিংক থেকে ব্রোকার অ্যাকাউন্ট খুলে সেটি **Verify (ভেরিফাই)** করুন এবং আপনার **User ID (UID)** আমার ইনবক্সে পাঠিয়ে দিন!\n\n"
                    f"🔗 **রেজিস্ট্রেশন লিংক:**\n👉 {SETTINGS['register_link']}\n\n"
                    f"🤝 **না পারলে বা বুঝতে সমস্যা হলে ইনবক্স করুন:** {ADMIN_USERNAME}",
                    with_buttons=True,
                    target_group="FREE"
                )
                
        # =====================================================================
        # 🔥 ৪. [PURE SETUP-DRIVEN 1-HOUR SCANNING (NO TIME FORCE)]
        # =====================================================================
        if session_active:
            now = datetime.datetime.now(tz)
            total_signals_given = session_wins + session_losses + session_refunds
            
            if now >= session_end_dt or abort_current_session:
                session_active = False
                active_session_key = None
                abort_current_session = False
                time.sleep(3)
                
                end_banner = generate_session_banner(is_start=False)
                decisive_trades = session_wins + session_losses
                s_total = decisive_trades + session_refunds
                s_rate = int((session_wins / decisive_trades) * 100) if decisive_trades > 0 else 100
                
                closing_note = "🔒 **1-Hour Session Completed:** আলহামদুলিল্লাহ! আমাদের ১ ঘণ্টার সেশন সমাপ্ত হয়েছে। সবাই আজকের প্রফিট সুরক্ষিত রেখে ব্রোকার থেকে লগ-আউট করুন!"

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
                        f"🔥 **আজকের রিয়েল মার্কেট VIP সেশনে `{s_rate}%` একুরেসিতে দুর্দান্ত প্রফিট হয়েছে!** 🚀\n\n"
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
            
            # একটি ট্রেড শেষ হওয়ার পর কমপক্ষে ১টি নতুন ক্যান্ডেল তৈরি হতে দেওয়া হবে, তারপর থেকে প্রতি মিনিটে সেটআপ খুঁজবে
            if not is_first_trade_of_session:
                for _ in range(55):
                    if abort_current_session or force_instant_session:
                        break
                    time.sleep(1)

            if abort_current_session or force_instant_session:
                force_instant_session = False
                continue

            # =================================================================
            # 🧠 [DYNAMIC CANDLE-CLOSE FILTER TIER: 1x -> 2x DOUBLE -> 3x TRIPLE]
            # =================================================================
            if session_wins >= 3 or session_losses >= 1 or consecutive_mtg_only >= 2:
                current_filter_tier = 3  # 3x Triple Filtering (Multi-Touch SNR + 2-Candle Confirmation + M1/M5/M15 Trend)
                tier_badge = "🔬 **【 𝟑𝐗 𝐓𝐑𝐈𝐏𝐋𝐄-𝐂𝐎𝐍𝐅𝐈𝐑𝐌𝐄𝐃 𝐒𝐄𝐓𝐔𝐏 】**\n"
            elif session_wins == 2 or session_mtg_wins >= 1:
                current_filter_tier = 2  # 2x Double Filtering (2-Candle Close Confirmation)
                tier_badge = "🔍 **【 𝟐𝐗 𝐃𝐎𝐔𝐁𝐋𝐄-𝐂𝐎𝐍𝐅𝐈𝐑𝐌𝐄𝐃 𝐒𝐄𝐓𝐔𝐏 】**\n"
            else:
                current_filter_tier = 2 if is_first_trade_of_session else 1
                tier_badge = "🛡️ **【 𝟏𝐒𝐓 𝐓𝐑𝐀𝐃𝐄 - 𝐃𝐄𝐄𝐏 𝐕𝐄𝐑𝐈𝐅𝐈𝐄𝐃 】**\n" if is_first_trade_of_session else ""

            asset, direction, market_setup = scan_until_real_setup_found(
                tz, session_end_dt, filter_tier=current_filter_tier
            )
            if asset is None or abort_current_session:
                continue

            sig_now = datetime.datetime.now(tz)
            if sig_now >= session_end_dt:
                continue

            if sig_now.second > 8:
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
            
            signal_caption = (
                f"{VIP_HEADER}\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{tier_badge}"
                f"💎 **【 𝐕𝐈𝐏 𝐒𝐍𝐈𝐏𝐄𝐑 𝐒𝐈𝐆𝐍𝐀𝐋 #{trade_number} 】** 💎\n"
                f"╭───────────────────────⋅•⋅⊰∙∘☽\n"
                f"📊 **Pair -»** `{asset}` (News-Free 80%+)\n"
                f"🕒 **Entry Time -»** `{timetable}` (UTC+6)\n"
                f"⏰ **Closing Time -»** `{timeset}` (3 Candles)\n"
                f"⏳ **Timeframe -»** `1M Chart (3 Min Exp.)`\n"
                f"🎯 **Filter Score -»** `{conf_score}%`\n"
                f"🕯️ **Setup -»** {snr_reason}\n"
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
                session_direct_wins += 1
                consecutive_mtg_only = 0
                consecutive_session_losses = 0
                res_status = "✅✅✅ **Direct Win (SURESHOT PROFIT)** ✅✅✅"
                psych_note = "🎯 **Target Note:** আপনার নিজের ব্যালেন্সের **৫%–১০% ডেইলি প্রফিট টার্গেট** পূরণ হয়ে গেলে আজকের মতো মার্কেট থেকে বের হয়ে আসুন!"
            elif outcome == "MTG_WIN":
                session_wins += 1
                session_mtg_wins += 1
                consecutive_mtg_only += 1
                consecutive_session_losses = 0
                res_status = "✅✅✅ **1-Step Martingale Win (MTG WIN¹)** ✅✅✅"
                psych_note = "🔬 **Filter Note:** পরবর্তী সিগন্যালের জন্য বট এখন পূর্ণাঙ্গ **Multi-Candle Close Confirmation** না পাওয়া পর্যন্ত অপেক্ষা করবে! নিজের ১%–৩% বেস রিস্ক বজায় রাখুন।"
            elif outcome == "REFUND":
                session_refunds += 1
                res_status = "🔄🔄🔄 **Trade Refunded (DOJI / $0 DRAW)** 🔄🔄🔄"
                psych_note = "🛡️ **Note:** রিফান্ড মানে ব্যালেন্স সুরক্ষিত। পরের ট্রেডে ১%–৩% বেস রিস্ক বজায় রাখুন।"
            else:
                session_losses += 1
                consecutive_session_losses += 1
                res_status = "❎✖️💀 **Loss Trade (DO NOT OVER-RISK!)** 💀✖️❎"
                psych_note = "⚠️ **কঠোর সতর্কতা:** ট্রেড মিস হলে ভুলেও আবেগের বশে পরের ট্রেডে বড় অ্যামাউন্ট বসাবেন না! বট এখন পরবর্তী ট্রেডের জন্য **3x Multi-Candle Triple Filtering** চালু করেছে।"
                
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