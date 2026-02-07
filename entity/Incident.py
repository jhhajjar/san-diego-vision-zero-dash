from datetime import datetime
from enum import Enum
from typing import Optional


class HitRunLevel(Enum):
    MISDEMEANOR = "Misdemeanor"
    FELONY = "Felony"
    NONE = "None"


class IncidentDTO:
    report_id: str
    date_time: datetime
    charge_desc: str
    injured: int
    killed: int
    neighborhood: str
    full_address: str
    latitude: Optional[float]
    longitude: Optional[float]


class IncidentListDTO:
    incidents: list[IncidentDTO]
    page: int
    pageSize: int
    totalIncidents: int


class IncidentMetadataDTO:
    number_of_days_since_last_incident: int
    latest_date: datetime
