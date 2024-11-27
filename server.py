from agent import *
from model import CityModel
from mesa.visualization import CanvasGrid, BarChartModule
from mesa.visualization import ModularServer

def agent_portrayal(agent):
    if agent is None: return
    portray_directions = False
    
    portrayal = {"Shape": "rect",
                    "Filled": "true",
                    "Layer": 1,
                    "w": 1,
                    "h": 1
                    }

    if (isinstance(agent, Road)):
        portrayal["Color"] = "gray"
        portrayal["h"] = 1
        portrayal["w"] = 1
         
        """if agent.direction == "Up":
            portrayal["Shape"] = "Images/up.png"
            portrayal["w"] = 1
            portrayal["h"] = 0.5
        elif agent.direction == "Down":
            portrayal["Shape"] = "Images/down.png"
            portrayal["w"] = 1
            portrayal["h"] = 0.5
        elif agent.direction == "Left":
            portrayal["Shape"] = "Images/left.png"
            portrayal["w"] = 0.5
            portrayal["h"] = 1
        elif agent.direction == "Right":
            portrayal["Shape"] = "Images/right.png"
            portrayal["w"] = 0.5
            portrayal["h"] = 1"""
            
        portrayal["Layer"] = 0
    
    if (isinstance(agent, Destination)):
        portrayal["Color"] = "lightgreen"
        portrayal["Layer"] = 0

    if (isinstance(agent, Traffic_Light)):
        portrayal["Color"] = "red" if not agent.state else "green"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    if (isinstance(agent, Obstacle)):
        portrayal["Color"] = "cadetblue"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1
        
    if (isinstance(agent, Car)):  
        portrayal["Color"] = "blue"   
        if agent.direction == "Up":
            portrayal["Shape"] = "Images/up.png"
        elif agent.direction == "Down":
            portrayal["w"] = 1
            portrayal["h"] = 1
            portrayal["Shape"] = "Images/down.png"
        elif agent.direction == "Left":
            portrayal["Shape"] = "Images/left.png"
        elif agent.direction == "Right":
            portrayal["Shape"] = "Images/right.png"
            

    return portrayal

width = 0
height = 0

with open('city_files/2024_base.txt') as baseFile:
    lines = baseFile.readlines()
    width = len(lines[0])-1
    height = len(lines)

model_params = {"N":4} # 4 Cars, 1 per corner

print(width, height)
grid = CanvasGrid(agent_portrayal, width, height, 500, 500)

server = ModularServer(CityModel, [grid], "Traffic Base", model_params)

server.port = 8521 # The default
server.launch()