# Daily Stock Bot

Automated stock market briefing delivered to Telegram every morning. Supports both scheduled daily reports and on-demand commands via Telegram.

## Features

### 📈 Daily Reports
- Fetches real-time stock prices for your watchlist
- Calculates daily price changes (percentage)
- Generates dynamic price targets based on news sentiment
- Sends formatted reports directly to Telegram at 8 AM

### 📰 News Integration
- Pulls latest news from Yahoo Finance
- Analyzes sentiment (Bullish/Bearish/Neutral)
- Provides actionable insights for each headline

### 💬 Telegram Commands
On-demand queries via Telegram bot:
- `/price MSFT` - Get current price and change
- `/news NFLX` - Get latest news (3 articles)
- `/alert MSFT 450` - Set price alert
- `/alerts` - List active alerts
- `/help` - Show all commands

## Installation

```bash
# Clone the repository
git clone https://github.com/shirleymbot/daily-stock-bot.git
cd daily-stock-bot

# Install dependencies
pip install yfinance requests flask
```

## Configuration

### Telegram Setup
1. Create a bot via @BotFather on Telegram
2. Get your bot token
3. Start a chat with your bot
4. Get your chat ID (use @userinfobot or check the chat URL)

### Environment Variables
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"
```

### Stock List (`stocks.json`)
```json
{
  "watchlist_Nasdaq": [
    {"symbol": "MSFT", "name": "Microsoft"},
    {"symbol": "NFLX", "name": "Netflix"},
    {"symbol": "BB", "name": "BlackBerry"},
    {"symbol": "NCLH", "name": "Norwegian Cruise Line"},
    {"symbol": "NIO", "name": "NIO Inc"},
    {"symbol": "API", "name": "Agora"},
    {"symbol": "PYPL", "name": "PayPal"}
  ]
}
```

## Usage

### Option 1: Daily Report Only (No Commands)
```bash
python3 daily_stock_brief.py
```

### Option 2: With On-Demand Commands (Webhook Mode)
Requires ngrok for Telegram to reach your local server.

```bash
# Start the webhook server
python3 daily_stock_brief.py --webhook
```

**Note:** For Telegram to reach your bot, you need ngrok (see below).

## Telegram Webhook Setup (For On-Demand Commands)

### Step 1: Install ngrok
Download from https://ngrok.com/download or on Linux:
```bash
curl -s https://ngrok.io/download.sh | bash
```

### Step 2: Set Telegram Webhook
Replace `<TOKEN>` with your bot token and `<NGROK_URL>` with your ngrok URL:
```bash
curl -F "url=https://<NGROK_URL>/webhook/<TOKEN>" https://api.telegram.org/bot<TOKEN>/setWebhook
```

### Step 3: Start the Bot
```bash
python3 daily_stock_brief.py --webhook
```

## 24/7 Operation (Linux with systemd)

### Install as System Services

```bash
# Copy service files
sudo cp daily-stock-bot.service /etc/systemd/system/
sudo cp ngrok.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable services (start on boot)
sudo systemctl enable daily-stock-bot
sudo systemctl enable ngrok

# Start services now
sudo systemctl start daily-stock-bot
sudo systemctl start ngrok

# Check status
sudo systemctl status daily-stock-bot
sudo systemctl status ngrok
```

### Manage Services
```bash
# Stop
sudo systemctl stop daily-stock-bot
sudo systemctl stop ngrok

# Restart
sudo systemctl restart daily-stock-bot
sudo systemctl restart ngrok

# View logs
journalctl -u daily-stock-bot -n 50
journalctl -u ngrok -n 50
```

## Telegram Commands

| Command | Description |
|---------|-------------|
| `/price MSFT` | Get current price and daily change |
| `/news NFLX` | Get latest news (3 articles) |
| `/alert MSFT 450` | Set price alert at $450 |
| `/alert MSFT 450+` | Alert when price goes above $450 |
| `/alert MSFT 450-` | Alert when price goes below $450 |
| `/alerts` | List all active alerts |
| `/help` | Show help message |

## Sample Output

### Daily Report
```
📈 DAILY STOCK BRIEF — Jan 30, 2026
────────────────────────────────────

📈 NFLX $83.46 ▲+0.4%
   🎯 Exp: $81.80-85.13 (+4.0%) | ↔️ 50%
   1. Netflix Warner Bros. Discovery Deal Tests Growth Story...
      Yahoo Finance | Jan 30
   💡 Strong growth metrics — consider adding on any pullback
   2. Is Artificial Intelligence Ready For Its Close-Up?...
      Yahoo Finance | Jan 30
   3. What's next for Netflix with shares down 35%...
      Yahoo Finance | Jan 30

📉 MSFT $430.80 ▼-0.6%
   🎯 Exp: $420.03-437.26 (+4.0%) | ⬇️ 63%
   1. Earnings live: Sandisk stock soars on profit beat...
      Yahoo Finance | Jan 30
   💡 Earnings beat — watch for post-earnings dip buying opportunity
   2. Stock market today: S&P 500, Nasdaq fall as Microsoft...
      Yahoo Finance | Jan 29

────────────────────────────────────
🤖 Generated: 20:33 | ⚠️ Not financial advice
✅ Processed: 7 | ❌ Failed: 0
```

### Command Response
```
/price MSFT
📉 *MSFT* $430.57 ▼-0.7%
```

```
/news NFLX
📰 *Latest News for NFLX*
──────────────────────────────

1. Netflix Warner Bros. Discovery Deal Tests Growth Story And Valuation A
   Yahoo Finance | Jan 30
2. Is Artificial Intelligence Ready For Its Close-Up? Hollywood vs. The T
   Yahoo Finance | Jan 30
3. What's next for Netflix with shares down 35% from its 52-week high?
   Yahoo Finance | Jan 30
```

## Requirements

- Python 3.7+
- yfinance
- requests
- flask (for webhook mode)
- Telegram account
- ngrok (for on-demand commands, optional)

## Files

| File | Description |
|------|-------------|
| `daily_stock_brief.py` | Main application |
| `stocks.json` | Stock watchlist configuration |
| `daily-stock-bot.service` | systemd service for the bot |
| `ngrok.service` | systemd service for ngrok tunnel |

## Disclaimer

⚠️ **Not financial advice.** This tool is for informational purposes only. Always do your own research before making investment decisions.

## License

MIT License

## Author

Built by Shirley (AI Assistant)
