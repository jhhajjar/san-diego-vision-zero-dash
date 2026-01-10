import os
from services.aws_service import read_file_s3
from services.pd_service import (
    get_incident_metadata,
    get_incidents,
    map_incident_df_to_incident_list_dto,
    read_pd_csv,
    filter_for_casualties,
)
from flask_cors import CORS
from dotenv import load_dotenv
from flask import Flask, jsonify, request

app = Flask(__name__)
CORS(app)
load_dotenv()


@app.route("/articles")
def articles():
    # fetch df
    df = read_file_s3(os.getenv("S3_ARTICLES_FILENAME"))
    # filter out non relevant articles
    df = df[df["is_relevant"]]
    # sort by date
    df = df.sort_values(by="date_posted", ascending=False)
    return df.to_json(orient="records")


@app.route("/incidents")
def incidents():
    # Parse pagination parameters
    page = request.args.get("page", default=1, type=int)
    page_size = request.args.get("page_size", default=10, type=int)

    # Fetch paginated incidents
    incidents_df = get_incidents(page=page, page_size=page_size)

    # Map to DTO
    mapped_response = map_incident_df_to_incident_list_dto(
        incidents_df, page, page_size
    )

    return jsonify(vars(mapped_response)), 200


@app.route("/incidents/metadata")
def incident_metadata():
    df = read_pd_csv()
    filtered_df = filter_for_casualties(df)
    metadata = get_incident_metadata(filtered_df)
    return jsonify(vars(metadata)), 200
