import time
from urllib.parse import urlparse

from apify_api import run_sales_nav_scraper
from google_spread_sheet_queue import google_sheets_queue


def linkedin_to_sales_company_url(company_url: str) -> str:
    """
    Converts a LinkedIn company URL into its Sales Navigator company URL.

    Example:
    https://www.linkedin.com/company/35921/
    → https://www.linkedin.com/sales/company/35921/
    """
    try:
        if not isinstance(company_url, str) or not company_url.strip():
            print("company url: ", company_url)
            raise ValueError(f"Invalid company URL {company_url}")

        company_url = company_url.strip()

        parsed = urlparse(company_url)

        if "linkedin.com" not in parsed.netloc:
            raise ValueError("URL is not a LinkedIn URL")

        # Extract path and remove query/fragment
        path = parsed.path.strip("/")

        # Expected format: company/<id or slug>
        parts = path.split("/")

        if len(parts) < 2 or parts[0] != "company":
            raise ValueError("URL is not a valid LinkedIn company URL")

        company_identifier = parts[1]

        sales_url = f"https://www.linkedin.com/sales/company/{company_identifier}/"

        return sales_url
    except Exception as e:
        print(f"[EXCEPTION] linkedin_to_sales_company_url: {e}")
        return ""

def convert_json_to_csv_row(result: dict):
    """
    Converts a Sales Navigator JSON result into a CSV row
    matching the required Google Sheets schema.
    Missing fields are left blank.

    # Example format
    # csv_data = [
    #     ["Company Name", "Linkedin URL", "Sales Navigator URL", "Website", "Employee Count", "Overview", "Headquarters", "Total Jobs", "Job Titles", "Frequent Jobs"]
    # ]

    """

    header = [
        "Company Name", "Linkedin URL", "Sales Navigator URL", "Website",
        "Employee Count", "Overview", "Headquarters", "Total Jobs",
        "Job Titles", "Frequent Jobs"
    ]

    # Helper to safely get value or blank
    def get_value(*keys):
        for key in keys:
            if result.get(key):
                return str(result.get(key))
        return ""

    row = [
        get_value("company_name", "companyName"),
        get_value("company_linkedin", "companyLinkedinUrl"),
        linkedin_to_sales_company_url(get_value("company_linkedin", "companyLinkedinUrl")), # get_value("employee_linkedin"),
        "", #get_value("company_domain"),
        "", #get_value("company_size"),
        "", #get_value("company_description"),
        "", # get_value("company_location"),
        "", # Total Jobs not available in this JSON
        "", # get_value("employee_experience_title", "title"),
        ""  # Frequent Jobs not available
    ]

    return [header, row]

def convert_multiple_json(results: list):

    """

    This is for multiple results processing

    Converts a Sales Navigator JSON result into a CSV row
    matching the required Google Sheets schema.
    Missing fields are left blank.

    # Example format
    # csv_data = [
    #     ["Company Name", "Linkedin URL", "Sales Navigator URL", "Website", "Employee Count", "Overview", "Headquarters", "Total Jobs", "Job Titles", "Frequent Jobs"]
    # ]

    :param results: list of json
    :return:
    """

    rows = []

    for result in results:
        row = convert_json_to_csv_row(result)
        print(row)
        rows.append(row)

    return rows

from typing import List, Dict, Any

