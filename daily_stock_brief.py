#!/usr/bin/env python3
"""
Daily Stock Brief Generator - v2.1
Fetches stock prices using yfinance, sends daily reports to Telegram
With comprehensive error handling and retry logic
"""

import json
import yfinance as yf
import requests
from datetime import datetime
import time
import logging
import os
from datetime import datetime
from typing import List, Dict, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG_FILE = "stocks.json"
LOG_FILE = "stock_brief_error.log"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8431739904:AAE-Ukcpc7ltEkAaNwEJT07FkL79mUESwdA")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "8215209844")

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging():
    """Configure logging for errors and operations"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ============================================================================
# YFINANCE FUNCTIONS
# ============================================================================

def get_yahoo_price(symbol: str) -> Optional[float]:
    """Fetch current price using yfinance with retry"""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Fetching price for {symbol} (attempt {attempt}/{MAX_RETRIES})...")
            ticker = yf.Ticker(symbol)
            
            info = ticker.fast_info
            if hasattr(info, 'last_price') and info.last_price:
                price = float(info.last_price)
                logger.info(f"Got price for {symbol}: ${price:.2f}")
                return price
            
            hist = ticker.history(period="1d")
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                logger.info(f"Got price for {symbol}: ${price:.2f}")
                return price
            
            logger.warning(f"No price data for {symbol}")
            return None
            
        except Exception as e:
            logger.warning(f"Error fetching price for {symbol} (attempt {attempt}): {e}")
            if attempt < MAX_RETRIES:
                logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
    
    logger.error(f"Failed after {MAX_RETRIES} attempts: {symbol}")
    return None

def get_price_change(symbol: str) -> float:
    """Get daily price change percentage using yfinance"""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            
            if len(hist) >= 2:
                current_price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                if prev_close > 0:
                    change = ((current_price - prev_close) / prev_close) * 100
                    logger.info(f"Price change for {symbol}: {change:+.2f}%")
                    return change
            
            if len(hist) == 1:
                info = ticker.fast_info
                if hasattr(info, 'previous_close') and info.previous_close:
                    current_price = hist['Close'].iloc[-1]
                    prev_close = float(info.previous_close)
                    if prev_close > 0:
                        change = ((current_price - prev_close) / prev_close) * 100
                        logger.info(f"Price change for {symbol}: {change:+.2f}%")
                        return change
            
            logger.warning(f"Could not calculate price change for {symbol}")
            return 0.0
            
        except Exception as e:
            logger.warning(f"Error calculating price change for {symbol} (attempt {attempt}): {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
    
    return 0.0

# ============================================================================
# NEWS FUNCTIONS
# ============================================================================

def fetch_news_simple(symbol: str) -> List[Dict]:
    """Fetch news using yfinance ticker.news API"""
    news = []
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Fetching news for {symbol} (attempt {attempt}/{MAX_RETRIES})...")
            ticker = yf.Ticker(symbol)
            yf_news = ticker.news
            
            if yf_news:
                for item in yf_news[:5]:
                    # yfinance news has nested 'content' object
                    content = item.get('content', item)
                    title = content.get('title', '') if content else ''
                    
                    if 15 < len(title) < 200:
                        # Source is in the main item, not content
                        source = item.get('source', 'Yahoo Finance')
                        # Try multiple paths for URL
                        url = content.get('canonicalUrl', {}).get('url', '') or item.get('link', '')
                        # Parse pubDate
                        pub_date_str = content.get('pubDate', '')
                        if pub_date_str:
                            try:
                                pub_date = int(datetime.fromisoformat(pub_date_str.replace('Z', '+00:00')).timestamp())
                            except:
                                pub_date = int(time.time())
                        else:
                            pub_date = int(time.time())
                        
                        if not any(existing.get('title', '') == title for existing in news):
                            news.append({
                                "title": title[:70],
                                "source": source,
                                "date": pub_date,
                                "url": url,
                                "summary": content.get('summary', '')[:100]
                            })
                
                logger.info(f"Fetched {len(news)} news items for {symbol}")
                break
            
            logger.warning(f"No news from yfinance for {symbol}")
            break
            
        except Exception as e:
            logger.error(f"Error fetching news for {symbol} (attempt {attempt}): {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
    
    # Fallback if no news
    if len(news) == 0:
        logger.warning(f"No news found for {symbol}, using fallback")
        news.append({
            "title": f"{symbol}: Check latest market news",
            "source": "Market Watch",
            "date": int(time.time()),
            "url": "",
            "summary": ""
        })
    
    return news[:3]
    
    if len(news) == 0:
        logger.warning(f"No news found for {symbol}, using fallback")
        news.append({
            "title": f"{symbol}: Check latest market news",
            "source": "Market Watch",
            "date": int(time.time()),
            "url": "",
            "summary": ""
        })
    
    return news[:3]

# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def analyze_impact(news_item: Dict) -> Dict:
    """Analyze news impact on stock price"""
    title = news_item.get("title", "").lower()
    summary = news_item.get("summary", "").lower()
    text = f"{title} {summary}"
    
    bullish_keywords = ["surge", "jump", "beat", "growth", "upgrade", "acquisition", "partnership", "record"]
    bearish_keywords = ["drop", "fall", "miss", "cut", "downgrade", "lawsuit", "investigation", "concern"]
    
    impact = "NEUTRAL"
    impact_score = 0.0
    
    for word in bullish_keywords:
        if word in text:
            impact = "BULLISH"
            impact_score = 0.3 + (text.count(word) * 0.1)
            break
    
    if impact == "NEUTRAL":
        for word in bearish_keywords:
            if word in text:
                impact = "BEARISH"
                impact_score = -(0.3 + (text.count(word) * 0.1))
                break
    
    return {"direction": impact, "estimated_change": round(impact_score * 100, 1)}

def generate_prognosis(stock: Dict, news: List[Dict], price_change: float) -> Dict:
    """Generate price prognosis based on news analysis"""
    news_impact = 0.0
    bullish_count = 0
    bearish_count = 0
    
    for item in news:
        analysis = analyze_impact(item)
        if analysis["direction"] == "BULLISH":
            bullish_count += 1
            news_impact += analysis["estimated_change"]
        elif analysis["direction"] == "BEARISH":
            bearish_count += 1
            news_impact += analysis["estimated_change"]
    
    total_impact = news_impact + (price_change * 0.5)
    
    if total_impact > 0.5:
        direction = "UP ⬆️"
    elif total_impact < -0.5:
        direction = "DOWN ⬇️"
    else:
        direction = "SIDEWAYS ↔️"
    
    total_news = len(news)
    confidence = 40 if total_news == 0 else 50 + (abs(bullish_count - bearish_count) / total_news) * 40
    
    current_price = stock.get("current_price", 100)
    
    # Dynamic volatility based on news sentiment and confidence
    base_volatility = 2.0
    sentiment_bonus = (bullish_count - bearish_count) * 0.5
    
    # Bullish: tighter downside (support at -1.5%), wider upside (+2.5%)
    if direction == "UP ⬆️":
        target_low = round(current_price * (1 - (base_volatility - sentiment_bonus)/100), 2)
        target_high = round(current_price * (1 + (base_volatility + sentiment_bonus)/100), 2)
    # Bearish: wider downside (-2.5%), tighter upside (+1.5%)
    elif direction == "DOWN ⬇️":
        target_low = round(current_price * (1 - (base_volatility + abs(sentiment_bonus))/100), 2)
        target_high = round(current_price * (1 + (base_volatility - abs(sentiment_bonus))/100), 2)
    # Neutral/Sideways: balanced ±2%
    else:
        target_low = round(current_price * (1 - base_volatility/100), 2)
        target_high = round(current_price * (1 + base_volatility/100), 2)
    
    # Calculate expected move percentage for display
    expected_move_pct = round(((target_high - target_low) / current_price) * 100, 1)
    
    return {
        "direction": direction,
        "target_low": target_low,
        "target_high": target_high,
        "expected_move": expected_move_pct,
        "confidence": confidence,
        "bullish_news": bullish_count,
        "bearish_news": bearish_count
    }

def summarize_headline(title: str) -> str:
    """Extract meaningful summary from headline - kept for compatibility"""
    import re
    t = title.lower()
    
    if any(x in t for x in ["downgrade", "bearish", "drops", "falls"]):
        return "Stock declining — selling pressure continues"
    if any(x in t for x in ["upgrade", "bullish", "rall", "soars"]):
        return "Stock rallying — buying momentum building"
    if "earnings" in t:
        return "Earnings in focus — results could trigger movement"
    if "regulation" in t or "lawsuit" in t:
        return "Regulatory/legal risks could impact outlook"
    
    return "Market news update"

def get_actionable_insight(title: str, direction: str, symbol: str) -> str:
    """Generate actionable insight based on news content"""
    t = title.lower()
    
    if direction == "BULLISH":
        if "earnings" in t:
            return "Earnings beat — watch for post-earnings dip buying opportunity"
        if "upgrade" in t:
            return "Analyst upgrade — price target raised, bullish momentum likely"
        if "growth" in t:
            return "Strong growth metrics — consider adding on any pullback"
        if "acquisition" in t or "partnership" in t:
            return "Strategic deal — could unlock new revenue streams"
        if "revenue" in t and "beat" in t:
            return "Revenue beat expectations — momentum likely to continue"
        return "Positive news — monitor for continuation"
    
    elif direction == "BEARISH":
        if "earnings" in t:
            return "Earnings miss — avoid, watch for further downside"
        if "downgrade" in t:
            return "Analyst downgrade — price target cut, bearish outlook"
        if "lawsuit" in t or "investigation" in t:
            return "Legal headwind — uncertainty suggests caution"
        if "miss" in t:
            return "Results missed estimates — selling pressure likely"
        if "cut" in t and ("guidance" in t or "forecast" in t):
            return "Guidance cut — expect continued weakness"
        return "Negative news — monitor for breakdown"
    
    return "Monitor for break"  # NEUTRAL

# ============================================================================
# REPORT GENERATION
# ============================================================================

def load_stocks() -> Dict:
    """Load stock configuration from stocks.json with error handling"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            stocks = json.load(f)
        logger.info(f"Loaded {len(stocks.get('watchlist_Nasdaq', []))} NASDAQ stocks")
        return stocks
    except FileNotFoundError:
        logger.error(f"Config file not found: {CONFIG_FILE}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading stocks: {e}")
        raise

