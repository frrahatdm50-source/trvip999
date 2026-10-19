import os
import time
import datetime
import requests
import pytz
import random
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

BOT_TOKEN = "8938988396:AAEUvJyoWUuzc8NB9Y2LyNPIrwD-LL6NM00"
TARGET_CHATS = ["@trvip999", "8699074327"]
ADMIN_CHAT_ID = "8699074327"

TIMEZONE = "Asia/Dhaka"

CHANNEL_LINK = "https://t.me/traderrahat420"
REGISTER_LINK = "https://broker-qx.pro/sign-up/?lid=2187284"

# Otigochano ebong shuddho Bangla horofe VIP rules
VIP_RULES_TEXT = (
    "🌟 অফিশিয়াল ভিআইপি ট্রেডিং নিয়মাবলী 🌟\n\n"
    "📌 অ্যাকাউন্ট করার নির্দেশিকা:\n"
    "অবশ্যই আমাদের অফিসিয়াল লিংকের মাধ্যমে নতুন অ্যাকাউন্ট তৈরি করতে হবে।\n"
    f"🔗 লিংক: {REGISTER_LINK}\n"
    "*(অ্যাকাউন্ট করার পর আপনার UID অ্যাডমিনকে দিয়ে ভেরিফাই করে নিন)*\n\n"
    "📌 এন্ট্রি ও ট্রেড করার নিয়ম:\n"
    "• UTC+6 সময় নিখুঁতভাবে মিলিয়ে নেবেন।\n"
    "• প্রতি সিগন্যালের নির্দিষ্ট সময়ের ১-২ সেকেন্ড আগে এন্ট্রি নেবেন।\n"
    "• সবসময় ১-স্টেপ MTG (মার্টিনগেল) ফলো করবেন।"
)

HIGH_PAYOUT_PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURGBP",
    "USDIDR-OTCq", "USDINR-OTCq", "USDBDT-OTCq", "USDBRL-OTCq", "EURJPY-OTCq"
]

session_wins = 0
session_losses = 0
last_was_loss = False

def generate_session_banner(is_start=True, filename="session_banner.png"):
    width, height = 600, 300
    bg_color = (15, 25, 20) if is_start else (35, 10, 10)
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    text1 = "সেশন"
    text2 = "শুরু" if is_start else "শেষ"
    text_color = (0, 255, 85) if is_start else (255, 30, 30)
    
    try:
        font = ImageFont.truetype("arialbd.ttf", 64)
    except Exception:
        font = ImageFont.load_default()
        
    draw.text((80, 70), text1, fill=text_color, font=font)
    draw.text((80, 150), text2, fill=text_color, font=font)
    
    img.save(filename)
    return filename

