import requests
import base64
import json

ZOULT_REPO_API = "https://api.github.com/repos/Zoult/.ovpn/contents"

def fetch_zoult_servers():
    print("Fetching server list from Zoult GitHub...")
    servers = []
    try:
        # 1. Get Root Content (List of Countries)
        r = requests.get(ZOULT_REPO_API)
        if r.status_code != 200:
            print(f"Failed to fetch repo: {r.status_code}")
            return []
            
        items = r.json()
        countries = [i for i in items if i['type'] == 'dir' and not i['name'].startswith('.')]
        
        print(f"Found {len(countries)} countries.")
        
        # 2. For each country, find the .ovpn file
        # To avoid rate limits, we limit to first 10 or randomize?
        # Or we just assume the file name matches folder name or is 'vpn.ovpn'
        # Scanning all folders is API expensive (60 calls limit!).
        
        # OFFICAL TRICK: Use the recursive tree API to get ALL files in one call.
        # GET https://api.github.com/repos/Zoult/.ovpn/git/trees/main?recursive=1 
        # (Assuming main branch)
        
        branch = "main"
        tree_url = "https://api.github.com/repos/Zoult/.ovpn/git/trees/main?recursive=1"
        r_tree = requests.get(tree_url)
        if r_tree.status_code != 200:
             # Try master
             branch = "master"
             tree_url = "https://api.github.com/repos/Zoult/.ovpn/git/trees/master?recursive=1"
             r_tree = requests.get(tree_url)
        
        if r_tree.status_code == 200:
             tree = r_tree.json().get('tree', [])
             ovpn_files = [f for f in tree if f['path'].endswith('.ovpn')]
             
             print(f"Found {len(ovpn_files)} .ovpn files via Tree API.")
             
             for f in ovpn_files:
                 path = f['path']
                 parts = path.split('/')
                 country = parts[0] if len(parts) > 1 else 'Global'
                 
                 raw_url = f"https://raw.githubusercontent.com/Zoult/.ovpn/{branch}/{path}"
                 
                 servers.append({
                     "ip": "GitHub", # Placeholder
                     "host": f"{country} Server",
                     "country": country,
                     "speed": 999,
                     "score": 100,
                     "config_url": raw_url, # NEW FIELD
                     "config_base64": None
                 })
             
             return servers
             
        return []
        
    except Exception as e:
        print(f"Error fetching from GitHub: {e}")
        return []

if __name__ == "__main__":
    s = fetch_zoult_servers()
    if s:
        print(f"Sample URL: {s[0]['config_url']}")
    for i in s[:5]:
        print(i)
