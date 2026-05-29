import math
import random

class LocalSearchBase:
    def __init__(self, world):
        self.world = world
        # وزن سنسورها در تابع هزینه (برای تحلیل trade-off قابل تغییر است)
        self.sensor_weight = 0.2 

    def evaluate(self, state):
        """
        محاسبه هزینه حالت فعلی.
        هدف: کمینه‌سازی هزینه = (اهداف پوشش‌داده‌نشده) + (وزن × تعداد سنسورها)
        """
        # حذف مختصات تکراری برای اطمینان
        state = list(dict.fromkeys(state))
        
        targets = self.world.get_targets()
        if not targets:
            return len(state) * self.sensor_weight

        covered_targets = set()
        sensor_range = self.world.sensor_range

        for sx, sy in state:
            for tx, ty in targets:
                if math.hypot(sx - tx, sy - ty) <= sensor_range:
                    covered_targets.add((tx, ty))

        uncovered_count = len(targets) - len(covered_targets)
        cost = uncovered_count + self.sensor_weight * len(state)
        return cost

    def _get_random_valid_position(self):
        """دریافت یک موقعیت معتبر تصادفی با بررسی محدودیت‌ها"""
        # تلاش برای استفاده از متد محیط
        if hasattr(self.world, 'random_position'):
            try:
                return self.world.random_position()
            except:
                pass
        
        # Fallback: جستجوی تصادفی در گرید
        while True:
            x = random.randint(0, self.world.cols - 1)
            y = random.randint(0, self.world.rows - 1)
            if self.world.is_valid_position(x, y):
                return (x, y)

    def get_neighbor(self, state):
        """
        تولید همسایه با سه عملیات: جابجایی، افزودن، حذف سنسور
        """
        state = list(dict.fromkeys(state)) # اطمینان از یکتایی
        new_state = state.copy()
        
        # انتخاب عملیات بر اساس شرایط فعلی
        possible_ops = ['move']
        if len(new_state) < self.world.max_sensors:
            possible_ops.append('add')
        if len(new_state) > 1: # حداقل یک سنسور حفظ شود
            possible_ops.append('remove')
            
        op = random.choice(possible_ops)

        if op == 'move' and len(new_state) > 0:
            idx = random.randint(0, len(new_state) - 1)
            new_state[idx] = self._get_random_valid_position()
        elif op == 'add':
            new_state.append(self._get_random_valid_position())
        elif op == 'remove':
            idx = random.randint(0, len(new_state) - 1)
            new_state.pop(idx)

        # حذف مختصات تکراری نهایی
        return list(dict.fromkeys(new_state))

    def initialize_state(self):
        """تولید حالت اولیه معتبر"""
        num_sensors = random.randint(1, max(1, self.world.max_sensors))
        state = [self._get_random_valid_position() for _ in range(num_sensors)]
        return list(dict.fromkeys(state))