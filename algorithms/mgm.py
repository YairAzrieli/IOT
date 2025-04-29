"""
Maximum Gain Message (MGM) implementation.

MGM is a local search algorithm for solving DCOPs (Distributed Constraint 
Optimization Problems). It guarantees that the solution quality will 
monotonically increase with each iteration.
"""

from typing import List, Dict, Any, Tuple, Callable, Set
import random
from core.agent import Agent
from core.message import Message


class MGMAgent(Agent):
    """
    Agent implementing the MGM algorithm.
    
    Attributes:
        id (str): Unique identifier for the agent.
        domain (List[Any]): Possible values this agent can take.
        neighbors (List[str]): IDs of neighboring agents.
        utility_function (Callable): Function to calculate utility of a value.
    """
    
    def __init__(self, id: str, domain: List[Any], neighbors: List[str]):
        """
        Initialize an MGM agent.
        
        Args:
            id (str): Unique identifier for the agent.
            domain (List[Any]): Possible values this agent can take.
            neighbors (List[str]): IDs of neighboring agents.
        """
        super().__init__(id)
        
        # Initialize state
        self.state = {
            "domain": domain,
            "neighbors": neighbors,
            "value": random.choice(domain),  # Start with random value
            "neighbor_values": {},  # Map of neighbor_id -> value
            "constraints": {},  # Map of (agent_id, value, neighbor_id, value) -> cost
            "current_iteration": 0,
            "phase": "value",  # "value" or "gain"
            "neighbor_gains": {},  # Map of neighbor_id -> gain
            "current_gain": 0.0,  # This agent's maximum gain
            "best_value": None  # Best value found in current iteration
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
    
    def find_best_value(self) -> Tuple[Any, float, float]:
        """
        Find the value with the highest utility and calculate gain.
        
        Returns:
            Tuple[Any, float, float]: (best_value, best_utility, gain)
        """
        current_value = self.state["value"]
        current_utility = self.calculate_utility(current_value)
        
        best_value = current_value
        best_utility = current_utility
        
        for value in self.state["domain"]:
            if value == current_value:
                continue  # Skip current value
                
            utility = self.calculate_utility(value)
            if utility > best_utility:
                best_value = value
                best_utility = utility
        
        gain = best_utility - current_utility
        return best_value, best_utility, gain
    
    def compute(self) -> List[Message]:
        """
        Run one iteration of the MGM algorithm.
        
        Returns:
            List[Message]: Messages for neighbors.
        """
        messages = []
        
        # Process incoming messages
        for msg in self.mailbox:
            content = msg.content
            
            if "type" in content:
                if content["type"] == "value_message":
                    self.state["neighbor_values"][msg.sender_id] = content["value"]
                
                elif content["type"] == "gain_message":
                    self.state["neighbor_gains"][msg.sender_id] = content["gain"]
        
        # MGM uses alternating phases: value and gain
        if self.state["phase"] == "value":
            # Value Phase: send current value and calculate maximum gain
            best_value, best_utility, gain = self.find_best_value()
            self.state["best_value"] = best_value
            self.state["current_gain"] = gain
            
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
            
            # Send gain message to all neighbors
            for neighbor_id in self.state["neighbors"]:
                messages.append(Message(
                    sender_id=self.id,
                    receiver_id=neighbor_id,
                    content={
                        "type": "gain_message",
                        "gain": gain,
                        "iteration": self.state["current_iteration"]
                    }
                ))
            
            # Switch to gain phase
            self.state["phase"] = "gain"
        
        else:  # phase == "gain"
            # Gain Phase: decide whether to change value based on neighbor gains
            should_change = True
            
            # Only change if our gain is positive
            if self.state["current_gain"] <= 0:
                should_change = False
            
            # Only change if our gain is greater than all neighbors' gains
            for neighbor_id, neighbor_gain in self.state["neighbor_gains"].items():
                if neighbor_gain > self.state["current_gain"]:
                    should_change = False
                    break
            
            # Change value if we should
            if should_change:
                self.state["value"] = self.state["best_value"]
            
            # Clear neighbor gains for next iteration
            self.state["neighbor_gains"] = {}
            
            # Increment iteration counter
            self.state["current_iteration"] += 1
            
            # Switch back to value phase
            self.state["phase"] = "value"
        
        return messages
    
    def update_state(self) -> None:
        """No additional state updates needed after compute."""
        pass