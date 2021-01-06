# Overview of Modbus registers in Fronius Gen 24 Inverters

Note: the provided register information is valid only for inverters configured to operate in floating mode

|Register Nr | Datatype | Description|
|--------|-----------|-----|
|40092 | Float 32 |Inverter AC Output in W |
|40285 | UInt 16 |PV String 1 Output in W (scaled) |
|40305 | UInt 16 |PV String 2 Output in W (scaled) |
|40267 | Int 16 |DC Scaling Factor |
|40361 | UInt 16 |Battery SoC in % (scaled, SF -2) |
|40325 | UInt 16 |Energy To Battery in W (scaled, charging) |
|40345 | UInt 16 |Energy From Battery in W  (scaled, discharging) |
| | | |
|40098 | Float 32 |Energy from/to grid in W (positive values: consumption; negative values: delivery); mind that you need to specify the Modbus unit number for your meter|
| | | |

Important note (page 13 of the Fronius documentation): to query register values, you need to decrease the register number by 1.
