import re
from typing import Tuple
import pandas as pd

from entity.Incident import IncidentDTO, IncidentListDTO, IncidentMetadataDTO
from services.geocoding_service import geocode_address


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
    incident_source = (
        "https://seshat.datasd.org/traffic_collisions/pd_collisions_datasd.csv"
    )
    incident_df = pd.read_csv(incident_source, parse_dates=["date_time"])
    beats_df = pd.read_csv(
        "https://seshat.datasd.org/gis_police_beats/pd_beat_codes_list_datasd.csv"
    )

    # Create a mapping: index = beat, value = neighborhood
    mapping = beats_df.set_index("beat")["neighborhood"]
    # Create the new column in df1 by mapping the 'beat' column
    incident_df["neighborhood"] = incident_df["police_beat"].map(mapping)
    incident_df["hit_run_lvl"] = incident_df["hit_run_lvl"].fillna("NONE")
    incident_df["date_time"] = pd.to_datetime(incident_df["date_time"])
    return incident_df.sort_values(by="date_time", ascending=False)


def filter_for_casualties(incident_df: pd.DataFrame) -> pd.DataFrame:
    """
    Filters the incident dataframe to only include incidents with injuries or fatalities.
    """
    return incident_df[(incident_df["injured"] > 0) | (incident_df["killed"] > 0)]


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
        incident_dto.report_id = incident_dict.get("report_id")
        incident_dto.date_time = map_date_time_to_string(incident_dict.get("date_time"))
        incident_dto.police_beat = incident_dict.get("police_beat")
        incident_dto.address_no_primary = incident_dict.get("address_no_primary")
        incident_dto.address_pd_primary = incident_dict.get("address_pd_primary")
        incident_dto.address_road_primary = incident_dict.get("address_road_primary")
        incident_dto.address_sfx_primary = incident_dict.get("address_sfx_primary")
        incident_dto.address_pd_intersecting = incident_dict.get(
            "address_pd_intersecting"
        )
        incident_dto.address_name_intersecting = incident_dict.get(
            "address_name_intersecting"
        )
        incident_dto.address_sfx_intersecting = incident_dict.get(
            "address_sfx_intersecting"
        )
        incident_dto.violation_section = incident_dict.get("violation_section")
        incident_dto.violation_type = incident_dict.get("violation_type")
        incident_dto.charge_desc = incident_dict.get("charge_desc")
        incident_dto.injured = incident_dict.get("injured")
        incident_dto.killed = incident_dict.get("killed")
        incident_dto.hit_run_lvl = incident_dict.get("hit_run_lvl")
        incident_dto.neighborhood = incident_dict.get("neighborhood")
        incident_dto.full_address = incident_dict.get("full_address")

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
    dto_object = IncidentMetadataDTO()
    dto_object.latest_date = df["date_time"].max()
    dto_object.number_of_days_since_last_incident = (
        pd.Timestamp.now().date() - dto_object.latest_date.date()
    ).days
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
        address = f"{row['address_pd_primary']} {row['address_road_primary']} {row['address_sfx_primary']}"
        if row["address_no_primary"] > 0:
            # If there is a st number, there is no intersection
            address = f"{row['address_no_primary']}" + " " + address
        else:
            # else use the intersecting st
            address += (
                " and "
                + f"{row['address_pd_intersecting']} {row['address_name_intersecting']} {row['address_sfx_intersecting']}"
            )
        address = address + ", SAN DIEGO, CA"
        return re.sub(" +", " ", address)

    df["full_address"] = df.apply(construct_full_address, axis=1)
    return df
