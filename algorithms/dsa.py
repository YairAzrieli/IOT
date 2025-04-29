"""
Distributed Stochastic Algorithm (DSA) implementation.

DSA is a local search algorithm for solving DCOPs (Distributed Constraint 
Optimization Problems). This implements the DSA-C variant where agents change 
their values with probability p only if it improves their local utility.
"""

from typing import List, Dict, Any, Tuple, Callable, Set
import random
from core.agent import Agent
from core.message import Message


class DSAAgent(Agent):
    """
    Agent implementing the DSA-C algorithm.
    
    Attributes:
        id (str): Unique identifier for the agent.
        domain (List[Any]): Possible values this agent can take.
        neighbors (List[str]): IDs of neighboring agents.
        probability (float): Probability of changing value when improvement is found.
        utility_function (Callable): Function to calculate utility of a value.
    """
    
    def __init__(self, id: str, domain: List[Any], neighbors: List[str], 
                 probability: float = 0.7):
        """
        Initialize a DSA agent.
        
        Args:
            id (str): Unique identifier for the agent.
            domain (List[Any]): Possible values this agent can take.
            neighbors (List[str]): IDs of neighboring agents.
            probability (float): Probability of changing value when improvement is found.
        """
        super().__init__(id)
        
        # Initialize state
        self.state = {
            "domain": domain,
            "neighbors": neighbors,
            "value": random.choice(domain),  # Start with random value
            "neighbor_values": {},  # Map of neighbor_id -> value
            "constraints": {},  # Map of (agent_id, value, neighbor_id, value) -> cost
            "probability": probability,
            "current_iteration": 0
        }
    
    def add_constraint(self, neighbor_id: str, costs: Dict[Tuple[Any, Any], float]) -> None:
        """
        Add constraint costs between this agent and a neighbor.
        
        Args:
            neighbor_id (str): ID of the neighboring agent.
            costs (Dict[Tuple[Any, Any], float]): Map of (value, neighbor_value) -> cost.
        """
        if neighbor_id not in self.state["neighbors"]:
            self.state["neighbors"].append(neighbor_id)
        
        # Convert costs to internal representation
        for (value, neighbor_value), cost in costs.items():
            self.state["constraints"][(self.id, value, neighbor_id, neighbor_value)] = cost
    
    def calculate_utility(self, value: Any) -> float:
        """
        Calculate the negative utility (cost) of a value.
        
        Args:
            value (Any): The value to evaluate.
            
        Returns:
            float: The negative utility (higher is worse).
        """
        total_cost = 0.0
        
        # Sum costs for all known neighbor values
        for neighbor_id, neighbor_value in self.state["neighbor_values"].items():
            key = (self.id, value, neighbor_id, neighbor_value)
            if key in self.state["constraints"]:
                total_cost += self.state["constraints"][key]
        
        return -total_cost  # Return negative cost as utility
    
    def find_best_value(self) -> Tuple[Any, float]:
        """
        Find the value with the highest utility.
        
        Returns:
            Tuple[Any, float]: (best_value, utility)
        """
        best_value = self.state["value"]
        best_utility = self.calculate_utility(best_value)
        
        for value in self.state["domain"]:
            utility = self.calculate_utility(value)
            if utility > best_utility:
                best_value = value
                best_utility = utility
        
        return best_value, best_utility
    
    def compute(self) -> List[Message]:
        """
        Run one iteration of the DSA algorithm.
        
        Returns:
            List[Message]: Value messages for neighbors.
        """
        messages = []
        
        # Update neighbor values from incoming messages
        for msg in self.mailbox:
            content = msg.content
            if "type" in content and content["type"] == "value_message":
                self.state["neighbor_values"][msg.sender_id] = content["value"]
        
        # Increment iteration counter
        self.state["current_iteration"] += 1
        
        # Find the best value
        best_value, best_utility = self.find_best_value()
        current_utility = self.calculate_utility(self.state["value"])
        
        # Check if we should change our value
        should_change = False
        if best_utility > current_utility:
            # Only change with probability p
            if random.random() < self.state["probability"]:
                should_change = True
        
        # Update value if needed
        if should_change:
            self.state["value"] = best_value
        
        # Send value message to all neighbors
        for neighbor_id in self.state["neighbors"]:
            messages.append(Message(
                sender_id=self.id,
                receiver_id=neighbor_id,
                content={
                    "type": "value_message",
                    "value": self.state["value"],
                    "iteration": self.state["current_iteration"]
                }
            ))
        
        return messages
    
    def update_state(self) -> None:
        """No additional state updates needed after compute."""
        pass