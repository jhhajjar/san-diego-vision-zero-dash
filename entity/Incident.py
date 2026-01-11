from datetime import datetime
from enum import Enum


class HitRunLevel(Enum):
    MISDEMEANOR = "Misdemeanor"
    FELONY = "Felony"
    NONE = "None"


class IncidentDTO:
    report_id: str
    date_time: datetime
    police_beat: int
    address_no_primary: int
    address_pd_primary: str
    address_road_primary: str
    address_sfx_primary: str
    address_pd_intersecting: str
    address_name_intersecting: str
    address_sfx_intersecting: str
    violation_section: str
    violation_type: str
    charge_desc: str
    injured: int
    killed: int
    hit_run_lvl: HitRunLevel
    neighborhood: str
    full_address: str


class IncidentListDTO:
    incidents: list[IncidentDTO]
    page: int
    pageSize: int
    totalIncidents: int


class IncidentMetadataDTO:
    number_of_days_since_last_incident: int
    latest_date: datetime
