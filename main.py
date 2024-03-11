"""
Through Traffic Factor: 1000
Count: 1000
Duration: 25
"""

import os
import sys
import psutil
import logging
import traci
import requests

from datetime import datetime
from dotenv import dotenv_values


sys.dont_write_bytecode = True

if "--instance" in sys.argv:
    instance = sys.argv[sys.argv.index("--instance") + 1]
else:
    print("Please, provide the instance number using --instance flag")
    sys.exit(1)

if "--steps" in sys.argv:
    steps = int(sys.argv[sys.argv.index("--steps") + 1])
else:
    steps = 30

logging.basicConfig(
    filename=f"{sys.argv[0].split('.')[0]}_{instance}.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

pid = os.getpid()
process = psutil.Process(pid)

env_vars = dotenv_values(".env")
ARCHITECTURE_URL = env_vars.get("ARCHITECTURE_URL")

logging.info(f"Starting SUMO simulation at [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")

traci.start([
    "sumo", "-c", "./sumo_files/osm.sumocfg",
    "--emission-output", "emission.xml",
], label=f"sumo_{instance}")

while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    
    sim_time = traci.simulation.getTime()

    if sim_time > steps:
        break

    for veh in traci.vehicle.getIDList():
        x, y = traci.vehicle.getPosition(veh)
        lon, lat = traci.simulation.convertGeo(x, y)

        data = {
            "vehid": f"{veh}_{instance}",
            "timestamp_sumo": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
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
    
    logging.info(f"STEP: [{traci.simulation.getTime()}] - MEM: [{process.memory_percent():.4f}%] - CPU: [{process.cpu_percent():.4f}%] - VEH: [{len(traci.vehicle.getIDList())}]")

traci.close()

logging.info(f"Ending SUMO simulation at [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
