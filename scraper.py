import requests
import sys
import json
from dotenv import load_dotenv
import os
from playwright.sync_api import sync_playwright
from datetime import datetime, timezone, timedelta

load_dotenv()

IST = timezone(timedelta(hours=5, minutes=30))

TNP_URL="https://tp.bitmesra.co.in/"
LOGIN_URL="https://tp.bitmesra.co.in/login.html"
TELEGRAM_URL="https://api.telegram.org"
NEWS_EVENTS_URL="https://tp.bitmesra.co.in/newsevents"

SELECTOR_USERNAME="#identity"
SELECTOR_PASSWORD="#password"
SELECTOR_LOGIN_BUTTON="input[name='submit']"
SELECTOR_TABLE="#newsevents tbody tr"
SELECTOR_JOB_LISTINGS="#job-listings_wrapper"

def ping_telegram(message):
    url=f"{TELEGRAM_URL}/bot{os.getenv("TELEGRAM_BOT_TOKEN")}/sendMessage"
    payload={
        "chat_id":os.getenv("TELEGRAM_CHAT_ID"),
        "text":message,
        "parse_mode":"Markdown"
    }

    try:
        response=requests.post(url,json=payload)
        if response.status_code==200:
            pass
        else:
            print(f"Failed. Error code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error, {e.message}")

def parse_dt(s):
    return datetime.strptime(s, "%d/%m/%Y %H:%M IST").replace(tzinfo=IST)

def structurefine(announcements):
    """
    a list of list of strings(text)
    """
    latest=parse_dt(announcements[0][-2])
    with open("state.json", "r") as f:
        data = json.load(f)
    last_fetched = datetime.fromisoformat(data["last_fetched"])

    if latest>last_fetched:
        with open("state.json","w") as f:
            json.dump({"last_fetched":latest.isoformat()},f,indent=2)

        for newsevent in announcements:
            date=parse_dt(newsevent[-2])
            if date>last_fetched:
                message=f"News: {newsevent[0]} \n Date of News: {newsevent[1]} \n Link {newsevent[2]}"
                ping_telegram(message)
    else:
        ping_telegram("No new announcements")

def main():
    USERNAME,PASSWORD=os.getenv("USERNAME_TP"),os.getenv("PASSWORD_TP")
    if not USERNAME or not PASSWORD:
        print("Error: Username or Password not configured")
        sys.exit(1)

    with sync_playwright() as p:
        print("launching browser")
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()

        try:
            print(f"Navigating to {LOGIN_URL}")
            page.goto(LOGIN_URL,wait_until="networkidle")

            print("Entering login credentials")
            page.wait_for_selector(SELECTOR_USERNAME, timeout=10000)
            page.fill(SELECTOR_USERNAME,USERNAME)
            page.fill(SELECTOR_PASSWORD,PASSWORD)

            print("Clicking login button")
            page.click(SELECTOR_LOGIN_BUTTON)

            print("Waiting for dashboard loading")
            page.wait_for_selector(SELECTOR_JOB_LISTINGS)
            page.goto(NEWS_EVENTS_URL,wait_until="networkidle")
            

            rows=page.locator(SELECTOR_TABLE)
            news=[]

            for i in range(rows.count()):
                row=rows.nth(i)
                cells=row.locator("td").all_text_contents()

                el=row.locator("td > div > h6 > a")

                if el.count()>0:
                    cells.append(TNP_URL+str(el.first.get_attribute("href")))
                else:
                    cells.append("No links available")

                news.append(cells)
            structurefine(news)

        except Exception as e:
            print(f"An exception occured:{e.message}")
            ping_telegram("Could not fetch the announcements")



if __name__ == "__main__":
    main()