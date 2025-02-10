"""
You are given an array of length 24, where each element represents the number of new subscribers during the corresponding hour. Implement a data structure that efficiently supports the following:
update(hour: int, value: int): Increment the element at index hour by value.
query(start: int, end: int): Retrieve the number of subscribers that have signed up between start and end (inclusive).
You can assume that all values get cleared at the end of the day, and that you will not be asked for start and end values that wrap around midnight.
"""
class HourlySubscriberTracker:
    def __init__(self):
        self.subscribers = [0] * 24  # Initialize an array of 24 hours

    def update(self, hour: int, value: int):
        """Increment the element at index hour by value."""
        if 0 <= hour < 24:
            self.subscribers[hour] += value
        else:
            raise ValueError("Hour must be between 0 and 23.")

    def query(self, start: int, end: int) -> int:
        """Retrieve the number of subscribers that have signed up between start and end (inclusive)."""
        if 0 <= start <= end < 24:
            return sum(self.subscribers[start:end+1])
        else:
            raise ValueError("Start and end must be between 0 and 23, and start must be <= end.")

# Example Usage
tracker = HourlySubscriberTracker()
tracker.update(5, 10)
tracker.update(10, 20)
tracker.update(15, 30)
print(tracker.query(5, 10))  # Output: 30
print(tracker.query(10, 15)) # Output: 50