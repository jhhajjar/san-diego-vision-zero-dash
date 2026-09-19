from enum import StrEnum
import re
import pandas as pd
import pytz

from services.geocoding_service import geocode_address
from entity.Incident import IncidentDTO, IncidentListDTO, IncidentMetadataDTO
from typing import Tuple


class Column(StrEnum):
    REPORT_ID = "REPORT_ID"
    DATE_TIME = "DATE_TIME"
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


COLLISIONS_DF_URL = (
    "https://seshat.datasd.org/traffic_collisions/pd_collisions_datasd.csv"
)
BEATS_DF_URL = (
    "https://seshat.datasd.org/gis_police_beats/pd_beat_codes_list_datasd.csv"
)


def read_pd_csv() -> pd.DataFrame:
    """
    Column descriptions:

    report_id: Collision report number
    date_time: Date/time of collision: Date / time in 24 hour format
    police_beat: San Diego Police beat: see list linked at https://data.sandiego.gov/datasets/police-beats/
    address_no_primary: Street number of collision location, abstracted to block level
    address_pd_primary: Direction of street in location
    address_road_primary: Name of street
    address_sfx_primary: Street type
    address_pd_intersecting: Direction of cross street, if collision at intersection
    address_name_intersecting: Street name, if collision at intersection
    address_sfx_intersecting: Street type, if collision at intersection
    violation_section: Violation section for primary collision factor
    violation_type: Violation type for primary collision factor
    charge_desc: Violation section description for primary collision factor: Felony or Misdemeanor (Null if not a hit & run)
    injured: Number of people injured in collision
    killed: Number of people killed in collision
    hit_run_lvl: Level of violation, if collision was a hit & run
    """

    incident_df = pd.read_csv(COLLISIONS_DF_URL, parse_dates=["DATE_TIME"])
    beats_df = pd.read_csv(BEATS_DF_URL)

    # Create a mapping: index = beat, value = neighborhood
    mapping = beats_df.set_index(Column.BEAT)[Column.NEIGHBORHOOD]
    # Create the new column in df1 by mapping the 'beat' column (default to "" if not found)
    incident_df[Column.POLICE_BEAT] = (
        incident_df[Column.POLICE_BEAT].map(mapping).fillna("")
    )
    incident_df[Column.HIT_RUN_LVL] = incident_df[Column.HIT_RUN_LVL].fillna("NONE")
    incident_df[Column.DATE_TIME] = pd.to_datetime(incident_df[Column.DATE_TIME])
    return incident_df.sort_values(by=Column.DATE_TIME, ascending=False)


def filter_date(start: str, end: str, incident_df: pd.DataFrame) -> pd.DataFrame:
    """
    Filters the incident dataframe to only include incidents within the specified date range.
    Date format: 'YYYY-MM-DD'
    """
    start_date = pd.to_datetime(start)
    end_date = pd.to_datetime(end)
    return incident_df[
        (incident_df[Column.DATE_TIME] >= start_date)
        & (incident_df[Column.DATE_TIME] <= end_date)
    ]


def filter_for_casualties(incident_df: pd.DataFrame) -> pd.DataFrame:
    """
    Filters the incident dataframe to only include incidents with injuries or fatalities.
    """
    return incident_df[
        (incident_df[Column.INJURED] > 0) | (incident_df[Column.KILLED] > 0)
    ]


def paginate(df: pd.DataFrame, page: int = 1, page_size: int = 10) -> pd.DataFrame:
    """
    Paginates the dataframe.
    """
    start = (page - 1) * page_size
    end = start + page_size
    return df[start:end]


def map_date_time_to_string(date_time: pd.Timestamp) -> str:
    return date_time.strftime("%Y-%m-%d")


def map_incident_dict_to_incident_dto(incident_dicts: list[dict]) -> list[IncidentDTO]:
    incident_dtos = []
    for incident_dict in incident_dicts:
        incident_dto = IncidentDTO()
        incident_dto.report_id = incident_dict.get(Column.REPORT_ID)
        incident_dto.date_time = map_date_time_to_string(
            incident_dict.get(Column.DATE_TIME)
        )
        incident_dto.charge_desc = incident_dict.get(Column.CHARGE_DESC)
        incident_dto.injured = incident_dict.get(Column.INJURED)
        incident_dto.killed = incident_dict.get(Column.KILLED)
        incident_dto.neighborhood = incident_dict.get(Column.NEIGHBORHOOD)
        incident_dto.full_address = incident_dict.get(Column.FULL_ADDRESS)

        # Geocode the address to get lat/lng
        coords = geocode_address(incident_dto.full_address)
        if coords:
            incident_dto.latitude = coords[0]
            incident_dto.longitude = coords[1]
        else:
            incident_dto.latitude = None
            incident_dto.longitude = None

        incident_dtos.append(vars(incident_dto))
    return incident_dtos


def get_incidents_and_count(
    page: int = 1, page_size: int = 10
) -> Tuple[pd.DataFrame, int]:
    df = read_pd_csv()
    filtered_df = filter_for_casualties(df)
    df_with_addresses = parse_full_address(filtered_df)
    paginated_df = paginate(df_with_addresses, page, page_size)
    return paginated_df, len(filtered_df)


def get_incident_metadata(df: pd.DataFrame) -> IncidentMetadataDTO:
    la_tz = pytz.timezone("America/Los_Angeles")
    dto_object = IncidentMetadataDTO()
    dto_object.latest_date = df[Column.DATE_TIME].max()

    # Get current date in LA timezone
    now_la = pd.Timestamp.now(tz=la_tz).date()

    # Assume latest_date is in LA timezone (localize if naive)
    latest_date = dto_object.latest_date
    if latest_date.tzinfo is None:
        latest_date = la_tz.localize(latest_date)
    latest_date_la = latest_date.date()

    dto_object.number_of_days_since_last_incident = (now_la - latest_date_la).days
    return dto_object


def map_incident_df_to_incident_list_dto(
    df: pd.DataFrame, page: int, page_size: int, total: int
) -> IncidentListDTO:
    dto_object = IncidentListDTO()
    dto_object.incidents = map_incident_dict_to_incident_dto(
        df.to_dict(orient="records")
    )
    dto_object.page = page
    dto_object.pageSize = page_size
    dto_object.totalIncidents = total
    return dto_object


def parse_full_address(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parses the full address from the dataframe.
    """

    def construct_full_address(row):
        address = f"{row[Column.ADDRESS_PD_PRIMARY]} {row[Column.ADDRESS_ROAD_PRIMARY]} {row[Column.ADDRESS_SFX_PRIMARY]}"
        if row[Column.ADDRESS_NO_PRIMARY] > 0:
            # If there is a st number, there is no intersection
            address = f"{row[Column.ADDRESS_NO_PRIMARY]}" + " " + address
        else:
            # else use the intersecting st
            address += (
                " and "
                + f"{row[Column.ADDRESS_PD_INTERSECTING]} {row[Column.ADDRESS_NAME_INTERSECTING]} {row[Column.ADDRESS_SFX_INTERSECTING]}"
            )
        address = address + ", SAN DIEGO, CA"
        return re.sub(" +", " ", address)

    df[Column.FULL_ADDRESS] = df.apply(construct_full_address, axis=1)
    return df
