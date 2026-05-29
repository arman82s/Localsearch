from search.local_search_base import LocalSearchBase
import random
import math

class HillClimbing(LocalSearchBase):
    def run(self, initial_state, max_iter=None, patience=None, **kwargs):
        max_iter = max_iter or 5000
        patience = patience or 800

        current_state = list(dict.fromkeys(initial_state))
        current_cost = self.evaluate(current_state)
        
        best_state = current_state.copy()
        best_cost = current_cost
        
        evaluations = [current_cost]
        states_history = [current_state.copy()]
        
        no_improve_count = 0
        
        for _ in range(max_iter):
            neighbor = self.get_neighbor(current_state)
            neighbor_cost = self.evaluate(neighbor)
            
            if neighbor_cost < current_cost:
                # Direct improvement
                current_state = neighbor
                current_cost = neighbor_cost
                no_improve_count = 0
            elif neighbor_cost == current_cost and random.random() < 0.30:
                # Sideways Move: 30% probability to cross plateaus and prevent premature freezing
                current_state = neighbor
                current_cost = neighbor_cost
                no_improve_count += 1
            else:
                no_improve_count += 1
                
            # Log absolute historical best
            if current_cost < best_cost:
                best_state = current_state.copy()
                best_cost = current_cost
                
            evaluations.append(current_cost)
            states_history.append(current_state.copy())
            
            # Smart Perturbation (Soft Restart)
            if no_improve_count >= patience:
                current_state = best_state.copy()
                # Target roughly 30% of current assets for repositioning
                num_to_perturb = max(1, int(len(current_state) * 0.30))
                indices = random.sample(range(len(current_state)), num_to_perturb)
                
                covered = self._get_coverage(current_state)
                uncovered = [t for t in self.targets if t not in covered]
                
                for idx in indices:
                    if uncovered and random.random() < 0.60:
                        # Re-route stalled assets toward completely blind spots
                        tgt = random.choice(uncovered)
                        current_state[idx] = self._get_pos_near_target(tgt)
                    else:
                        current_state[idx] = random.choice(self.valid_positions)
                        
                current_state = list(dict.fromkeys(current_state))
                current_cost = self.evaluate(current_state)
                no_improve_count = 0
                
        return best_state, best_cost, evaluations, states_history
