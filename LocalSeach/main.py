"""
University: University of Isfahan
Faculty: Mathematics and Statistics
Branch: Computer Science
Course: Artificial Intelligence
Professor: Dr. Faria Nasiri Mofakham
TAs: MehrAzin Marzough, Mohammad Karimi, Anahita Honarmandian
Project: Implementing Local Search Algorithms for a Sensor Placement Optimization Problem
"""
from env.grid_world import GridWorld
from search.hill_climbing import HillClimbing
from search.simulated_annealing import SimulatedAnnealing
from utils import represent
import re
import matplotlib
matplotlib.use("TkAgg")

def run_algorithms(world, initial_state, algorithm_classes):
    best_states = []
    best_costs = []
    evaluations = []
    histories = []
    names = []
    
    for algorithm_class in algorithm_classes:
        name = re.sub(r'(?<!^)([A-Z])', r' \1', algorithm_class.__name__)
        names.append(name)
        
        algorithm_instance = algorithm_class(world)
        print(f"\nRunning {name}...")
        
        state, cost, evals, hist = algorithm_instance.run(initial_state)
        
        best_states.append(state)
        best_costs.append(cost)
        evaluations.append(evals)
        histories.append(hist)

    represent(
        best_states=best_states,
        best_costs=best_costs,
        evaluations=evaluations,
        histories=histories,
        names=names,
        world=world
    )

if __name__ == "__main__": 
    world = GridWorld("map1")
    algorithm_classes = [
        HillClimbing,
        SimulatedAnnealing
    ]

    initial_state = HillClimbing(world).initialize_state()
    print(f"Initial State: {initial_state}")

    run_algorithms(world, initial_state, algorithm_classes)
