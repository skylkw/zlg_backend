import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from routes import motor_0_routes, motor_1_routes, zlg_routes, sse_routes
from fastapi.middleware.cors import CORSMiddleware

from schemas import StatusResponse


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
static_file_abspath = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_file_abspath), name="static")

# 注册路由
app.include_router(zlg_routes.router)
app.include_router(sse_routes.router)
app.include_router(motor_0_routes.router)
app.include_router(motor_1_routes.router)


# 首页
@app.get("/")
def index():
    return FileResponse(f"{static_file_abspath}/index.html")

# 测试接口
@app.get("/test")
def test():
    return StatusResponse(status="ok", message="test success")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
