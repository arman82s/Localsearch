from search.local_search_base import LocalSearchBase
import random
import math

class SimulatedAnnealing(LocalSearchBase):
    def run(self, initial_state, initial_temp=None, cooling_rate=None, min_temp=1e-3, max_iter=None, **kwargs):
        max_iter = max_iter or 6000
        cooling_rate = cooling_rate or 0.996
        
        current_state = list(dict.fromkeys(initial_state))
        current_cost = self.evaluate(current_state)
        
        # Dynamic Initial Temperature scaling to accommodate varied maps safely
        initial_temp = initial_temp or max(50.0, current_cost * 3.0)
        
        best_state = current_state.copy()
        best_cost = current_cost
        
        evaluations = [current_cost]
        states_history = [current_state.copy()]
        
        temp = initial_temp
        iteration = 0
        
        while temp > min_temp and iteration < max_iter:
            neighbor = self.get_neighbor(current_state)
            neighbor_cost = self.evaluate(neighbor)
            
            delta = neighbor_cost - current_cost
            
            # Metropolis Criterion for stochastic hill-climbing escape vectors
            if delta < 0 or random.random() < math.exp(-delta / max(temp, 1e-9)):
                current_state = neighbor
                current_cost = neighbor_cost
                
            if current_cost < best_cost:
                best_state = current_state.copy()
                best_cost = current_cost
                
            evaluations.append(current_cost)
            states_history.append(current_state.copy())
            
            # Continuous monotonic temperature adjustment
            temp *= cooling_rate
            iteration += 1
            
        return best_state, best_cost, evaluations, states_history
