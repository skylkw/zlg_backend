import random
import struct
import time

from zlg.zlgcan import ZCAN_Receive_Data


def parse_motor_0(message: ZCAN_Receive_Data) -> dict[str, int | float | str]:
    match message.frame.can_id:
        case 0x0CFF01EF:
            (
                torque,
                speed,
                input_vol,
                input_curr,
            ) = struct.unpack("<4H", message.frame.data)
            return {
                "torque": round(torque / 10 - 2000, 2),
                "speed": speed - 20000,
                "inputVoltage": input_vol / 10,
                "inputCurrent": round(input_curr / 10 - 1000, 2),
            }

        case 0x0CFF02EF:
            (
                byte0,
                fault_code,
                fault_level,
                _,
                software_version,
                _,
                mcu_temp,
                motor_temp,
            ) = struct.unpack("<8B", message.frame.data)

            # Extract work mode (bits 0-2)
            work_mode = byte0 & 0b00000111
            match work_mode:
                case 0:
                    work_mode_str = "自由模式"
                case 1:
                    work_mode_str = "扭矩模式"
                case 2:
                    work_mode_str = "速度模式"
                case _:
                    work_mode_str = "无效模式"

            # Extract hill assist (bit 3)
            hill_assists = (byte0 >> 3) & 0b00000001
            match hill_assists:
                case 0:
                    hill_assists_str = "爬坡模式关闭"
                case 1:
                    hill_assists_str = "爬坡模式开启"
                case _:
                    hill_assists_str = "未知"

            # Extract MCU status (bits 4-5)
            mcu_status = (byte0 >> 4) & 0b00000011
            match mcu_status:
                case 0:
                    mcu_status_str = "无故障"
                case 1:
                    mcu_status_str = "有故障"
                case _:
                    mcu_status_str = "无效"

            # Handle fault level
            match fault_level:
                case 0:
                    fault_level_str = "无故障"
                case 1:
                    fault_level_str = "一级故障"
                case 2:
                    fault_level_str = "二级故障"
                case 3:
                    fault_level_str = "三级故障"

            software_version *= 0.1
            mcu_temp -= 40
            motor_temp -= 40

            return {
                "workMode": work_mode_str,
                "hillAssists": hill_assists_str,
                "mcuStatus": mcu_status_str,
                "faultCode": fault_code,
                "faultLevel": fault_level_str,
                "softwareVersion": software_version,
                "mcuTemperature": mcu_temp,
                "motorTemperature": motor_temp,
            }

        case 0x0CFF03EF:
            (
                position,
                mechanical_position,
                _,
                _,
                _,
                _,
            ) = struct.unpack("<2H4B", message.frame.data)

            return {
                "position": round(position * 0.0055, 2),
                "mechanicalPosition": round(mechanical_position * 0.0055, 2),
            }

        case _:
            return {"error": "未知的 CAN ID"}


def parse_motor_1(message: ZCAN_Receive_Data) -> dict[str, int | float | str]:
    match message.frame.can_id:
        case 0x0CFE01EF:
            (
                torque,
                speed,
                input_vol,
                input_curr,
            ) = struct.unpack("<4H", message.frame.data)
            return {
                "torque": round(torque / 10 - 2000, 2),
                "speed": speed - 20000,
                "inputVoltage": input_vol / 10,
                "inputCurrent": round(input_curr / 10 - 1000, 2),
            }

        case 0x0CFE02EF:
            (
                byte0,
                fault_code,
                fault_level,
                _,
                software_version,
                _,
                mcu_temp,
                motor_temp,
            ) = struct.unpack("<8B", message.frame.data)

            # Extract work mode (bits 0-2)
            work_mode = byte0 & 0b00000111
            match work_mode:
                case 0:
                    work_mode_str = "自由模式"
                case 1:
                    work_mode_str = "扭矩模式"
                case 2:
                    work_mode_str = "速度模式"
                case _:
                    work_mode_str = "无效模式"

            # Extract hill assist (bit 3)
            hill_assists = (byte0 >> 3) & 0b00000001
            match hill_assists:
                case 0:
                    hill_assists_str = "爬坡模式关闭"
                case 1:
                    hill_assists_str = "爬坡模式开启"
                case _:
                    hill_assists_str = "未知"

            # Extract MCU status (bits 4-5)
            mcu_status = (byte0 >> 4) & 0b00000011
            match mcu_status:
                case 0:
                    mcu_status_str = "无故障"
                case 1:
                    mcu_status_str = "有故障"
                case _:
                    mcu_status_str = "无效"

            # Handle fault level
            match fault_level:
                case 0:
                    fault_level_str = "无故障"
                case 1:
                    fault_level_str = "一级故障"
                case 2:
                    fault_level_str = "二级故障"
                case 3:
                    fault_level_str = "三级故障"
                case _:
                    fault_level_str = "未知故障等级"

            software_version *= 0.1
            mcu_temp -= 40
            motor_temp -= 40

            return {
                "workMode": work_mode_str,
                "hillAssists": hill_assists_str,
                "mcuStatus": mcu_status_str,
                "faultCcode": fault_code,
                "faultLevel": fault_level_str,
                "softwareVersion": software_version,
                "mcuTemperature": mcu_temp,
                "motorTemperature": motor_temp,
            }

        case 0x0CFE03EF:
            (
                position,
                mechanical_position,
                _,
                _,
                _,
                _,
            ) = struct.unpack("<2H4B", message.frame.data)

            return {
                "position": round(position * 0.0055, 2),
                "mechanicalPosition": round(mechanical_position * 0.0055, 2),
            }

        case _:
            return {"error": "未知的 CAN ID"}
