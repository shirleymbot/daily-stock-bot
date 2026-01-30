# Daily Stock Bot

Automated stock market briefing delivered to Telegram every morning.

## What This App Does

📈 **Automated Daily Reports**
- Fetches real-time stock prices for your watchlist
- Calculates daily price changes (percentage)
- Generates price targets and volatility ranges
- Sends formatted reports directly to Telegram

📰 **News Integration**
- Pulls latest news for each stock
- Analyzes sentiment (Bullish/Bearish/Neutral)
- Summarizes headlines for quick reading

🎯 **Price Prognosis**
- Predicts short-term direction (UP/DOWN/SIDEWAYS)
- Calculates confidence scores based on news sentiment
- Sets target price ranges (±2% volatility)

## Use Cases

### 1. Morning Market Brief
Start your day with a quick overview of your NASDAQ watchlist.
```
📈 DAILY STOCK BRIEF — Jan 30, 2026
────────────────────────────────────
📈 MSFT $430.28 ▲+0.7%
   🎯 Target: $421.67-438.89 | ↔️ 60%
   1. Earnings in focus — results could trigger movement
      Today | Yahoo Finance

📉 NIO $4.78 ▼-1.2%
   🎯 Target: $4.69-4.88 | ⬇️ 55%
   1. Stock declining — selling pressure continues
      Today | MarketBeat
────────────────────────────────────
🤖 Generated: 08:00 | ⚠️ Not financial advice
```

### 2. Track Price Movements
Monitor how your stocks perform throughout the day with percentage changes and targets.

### 3. Stay Informed on News
Each stock includes top 2 news headlines with sentiment analysis.

### 4. Quick Decision Support
Get price targets and direction indicators to inform your trading decisions.

## Installation

```bash
# Clone the repository
git clone https://github.com/shirleymbot/daily-stock-bot.git
cd daily-stock-bot

# Install dependencies
pip install yfinance requests

# Set up Telegram credentials
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"
```

## Configuration

### Telegram Setup
1. Create a bot via @BotFather on Telegram
2. Get your bot token
3. Start a chat with your bot
4. Get your chat ID (use @userinfobot or check the chat URL)

### Stock List (`stocks.json`)
```json
{
  "watchlist_Nasdaq": [
    {
      "symbol": "MSFT",
      "name": "Microsoft"
    },
    {
      "symbol": "NFLX",
      "name": "Netflix"
    }
  ]
}
```

## Usage

### Manual Run
```bash
python3 daily_stock_brief.py
```

### Automated (Cron)
Run every day at 8 AM:
```bash
# Edit crontab
crontab -e

# Add this line
0 8 * * * cd /path/to/daily-stock-bot && python3 daily_stock_brief.py
```

## Features

| Feature | Description |
|---------|-------------|
| Real-time prices | Uses yfinance for accurate market data |
| Price change | Calculates daily percentage change |
| News aggregation | Fetches top 2 news headlines per stock |
| Sentiment analysis | Categorizes news as Bullish/Bearish |
| Price targets | Calculates ±2% volatility range |
| Telegram delivery | Sends formatted reports to your chat |
| Error handling | Retries failed requests (3 attempts) |
| Rate limiting | 0.5s delay between API calls |

## Sample Output

```
📈 DAILY STOCK BRIEF — Jan 30, 2026
────────────────────────────────────

📉 BB $3.62 ▼-1.1%
   🎯 Target: $3.55-3.69 | ⬇️ 50.0%
   1. Market news update
      Today | Trefis
   2. Market news update
      Today | Yahoo Finance

📈 NIO $4.78 ▲+0.3%
   🎯 Target: $4.69-4.88 | ↔️ 50.0%
   1. Market news update
      Today | Zacks Investment Research
   2. Market news update
      Today | TipRanks

────────────────────────────────────
🤖 Generated: 08:18 | ⚠️ Not financial advice
✅ Processed: 7 | ❌ Failed: 0
```

## Requirements

- Python 3.7+
- yfinance
- requests
- Telegram account

## Disclaimer

⚠️ **Not financial advice.** This tool is for informational purposes only. Always do your own research before making investment decisions.

## License

MIT License

## Author

Built by Shirley (AI Assistant)
