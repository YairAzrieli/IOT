"""
Logging utilities for the DCOP simulation.

Provides functions to record metrics and create visualizations.
"""

import logging
import matplotlib.pyplot as plt
from typing import List, Dict, Any


class Logger:
    """
    Logger for simulation metrics and events.
    
    Attributes:
        metrics (Dict): Record of metrics over time.
        log_file (str): Path to log file.
    """
    
    def __init__(self, log_file: str = "simulation.log"):
        """
        Initialize a logger.
        
        Args:
            log_file (str): Path to log file.
        """
        self.metrics = {
            "global_cost": [],
            "iterations": [],
            "messages_sent": [],
            "algorithm": None
        }
        self.log_file = log_file
        
        # Set up Python logging
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("DCOP_Simulation")
    
    def log_iteration(self, iteration: int, global_cost: float, 
                      messages_sent: int) -> None:
        """
        Log metrics for a simulation iteration.
        
        Args:
            iteration (int): Current iteration.
            global_cost (float): Global cost of current assignment.
            messages_sent (int): Number of messages sent in this iteration.
        """
        self.metrics["iterations"].append(iteration)
        self.metrics["global_cost"].append(global_cost)
        self.metrics["messages_sent"].append(messages_sent)
        
        self.logger.info(
            f"Iteration {iteration}: Cost = {global_cost:.2f}, "
            f"Messages = {messages_sent}"
        )
    
    def set_algorithm(self, algorithm: str) -> None:
        """
        Set the algorithm being used.
        
        Args:
            algorithm (str): Name of the algorithm.
        """
        self.metrics["algorithm"] = algorithm
        self.logger.info(f"Using algorithm: {algorithm}")
    
    def log_event(self, event: str) -> None:
        """
        Log a simulation event.
        
        Args:
            event (str): Event description.
        """
        self.logger.info(event)
    
    def plot_cost_vs_iteration(self, save_path: str = None) -> None:
        """
        Plot global cost vs. iteration.
        
        Args:
            save_path (str): Path to save the plot. If None, display instead.
        """
        plt.figure(figsize=(10, 6))
        plt.plot(self.metrics["iterations"], self.metrics["global_cost"], 
                 marker='o', linestyle='-')
        
        plt.title("Global Cost vs. Iteration")
        plt.xlabel("Iteration")
        plt.ylabel("Global Cost")
        plt.grid(True)
        
        if self.metrics["algorithm"]:
            plt.title(f"{self.metrics['algorithm']}: Global Cost vs. Iteration")
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()
    
    def plot_messages_vs_iteration(self, save_path: str = None) -> None:
        """
        Plot messages sent vs. iteration.
        
        Args:
            save_path (str): Path to save the plot. If None, display instead.
        """
        plt.figure(figsize=(10, 6))
        plt.plot(self.metrics["iterations"], self.metrics["messages_sent"], 
                 marker='o', linestyle='-')
        
        plt.title("Messages Sent vs. Iteration")
        plt.xlabel("Iteration")
        plt.ylabel("Messages Sent")
        plt.grid(True)
        
        if self.metrics["algorithm"]:
            plt.title(f"{self.metrics['algorithm']}: Messages Sent vs. Iteration")
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()
    
    def get_average_cost(self, start_iteration: int = 0) -> float:
        """
        Get average global cost from a starting iteration.
        
        Args:
            start_iteration (int): First iteration to include.
            
        Returns:
            float: Average global cost.
        """
        if not self.metrics["global_cost"]:
            return 0.0
        
        if start_iteration >= len(self.metrics["global_cost"]):
            return 0.0
        
        costs = self.metrics["global_cost"][start_iteration:]
        return sum(costs) / len(costs)


def compare_algorithms(loggers: Dict[str, Logger], save_path: str = None) -> None:
    """
    Compare multiple algorithms on a single plot.
    
    Args:
        loggers (Dict[str, Logger]): Map of algorithm name to logger.
        save_path (str): Path to save the plot. If None, display instead.
    """
    plt.figure(figsize=(12, 8))
    
    for algorithm, logger in loggers.items():
        plt.plot(logger.metrics["iterations"], 
                 logger.metrics["global_cost"],
                 label=algorithm)
    
    plt.title("Algorithm Comparison: Global Cost vs. Iteration")
    plt.xlabel("Iteration")
    plt.ylabel("Global Cost")
    plt.legend()
    plt.grid(True)
    
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()