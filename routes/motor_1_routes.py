import asyncio
from fastapi import APIRouter, Depends
from utils.parsing import parse_motor_1
from schemas.motor_schemas import SetMotorSettingsRequest
from schemas import StatusResponse
from utils.command import Motor1Command
from dependencies import get_motor_1_command, get_zlg_can_manager
from zlg.manager import ZLGCanManager

router = APIRouter()


@router.post("/enable_motor_1", response_model=StatusResponse)
async def enable_motor_1(
    zlg_can_manager: ZLGCanManager = Depends(get_zlg_can_manager),
    motor_1_command: Motor1Command = Depends(get_motor_1_command),
):
    # 停止之前的自动发送和接收任务
    await zlg_can_manager.stop_auto_send_message(motor_1_command.chn)
    await zlg_can_manager.stop_receive_message(motor_1_command.chn)

    # 注册解析函数
    zlg_can_manager.register_parse_function(motor_1_command.chn, parse_motor_1)
    datas = motor_1_command.enable_motor()

    # 启动新的自动发送任务前进行检查
    zlg_can_manager.can_start_auto_send(motor_1_command.chn)

    # 启动新的接收任务前进行检查
    zlg_can_manager.can_start_receive(motor_1_command.chn)

    # 启动自动发送和接收任务
    asyncio.create_task(
        zlg_can_manager.start_auto_send_message(motor_1_command.chn, datas, interval=20)
    )
    asyncio.create_task(zlg_can_manager.start_receive_message(motor_1_command.chn))

    return StatusResponse(status="success", message="电机 1 使能成功")


@router.post("/disable_motor_1", response_model=StatusResponse)
async def disable_motor_1(
    zlg_can_manager: ZLGCanManager = Depends(get_zlg_can_manager),
    motor_1_command: Motor1Command = Depends(get_motor_1_command),
):
    await zlg_can_manager.send_message(motor_1_command.chn, motor_1_command.disable_motor())
    await zlg_can_manager.stop_receive_message(motor_1_command.chn)
    await zlg_can_manager.stop_auto_send_message(motor_1_command.chn)
    return StatusResponse(status="success", message="电机 1 失能成功")


@router.post("/set_motor_1_settings", response_model=StatusResponse)
async def set_motor_1_settings(
    request: SetMotorSettingsRequest,
    zlg_can_manager: ZLGCanManager = Depends(get_zlg_can_manager),
    motor_1_command: Motor1Command = Depends(get_motor_1_command),
):
    # 停止之前的自动发送任务
    await zlg_can_manager.stop_auto_send_message(motor_1_command.chn)

    # 设置电机参数
    datas = motor_1_command.set_motor_settings(
        request.mode, request.value, request.gear
    )

    # 启动新的自动发送任务前进行检查
    zlg_can_manager.can_start_auto_send(motor_1_command.chn)

    # 启动新的自动发送任务
    asyncio.create_task(
        zlg_can_manager.start_auto_send_message(motor_1_command.chn, datas, interval=20)
    )

    return StatusResponse(status="success", message="电机 1 速度设置成功")
