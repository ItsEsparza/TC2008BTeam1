from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import *
import json

class CityModel(Model):
    """ 
        Creates a model based on a city map.

        Args:
            N: Number of agents in the simulation
    """
    def __init__(self, N):

        # Load the map dictionary. The dictionary maps the characters in the map file to the corresponding agent.
        dataDictionary = json.load(open("city_files/mapDictionary.json"))

        self.traffic_lights = []

        # Load the map file. The map file is a text file where each character represents an agent.
        with open('city_files/2024_base.txt') as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0])-1
            self.height = len(lines)

            self.grid = MultiGrid(self.width, self.height, torus = False) 
            self.schedule = RandomActivation(self)

            # Goes through each character in the map file and creates the corresponding agent.
            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    if col in ["v", "^", ">", "<"]:
                        agent = Road(f"r_{r*self.width+c}", self, dataDictionary[col])
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col in ["S", "s"]:
                        agent = Traffic_Light(f"tl_{r*self.width+c}", self, False if col == "S" else True, int(dataDictionary[col]))
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)
                        self.traffic_lights.append(agent)

                    elif col == "#":
                        agent = Obstacle(f"ob_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col == "D":
                        agent = Destination(f"d_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

        self.num_agents = N
        
        #Variables for spawning cars
        self.corners = [(0, 0), (0, self.grid.height - 1), (self.grid.width - 1, 0), (self.grid.width - 1, self.grid.height - 1)] # Spawining locations
        self.i = 0  # Selected corner index

        # Add cars in the corners
        for (x, y) in self.corners:
            if self.num_agents > 0:
                road = next((agent for agent in self.grid.get_cell_list_contents((x, y)) if isinstance(agent, Road)), None)
                agent = Car(f"car_{x}_{y}", self, direction=road.direction)
                self.grid.place_agent(agent, (x, y))
                self.schedule.add(agent)
                self.num_agents -= 1
                
                self.running = True
                
    def spawnCars(self):
        # Get the current step
        current_step = self.schedule.time

        # Spawn a new car every 10 steps
        if current_step > 0 and current_step % 10 == 0:
            print(f"Spawning a car at step {current_step}")
            
            # Get the current corner and increment `i`
            x, y = self.corners[self.i]
            self.i = (self.i + 1) % len(self.corners)  # Cycle `i` between 0 and 3

            # Check if there's a road at the selected corner
            road = next((agent for agent in self.grid.get_cell_list_contents((x, y)) if isinstance(agent, Road)), None)
            if road:
                # Spawn a car at the selected corner
                agent = Car(f"car_{x}_{y}_{current_step}", self, direction=road.direction)
                self.grid.place_agent(agent, (x, y))
                self.schedule.add(agent)
                self.num_agents -= 1
        
        

    def step(self):
        '''Advance the model by one step.'''
        self.spawnCars()
        self.schedule.step()