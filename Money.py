import time
import threading
import requests

# ===============================
# 🔐 CONFIG & KEYS
# ===============================
TOKEN = '8328573784:AAHUKbK_QLdCCMINoHauSJhHzd6lMjbkh58'
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"

KEY_MAP = {
    "CASH-300-VIP": {"mode": "💰 300 to 1200", "start": 300, "target": 1200, "type": "money", "chart": [10, 30, 90, 240, 600]},
    "GOLD-500-VIP": {"mode": "💎 500 to 2000", "start": 500, "target": 2000, "type": "money", "chart": [20, 50, 150, 400, 900]},
    "PRO-KING-999": {"mode": "🔥 PRO MODE", "start": 1000, "target": 5000, "type": "money", "chart": [50, 150, 400, 1000, 2500]},
    "STREAK-5-WIN": {"mode": "🎯 5 Back-to-Back", "start": 0, "target": 5, "type": "streak", "chart": [10, 30, 90, 270, 810]}
}

class PantherFinalV55:
    def __init__(self):
        self.last_period = ""
        self.processed_period = ""
        self.pending_prediction = None
        self.last_pred_side = None
        self.users = {} 
        self.m_level = 1

    def send(self, cid, txt):
        payload = {"chat_id": cid, "text": txt, "parse_mode": "Markdown"}
        try: requests.post(f"{BASE_URL}/sendMessage", json=payload, timeout=5)
        except: pass

bot_eng = PantherFinalV55()

def all_logics_combined(data):
    h = [("BIG" if int(x['number']) >= 5 else "SMALL") for x in data[:10]]
    # (6) SURFING SHIFTING
    if h[0] == h[1] and h[1] != h[2]: return h[0], "SURFING SHIFTING"
    # (3) DRAGON
    if h[0] == h[1] == h[2]: return h[0], "DRAGON TREND"
    # (2) ZIGZAG
    if h[0] != h[1]: return h[0], "ZIGZAG PATTERN"
    # (4) MIRROR
    if len(h) >= 4 and h[0] == h[1] and h[2] == h[3]: return h[0], "MIRROR THEORY"
    # (1) & (5) ADVANCED DB-9
    return ("BIG" if h.count("BIG") < 5 else "SMALL"), "ADVANCED DB-9"

def scanner():
    while True:
        try:
            r = requests.get(API_URL, headers={"User-Agent":"Mozilla/5.0"}, timeout=10).json()
            data = r.get("data", {}).get("list", [])
            if not data: continue
            
            top = data[0]
            curr_p, curr_num = str(top['issueNumber']), int(top['number'])
            curr_res = "BIG" if curr_num >= 5 else "SMALL"

            if bot_eng.pending_prediction == curr_p and bot_eng.processed_period != curr_p:
                win = (bot_eng.last_pred_side == curr_res)
                bot_eng.processed_period = curr_p
                
                for cid, u in bot_eng.users.items():
                    if u["active"]:
                        if win:
                            u["wins"] += 1
                            if u["type"] == "money": u["balance"] += (u["chart"][bot_eng.m_level-1] * 0.9)
                            bot_eng.m_level = 1
                            bot_eng.send(cid, f"✅ **WIN**\nPeriod: {curr_p}\nResult: {curr_res}\nNew Balance: ₹{int(u['balance'])}")
                        else:
                            if u["type"] == "streak": u["wins"] = 0
                            bot_eng.m_level = (bot_eng.m_level % 5) + 1
                            bot_eng.send(cid, f"❌ **LOSS**\nNext Level: L{bot_eng.m_level}")

                        if (u["type"] == "money" and u["balance"] >= u["target"]) or (u["type"] == "streak" and u["wins"] >= 5):
                            bot_eng.send(cid, f"💰 **TARGET ACHIEVED!**\nFinal Balance: ₹{int(u['balance'])}\n**SESSION CLOSED**")
                            u["active"] = False
                bot_eng.pending_prediction = None

            next_p = str(int(curr_p) + 1)
            if next_p != bot_eng.last_period:
                time.sleep(2)
                bot_eng.last_pred_side, logic_name = all_logics_combined(data)
                bot_eng.pending_prediction = next_p
                
                for cid, u in bot_eng.users.items():
                    if u["active"]:
                        # Display specific amount to bet
                        bet_amt = u["chart"][bot_eng.m_level-1]
                        msg = (f"🚀 **MODE: {u['mode']}**\n"
                               f"━━━━━━━━━━━━━━━━━━\n"
                               f"🎯 Period: `{next_p}`\n"
                               f"🔮 Prediction: **{bot_eng.last_pred_side}**\n"
                               f"💰 **Bet Amount: ₹{bet_amt}**\n"
                               f"📊 Level: `L{bot_eng.m_level}`\n"
                               f"⚙️ Logic: `{logic_name}`\n"
                               f"━━━━━━━━━━━━━━━━━━")
                        bot_eng.send(cid, msg)
                bot_eng.last_period = next_p
        except: pass
        time.sleep(5)

def main():
    offset = 0
    while True:
        try:
            res = requests.get(f"{BASE_URL}/getUpdates?offset={offset}&timeout=10").json()
            for up in res.get("result", []):
                offset = up["update_id"] + 1
                if "message" in up:
                    cid, txt = up["message"]["chat"]["id"], up["message"].get("text", "")
                    if txt == "/start":
                        bot_eng.send(cid, "💎 **Panther V55 FIXED**\nEnter VIP KEY to start money session:")
                    elif txt in KEY_MAP:
                        bot_eng.users[cid] = {
                            "mode": KEY_MAP[txt]["mode"], "balance": KEY_MAP[txt]["start"],
                            "target": KEY_MAP[txt]["target"], "type": KEY_MAP[txt]["type"],
                            "chart": KEY_MAP[txt]["chart"], "wins": 0, "active": True
                        }
                        bot_eng.send(cid, f"✅ **{KEY_MAP[txt]['mode']}** Unlocked!\nTarget: ₹{KEY_MAP[txt]['target']}\nAI Scanning...")
        except: pass
        time.sleep(1)

if __name__ == "__main__":
    threading.Thread(target=scanner, daemon=True).start()
    main()
