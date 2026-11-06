# Google_search_automation

A small Python + Selenium 4 script that opens Google in Chrome, searches for "Nature Images" and prints the result-count text from the results page.

## What it does

[`main.py`](main.py) defines a `GoogleSearchTest` class that:

1. Starts a Chrome WebDriver session and maximizes the window
2. Opens `https://www.google.com/`
3. Waits (up to 40 s) for the search box (`name="q"`), types `Nature Images` and submits
4. Waits (up to 10 s) for the `result-stats` element and prints its text, e.g. `Search Results: About ... results`
5. Quits the browser

The search term is hard-coded in `perform_google_search()`; edit it there to search for something else.

## Tech stack

- Python 3 (written against 3.10)
- Selenium 4
- Google Chrome + ChromeDriver

## Setup

Prerequisites: Python 3 and Google Chrome.

```bash
git clone https://github.com/AkshayTripathiAI/Google_search_automation.git
cd Google_search_automation
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install selenium
```

There is no `requirements.txt`; Selenium is the only dependency.

### Browser driver

The script creates `ChromeService()` without a driver path, so Selenium looks for a driver itself. With Selenium 4.6 or newer, Selenium Manager downloads a ChromeDriver that matches your installed Chrome automatically. On older Selenium versions, put a matching `chromedriver` on your `PATH`.

The `chromedriver_path` variable in `main.py` and the `Drivers/chromedriver` binary in the repo are left over from the original Linux setup. The path is only written to an environment variable that Selenium does not read, so it has no effect.

## Usage

```bash
python main.py
```

## Project structure

```
Google_search_automation/
├── main.py              # GoogleSearchTest: open Google, search, print result stats
├── Drivers/
│   └── chromedriver     # bundled ChromeDriver binary (Linux); not used by main.py
└── README.md
```

## Note

This script automates a third-party website. It can stop working whenever Google changes its page (element names and IDs such as `q` and `result-stats`, consent screens, bot checks), and automated querying may be subject to Google's terms of service. It is intended for learning Selenium, not for scraping.
