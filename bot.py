import os
import time
import logging
import ccxt
import requests
import schedule
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ===================== CONFIG =====================
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = "8484289790:AAGKFL0MmP9iafuM50okuJAeRIDRTAQIPnE"
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SYMBOL = "BTC/USDT:USDT"
LEVERAGE = 10

# ===================== TELEGRAM =====================
def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"})
    except:
        pass

# ===================== BINANCE =====================
exchange = ccxt.binance({
    'apiKey': os.getenv('BINANCE_API_KEY'),
    'secret': os.getenv('BINANCE_API_SECRET'),
    'options': {'defaultType': 'future'},
    'enableRateLimit': True,
})

# Set to REAL trading (remove testnet)
# exchange.set_sandbox_mode(False)   # Real money mode

exchange.set_leverage(LEVERAGE, SYMBOL)

# ===================== SCHEDULER =====================
def place_order(side, amount):
    try:
        order = exchange.create_market_order(SYMBOL, side, amount)
        send_msg(f"✅ {side.upper()} ORDER EXECUTED\nSymbol: {SYMBOL}\nAmount: {amount}\nTime: {datetime.now()}")
        logger.info(f"Order executed: {side} {amount}")
    except Exception as e:
        send_msg(f"❌ Order Failed: {str(e)}")

# ===================== COMMANDS =====================
def handle_command(command):
    try:
        parts = command.split()
        cmd = parts[0].lower()

        if cmd == "/buy":
            amount = float(parts[1]) if len(parts) > 1 else 0.001
            schedule.every().day.at("10:00").do(place_order, "buy", amount)   # Example time
            send_msg(f"🟢 BUY scheduled for 10:00 daily\nAmount: {amount} BTC")

        elif cmd == "/sell":
            amount = float(parts[1]) if len(parts) > 1 else 0.001
            schedule.every().day.at("22:00").do(place_order, "sell", amount)
            send_msg(f"🔴 SELL scheduled for 22:00 daily\nAmount: {amount} BTC")

        elif cmd == "/nowbuy":
            amount = float(parts[1]) if len(parts) > 1 else 0.001
            place_order("buy", amount)

        elif cmd == "/nowsell":
            amount = float(parts[1]) if len(parts) > 1 else 0.001
            place_order("sell", amount)

        elif cmd == "/status":
            send_msg("✅ Bot is running\nUse /buy <amount> or /nowbuy <amount>")

    except:
        send_msg("Usage:\n/buy 0.001\n/sell 0.001\n/nowbuy 0.001\n/status")

# ===================== MAIN =====================
send_msg("🚀 <b>Simple Scheduling Trading Bot Started</b>\nReal Mode - Be Careful!")

while True:
    try:
        # You can add polling logic later, but for now we run scheduled tasks
        schedule.run_pending()
        time.sleep(10)
    except Exception as e:
        logger.error(e)
        time.sleep(30)
