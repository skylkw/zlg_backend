import asyncio
from fastapi import APIRouter, Depends
from schemas import StatusResponse
from utils.parsing import parse_motor_0
from schemas.motor_schemas import SetMotorSettingsRequest

from utils.command import Motor0Command
from dependencies import get_motor_0_command, get_zlg_can_manager
from zlg.manager import ZLGCanManager

router = APIRouter()


@router.post("/enable_motor_0", response_model=StatusResponse)
async def enable_motor_0(
    zlg_can_manager: ZLGCanManager = Depends(get_zlg_can_manager),
    motor_0_command: Motor0Command = Depends(get_motor_0_command),
):
    # 停止之前的自动发送和接收任务
    await zlg_can_manager.stop_auto_send_message(
        motor_0_command.chn, motor_0_command.id
    )
    await zlg_can_manager.stop_receive_message(motor_0_command.chn)

    # 注册电机
    zlg_can_manager.register_motor(
        motor_0_command.chn, motor_0_command.id, parse_motor_0
    )
    datas = motor_0_command.enable_motor()

    # 启动新的自动发送任务前进行检查
    zlg_can_manager.can_start_auto_send(motor_0_command.chn, motor_0_command.id)

    # 启动新的接收任务前进行检查
    zlg_can_manager.can_start_receive(motor_0_command.chn)

    # 启动自动发送和接收任务
    asyncio.create_task(
        zlg_can_manager.start_auto_send_message(
            motor_0_command.chn, motor_0_command.id, datas, interval=20
        )
    )
    asyncio.create_task(zlg_can_manager.start_receive_message(motor_0_command.chn))

    return StatusResponse(status="success", message="电机 0 使能成功")


@router.post("/disable_motor_0", response_model=StatusResponse)
async def disable_motor_0(
    zlg_can_manager: ZLGCanManager = Depends(get_zlg_can_manager),
    motor_0_command: Motor0Command = Depends(get_motor_0_command),
):
    await zlg_can_manager.send_message(
        motor_0_command.chn, motor_0_command.disable_motor()
    )
    zlg_can_manager.unregister_motor(motor_0_command.chn, motor_0_command.id)
    await zlg_can_manager.stop_auto_send_message(motor_0_command.chn, motor_0_command.id)
    return StatusResponse(status="success", message="电机 0 失能成功")


@router.post("/set_motor_0_settings", response_model=StatusResponse)
async def set_motor_0_settings(
    request: SetMotorSettingsRequest,
    zlg_can_manager: ZLGCanManager = Depends(get_zlg_can_manager),
    motor_0_command: Motor0Command = Depends(get_motor_0_command),
):
    # 停止之前的自动发送任务
    await zlg_can_manager.stop_auto_send_message(motor_0_command.chn, motor_0_command.id)

    # 设置电机参数
    datas = motor_0_command.set_motor_settings(
        request.mode, request.value, request.gear, request.climb, request.hand_brake
    )

    # 启动新的自动发送任务前进行检查
    zlg_can_manager.can_start_auto_send(motor_0_command.chn, motor_0_command.id)

    # 启动新的自动发送任务
    asyncio.create_task(
        zlg_can_manager.start_auto_send_message(motor_0_command.chn,motor_0_command.id, datas, interval=20)
    )

    return StatusResponse(status="success", message="电机 0 速度设置成功")
