# app/dependencies.py

import sys
from utils.command import Motor0Command, Motor1Command
from zlg.manager import ZLGCanManager
import os

# 获取 zlgcan_x64/zlgcan.dll的路径

dll_path = os.path.join(os.path.dirname(__file__), "zlgcan_x64", "zlgcan.dll")


zlcan_manager = ZLGCanManager(dll_path)
motor_0_command = Motor0Command(0, 1, 0, 20)

motor_1_command = Motor1Command(1, 1, 0, 20)


def get_zlg_can_manager():
    return zlcan_manager


def get_motor_0_command():
    return motor_0_command


def get_motor_1_command():
    return motor_1_command
