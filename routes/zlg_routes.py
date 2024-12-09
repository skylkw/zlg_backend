from fastapi import APIRouter, Depends
import asyncio
from schemas import StatusResponse
from schemas.zlg_schemas import (
    AutoSendMessageRequest,
    ChannelRequest,
    OpenChannelRequest,
    OpenDeviceRequest,
    SendMessageRequest,
)
from zlg.manager import ZLGCanManager
from dependencies import get_zlg_can_manager

router = APIRouter()


@router.post("/open_device")
async def open_device(
    request: OpenDeviceRequest,
    zlg_can_manager: ZLGCanManager = Depends(get_zlg_can_manager),
):
    return await zlg_can_manager.open_device(request.device_type, request.device_index)


@router.post("/close_device")
async def close_device(zlg_can_manager: ZLGCanManager = Depends(get_zlg_can_manager)):
    return await zlg_can_manager.close_device()


@router.post("/open_channel")
async def open_channel(
    request: OpenChannelRequest,
    zlg_can_manager: ZLGCanManager = Depends(get_zlg_can_manager),
):
    can_type = ZCAN_TYPE_CANFD if request.can_type else ZCAN_TYPE_CAN
    return await zlg_can_manager.open_channel(request.chn, request.baud_rate, can_type)


@router.post("/close_channel")
async def close_channel(
    request: ChannelRequest,
    zlg_can_manager: ZLGCanManager = Depends(get_zlg_can_manager),
):
    return await zlg_can_manager.close_channel(request.chn)


@router.post("/send_message")
async def send_message(
    request: SendMessageRequest,
    zlg_can_manager: ZLGCanManager = Depends(get_zlg_can_manager),
):
    return await zlg_can_manager.send_message(
        request.chn, request.datas, request.eff, request.transmit_type
    )


@router.post("/start_auto_send_message")
async def start_auto_send_message(
    request: AutoSendMessageRequest,
    zlg_can_manager: ZLGCanManager = Depends(get_zlg_can_manager),
):
    asyncio.create_task(
        zlg_can_manager.start_auto_send_message(
            request.chn, request.datas, request.interval
        )
    )
    return StatusResponse(status="success", message="自动发送任务启动成功")


@router.post("/stop_auto_send_message")
async def stop_auto_send_message(
    request: ChannelRequest,
    zlg_can_manager: ZLGCanManager = Depends(get_zlg_can_manager),
):
    return await zlg_can_manager.stop_auto_send_message(request.chn)


@router.post("/start_receive_message")
async def start_receive_message(
    request: ChannelRequest,
    zlg_can_manager: ZLGCanManager = Depends(get_zlg_can_manager),
):
    asyncio.create_task(zlg_can_manager.start_receive_message(request.chn))
    return StatusResponse(status="success", message="接收任务启动成功")


@router.post("/stop_receive_message")
async def stop_receive_message(
    request: ChannelRequest,
    zlg_can_manager: ZLGCanManager = Depends(get_zlg_can_manager),
):
    return await zlg_can_manager.stop_receive_message(request.chn)
