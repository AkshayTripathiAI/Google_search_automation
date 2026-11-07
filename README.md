# Google_search_automation

A Python + Selenium 4 command-line script that runs a Google search in Chrome and prints the top organic results (title and URL), plus the result-count text when Google shows it. It can also print the results as JSON.

## What it does

[`main.py`](main.py) defines a `GoogleSearchAutomation` class that:

1. Starts Chrome (optionally headless). Selenium Manager finds or downloads a matching ChromeDriver, so no driver binary is needed.
2. Opens `https://www.google.com/` and accepts or rejects the cookie-consent dialog if one appears (EU/UK).
3. Waits for the search box (`name="q"`), types the query and presses Enter.
4. Waits for the results container (`#search`) and collects the first N unique organic results (`#search a h3`).
5. Prints them, along with `#result-stats` (for example "About 1,230,000 results") when Google renders it.
6. Quits the browser.

Every step uses an explicit `WebDriverWait`. If Google shows its "unusual traffic" CAPTCHA, or the page does not load, the script prints a clear error and exits with a non-zero code.

## Tech stack

- Python 3.9+
- Selenium 4.15+ (uses Selenium Manager to resolve the driver)
- Google Chrome

## Setup

```bash
git clone https://github.com/AkshayTripathiAI/Google_search_automation.git
cd Google_search_automation
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

You need Google Chrome installed. There is no driver to download.

## Usage

```bash
python main.py                                  # search "Nature Images", print top 5
python main.py --query "selenium python" -n 10
python main.py -q "weather in pune" --headless
python main.py -q "openai" --json > results.json
```

| Option | Default | Description |
| --- | --- | --- |
| `-q`, `--query` | `Nature Images` | Search term |
| `-n`, `--results` | `5` | Number of results to print |
| `--headless` | off | Run Chrome without a window |
| `--timeout` | `15` | Seconds to wait for page elements |
| `--lang` | `en` | Google interface language |
| `--json` | off | Print `{query, stats, results:[{title,url}]}` as JSON |

Example output:

```
Query: selenium python
 1. Selenium with Python — Selenium Python Bindings documentation
    https://selenium-python.readthedocs.io/
 2. ...
```

Exit codes: `0` success, `1` browser could not start or crashed, `2` an automation step failed (message on stderr).

## Project structure

```
Google_search_automation/
├── main.py            # GoogleSearchAutomation + argparse CLI
├── requirements.txt
└── README.md
```

## Note

This script automates a third-party website. It can stop working when Google changes its markup, and Google may show a CAPTCHA to automated browsers, more often in headless mode. Automated querying may also be subject to Google's terms of service. The script is meant for learning Selenium, not for scraping at scale.
