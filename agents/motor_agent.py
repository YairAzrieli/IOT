"""
Motor Agent implementation.

Responsible for handling motor commands and translating them to wheel movements.
"""

from typing import List, Dict, Any, Tuple, Optional
from core.agent import Agent
from core.message import Message
import math


class MotorAgent(Agent):
    """
    Agent responsible for motor control of the wheelchair.
    
    Attributes:
        id (str): Unique identifier for the agent.
        navigation_agent_id (str): ID of the navigation agent.
        speed (float): Current speed in units/second.
        direction (float): Current direction in radians.
        position (Tuple[float, float]): Current position (x, y).
    """
    
    def __init__(self, id: str, navigation_agent_id: str):
        """
        Initialize a motor agent.
        
        Args:
            id (str): Unique identifier for the agent.
            navigation_agent_id (str): ID of the navigation agent.
        """
        super().__init__(id)
        self.navigation_agent_id = navigation_agent_id
        
        # Initialize state
        self.state = {
            "speed": 0.0,  # Units/second
            "direction": 0.0,  # Radians (0 = +x axis)
            "position": (0.0, 0.0),  # (x, y) coordinates
            "target_position": None,  # Target position for move_to commands
            "max_speed": 5.0,  # Maximum speed
            "acceleration": 1.0,  # Acceleration rate
            "turning_rate": 0.5  # Radians/second turning rate
        }
    
    def execute_motor_command(self, command: str, params: Dict[str, Any]) -> None:
        """
        Execute a motor command.
        
        Args:
            command (str): Command type (e.g., "move", "stop", "turn").
            params (Dict[str, Any]): Command parameters.
        """
        # This would eventually control actual motors
        # For now, just update our simulated state
        
        if command == "set_speed":
            if "speed" in params:
                # Clamp speed to maximum
                requested_speed = params["speed"]
                self.state["speed"] = min(requested_speed, self.state["max_speed"])
        
        elif command == "set_direction":
            if "direction" in params:
                self.state["direction"] = params["direction"]
        
        elif command == "stop":
            self.state["speed"] = 0.0
        
        elif command == "move_to":
            if "target" in params:
                self.state["target_position"] = params["target"]
    
    def compute(self) -> List[Message]:
        """
        Process incoming messages and control motors.
        
        Returns:
            List[Message]: Status updates for other agents.
        """
        messages = []
        
        # Process incoming messages
        for msg in self.mailbox:
            content = msg.content
            
            if "type" in content and content["type"] == "motor_command":
                self.execute_motor_command(
                    content["command"],
                    {k: v for k, v in content.items() if k != "type" and k != "command"}
                )
        
        # Send position update to navigation agent
        messages.append(Message(
            sender_id=self.id,
            receiver_id=self.navigation_agent_id,
            content={
                "type": "position_update",
                "position": self.state["position"]
            }
        ))
        
        return messages
    
    def update_state(self) -> None:
        """
        Update position based on current speed and direction.
        
        This simulates the movement of the wheelchair over one time step.
        """
        # If we have a target position, adjust direction and speed to reach it
        if self.state["target_position"]:
            target_x, target_y = self.state["target_position"]
            curr_x, curr_y = self.state["position"]
            
            # Calculate vector to target
            dx = target_x - curr_x
            dy = target_y - curr_y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # If we're close enough, stop and clear target
            if distance < 0.1:  # Small threshold to prevent oscillation
                self.state["speed"] = 0.0
                self.state["target_position"] = None
                return
            
            # Calculate target direction
            target_direction = math.atan2(dy, dx)
            
            # Adjust direction toward target
            current_direction = self.state["direction"]
            angle_diff = target_direction - current_direction
            
            # Normalize angle difference to [-pi, pi]
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            # Apply turning at the turning rate
            max_turn = self.state["turning_rate"]
            if abs(angle_diff) > max_turn:
                if angle_diff > 0:
                    self.state["direction"] += max_turn
                else:
                    self.state["direction"] -= max_turn
            else:
                self.state["direction"] = target_direction
            
            # Adjust speed based on distance and angle
            # Slow down if we're not pointing at the target or getting close
            direction_factor = abs(math.cos(angle_diff))
            distance_factor = min(1.0, distance / 2.0)
            target_speed = self.state["max_speed"] * direction_factor * distance_factor
            
            # Apply acceleration/deceleration
            speed_diff = target_speed - self.state["speed"]
            max_speed_change = self.state["acceleration"]
            
            if abs(speed_diff) > max_speed_change:
                if speed_diff > 0:
                    self.state["speed"] += max_speed_change
                else:
                    self.state["speed"] -= max_speed_change
            else:
                self.state["speed"] = target_speed
        
        # Update position based on speed and direction
        speed = self.state["speed"]
        direction = self.state["direction"]
        
        # Calculate movement vector
        dx = speed * math.cos(direction)
        dy = speed * math.sin(direction)
        
        # Update position
        curr_x, curr_y = self.state["position"]
        self.state["position"] = (curr_x + dx, curr_y + dy)