from pydantic import BaseModel

from utils.command import Motor0Gear, Motor0WorkMode, Motor1Gear, Motor1WorkMode


class SetMotor0SpeedRequest(BaseModel):

    mode: Motor0WorkMode
    value: int
    gear: Motor0Gear
    climb: int = 0
    handbrake: int = 0
    brake: int = 0
    life: int = 0


class SetMotor1SpeedRequest(BaseModel):

    mode: Motor1WorkMode
    value: int
    gear: Motor1Gear
    climb: int = 0
    handbrake: int = 0
    brake: int = 0
    life: int = 0
