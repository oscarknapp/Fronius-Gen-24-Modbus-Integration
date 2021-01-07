# Copyright notes: this script was initially made public by user MobusTest in photovoltaikforum.com
# https://www.photovoltaikforum.com/thread/117173-datamanager-und-modbus-register-mit-modbus-tcp/?postID=2021510#post2021510
# This client re-uses all the modbus protocoll implementation and data conversion from the original work. 
# The client provides an easy way to explore modbus registers on a Fronius inverter
# This software is provided "as is" without any guarantee 


#!/usr/bin/env python
# -*- coding: utf-8 -*-

# >>> To install 'pymodbus' you have to execute the following linux command:  pip3 install pymodbus
# general imports
import datetime

# imports for Modbus
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.diag_message import *
from pymodbus.file_message import *
from pymodbus.other_message import *
from pymodbus.mei_message import *
from pymodbus.compat import iteritems

# imports for using enumerations
from enum import Enum

# enumeration by using a class. value of the enum ( 1-8 ) is irrelevant!
# use the method getRegisterLength() instead
class DataType(Enum):
    String8 = 1
    String16 = 2
    String32 = 3
    Int16 = 4
    UInt16 = 5
    Int32 = 6
    UInt32 = 7
    Float32 = 8
    UInt64 = 7

    # Returns the length (amount) of the registers.
    # This corresponds to the value from the Fronius Excel list (column "Size").
    # This refers to how many registers the Mobus function read_holding_registers() must read to get the complete value
    def getRegisterLength(self):

        if (self == DataType.String8) or (self == DataType.UInt64):
            return int(4)
        elif (self == DataType.String16):
            return int(8)
        elif (self == DataType.String32):
            return int(16)
        elif (self == DataType.Int16) or (self == DataType.UInt16):
            return int(1)
        elif (self == DataType.Int32) or (self == DataType.UInt32) or (self == DataType.Float32):
            return int(2)

# -------------------------------------------------------------------------------------------------------[ private ]---
# | The Main Entry Point                                                                                              |
# ---------------------------------------------------------------------------------------------------------------------
def main():

    #print ("Current Time: " + datetime.datetime.now().strftime('%H:%M:%S'))

    # Open a new Modbus connection to the fronius inverter (e.g. Symo 10.3)
    modbusClient = ModbusClient("192.168.10.19", port=502, timeout=10)
    modbusClient.connect()

    # The modbus addresses of the registers are documented in the following lists:
    # - Inverter_Register_Map_Float_v1.0_with_SYMOHYBRID_MODEL_124.xlsx
    # - Meter_Register_Map_Float_v1.0.xlsx
    # Goto: https://www.fronius.com/en/photovoltaics/downloads and search for "Modbus Sunspec Maps, State Codes und Events"
    # Downloads the hole ZIP package and enjoy the documentation ;-) 
    #  
    # Gen 24 specific: 
    # Gen24_Primo_Symo_Inverter_Register_Map_Float_storage.xlsx
    # go to https://www.fronius.com/en/solar-energy/installers-partners/downloads
    # search for "GEN24 modbus" to find GEN24 related modbus documentation (register addresses are provided in the .zip file)
    #
    # Note: In this script you have to specify a data type when calling the method getRegisterValue(). This corresponds
    #       to the value from the Fronius Excel list (column "Type").
    #
    #       The optional parameter "unitNo" of method getRegisterValue() is used to specify from which device the
    #       data is to be read. The default value is 1 which corresponds to the inverter.
    #       If you want to read data from the SmartMeter, 240 must be used instead.

    # to use this script, adapt and enhance the following list with tuples, containing the follwing information 
    # [REGISTERADDRESS, DATATYPE, MODBUSUNITNUMBER] 
    # the MODBUSUNITNUMBER is commonly 1 for the inverter and a user defined value for the primary smart meter (common values are 200 or 240)

    print ("Register Overview:")
   
    reg_map = (
	[40092, DataType.Float32, 1], 	# Inverter AC Output in W
	[40285, DataType.UInt16, 1],  	# PV String 1 Output in W (scaled)
	[40305, DataType.UInt16, 1],  	# PV String 2 Output in W (scaled)
	[40267, DataType.Int16, 1],   	# DC Scaling Factor
	[40361, DataType.UInt16, 1],  	# Battery SoC in % (scaled, SF -2)
	[40325, DataType.UInt16, 1],  	# Energy To Battery in W (scaled, charging)
	[40345, DataType.UInt16, 1],  	# Energy From Battery in W  (scaled, discharging)
	[40098, DataType.Float32, 200],	# Energy to/from grid (smart meter, positive values: consumption)
	)
 
    for reg in reg_map:
      tmp_reg = getRegisterValue(modbusClient, reg[0], reg[1], reg[2])
      print ("Register " + str(reg[0]) + ": " + str(tmp_reg))

    modbusClient.close()

