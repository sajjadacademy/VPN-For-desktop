import os
import glob

CONFIG_DIR = "Configuration files"

def fetch_local_configs():
    """Scans the local 'Configuration files' folder for .ovpn files."""
    print(f"Scanning '{CONFIG_DIR}' for config files...")
    
    if not os.path.exists(CONFIG_DIR):
        try:
            os.makedirs(CONFIG_DIR)
            print(f"Created directory: {CONFIG_DIR}")
        except Exception as e:
            print(f"Failed to create directory: {e}")
            return []
            
    # Find all .ovpn files
    path_pattern = os.path.join(CONFIG_DIR, "*.ovpn")
    files = glob.glob(path_pattern)
    
    servers = []
    
    # Country Code Mapping
    country_map = {
        "jp": "Japan", "us": "USA", "nl": "Netherlands", "de": "Germany",
        "ca": "Canada", "fr": "France", "uk": "United Kingdom", "sg": "Singapore",
        "mx": "Mexico", "br": "Brazil", "au": "Australia", "pl": "Poland",
        "ch": "Switzerland", "no": "Norway", "ro": "Romania"
    }
    
    for filepath in files:
        filename = os.path.basename(filepath)
        # Pattern: cc-free-XX.protonvpn.tcp.ovpn
        # We want: "Japan Free XX (TCP)"
        
        name_parts = filename.lower().split('-')
        cc = name_parts[0]
        
        country = country_map.get(cc, cc.upper())
        
        # Try to extract number
        number = ""
        for part in name_parts:
             if part.isdigit():
                 number = f" #{part}"
                 break
        
        # Check Protocol
        proto = "TCP" if "tcp" in filename.lower() else "UDP"
        
        display_name = f"{country}{number} ({proto})"
        
        servers.append({
            "ip": "Local File", 
            "host": display_name,
            "country": display_name, # Use cleaned name for display
            "speed": 9999,
            "score": 1000,
            "config_path": os.path.abspath(filepath), 
            "config_base64": None
        })
        
    print(f"Found {len(servers)} local configuration files.")
    return servers

if __name__ == "__main__":
    fetch_local_configs()
