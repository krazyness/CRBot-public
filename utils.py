from functools import wraps
import time


def timing_decorator(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        result = func(self, *args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time

        # Use class logger if available, otherwise fall back to print
        if hasattr(self, 'logger') and self.logger:
            self.logger.debug(f"[Performance] {func.__name__:<25} took {execution_time:.4f} seconds")
        else:
            print(f"[Performance] {func.__name__:<25} took {execution_time:.4f} seconds")

        return result
    return wrapper