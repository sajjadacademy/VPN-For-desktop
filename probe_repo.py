import requests

base_url = "https://raw.githubusercontent.com/Zoult/.ovpn/master"
countries = ["Japan", "USA", "Canada"]
filenames = ["vpn.ovpn", "config.ovpn", "Japan.ovpn", "USA.ovpn", "Canada.ovpn", "setup.ovpn", "README.md"]

for country in countries:
    for fname in filenames:
        url = f"{base_url}/{country}/{fname}"
        # try root readme as well
        if fname == "README.md":
             url = f"{base_url}/{fname}"
             
        try:
            r = requests.head(url)
            print(f"Checked {url}: {r.status_code}")
        except Exception as e:
            print(f"Error {url}: {e}")
