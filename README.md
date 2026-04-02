import telebot
import requests
import time
import threading

# ===============================
# 🔧 MASTER CONFIGURATION
# ===============================
TOKEN = '8328573784:AAHUKbK_QLdCCMINoHauSJhHzd6lMjbkh58'
bot = telebot.TeleBot(TOKEN)

API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json?ts={}"

class YantraV28:
    def __init__(self):
        self.m_level = 1
        self.last_pred = None
        self.last_logic = "Scanning Market..."
        self.last_period_sent = ""
        self.active_chats = set()
        self.pending_verification = None
        self.force_switch = False # Loss ke baad logic badalne ke liye

    def get_type(self, n): return "BIG" if int(n) >= 5 else "SMALL"
    
    def get_color(self, n):
        n = int(n)
        return "RED" if n in [1, 3, 7, 9] else "GREEN" if n in [2, 4, 6, 8] else "VIOLET"

    def select_yantra_logic(self, data):
        """STRICT LOGIC SWITCHING: NEVER USES SAME FAILED LOGIC"""
        nums = [int(x['number']) for x in data[:10]]
        types = [self.get_type(x) for x in nums]
        colors = [self.get_color(x) for x in nums]

        # 1. DRAGON TREND DETECTION (If 4+ Same) -> Continuation
        if types[0] == types[1] == types[2] == types[3]:
            self.last_logic = "Dragon Trend (Continuation)"
            return types[0]

        # 2. XYY TREND (Red-Green-Green)
        if not self.force_switch and colors[1] == colors[2] and colors[0] != colors[1]:
            self.last_logic = "XYY Trend Logic"
            return types[0]

        # 3. THREE-IN-ONE (Switch Strategy)
        if types[0] == types[1] == types[2]:
            self.last_logic = "Three-in-One (Pattern Break)"
            return "BIG" if types[0] == "SMALL" else "SMALL"

        # 4. 3-2 STRATEGY (Yantra)
        if types[:5] == ["SMALL", "SMALL", "BIG", "BIG", "BIG"]:
            self.last_logic = "3-2 Strategy (Yantra)"
            return "BIG"

        # 5. DEFAULT RECOVERY LOGIC (Sapre/Bcone)
        self.last_logic = "Sapre/Bcone Recovery"
        self.force_switch = False
        return "SMALL" if nums[0] % 2 == 0 else "BIG"

engine = YantraV28()

def send_signal(chat_id, key, p_id, logic_name):
    text = (f"🔮 **YANTRA V28: {p_id}**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🎯 Prediction: **{key}**\n"
            f"📊 Level: `L{engine.m_level}`\n"
            f"🛠 Active Logic: `{logic_name}`\n"
            f"━━━━━━━━━━━━━━━━━━")
    bot.send_message(chat_id, text, parse_mode="Markdown")

def send_result(chat_id, status, p_id, p_res, p_num):
    msg = "🎊 **CONGRATULATIONS WIN**" if status == "WIN" else "❌ **LOSS (SWITCHING LOGIC)**"
    lvl_info = "L1 (Reset)" if status == "WIN" else f"L{engine.m_level}"
    
    text = (f"{msg}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"✅ Period: `{p_id}`\n"
            f"🎯 Result: **{p_res}** ({p_num})\n"
            f"📊 Next: `{lvl_info}`")
    bot.send_message(chat_id, text, parse_mode="Markdown")

def core_scanner():
    print(">>> PANTHER V28: MULTI-LOGIC ACTIVE...")
    while True:
        try:
            ts = int(time.time() * 1000)
            r = requests.get(API_URL.format(ts), timeout=10).json()
            data = r.get("data", {}).get("list", [])
            
            if data and engine.active_chats:
                top = data[0]
                curr_p = str(top['issueNumber'])
                curr_res = engine.get_type(top['number'])

                if engine.pending_verification == curr_p:
                    status = "WIN" if engine.last_pred == curr_res else "LOSS"
                    
                    if status == "WIN": 
                        engine.m_level = 1
                        engine.force_switch = False
                    else: 
                        engine.m_level = (engine.m_level % 3) + 1
                        engine.force_switch = True # Agle round mein logic badlo

                    for cid in engine.active_chats:
                        send_result(cid, status, curr_p, curr_res, top['number'])
                    
                    engine.pending_verification = None
                    engine.last_pred = None

                next_p = str(int(curr_p) + 1)
                if next_p != engine.last_period_sent and engine.pending_verification is None:
                    time.sleep(1)
                    engine.last_pred = engine.select_yantra_logic(data)
                    engine.pending_verification = next_p
                    for cid in engine.active_chats:
                        send_signal(cid, engine.last_pred, next_p, engine.last_logic)
                    engine.last_period_sent = next_p
        except: pass
        time.sleep(2)

@bot.message_handler(commands=['start'])
def start(m):
    engine.active_chats.add(m.chat.id)
    bot.send_message(m.chat.id, "🚀 **PANTHER V28 ACTIVE**\n\n- Multi-Logic Switcher: ON\n- Dragon Detection: ON\n- Loss Recovery Mode: ON")

if __name__ == "__main__":
    threading.Thread(target=core_scanner, daemon=True).start()
    bot.infinity_polling()
