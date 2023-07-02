import requests
import time

class RateLimitedSession(requests.Session):
    """Use a requests session, but ensure no more than `max_requests` number of requests are sent every second."""
    def __init__(self, max_requests:int=30, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_requests: int = max_requests
        self.interval: float = 1 / max_requests
        self.last_request_time: float = time.monotonic()

    def send(self, *args, **kwargs):
        # Calculate the time since the last request
        current_time: float = time.monotonic()
        elapsed_time: float = current_time - self.last_request_time

        # If the elapsed time is less than the interval, pause execution
        if elapsed_time < self.interval:
            time.sleep(self.interval - elapsed_time)

        # Make the request and update the last request time
        response: requests.Response = super().send(*args, **kwargs)
        self.last_request_time = time.monotonic()

        return response
