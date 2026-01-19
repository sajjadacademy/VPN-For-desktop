import requests

# Try both branches
urls = [
    "https://raw.githubusercontent.com/Zoult/.ovpn/main/Germany/Germany.ovpn",
    "https://raw.githubusercontent.com/Zoult/.ovpn/master/Germany/Germany.ovpn",
    "https://raw.githubusercontent.com/Zoult/.ovpn/main/Germany/vpn.ovpn",
    "https://raw.githubusercontent.com/Zoult/.ovpn/master/Germany/vpn.ovpn"
]

print("Testing URLs...")
for url in urls:
    try:
        print(f"Checking {url}...")
        r = requests.get(url, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print("SUCCESS! Content preview:")
            print(r.text[:200])
            if "html" in r.text.lower():
                 print("WARNING: Content looks like HTML (Soft 404?)")
            break
    except Exception as e:
        print(f"Error: {e}")
