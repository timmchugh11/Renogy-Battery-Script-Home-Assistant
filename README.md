# Renogy Smart Battery - Home-Assistant

A simple script I made to send infomation to Home Assistant from Renogy Smart Batteries.

I use it with four batteries, If you want to use it with more than one you need to connect to each battery seperatly first to change the address.

Batteries come with a default address is 247.

I run this every minute using a cron job, lazy way to deal with errors if they appear.

I have included the corresponding webhook template for homeassitant, you will have to edit this to add or remove batteries if you are not running four.
