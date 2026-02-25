
from urllib.parse import urlparse

def linkedin_to_sales_company_url(company_url: str) -> str:
    """
    Converts a LinkedIn company URL into its Sales Navigator company URL.

    Example:
    https://www.linkedin.com/company/35921/
    → https://www.linkedin.com/sales/company/35921/
    """

    if not isinstance(company_url, str) or not company_url.strip():
        raise ValueError("Invalid company URL")

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
        get_value("company_location"),
        "", # Total Jobs not available in this JSON
        "", # get_value("employee_experience_title", "title"),
        ""  # Frequent Jobs not available
    ]

    return [header, row]