"""Scrape book listings from books.toscrape.com and save to CSV."""

import argparse
import csv
import sys
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
DEFAULT_PAGES = 5
OUTPUT_FILE = "books.csv"
REQUEST_TIMEOUT = 15
MAX_RETRIES_PER_PAGE = 3

RATING_MAP = {
    "One": "1",
    "Two": "2",
    "Three": "3",
    "Four": "4",
    "Five": "5",
}


def page_url(page_number: int) -> str:
    if page_number == 1:
        return BASE_URL
    return urljoin(BASE_URL, f"catalogue/page-{page_number}.html")


def fetch_page_with_retry(
    session: requests.Session, url: str, retries: int = MAX_RETRIES_PER_PAGE
) -> BeautifulSoup:
    last_error: requests.RequestException | None = None
    for attempt in range(1, retries + 1):
        try:
            response = session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except requests.RequestException as exc:
            last_error = exc
            if attempt < retries:
                backoff_seconds = 0.5 * attempt
                print(
                    f"  Attempt {attempt}/{retries} failed ({exc}). Retrying in {backoff_seconds:.1f}s...",
                    flush=True,
                )
                time.sleep(backoff_seconds)
    raise RuntimeError(f"Failed to fetch page after {retries} attempts: {last_error}")


def parse_books(soup: BeautifulSoup) -> list[dict[str, str]]:
    books = []
    for article in soup.select("article.product_pod"):
        title_tag = article.select_one("h3 a")
        price_tag = article.select_one("p.price_color")
        rating_tag = article.select_one("p.star-rating")
        availability_tag = article.select_one("p.instock.availability")

        rating_class = ""
        if rating_tag:
            rating_class = next(
                (cls for cls in rating_tag.get("class", []) if cls in RATING_MAP),
                "",
            )

        books.append(
            {
                "Title": title_tag.get("title", title_tag.get_text(strip=True))
                if title_tag
                else "",
                "Price": price_tag.get_text(strip=True) if price_tag else "",
                "Rating": RATING_MAP.get(rating_class, rating_class),
                "Availability": availability_tag.get_text(strip=True)
                if availability_tag
                else "",
            }
        )
    return books


def scrape_books(num_pages: int) -> tuple[list[dict[str, str]], list[int]]:
    all_books: list[dict[str, str]] = []
    failed_pages: list[int] = []
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (compatible; PriceScraper/1.0; +https://books.toscrape.com)"
            )
        }
    )

    for page in range(1, num_pages + 1):
        url = page_url(page)
        print(f"[{page}/{num_pages}] Fetching {url} ...", flush=True)

        try:
            soup = fetch_page_with_retry(session, url)
        except RuntimeError as exc:
            print(f"  Error: {exc}", file=sys.stderr)
            failed_pages.append(page)
            continue

        books = parse_books(soup)
        all_books.extend(books)
        print(f"  Found {len(books)} books (total so far: {len(all_books)})", flush=True)

        if page < num_pages:
            time.sleep(0.5)

    return all_books, failed_pages


def save_to_csv(books: list[dict[str, str]], output_path: str) -> None:
    fieldnames = ["Title", "Price", "Rating", "Availability"]
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(books)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape book titles, prices, ratings, and availability from books.toscrape.com"
    )
    parser.add_argument(
        "-p",
        "--pages",
        type=int,
        default=DEFAULT_PAGES,
        help=f"Number of catalogue pages to scrape (default: {DEFAULT_PAGES})",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=OUTPUT_FILE,
        help=f"Output CSV file path (default: {OUTPUT_FILE})",
    )
    args = parser.parse_args()

    if args.pages < 1:
        print("Pages must be at least 1.", file=sys.stderr)
        sys.exit(1)

    print(f"Starting scrape of {args.pages} page(s) from books.toscrape.com\n")
    books, failed_pages = scrape_books(args.pages)

    if not books:
        print("\nNo books scraped. CSV file was not created.", file=sys.stderr)
        sys.exit(1)

    save_to_csv(books, args.output)
    print(f"\nDone. Saved {len(books)} books to {args.output}")
    if failed_pages:
        failed = ", ".join(str(page) for page in failed_pages)
        print(f"Warning: failed to scrape page(s): {failed}", file=sys.stderr)


if __name__ == "__main__":
    main()
