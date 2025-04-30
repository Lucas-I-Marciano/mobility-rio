from enum import Enum

class EndpointTags(str, Enum):
    NOTIFICATION ="Notification"
    BUS = "Bus"
    ALERTS = "Alerts"
    DEFAULT = ".Welcome."