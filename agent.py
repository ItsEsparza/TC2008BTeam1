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
        self.path_Found = False
        self.moveIndex = 0
        self.path = []
        
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
        
        # Get the neighborhood of the current position (around the current cell)
        around = self.model.grid.get_neighborhood(position, moore=True, include_center=False)
        x, y = position

        # Define potential moves based on the current direction
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

        # Iterate over each potential move and check conditions
        for idx, move in enumerate(potential_moves):
            # Ensure the move is within the grid bounds
            if not self.model.grid.out_of_bounds(move):
                # Get all agents in the cell where the move is going
                cell_agents = self.model.grid.get_cell_list_contents(move)
                
                # Check if the move is within bounds and no obstacles are in the way
                if move in around and not any(isinstance(agent, Obstacle) for agent in cell_agents):
                    # Now check for valid moves based on agents in the destination cell
                    for agent in cell_agents:
                        if isinstance(agent, Road) and agent.direction in valid_directions[idx]:
                            valid_moves.append(move)
                            break
                        elif isinstance(agent, Destination) and agent.pos == self.objective.pos:
                            # Allow any direction to a Destination
                            valid_moves.append(move)
                            break
                        elif isinstance(agent, Traffic_Light) and idx == 0:
                            # Allow movement if the Traffic_Light is green and directly in front of the car
                            valid_moves.append(move)
                            break

        return valid_moves
    
    def A_star(self):
        """
        A* algorithm to find the shortest path to the destination.
        """
        start = self.pos
        end = self.objective.pos
        starting_direction = self.direction
        open_list = [start]
        closed_list = []
        g_cost = {start: 0}
        f_cost = {start: self.calculate_distances(start, end)}
        came_from = {}

        while open_list:
            # Get the node with the lowest f_cost
            current_node = min(open_list, key=lambda node: f_cost[node])
            # If we reached the destination, reconstruct the path
            if current_node == end:
                path = []
                while current_node in came_from:
                    path.append(current_node)
                    current_node = came_from[current_node]
                path.reverse()  # Reverse path to start from the origin
                #Reset direction to starting
                self.direction = starting_direction
                return path

            open_list.remove(current_node)
            closed_list.append(current_node)

            # Update the car's direction based on the type of agent it's standing on
            current_cell_agents = self.model.grid.get_cell_list_contents(current_node)
            for agent in current_cell_agents:
                if isinstance(agent, Road):
                    self.direction = agent.direction  # Update direction to match the road's direction
                    break  # Stop once we update the direction from a road

            # Explore neighbors (possible moves) with the updated direction
            for neighbor in self.possible_moves_f(current_node, self.direction):
                if neighbor in closed_list:
                    continue

                tentative_g_cost = g_cost[current_node] + self.calculate_distances(current_node, neighbor)

                if neighbor not in open_list:
                    open_list.append(neighbor)
                elif tentative_g_cost >= g_cost.get(neighbor, float('inf')):
                    continue

                # This path is the best one to this neighbor so far
                came_from[neighbor] = current_node
                g_cost[neighbor] = tentative_g_cost
                f_cost[neighbor] = g_cost[neighbor] + self.calculate_distances(neighbor, end)
        return []  # Return an empty list if no path is found
        
    def move(self):
        """
        Determines if the agent can move in the direction that was chosen.
        Enforces valid traffic flow based on direction and position relative to the car.
        """
        if self.path_Found == False:
            self.path = self.A_star()  # Get the path from A*
            self.path_Found = True
        
        move = self.path[self.moveIndex]  # Get the current target position from the path
        cell_agents = self.model.grid.get_cell_list_contents(move)  # Get the agents in the target cell

        # Check if the car is currently on a Traffic_Light
        current_cell_agents = self.model.grid.get_cell_list_contents(self.pos)
        is_on_traffic_light = any(isinstance(agent, Traffic_Light) for agent in current_cell_agents)

        # Ensure no other Car is already in the target cell
        if any(isinstance(agent, Car) for agent in cell_agents):
            return  # Don't move if another car is in the target cell

        # Handle traffic light rules (if on a traffic light)
        if is_on_traffic_light:
            traffic_light = next((agent for agent in current_cell_agents if isinstance(agent, Traffic_Light)), None)
            if traffic_light and not traffic_light.state:  # If the light is red
                return  # Don't move
            
        self.model.grid.move_agent(self, self.path[self.moveIndex])
        self.moveIndex += 1  # Increment the move index
        
        for agent in cell_agents:
            if isinstance(agent, Road):  # Check if it's a Road agent
                self.direction = agent.direction  # Copy the direction from the Road agent
                break  # Update direction only once
            
            elif isinstance(agent, Destination):  # Check if it's a Destination agent
                self.model.cars_reached_destination += 1  # Increment the counter
                self.model.grid.remove_agent(self)  # Remove the car from the grid
                self.model.schedule.remove(self)  # Remove the car from the schedule
                break  # If destination is reached, end the movement
                    
                


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
