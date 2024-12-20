import asyncio
from concurrent.futures import ThreadPoolExecutor
from tkinter import NO
from typing import Callable, Dict, Any, Optional
from ctypes import c_uint
from utils.logger import logger

from fastapi import HTTPException
from schemas import StatusResponse
from zlg.zlgcan import (
    INVALID_DEVICE_HANDLE,
    ZCAN,
    ZCAN_CHANNEL_INIT_CONFIG,
    ZCAN_DEVICE_TYPE,
    ZCAN_STATUS_OK,
    ZCAN_TYPE_CAN,
    ZCAN_Receive_Data,
    ZCAN_Transmit_Data,
)


class ZLGCanManager:
    def __init__(self, dll_path: str, max_workers: int = 10):
        """
        初始化 ZLGCanManager 实例。

        :param dll_path: DLL 文件路径。
        :param max_workers: 线程池的最大工作线程数。
        """
        self.executor = ThreadPoolExecutor(max_workers)
        self.zcan = ZCAN(dll_path)
        self.device_handle = INVALID_DEVICE_HANDLE
        self.chn_handles: Dict[int, Any] = {}
        # 格式: {channel_id: {motor_id: asyncio.Queue}}
        self.queues: Dict[int, Dict[int, asyncio.Queue]] = {}
        # 格式: {channel_id: {motor_id: parse_func}}
        self.parse_functions: Dict[int, Dict[int, Callable]] = {}
        # 格式: {channel_id: {motor_id: asyncio.Task}}
        self.auto_send_tasks: Dict[int, Dict[int, asyncio.Task]] = {}
        # 格式: {channel_id: asyncio.Task}
        self.receive_tasks: Dict[int, asyncio.Task] = {}
        logger.info("初始化 ZLGCanManager 实例")

    def register_motor(self, chn: int, motor_id: int, parse_func: Callable) -> None:
        """
        注册电机。

        :param chn: 通道号。
        :param motor_id: 电机 ID。
        :param parse_func: 解析函数。
        """
        self.parse_functions[chn][motor_id] = parse_func
        self.queues[chn][motor_id] = asyncio.Queue()
        logger.info(f"注册解析函数：通道 {chn}, 电机 {motor_id}")

    def unregister_motor(self, chn: int, motor_id: int) -> None:
        """
        注销电机。

        :param chn: 通道号。
        :param motor_id: 电机 ID。
        """
        self.parse_functions[chn].pop(motor_id, None)
        self.queues[chn].pop(motor_id, None)
        logger.info(f"注销解析函数：通道 {chn}, 电机 {motor_id}")

    async def open_device(
        self, device_type: ZCAN_DEVICE_TYPE, device_index: int
    ) -> StatusResponse:
        """
        打开设备。

        :param device_type: 设备类型。
        :param device_index: 设备索引。
        :return: StatusResponse 对象。
        """
        self.device_handle = self.zcan.OpenDevice(device_type, device_index, 0)

        if self.device_handle == INVALID_DEVICE_HANDLE:
            logger.error("打开设备失败")
            raise HTTPException(status_code=500, detail="打开设备失败")
        logger.info("打开设备成功")
        return StatusResponse(status="success", message="打开设备成功")

    async def get_device_info(self) -> StatusResponse:
        """
        获取设备信息。

        :return: StatusResponse 对象，包含设备信息。
        """
        if self.device_handle == INVALID_DEVICE_HANDLE:
            logger.error("设备未打开")
            raise HTTPException(status_code=400, detail="设备未打开")

        device_info = self.zcan.GetDeviceInf(self.device_handle)
        if device_info is None:
            logger.error("获取设备信息失败")
            raise HTTPException(status_code=500, detail="获取设备信息失败")

        # 将设备信息转换为字典
        device_info_dict = {
            "hw_version": device_info.hw_Version,
            "fw_version": device_info.fw_Version,
            "dr_version": device_info.dr_Version,
            "in_version": device_info.in_Version,
            "irq_num": device_info.irq_Num,
            "can_num": device_info.can_Num,
            "serial": "".join(map(chr, device_info.str_Serial_Num)).strip("\x00"),
            "hw_type": "".join(map(chr, device_info.str_hw_Type)).strip("\x00"),
        }

        logger.info("获取设备信息成功")
        return StatusResponse(
            status="success", message="获取设备信息成功", data=device_info_dict
        )

    async def open_channel(
        self,
        chn: int,
        baud_rate: str | int = "250000",
        can_type: c_uint = ZCAN_TYPE_CAN,
    ) -> StatusResponse:
        """
        打开通道。

        :param chn: 通道号。
        :param baud_rate: 波特率。
        :param can_type: CAN 类型。
        :return: StatusResponse 对象。
        """
        ret = self.zcan.ZCAN_SetValue(
            self.device_handle, f"{chn}/baud_rate", str(baud_rate).encode("utf-8")
        )
        if ret != ZCAN_STATUS_OK:
            logger.error(f"设置通道 {chn} 波特率失败")
            raise HTTPException(status_code=500, detail=f"设置通道 {chn} 波特率失败")

        chn_init_cfg = ZCAN_CHANNEL_INIT_CONFIG()
        chn_init_cfg.can_type = can_type
        chn_init_cfg.config.can.acc_code = 0
        chn_init_cfg.config.can.acc_mask = 0xFFFFFFFF
        chn_init_cfg.config.can.mode = 0

        chh_handle = self.zcan.InitCAN(self.device_handle, chn, chn_init_cfg)
        if chh_handle == INVALID_DEVICE_HANDLE:
            logger.error(f"初始化通道 {chn} 失败")
            raise HTTPException(status_code=500, detail=f"初始化通道 {chn} 失败")

        ret = self.zcan.StartCAN(chh_handle)
        if ret != ZCAN_STATUS_OK:
            logger.error(f"启动通道 {chn} 失败")
            raise HTTPException(status_code=500, detail=f"启动通道 {chn} 失败")
        self.chn_handles[chn] = chh_handle
        logger.info(f"通道 {chn} 启动成功")
        return StatusResponse(status="success", message=f"通道 {chn} 启动成功")

    async def send_message(
        self,
        chn: int,
        datas: Dict[int, list[int]],
        eff: int = 0,
        transmit_type: int = 0,
    ) -> StatusResponse:
        """
        发送消息。

        :param chn: 通道号。
        :param datas: 发送的数据，key 为 ID，value 为数据列表。
        :param eff: 是否为扩展帧，0 为标准帧，1 为扩展帧。
        :param transmit_type: 发送类型，0 为正常发送，1 为单次发送，2 为自发自收。
        :return: StatusResponse 对象。
        """
        try:
            transmit_num = len(datas)
            msgs = (ZCAN_Transmit_Data * transmit_num)()
            for i, (msg_id, data) in enumerate(datas.items()):
                msgs[i].transmit_type = transmit_type
                msgs[i].frame.can_id = msg_id
                msgs[i].frame.can_dlc = len(data)
                msgs[i].frame.eff = eff

                for j, byte in enumerate(data):
                    msgs[i].frame.data[j] = byte

            loop = asyncio.get_running_loop()
            ret = await loop.run_in_executor(
                self.executor,
                self.zcan.Transmit,
                self.chn_handles.get(chn),
                msgs,
                transmit_num,
            )

            if ret != transmit_num:
                logger.error("发送失败")
                raise HTTPException(status_code=500, detail="发送失败")
            logger.info(f"发送成功：通道 {chn}, 数据 {datas}")
            return StatusResponse(status="success", message="发送成功")
        except Exception as e:
            logger.error(f"发送消息时出现错误：{e}")
            raise HTTPException(status_code=500, detail=f"发送失败：{e}")

    def can_start_auto_send(self, chn: int, motor_id: int) -> None:
        """
        检查是否可以启动自动发送任务。

        :param chn: 通道号。
        :param motor_id: 电机 ID。
        :raises HTTPException: 如果任务已在运行或通道未打开。
        """
        # 判断当前电机是否已经在运行自动发送任务
        if chn in self.auto_send_tasks and motor_id in self.auto_send_tasks[chn]:
            logger.warning(f"自动发送任务已经在运行：通道 {chn}, 电机 {motor_id}")
            raise HTTPException(status_code=400, detail="自动发送任务已经在运行")
        if chn not in self.chn_handles:
            logger.error(f"通道 {chn} 未打开")
            raise HTTPException(status_code=400, detail=f"通道 {chn} 未打开")

    def can_start_receive(self, chn: int) -> None:
        """
        检查是否可以启动接收任务。

        :param chn: 通道号。
        :raises HTTPException: 如果任务已在运行或通道未打开。
        """
        if chn not in self.chn_handles:
            logger.error(f"通道 {chn} 未打开")
            raise HTTPException(status_code=400, detail=f"通道 {chn} 未打开")

    async def start_auto_send_message(
        self,
        chn: int,
        motor_id: int,
        datas: Dict[int, list[int]],
        eff: int = 1,
        transmit_type: int = 0,
        interval: int = 10,
    ) -> None:
        """
        启动自动定时发送消息。

        :param chn: 通道号。
        :param motor_id: 电机 ID。
        :param datas: 发送的数据。
        :param eff: 扩展帧标志。
        :param transmit_type: 发送类型。
        :param interval: 发送间隔（毫秒）。
        """

        async def auto_send_loop():
            try:
                while True:
                    await self.send_message(chn, datas, eff, transmit_type)
                    await asyncio.sleep(interval / 1000)
            except asyncio.CancelledError:
                logger.info(f"自动发送任务已取消：通道 {chn}")
            except Exception as e:
                logger.error(f"自动发送任务错误：{e}")

        task = asyncio.create_task(auto_send_loop())
        self.auto_send_tasks[chn][motor_id] = task
        logger.info(f"自动发送任务已启动：通道 {chn}")

    async def stop_auto_send_message(self, chn: int, motor_id: int) -> StatusResponse:
        task = self.auto_send_tasks.get(chn, {}).get(motor_id)
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logger.info(f"自动发送任务已停止：通道 {chn}, 电机 {motor_id}")
            except Exception as e:
                logger.error(f"停止自动发送任务时出现错误：{e}")
                return StatusResponse(
                    status="error", message=f"停止自动发送任务时出现错误：{e}"
                )
            finally:
                del self.auto_send_tasks[chn]
            return StatusResponse(
                status="success",
                message=f"自动发送任务已停止：通道 {chn}, 电机 {motor_id}",
            )
        else:
            logger.info(f"通道 {chn} 没有正在运行的自动发送任务")
            return StatusResponse(
                status="info",
                message=f"通道 {chn}, 电机 {motor_id} 没有正在运行的自动发送任务",
            )

    async def start_receive_message(self, chn: int) -> None:
        """
        启动接收消息任务。

        :param chn: 通道号。
        """

        async def receive_loop():
            try:
                while True:
                    loop = asyncio.get_running_loop()
                    rcv_num = await loop.run_in_executor(
                        self.executor,
                        self.zcan.GetReceiveNum,
                        self.chn_handles.get(chn),
                        ZCAN_TYPE_CAN,
                    )
                    if rcv_num:
                        rcv_msg, rcv_num = await loop.run_in_executor(
                            self.executor,
                            self.zcan.Receive,
                            self.chn_handles.get(chn),
                            rcv_num,
                        )
                        for i in range(rcv_num):
                            await self.handle_can_data(chn, rcv_msg[i])
                    await asyncio.sleep(0.5)
            except asyncio.CancelledError:
                logger.info(f"接收任务已取消：通道 {chn}")
            except Exception as e:
                logger.error(f"接收任务错误：{e}")

        task = asyncio.create_task(receive_loop())
        self.receive_tasks[chn] = task
        logger.info(f"接收任务已启动：通道 {chn}")

    async def stop_receive_message(self, chn: int) -> StatusResponse:
        """
        停止接收消息任务。

        :param chn: 通道号。
        :return: StatusResponse 对象。
        """
        task = self.receive_tasks.get(chn)
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logger.info(f"接收任务已停止：通道 {chn}")
            except Exception as e:
                logger.error(f"停止接收任务时出现错误：{e}")
            finally:
                del self.receive_tasks[chn]
            return StatusResponse(
                status="success", message=f"接收任务已停止：通道 {chn}"
            )
        else:
            logger.warning(f"通道 {chn} 没有正在运行的接收任务")
            return StatusResponse(
                status="info", message=f"通道 {chn} 没有正在运行的接收任务"
            )

    async def handle_can_data(self, chn: int, message: ZCAN_Receive_Data) -> None:
        """
        处理接收到的 CAN 数据。

        :param chn: 通道号。
        :param message: 接收到的消息。
        """
        motor_id = (message.frame.can_id >> 16) & 0xFF
        parse_func = self.parse_functions.get(chn, {}).get(motor_id)
        if not parse_func:
            return
        try:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(self.executor, parse_func, message)
            queue = self.queues.get(chn, {}).get(motor_id)
            if queue:
                await queue.put(result)
        except Exception as e:
            logger.error(f"处理 CAN 数据时出现错误：{e}")

    async def close_channel(self, chn: int) -> StatusResponse:
        if chn not in self.chn_handles:
            logger.warning(f"通道 {chn} 未打开")
            raise HTTPException(status_code=400, detail=f"通道 {chn} 未打开")

        # 关闭所有的任务
        if chn in self.auto_send_tasks:
            for motor_id in list(self.auto_send_tasks[chn].keys()):
                await self.stop_auto_send_message(chn, motor_id)
        await self.stop_receive_message(chn)

        ret = self.zcan.ResetCAN(self.chn_handles.get(chn))
        if ret == 1:
            del self.chn_handles[chn]
            self.queues.pop(chn, None)
            logger.info(f"通道已关闭：{chn}")
            return StatusResponse(status="success", message=f"通道已关闭：{chn}")
        else:
            logger.error(f"关闭通道失败：{chn}")
            raise HTTPException(status_code=500, detail=f"关闭通道失败：{chn}")

    async def close_device(self) -> StatusResponse:
        for chn in list(self.auto_send_tasks.keys()):
            for motor_id in list(self.auto_send_tasks[chn].keys()):
                await self.stop_auto_send_message(chn, motor_id)
        for chn in list(self.receive_tasks.keys()):
            await self.stop_receive_message(chn)

        ret = self.zcan.CloseDevice(self.device_handle)
        if ret == 1:
            self.device_handle = INVALID_DEVICE_HANDLE
            self.chn_handles.clear()
            self.queues.clear()
            logger.info("设备已关闭")
            return StatusResponse(status="success", message="设备已关闭")
        else:
            logger.error("关闭设备失败")
            raise HTTPException(status_code=500, detail="关闭设备失败")

    def get_queue(self, chn: int, motor_id: int) -> Optional[asyncio.Queue]:
        return self.queues.get(chn, {}).get(motor_id)
