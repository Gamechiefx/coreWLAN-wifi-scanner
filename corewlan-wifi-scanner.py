#!/usr/bin/env python3

import objc
import logging
import time
from typing import Dict, List, Optional, Tuple
from CoreLocation import (
    CLLocationManager,
    kCLAuthorizationStatusNotDetermined,
    kCLAuthorizationStatusRestricted,
    kCLAuthorizationStatusDenied,
    kCLAuthorizationStatusAuthorizedWhenInUse,
    kCLAuthorizationStatusAuthorizedAlways
)
from Foundation import NSDate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LocationAuthDelegate(objc.lookUpClass('NSObject')):
    """Delegate to handle location authorization callbacks"""
    
    def init(self):
        self = objc.super(LocationAuthDelegate, self).init()
        if self is not None:
            self.auth_event = False
        return self
    
    def locationManager_didChangeAuthorizationStatus_(self, manager, status):
        """Called when location authorization status changes"""
        self.auth_event = True
        status_map = {
            kCLAuthorizationStatusNotDetermined: "not determined",
            kCLAuthorizationStatusRestricted: "restricted",
            kCLAuthorizationStatusDenied: "denied",
            kCLAuthorizationStatusAuthorizedWhenInUse: "authorized when in use",
            kCLAuthorizationStatusAuthorizedAlways: "authorized always"
        }
        logger.info(f"Location authorization status changed to: {status_map.get(status, 'unknown')}")

