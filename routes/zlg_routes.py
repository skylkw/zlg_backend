import asyncio
from fastapi import APIRouter, Depends
from schemas import StatusResponse
from schemas.zlg_schemas import (
    AutoSendMessageRequest,
    ChannelRequest,
    OpenChannelRequest,
    OpenDeviceRequest,
    SendMessageRequest,
)
from zlg.zlgcan import ZCAN_DEVICE_TYPE, ZCAN_TYPE_CAN, ZCAN_TYPE_CANFD
from dependencies import get_zlg_can_manager
from zlg.manager import ZLGCanManager

router = APIRouter()


@router.post("/open_device")
async def open_device(
    request: OpenDeviceRequest,
    zlg_can_manager: ZLGCanManager = Depends(get_zlg_can_manager),
):
    """
    打开设备。

    :param request: 包含设备类型和设备索引的请求。
    :param zlg_can_manager: ZLGCanManager 实例。
    :return: 设备打开的结果。
    """
    device_type = ZCAN_DEVICE_TYPE(request.device_type)
    return await zlg_can_manager.open_device(device_type, request.device_index)


@router.post("/open_channel")
async def open_channel(
    request: OpenChannelRequest,
    zlg_can_manager: ZLGCanManager = Depends(get_zlg_can_manager),
):
    """
    打开通道。

    :param request: 包含通道号、波特率和CAN类型的请求。
    :param zlg_can_manager: ZLGCanManager 实例。
    :return: 通道打开的结果。
    """
    can_type = ZCAN_TYPE_CAN if request.can_type == 0 else ZCAN_TYPE_CANFD
    return await zlg_can_manager.open_channel(request.chn, request.baud_rate, can_type)


@router.post("/send_message")
async def send_message(
    request: SendMessageRequest,
    zlg_can_manager: ZLGCanManager = Depends(get_zlg_can_manager),
):
    """
    发送消息到指定通道。

    :param request: 包含通道号、数据、EFF标志和发送类型的请求。
    :param zlg_can_manager: ZLGCanManager 实例。
    :return: 消息发送的结果。
    """
    return await zlg_can_manager.send_message(
        request.chn, request.datas, request.eff, request.transmit_type
    )


@router.post("/start_auto_send_message")
async def start_auto_send_message(
    request: AutoSendMessageRequest,
    zlg_can_manager: ZLGCanManager = Depends(get_zlg_can_manager),
):
    """
    启动自动发送消息任务。

    :param request: 包含通道号、数据和发送间隔的请求。
    :param zlg_can_manager: ZLGCanManager 实例。
    :return: 自动发送任务启动的状态响应。
    """
    # 停止已存在的自动发送任务（如果有）
    await zlg_can_manager.stop_auto_send_message(request.chn)
    # 启动新的自动发送任务
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
    """
    停止自动发送消息任务。

    :param request: 包含通道号的请求。
    :param zlg_can_manager: ZLGCanManager 实例。
    :return: 自动发送任务停止的结果。
    """
    return await zlg_can_manager.stop_auto_send_message(request.chn)


@router.post("/start_receive_message")
async def start_receive_message(
    request: ChannelRequest,
    zlg_can_manager: ZLGCanManager = Depends(get_zlg_can_manager),
):
    """
    启动接收消息任务。

    :param request: 包含通道号的请求。
    :param zlg_can_manager: ZLGCanManager 实例。
    :return: 接收任务启动的状态响应。
    """
    # 停止已存在的接收任务（如果有）
    await zlg_can_manager.stop_receive_message(request.chn)
    # 启动新的接收任务
    asyncio.create_task(zlg_can_manager.start_receive_message(request.chn))
    return StatusResponse(status="success", message="接收任务启动成功")


@router.post("/stop_receive_message")
async def stop_receive_message(
    request: ChannelRequest,
    zlg_can_manager: ZLGCanManager = Depends(get_zlg_can_manager),
):
    """
    停止接收消息任务。

    :param request: 包含通道号的请求。
    :param zlg_can_manager: ZLGCanManager 实例。
    :return: 接收任务停止的结果。
    """
    return await zlg_can_manager.stop_receive_message(request.chn)


@router.post("/close_channel")
async def close_channel(
    request: ChannelRequest,
    zlg_can_manager: ZLGCanManager = Depends(get_zlg_can_manager),
):
    """
    关闭指定通道。

    :param request: 包含通道号的请求。
    :param zlg_can_manager: ZLGCanManager 实例。
    :return: 通道关闭的结果。
    """
    return await zlg_can_manager.close_channel(request.chn)


@router.post("/close_device")
async def close_device(
    zlg_can_manager: ZLGCanManager = Depends(get_zlg_can_manager),
):
    """
    关闭设备。

    :param zlg_can_manager: ZLGCanManager 实例。
    :return: 设备关闭的结果。
    """
    return await zlg_can_manager.close_device()
