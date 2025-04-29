"""
UI Agent implementation.

Responsible for handling user inputs (voice, joystick)
and translating them to navigation commands.
"""

from typing import List, Dict, Any, Tuple, Optional
from core.agent import Agent
from core.message import Message


class UIAgent(Agent):
    """
    Agent responsible for user interface interaction.
    
    Attributes:
        id (str): Unique identifier for the agent.
        navigation_agent_id (str): ID of the navigation agent.
        input_devices (List[str]): Available input devices.
    """
    
    def __init__(self, id: str, navigation_agent_id: str, input_devices: List[str] = None):
        """
        Initialize a UI agent.
        
        Args:
            id (str): Unique identifier for the agent.
            navigation_agent_id (str): ID of the navigation agent.
            input_devices (List[str]): Available input devices (e.g., "joystick", "voice").
        """
        super().__init__(id)
        self.navigation_agent_id = navigation_agent_id
        
        if input_devices is None:
            input_devices = ["joystick"]
        
        # Initialize state
        self.state = {
            "input_devices": input_devices,
            "user_input": {},  # Latest inputs from user
            "emergency_stop": False,  # Emergency stop flag
            "destinations": {}  # Known destinations
        }
    
    def read_user_input(self) -> Dict[str, Any]:
        """
        Read inputs from user input devices.
        
        This would be replaced with actual input reading from joystick, voice, etc.
        
        Returns:
            Dict[str, Any]: The user inputs from various devices.
        """
        # In a real implementation, this would read from input devices
        # For simulation, we can return simulated inputs
        
        # Example: no input by default
        return {}
    
    def process_voice_command(self, command: str) -> Dict[str, Any]:
        """
        Process a voice command.
        
        Args:
            command (str): Voice command (e.g., "go to kitchen", "stop").
            
        Returns:
            Dict[str, Any]: Command structure to send to navigation agent.
        """
        # Simple command processing
        command = command.lower()
        result = {}
        
        if "stop" in command:
            result = {
                "command": "stop"
            }
        elif "go to" in command:
            # Extract destination
            parts = command.split("go to")[1].strip()
            destination = parts.split()[0] if parts else None
            
            if destination and destination in self.state["destinations"]:
                result = {
                    "command": "set_target",
                    "position": self.state["destinations"][destination]
                }
        
        return result
    
    def process_joystick_input(self, joystick_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Process joystick input.
        
        Args:
            joystick_data (Dict[str, float]): Joystick input (e.g., x, y axes).
            
        Returns:
            Dict[str, Any]: Command structure to send to navigation agent.
        """
        # Simplified joystick processing
        result = {}
        
        if "x" in joystick_data and "y" in joystick_data:
            x = joystick_data["x"]
            y = joystick_data["y"]
            
            # Convert to polar coordinates for direction/speed
            import math
            r = math.sqrt(x*x + y*y)
            theta = math.atan2(y, x)
            
            # Only send command if joystick is moved significantly
            if r > 0.1:  # Threshold to ignore small movements
                result = {
                    "command": "manual_move",
                    "direction": theta,
                    "speed": r * 5.0  # Scale to max speed
                }
            else:
                result = {
                    "command": "stop"
                }
        
        return result
    
    def compute(self) -> List[Message]:
        """
        Read user inputs and convert them to navigation commands.
        
        Returns:
            List[Message]: Commands for the navigation agent.
        """
        messages = []
        
        # Process incoming messages (e.g., emergency alerts)
        for msg in self.mailbox:
            content = msg.content
            
            if "type" in content and content["type"] == "emergency_alert":
                self.state["emergency_stop"] = True
        
        # Read user input
        user_input = self.read_user_input()
        self.state["user_input"] = user_input
        
        # If in emergency stop, don't process new commands
        if self.state["emergency_stop"]:
            messages.append(Message(
                sender_id=self.id,
                receiver_id=self.navigation_agent_id,
                content={
                    "type": "ui_command",
                    "command": "stop",
                    "params": {}
                }
            ))
            return messages
        
        # Process user input based on device
        command = {}
        
        if "voice" in user_input:
            command = self.process_voice_command(user_input["voice"])
        
        elif "joystick" in user_input:
            command = self.process_joystick_input(user_input["joystick"])
        
        # Send command to navigation agent if we have one
        if command:
            messages.append(Message(
                sender_id=self.id,
                receiver_id=self.navigation_agent_id,
                content={
                    "type": "ui_command",
                    "command": command.get("command"),
                    "params": {k: v for k, v in command.items() if k != "command"}
                }
            ))
        
        return messages
    
    def add_destination(self, name: str, position: Tuple[float, float]) -> None:
        """
        Add a named destination for voice commands.
        
        Args:
            name (str): Name of destination (e.g., "kitchen").
            position (Tuple[float, float]): Coordinates of destination.
        """
        self.state["destinations"][name] = position
    
    def clear_emergency(self) -> None:
        """Clear the emergency stop flag."""
        self.state["emergency_stop"] = False