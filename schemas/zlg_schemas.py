from pydantic import BaseModel


class OpenDeviceRequest(BaseModel):
    device_type: int
    device_index: int

class OpenChannelRequest(BaseModel):
    chn: int
    baud_rate: str | int = "250000"
    can_type: int = 0

class SendMessageRequest(BaseModel):
    chn: int
    datas: dict[int, list[int]]
    eff: int = 1
    transmit_type: int = 0

class AutoSendMessageRequest(BaseModel):
    chn: int
    datas: dict[int, list[int]]
    eff: int = 1
    transmit_type: int = 0
    interval: int = 50

class ChannelRequest(BaseModel):
    chn: int