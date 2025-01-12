# macOS WiFi Scanner for macOS versions later than 14.4 (sonoma)

A Python script that provides comprehensive WiFi network scanning capabilities for macOS using the native CoreWLAN framework. This script supports modern WiFi standards including WiFi 6E and provides detailed network information such as signal strength, channel information, and security modes.

## Features

- Get current WiFi connection details
- Scan for available WiFi networks
- View WiFi network security modes (WPA2, WPA3, etc.)
- Support for all WiFi bands (2.4GHz, 5GHz, 6GHz)
- List preferred (saved) networks
- Detailed network information including:
  - SSID and BSSID
  - Signal strength (RSSI) and noise levels
  - Channel information with band and width
  - Country codes
  - Security types
  - Network capabilities (IBSS)

## Requirements

- macOS 10.10 or later
- Python 3.7 or later
- Location Services access (required for WiFi scanning on modern macOS)

### Python Dependencies

```bash
pip install pyobjc
pip install pyobjc-framework-CoreWLAN
pip install pyobjc-framework-CoreLocation
```

## Installation

1. Clone or download this repository
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Ensure Location Services is enabled for Terminal/Python: (or you will be prompted)
   - Open System Settings
   - Navigate to Privacy & Security > Location Services
   - Find your Terminal app or Python in the list
   - Enable location access

2. Run the script:
   ```bash
   python3 corewlan-wifi-scanner.py
   ```

## Output Example

```
Current Network:
interface: en0
ssid: MyNetwork
bssid: ac:8b:a9:5c:5f:5b
channel: [channelNumber=40(5GHz), channelWidth={160MHz}]
rssi: -37
noise: -92
tx_rate: 2401.0
security_mode: WPA2 Personal

Available Networks:
--------------------------------------------------
ssid: Network1
bssid: 42:70:4e:59:37:7f
rssi: -62
channel: [channelNumber=128(5GHz), channelWidth={160MHz}]
is_ibss: False
noise: 0
country_code: US
```

## Security Note

This script requires location access due to Apple's privacy requirements for WiFi scanning. The location permission is used solely for WiFi scanning purposes and no actual location data is collected or stored.

## Last Updated

January 11, 2025

## License

MIT License - Feel free to use and modify as needed.
