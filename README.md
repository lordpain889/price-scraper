# Price Scraper

A Python web scraper that collects book listings from [books.toscrape.com](https://books.toscrape.com) and saves them to a CSV file.

## Features

- Scrapes **Title**, **Price**, **Rating**, and **Availability** for each book
- Supports scraping multiple catalogue pages (default: 5)
- Prints progress to the terminal while running
- Writes results to `books.csv`

## Requirements

- Python 3.10+

## Setup

1. Create and activate a virtual environment (recommended):

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Scrape the default 5 pages and save to `books.csv`:

```bash
python scraper.py
```

Scrape a custom number of pages:

```bash
python scraper.py --pages 10
```

Write output to a different file:

```bash
python scraper.py --output my_books.csv
```

### Example output

```
Starting scrape of 5 page(s) from books.toscrape.com

[1/5] Fetching https://books.toscrape.com/ ...
  Found 20 books (total so far: 20)
[2/5] Fetching https://books.toscrape.com/catalogue/page-2.html ...
  Found 20 books (total so far: 40)
...

Done. Saved 100 books to books.csv
```

## CSV format

| Column       | Description                          |
| ------------ | ------------------------------------ |
| Title        | Full book title                      |
| Price        | Price including currency symbol      |
| Rating       | Star rating (1–5)                    |
| Availability | Stock status (e.g. "In stock")       |

## Notes

[books.toscrape.com](https://books.toscrape.com) is a sandbox site intended for learning web scraping. Prices and ratings are randomly assigned and have no real meaning.
