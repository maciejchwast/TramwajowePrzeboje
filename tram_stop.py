import uuid


class TramStop:
    """
  This class represents a stop in a tram network.

  Attributes:
      name (str): The name of the stop.
      x (int): The x-coordinate of the stop's position (for visualization).
      y (int): The y-coordinate of the stop's position (for visualization).
      waiting_passengers (int): The number of passengers currently waiting at the stop.
      connected_stops (list): A list of TramStop objects representing stops connected to this stop.
  """

    def __init__(self, name, x, y):
        """
    Initializes a TramStop object.

    Args:
        name (str): The name of the stop.
        x (int): The x-coordinate of the stop's position.
        y (int): The y-coordinate of the stop's position.
    """
        self.name = name
        self.x = x
        self.y = y
        self.stop_id = str(uuid.uuid4())  # Generate unique stop_id using uuid
        self.waiting_passengers = 0
        self.connected_stops = []

    def add_passenger(self):
        """
    Increases the number of waiting passengers at the stop by 1.
    """
        self.waiting_passengers += 1

    def remove_passenger(self, count=1):
        """
    Decreases the number of waiting passengers at the stop.

    Args:
        count (int, optional): The number of passengers to remove. Defaults to 1.
    """
        self.waiting_passengers = max(self.waiting_passengers - count, 0)

    def connect_to(self, stop_uuid):
        """
    Connects this stop to another stop.

    Args:
        stop (TramStop): The TramStop object to connect to.
    """
        self.connected_stops.append(stop_uuid)

    def get_info(self):
        """
    Returns a string containing information about the stop.
    """
        return f"Stop: {self.name}, Waiting: {self.waiting_passengers}"