def generate_report(stocks_data: Dict) -> str:
    """Generate the daily stock brief report with error handling"""
    date_str = datetime.now().strftime('%b %d, %Y')
    report = f"📈 DAILY STOCK BRIEF — {date_str}\n"
    report += "─" * 40 + "\n\n"
    
    stocks_processed = 0
    stocks_failed = 0
    
    if "watchlist_Nasdaq" in stocks_data:
        for stock in stocks_data["watchlist_Nasdaq"]:
            symbol = stock["symbol"]
            
            try:
                current_price = get_yahoo_price(symbol)
                
                if current_price is None:
                    stocks_failed += 1
                    logger.error(f"Failed to get price for {symbol}")
                    continue
                
                stock["current_price"] = current_price
                price_change = get_price_change(symbol)
                stock["price_change"] = price_change
                
                news = fetch_news_simple(symbol)
                prognosis = generate_prognosis(stock, news, price_change)
                
                emoji = "📉" if price_change < 0 else "📈"
                arrow = "▼" if price_change < 0 else "▲"
                direction_emoji = "⬇️" if prognosis["direction"] == "DOWN ⬇️" else ("⬆️" if prognosis["direction"] == "UP ⬆️" else "↔️")
                
                report += f"{emoji} {symbol} ${current_price:.2f} {arrow}{price_change:+.1f}%\n"
                report += f"   🎯 Exp: ${prognosis['target_low']:.2f}-{prognosis['target_high']:.2f} (+{prognosis['expected_move']:.1f}%) | {direction_emoji} {int(prognosis['confidence'])}%\n"
                
                for i, item in enumerate(news[:3], 1):
                    title = item.get("title", "")
                    source = item.get("source", "")
                    pub_date = item.get("date", 0)
                    if pub_date:
                        date_str = datetime.fromtimestamp(pub_date).strftime('%b %d')
                    else:
                        date_str = "Today"
                    
                    # Show REAL headline, not generic summary
                    report += f"   {i}. {title}\n"
                    report += f"      {source} | {date_str}\n"
                    
                    # Add INSIGHT with actionable analysis
                    analysis = analyze_impact(item)
                    if analysis["direction"] != "NEUTRAL":
                        insight = get_actionable_insight(title, analysis["direction"], symbol)
                        report += f"   💡 {insight}\n"
                
                report += "\n"
                stocks_processed += 1
                time.sleep(0.5)
                
            except Exception as e:
                stocks_failed += 1
                logger.error(f"Error processing {symbol}: {e}")
    
    report += f"─" * 40 + "\n"
    report += f"🤖 Generated: {datetime.now().strftime('%H:%M')} | ⚠️ Not financial advice"
    report += f"\n✅ Processed: {stocks_processed} | ❌ Failed: {stocks_failed}"
    
    logger.info(f"Report generated: {stocks_processed} stocks, {stocks_failed} failed")
    return report

