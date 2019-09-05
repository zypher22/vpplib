# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 16:57:02 2019

@author: patri
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 15:33:53 2019

@author: patri
"""
from model.VPPUserProfile import VPPUserProfile as UP
from model.VPPThermalEnergyStorage import VPPThermalEnergyStorage
from model.VPPCombinedHeatAndPower import VPPCombinedHeatAndPower
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm 


start = '2017-01-01 00:00:00'
end = '2017-12-31 23:45:00'
year = '2017'
periods = None
freq = "15 min"

#Values for Thermal Storage
target_temperature = 60 # °C
hysteresis = 5 # °K
mass_of_storage = 500 # kg
yearly_heat_demand = 2500 # kWh

#Values for Heatpump
nominalPowerEl, nominalPowerTh = 4, 6 #kW
rampUpTime = 1/15 #timesteps
rampDownTime = 1/15 #timesteps
minimumRunningTime = 1 #timesteps
minimumStopTime = 2 #timesteps
timebase = 15


up = UP(heat_sys_temp = target_temperature, #Das könnte problematisch werden
        yearly_heat_demand = yearly_heat_demand, full_load_hours = 2100)

tes = VPPThermalEnergyStorage(timebase, mass = mass_of_storage, 
                              hysteresis = hysteresis, 
                              target_temperature = target_temperature, 
                              userProfile = up)

chp = VPPCombinedHeatAndPower(environment = None, identifier='chp1', timebase=timebase, userProfile = up,
                 nominalPowerEl = nominalPowerEl, nominalPowerTh = nominalPowerTh, rampUpTime = rampUpTime, 
                 rampDownTime = rampDownTime, 
                 minimumRunningTime = minimumRunningTime, 
                 minimumStopTime = minimumStopTime)

def test_get_heat_demand(tes):
    
    tes.userProfile.get_heat_demand()
    tes.userProfile.heat_demand.plot()
    plt.show()
    
test_get_heat_demand(tes)


loadshape = tes.userProfile.get_heat_demand()[0:]["heat_demand"]
outside_temp = tes.userProfile.mean_temp_hours.mean_temp
outside_temp.plot()
log, log_load, log_el = [], [],[]
#for i, heat_demand in tqdm(enumerate(loadshape)): 
chp.lastRampUp = chp.userProfile.heat_demand.index[0]
chp.lastRampDown = chp.userProfile.heat_demand.index[0]
for i in chp.userProfile.heat_demand.index:
    heat_demand = chp.userProfile.heat_demand.heat_demand.loc[i]
    if tes.get_needs_loading(): 
        chp.rampUp(i)              
    else: 
        chp.rampDown(i)
    temp = tes.operate_storage(heat_demand, i, chp)
    if chp.isRunning: 
        log_load.append(nominalPowerTh)
        log_el.append(nominalPowerEl)
    else: 
        log_load.append(0)
        log_el.append(0)
    log.append(temp)

pd.DataFrame(log).plot(figsize = (16,9), title = "Yearly Temperature of Storage")
pd.DataFrame(log)[10000:10960].plot(figsize = (16,9),title = "10-Day View")
pd.DataFrame(log)[10000:10096].plot(figsize = (16,9),title = "Daily View")
pd.DataFrame(log_load).plot(figsize = (16,9), title = "Yearly Electrical Loadshape")
pd.DataFrame(log_load)[20000:20960].plot(figsize = (16,9),title = "10-Day View")
pd.DataFrame(log_load)[20000:20096].plot(figsize = (16,9),title = "Daily View")
pd.DataFrame(log_el).plot(figsize = (16,9), title = "Yearly Electrical Loadshape")
pd.DataFrame(log_el)[20000:20960].plot(figsize = (16,9),title = "10-Day View")
pd.DataFrame(log_el)[20000:20096].plot(figsize = (16,9),title = "Daily View")
