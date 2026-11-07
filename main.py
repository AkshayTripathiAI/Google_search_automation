"""Google search automation with Selenium.

Opens Google, searches for a query and prints the top organic results
(title + URL) and, when Google shows it, the result-count text.

Example:
    python main.py --query "nature images" --results 5 --headless
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Buttons on Google's cookie-consent screen (shown in the EU/UK).
CONSENT_BUTTON_XPATH = (
    "//button[.//div[contains(., 'Accept all') or contains(., 'Reject all')]"
    " or contains(., 'Accept all') or contains(., 'Reject all') or contains(., 'I agree')]"
)


class AutomationError(RuntimeError):
    """Raised with a human-readable message when a step fails."""


@dataclass
class SearchResult:
    title: str
    url: str


class GoogleSearchAutomation:
    def __init__(self, headless: bool = False, timeout: int = 15, lang: str = "en"):
        self.timeout = timeout
        self.lang = lang

        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1366,900")
        options.add_argument(f"--lang={lang}")
        # Selenium >= 4.6 resolves a matching ChromeDriver automatically
        # (Selenium Manager), so no driver path is needed.
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, timeout)

    def _check_for_bot_page(self) -> None:
        if "/sorry/" in self.driver.current_url or self.driver.find_elements(By.ID, "captcha-form"):
            raise AutomationError(
                "Google is showing an 'unusual traffic' CAPTCHA. Try again later or run without --headless."
            )

    def _dismiss_consent(self) -> None:
        """Click through the cookie-consent dialog if Google shows one."""
        try:
            button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, CONSENT_BUTTON_XPATH))
            )
            button.click()
        except TimeoutException:
            pass  # No consent dialog.

    def search(self, query: str) -> None:
        self.driver.get(f"https://www.google.com/?hl={self.lang}")
        self._dismiss_consent()
        try:
            search_box = self.wait.until(EC.element_to_be_clickable((By.NAME, "q")))
        except TimeoutException:
            self._check_for_bot_page()
            raise AutomationError("Could not find the Google search box.") from None
        search_box.clear()
        search_box.send_keys(query, Keys.ENTER)

        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "search")))
        except TimeoutException:
            self._check_for_bot_page()
            raise AutomationError("Search results did not load.") from None

    def results(self, limit: int) -> list[SearchResult]:
        found: list[SearchResult] = []
        seen: set[str] = set()
        for heading in self.driver.find_elements(By.CSS_SELECTOR, "#search a h3"):
            title = heading.text.strip()
            link = heading.find_element(By.XPATH, "./ancestor::a[1]")
            url = link.get_attribute("href") or ""
            if not title or not url or url in seen:
                continue
            seen.add(url)
            found.append(SearchResult(title=title, url=url))
            if len(found) >= limit:
                break
        return found

    def result_stats(self) -> str | None:
        """Return text such as 'About 1,230,000 results' if Google renders it."""
        elements = self.driver.find_elements(By.ID, "result-stats")
        text = (elements[0].get_attribute("textContent") or "").strip() if elements else ""
        return text or None

    def close(self) -> None:
        self.driver.quit()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a Google search and print the top results.")
    parser.add_argument("-q", "--query", default="Nature Images", help="search term (default: 'Nature Images')")
    parser.add_argument("-n", "--results", type=int, default=5, help="number of results to print (default: 5)")
    parser.add_argument("--headless", action="store_true", help="run Chrome without a window")
    parser.add_argument("--timeout", type=int, default=15, help="seconds to wait for page elements (default: 15)")
    parser.add_argument("--lang", default="en", help="interface language code (default: en)")
    parser.add_argument("--json", action="store_true", help="print results as JSON")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        bot = GoogleSearchAutomation(headless=args.headless, timeout=args.timeout, lang=args.lang)
    except WebDriverException as exc:
        print(f"Could not start Chrome: {exc.msg}", file=sys.stderr)
        print("Make sure Google Chrome is installed and selenium>=4.15 is in use.", file=sys.stderr)
        return 1

    try:
        bot.search(args.query)
        results = bot.results(args.results)
        stats = bot.result_stats()

        if args.json:
            payload = {"query": args.query, "stats": stats, "results": [asdict(r) for r in results]}
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(f"Query: {args.query}")
            if stats:
                print(f"Search Results: {stats}")
            if not results:
                print("No organic results found (Google's layout may have changed).")
            for i, result in enumerate(results, start=1):
                print(f"{i:>2}. {result.title}\n    {result.url}")
        return 0
    except AutomationError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except WebDriverException as exc:
        print(f"Browser error: {exc.msg}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
    finally:
        bot.close()


if __name__ == "__main__":
    sys.exit(main())
