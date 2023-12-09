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
class AttractionDetails:
    name: str
    type: str = None
    subtype: str = None
    post_code: str = None
    rating: float = None
    image_link_1: str = None
    image_link_2: str = None
    id: int = None
    description: str = None
    duration: int = None

    @classmethod
    def from_details_query(cls, data: tuple) -> "AttractionDetails":
        return cls(
            name=data[1],
            type=data[2],
            subtype=data[3],
            description=data[4],
            post_code=data[5],
            rating=data[6],
            image_link_1=data[7],
            image_link_2=data[8]
        )

    @classmethod
    def from_api_data(cls, query_data: list, api_response):
        return cls(
            id=query_data[2],
            name=query_data[0],
            subtype=query_data[3] if query_data[3] else 'restaurant',
            image_link_1=query_data[4],
            image_link_2=query_data[5],
            duration=api_response.json()['journeys'][0]['duration']
        )

    def get_dict(self) -> dict:
        dict_rep = {}
        if self.id:
            dict_rep['id'] = self.id
        if self.type:
            dict_rep['type'] = self.type
        if self.description:
            dict_rep['description'] = self.description
        if self.post_code:
            dict_rep['post_code'] = self.post_code
        if self.rating:
            dict_rep['rating'] = self.rating
        if self.duration:
            dict_rep['duration'] = self.duration
        dict_rep['name'] = self.name
        dict_rep['subtype'] = self.subtype
        dict_rep['image_link_1'] = self.image_link_1
        dict_rep['image_link_2'] = self.image_link_2
        return dict_rep


@dataclass
class RouteDetails:
    duration: int
    legs: list

    @classmethod
    def from_api_response(cls, data: dict) -> "RouteDetails":
        return cls(
            duration=data["duration"],
            legs=[{
                "duration": leg["duration"],
                "summary": leg["instruction"]["summary"],
                "steps": [
                    step["descriptionHeading"] + step["description"]
                    for step in leg["instruction"]["steps"]
                ],
                "arrivalPoint": leg["arrivalPoint"]["commonName"],
                "path": [stop["name"] for stop in leg["path"]["stopPoints"]],
            } for leg in data["legs"]]
        )
