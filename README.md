# WiFi Network Scanner for macOS

A Python script that uses CoreWLAN and CoreLocation frameworks to scan for WiFi networks on macOS. This script provides detailed information about the current network connection and available networks in the area.

## Features

- Get current WiFi connection details including:
  - SSID
  - BSSID
  - Channel information
  - Signal strength (RSSI)
  - Noise level
  - Transmission rate
  - Security mode

- Scan for available networks with:
  - Automatic retry on busy interface
  - Persistent scanning until successful
  - Support for filtering by specific SSID
  - Comprehensive network information

- Smart location services handling:
  - Automatic detection of existing authorization
  - Quick initial scan to check authorization status
  - Cached authorization state for better performance
  - Clear user feedback about authorization status

## Requirements

- macOS (tested on Sonoma)
- Python 3.x
- pyobjc-framework-CoreWLAN
- pyobjc-framework-CoreLocation

## Installation

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the script:
```bash
./test_wifi_scanning.py
```

First time running:
1. The script will check if location services are already authorized
2. If not authorized, it will request location access
3. Accept the location services prompt when it appears

Subsequent runs:
- Uses cached authorization status for faster execution
- Automatically retries scanning if the interface is busy
- Continues scanning until successful

## Output

The script provides information in three sections:

1. Current Network:
```
Current Network:
interface: en0
ssid: MyNetwork
bssid: aa:bb:cc:dd:ee:ff
channel: channelNumber=36(5GHz)
rssi: -45
noise: -90
tx_rate: 1299.0
security_mode: WPA2 Personal
```

2. Available Networks:
- List of all visible networks with their details
- Automatically retries if scanning is temporarily unavailable

3. Preferred Networks:
- List of networks saved in system preferences

## Error Handling

- Gracefully handles "Resource busy" errors with automatic retry
- Clear feedback about location services status
- Detailed debug logging available if needed
- Resets authorization state on persistent errors

## Debugging

To enable debug logging, set the logging level to DEBUG in the script:
```python
logger.setLevel(logging.DEBUG)
```

This will show additional information such as:
- Scan retry attempts
- Authorization status changes
- Interface busy states

## Notes

- Location services must be enabled for WiFi scanning on macOS
- The script will continue retrying indefinitely until a successful scan
- Authorization status is cached to minimize system checks
- Debug messages are hidden by default for cleaner output

## Security Note

This script requires location access due to Apple's privacy requirements for WiFi scanning. The location permission is used solely for WiFi scanning purposes and no actual location data is collected or stored.

## Last Updated

January 11, 2025

## License

MIT License - Feel free to use and modify as needed.