class WiFiScanner:
    def __init__(self):
        """Initialize WiFi scanner"""
        # Load CoreWLAN framework
        bundle_path = '/System/Library/Frameworks/CoreWLAN.framework'
        objc.loadBundle('CoreWLAN',
                       bundle_path=bundle_path,
                       module_globals=globals())
        
        # Get WiFi interface first
        self.interface = CWInterface.interface()
        if not self.interface:
            raise RuntimeError("No WiFi interface available")
            
        logger.info(f"Using WiFi interface: {self.interface.interfaceName()}")
        
        # Initialize location manager and delegate
        self.location_delegate = LocationAuthDelegate.alloc().init()
        self.location_manager = CLLocationManager.alloc().init()
        self.location_manager.setDelegate_(self.location_delegate)
        
        # Track authorization state
        self._has_auth = False
        
        # Try a quick scan to check if we already have permission
        try:
            _, error = self.interface.scanForNetworksWithSSID_error_(None, None)
            if not error:
                logger.info("Location services already authorized - WiFi scanning working")
                self._has_auth = True
                return
        except Exception:
            pass

        # If we get here, we need to check/request authorization
        auth_status = CLLocationManager.authorizationStatus()
        if auth_status == kCLAuthorizationStatusNotDetermined:
            logger.info("Requesting location authorization...")
            self.location_manager.requestWhenInUseAuthorization()
            
        elif auth_status in [kCLAuthorizationStatusAuthorizedWhenInUse, 
                           kCLAuthorizationStatusAuthorizedAlways]:
            logger.info("Location services authorized in system settings")
            self._has_auth = True
        else:
            logger.error("Location services not authorized. WiFi scanning may be limited.")
            logger.error("Please enable location services for this application in System Settings.")
    
    def check_location_auth(self) -> bool:
        """Check if we have proper location authorization"""
        if self._has_auth:
            return True
            
        # Recheck authorization through scan
        try:
            _, error = self.interface.scanForNetworksWithSSID_error_(None, None)
            if not error:
                self._has_auth = True
                return True
        except Exception:
            pass
        
        return False
    
    def get_current_network(self) -> Dict[str, str]:
        """Get information about currently connected network"""
        if not self.check_location_auth():
            logger.warning("Limited network information available without location authorization")
            
        try:
            return {
                "interface": self.interface.interfaceName(),
                "ssid": self.interface.ssid(),
                "bssid": self.interface.bssid(),
                "channel": self.interface.wlanChannel(),
                "rssi": self.interface.rssiValue(),
                "noise": self.interface.noiseMeasurement(),
                "tx_rate": self.interface.transmitRate(),
                "security_mode": self._get_security_string(self.interface.security())
            }
        except Exception as e:
            logger.error(f"Error getting current network: {e}")
            return {}
    
    def _get_security_string(self, security_mode: int) -> str:
        """Convert security mode integer to string"""
        security_map = {
            0: "None",
            1: "WEP",
            2: "WPA Personal",
            3: "WPA/WPA2 Personal",
            4: "WPA2 Personal",
            5: "WPA2/WPA3 Personal",
            6: "WPA3 Personal",
            7: "Dynamic WEP",
            8: "WPA Enterprise",
            9: "WPA/WPA2 Enterprise",
            10: "WPA2 Enterprise",
            11: "WPA2/WPA3 Enterprise",
            12: "WPA3 Enterprise"
        }
        return security_map.get(security_mode, f"Unknown ({security_mode})")
    
    def scan_networks(self, ssid: Optional[str] = None, retry_delay: float = 2.0) -> List[Dict[str, str]]:
        """Scan for available WiFi networks
        
        Args:
            ssid: Optional SSID to scan for specifically
            retry_delay: Delay in seconds between retries
            
        Returns:
            List of dictionaries containing network information
        """
        if not self.check_location_auth():
            logger.error("Location authorization required for network scanning")
            logger.error("Please enable location services and try again")
            return []
            
        # Convert SSID to NSData if provided
        ssid_data = None
        if ssid:
            ssid_data = ssid.encode('utf-8')
        
        # Try scanning until successful
        attempt = 1
        while True:
            try:
                # Perform scan
                networks, error = self.interface.scanForNetworksWithSSID_error_(ssid_data, None)
                
                if error:
                    error_domain = error.domain()
                    error_code = error.code()
                    
                    # Check for resource busy error (NSPOSIXErrorDomain, code 16)
                    if str(error_domain) == 'NSPOSIXErrorDomain' and error_code == 16:
                        logger.debug(f"Scan attempt {attempt} failed with resource busy, retrying...")
                        time.sleep(retry_delay)
                        attempt += 1
                        continue
                    else:
                        logger.debug(f"Scan attempt {attempt} failed: domain={error_domain}, code={error_code}")
                        time.sleep(retry_delay)
                        attempt += 1
                        continue
                
                # Process results
                results = []
                for network in networks:
                    try:
                        network_info = {
                            "ssid": network.ssid(),
                            "bssid": network.bssid(),
                            "rssi": network.rssiValue(),
                            "channel": network.wlanChannel(),
                            "is_ibss": network.ibss(),
                            "noise": network.noiseMeasurement(),
                            "country_code": network.countryCode()
                        }
                        results.append(network_info)
                    except Exception as e:
                        logger.warning(f"Error processing network {network.ssid()}: {e}")
                        continue
                
                # If we got results, return them
                if results:
                    return results
                else:
                    logger.debug("No networks found, retrying...")
                    time.sleep(retry_delay)
                    attempt += 1
                    continue
                
            except Exception as e:
                logger.debug(f"Scan attempt failed: {e}")
                time.sleep(retry_delay)
                attempt += 1
                continue
    
    def get_preferred_networks(self) -> List[Dict[str, str]]:
        """Get list of preferred (saved) networks"""
        if not self.check_location_auth():
            logger.warning("Limited network information available without location authorization")
            
        try:
            networks = []
            config = self.interface.configuration()
            if not config:
                return []
                
            preferred = config.preferredNetworks()
            if not preferred:
                return []
                
            for network in preferred:
                try:
                    network_info = {
                        "ssid": network.ssid(),
                        "security_mode": self._get_security_string(network.security()),
                        "is_auto_join": network.autoJoin(),
                        "last_connected": network.lastConnected()
                    }
                    networks.append(network_info)
                except Exception as e:
                    logger.warning(f"Error processing preferred network: {e}")
                    continue
                    
            return networks
            
        except Exception as e:
            logger.error(f"Error getting preferred networks: {e}")
            return []

def main():
    try:
        # Initialize scanner with location auth handling
        scanner = WiFiScanner()
        
        # Get current network info
        logger.info("\nCurrent Network:")
        current = scanner.get_current_network()
        for key, value in current.items():
            logger.info(f"{key}: {value}")
        
        # Scan for networks
        logger.info("\nAvailable Networks:")
        networks = scanner.scan_networks()
        for network in networks:
            logger.info("-" * 50)
            for key, value in network.items():
                logger.info(f"{key}: {value}")
        
        # Get preferred networks
        logger.info("\nPreferred Networks:")
        preferred = scanner.get_preferred_networks()
        for network in preferred:
            logger.info("-" * 50)
            for key, value in network.items():
                logger.info(f"{key}: {value}")
                
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == '__main__':
    main()
