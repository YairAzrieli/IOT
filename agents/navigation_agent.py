"""
Navigation Agent implementation.

Responsible for path planning and navigation decisions based on sensor inputs.
"""

from typing import List, Dict, Any, Tuple, Optional
from core.agent import Agent
from core.message import Message
import math


class NavigationAgent(Agent):
    """
    Agent responsible for path planning and navigation.
    
    Attributes:
        id (str): Unique identifier for the agent.
        motor_agent_id (str): ID of the motor agent to send commands to.
        map (Dict): Environment map data.
        current_position (Tuple[float, float]): Current position (x, y).
        target_position (Tuple[float, float]): Target position to navigate to.
        obstacle_data (Dict): Latest data about obstacles from sensors.
    """
    
    def __init__(self, id: str, motor_agent_id: str):
        """
        Initialize a navigation agent.
        
        Args:
            id (str): Unique identifier for the agent.
            motor_agent_id (str): ID of the motor agent to command.
        """
        super().__init__(id)
        self.motor_agent_id = motor_agent_id
        
        # Initialize state with default values
        self.state = {
            "map": {},  # Would contain a grid or graph representation
            "current_position": (0.0, 0.0),
            "target_position": (0.0, 0.0),
            "obstacle_data": {},
            "planned_path": [],
            "navigation_mode": "idle"  # Could be "idle", "manual", "autonomous"
        }
    
    def set_target(self, target_position: Tuple[float, float]) -> None:
        """
        Set a new navigation target.
        
        Args:
            target_position (Tuple[float, float]): Target (x, y) coordinates.
        """
        self.state["target_position"] = target_position
        self.plan_path()
    
    def update_position(self, new_position: Tuple[float, float]) -> None:
        """
        Update the current position.
        
        Args:
            new_position (Tuple[float, float]): New (x, y) coordinates.
        """
        self.state["current_position"] = new_position
    
    def plan_path(self) -> List[Tuple[float, float]]:
        """
        Plan a path from current position to target.
        
        This is a placeholder that would be replaced by actual path planning
        algorithms like A* or Dijkstra's.
        
        Returns:
            List[Tuple[float, float]]: Waypoints from current to target position.
        """
        # In a real implementation, this would use a path planning algorithm
        # like A* or Dijkstra's to find a path through the map
        
        # For now, just return a direct line (simplified)
        current = self.state["current_position"]
        target = self.state["target_position"]
        
        # Just create a straight line path for now
        path = [current, target]
        self.state["planned_path"] = path
        return path
    
    def process_sensor_data(self, sensor_type: str, value: float, sensor_id: str) -> None:
        """
        Process incoming sensor data.
        
        Args:
            sensor_type (str): Type of sensor.
            value (float): Sensor reading.
            sensor_id (str): ID of the sensor.
        """
        # Update our obstacle data
        self.state["obstacle_data"][sensor_id] = {
            "type": sensor_type,
            "value": value
        }
        
        # Check if we need to replan based on new data
        if self.state["navigation_mode"] == "autonomous":
            # Check if any obstacles are close
            obstacle_detected = False
            for sensor_data in self.state["obstacle_data"].values():
                if sensor_data["type"] == "proximity" and sensor_data["value"] < 10.0:
                    obstacle_detected = True
                    break
            
            if obstacle_detected:
                # Replan to avoid obstacle
                self.plan_path()
    
    def process_ui_command(self, command: str, params: Dict[str, Any]) -> None:
        """
        Process commands from the UI agent.
        
        Args:
            command (str): Command type (e.g., "move", "stop").
            params (Dict[str, Any]): Command parameters.
        """
        if command == "set_mode":
            self.state["navigation_mode"] = params.get("mode", "idle")
        
        elif command == "set_target":
            if "position" in params:
                self.set_target(params["position"])
                self.state["navigation_mode"] = "autonomous"
        
        elif command == "manual_move":
            # Direct manual control - pass through to motor
            self.state["navigation_mode"] = "manual"
    
    def compute(self) -> List[Message]:
        """
        Process incoming messages and determine navigation actions.
        
        Returns:
            List[Message]: Motor commands and status updates.
        """
        messages = []
        
        # Process incoming messages
        for msg in self.mailbox:
            content = msg.content
            
            if "type" in content:
                if content["type"] == "sensor_reading":
                    self.process_sensor_data(
                        content["sensor_type"], 
                        content["value"], 
                        msg.sender_id
                    )
                
                elif content["type"] == "ui_command":
                    self.process_ui_command(
                        content["command"],
                        content.get("params", {})
                    )
                
                elif content["type"] == "position_update":
                    if "position" in content:
                        self.update_position(content["position"])
        
        # Generate motor commands based on current state and mode
        if self.state["navigation_mode"] == "autonomous":
            # If we have a path and are in autonomous mode, send the next waypoint
            if self.state["planned_path"]:
                next_waypoint = self.state["planned_path"][1] if len(self.state["planned_path"]) > 1 else self.state["planned_path"][0]
                
                messages.append(Message(
                    sender_id=self.id,
                    receiver_id=self.motor_agent_id,
                    content={
                        "type": "motor_command",
                        "command": "move_to",
                        "target": next_waypoint
                    }
                ))
        
        return messages
    
    def update_state(self) -> None:
        """Update the navigation state based on processed data."""
        # This could include updating the path if obstacles were detected
        # or if we've reached a waypoint
        
        # If we're close enough to the target, remove it from the path
        if self.state["planned_path"]:
            current = self.state["current_position"]
            next_waypoint = self.state["planned_path"][0]
            
            # Calculate distance to next waypoint
            dx = next_waypoint[0] - current[0]
            dy = next_waypoint[1] - current[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            # If we're close enough, remove this waypoint
            if distance < 1.0:  # Threshold distance
                self.state["planned_path"] = self.state["planned_path"][1:]
                
                # If path is now empty and we were in autonomous mode, switch to idle
                if not self.state["planned_path"] and self.state["navigation_mode"] == "autonomous":
                    self.state["navigation_mode"] = "idle"