# Home Assistant Integration - Mikrotik SwitchOS

Home Assistant integration for Mikrotik SwitchOS and SwitchOS Lite

[![Static Badge](https://img.shields.io/badge/HACS-Custom-41BDF5?style=for-the-badge&logo=homeassistantcommunitystore&logoColor=white)](https://github.com/hacs/integration) 
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/probert94/ha-switchos/total?style=for-the-badge)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/probert94/ha-switchos?style=for-the-badge)
[![GitHub Release](https://img.shields.io/github/v/release/probert94/ha-switchos?style=for-the-badge)](https://github.com/probert94/ha-switchos/releases)

## HACS install
To install the integration in your Home Assistant instance, use this My button:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=probert94&repository=ha-switchos&category=Integration)

Alternatively, you can add it to HACS by following this steps:
1. Go to HACS
2. Click on the 3 points in the upper right corner and click `Custom repositories`
3. Paste https://github.com/probert94/ha-switchos into `Repository` and select type `Integration`
4. Click `ADD` and check if the repository can be found in HACS
5. Select it and click `INSTALL`

## Configuration

1. After installing the integration use this My button to add it to your Home Assistant instance:

    [![Open your Home Assistant instance and add an integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=mikrotik_switchos)

    Alternatively, go to Settings -> Devices & Services in Home Assistance, click `ADD INTEGRATION`, search for "Mikrotik SwitchOS" and install it.

2. In the configuration dialog enter the following details:
    - Host: The address of the Mikrotik SwitchOS device (e.g. `http://192.168.1.2`)
    - Username: The __case sensitive__ username, defaults to _admin_ (cannot be changed in current SwitchOS versions)
    - Password: The password

## Features

The integration displays model, firmware, serial number and MAC address of the SwitchOS device.  
It also reads information about the ports, including the customized name which is then used for the entities.

### Sensors
- PoE power
- PoE current
- PoE voltage

### Compatibility

The integration has been tested with:
| Model | Versions |
| - | - |
| CSS610-8P-2S+ | 2.20 |
