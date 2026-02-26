import os
import json
import time
from typing import Any, Dict, List, Optional, Tuple

from apify_client import ApifyClient

from dotenv import load_dotenv

load_dotenv()

class ActorRunError(RuntimeError):
    pass


def run_sales_nav_scraper(
    search_url: str,
    *,
    total_records: int = 25,
    start_page: int = 1,
    deep_scrape: bool = False,
    min_wait_s: int = 5,
    max_wait_s: int = 30,
    proxy_group: str = "RESIDENTIAL",
    proxy_country: Optional[str] = None,
    timeout_s: int = 900,
    poll_interval_s: float = 2.0,
    max_items: Optional[int] = None,
    actor_id: str = "quantifiable_extension/linkedin-sales-navigator-scraper",
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    apify_token = os.getenv("APIFY_TOKEN")
    cookieString = os.getenv("COOKIE_STRING")

    if not apify_token:
        raise ValueError("Set APIFY_TOKEN env var.")

    # Read README on how to get this COOKIE_STRING
    if not cookieString:
        raise ValueError("Set COOKIE_STRING env var.")

    client = ApifyClient(apify_token)

    # ---- IMPORTANT: Actor requires input.searchUrl (per your error) ----
    run_input: Dict[str, Any] = {
        "searchUrl": search_url,  # ✅ required by your actor
        "cookieString": cookieString,
        # Try both common field name variants (your actor will accept whichever matches schema)
        "totalRecords": total_records,
        "totalRecordsToScrape": total_records,

        "startPage": start_page,

        "deepScrape": deep_scrape,

        "minWaitBetweenPages": min_wait_s,
        "maxWaitBetweenPages": max_wait_s,

        "proxyConfiguration": {
            "useApifyProxy": True,
            "apifyProxyGroups": [proxy_group],
            **({"apifyProxyCountry": proxy_country} if proxy_country else {}),
        },
    }

    # Start run
    run = client.actor(actor_id).start(run_input=run_input)
    run_id = run["id"]

    # Poll status
    start = time.time()
    while True:
        info = client.run(run_id).get()
        status = info.get("status")
        if status in {"SUCCEEDED", "FAILED", "TIMED-OUT", "ABORTED"}:
            break
        if time.time() - start > timeout_s:
            raise ActorRunError(f"Timed out waiting for run {run_id}")
        time.sleep(poll_interval_s)

    if status != "SUCCEEDED":
        raise ActorRunError(f"Run ended with status={status}. Run: https://console.apify.com/actors/runs/{run_id}")

    dataset_id = info.get("defaultDatasetId")
    items: List[Dict[str, Any]] = []
    n = 0
    for item in client.dataset(dataset_id).iterate_items():
        items.append(item)
        n += 1
        if max_items is not None and n >= max_items:
            break

    meta = {
        "run_id": run_id,
        "dataset_id": dataset_id,
        "console_run_url": f"https://console.apify.com/actors/runs/{run_id}",
        "console_dataset_url": f"https://console.apify.com/storage/datasets/{dataset_id}",
        "status": status,
    }
    return items, meta


if __name__ == "__main__":
    industry_link = "https://www.linkedin.com/sales/search/company?query=(filters%3AList((type%3AINDUSTRY%2Cvalues%3AList((id%3A19%2Ctext%3ARetail%2520Apparel%2520and%2520Fashion%2CselectionType%3AINCLUDED)))%2C(type%3ACOMPANY_HEADCOUNT%2Cvalues%3AList((id%3AE%2Ctext%3A201-500%2CselectionType%3AINCLUDED)))))&sessionId=dgbhZuu3QVqdHItpMZuBFA%3D%3D&viewAllFilters=true"
    personal_link = "https://www.linkedin.com/sales/search/people?query=(filters%3AList((type%3ACURRENT_COMPANY%2Cvalues%3AList((id%3A35921%2CselectionType%3AINCLUDED)))%2C(type%3APERSONA%2Cvalues%3AList((id%3A1962673041%2CselectionType%3AINCLUDED)))))&sessionId=jEQhyR76Ri%2BNSaBgRe%2FbAg%3D%3D"

    url = industry_link

    results, meta = run_sales_nav_scraper(url, total_records=25, deep_scrape=False)

    print("Run metadata:", meta)
    print("Number of items returned:", len(results))
    print("All items:", results if results else "No data returned.")