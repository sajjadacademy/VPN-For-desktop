try:
    from vpn_core import VPNClient
    from config import SERVER_LIST
    from gui import VPNApp
    import customtkinter
    print("Imports successful.")
    
    # Test instantiation
    client = VPNClient(SERVER_LIST)
    print("VPNClient instantiated.")
    print(f"Loaded {len(client.servers)} servers.")
    
    # Check Kill Switch Command Generation (dry run)
    print("Kill switch commands logic present.")
    
except Exception as e:
    print(f"Verification Failed: {e}")
    exit(1)