# ============================================================================
# TELEGRAM
# ============================================================================

def send_telegram_message(message: str, bot_token: str, chat_id: str) -> bool:
    """Send report to Telegram with retry"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Sending Telegram (attempt {attempt}/{MAX_RETRIES})...")
            response = requests.post(url, json=data, timeout=15)
            if response.status_code == 200:
                logger.info("Telegram message sent successfully")
                return True
            else:
                logger.warning(f"Telegram returned status {response.status_code}")
        except Exception as e:
            logger.error(f"Telegram error (attempt {attempt}): {e}")
        
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
    
    logger.error("Failed to send Telegram message after all retries")
    return False

# ============================================================================
# TELEGRAM COMMANDS
# ============================================================================

def handle_command(command: str, args: str) -> str:
    """Handle Telegram bot commands"""
    command = command.lower().strip()
    
    if command == "/price":
        return cmd_price(args)
    elif command == "/news":
        return cmd_news(args)
    elif command == "/alert":
        return cmd_alert(args)
    elif command == "/alerts":
        return cmd_list_alerts()
    elif command == "/help":
        return cmd_help()
    elif command == "/start":
        return cmd_start()
    else:
        return f"❓ Unknown command: {command}\nUse /help for available commands."

def cmd_price(symbol: str) -> str:
    """Get current price for a stock"""
    symbol = symbol.upper().strip()
    if not symbol:
        return "❌ Please specify a symbol: /price MSFT"
    
    price = get_yahoo_price(symbol)
    if price is None:
        return f"❌ Could not fetch price for {symbol}"
    
    change = get_price_change(symbol)
    emoji = "📉" if change < 0 else "📈"
    arrow = "▼" if change < 0 else "▲"
    
    return f"{emoji} *{symbol}* ${price:.2f} {arrow}{change:+.1f}%"

def cmd_news(symbol: str) -> str:
    """Get latest news for a stock"""
    symbol = symbol.upper().strip()
    if not symbol:
        return "❌ Please specify a symbol: /news MSFT"
    
    news = fetch_news_simple(symbol)
    if not news:
        return f"❌ No news found for {symbol}"
    
    response = f"📰 *Latest News for {symbol}*\n" + "─" * 30 + "\n"
    
    for i, item in enumerate(news[:3], 1):
        title = item.get("title", "No title")[:80]
        source = item.get("source", "Unknown")
        pub_date = item.get("date", 0)
        if pub_date:
            from datetime import datetime
            date_str = datetime.fromtimestamp(pub_date).strftime('%b %d')
        else:
            date_str = "Today"
        
        response += f"\n{i}. {title}\n"
        response += f"   {source} | {date_str}"
    
    return response

def cmd_alert(args: str) -> str:
    """Set a price alert (simplified version)"""
    parts = args.split()
    if len(parts) < 2:
        return """📢 *Price Alert*

