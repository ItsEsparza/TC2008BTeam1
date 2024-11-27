from mesa import Agent
import random

class Car(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID 
        direction: Randomly chosen direction chosen from one of eight directions
    """
    def __init__(self, unique_id, model, direction = "Left"):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
        self.direction = direction

    def move(self):
        """ 
        Determines if the agent can move in the direction that was chosen
        """        
        # Store all cells around
        around = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        
        x, y = self.pos  # Current position of the agent
        
        #Possible movements
        if self.direction == "Left":
            potential_moves = [(x - 1, y), (x - 1, y + 1), (x - 1, y - 1)]
        elif self.direction == "Right":
            potential_moves = [(x + 1, y), (x + 1, y + 1), (x + 1, y - 1)]
        elif self.direction == "Up":
            potential_moves = [(x, y + 1), (x + 1, y + 1), (x - 1, y + 1)]
        elif self.direction == "Down":
            potential_moves = [(x, y - 1), (x + 1, y - 1), (x - 1, y - 1)]
            
        # Filter valid moves (Green light, Road or Destination)
        valid_moves = []
        for move in potential_moves:
            if move in around:  # Check if the move is within bounds
                # Get all agents in the cell
                cell_agents = self.model.grid.get_cell_list_contents(move)
                
                # Check if the cell contains valid agents
                for agent in cell_agents:
                    if isinstance(agent, (Road, Destination)) or (isinstance(agent, Traffic_Light) and agent.state is True):
                        valid_moves.append(move)
                        break  # No need to check further if one valid agent is found
        
        # Update possible_moves with valid moves
        possible_moves = valid_moves
        
        # Move to a valid random cell (TODO: Implement A* algorithm)
        # If there are valid moves, choose one randomly and move
        if possible_moves:
            new_position = random.choice(possible_moves)  # Choose a random position from valid moves
            
            # Move the agent to the new position
            self.model.grid.move_agent(self, new_position)
            
            # Get the agents in the new position
            cell_agents = self.model.grid.get_cell_list_contents(new_position)
            
            # Update direction based on the Road agent in the new position
            for agent in cell_agents:
                if isinstance(agent, Road):  # Check if it's a Road agent
                    self.direction = agent.direction  # Copy the direction from the Road agent
                    break  # Update direction only once
                elif isinstance(agent, Destination):  # Check if it's a Destination agent, if so remove from the grid
                    self.model.grid.remove_agent(self)
                    self.model.schedule.remove(self)
                    break
        

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        self.move()

class Traffic_Light(Agent):
    """
    Traffic light. Where the traffic lights are in the grid.
    """
    def __init__(self, unique_id, model, state = False, timeToChange = 10):
        super().__init__(unique_id, model)
        """
        Creates a new Traffic light.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            state: Whether the traffic light is green or red
            timeToChange: After how many step should the traffic light change color 
        """
        self.state = state
        self.timeToChange = timeToChange

    def step(self):
        """ 
        To change the state (green or red) of the traffic light in case you consider the time to change of each traffic light.
        """
        if self.model.schedule.steps % self.timeToChange == 0:
            self.state = not self.state

class Destination(Agent):
    """
    Destination agent. Where each car should go.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Obstacle(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Road(Agent):
    """
    Road agent. Determines where the cars can move, and in which direction.
    """
    def __init__(self, unique_id, model, direction= "Left"):
        """
        Creates a new road.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            direction: Direction where the cars can move
        """
        super().__init__(unique_id, model)
        self.direction = direction

    def step(self):
        pass
