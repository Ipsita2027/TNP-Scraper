# 📢 Automated News & Announcement Scraper (with Telegram Alerts)

This project is a Python-based automation tool that logs into a portal using Playwright, scrapes the latest announcements/news, and sends updates via Telegram notifications. It also tracks previously fetched data to avoid duplicate alerts.

---

## 🚀 Features

- Automated login using Playwright
- Scrapes announcements/news from a dashboard
- Detects new updates using timestamp comparison
- Stores last fetched state locally (`state.json`)
- Sends notifications via Telegram bot
- Avoids duplicate alerts
- Basic error handling and fallback alerts

---

## 🧰 Tech Stack

- Python 3.x
- Playwright
- Requests
- Telegram Bot API
- JSON for state tracking
- Environment variables for credentials

---