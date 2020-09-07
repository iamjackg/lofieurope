import json

import flask
from flask_caching import Cache

import pathlib
import yaml

config = {"CACHE_TYPE": "simple", "CACHE_DEFAULT_TIMEOUT": 60}
app = flask.Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)


@cache.cached(key_prefix="all_data")
def get_all_country_data():
    try:
        with (pathlib.Path(app.root_path) / "countries.yml").open() as countries_fp:
            country_data = yaml.safe_load(countries_fp)
    except FileNotFoundError as e:
        return {}

    return country_data


@app.route("/api/map/countries")
def get_map_countries():
    final_data = list()

    for country_name, country_details in get_all_country_data().items():
        final_data.append(
            {
                "type": "text",
                "title": country_details["name"],
                "description": "",
                "position": {
                    "left": country_details["coordinates"][0] - 25,
                    "top": country_details["coordinates"][1] - 10,
                },
                "link": {
                    "url": flask.url_for("country_page", country_id=country_name),
                    "label": "View image",
                },
            }
        )

    return flask.jsonify(final_data)


@app.route("/api/countries/<country_id>")
def get_country_data(country_id):
    final_data = list()
    all_country_data = get_all_country_data()

    try:
        country_data = all_country_data[country_id]
    except KeyError:
        return flask.jsonify({}), 404

    for point_data in country_data["image_points"]:
        final_data.append(
            {
                "type": "text",
                "title": point_data["title"],
                "description": point_data["description"],
                "position": {
                    "left": point_data["coordinates"][0] - 25,
                    "top": point_data["coordinates"][1] - 10,
                },
            }
        )

    return flask.jsonify(final_data)


@app.route("/country")
def country_page():
    all_country_data = get_all_country_data()

    country_id = flask.request.args.get("country_id", [])
    if not country_id:
        return "", 400

    try:
        country_data = all_country_data[country_id]
    except KeyError:
        return "", 404

    return flask.render_template(
        "country.html",
        country_id=country_id,
        country_name=country_data["name"],
        image_author=country_data["image_author"],
        image_author_link=country_data["image_author_link"],
        image_file=flask.url_for(
            "static", filename=f"countries/{country_data['image_file']}"
        ),
    )


@app.route("/")
def main_page():
    return flask.render_template("index.html")


@app.route("/about")
def about_page():
    return flask.render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
