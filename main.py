"""
The main file that runs the simulation and sends to the database the data collected.
"""

import os
import sys
import logging
import requests
import traci

from datetime import datetime


logging.basicConfig(
    filename="main.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

sys.dont_write_bytecode = True

ARCHITECTURE_URL = YOUR_ARCHITECTURE_URL

logging.info(f"Starting SUMO simulation at [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")

traci.start([
    "sumo", "-c", "./sumo_files/osm.sumocfg",
    "--emission-output", "emission.xml",
])

while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    logging.info(f"Simulation time: [{traci.simulation.getTime()}] - Number of vehicles: [{len(traci.vehicle.getIDList())}]")

    for veh in traci.vehicle.getIDList():
        x, y = traci.vehicle.getPosition(veh)
        lon, lat = traci.simulation.convertGeo(x, y)

        data = {
            "vehid": veh,
            "timestamp_sumo": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "acceleration": round(traci.vehicle.getAcceleration(veh), 2),
            "co2_emission": round(traci.vehicle.getCO2Emission(veh), 2),
            "distance_odometer": round(traci.vehicle.getDistance(veh), 2),
            "eletri_consumption": round(traci.vehicle.getElectricityConsumption(veh), 2),
            "fuel_consumption": round(traci.vehicle.getFuelConsumption(veh), 2),
            "noise_emission": round(traci.vehicle.getNoiseEmission(veh), 2),
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "speed": round(traci.vehicle.getSpeed(veh), 2),
            "simulation_time": traci.simulation.getTime()
        }

        requests.post(
            url = ARCHITECTURE_URL,
            data = data
        )

traci.close()

logging.info(f"Ending SUMO simulation at [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
