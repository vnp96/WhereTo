from dataclasses import dataclass


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
    type: str
    subtype: str
    description: str
    post_code: str
    rating: float
    image_link_1: str
    image_link_2: str

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
