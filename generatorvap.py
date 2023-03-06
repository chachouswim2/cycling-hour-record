#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 14 01:03:57 2021

@author: josephmestrallet
"""
import datetime
import time

v=100
a=0
b=0

for a in range(21):
    for i in range(1,11):
        print("<Trackpoint><Time>2021-11-13T"+str(datetime.datetime.fromisoformat("2021-11-13T12:00:00")+datetime.timedelta(((v*i+a*v*10)/(60*3600))))[11:]+"Z</Time><AltitudeMeters>"+str(1*i*a+b)+"</AltitudeMeters><DistanceMeters>"+str(100*i+1000*a)+"</DistanceMeters></Trackpoint>")
    b+=a*10

