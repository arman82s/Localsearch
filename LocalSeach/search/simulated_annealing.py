from search.local_search_base import LocalSearchBase
import random
import math

class SimulatedAnnealing(LocalSearchBase):
    def run(self, initial_state, initial_temp=100.0, cooling_rate=0.95, 
            min_temp=1e-3, max_iter=1000, **kwargs):
        """
        اجرای الگوریتم Simulated Annealing
        """
        current_state = list(initial_state)
        current_cost = self.evaluate(current_state)
        
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

            # معیار پذیرش متروپولیس
            if delta < 0 or random.random() < math.exp(-delta / temp):
                current_state = neighbor
                current_cost = neighbor_cost

            # ذخیره بهترین حالت سراسری
            if current_cost < best_cost:
                best_state = current_state.copy()
                best_cost = current_cost

            evaluations.append(current_cost)
            states_history.append(current_state.copy())

            # کاهش دما
            temp *= cooling_rate
            iteration += 1

        return best_state, best_cost, evaluations, states_history