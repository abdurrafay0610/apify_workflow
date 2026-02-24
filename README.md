
---

# LinkedIn Sales Navigator Scraper (Apify Integration)

## 📌 Overview

This project is a Python-based automation tool that integrates with the Apify Actor:

> **quantifiable_extension/linkedin-sales-navigator-scraper**

It allows you to:

* Provide any LinkedIn Sales Navigator search URL
* Authenticate using your LinkedIn session cookies
* Run the Apify Sales Navigator Scraper Actor
* Retrieve structured profile results as JSON
* Control scraping parameters directly from Python

The script handles:

* Cookie loading from file
* Actor execution and polling
* Dataset retrieval
* Returning clean Python JSON output

---

## 🧠 How It Works

1. You generate LinkedIn authentication cookies.
2. Store them locally in `linkedin_cookies.json`.
3. Provide a Sales Navigator search URL.
4. The script:

   * Uses your Linkedin cookies (`linkedin_cookies.json`)
   * Sends it to the Apify Actor
   * Waits for completion
   * Returns scraped profiles as JSON

---

# 🚀 Setup Guide

## 1️⃣ Install Dependencies

```bash
pip install apify-client python-dotenv
pip install -r requirements.txt
```

---

## 2️⃣ Create Environment Variables

Create a `.env` file in the project root:

```env
APIFY_TOKEN=your_apify_api_token_here
LINKEDIN_COOKIES_FILE=linkedin_cookies.json
```

⚠️ **Never commit this file to GitHub.**

---

# 🔐 How to Get LinkedIn Cookies

This scraper requires authenticated LinkedIn cookies.

The official Apify actor instructions are available here:

[https://apify.com/quantifiable_extension/linkedin-sales-navigator-scraper](https://apify.com/quantifiable_extension/linkedin-sales-navigator-scraper)

---

## ✅ Recommended Method (Using Chrome Extension)

Install Chrome extension:

👉 Cookie Editor
[https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)

---

### Steps:

1. Log into LinkedIn Sales Navigator.
2. Open a Sales Navigator search page.
3. Click the Cookie Editor extension.
4. Click **Export**.
5. Select **JSON format**.
6. Copy the exported cookies.

---

# 📁 Store Cookies in File

Create a file named:

```
linkedin_cookies.json
```

Paste the exported JSON array into it.

Example structure:

```json
[
  {
    "domain": ".linkedin.com",
    "name": "li_at",
    "value": "AQEDARABAAAAA..."
  },
  {
    "domain": ".linkedin.com",
    "name": "JSESSIONID",
    "value": "\"ajax:123456\""
  }
]
```

⚠️ Keep this file private.

---

# 🛠 How to Use the Script

Inside your script:

```python
url = "https://www.linkedin.com/sales/search/people?query=(filters:...)"

results, meta = run_sales_nav_scraper(
    search_url=url,
    total_records=50,
    start_page=1,
    deep_scrape=False,
    min_wait_s=5,
    max_wait_s=30,
)
```

---

# ⚙️ Parameters Explained

| Parameter       | Type | Description                                            |
| --------------- | ---- | ------------------------------------------------------ |
| `search_url`    | str  | Full LinkedIn Sales Navigator search URL               |
| `total_records` | int  | Maximum number of profiles to scrape                   |
| `start_page`    | int  | Page number to begin scraping from                     |
| `deep_scrape`   | bool | If True, visits each profile for detailed extraction   |
| `min_wait_s`    | int  | Minimum wait between page loads (anti-detection delay) |
| `max_wait_s`    | int  | Maximum wait between page loads                        |
| `proxy_group`   | str  | Apify proxy group (default: RESIDENTIAL)               |
| `proxy_country` | str  | Optional proxy country code (e.g., US, GB)             |
| `timeout_s`     | int  | Max seconds to wait for Actor completion               |
| `max_items`     | int  | Limit number of dataset items returned locally         |

---

# 📦 Output

The function returns:

```python
results  # list of dicts (JSON profiles)
meta     # run metadata
```

Example:

```python
print(meta)
print(len(results))
print(results[0])
```

---

# 🧾 Example Output Structure

```json
{
  "fullName": "John Doe",
  "headline": "CEO at Example Corp",
  "company": "Example Corp",
  "location": "United States",
  "linkedinUrl": "https://www.linkedin.com/in/johndoe"
}
```

(The exact structure depends on the Actor output schema.)

---

# 🛡 Security Recommendations

* Rotate LinkedIn cookies regularly.
* Use residential proxies.
* Keep scraping volumes reasonable.
* Avoid scraping thousands of profiles per day.
* Never hardcode cookies in source files.
* Never share `li_at` publicly.

---

# ⚠️ Important Notes

* Sales Navigator scraping requires valid authenticated cookies.
* LinkedIn may invalidate sessions if scraping is aggressive.
* Cookie expiration will cause Actor failures.
* If you get `Input is not valid: Field input.cookieString is required`, ensure:

  * Cookie file is loaded correctly
  * `cookieString` is properly constructed

---

# 🧪 Troubleshooting

## JSONDecodeError when loading cookies

* Ensure `linkedin_cookies.json` is valid JSON.
* Ensure `.env` is loaded via `load_dotenv()`.

## Actor fails with authentication error

* Your `li_at` cookie may be expired.
* Re-export cookies using the Chrome extension.

---

# 🧱 Project Structure

```
project/
│
├── apify.py
├── linkedin_cookies.json
├── .env
└── README.md
```

---

# 🎯 Use Cases

* Lead generation
* ICP segmentation
* Market research
* Recruiting intelligence
* Sales automation pipelines

---

If you want, I can now:

* Make this README more enterprise/polished
* Add API mode usage
* Add Docker deployment section
* Add production hardening notes
* Or convert this into a clean GitHub-ready professional template

Just tell me your intended audience (hackathon demo vs production system vs internal tool).
