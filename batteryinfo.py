import minimalmodbus, os, time, json, ast
from datetime import datetime
from requests import get

#Set the addresses of the batteries
#For multiple batteries, use the following format after changing the addresses
#battery_addresses = {1:11,2:12,3:13,4:14}
#Default address is 247
battery_addresses = {1:247}


#Set the USB port that the batteries are connected to
usb_device ="/dev/ttyUSB2"

#Set custom address to view another register
custom_address = ''

#Set Home Assistant URL
ha_url = "127.0.0.1:8123"

#Update interval in seconds
update_interval = 2

#Set the battery address to change (change to desired address), Set to false to get info
new_address = False

class RenogySmartBattery(minimalmodbus.Instrument):
    def __init__(self, slaveaddress, portname=usb_device, baudrate=9600, timeout=0.5):
        minimalmodbus.Instrument.__init__(self, portname, slaveaddress)
        self.serial.baudrate = baudrate
        self.serial.timeout = timeout

    def amps(self):
        r = self.read_register(5042)
        return r / 100.0 if r < 61440 else (r - 65535) / 100.0

    def volts(self):
        return self.read_register(5043) / 10.0

    def capacity(self):
        r = self.read_registers(5044, 2)
        return ( r[0] << 15 | (r[1] >> 1) ) * 0.002

    def max_capacity(self):
        r = self.read_registers(5046, 2)
        return ( r[0] << 15 | (r[1] >> 1) ) * 0.002

    def percentage(self):
        return round(self.capacity() / self.max_capacity() * 100,2)

    def custom(self, address):
        return self.read_register(address)

    def state(self):
        a = self.amps()
        if a < 0: return "Discharging"
        elif a > 0: return "Charging"
        return "Idle"

    def changeAddress(self,value):
        try:
            return self.write_register(5223, value)
        except Exception as e:
            print(e)

min = datetime.now().minute
time_rem_check = False
ave_amps_now = []

ave_amps = []

if new_address:
    RenogySmartBattery(247).changeAddress(new_address)
else:
    while datetime.now().minute == min:
        info = {}
        for battery in battery_addresses:
            info[battery] = RenogySmartBattery(battery_addresses[battery])
            info[str(battery) + "amps"] = info[battery].amps()
            info[str(battery) + "volts"] = info[battery].volts()
            info[str(battery) + "capacity"] = info[battery].capacity()
            info[str(battery) + "max_capacity"] = info[battery].max_capacity()
            info[str(battery) + "percentage"] = info[battery].percentage()
            info[str(battery) + "state"] = info[battery].state()
        
        for battery in battery_addresses:    
            voltage = info[str(battery) + "volts"] 
            curlcmd = 'curl --header "Content-Type: application/json" --request POST --data \'{"current":"' + str(info[str(battery) + "amps"] ) + '","percent":"' + str(info[str(battery) + "percentage"]) + '","status":"' + str(info[str(battery) + "state"]) + '","wattage":"' + str(round(float(info[str(battery) + "amps"]) * float(voltage),2)) + '"}\' http://' + ha_url + '/api/webhook/battery'+str(battery)
            os.system(curlcmd)
        total_amps = 0
        for battery in battery_addresses:
            total_amps = total_amps + info[str(battery) + "amps"]
        total_amps = round(total_amps,2)
        total_percentages = []
        for battery in battery_addresses:
            total_percentages.append(info[str(battery) + "percentage"])
        total_percentage = 101
        for line in total_percentages:
            if line < total_percentage:
                total_percentage = line
        ave_amps.append(total_amps)
        wattage = round(float(voltage) * total_amps)

        if datetime.now().second > 55 and time_rem_check == False:
            if len(ave_amps) > 0:
                aveamps = sum(ave_amps) / len(ave_amps)
                percent_total = 0
                for battery in battery_addresses:
                    percent_total = percent_total + info[str(battery) + "percentage"]
                if aveamps < 0:
                    time_rem = round((percent_total)/float(str(aveamps).replace('-','')),2)
                    hours = int(time_rem)
                    mins = int((time_rem - int(time_rem))*60.0)
                    string = '{} hours, {} mins remaining'.format(hours,mins)
                else:
                    time_rem = round((400 - (percent_total))/aveamps,2)
                    hours = int(time_rem)
                    mins = int((time_rem - int(time_rem))*60.0)
                    string = '{} hours, {} mins until full charged'.format(hours,mins)
                time_rem_check = True
                curlcmd = 'curl --header "Content-Type: application/json" --request POST --data \'{"time_rem":"' + str(string) + '"}\' http://' + ha_url + '/api/webhook/batteryrem'
                os.system(curlcmd)

        curlcmd = 'curl --header "Content-Type: application/json" --request POST --data \'{"current":"' + str(total_amps) + '","percent":"' + str(total_percentage) + '","wattage":"' + str(wattage) + '"}\' http://' + ha_url + '/api/webhook/battery'
        os.system(curlcmd)

        if wattage < 0:
            inwatt = 0
            outwatt = str(wattage).replace('-','')
        else:
            inwatt = str(wattage).replace('-','')
            outwatt = 0
        curlcmd = 'curl --header "Content-Type: application/json" --request POST --data \'{"in":"' + str(inwatt) + '","out":"' + str(outwatt) + '"}\' http://' + ha_url + '/api/webhook/batteryinout'
        os.system(curlcmd)
        if custom_address:
            for battery in battery_addresses:
                print('Battery ' + str(battery_addresses[battery]) + ' Custom Address Value: ' + str(battery_addresses[battery].custom(custom_address)))
        time.sleep(update_interval)

