from search.local_search_base import LocalSearchBase

class HillClimbing(LocalSearchBase):
    def run(self, initial_state, max_iter=1000, patience=50, **kwargs):
        """
        اجرای الگوریتم Hill Climbing
        """
        current_state = list(initial_state)
        current_cost = self.evaluate(current_state)
        
        best_state = current_state.copy()
        best_cost = current_cost

        evaluations = [current_cost]
        states_history = [current_state.copy()]
        
        no_improve_count = 0

        for _ in range(max_iter):
            neighbor = self.get_neighbor(current_state)
            neighbor_cost = self.evaluate(neighbor)

            # پذیرش همسایه فقط در صورت بهبود
            if neighbor_cost < current_cost:
                current_state = neighbor
                current_cost = neighbor_cost
                no_improve_count = 0
            else:
                no_improve_count += 1

            # به‌روزرسانی بهترین حالت یافت‌شده
            if current_cost < best_cost:
                best_state = current_state.copy()
                best_cost = current_cost

            evaluations.append(current_cost)
            states_history.append(current_state.copy())

            # خروج از بهینه محلی با معیار صبر
            if no_improve_count >= patience:
                break

        return best_state, best_cost, evaluations, states_history