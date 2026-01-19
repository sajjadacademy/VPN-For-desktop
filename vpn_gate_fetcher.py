import requests
import csv
import base64
import io

# List of mirrors to try
MIRRORS = [
    "https://api.allorigins.win/raw?url=http://www.vpngate.net/api/iphone/",
    "http://www.vpngate.net/api/iphone/",
    "https://www.vpngate.net/api/iphone/",
    "http://219.100.37.201/api/iphone/",
    "http://public-vpn-218.opengw.net/api/iphone/"
]

def fetch_vpn_gate_servers():
    print("Fetching server list from VPN Gate...")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    csv_text = None
    
    for url in MIRRORS:
        try:
            print(f"Trying {url}...")
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200 and "HostName" in response.text:
                csv_text = response.text
                print("Success!")
                break
        except Exception as e:
            print(f"Failed {url}: {e}")
            
    if not csv_text:
        print("All mirrors failed. Return dummy.")
        return [{
            "ip": "Manual Import Required", 
            "host": "Please use Import Button", 
            "country": "⚠ Connectivity Issue", 
            "speed": 0, 
            "score": 0, 
            "config_base64": ""
        }]

    try:
        servers = []
        lines = [line for line in csv_text.splitlines() if not line.startswith('*') and not line.startswith('#')]
        
        reader = csv.DictReader(lines)
        
        for row in reader:
            try:
                # We need OpenVPN Config Data
                if not row.get("OpenVPN_ConfigData_Base64"):
                    continue
                    
                server = {
                    "ip": row["IP"],
                    "host": row["HostName"],
                    "country": row["CountryLong"],
                    "speed": int(row["Speed"]) / 1000000, # Convert to Mbps
                    "score": int(row["Score"]),
                    "config_base64": row["OpenVPN_ConfigData_Base64"]
                }
                servers.append(server)
            except KeyError:
                continue
                
        # Sort by Score (Quality)
        servers.sort(key=lambda x: x['score'], reverse=True)
        
        # Filter for unique countries/high speed to give variety
        # Simple top 15 for now
        print(f"Found {len(servers)} servers. Returning top 15.")
        return servers[:15] 
        
    except Exception as e:
        print(f"Error parsing servers: {e}")
        return []

if __name__ == "__main__":
    s = fetch_vpn_gate_servers()
    for i, srv in enumerate(s):
        print(f"{i+1}. {srv['country']} - {srv['ip']} ({srv['speed']:.2f} Mbps)")
