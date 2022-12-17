# Renogy Smart Battery - Home-Assistant

A simple script I made to send information to Home Assistant from Renogy Smart Batteries.


I use it with four batteries, If you want to use it with more than one you need to connect to each battery separately first to change the address.

```
#Set the battery address to change (change to desired address), Set to false to get info
new_address = False
```

Batteries come with a default address is 247.

```
#Set the addresses of the batteries

#For multiple batteries, use the following format after changing the addresses
battery_addresses = {1:11,2:12,3:13,4:14}

#Default address is 247
battery_addresses = {1:247}
```

I run this every minute using a cron job, lazy way to deal with errors if they appear.
```
* * * * * python3 /PATH/TO/SCRIPT/batteryinfo.py
```

I have included the corresponding webhook template for homeassitant, you will have to edit this to add or remove batteries if you are not running four.
