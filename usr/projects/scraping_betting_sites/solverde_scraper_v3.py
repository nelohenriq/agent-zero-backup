
import json
import os
import time
from playwright.sync_api import sync_playwright, Response

PROJECT_DIR = "/a0/usr/projects/scraping_betting_sites"
OUTPUT_FILE = os.path.join(PROJECT_DIR, "processed_sports", "solverde_matches.json")

def is_match_data(response: Response):
    try:
        if response.status != 200:
            return False
        content_type = response.headers.get("content-type", "").lower()
        if "application/json" not in content_type:
            return False

        body = response.body()
        if not body:
            return False

        text = body.decode("utf-8", errors="ignore")
        if len(text) < 50:
            return False

        keywords = ["odds", "events", "competitions", "markets", "teams", "homeTeam", "awayTeam", "selections", "games", "match"]
        text_lower = text.lower()
        if any(k in text_lower for k in keywords):
            return True
    except Exception:
        pass
    return False

def scrape_solverde():
    print("🚀 Starting Solverde Scraper (XHR Interception v3)...")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    captured_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        def handle_response(response):
            if is_match_data(response):
                try:
                    body = response.body()
                    data = json.loads(body.decode("utf-8", errors="ignore"))
                    captured_data.append({
                        "url": response.url,
                        "status": response.status,
                        "data": data
                    })
                    print(f"🔍 Captured match data from: {response.url}")
                except Exception as e:
                    print(f"⚠️ Error parsing response from {response.url}: {e}")

        context.on("response", handle_response)

        page = context.new_page()
        print("🌐 Navigating to solverde.pt...")
        try:
            page.goto("https://www.solverde.pt/", wait_until="networkidle", timeout=30000)
            print("✅ Page loaded. Waiting for dynamic content...")
            time.sleep(5)

            # Try to navigate to sports section if available
            try:
                page.goto("https://www.solverde.pt/futebol", wait_until="networkidle", timeout=30000)
                print("✅ Navigated to football section.")
                time.sleep(5)
            except Exception as e:
                print(f"⚠️ Could not navigate to football section: {e}")

            # Scroll to trigger lazy loading
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(3)
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(2)

        except Exception as e:
            print(f"❌ Navigation error: {e}")
        finally:
            browser.close()

    if captured_data:
        print(f"\n📊 Total captured responses: {len(captured_data)}")
        best_data = None
        max_matches = 0

        for item in captured_data:
            data = item.get("data", {})
            if isinstance(data, dict) and "data" in data:
                data = data["data"]

            count = 0
            if isinstance(data, list):
                count = len(data)
            elif isinstance(data, dict):
                for key in ["events", "competitions", "matches", "games", "topEvents", "leagues"]:
                    if key in data and isinstance(data[key], list):
                        count = len(data[key])
                        break

            if count > max_matches:
                max_matches = count
                best_data = data

        if best_data:
            structured_output = {
                "site": "solverde.pt",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "raw_source_url": None,
                "data": best_data
            }

            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(structured_output, f, indent=2, ensure_ascii=False)

            print(f"✅ Saved structured data to: {OUTPUT_FILE}")
            print(f"📈 Found {max_matches} potential match entries.")

            if isinstance(best_data, list) and len(best_data) > 0:
                print("\n📝 Sample entry:")
                print(json.dumps(best_data[0], indent=2, ensure_ascii=False)[:1500])
            elif isinstance(best_data, dict):
                print("\n📝 Top-level keys:")
                print(json.dumps(list(best_data.keys()), indent=2, ensure_ascii=False))
            else:
                print("❌ No valid match data structure found.")
        else:
            print("❌ No valid match data structure found.")
    else:
        print("❌ No JSON data captured with match keywords.")
        print("🔍 Attempting broader capture for debugging...")

if __name__ == "__main__":
    scrape_solverde()