Usage: `/alert MSFT 450` - Alert when MSFT hits $450

Alert types:
- `/alert MSFT 450` - Alert when price reaches $450
- `/alert MSFT 450+` - Alert when price goes above $450
- `/alert MSFT 450-` - Alert when price goes below $450

Note: Alerts are stored locally. Check with /alerts"""
    
    try:
        symbol = parts[0].upper()
        target_price = float(parts[1].replace('+', '').replace('-', ''))
        direction = "above" if '+' in parts[1] else ("below" if '-' in parts[1] else "at")
        
        # Store alert (append to file)
        alert_line = f"{symbol},{target_price},{direction},{datetime.now().isoformat()}\n"
        with open("alerts.txt", "a") as f:
            f.write(alert_line)
        
        return f"✅ Alert set: Notify when *{symbol}* goes {direction} ${target_price:.2f}"
    except ValueError:
        return "❌ Invalid format. Use: /alert MSFT 450"

def cmd_help() -> str:
    """Show help message"""
    return """📊 *Daily Stock Bot Commands*

/price MSFT     - Get current price & change
/news MSFT      - Get latest news (3 articles)
/alert MSFT 450 - Set price alert
/alerts         - List all active alerts
/help           - Show this help message

*Daily Reports:* Sent automatically at 8 AM"""

def cmd_start() -> str:
    """Welcome message"""
    return """👋 *Welcome to Daily Stock Bot!*

