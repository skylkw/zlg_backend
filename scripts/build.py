from PyInstaller import __main__ as pyi


params = [
    "-F",
    "-w",
    # static目录纳入打包
    "--add-data",
    "static:static",
    "--add-data",
    "zlgcan_x64:zlgcan_x64",
    # 每次打包前清除build 和 dist目录
    "--clean",
    "--name",
    "zlg",
    "-i",
    "static/favicon.ico",
    # 无需用户确认
    "--noconfirm",

    "client.py",
]

pyi.run(params)
