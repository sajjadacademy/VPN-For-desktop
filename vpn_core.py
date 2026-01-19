import subprocess
import threading
import time
import os
import base64
import logging
import sys

# Path to OpenVPN binary
OPENVPN_PATH = r"C:\Program Files\OpenVPN\bin\openvpn.exe"

class VPNClient:
    def __init__(self, servers=None):
        self.servers = servers if servers else []
        self.current_server = None
        self.connected = False
        self.process = None
        self.running = False
        self.kill_switch_active = False
        self.log_buffer = []
        
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        self.logger = logging.getLogger("VPNClient")

    def connect_to_file(self, config_path):
        """Connects using a local .ovpn file."""
        self.logger.info(f"Connecting to manual config: {config_path}...")
        
        # 1. Start OpenVPN Process directly with the file
        # Check if file exists
        if not os.path.exists(config_path):
             self.logger.error("Config file not found.")
             return False

        cmd = [OPENVPN_PATH, "--config", config_path]
        return self._start_openvpn_process(cmd, {"ip": "Manual File", "location": "Custom Config"})

    def connect_to_server(self, server):
        """Connects using OpenVPN subprocess."""
        self.logger.info(f"Connecting to {server.get('country', 'Unknown')} ({server['ip']})...")
        
        # 1. Prepare Config File path
        config_path = "temp_vpn_config.ovpn"
        
        # Check if we have a direct local path (from Local Fetcher)
        if server.get('config_path'):
            config_path = server['config_path']
            self.logger.info(f"Using local config: {config_path}")
        else:
            # Download or write temp file
            try:
                if server.get('config_url'):
                    import requests
                    self.logger.info(f"Downloading config from {server['config_url']}...")
                    r = requests.get(server['config_url'])
                    r.raise_for_status()
                    config_data = r.text
                elif server.get('config_base64'):
                    config_data = base64.b64decode(server['config_base64']).decode('utf-8')
                else:
                    self.logger.error("No config data found for server.")
                    return False
                    
                with open(config_path, "w") as f:
                    f.write(config_data)
            except Exception as e:
                self.logger.error(f"Failed to process config: {e}")
                return False

        # 2. Prepare Credentials
        # Check for 'credentials.txt' in the config directory first
        custom_auth_path = os.path.join("Configuration files", "credentials.txt")
        auth_path = "temp_auth.txt"
        
        if os.path.exists(custom_auth_path):
            self.logger.info(f"Using credentials from {custom_auth_path}")
            # Read content to ensure it's valid or just pass the path?
            # OpenVPN needs a file with 2 lines: username\npassword
            # We can just pass this path directly!
            auth_file_to_use = os.path.abspath(custom_auth_path)
        else:
             # Fallback to default vpn/vpn
             with open(auth_path, "w") as f:
                 f.write("vpn\nvpn") 
             auth_file_to_use = os.path.abspath(auth_path)
            
        # 3. Start OpenVPN Process
        cmd = [OPENVPN_PATH, "--config", config_path, "--auth-user-pass", auth_file_to_use]
        return self._start_openvpn_process(cmd, server)

    def _start_openvpn_process(self, cmd, server_info):
        try:
            # Creation flags to hide window
            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NO_WINDOW

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                universal_newlines=True,
                creationflags=creationflags
            )
            
            # 3. Monitor Output
            self.connected = False
            start_time = time.time()
            
            while time.time() - start_time < 30: # Increased Timeout
                line = self.process.stdout.readline()
                if not line: break
                print(f"[OpenVPN] {line.strip()}")
                
                if "enter credentials" in line.lower() or "auth" in line.lower():
                     self.logger.warning("OpenVPN is asking for credentials!")
                
                if "Initialization Sequence Completed" in line:
                    self.connected = True
                    self.current_server = server_info # Update with info
                    self.logger.info("VPN Connection Established!")
                    threading.Thread(target=self._monitor_process, daemon=True).start()
                    return True
                
                if "Exiting due to fatal error" in line:
                    self.logger.error("OpenVPN Fatal Error")
                    break
                    
            if not self.connected:
                self.logger.error("Connection timed out or failed.")
                self.disconnect()
                return False

        except Exception as e:
            self.logger.error(f"Error executing OpenVPN: {e}")
            self.disconnect()
            return False
            
        return False

    def _monitor_process(self):
        """Reads output to keep buffer clear and detect disconnects."""
        while self.process and self.process.poll() is None:
            line = self.process.stdout.readline()
            if not line: break
            # We could parse stats here if we wanted
            
        if self.connected:
            self.logger.info("OpenVPN process ended unexpectedly.")
            self.disconnect()

    def disconnect(self):
        """Terminates the OpenVPN process."""
        self.running = False
        if self.process:
            self.logger.info("Terminating OpenVPN process...")
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except:
                try:
                    self.process.kill()
                except:
                    pass
            self.process = None
        
        self.connected = False
        self.current_server = None
        self.logger.info("Disconnected.")
        
        if self.kill_switch_active:
            self.disable_kill_switch()

    def auto_switch_servers(self):
        self.running = True
        while self.running:
            if not self.connected and self.servers:
                for server in self.servers:
                    if not self.running: break
                    if self.connect_to_server(server):
                        break
                    time.sleep(2)
                
                if not self.connected and self.running:
                    time.sleep(30)
            else:
                time.sleep(1)

    def start_auto_switch_thread(self):
        thread = threading.Thread(target=self.auto_switch_servers)
        thread.daemon = True
        thread.start()

    def get_bandwidth_stats(self):
        # We can't easily get this from stdout without parsing management interface.
        # Returning dummy data or implementation for another time.
        return 0, 0

    # Windows Kill Switch (Same as before)
    def enable_kill_switch(self):
        self.logger.info("Enabling Kill Switch...")
        try:
            cmd = ['netsh', 'advfirewall', 'firewall', 'add', 'rule', 
                   'name="AG_VPN_KillSwitch"', 'dir=out', 'action=block', 'enable=yes']
            
            # Need to get the actual OpenVPN EXE to whitelist it?
            # Or just the remote IP.
            if self.current_server:
                ip = self.current_server['ip']
                allow_cmd = ['netsh', 'advfirewall', 'firewall', 'add', 'rule',
                             f'name="AG_VPN_Allow_{ip}"', 
                             'dir=out', 'action=allow', f'remoteip={ip}']
                subprocess.run(allow_cmd, shell=True, check=False)

            subprocess.run(cmd, shell=True, check=False)
            self.kill_switch_active = True
        except Exception as e:
            self.logger.error(f"Failed to enable Kill Switch: {e}")

    def disable_kill_switch(self):
        self.logger.info("Disabling Kill Switch...")
        try:
            subprocess.run(['netsh', 'advfirewall', 'firewall', 'delete', 'rule', 'name="AG_VPN_KillSwitch"'], 
                           shell=True, check=False)
            # Remove specific allows? ideally yes.
            # subprocess.run(['netsh', 'advfirewall', 'firewall', 'delete', 'rule', 'name="AG_VPN_Allow_..."'], ...)
            self.kill_switch_active = False
        except Exception as e:
            self.logger.error(f"Failed to disable Kill Switch: {e}")
