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

    
    
"""
format du fichier tcx : 

EN TÊTE

<?xml version="1.0" encoding="UTF-8"?>
<!-- Written by Strava -->
<TrainingCenterDatabase xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd" xmlns:ns5="http://www.garmin.com/xmlschemas/ActivityGoals/v1" xmlns:ns3="http://www.garmin.com/xmlschemas/ActivityExtension/v2" xmlns:ns2="http://www.garmin.com/xmlschemas/UserProfile/v2" xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
 <Activities>
 
SUM UP 


  <Activity Sport="Running">
   <Id>2020-11-25T12:00:09Z</Id>
   <Lap StartTime="2021-09-25T12:00:09Z">
    <TotalTimeSeconds>253</TotalTimeSeconds>
    <DistanceMeters>1000.0</DistanceMeters>
    <MaximumSpeed>5.2</MaximumSpeed>
    <Calories>1</Calories>
    <AverageHeartRateBpm>
     <Value>154</Value>
    </AverageHeartRateBpm>
    <MaximumHeartRateBpm>
     <Value>172</Value>
    </MaximumHeartRateBpm>
    <Intensity>Active</Intensity>
    <Cadence>97</Cadence>
    <TriggerMethod>Manual</TriggerMethod>
    <Track>


POINTAGE (À RÉPÉTER X FOIS° 

     <Trackpoint> 
      <Time>2021-09-25T12:00:09Z</Time>
      <Position>
       <LatitudeDegrees>43.3450840</LatitudeDegrees>
       <LongitudeDegrees>-1.6209490</LongitudeDegrees>
      </Position>
      <AltitudeMeters>34.6</AltitudeMeters>
      <DistanceMeters>0.1</DistanceMeters>
      <HeartRateBpm>
       <Value>110</Value>
      </HeartRateBpm>
      <Extensions>
       <TPX xmlns="http://www.garmin.com/xmlschemas/ActivityExtension/v2">
        <Speed>0.0</Speed>
        <RunCadence>0</RunCadence>
       </TPX>
      </Extensions>
     </Trackpoint>


FIN


    </Track>
   </Lap>
  </Activity>
 </Activities>
</TrainingCenterDatabase>

"""
