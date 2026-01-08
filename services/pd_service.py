import pandas as pd


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


def get_incidents(page: int = 1, page_size: int = 10) -> pd.DataFrame:
    df = read_pd_csv()
    filtered_df = filter_for_casualties(df)
    paginated_df = paginate(filtered_df, page, page_size)
    return paginated_df.to_json(orient="records")
