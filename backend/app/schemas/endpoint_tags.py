from enum import Enum

class EndpointTags(str, Enum):
    NOTIFICATION ="Notifications"
    BUS = "Bus Status"
    ALERTS = "Alerts"
    DEFAULT = "Welcome"
    ETA_CALCULATION = "ETA Calculation"
    USERS = "Users"