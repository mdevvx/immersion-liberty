import time
from collections import deque
from config.settings import JOIN_WINDOW_SECONDS, MAX_JOINS_PER_WINDOW


class JoinRateLimiter:
    def __init__(self):
        self.joins = deque()

    def record_join(self) -> bool:
        """
        Returns True if joins are allowed,
        False if rate limit is exceeded.
        """
        now = time.time()
        self.joins.append(now)

        # Remove old entries
        while self.joins and now - self.joins[0] > JOIN_WINDOW_SECONDS:
            self.joins.popleft()

        return len(self.joins) <= MAX_JOINS_PER_WINDOW