# -------------------------------------------------------------------------------------------------------[ private ]---
# | Gets a value from the inverter                                                                                    |
# | ----------------------------------------------------------------------------------------------------------------- |
# | Input parameters:                                                                                                 |
# | -> device           ModbusClient  An open connection to the modbus device (inverter or smartmeter)                |
# | -> address          INT           The starting address to read from                                               |
# | -> dataType         DataType      The DataType of registers to read                                               |
# | -> humidity         INT           The slave unit this request is targeting                                        |
# | ----------------------------------------------------------------------------------------------------------------- |
# | Return value:                                                                                                     |
# | <- result           STRING        Value of the defined address                                                    |
# ---------------------------------------------------------------------------------------------------------------------
def getRegisterValue(device, address, dataType, unitNo=1):

    #print ("  Adr: " + str(address) + "  Name: " + dataType.name)

    # Now we can read the data of the register with a Modbus function
    # In the fronius documentation it is described that you have to subtract 1 from the actual address.
    result = device.read_holding_registers(address-1, dataType.getRegisterLength(), unit=unitNo)

    if (result.isError()) :
        return "n.a."

    #print ("  value: " + str(result.registers))

    # The values from Modbus must now be reformatted accordingly
    # How to do this reformatting depends on the DataType
    decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big, wordorder=Endian.Big)

    if (dataType == DataType.String8) or (dataType == DataType.String16) or (dataType == DataType.String32):
        return str(decoder.decode_string(16).decode('utf-8'))

    elif (dataType == DataType.Int16):
        return decoder.decode_16bit_int()

    elif (dataType == DataType.UInt16):
        return decoder.decode_16bit_uint()

    elif (dataType == DataType.Int32):
        return decoder.decode_32bit_int()

    elif (dataType == DataType.UInt32):
        return decoder.decode_32bit_uint()

    elif (dataType == DataType.Float32):
        return decoder.decode_32bit_float()

    else:
        return str(decoder.decode_bits())


# -------------------------------------------------------------------------------------------------------[ private ]---
# | Formats the given nuber (powerValue) into a well-formed and readable text                                         |
# | ----------------------------------------------------------------------------------------------------------------- |
# | Input parameters:                                                                                                 |
# | -> powerValue       FLOAT   The value to format                                                                   |
# | ----------------------------------------------------------------------------------------------------------------- |
# | Return value:                                                                                                     |
# | <- formatedText     STRING  A well-formed and readable text containing the powerValue                             |
# ---------------------------------------------------------------------------------------------------------------------
def formatPowerText(powerValue):

    formatedText = ""

    # Over 1000 'kilo Watt' will be displayed instead of 'Watt'
    if abs(powerValue) > 1000:
        formatedText = "{0} kW".format(str('{:0.2f}'.format(powerValue / 1000))).replace('.', ',')
    else:
        formatedText = "{0} W".format(str('{:.0f}'.format(powerValue))).replace('.', ',')

    return formatedText


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# | Call the main function to start this script                                                                       |
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
main()

