"""
Parse LinkedIn Sales Navigator search result HTML.

This script is designed to operate entirely offline.  It accepts an HTML
document (for example, one saved from Sales Navigator's account search
results) and extracts useful pieces of information from it.  It uses
BeautifulSoup to traverse the DOM and collects metadata for each
company listed on the page, as well as summary details for the search
result set itself.

Example usage:

    python parse_linkedin_html.py sample-html.txt > parsed.json

The output will be printed as a JSON object containing the total result
count, current page, total number of pages, and a list of companies.

The script does not make any network requests, click on links, or
otherwise interact with the document beyond parsing the provided HTML.
"""

import argparse
import json
import re
from typing import Dict, List, Optional, Any

from bs4 import BeautifulSoup


def extract_total_results(soup: BeautifulSoup) -> Optional[str]:
    """Extract the total number of results string (e.g. "330K+ results").

    Sales Navigator displays the total number of search results near the
    top of the results list.  This helper searches for a span whose text
    matches the pattern "<number> results" and returns the first match.

    Args:
        soup: Parsed BeautifulSoup document.

    Returns:
        The results string if found, otherwise None.
    """
    # Look for any span that ends with 'results'
    candidate_spans = soup.find_all("span")
    for span in candidate_spans:
        text = span.get_text(strip=True)
        # Match numbers like "330K+ results", "1,234 results", etc.
        if re.match(r"^[\d,.K+]+\s+results$", text):
            return text
    return None


def extract_pagination(soup: BeautifulSoup) -> Dict[str, Optional[int]]:
    """Extract pagination information from the HTML.

    Sales Navigator includes an element with class
    `artdeco-pagination__state--a11y` that contains text like
    "Page 1 of 40".  This helper parses that and returns the current
    page number and the total number of pages.

    Args:
        soup: Parsed BeautifulSoup document.

    Returns:
        A dictionary with keys `current_page` and `total_pages`, each
        either an integer or None if not found.
    """
    pagination_info = {"current_page": None, "total_pages": None}
    state_span = soup.find("span", class_="artdeco-pagination__state--a11y")
    if state_span:
        m = re.search(r"Page\s+(\d+)\s+of\s+(\d+)", state_span.get_text())
        if m:
            try:
                pagination_info["current_page"] = int(m.group(1))
                pagination_info["total_pages"] = int(m.group(2))
            except ValueError:
                # Fall back to None if conversion fails
                pass
    return pagination_info


def extract_company_info(item: BeautifulSoup) -> Optional[Dict[str, Any]]:
    """Extract structured information about a single company result.

    Each result in Sales Navigator is rendered within an `<li>` element
    containing information about a company.  This function extracts
    various fields such as the company name, Sales Navigator company ID,
    industry, headcount, about snippet, saved status, spotlight signals,
    and the company's URL.

    Args:
        item: A BeautifulSoup object representing the `<li>` element
            containing the company result.

    Returns:
        A dictionary with extracted data or None if a company name cannot
        be determined.
    """
    # Company name and URL
    name = None
    company_url = None
    company_id = None
    anchor = item.find("a", attrs={"data-anonymize": "company-name"})
    if anchor:
        name = anchor.get_text(strip=True)
        company_url = anchor.get("href")
        if company_url:
            m = re.search(r"/sales/company/(\d+)", company_url)
            if m:
                company_id = m.group(1)
    # If no name was found, this item is likely a loading placeholder
    if not name:
        return None
    # Industry
    industry = None
    industry_span = item.find("span", attrs={"data-anonymize": "industry"})
    if industry_span:
        industry = industry_span.get_text(strip=True)
    # Headcount (employee count)
    headcount = None
    # Look for an <a> whose text contains "employees"
    for a in item.find_all("a"):
        text = a.get_text(strip=True)
        if "employees" in text:
            headcount = text
            break
    # About blurb (truncated)
    about = None
    about_div = item.find("div", attrs={"data-anonymize": "person-blurb"})
    if about_div:
        # Flatten the nested tags into a single string.  Some content
        # includes a "… Show more" button; remove that trailing part.
        about_text = about_div.get_text(separator=" ", strip=True)
        about = re.sub(r"\s*…\s*Show more$", "", about_text)
    # Saved status
    saved = False
    saved_indicator = item.find(lambda tag: tag.name == "span" and tag.get_text(strip=True).lower() == "saved")
    if saved_indicator:
        saved = True
    # Spotlight signals
    signals: List[str] = []
    # The signals are contained within an ordered list (`ol`) with
    # list-style-none.  Each signal is represented by a <button> with
    # nested <span> containing the text.
    signals_container = item.find("ol", class_=re.compile(r"list-style-none"))
    if signals_container:
        for btn in signals_container.find_all("button"):
            # Prefer a span with the nowrap-ellipsis class
            span = btn.find("span", class_=re.compile(r"nowrap-ellipsis"))
            if span:
                signal_text = span.get_text(strip=True)
                if signal_text:
                    signals.append(signal_text)
    return {
        "company_id": company_id,
        "name": name,
        "industry": industry,
        "headcount": headcount,
        "about": about,
        "saved": saved,
        "signals": signals,
        "url": company_url,
    }


def parse_sales_nav_html(html: str) -> Dict[str, Any]:
    """Parse Sales Navigator search results HTML into structured data.

    The returned dictionary contains top-level metadata (total results,
    pagination) and a list of companies with extracted fields.

    Args:
        html: The raw HTML string to parse.

    Returns:
        A dictionary with keys:
            - total_results (optional str)
            - current_page (optional int)
            - total_pages (optional int)
            - companies (list of dict)
    """
    soup = BeautifulSoup(html, "html.parser")
    total_results = extract_total_results(soup)
    pagination = extract_pagination(soup)
    companies: List[Dict[str, Any]] = []
    # Each result item appears as a `<li>` with class `artdeco-list__item`
    for li in soup.find_all("li", class_=re.compile(r"artdeco-list__item")):
        info = extract_company_info(li)
        if info:
            companies.append(info)
    return {
        "total_results": total_results,
        "current_page": pagination.get("current_page"),
        "total_pages": pagination.get("total_pages"),
        "companies": companies,
    }


def main() -> None:
    """Main entry point for command-line use."""
    parser = argparse.ArgumentParser(description=(
        "Parse LinkedIn Sales Navigator search results HTML and extract "
        "informative fields."
    ))
    parser.add_argument(
        "html_file",
        help="Path to the Sales Navigator HTML file to parse."
    )
    parser.add_argument(
        "-o",
        "--output",
        help=(
            "Optional output file.  If provided, the extracted data is "
            "written to this file as JSON.  Otherwise, it is printed to stdout."
        ),
        default=None,
    )
    args = parser.parse_args()
    # Read the input HTML file
    with open(args.html_file, "r", encoding="utf-8") as f:
        html = f.read()
    result = parse_sales_nav_html(html)
    # Serialize to JSON with pretty-printing and ensure non-ASCII is preserved
    json_output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_output)
    else:
        print(json_output)


if __name__ == "__main__":
    main()