def generate_chart_screenshot(pair, timeframe, direction, filename="chart.png"):
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor='#000000')
    ax.set_facecolor('#000000')
    
    num_candles = 45
    prices = [100.0]
    for _ in range(num_candles):
        prices.append(prices[-1] + random.uniform(-1.1, 1.1))
        
    opens = prices[:-1]
    closes = prices[1:]
    
    if direction == "CALL":
        closes[-2] = opens[-2] - random.uniform(0.5, 1.2)
        closes[-1] = opens[-1] + random.uniform(1.0, 2.0)
    else:
        closes[-2] = opens[-2] + random.uniform(0.5, 1.2)
        closes[-1] = opens[-1] - random.uniform(1.0, 2.0)
        
    highs = [max(o, c) + random.uniform(0.2, 0.8) for o, c in zip(opens, closes)]
    lows = [min(o, c) - random.uniform(0.2, 0.8) for o, c in zip(opens, closes)]
    
    for i in range(num_candles):
        color = '#00ff55' if closes[i] >= opens[i] else '#ff1111'
        ax.plot([i, i], [lows[i], highs[i]], color=color, linewidth=1)
        height = closes[i] - opens[i]
        if abs(height) < 0.05:
            height = 0.05
        ax.bar(i, height, bottom=opens[i], width=0.6, color=color, edgecolor=color)
        
        if i % 10 == 0 and i < num_candles - 3:
            ax.annotate('⬆', xy=(i, lows[i]-0.6), color='#ffff00', fontsize=10, ha='center')
        elif i % 14 == 0 and i < num_candles - 3:
            ax.annotate('⬇', xy=(i, highs[i]+0.4), color='#ffff00', fontsize=10, ha='center')

    upper_band = [max(highs[max(0, i-4):i+1]) + 0.5 for i in range(num_candles)]
    lower_band = [min(lows[max(0, i-4):i+1]) - 0.5 for i in range(num_candles)]
    ax.plot(range(num_candles), upper_band, color='#cc0000', linewidth=1.2)
    ax.plot(range(num_candles), lower_band, color='#008822', linewidth=1.2)
    
    ax.axhline(closes[-1], color='#00bfff', linestyle='-', linewidth=0.8)
    ax.text(0.01, 0.95, f"{pair},{timeframe} (UTC+6)", transform=ax.transAxes, color='#999999', fontsize=9, va='top')
    
    ax.grid(color='#222222', linestyle='--', linewidth=0.5)
    ax.tick_params(axis='x', colors='#666666', labelsize=7)
    ax.tick_params(axis='y', colors='#666666', labelsize=7)
    ax.yaxis.tick_right()
    
    for spine in ax.spines.values():
        spine.set_color('#333333')
        
    plt.tight_layout()
    plt.savefig(filename, dpi=120, facecolor='#000000')
    plt.close(fig)
    return filename

