import enum
import re
import pydantic


class BountyCondition(enum.Enum):
    IS_STEEL_PATH = 0
    IS_WRONG_TIER = 1
    HAS_INCORRECT_STAGES = 2


class Bounty(pydantic.BaseModel):

    job: str
    jobTier: int
    jobStages: list[str]

    isHardJob: bool = False

    def is_steel_path(self):
        return self.isHardJob

    def __str__(self) -> str:
        stages = "\n- ".join(BOUNTIES.get(b, b) for b in self.jobStages)
        steel_path = "(Steel Path)" if self.is_steel_path() else ""
        return f"Tier {self.jobTier} Bounty {steel_path}\nStages:\n- {stages}"

    @property
    def tier(self) -> int:
        result = self.jobTier + 1
        if self.is_steel_path():
            result -= 1
        return result


BOUNTY_START = re.compile(r"\d+\.\d+ Net \[Info\]: Set squad mission: (.+)")

BOUNTIES = {
    "/Lotus/Types/Gameplay/Eidolon/Encounters/DynamicAssassinate": "Assassinate",
    "/Lotus/Types/Gameplay/Eidolon/Encounters/DynamicHijack": "Drone",
    "/Lotus/Types/Gameplay/Eidolon/Encounters/DynamicRescue": "Rescue",
    "/Lotus/Types/Gameplay/Eidolon/Encounters/DynamicExterminate": "Exterminate",
    "/Lotus/Types/Gameplay/Eidolon/Encounters/CaveEncounters/DynamicCaveExterminate": "Cave Exterminate",
    "/Lotus/Types/Gameplay/Eidolon/Encounters/HiddenResourceCaches": "Cache",
    "/Lotus/Types/Gameplay/Eidolon/Encounters/DynamicCapture": "Capture",
    "/Lotus/Types/Gameplay/Eidolon/Encounters/DynamicDefend": "Liberate the Camp",
    "/Lotus/Types/Gameplay/Eidolon/Encounters/DynamicResourceTheft": "Armored Vault",
    "/Lotus/Types/Gameplay/Eidolon/Encounters/CaveEncounters/HiddenResourceCachesCave": "Cave Cache",
    "/Lotus/Types/Gameplay/Eidolon/Encounters/DynamicSabotage": "Sabotage",
}