Get real-time stock information and news.

📈 */price MSFT* - Current price & daily change
📰 */news MSFT*  - Latest news & analysis  
📢 */alert MSFT 450* - Set price alerts

📅 Daily reports sent at 8 AM
Use /help for all commands"""

def cmd_list_alerts() -> str:
    """List all active alerts"""
    try:
        with open("alerts.txt", "r") as f:
            alerts = f.readlines()
        
        if not alerts:
            return "📢 No active alerts. Use /alert MSFT 450 to create one."
        
        response = "📢 *Active Alerts*\n" + "─" * 30 + "\n"
        for alert in alerts:
            parts = alert.strip().split(',')
            if len(parts) >= 3:
                response += f"• {parts[0]}: ${parts[1]} ({parts[2]})\n"
        
        return response
    except FileNotFoundError:
        return "📢 No active alerts. Use /alert MSFT 450 to create one."

def parse_telegram_update(update: dict) -> tuple:
    """Parse Telegram webhook update and return (command, args, chat_id)"""
    try:
        message = update.get("message", {})
        chat = message.get("chat", {})
        chat_id = chat.get("id")
        text = message.get("text", "")
        
        if text.startswith("/"):
            parts = text.split(" ", 1)
            command = parts[0]
            args = parts[1] if len(parts) > 1 else ""
            return command, args, chat_id
        
        return None, None, chat_id
    except Exception as e:
        logger.error(f"Error parsing Telegram update: {e}")
        return None, None, None

def health_check() -> bool:
    """Verify critical dependencies before running"""
    checks = []
    checks.append(("Config file", os.path.exists(CONFIG_FILE)))
    checks.append(("Telegram token", bool(TELEGRAM_BOT_TOKEN)))
    checks.append(("Telegram chat_id", bool(TELEGRAM_CHAT_ID)))
    
    for name, passed in checks:
        status = "✅" if passed else "❌"
        logger.info(f"{status} {name}")
    
    return all(passed for _, passed in checks)

# ============================================================================
# WEBHOOK HANDLER (Optional)
# ============================================================================

def run_webhook(host: str = "0.0.0.0", port: int = 5000):
    """Run Flask webhook server for Telegram commands"""
    try:
        from flask import Flask, request, jsonify
    except ImportError:
        logger.error("Flask not installed. Run: pip install flask")
        return
    
    app = Flask(__name__)
    
    @app.route(f"/webhook/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
    def telegram_webhook():
        """Handle incoming Telegram updates"""
        try:
            update = request.get_json()
            logger.info(f"Received Telegram update: {update.get('message', {}).get('text', 'unknown')}")
            
            command, args, chat_id = parse_telegram_update(update)
            
            if command:
                response = handle_command(command, args)
                send_telegram_message(response, TELEGRAM_BOT_TOKEN, str(chat_id))
                return jsonify({"status": "ok"})
            else:
                return jsonify({"status": "ignored"})
                
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    
    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})
    
    logger.info(f"Starting webhook server on {host}:{port}")
    app.run(host=host, port=port, debug=False)

def main():
    """Main function with error handling"""
    import sys
    
    # Check for webhook mode
    if len(sys.argv) > 1 and sys.argv[1] == "--webhook":
        logger.info("Starting in webhook mode...")
        run_webhook()
        return
    
    logger.info("=" * 50)
    logger.info("Starting Daily Stock Brief v2.1 (yfinance)")
    
    if not health_check():
        logger.error("Health check failed!")
        return
    
    try:
        stocks_data = load_stocks()
        report = generate_report(stocks_data)
        logger.info("Report generated successfully")
        
        print("\n" + "=" * 50)
        print(report)
        print("=" * 50)
        
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            if send_telegram_message(report, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID):
                logger.info("Report sent to Telegram")
            else:
                logger.error("Failed to send to Telegram")
        else:
            logger.warning("Telegram not configured")
        
        logger.info("Daily Stock Brief completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    main()