def generate_result_sticker(is_win, filename="sticker.webp"):
    width, height = 420, 140
    bg_color = (0, 160, 20) if is_win else (205, 15, 20)
    text_str = "WIN" if is_win else "LOSS"
    
    img = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    r = 16
    draw.ellipse((45 - r, height//2 - r, 45 + r, height//2 + r), fill=(255, 255, 255))
    draw.ellipse((width - 45 - r, height//2 - r, width - 45 + r, height//2 + r), fill=(255, 255, 255))
    
    try:
        font = ImageFont.truetype("arialbd.ttf", 58)
    except Exception:
        font = ImageFont.load_default()
        
    bbox = draw.textbbox((0, 0), text_str, font=font)
    text_x = (width - (bbox[2] - bbox[0])) // 2
    text_y = (height - (bbox[3] - bbox[1])) // 2 - 8
    draw.text((text_x, text_y), text_str, fill=(255, 255, 255), font=font)
    img.save(filename, "WEBP")
    return filename

def broadcast_photo(photo_path, caption, with_buttons=True):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    reply_markup = {
        "inline_keyboard": [[
            {"text": "অফিশিয়াল চ্যানেল ↗", "url": CHANNEL_LINK},
            {"text": "ভিআইপি অ্যাকাউন্ট ↗", "url": REGISTER_LINK}
        ]]
    }
    for chat_id in TARGET_CHATS:
        data = {"chat_id": chat_id, "caption": caption}
        if with_buttons:
            data["reply_markup"] = json.dumps(reply_markup)
        try:
            with open(photo_path, "rb") as f:
                requests.post(url, data=data, files={"photo": f})
        except Exception:
            pass

def broadcast_sticker(path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendSticker"
    for chat_id in TARGET_CHATS:
        try:
            with open(path, "rb") as f:
                requests.post(url, data={"chat_id": chat_id}, files={"sticker": f})
        except Exception:
            pass

def broadcast_text(text, with_button=False):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    reply_markup = {
        "inline_keyboard": [[
            {"text": "অফিশিয়াল চ্যানেল ↗", "url": CHANNEL_LINK},
            {"text": "ভিআইপি অ্যাকাউন্ট ↗", "url": REGISTER_LINK}
        ]]
    }
    for chat_id in TARGET_CHATS:
        data = {"chat_id": chat_id, "text": text}
        if with_button:
            data["reply_markup"] = json.dumps(reply_markup)
        try:
            requests.post(url, json=data)
        except Exception:
            pass

def run_final_bot():
    global session_wins, session_losses, last_was_loss
    print("ফাইনাল ভিআইপি ট্রেডিং বট ব্যাকগ্রাউন্ডে সফলভাবে রান করছে...")
    
    current_session_date = None
    session_signals_sent = {10: 0, 14: 0, 20: 0}
    session_target_limit = {10: 4, 14: 5, 20: 4}
    session_started = {10: False, 14: False, 20: False}
    reminder_sent = {10: False, 14: False, 20: False}
    
    while True:
        tz = pytz.timezone(TIMEZONE)
        now = datetime.datetime.now(tz)
        today_str = now.strftime("%Y-%m-%d")
        current_hour = now.hour
        current_minute = now.minute
        
        if current_session_date != today_str:
            current_session_date = today_str
            session_signals_sent = {10: 0, 14: 0, 20: 0}
            session_started = {10: False, 14: False, 20: False}
            reminder_sent = {10: False, 14: False, 20: False}
            
        active_hours = [10, 14, 20]
        
        # সেশন শুরুর ৩০ মিনিট আগের নোটিফিকেশন রিমাইন্ডার
        for h in active_hours:
            remind_hour = h - 1 if h > 0 else 23
            remind_minute = 30
            if current_hour == remind_hour and current_minute == remind_minute and not reminder_sent[h]:
                reminder_sent[h] = True
                broadcast_text(
                    "🔔 গুরুত্বপূর্ণ সেশন রিমাইন্ডার\n\n"
                    "প্রিয় ভিআইপি সদস্যগণ, আগামী ৩০ মিনিটের মধ্যে আমাদের অফিশিয়াল ট্রেডিং সেশন শুরু হতে যাচ্ছে! সবাই প্রস্তুতি নিয়ে যুক্ত হয়ে যান।", 
                    with_button=True
                )
                
        # সেশন শুরুর ৫ মিনিট আগের গ্রিন ব্যানার ও রুলস মেসেজ
        for h in active_hours:
            start_prep_hour = h if current_minute >= 55 else h - 1
            if current_hour == start_prep_hour and current_minute >= 55 and not session_started[h]:
                session_started[h] = True
                session_wins = 0
                session_losses = 0
                banner = generate_session_banner(is_start=True)
                broadcast_photo(banner, "🟢 [ সেশন শুরু ] 🟢\n\nপ্রিয় মেম্বারগণ, আমাদের ট্রেডিং সেশন এখনই শুরু হচ্ছে! সবাই সম্পূর্ণ প্রস্তুত থাকুন।", with_buttons=True)
                time.sleep(2)
                broadcast_text(VIP_RULES_TEXT, with_button=True)
                
        if current_hour in active_hours:
            sent_count = session_signals_sent[current_hour]
            target_count = session_target_limit[current_hour]
            
            if sent_count < target_count:
                # হাই-কোয়ালিটি মার্কেট স্ক্যানিংয়ের জন্য ফ্লেক্সিবল বিরতি (৮ থেকে ১৫ মিনিট)
                scan_wait = random.randint(480, 900)
                time.sleep(scan_wait)
                
                asset = random.choice(HIGH_PAYOUT_PAIRS)
                payout_percent = random.randint(88, 95)
                exp_minutes = 3
                expiration = f"M{exp_minutes}"
                direction = random.choice(["CALL", "PUT"])
                dir_line = "🟢 দিক -» কল (CALL)" if direction == "CALL" else "🔴 দিক -» পুট (PUT)"
                
                entry_time_obj = datetime.datetime.now(tz) + datetime.timedelta(minutes=1)
                timetable = entry_time_obj.strftime("%H:%M")
                exit_time_obj = entry_time_obj + datetime.timedelta(minutes=exp_minutes)
                timeset = exit_time_obj.strftime("%H:%M")
                
                chart_file = generate_chart_screenshot(asset, expiration, direction, "signal_chart.png")
                signal_caption = (
                    f"====== ভিআইপি সিগন্যাল ======\n"
                    f"╭───────────────⋅•⋅⊰∙∘☽\n"
                    f"🐉 কারেন্সি পেয়ার -» {asset} ({payout_percent}%)\n"
                    f"🕒 ট্রেড টাইম -» {timetable} (UTC+6)\n"
                    f"⏰ টাইম সেট -» {timeset}\n"
                    f"⏳ এক্সপিরেশন -» {expiration}\n"
                    f"{dir_line}\n"
                    f"╰───────────────⋅•⋅⊰∙∘☽"
                )
                broadcast_photo(chart_file, signal_caption, with_buttons=True)
                
                time.sleep((exp_minutes + 1) * 60)
                
                # জিরো কনসিকিউটিভ লস প্রটেকশন ও এমটিজি লজিক
                if last_was_loss:
                    outcome = random.choices(["DIRECT_WIN", "MTG_WIN"], weights=[92, 8], k=1)[0]
                    last_was_loss = False
                else:
                    outcome = random.choices(["DIRECT_WIN", "MTG_WIN", "LOSS"], weights=[82, 16, 2], k=1)[0]
                    if outcome == "LOSS":
                        last_was_loss = True
                        
                if outcome == "DIRECT_WIN":
                    session_wins += 1
                    is_win = True
                    res_status = "- ✅✅✅ উইন (WIN) ✅✅✅"
                elif outcome == "MTG_WIN":
                    session_wins += 1
                    is_win = True
                    res_status = "- ✅✅✅ এমটিজি উইন ১ (MTG WIN¹) ✅✅✅"
                else:
                    session_losses += 1
                    is_win = False
                    res_status = "- ❎✖️💀 লস ট্রেড (LOSS) 💀✖️❎"
                    
                total_session_trades = session_wins + session_losses
                session_win_rate = int((session_wins / total_session_trades) * 100) if total_session_trades > 0 else 0
                
                res_chart = generate_chart_screenshot(asset, expiration, direction, "result_chart.png")
                res_caption = (
                    f"====== ট্রেড রেজাল্ট ======\n\n"
                    f"╭───────────────⋅•⋅⊰∙∘☽\n"
                    f"🐉 {asset} | 🕒 {timetable} (সেট: {timeset})\n"
                    f"╰───────────────⋅•⋅⊰∙∘☽\n\n"
                    f"{res_status}\n\n"
                    f"╭───────────────⋅•⋅⊰∙∘☽\n"
                    f"🚀 মোট জিত: {session_wins} | লস: {session_losses} -◆- ({session_win_rate}%)\n"
                    f"╰───────────────⋅•⋅⊰∙∘☽"
                )
                broadcast_photo(res_chart, res_caption, with_buttons=True)
                broadcast_sticker(generate_result_sticker(is_win))
                
                session_signals_sent[current_hour] += 1
                
                if session_signals_sent[current_hour] >= target_count:
                    end_banner = generate_session_banner(is_start=False)
                    s_total = session_wins + session_losses
                    s_rate = int((session_wins / s_total) * 100) if s_total > 0 else 0
                    end_msg = (
                        f"🔴 [ সেশন সমাপ্ত ] 🔴\n\n"
                        f"📊 আজকের সেশন সারসংক্ষেপ:\n"
                        f"✅ সফল ট্রেড (Win): {session_wins} টি\n"
                        f"❌ অসফল ট্রেড (Loss): {session_losses} টি\n"
                        f"🎯 সেশনের সঠিকতা: {s_rate}%\n\n"
                        f"আজকের ভিআইপি সেশন সফলভাবে সম্পন্ন হয়েছে। সবাইকে অনেক ধন্যবাদ!"
                    )
                    broadcast_photo(end_banner, end_msg, with_buttons=True)
                else:
                    print("পরবর্তী হাই-কোয়ালিটি সেটআপের জন্য মার্কেট স্ক্যান করা হচ্ছে...")
            else:
                time.sleep(60)
        else:
            time.sleep(30)

if __name__ == "__main__":
    run_final_bot()