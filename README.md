# Anti-Gravity VPN

Anti-Gravity VPN is a robust, Python-based desktop VPN application designed for simplicity and versatility. It aggregates VPN servers from multiple sources, ensuring you always have a reliable connection option.

## Features

*   **Multi-Source Server Aggregation**:
    *   **Local Configs**: Automatically loads `.ovpn` configuration files from a local directory.
    *   **Cloud Servers**: Fetches real-time server configurations from GitHub repositories.
    *   **VPN Gate**: Falls back to the VPN Gate public relay server network if other sources are unavailable.
*   **Modern GUI**: Built with `customtkinter` for a sleek, dark-mode friendly user interface.
*   **Kill Switch**: Optional kill switch functionality to block traffic if the VPN connection drops.
*   **Manual Import**: Easily import custom `.ovpn` files directly from the UI.
*   **Admin Privileges**: Automatically requests necessary administrative permissions for OpenVPN operations.

## Requirements

*   **OS**: Windows (due to `ctypes` admin checks and OpenVPN integration specifics).
*   **Python**: Python 3.8 or higher.
*   **OpenVPN**: Must be installed and accessible on the system.

### Python Dependencies

Install the required Python packages using pip:

```bash
pip install customtkinter requests
```

## Usage

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/sajjadacademy/VPN-For-desktop.git
    cd VPN-For-desktop
    ```

2.  **Run the Application**:
    Execute the main script. The application will automatically request Administrator privileges which are required to modify network routes.

    ```bash
    python main.py
    ```

3.  **Connect**:
    *   Select a server from the dropdown list.
    *   Click "Connect" to establish a secure VPN tunnel.

## Project Structure

*   `main.py`: The entry point of the application. Handles initialization and server fetching.
*   `gui.py`: Contains the `VPNApp` class, defining the user interface using `customtkinter`.
*   `vpn_core.py`: Manages the OpenVPN process and connection logic.
*   `local_config_fetcher.py`: Scans for local `.ovpn` files.
*   `zoult_fetcher.py` & `vpn_gate_fetcher.py`: Modules for fetching remove server configurations.
*   `configuration files/`: Directory for placing your custom `.ovpn` files.

## Disclaimer

This project is for educational purposes. Ensure you comply with the terms of service of any VPN provider or public network you access.
