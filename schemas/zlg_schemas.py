from ast import alias
from pydantic import BaseModel, Field


class OpenDeviceRequest(BaseModel):
    device_type: int = Field(..., alias="deviceType")
    device_index: int = Field(..., alias="deviceIndex")


class OpenChannelRequest(BaseModel):
    chn: int
    baud_rate: int = Field(default=250000, alias="baudRate")
    can_type: int = Field(default=0, alias="canType")


class SendMessageRequest(BaseModel):
    chn: int
    datas: dict[int, list[int]]
    eff: int = 1
    transmit_type: int = Field(default=0, alias="transmitType")


class AutoSendMessageRequest(BaseModel):
    chn: int
    motor_id: int = Field(default=0, alias="motorId")
    datas: dict[int, list[int]]
    eff: int = 1
    transmit_type: int = Field(default=0, alias="transmitType")
    interval: int = 50


class MotorRequest(BaseModel):
    chn: int
    motor_id: int = Field(default=0, alias="motorId")
