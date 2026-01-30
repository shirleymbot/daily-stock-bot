# Daily Stock Bot - Architecture Guide

## Overview

The Daily Stock Bot is an automated stock market briefing system that delivers real-time stock prices, news analysis, and price alerts to Telegram. This document explains the architecture and how all components work together.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DAILY STOCK BOT ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────────────────┘

                              TELEGRAM USERS
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TELEGRAM BOT API                                      │
│                     (cloud.telegram.org)                                     │
│                                                                              │
│  • Receives your messages (/price MSFT)                                     │
│  • Forwards them as HTTP POST to webhook                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTPS POST (webhook)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           NGROK TUNNEL                                       │
│                                                                              │
│  • Public URL: https://abc123.ngrok-free.dev                                │
│  • Forwards requests to localhost:5000                                      │
│  • Creates secure HTTPS tunnel                                              │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Your PC (192.168.x.x)                                               │    │
│  │                                                                     │    │
│  │   ┌─────────────────────────────────────────────────────────────┐   │    │
│  │   │              FLASK WEB SERVER (Port 5000)                   │   │    │
│  │   │                                                             │   │    │
│  │   │   ┌─────────────────────────────────────────────────────┐   │   │    │
│  │   │   │              DAILY STOCK BOT                         │   │   │    │
│  │   │   │                                                     │   │   │    │
│  │   │   │   ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │   │   │    │
│  │   │   │   │ /price CMD   │  │ /news CMD   │  │ /alert   │ │   │   │    │
│  │   │   │   └──────┬───────┘  └──────┬───────┘  └────┬─────┘ │   │   │    │
│  │   │   │          │                 │               │       │   │   │    │
│  │   │   │          └────────────┬────┴───────────────┘       │   │   │    │
│  │   │   │                       ▼                            │   │   │    │
│  │   │   │              ┌─────────────────┐                   │   │   │    │
│  │   │   │              │  COMMAND PARSER  │                   │   │   │    │
│  │   │   │              └────────┬────────┘                   │   │   │    │
│  │   │   │                       │                            │   │   │    │
│  │   │   │          ┌────────────┼────────────┐              │   │   │    │
│  │   │   │          ▼            ▼            ▼              │   │   │    │
│  │   │   │   ┌────────────┐ ┌──────────┐ ┌──────────────┐   │   │   │    │
│  │   │   │   │ get_price()│ │get_news()│ │ save_alert() │   │   │   │    │
│  │   │   │   └─────┬──────┘ └────┬─────┘ └──────┬───────┘   │   │   │    │
│  │   │   │         │             │              │           │   │   │    │
│  │   │   │         └──────┬──────┴──────┬──────┘           │   │   │    │
│  │   │   │                ▼             ▼                   │   │   │    │
│  │   │   │        ┌───────────────────────────────────┐    │   │   │    │
│  │   │   │        │         YFINANCE API              │    │   │   │    │
│  │   │   │        │   (stock prices, news, etc.)      │    │   │   │    │
│  │   │   │        └───────────────────────────────────┘    │   │   │    │
│  │   │   │                                                 │   │   │    │
│  │   │   │   ┌─────────────────────────────────────────┐   │   │   │    │
│  │   │   │   │         SEND TO TELEGRAM                │   │   │   │    │
│  │   │   │   │  (HTTP POST to Telegram Bot API)        │   │   │   │    │
│  │   │   │   └─────────────────────────────────────────┘   │   │   │    │
│  │   │   │                                                     │   │   │    │
│  │   │   └─────────────────────────────────────────────────────┘   │   │    │
│  │   │                                                               │   │    │
│  │   └───────────────────────────────────────────────────────────────┘   │    │
│                                                                              │
│   SYSTEMD SERVICES:                                                          │
│   • daily-stock-bot.service  → Starts the Flask server                      │
│   • ngrok.service            → Maintains the ngrok tunnel                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Overview

| Component | Role | Type |
|-----------|------|------|
| **Telegram** | User interface, sends/receives messages | External Service |
| **Telegram Bot API** | Cloud service, routes messages | External Service |
| **ngrok** | Creates public URL pointing to your PC | Tunnel Service |
| **Flask** | Web server, receives webhook requests | Python Web Framework |
| **Daily Stock Bot** | Business logic (commands, prices, news) | Python Application |
| **yfinance** | Data source for stock prices and news | Python Library |
| **systemd** | Keeps bot and ngrok running 24/7 | Linux Service Manager |

