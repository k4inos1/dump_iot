## 🚀 Features

*   **📡 Monitor Mode Automation:** One-click activation for Fenvi AX1800 (RTL8852BU) and other adapters.
*   **🕵️ Intensive Tracking:** Real-time detection of nearby devices via Probe Requests (MAC, RSSI, SSID History).
*   **⚔️ Offensive Tools:**
    *   **Deauth Attack:** Disconnect targets from their networks.
    *   **Vuln Scan:** Automated Nmap vulnerability scanning.
    *   **Bettercap:** Integrated MITM and sniffing capabilities.
*   **☁️ Cloud Intelligence:** Real-time synchronization of logs and detected networks to **Firebase Realtime Database**.
*   **🎛️ Dual Consoles:**
    *   **GUI (Graphical):** Modern Dark-Mode interface with Smart Target Selection.
    *   **CLI (Terminal):** Lightweight TUI for SSH connections.

## 🛠️ Installation

1.  **Clone the repository** to your Raspberry Pi:
    ```bash
    git clone https://github.com/YOUR_USERNAME/kainos-auditor.git
    cd kainos-auditor
    ```

2.  **Install Dependencies:**
    ```bash
    chmod +x install_warfare.sh
    sudo ./install_warfare.sh
    ```

3.  **Setup Credentials:**
    *   Place your Firebase Service Account JSON in the folder (DO NOT COMMIT IT).
    *   Run the generator to secure it:
        ```bash
        python3 generate_env.py
        ```

## 🎮 Usage

### Graphical Console (Recommended for RDP)
```bash
python3 console.py
```
*   **Smart Selection:** Scan networks first, then use the dropdown to auto-fill BSSID and Channel.
*   **Sync Switch:** Toggle cloud upload on/off.

### Terminal Console (Recommended for SSH)
```bash
python3 console_cli.py
```

## 📂 Project Structure

*   `console.py`: Main GUI Application.
*   `console_cli.py`: Terminal Interface.
*   `tracker.py`: Scapy-based Probe Request sniffer.
*   `sync_service.py`: Background daemon for Firebase sync.
*   `vuln_scan.sh`: Nmap automation script.
*   `setup_monitor.sh`: Helper for monitor mode.

---
