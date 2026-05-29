import math
import random

class LocalSearchBase:
    def __init__(self, world):
        self.world = world
        self.targets = self.world.get_targets()
        self.num_targets = len(self.targets)
        self.max_sensors = getattr(self.world, 'max_sensors', 20)
        self.sensor_range = getattr(self.world, 'sensor_range', 2)
        self.sensor_weight = 0.15
        
        # Safely extract grid rows and columns across different data structures
        if hasattr(world, 'rows') and hasattr(world, 'cols'):
            self.rows = world.rows
            self.cols = world.cols
        elif hasattr(world, 'grid'):
            grid = world.grid
            if hasattr(grid, 'shape'):
                self.rows, self.cols = grid.shape
            else:
                self.rows = len(grid)
                self.cols = len(grid[0]) if self.rows > 0 else 0
        else:
            self.rows = 0
            self.cols = 0

        # Pre-calculate valid positions to prevent redundant overhead during search
        self.valid_positions = [
            (c, r) for r in range(self.rows) for c in range(self.cols) 
            if self.world.is_valid_position(c, r)
        ]

    def _get_coverage(self, state):
        """Returns a set of all targets covered by the current sensor layout."""
        covered = set()
        for sx, sy in state:
            for tx, ty in self.targets:
                if math.hypot(sx - tx, sy - ty) <= self.sensor_range:
                    covered.add((tx, ty))
        return covered

    def evaluate(self, state):
        """Strict Objective Function: Uncovered Targets + (0.15 * Number of Sensors)."""
        unique_state = list(dict.fromkeys(state))
        if not self.targets: 
            return len(unique_state) * self.sensor_weight
            
        covered = self._get_coverage(unique_state)
        uncovered_count = self.num_targets - len(covered)
        return uncovered_count + (self.sensor_weight * len(unique_state))

    def _get_pos_near_target(self, target_pos):
        """Finds a random valid position within the sensor_range of a specific target."""
        tx, ty = target_pos
        candidates = []
        # Look within a bounding box bounded by the sensor range
        for dx in range(-self.sensor_range, self.sensor_range + 1):
            for dy in range(-self.sensor_range, self.sensor_range + 1):
                nx, ny = tx + dx, ty + dy
                if 0 <= nx < self.cols and 0 <= ny < self.rows:
                    if self.world.is_valid_position(nx, ny) and math.hypot(nx - tx, ny - ty) <= self.sensor_range:
                        candidates.append((nx, ny))
                        
        return random.choice(candidates) if candidates else (random.choice(self.valid_positions) if self.valid_positions else (0, 0))

    def initialize_state(self):
        """Smart Initialization: Places sensors directly covering randomly selected targets."""
        num_sensors = random.randint(max(1, self.max_sensors // 2), self.max_sensors)
        state = []
        uncovered = list(self.targets)
        random.shuffle(uncovered)
        
        while len(state) < num_sensors and uncovered:
            tgt = uncovered.pop(0)
            pos = self._get_pos_near_target(tgt)
            if pos not in state:
                state.append(pos)
                # Dynamic filtering to avoid putting redundant sensors close by during initialization
                uncovered = [t for t in uncovered if math.hypot(pos[0] - t[0], pos[1] - t[1]) > self.sensor_range]
                
        # Fallback padding if target density is too low to fill up desired initial sensors
        while len(state) < num_sensors and self.valid_positions:
            pos = random.choice(self.valid_positions)
            if pos not in state:
                state.append(pos)
            if len(state) >= len(self.valid_positions):
                break
                
        return list(dict.fromkeys(state))

    def get_neighbor(self, state):
        """
        Target-Aware Heuristic Neighbor Generation.
        Balances exploring alternative grids with focused target placement and smart culling.
        """
        state = list(dict.fromkeys(state))
        if not state:
            return [random.choice(self.valid_positions)] if self.valid_positions else [(0, 0)]

        new_state = state.copy()
        covered = self._get_coverage(new_state)
        uncovered_targets = [t for t in self.targets if t not in covered]

        # Dynamically set allowable local modifications
        actions = ['move']
        weights = [1.0]
        
        if len(new_state) < self.max_sensors:
            actions.append('add')
            weights.append(1.0)
        if len(new_state) > 1:
            actions.append('remove')
            # If everything is already covered, strongly prioritize sensor removal (optimization)
            weights.append(2.0 if not uncovered_targets else 0.4)

        chosen_action = random.choices(actions, weights=weights)[0]

        # --- ACTION 1: ADD A SENSOR ---
        if chosen_action == 'add':
            if uncovered_targets and random.random() < 0.85:
                # 85% Heuristic: Target-directed placement
                tgt = random.choice(uncovered_targets)
                pos = self._get_pos_near_target(tgt)
            else:
                # 15% Uniform Exploration
                pos = random.choice(self.valid_positions) if self.valid_positions else (0, 0)
            new_state.append(pos)

        # --- ACTION 2: MOVE A SENSOR ---
        elif chosen_action == 'move':
            idx = random.randrange(len(new_state))
            if uncovered_targets and random.random() < 0.75:
                # 75% Heuristic: Guide an underperforming sensor toward an unreached objective
                tgt = random.choice(uncovered_targets)
                pos = self._get_pos_near_target(tgt)
            else:
                # 25% Uniform Exploration
                pos = random.choice(self.valid_positions) if self.valid_positions else (0, 0)
            new_state[idx] = pos

        # --- ACTION 3: REMOVE A SENSOR ---
        elif chosen_action == 'remove':
            # Calculate unique coverage: count how many targets rely solely on each sensor
            unique_counts = [0] * len(new_state)
            target_to_sensors = {tgt: [] for tgt in self.targets}
            
            for s_idx, (sx, sy) in enumerate(new_state):
                for tgt in self.targets:
                    if math.hypot(sx - tgt[0], sy - tgt[1]) <= self.sensor_range:
                        target_to_sensors[tgt].append(s_idx)
                        
            for tgt, s_indices in target_to_sensors.items():
                if len(s_indices) == 1:
                    unique_counts[s_indices[0]] += 1
            
            # Prune the weakest link (sensor providing the least unique coverage)
            min_unique = min(unique_counts)
            candidates = [i for i, count in enumerate(unique_counts) if count == min_unique]
            remove_idx = random.choice(candidates)
            new_state.pop(remove_idx)

        # Sanity check deduplication and ensure state remains non-empty
        final_state = list(dict.fromkeys(new_state))
        if not final_state and self.valid_positions:
            final_state.append(random.choice(self.valid_positions))
            
        return final_state