## Data Flow: /price MSFT Command

```
1. USER SENDS "/price MSFT" TO TELEGRAM BOT
   │
   ▼
2. TELEGRAM API RECEIVES MESSAGE
   │
   ▼
3. TELEGRAM API SENDS HTTPS POST TO NGROK URL
   Endpoint: /webhook/<TOKEN>
   │
   ▼
4. NGROK FORWARDS REQUEST TO LOCALHOST:5000
   │
   ▼
5. FLASK SERVER RECEIVES REQUEST
   Routes to webhook handler
   │
   ▼
6. COMMAND PARSER EXTRACTS "MSFT"
   │
   ▼
7. get_price() CALLS YFINANCE API
   │
   ▼
8. YFINANCE RETURNS: $430.57, -0.7%
   │
   ▼
9. BOT SENDS RESPONSE TO TELEGRAM API
   Format: 📉 *MSFT* $430.57 ▼-0.7%
   │
   ▼
10. TELEGRAM DELIVERS MESSAGE TO USER'S PHONE
```

## Component Details

### 1. Telegram Bot API
- **Role:** Acts as a bridge between users and your bot
- **How it works:** 
  - Receives messages from users
  - Forwards them as HTTP POST requests to your webhook URL
  - Sends bot responses back to users

### 2. ngrok Tunnel
- **Role:** Makes your local bot accessible from the internet
- **Why it's needed:** Telegram cannot send messages to `localhost` or private IPs
- **How it works:** Creates a public HTTPS URL that tunnels to your PC's port 5000

### 3. Flask Web Server
- **Role:** Receives and processes Telegram webhook requests
- **Port:** 5000 (default)
- **Routes:**
  - `/webhook/<TOKEN>` - Receives Telegram updates
  - `/health` - Health check endpoint

### 4. Daily Stock Bot
- **Role:** Business logic and command handling
- **Commands:**
  - `/price <SYMBOL>` - Get current price
  - `/news <SYMBOL>` - Get latest news
  - `/alert <SYMBOL> <PRICE>` - Set price alert
  - `/alerts` - List active alerts
  - `/help` - Show help message

### 5. yfinance API
- **Role:** Fetches real-time stock data
- **Data provided:**
  - Current stock prices
  - Daily price changes
  - Latest news headlines
  - Publication dates and sources

### 6. systemd Services
- **daily-stock-bot.service**
  - Starts the Flask webhook server
  - Runs as background service
  - Auto-restarts on failure
  - Starts on system boot

- **ngrok.service**
  - Maintains the ngrok tunnel
  - Runs as background service
  - Auto-restarts on failure
  - Starts on system boot

## Network Ports

| Port | Service | Description |
|------|---------|-------------|
| 5000 | Flask | Webhook server (receives Telegram updates) |
| 4040 | ngrok | Management API (check tunnel status) |

## Security Considerations

1. **Bot Token Protection**
   - Never share your Telegram bot token
   - The token is part of the webhook URL
   - Regenerate via @BotFather if exposed

2. **ngrok URL**
   - ngrok URLs are temporary
   - Each tunnel restart creates a new URL
   - Webhook URL must be updated when URL changes

3. **Local Access Only**
   - Flask server binds to 0.0.0.0 (all interfaces)
   - ngrok provides the only public access point
   - Firewall not required for basic setup

## 24/7 Operation

For the bot to run continuously without manual intervention:

```bash
# Enable services on boot
sudo systemctl enable daily-stock-bot
sudo systemctl enable ngrok

# Start services
sudo systemctl start daily-stock-bot
sudo systemctl start ngrok

# Check status
sudo systemctl status daily-stock-bot
sudo systemctl status ngrok

# View logs
journalctl -u daily-stock-bot -n 50
journalctl -u ngrok -n 50
```

## Related Documentation

- [README.md](../README) - Installation and usage guide
- [stocks.json](../stocks.json) - Stock watchlist configuration
- [daily-stock-bot.service](../daily-stock-bot.service) - Bot systemd service
- [ngrok.service](../ngrok.service) - ngrok systemd service

---

*Last Updated: January 30, 2026*
