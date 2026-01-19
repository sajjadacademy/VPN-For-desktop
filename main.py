import sys
import ctypes
import os
import threading
from vpn_core import VPNClient
from gui import VPNApp
from vpn_gate_fetcher import fetch_vpn_gate_servers
from zoult_fetcher import fetch_zoult_servers
from local_config_fetcher import fetch_local_configs
from config import APP_NAME, VERSION

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    if not is_admin():
        print("Requesting Administrator privileges...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    print("Initializing Anti-Gravity VPN...")
    
    # 1. Fetch Real Servers
    servers = []
    
    # Priority 1: Local Config Files
    local_servers = fetch_local_configs()
    if local_servers:
        print(f"Loaded {len(local_servers)} local configuration files.")
        servers.extend(local_servers)
    
    # Priority 2: Zoult Repo (GitHub)
    zoult_servers = fetch_zoult_servers()
    if zoult_servers:
        print(f"Loaded {len(zoult_servers)} servers from GitHub.")
        servers.extend(zoult_servers)
        
    # Priority 3: VPN Gate (Backup)
    gate_servers = fetch_vpn_gate_servers()
    # Filter out dummy if both exist? 
    # If fetch_vpn_gate_servers returns a dummy error item, we might not want it if we have real Zoult servers.
    if gate_servers:
        if "Manual Import" in gate_servers[0]['ip'] and (zoult_servers or local_servers):
             pass # Skip dummy if we have other servers
        else:
            servers.extend(gate_servers)

    if not servers:
        print("All fetchers failed.")
        servers = []
    
    # Initialize Client logic
    vpn_client = VPNClient(servers)
    
    # Initialize UI
    app = VPNApp(vpn_client)
    
    # Normalize server data for GUI consistency
    formatted_servers = []
    for s in servers:
        # If it's a local file, we might want special display
        formatted_servers.append({
            "ip": s["ip"],
            "port": 1194, 
            "location": s["country"],
            "config_base64": s.get("config_base64"),
            "config_url": s.get("config_url"),
            "config_path": s.get("config_path")
        })
    
    # Inject into config-like structure or just pass to client/app
    vpn_client.servers = formatted_servers
    
    # Update UI with the final server list
    app.update_server_list(formatted_servers)
    
    app.mainloop()
    
    vpn_client.disconnect()

if __name__ == "__main__":
    main()
