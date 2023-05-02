from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
import jsonschema
import googlemaps
from enum import Enum
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


class TransportMode(str, Enum):
    driving = "driving"
    walking = "walking"
    bicycling = "bicycling"
    transit = "transit"


class TransitMode(str, Enum):
    bus = "bus"
    subway = "subway"
    train = "train"
    tram = "tram"
    rail = "rail"


gmaps = googlemaps.Client(key=GMAP_API_KEY)
# Define the schemas
placesSearchSchema = {
    "type": "object",
    "properties": {
        "search_text": {"type": "string", "minLength": 3, "maxLength": 50},
    },
    "required": ["search_text"],
}
directionsSearchSchema = {
    "type": "object",
    "properties": {
        "origin_place_id": {"type": "string", "minLength": 3},
        "destination_place_id": {"type": "string", "minLength": 3},
        "mode": {"type": "string", "enum": [mode.value for mode in TransportMode]},
        "transit_mode": {"type": "array", "items": {"type": "string", "enum": [mode.value for mode in TransitMode]}},
    },
    "required": ["origin_place_id", "destination_place_id", "mode"],
}
geocodingSearchSchema = {
    "type": "object",
    "properties": {
        "place_id": {"type": "string", "minLength": 3},
    },
    "required": ["place_id"],
}


class APIType(str, Enum):
    placeSearch = "places"
    geocodingSearch = "geocoding"
    directionsSearch = "directions"


app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def transit_mode_list_to_string(transit_mode_list: list[str]) -> str:
    return "|".join(transit_mode_list)


class Validator:
    def __init__(self):
        self.schemas = {
            APIType.placeSearch: placesSearchSchema,
            APIType.geocodingSearch: geocodingSearchSchema,
            APIType.directionsSearch: directionsSearchSchema,
        }

    def validate(self, api_type: APIType, data: dict):
        jsonschema.validate(data, self.schemas[api_type])


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def handle_places_search(self, message: dict, session_id: str, websocket: WebSocket):

        places_result = gmaps.places_autocomplete(
            input_text=message["search_text"], session_token=session_id, components={"country": "IE"}, language="en")
        print(places_result)
        await websocket.send_json(places_result)

    async def handle_geocoding_search(self, message: dict,  websocket: WebSocket):
        geocode_result = gmaps.geocode(
            place_id=message["place_id"], components={"country": "IE"}, language="en")

        await websocket.send_json(geocode_result)

    async def handle_directions_search(self, message: dict, websocket: WebSocket):
        directions_result = gmaps.directions(
            origin=f"place_id:{message['origin_place_id']}",
            destination=f"place_id:{message['destination_place_id']}",
            alternatives=True, units="metric",
            mode=message["mode"],
            transit_mode=transit_mode_list_to_string(
                message["transit_mode"]) if ("transit_mode" in message and message["mode"] == TransportMode.transit) else None,
            language="en")

        await websocket.send_json(directions_result)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


manager = ConnectionManager()


@ app.websocket("/{api_type}/{session_id}")
async def websocket_endpoint(websocket: WebSocket, api_type: APIType, session_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Validate the data
            json_data = None

            validator = Validator()

            try:
                json_data = json.loads(data)
                validator.validate(api_type, json_data)
            except jsonschema.exceptions.ValidationError as err:
                await manager.send_personal_message(f"Error: {err}", websocket)
                continue

            if api_type == APIType.placeSearch:
                await manager.handle_places_search(json_data, session_id, websocket)
            elif api_type == APIType.geocodingSearch:
                await manager.handle_geocoding_search(json_data, websocket)
            elif api_type == APIType.directionsSearch:
                await manager.handle_directions_search(json_data, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)


class ShortestPathProps(BaseModel):
    from_point: list[float]
    to_point: list[float]

# waypoints=via:enc:wc~oAwquwMdlTxiKtqLyiK:|enc:c~vnAamswMvlTor@tjGi}L:| via:enc:udymA{~bxM:
# I get a list of polyline strings from the client


def get_waypoints_from_polyline(polylines: list[str]) -> str:
    # Don't insert | at the end
    return "|".join([f"via:enc:{polyline}:" for polyline in polylines])


@app.post("/shortest_route/")
async def shortest_route(props: ShortestPathProps):
    props_json = json.loads(props.json())

    directions_result = gmaps.directions(
        origin=f"{props_json['from_point'][1]}," f"{props_json['to_point'][0]}",
        destination=f"{props_json['to_point'][1]}," f"{props_json['to_point'][0]}",
        alternatives=True, units="metric",
        mode=TransportMode.driving,
        language="en")

    return directions_result
