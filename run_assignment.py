"""
All-in-one script to run the DCOP algorithm assignment.

This script sets up and runs all the experiments required for the assignment.
It will:
1. Create all the necessary directories
2. Initialize all modules
3. Run the wheelchair simulation as a demo
4. Run the DCOP algorithm comparison with parameters matching the assignment requirements
5. Generate visualizations and result files
"""

import os
import sys
import subprocess
import time
import shutil

def print_header(text):
    """Print a section header."""
    print("\n" + "="*80)
    print(f" {text} ".center(80, "="))
    print("="*80 + "\n")

def setup_environment():
    """Set up the Python environment and create necessary directories."""
    print_header("Setting up environment")
    
    # Create results directory
    os.makedirs("results", exist_ok=True)
    print("✓ Created results directory.")
    
    # Check for necessary Python packages
    try:
        import matplotlib
        import numpy
        print("✓ Required packages are already installed.")
    except ImportError:
        print("Installing required packages...")
        subprocess.run([sys.executable, "-m", "pip", "install", "matplotlib", "numpy"])
        print("✓ Required packages installed.")

def copy_missing_files():
    """Copy any missing files in case some weren't created properly."""
    print_header("Ensuring all required files exist")
    
    # Ensure blank __init__.py files exist in all directories
    for directory in ["core", "agents", "algorithms", "utils", "tests"]:
        init_file = os.path.join(directory, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                pass
            print(f"✓ Created {init_file}")

def run_wheelchair_demo():
    """Run the wheelchair simulation as a demo."""
    print_header("Running wheelchair simulation demo")
    
    # Import and run
    from main import run_wheelchair_simulation
    run_wheelchair_simulation(num_steps=10)

def run_dcop_experiments():
    """Run the DCOP algorithm experiments."""
    print_header("Running DCOP algorithm comparison")
    
    print("This will run 5 algorithms on 3 graph types with 30 runs each.")
    print("This may take a significant amount of time (up to several hours).")
    print("\nWould you like to run:")
    print("1. A quick demo with reduced parameters (a few minutes)")
    print("2. The full experiment as required in the assignment (hours)")
    print("3. Skip this part and exit")
    
    try:
        choice = int(input("\nEnter your choice (1-3): ").strip())
    except ValueError:
        choice = 3
    
    if choice == 1:
        # Run with reduced parameters
        from run_dcop_comparison import run_comparison
        run_comparison(num_agents=5, num_iterations=10, num_runs=2, seed=42)
    elif choice == 2:
        # Run with full parameters
        from run_dcop_comparison import run_comparison
        run_comparison(num_agents=30, num_iterations=50, num_runs=30, seed=42)
    else:
        print("Skipping DCOP experiments.")
        return
    
    print("\n✓ DCOP experiments completed.")
    
    # Open results folder
    if os.path.exists("results"):
        print("Opening results folder...")
        try:
            if sys.platform == 'win32':
                os.startfile(os.path.abspath("results"))
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', os.path.abspath("results")])
            else:  # Linux
                subprocess.run(['xdg-open', os.path.abspath("results")])
        except Exception:
            print("Could not open results folder automatically. Please check the 'results' directory.")

def check_modules():
    """Check that all modules can be imported."""
    print_header("Checking module imports")
    
    try:
        # Core modules
        from core.agent import Agent
        from core.message import Message
        from core.environment import Environment, Scheduler
        print("✓ Core modules loaded.")
        
        # Agent modules
        from agents.sensor_agent import SensorAgent, ProximitySensorAgent, BodySensorAgent
        from agents.navigation_agent import NavigationAgent
        from agents.motor_agent import MotorAgent
        from agents.ui_agent import UIAgent
        print("✓ Agent modules loaded.")
        
        # Algorithm modules
        from algorithms.dsa import DSAAgent
        from algorithms.mgm import MGMAgent
        from algorithms.mgm2 import MGM2Agent
        print("✓ Algorithm modules loaded.")
        
        # Utility modules
        from utils.graph_generator import generate_uniform_random_graph, generate_graph_coloring
        from utils.logger import Logger
        print("✓ Utility modules loaded.")
        
        return True
    except ImportError as e:
        print(f"Error importing modules: {e}")
        return False

if __name__ == "__main__":
    print_header("DCOP Assignment Runner")
    
    try:
        # Change to the directory of this script
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        setup_environment()
        copy_missing_files()
        
        if check_modules():
            run_wheelchair_demo()
            run_dcop_experiments()
        
        print_header("Assignment run complete!")
        print("Check the 'results' directory for outputs.")
        print("Folder path:", os.path.abspath("results"))
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Keep console open
    input("\nPress Enter to exit...")
