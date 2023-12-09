from dataclasses import dataclass, asdict


@dataclass
class JourneyLegInfo:
    duration: float
    instruction: str


@dataclass
class JourneyInfo:
    duration: float
    legs: list

    @classmethod
    def from_dict(cls, data: dict) -> "JourneyInfo":
        return cls(
            duration=data["journeys"][0]["duration"],
            legs=[
                JourneyLegInfo(leg["duration"], leg["instruction"]["summary"])
                for leg in data["journeys"][0]["legs"]
            ],
        )


@dataclass
class TflJourneyResponse:
    response_code: int
    duration: int = None
    legs: list = None

    @classmethod
    def from_api_response(cls, response) -> "TflJourneyResponse":
        if response.status_code == 200:
            data = response.json()["journeys"][0]
            return cls(
                response_code=response.status_code,
                duration=data["duration"],
                legs=[{
                    "duration": leg["duration"],
                    "summary": leg["instruction"]["summary"],
                    "steps": [
                        step["descriptionHeading"] + step["description"]
                        for step in leg["instruction"]["steps"]
                    ],
                    "arrivalPoint": leg["arrivalPoint"]["commonName"],
                    "path": [stop["name"] for stop in
                             leg["path"]["stopPoints"]],
                } for leg in data["legs"]]
            )
        else:
            return cls(
                response_code=response.status_code
            )

    @classmethod
    def same_location(cls, postcode) -> "TflJourneyResponse":
        return cls(
            response_code=200,
            duration=0,
            legs=[{
                "duration": 0,
                "summary": "You are already there!",
                "steps": [],
                "arrivalPoint": postcode,
                "path": [],
            }]
        )

    def get_dict(self):
        return asdict(self)


@dataclass
class AttractionDetails:
    name: str
    type: str
    subtype: str
    post_code: str
    rating: float
    image_link_1: str
    image_link_2: str
    id: int
    description: str
    response_code: int = None
    duration: int = None

    @classmethod
    def from_details_query(cls, data: tuple) -> "AttractionDetails":
        return cls(
            id=data[0],
            name=data[1],
            type=data[2],
            subtype=data[3],
            description=data[4],
            post_code=data[5],
            rating=data[6],
            image_link_1=data[7],
            image_link_2=data[8]
        )

    def add_api_response(self, api_response: dict):
        self.response_code = api_response["response_code"]
        if self.response_code == 200:
            self.duration = api_response["duration"]

    def get_dict(self) -> dict:
        dict_rep = asdict(self)
        if self.response_code is None:
            del dict_rep['response_code']
        if self.duration is None:
            del dict_rep['duration']
        return dict_rep


