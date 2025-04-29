"""
Graph generator for DCOP problems.

Provides functions to generate random constraint graphs
for testing DCOP algorithms.
"""

import random
from typing import Dict, List, Tuple, Any, Set


def generate_uniform_random_graph(num_agents: int, domain_size: int, 
                                 density: float, cost_lb: int = 100, 
                                 cost_ub: int = 200) -> Dict:
    """
    Generate a uniform random constraint graph.
    
    Args:
        num_agents (int): Number of agents.
        domain_size (int): Size of each agent's domain.
        density (float): Probability of a constraint between any two agents.
        cost_lb (int): Lower bound for random costs.
        cost_ub (int): Upper bound for random costs.
        
    Returns:
        Dict: Graph description with agents, domains, and constraints.
    """
    # Create agent IDs
    agent_ids = [f"agent_{i}" for i in range(num_agents)]
    
    # Create domains (all agents have the same domain)
    domains = {}
    for agent_id in agent_ids:
        domains[agent_id] = list(range(domain_size))
    
    # Create random constraints
    constraints = {}
    for i in range(num_agents):
        for j in range(i+1, num_agents):
            # With probability 'density', create a constraint
            if random.random() < density:
                agent_i = agent_ids[i]
                agent_j = agent_ids[j]
                
                # Create random costs for all value combinations
                costs = {}
                for val_i in domains[agent_i]:
                    for val_j in domains[agent_j]:
                        costs[(val_i, val_j)] = random.uniform(cost_lb, cost_ub)
                
                # Store constraint with costs
                constraints[(agent_i, agent_j)] = costs
    
    return {
        "agents": agent_ids,
        "domains": domains,
        "constraints": constraints
    }


def generate_graph_coloring(num_agents: int, num_colors: int, 
                           density: float, cost_lb: int = 100, 
                           cost_ub: int = 200) -> Dict:
    """
    Generate a graph coloring problem.
    
    Args:
        num_agents (int): Number of agents (vertices).
        num_colors (int): Number of colors.
        density (float): Probability of an edge between any two vertices.
        cost_lb (int): Lower bound for random costs when colors match.
        cost_ub (int): Upper bound for random costs when colors match.
        
    Returns:
        Dict: Graph description with agents, domains, and constraints.
    """
    # Create agent IDs
    agent_ids = [f"agent_{i}" for i in range(num_agents)]
    
    # Create domains (colors)
    domains = {}
    for agent_id in agent_ids:
        domains[agent_id] = list(range(num_colors))
    
    # Create random constraints
    constraints = {}
    for i in range(num_agents):
        for j in range(i+1, num_agents):
            # With probability 'density', create a constraint
            if random.random() < density:
                agent_i = agent_ids[i]
                agent_j = agent_ids[j]
                
                # Create costs for all value combinations
                costs = {}
                for val_i in domains[agent_i]:
                    for val_j in domains[agent_j]:
                        if val_i == val_j:
                            # Same color = penalty
                            costs[(val_i, val_j)] = random.uniform(cost_lb, cost_ub)
                        else:
                            # Different colors = no penalty
                            costs[(val_i, val_j)] = 0.0
                
                # Store constraint with costs
                constraints[(agent_i, agent_j)] = costs
    
    return {
        "agents": agent_ids,
        "domains": domains,
        "constraints": constraints
    }


def calculate_global_cost(graph: Dict, assignment: Dict[str, Any]) -> float:
    """
    Calculate the global cost of an assignment.
    
    Args:
        graph (Dict): Graph description with constraints.
        assignment (Dict[str, Any]): Assignment of values to agents.
        
    Returns:
        float: Total cost of the assignment.
    """
    total_cost = 0.0
    
    for (agent_i, agent_j), costs in graph["constraints"].items():
        if agent_i in assignment and agent_j in assignment:
            val_i = assignment[agent_i]
            val_j = assignment[agent_j]
            
            if (val_i, val_j) in costs:
                total_cost += costs[(val_i, val_j)]
    
    return total_cost