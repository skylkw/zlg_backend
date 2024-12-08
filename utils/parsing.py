def parse_motor_0(data: list[int]) -> dict[str, int]:
    # time.sleep(2)  # 模拟耗时操作
    a = 0
    for i in range(10000000):
        a += i
    print(a)

    return {"status": 1}


def parse_motor_1(data: list[int]) -> dict[str, int]:
    # time.sleep(2)  # 模拟耗时操作
    a = 0
    for i in range(1000000):
        a += i
    print(a)

    return {"status": 1}
