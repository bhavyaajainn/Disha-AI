from langchain.tools import tool
import requests
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

MAX_RESULTS_PER_API = 5
TIMEOUT = 15

@tool("remote_job_tool", return_direct=True)
def remote_job_tool(query: str = "") -> str:
    """
    This function handles remote job-related tasks.
    Add more details about what the function does here.
    """
    query = sanitize_query(query)
    encoded_query = urllib.parse.quote(query)

    results, all_jobs = fetch_jobs_in_parallel(encoded_query)

    global last_fetched_jobs
    last_fetched_jobs = all_jobs

    if not any(not r.startswith("❌") for r in results):
        results.append(f"⚠️ No valid job results found for '{query}'")
    elif not results:
        results.append(f"⚠️ No jobs found for '{query}'")

    header = f"🔍 **Job Search Results for: '{query}'**\n\n"
    footer = "\n\n📱 Click on the application links above to apply directly on the company websites."
    
    return header + "\n\n".join(results) + footer


def sanitize_query(query):
    if isinstance(query, list):
        query = query[0] if query else ""
    return str(query).strip().strip("'").strip('"')


def fetch_jobs_in_parallel(encoded_query):
    results = []
    all_jobs = []

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(fetch_from_remotive, encoded_query, all_jobs),
            executor.submit(fetch_from_remoteok, encoded_query, all_jobs),
            executor.submit(fetch_from_indianapi, encoded_query, all_jobs)
        ]
        for future in futures:
            try:
                future_results = future.result()
                if future_results:
                    results.extend(future_results)
            except Exception as e:
                results.append(f"❌ Unexpected error: {str(e)}")

    return results, all_jobs


def fetch_from_remotive(encoded_query, all_jobs):
    try:
        res = requests.get(f"https://remotive.com/api/remote-jobs?search={encoded_query}", timeout=TIMEOUT)
        if res.status_code != 200:
            return [f"❌ Remotive error: Status code {res.status_code}"]

        jobs_data = res.json().get("jobs", [])[:MAX_RESULTS_PER_API]
        all_jobs.extend(jobs_data)

        return [
            f"🟢 **[Remotive] {j['title']}**\n"
            f"- 🏢 {j.get('company_name', 'N/A')}\n"
            f"- 📍 {j.get('candidate_required_location', 'Remote')}\n"
            f"- 📌 {j.get('job_type', 'N/A')}\n"
            f"- 🔗 **[APPLY HERE]({j.get('url', '#')})** ← Click to apply directly"
            for j in jobs_data
        ]
    except Exception as e:
        return [f"❌ Remotive error: {str(e)}"]


def fetch_from_remoteok(encoded_query, all_jobs):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        res = requests.get("https://remoteok.io/api", timeout=TIMEOUT, headers=headers)
        if res.status_code != 200:
            return [f"❌ RemoteOK error: Status code {res.status_code}"]

        raw_data = res.json()
        if not raw_data or len(raw_data) == 0:
            return ["❌ RemoteOK error: Empty response"]

        jobs_data = [
            j for j in raw_data[1:]
            if isinstance(j, dict) and "position" in j and "company" in j
        ]

        if encoded_query:
            jobs_data = [
                j for j in jobs_data
                if encoded_query.lower() in j.get("position", "").lower()
            ]

        jobs_data = jobs_data[:MAX_RESULTS_PER_API]
        all_jobs.extend(jobs_data)

        return [
            f"🔵 **[RemoteOK] {j['position']}**\n"
            f"- 🏢 {j.get('company', 'Unknown')}\n"
            f"- 📍 Remote\n"
            f"- 📌 {j.get('tags', ['N/A'])[0] if j.get('tags') else 'N/A'}\n"
            f"- 🔗 **[APPLY HERE](https://remoteok.io{j.get('url', '#')})** ← Click to apply directly"
            for j in jobs_data
        ]
    except Exception as e:
        return [f"❌ RemoteOK error: {str(e)}"]


def fetch_from_indianapi(encoded_query, all_jobs):
    try:
        res = requests.get(f"https://www.arbeitnow.com/api/job-board-api?search={encoded_query}", timeout=TIMEOUT)
        if res.status_code != 200:
            return [f"❌ ArbeitNow API error: Status code {res.status_code}"]

        jobs_data = res.json().get("data", [])[:MAX_RESULTS_PER_API]
        all_jobs.extend(jobs_data)

        return [
            f"🌍 **[ArbeitNow] {j['title']}**\n"
            f"- 🏢 {j.get('company_name', 'N/A')}\n"
            f"- 📍 {j.get('location', 'Remote')}\n"
            f"- 📌 {', '.join(j.get('tags', ['N/A']))}\n"
            f"- 🔗 **[APPLY HERE]({j.get('url', '#')})** ← Click to apply directly"
            for j in jobs_data
        ]
    except Exception as e:
        return [f"❌ ArbeitNow API error: {str(e)}"]


def get_apply_link_by_company(company_name: str) -> str:
    try:
        for job in last_fetched_jobs:
            # Check different fields that might contain company name
            company_field = job.get("company_name", job.get("company", ""))
            if isinstance(company_field, dict):
                company_field = company_field.get("display_name", "")
                
            if company_name.lower() in str(company_field).lower():
                # Get URL from different possible fields
                url = job.get("url", job.get("redirect_url", "No link found"))
                return url
        return "No job found for the given company name."
    except NameError:
        return "No jobs have been fetched yet. Please run the remote_job_tool first."

last_fetched_jobs = []