# Inverter Configuration
To enable Modbus TCP on the GEN 24, point your browser to the IP of your inverter. We assume that your inverter is attached to your LAN/WLAN and is accessible.
You need to login as "Technician", go to "Communication", "Modbus".
Enable "Slave as Modbus TCP", set the Modbus Port (default: 502). For this documentation, we assume that the SunSpec Model Type is set to "float".
The Meter Address is commonly set to 200 or 240 - this ID needs to be configured in the test client as Object Number. 
Inverter Control via Modbus can be disabled. 

![Inverter Configuration](https://github.com/oscarknapp/Fronius-Gen-24-Modbus-Integration/tree/main/Documentation/assets/01_inverterconfiguration.png "Inverter Configuration")
