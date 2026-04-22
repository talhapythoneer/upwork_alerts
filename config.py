import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REQUIRED_FILES_DIR = BASE_DIR / "requiredFiles"

# Credentials are read from environment variables so source files stay shareable.
UPWORK_EMAIL = os.getenv("UPWORK_EMAIL", "your_email@example.com")
UPWORK_PASSWORD = os.getenv("UPWORK_PASSWORD", "your_password_here")
UPWORK_OAUTH_TOKEN = os.getenv("UPWORK_OAUTH_TOKEN", "your_oauth_token_here")
UPWORK_COOKIE = os.getenv("UPWORK_COOKIE", "")

CHROMEDRIVER_PATH = REQUIRED_FILES_DIR / "chromedriver.exe"
COVER_LETTER_PATH = REQUIRED_FILES_DIR / "cover_scraping.txt"
PROCESSED_JOBS_PATH = REQUIRED_FILES_DIR / "processed_jobs.txt"
NOTIFICATION_SOUND_PATH = REQUIRED_FILES_DIR / "MoreBoxes.wav"

HOURLY_BUDGET_MIN_THRESHOLD = 10
HOURLY_BUDGET_MAX_THRESHOLD = 20
FIXED_BUDGET_THRESHOLD = 50
TOTAL_HIRES_THRESHOLD = 1
TOTAL_SPENT_THRESHOLD = 50
TOTAL_FEEDBACK_THRESHOLD = 4
AVG_SPENT_THRESHOLD = 40

NEGATIVE_KEYWORDS = [
    "trading bot",
    "puppeteer",
    "data entry",
    "scrape video",
    "tiktok",
    "instagram",
    "facebook",
    "linkedin",
    "reddit",
    "telegram",
    "chrome extension",
    "pine script",
    "pinescript",
    "google apps script",
    "vba",
    "zapier",
]

NEGATIVE_COUNTRIES = [
    "india",
    "pakistan",
    "bangladesh",
    "nigeria",
    "philippines",
    "indonesia",
    "kenya",
    "ghana",
]

REQUEST_HEADERS_BASE = {
    "User-Agent": os.getenv(
        "UPWORK_USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/127.0",
    ),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Content-Type": "application/json",
    "X-Upwork-Accept-Language": "en-US",
    "Origin": "https://www.upwork.com",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Connection": "keep-alive",
    "Alt-Used": "www.upwork.com",
    "Priority": "u=1",
    "TE": "trailers",
}


def get_api_headers(referer: str) -> dict:
    headers = dict(REQUEST_HEADERS_BASE)
    headers["Referer"] = referer

    if UPWORK_OAUTH_TOKEN and UPWORK_OAUTH_TOKEN != "your_oauth_token_here":
        headers["Authorization"] = f"bearer oauth2v2_{UPWORK_OAUTH_TOKEN}"

    if UPWORK_COOKIE:
        headers["Cookie"] = UPWORK_COOKIE

    return headers
