from enum import IntEnum
import struct


class MotorWorkMode(IntEnum):  # 电机工作模式
    FREE_MODE = 0
    TORQUE_MODE = 1
    SPEED_MODE = 2


class MotorGear(IntEnum):  # 挡位
    GEAR_N = 0
    GEAR_D = 1
    GEAR_R = 2


class Motor0Command:
    def __init__(self, chn: int, id: int, eff: int, transmit_type: int, interval: int):
        self.chn = chn
        self.id = id
        self.eff = eff
        self.transmit_type = transmit_type
        self.interval = interval

    def enable_motor(self):
        datas = {0x0CF103D0: [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]}
        return datas

    def disable_motor(self):
        datas = {0x0CF103D0: [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]}
        return datas

    def set_motor_settings(
        self,
        mode: MotorWorkMode,
        value: int,
        gear: MotorGear,
        climb: int = 0,
        hand_brake: int = 0,
        foot_brake: int = 0,
        life: int = 0,
    ):
        byte0 = 0x01
        byte1 = mode.value
        match mode:
            case MotorWorkMode.FREE_MODE:
                byte_2_3 = 0
                byte_4_5 = 0
            case MotorWorkMode.TORQUE_MODE:
                byte_2_3 = 0
                byte_4_5 = (value + 2000) * 10
            case MotorWorkMode.SPEED_MODE:
                byte_2_3 = value + 20000
                byte_4_5 = 0
        byte6 = gear.value | (climb << 2) | (hand_brake << 3) | (foot_brake << 4)
        byte7 = life
        # 将报文打包，每个元素是一个字节，共8个字节
        packed_data = struct.pack(
            "<BBHHBB", byte0, byte1, byte_2_3, byte_4_5, byte6, byte7
        )
        # 将报文解包为数组
        data = list(struct.unpack("<BBBBBBBB", packed_data))
        datas = {0x0CF103D0: data}
        return datas


class Motor1Command:
    def __init__(self, chn: int, id: int, eff: int, transmit_type: int, interval: int):
        self.chn = chn
        self.id = id
        self.eff = eff
        self.transmit_type = transmit_type
        self.interval = interval

    def enable_motor(self):
        datas = {0x0CF203D0: [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]}
        return datas

    def disable_motor(self):
        datas = {0x0CF203D0: [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]}
        return datas

    def set_motor_settings(
        self,
        mode: MotorWorkMode,
        value: int,
        gear: MotorGear,
        climb: int = 0,
        hand_brake: int = 0,
        foot_brake: int = 0,
        life: int = 0,
    ):
        byte0 = 0x01
        byte1 = mode.value
        match mode:
            case MotorWorkMode.FREE_MODE:
                byte_2_3 = 0
                byte_4_5 = 0
            case MotorWorkMode.TORQUE_MODE:
                byte_2_3 = 0
                byte_4_5 = (value + 2000) * 10
            case MotorWorkMode.SPEED_MODE:
                byte_2_3 = value + 20000
                byte_4_5 = 0
        byte6 = gear.value | (climb << 2) | (hand_brake << 3) | (foot_brake << 4)
        byte7 = life
        # 将报文打包，每个元素是一个字节，共8个字节
        packed_data = struct.pack(
            "<BBHHBB", byte0, byte1, byte_2_3, byte_4_5, byte6, byte7
        )
        # 将报文解包为数组
        data = list(struct.unpack("<BBBBBBBB", packed_data))
        datas = {0x0CF203D0: data}
        return datas
