# Upwork Alert Automation (Portfolio Template)

This repository is a sanitized portfolio version of an Upwork job-alert automation project.

## What This Project Does

- Polls Upwork GraphQL job feeds.
- Filters jobs using configurable relevance rules.
- Opens proposal pages in Selenium for manual review before submission.
- Tracks processed jobs to avoid duplicates.

## Project Structure

- `upworkAlert_v2.py`: Main automation workflow for most-recent jobs feed.
- `config.py`: Centralized configuration for credentials, paths, thresholds, and request headers.
- `.env.example`: Example environment variables file.
- `requirements.txt`: Python dependencies.
- `requiredFiles/cover_scraping.txt`: Cover letter template used in proposals.
- `requiredFiles/processed_jobs.txt`: Stores already-processed job IDs.
- `requiredFiles/MoreBoxes.wav`: Notification sound file.

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your values.
4. Ensure required files exist under `requiredFiles/`:
   - `chromedriver.exe`
   - `cover_scraping.txt`
   - `processed_jobs.txt`
   - `MoreBoxes.wav`

## Configuration

All sensitive values and file paths are centralized in `config.py` and environment variables.

Environment variables:

- `UPWORK_EMAIL`
- `UPWORK_PASSWORD`
- `UPWORK_OAUTH_TOKEN`
- `UPWORK_COOKIE` (optional)
- `UPWORK_USER_AGENT` (optional)

## Run

Most recent feed:

`python upworkAlert_v2.py`

## Notes

- This portfolio version intentionally contains placeholder credentials and template text.
- Keep real secrets in environment variables only.
- Respect Upwork terms of service and platform automation policies.
