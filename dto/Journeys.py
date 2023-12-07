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
