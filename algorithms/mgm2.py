"""
Maximum Gain Message 2 (MGM-2) implementation.

MGM-2 is an extension of MGM that allows coordinated value changes
between pairs of neighboring agents, enabling greater gains per cycle.
"""

from typing import List, Dict, Any, Tuple, Callable, Set
import random
from core.agent import Agent
from core.message import Message


class MGM2Agent(Agent):
    """
    Agent implementing the MGM-2 algorithm.
    
    Attributes:
        id (str): Unique identifier for the agent.
        domain (List[Any]): Possible values this agent can take.
        neighbors (List[str]): IDs of neighboring agents.
        p (float): Probability of being an offerer vs. receiver.
    """
    
    def __init__(self, id: str, domain: List[Any], neighbors: List[str], p: float = 0.5):
        """
        Initialize an MGM-2 agent.
        
        Args:
            id (str): Unique identifier for the agent.
            domain (List[Any]): Possible values this agent can take.
            neighbors (List[str]): IDs of neighboring agents.
            p (float): Probability of being an offerer vs. receiver.
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
            "p": p,  # Probability of being an offerer
            "phase": "value",  # "value", "offer", "accept", or "evaluate"
            "role": None,  # "offerer" or "receiver"
            "received_offers": {},  # Map of neighbor_id -> (offerer_value, receiver_value, gain)
            "sent_offer": None,  # Tuple of (neighbor_id, offerer_value, receiver_value, gain)
            "accepted_offer": None,  # Tuple of (neighbor_id, offerer_value, receiver_value, gain)
            "unilateral_gain": 0.0,  # Gain from changing value alone
            "unilateral_best_value": None,  # Best value for unilateral change
            "neighbor_unilateral_gains": {}  # Map of neighbor_id -> gain
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
    
    def calculate_pair_utility(self, value: Any, neighbor_id: str, 
                               neighbor_value: Any) -> float:
        """
        Calculate utility if we change to 'value' and neighbor changes to 'neighbor_value'.
        
        Args:
            value (Any): Our new value.
            neighbor_id (str): ID of the neighbor.
            neighbor_value (Any): Neighbor's new value.
            
        Returns:
            float: The utility for this agent only.
        """
        total_cost = 0.0
        
        # Create a temporary set of neighbor values with the changed value
        temp_neighbor_values = dict(self.state["neighbor_values"])
        temp_neighbor_values[neighbor_id] = neighbor_value
        
        # Sum costs for all neighbors
        for n_id, n_value in temp_neighbor_values.items():
            key = (self.id, value, n_id, n_value)
            if key in self.state["constraints"]:
                total_cost += self.state["constraints"][key]
        
        return -total_cost  # Return negative cost as utility
    
    def find_best_unilateral_change(self) -> Tuple[Any, float, float]:
        """
        Find the best value to change to by ourselves.
        
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
    
    def find_best_bilateral_change(self, neighbor_id: str) -> Tuple[Any, Any, float]:
        """
        Find the best value pair change with a neighbor.
        
        Args:
            neighbor_id (str): ID of the neighbor to consider.
            
        Returns:
            Tuple[Any, Any, float]: (our_value, neighbor_value, gain)
        """
        current_value = self.state["value"]
        neighbor_current_value = self.state["neighbor_values"].get(neighbor_id)
        
        if neighbor_current_value is None:
            return current_value, None, 0.0
        
        current_utility = self.calculate_utility(current_value)
        best_our_value = current_value
        best_neighbor_value = neighbor_current_value
        best_gain = 0.0
        
        # Try all value pairs
        for our_value in self.state["domain"]:
            if our_value == current_value:
                continue  # Must be a different value
                
            for neighbor_value in self.state["domain"]:
                if neighbor_value == neighbor_current_value:
                    continue  # Must be a different value
                
                # Calculate the gain for both agents
                our_new_utility = self.calculate_pair_utility(
                    our_value, neighbor_id, neighbor_value)
                
                our_gain = our_new_utility - current_utility
                
                # For this simplified version, we don't have the neighbor's utility function
                # In a real implementation, you'd need to exchange more information
                # For now, we'll use a heuristic based on our own utility
                
                if our_gain > best_gain:
                    best_our_value = our_value
                    best_neighbor_value = neighbor_value
                    best_gain = our_gain
        
        return best_our_value, best_neighbor_value, best_gain
    
    def compute(self) -> List[Message]:
        """
        Run one iteration of the MGM-2 algorithm.
        
        Returns:
            List[Message]: Messages for neighbors.
        """
        messages = []
        
        # Process incoming messages based on phase
        for msg in self.mailbox:
            content = msg.content
            
            if "type" in content:
                if content["type"] == "value_message":
                    self.state["neighbor_values"][msg.sender_id] = content["value"]
                
                elif content["type"] == "unilateral_gain_message":
                    self.state["neighbor_unilateral_gains"][msg.sender_id] = content["gain"]
                
                elif content["type"] == "offer_message" and self.state["role"] == "receiver":
                    # Store received offers
                    self.state["received_offers"][msg.sender_id] = (
                        content["offerer_value"],
                        content["receiver_value"],
                        content["gain"]
                    )
                
                elif content["type"] == "accept_message" and self.state["role"] == "offerer":
                    # Record accepted offer
                    if content["accepted"] and self.state["sent_offer"] and \
                       self.state["sent_offer"][0] == msg.sender_id:
                        self.state["accepted_offer"] = self.state["sent_offer"]
        
        # Handle current phase
        if self.state["phase"] == "value":
            # Value Phase: exchange values and calculate unilateral gains
            
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
            
            # Calculate unilateral gain
            best_value, best_utility, gain = self.find_best_unilateral_change()
            self.state["unilateral_best_value"] = best_value
            self.state["unilateral_gain"] = gain
            
            # Send unilateral gain to all neighbors
            for neighbor_id in self.state["neighbors"]:
                messages.append(Message(
                    sender_id=self.id,
                    receiver_id=neighbor_id,
                    content={
                        "type": "unilateral_gain_message",
                        "gain": gain,
                        "iteration": self.state["current_iteration"]
                    }
                ))
            
            # Decide whether to be offerer or receiver
            if random.random() < self.state["p"]:
                self.state["role"] = "offerer"
            else:
                self.state["role"] = "receiver"
            
            # Switch to offer phase
            self.state["phase"] = "offer"
            
        elif self.state["phase"] == "offer":
            # Offer Phase: offerers send offers, receivers wait
            
            if self.state["role"] == "offerer":
                # Find the neighbor with highest potential gain
                best_neighbor_id = None
                best_our_value = None
                best_neighbor_value = None
                best_gain = 0.0
                
                for neighbor_id in self.state["neighbors"]:
                    our_value, neighbor_value, gain = self.find_best_bilateral_change(neighbor_id)
                    if gain > best_gain:
                        best_neighbor_id = neighbor_id
                        best_our_value = our_value
                        best_neighbor_value = neighbor_value
                        best_gain = gain
                
                # Send offer to best neighbor if gain is positive
                if best_gain > 0 and best_neighbor_id is not None:
                    messages.append(Message(
                        sender_id=self.id,
                        receiver_id=best_neighbor_id,
                        content={
                            "type": "offer_message",
                            "offerer_value": best_our_value,
                            "receiver_value": best_neighbor_value,
                            "gain": best_gain,
                            "iteration": self.state["current_iteration"]
                        }
                    ))
                    
                    # Store the sent offer
                    self.state["sent_offer"] = (
                        best_neighbor_id, best_our_value, best_neighbor_value, best_gain
                    )
            
            # Switch to accept phase
            self.state["phase"] = "accept"
            
        elif self.state["phase"] == "accept":
            # Accept Phase: receivers decide which offers to accept
            
            if self.state["role"] == "receiver" and self.state["received_offers"]:
                # Find the best received offer
                best_offerer_id = None
                best_total_gain = 0.0
                
                for offerer_id, (offerer_value, receiver_value, offerer_gain) in \
                    self.state["received_offers"].items():
                    
                    # Calculate our gain from this offer
                    current_utility = self.calculate_utility(self.state["value"])
                    new_utility = self.calculate_pair_utility(
                        receiver_value, offerer_id, offerer_value)
                    our_gain = new_utility - current_utility
                    
                    # Total gain is the sum of our gain and the offerer's gain
                    total_gain = our_gain + offerer_gain
                    
                    if total_gain > best_total_gain:
                        best_offerer_id = offerer_id
                        best_total_gain = total_gain
                
                # Accept the best offer if it's better than our unilateral change
                should_accept = False
                if best_total_gain > self.state["unilateral_gain"] and best_offerer_id is not None:
                    should_accept = True
                    self.state["accepted_offer"] = (
                        best_offerer_id,
                        self.state["received_offers"][best_offerer_id][1],  # receiver_value
                        self.state["received_offers"][best_offerer_id][0],  # offerer_value
                        best_total_gain
                    )
                
                # Send acceptance or rejection to all offerers
                for offerer_id in self.state["received_offers"]:
                    messages.append(Message(
                        sender_id=self.id,
                        receiver_id=offerer_id,
                        content={
                            "type": "accept_message",
                            "accepted": should_accept and offerer_id == best_offerer_id,
                            "iteration": self.state["current_iteration"]
                        }
                    ))
            
            # Switch to evaluate phase
            self.state["phase"] = "evaluate"
            
        elif self.state["phase"] == "evaluate":
            # Evaluate Phase: decide whether to make unilateral or bilateral change
            
            # Determine if we should make a bilateral change
            bilateral_change = False
            if self.state["accepted_offer"]:
                neighbor_id, our_value, _, _ = self.state["accepted_offer"]
                # Set our new value
                self.state["value"] = our_value
                bilateral_change = True
            
            # If no bilateral change and we're not involved in anyone else's bilateral change,
            # consider unilateral change
            if not bilateral_change:
                # Check if our unilateral gain is better than all neighbors
                has_better_neighbor = False
                for neighbor_id, neighbor_gain in self.state["neighbor_unilateral_gains"].items():
                    if neighbor_gain > self.state["unilateral_gain"]:
                        has_better_neighbor = True
                        break
                
                # Change value if we have the best gain
                if self.state["unilateral_gain"] > 0 and not has_better_neighbor:
                    self.state["value"] = self.state["unilateral_best_value"]
            
            # Clean up for next iteration
            self.state["received_offers"] = {}
            self.state["sent_offer"] = None
            self.state["accepted_offer"] = None
            self.state["neighbor_unilateral_gains"] = {}
            self.state["role"] = None
            
            # Increment iteration counter
            self.state["current_iteration"] += 1
            
            # Switch back to value phase
            self.state["phase"] = "value"
        
        return messages
    
    def update_state(self) -> None:
        """No additional state updates needed after compute."""
        pass