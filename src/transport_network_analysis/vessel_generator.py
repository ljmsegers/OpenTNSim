"""Vessel generator."""

# package(s) related to time, space and id
import json
import logging
import uuid

# you need these dependencies (you can get these from anaconda)
# package(s) related to the simulation
import simpy
import networkx as nx

# spatial libraries
import pyproj
import shapely.geometry

# additional packages
import datetime, time
import random

# import core from self
import transport_network_analysis.core as core

logger = logging.getLogger(__name__)


class VesselGenerator:
    """
    A class to generate vessels from a database
    """

    def __init__(self, vessel_type, vessel_database, random_seed = 4):
        """ Initialization """

        self.vessel_type = vessel_type
        self.vessel_database = vessel_database

        random.seed(random_seed)
    
    def generate(self, environment, vessel_name, path = None, scenario = None):
        """ Generate a vessel """

        vessel_info = self.vessel_database.sample(n = 1, random_state = int(1000 * random.random()))
        vessel_data = {}

        vessel_data["env"] = environment
        vessel_data["name"] = vessel_name

        if scenario:
            vessel_info = vessel_info[vessel_info["scenario"] == scenario]

        for key in vessel_info:
            if key == "vessel_id":
                vessel_data["id"] = vessel_info[key].values[0]
            else:
                vessel_data[key] = vessel_info[key].values[0]
        
        if path:
            vessel_data["route"] = path
            vessel_data["geometry"] = nx.get_node_attributes(environment.FG, "geometry")[path[0]]
        
        return self.vessel_type(**vessel_data)
    
    def arrival_process(self, environment, arrival_distribution = 1, arrival_process = "Markovian"):
        """ 
        Make arrival process
        
        environment:            simpy environment
        arrival_distribution:   specify the distribution from which vessels are generated, int or list
        arrival_process:        process of arrivals
        """

        # Create an array with inter-arrival times -- average number of seconds between arrivals
        if type(arrival_distribution) == int:
            self.inter_arrival_times = [3600 / arrival_distribution] * 24
        
        elif type(arrival_distribution) == list and len(arrival_distribution) == 24:
            self.inter_arrival_times = [3600 / n for n in arrival_distribution]
        
        elif type(arrival_distribution) == list:
            raise ValueError("List should contain an average number of vessels per hour for an entire day: 24 entries")
        
        else:
            raise ValueError("Specify an arrival distribution: type Integer or type List")
        
        while True:

            # Check simulation time
            inter_arrival = self.inter_arrival_times[datetime.datetime.fromtimestamp(environment.now).hour]

            # In the case of a Markovian arrival process
            if arrival_process == "Markovian":

                # Make a timestep based on the poisson process
                time = random.expovariate(inter_arrival)
                
                environment.arrivals.append(time)
                yield environment.timeout(time)

                # Create a vessel
                vessel = environment.vessel_generator.generate()

                # Move on path
                


class Simulation(core.SimpyObject, core.Identifiable):
    """
    A class to generate vessels from a database
    """

    def __init__(self, vessel_generator, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """ Initialization """

        self.vessel_generator = vessel_generator
    
    def run(self, duration = 24 * 60 * 60, scenario = None):
        """ 
        Run the simulation 
        
        duration:               specify the duration of the simulation in seconds
        scenario:               scenario with vessels - should be coupled to the database
        """ 

    


