from typing import Literal
from enum import StrEnum


class Column(StrEnum):
    REPORT_ID = "REPORT_ID"
    DATE_TIME = "DATE_TIME"
    PERSON_ROLE = "PERSON_ROLE"
    PERSON_INJURY_LVL = "PERSON_INJURY_LVL"
    PERSON_VEH_TYPE = "PERSON_VEH_TYPE"
    VEH_TYPE = "VEH_TYPE"
    VEH_MAKE = "VEH_MAKE"
    VEH_MODEL = "VEH_MODEL"
    POLICE_BEAT = "POLICE_BEAT"
    ADDRESS_NO_PRIMARY = "ADDRESS_NO_PRIMARY"
    ADDRESS_PD_PRIMARY = "ADDRESS_PD_PRIMARY"
    ADDRESS_ROAD_PRIMARY = "ADDRESS_ROAD_PRIMARY"
    ADDRESS_SFX_PRIMARY = "ADDRESS_SFX_PRIMARY"
    ADDRESS_PD_INTERSECTING = "ADDRESS_PD_INTERSECTING"
    ADDRESS_NAME_INTERSECTING = "ADDRESS_NAME_INTERSECTING"
    ADDRESS_SFX_INTERSECTING = "ADDRESS_SFX_INTERSECTING"
    VIOLATION_SECTION = "VIOLATION_SECTION"
    VIOLATION_TYPE = "VIOLATION_TYPE"
    CHARGE_DESC = "CHARGE_DESC"
    INJURED = "INJURED"
    KILLED = "KILLED"
    HIT_RUN_LVL = "HIT_RUN_LVL"
    FULL_ADDRESS = "full_address"
    BEAT = "beat"
    NEIGHBORHOOD = "neighborhood"


class Severity(StrEnum):
    POSSIBLE = "POSSIBLE"
    MINOR = "MINOR"
    VISABLE = "VISABLE"
    PAIN = "PAIN"
    SERIOUS = "SERIOUS"
    SEVERE = "SEVERE"
    FATAL = "FATAL"


def translate_severity(severity_lvl: Literal["Light", "Serious", "Fatal"]):
    light = [Severity.POSSIBLE, Severity.MINOR, Severity.VISABLE, Severity.PAIN]
    serious = [Severity.SERIOUS, Severity.SEVERE]
    fatal = [Severity.FATAL]
    if severity_lvl == "Light":
        return light
    if severity_lvl == "Serious":
        return serious
    if severity_lvl == "Fatal":
        return fatal
