from agent import *
from model import CityModel
from mesa.visualization import CanvasGrid, TextElement
from mesa.visualization import ModularServer

# Function to define the agent portrayal
def agent_portrayal(agent):
    if agent is None: return
    portrayal = {"Shape": "rect", "Filled": "true", "Layer": 1, "w": 1, "h": 1}

    if isinstance(agent, Road):
        portrayal["Color"] = "gray"
        portrayal["Layer"] = 0

    if isinstance(agent, Destination):
        portrayal["Color"] = "lightgreen"
        portrayal["Layer"] = 0

    if isinstance(agent, Traffic_Light):
        portrayal["Color"] = "red" if not agent.state else "green"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    if isinstance(agent, Obstacle):
        portrayal["Color"] = "cadetblue"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1
        
    if isinstance(agent, Car):
        portrayal["Color"] = "blue"   
        if agent.direction == "Up":
            portrayal["Shape"] = "Images/up.png"
        elif agent.direction == "Down":
            portrayal["Shape"] = "Images/down.png"
            portrayal["w"] = 1
            portrayal["h"] = 1
        elif agent.direction == "Left":
            portrayal["Shape"] = "Images/left.png"
        elif agent.direction == "Right":
            portrayal["Shape"] = "Images/right.png"

    return portrayal

# Read the map dimensions from the city map file
width = 0
height = 0

with open('city_files/2024_base.txt') as baseFile:
    lines = baseFile.readlines()
    width = len(lines[0]) - 1
    height = len(lines)

# Set model parameters
model_params = {"N": 4}  # 4 Cars, 1 per corner

# Create the CanvasGrid for the model visualization
grid = CanvasGrid(agent_portrayal, width, height, 500, 500)

# Custom TextElement to display the car count as text
class CarCountTextElement(TextElement):
    """A simple text display for the number of cars in the model."""
    def __init__(self, model):
        self.model = model
        super().__init__()

    def render(self, model):
        # Get the car count using the `get_car_count` method from the model
        car_count = model.get_car_count()
        return f"Number of Cars: {car_count}"

class CarsReachedTextElement(TextElement):
    """A simple text display for the number of cars that reached their destination."""
    def __init__(self, model):
        self.model = model
        super().__init__()

    def render(self, model):
        # Get the count of cars that reached their destination
        cars_reached = model.get_cars_reached_destination()
        return f"Cars Reached Destination: {cars_reached}"

# Create an instance of the CarCountTextElement
car_count_text = CarCountTextElement(model=None)  # Initially no model is passed
cars_reached_text = CarsReachedTextElement(model=None)

def update_cars_reached_text(model):
    cars_reached_text.model = model  # Set the model reference

# Create the server with the grid and the car count text
server = ModularServer(
    CityModel,
    [grid, car_count_text, cars_reached_text],  # Add the CarsReachedTextElement here
    "Traffic Base",
    model_params
)

# Update the text element to use the model
def update_car_count_text(model):
    car_count_text.model = model  # Set the model reference

# Set the server port and launch it
server.port = 8521  # Default port
server.launch()

# Update the car count text every time the step is called
server.update_text_element = update_car_count_text
