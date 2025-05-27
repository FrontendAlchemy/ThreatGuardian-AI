# subdomain_finder.py
import requests

def find_subdomains(domain, mode="deep"):
    if mode == "quick":
        try:
            url = f"https://crt.sh/?q=%25.{domain}&output=json"
            res = requests.get(url, timeout=10)
            if res.status_code != 200:
                return [f"Error: crt.sh returned {res.status_code}"]

            data = res.json()
            subdomains = set()
            for entry in data:
                name = entry.get("name_value", "")
                for sub in name.split('\n'):
                    if sub.endswith(domain):
                        subdomains.add(sub.strip())

            return sorted(subdomains)
        except Exception as e:
            return [f"Error: {str(e)}"]

    # Fall back to Sublist3r for deep scans
    try:
        from sublist3r import main as sublist3r_main

        subdomains = sublist3r_main(
            domain=domain,
            threads=40,
            savefile=None,
            ports=None,
            silent=True,
            verbose=False,
            enable_bruteforce=False,
            engines=None
        )
        return list(subdomains)
    except Exception as e:
        return [f"Error: {str(e)}"]
