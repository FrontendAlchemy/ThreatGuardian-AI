# tech_scanner.py
import builtwith

def clean_url(url):
    if not url.startswith("http"):
        url = "https://" + url
    return url

def scan_technologies(url):
    try:
        url = clean_url(url)
        tech = builtwith.parse(url)
        return tech
    except Exception as e:
        return {"Error": [str(e)]}
