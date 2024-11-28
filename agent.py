from mesa import Agent
import random, math

class Car(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID 
        direction: Randomly chosen direction chosen from one of eight directions
    """
    def __init__(self, unique_id, model, direction = "Left", objective = None):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
        self.direction = direction
        self.objective = objective
        
    def calculate_distances(self, pos_1, pos_2):
        x1, y1 = pos_1
        x2, y2 = pos_2
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        
    def possible_moves_f(self, position, direction):
        """
        Returns a list of possible moves based on the current direction, grid bounds and buildings.
        """
        possible_moves = []
        valid_directions = []
        valid_moves = []
        # Get all agents in the cell
        cell_agents = self.model.grid.get_cell_list_contents(move)
        
        around = self.model.grid.get_neighborhood(position, moore=True, include_center=False) # Used to check if the move is within bounds
        x, y = position

        if direction == "Left":
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
        elif direction == "Right":
            potential_moves = [
                (x + 1, y),
                (x + 1, y + 1),
                (x + 1, y - 1),
            ]
            valid_directions = [
                ["Right", "Up", "Down"],
                ["Right", "Up"],
                ["Right", "Down"],
            ]
        elif direction == "Up":
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
        elif direction == "Down":
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

        # Add moves within bounds and without obstacles to possible moves
        for move in potential_moves:
            if move in around and any(isinstance(agent, Obstacle) for agent in self.model.grid.get_cell_list_contents(move)) == False:
                possible_moves.append(move)
    
        for idx, move in enumerate(potential_moves):
            for agent in cell_agents:
                    if isinstance(agent, Road) and agent.direction in valid_directions[idx]:
                        valid_moves.append(move)
                        break
                    elif isinstance(agent, Destination) and agent.pos == self.objective.pos:  # Allow any direction to a Destination
                        valid_moves.append(move)
                        break
                    elif isinstance(agent, Traffic_Light) and idx == 0:  # Allow movement if the Traffic_Light is green and is directly in front of the car
                        valid_moves.append(move)
                        break
        
        return possible_moves, valid_directions
    
    def A_star(self):
        """
        A* algorithm to find the shortest path to the destination.
        """
        start = self.pos
        end = self.objective.pos
        open_list = [start]
        closed_list = []
        g_cost = {start: 0}
        
        while open_list:
            current = open_list[0]
            open_list = open_list[1:]
            closed_list.append(current)
            
            if current == end:
                return True
            
            possible_moves, _ = self.possible_moves_f(position=current, direction=self.direction)
            for move in possible_moves:
                if move in closed_list:
                    continue
                
                if move not in open_list:
                    open_list.append(move)
                
                new_g_cost = g_cost[current] + self.calculate_distances(current, move)
                if move not in g_cost or new_g_cost < g_cost[move]:
                    g_cost[move] = new_g_cost
        
        
        
    def move(self):
        """ 
        Determines if the agent can move in the direction that was chosen.
        Enforces valid traffic flow based on direction and position relative to the car.
        """
        
        # Check if the car is currently on a Traffic_Light
        current_cell_agents = self.model.grid.get_cell_list_contents(self.pos)
        is_on_traffic_light = any(isinstance(agent, Traffic_Light) for agent in current_cell_agents)
        
        # Filter valid moves (Green light, Road or Destination) and enforce direction rules
        valid_moves = []
        potential_moves, valid_directions = self.possible_moves_f(position=self.pos, direction=self.direction)
        
            # Ensure no other Car is already in the cell
            if any(isinstance(agent, Car) for agent in cell_agents):
                continue  # Skip this move if a Car is present
            
            # Prevent front movement to another Traffic_Light if currently on a Traffic_Light
            if idx == 0 and is_on_traffic_light and any(isinstance(agent, Traffic_Light) for agent in cell_agents):
                continue  # Skip front move if it leads to a Traffic_Light
            
        
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
        self.A_star()
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
