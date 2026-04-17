# =====================================================
# SMART TRADING AI BOT - SINGLE FILE
# Telegram + Binance Futures + 24/7 on Railway
# =====================================================

import os
import time
import logging
import ccxt
import requests
from dotenv import load_dotenv

load_dotenv()

# ===================== CONFIG =====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# === Your Credentials ===
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8484289790:AAGKFL0MmP9iafuM50okuJAeRIDRTAQIPnE')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
SYMBOL = os.getenv('SYMBOL', 'BTC/USDT:USDT')
LEVERAGE = int(os.getenv('LEVERAGE', '10'))
TESTNET = os.getenv('TESTNET', 'true').lower() == 'true'

# ===================== TELEGRAM HELPER =====================
def send_telegram(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        requests.post(url, json=payload, timeout=10)
    except:
        pass

# ===================== MAIN BOT =====================
class SmartTradingBot:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': os.getenv('BINANCE_API_KEY'),
            'secret': os.getenv('BINANCE_API_SECRET'),
            'enableRateLimit': True,
            'options': {'defaultType': 'future'},
        })

        if TESTNET:
            self.exchange.set_sandbox_mode(True)
            logger.info("🔧 TESTNET MODE ACTIVATED - Safe Mode")
            send_telegram("🚀 <b>Smart Trading AI Bot Started</b>\nMode: <b>TESTNET</b> ✅")

        self.symbol = SYMBOL
        self.leverage = LEVERAGE

    def run(self):
        logger.info(f"🤖 Bot Running on {self.symbol} @ {self.leverage}x")
        send_telegram(
            f"✅ <b>Bot is Live!</b>\n"
            f"Symbol: <b>{self.symbol}</b>\n"
            f"Leverage: <b>{self.leverage}x</b>\n"
            f"Mode: {'TESTNET 🛡️' if TESTNET else 'LIVE ⚠️'}"
        )

        self.exchange.set_leverage(self.leverage, self.symbol)

        while True:
            try:
                ticker = self.exchange.fetch_ticker(self.symbol)
                price = float(ticker['last'])
                change = float(ticker.get('percentage', 0))

                # === Trading Logic ===
                if price % 100 < 33:
                    signal = "🟢 STRONG BUY"
                    send_telegram(
                        f"{signal}\n"
                        f"💰 Price: <b>${price:,.2f}</b>\n"
                        f"24h: {change:+.2f}%\n"
                        f"Symbol: {self.symbol}"
                    )
                elif price % 100 > 67:
                    signal = "🔴 STRONG SELL"
                    send_telegram(
                        f"{signal}\n"
                        f"💰 Price: <b>${price:,.2f}</b>\n"
                        f"24h: {change:+.2f}%\n"
                        f"Symbol: {self.symbol}"
                    )
                else:
                    signal = "🟡 HOLD"

                logger.info(f"Price: ${price:,.2f} | {signal}")
                time.sleep(60)   # Check every 60 seconds

            except Exception as e:
                error = f"⚠️ Error: {str(e)[:150]}"
                logger.error(error)
                send_telegram(error)
                time.sleep(10)


# ===================== START BOT =====================
if __name__ == "__main__":
    try:
        bot = SmartTradingBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        send_telegram("🛑 Bot stopped manually")
    except Exception as e:
        logger.critical(f"Fatal Error: {e}")
        send_telegram(f"❌ Bot Crashed: {str(e)[:200]}")
