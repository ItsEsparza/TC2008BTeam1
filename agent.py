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
        Determines if the agent can move in the direction that was chosen.
        Enforces valid traffic flow based on direction and position relative to the car.
        """
        # Store all cells around the agent's current position
        around = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        
        x, y = self.pos  # Current position of the agent
        
        # Define potential moves based on the car's current direction
        if self.direction == "Left":
            potential_moves = [
                (x - 1, y),
                (x - 1, y + 1),
                (x - 1, y - 1),
            ]
            valid_directions = [
                ["Left", "Up", "Down"],
                ["Left", "Up"],
                ["Left", "Down"],
            ]
        elif self.direction == "Right":
            potential_moves = [
                (x + 1, y),
                (x + 1, y + 1),
                (x + 1, y - 1),
            ]
            valid_directions = [
                ["Right", "Up", "Down"],
                ["Left", "Up"],
                ["Right", "Down"],
            ]
        elif self.direction == "Up":
            potential_moves = [
                (x, y + 1),
                (x + 1, y + 1),
                (x - 1, y + 1),
            ]
            valid_directions = [
                ["Up", "Left", "Right"],
                ["Up", "Right"],
                ["Up", "Left"],
            ]
        elif self.direction == "Down":
            potential_moves = [
                (x, y - 1),
                (x + 1, y - 1),
                (x - 1, y - 1),
            ]
            valid_directions = [
                ["Down", "Left", "Right"],
                ["Down", "Right"],
                ["Down", "Left"],
            ]
        
        # Filter valid moves (Green light, Road or Destination) and enforce direction rules
        valid_moves = []
        for idx, move in enumerate(potential_moves):
            if move in around:  # Check if the move is within bounds
                # Get all agents in the cell
                cell_agents = self.model.grid.get_cell_list_contents(move)
                
                # Ensure no other Car is already in the cell
                if any(isinstance(agent, Car) for agent in cell_agents):
                    continue  # Skip this move if a Car is present
                
                # Check if the cell contains valid agents and the direction aligns
                for agent in cell_agents:
                    if isinstance(agent, Road) and agent.direction in valid_directions[idx]:
                        valid_moves.append(move)
                        break  # Stop checking this cell if a valid move is found
                    elif isinstance(agent, Destination):  # Allow any direction to a Destination
                        valid_moves.append(move)
                        break
                    elif isinstance(agent, Traffic_Light) and agent.state is True:
                        valid_moves.append(move)
                        break
        
        # Move to a valid random cell
        if valid_moves:
            new_position = random.choice(valid_moves)  # Choose a random position from valid moves
            
            # Move the agent to the new position
            self.model.grid.move_agent(self, new_position)
            
            # Get the agents in the new position
            cell_agents = self.model.grid.get_cell_list_contents(new_position)
            
            # Update direction based on the Road agent in the new position
            for agent in cell_agents:
                if isinstance(agent, Road):  # Check if it's a Road agent
                    self.direction = agent.direction  # Copy the direction from the Road agent
                    break  # Update direction only once
                elif isinstance(agent, Destination):  # Check if it's a Destination agent
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
