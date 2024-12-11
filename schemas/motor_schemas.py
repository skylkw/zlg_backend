from pydantic import BaseModel, Field

from utils.command import MotorGear, MotorWorkMode


class SetMotorSettingsRequest(BaseModel):

    mode: MotorWorkMode
    value: int
    gear: MotorGear
    climb: int = 0
    hand_brake: int =  Field(default=0, alias="handBrake")
    foot_brake: int = Field(default=0, alias="footBrake")
    life: int = 0