def convert_person_json_to_csv_row(result: dict):
    """
    Converts a Sales Navigator *person* JSON result into a CSV row
    matching a Google Sheets schema for leads.
    Missing fields are left blank.

    Example format:
    csv_data = [
        ["First Name", "Last Name", "Full Name", "Designation", "Headline", "Location",
         "Industry", "Company Name", "Company Linkedin URL", "Company Sales Navigator URL",
         "Lead (Sales) URL", "Picture URL", "Email", "Scraped At"],
        [...]
    ]
    """

    header = [
        "First Name", "Last Name", "Full Name",
        "Designation", "Headline", "Location",
        "Industry",
        "Company Name", "Company Linkedin URL", "Company Sales Navigator URL",
        "Lead (Sales) URL",
        "Picture URL", "Email",
        "Scraped At"
    ]

    # Helper to safely get value or blank
    def get_value(*keys):
        for key in keys:
            val = result.get(key)
            if val is not None and str(val).strip() != "":
                return str(val).strip()
        return ""

    # If you already have this function in your codebase, it will be used as-is.
    # It converts: https://www.linkedin.com/company/<id>/  -> https://www.linkedin.com/sales/company/<id>/
    def linkedin_to_sales_company_url(company_linkedin_url: str) -> str:
        if not company_linkedin_url:
            return ""
        u = company_linkedin_url.strip()
        # already sales company url
        if "/sales/company/" in u:
            return u
        # normalize trailing slash
        if not u.endswith("/"):
            u += "/"
        # replace company path -> sales/company path
        if "linkedin.com/company/" in u:
            return u.replace("linkedin.com/company/", "linkedin.com/sales/company/")
        return ""

    company_linkedin = get_value("company_linkedin", "companyLinkedinUrl")
    company_sales_url = linkedin_to_sales_company_url(company_linkedin)

    row = [
        get_value("employee_first_name", "firstName"),
        get_value("employee_last_name", "lastName"),
        get_value("employee_full_name", "fullName", "name"),

        # Designation / title
        get_value("employee_experience_title", "title"),

        # Headline
        get_value("employee_linkedin_headline", "headline"),

        # Location
        get_value("employee_location", "location"),

        # Industry
        get_value("company_industry"),

        # Company
        get_value("company_name", "companyName", "company"),
        company_linkedin,
        company_sales_url,

        # Lead/Person URL (Sales Navigator)
        get_value("employee_linkedin", "linkedinUrl", "profileUrl"),

        # Picture / email / scraped time
        get_value("pictureUrl"),
        get_value("employee_email"),
        get_value("scrapedAt"),
    ]

    return [header, row]


def convert_multiple_person_json(results: List[Dict[str, Any]]):
    """
    For multiple results processing (people/leads).
    Returns a list of [header,row] pairs (same pattern as your existing function).
    """

    rows = []
    for result in results:
        row = convert_person_json_to_csv_row(result)
        print(row)
        rows.append(row)
    return rows


def scrape_industry(industry_link, sheet_id, page_name):
    """

    :param industry_link:
    :return:
    """
    # Initialize sheet queue handler
    sheets_queue = google_sheets_queue(sheet_id, page_name)
    sheets_queue.start_worker()

    # Scrape the result
    results, meta = run_sales_nav_scraper(industry_link, total_records=25, deep_scrape=False)
    # Get them in a csv format

    csv_data = convert_multiple_json(results)
    print(csv_data)
    # Save to redis for record keeping

    # redis code here

    # Upload the data to google spreadsheet
    for data in csv_data:
        sheets_queue.enqueue(data)

    # Wait until all the items have not been uploaded to the sheet
    if sheets_queue.size() > 0:
        time.sleep(1)


def scrape_personal(personal_link, sheet_id, page_name):
    """

    :param personal_link:
    :return:
    """
    # Initialize sheet queue handler
    sheets_queue = google_sheets_queue(sheet_id, page_name)
    sheets_queue.start_worker()

    # Scrape the result
    results, meta = run_sales_nav_scraper(personal_link, total_records=25, deep_scrape=False)
    # Get them in a csv format

    csv_data = convert_multiple_person_json(results)
    print(csv_data)
    # Save to redis for record keeping

    # redis code here

    # Upload the data to google spreadsheet
    for data in csv_data:
        sheets_queue.enqueue(data)

    # Wait until all the items have not been uploaded to the sheet
    if sheets_queue.size() > 0:
        time.sleep(1)
