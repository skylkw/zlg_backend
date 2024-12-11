import asyncio
import json
from fastapi import APIRouter, Request, HTTPException, Depends
from sse_starlette.sse import EventSourceResponse
from dependencies import get_zlg_can_manager
from zlg.manager import ZLGCanManager

router = APIRouter()


@router.get("/sse/{chn}")
async def sse(
    request: Request,
    chn: int,
    zlg_can_manager: ZLGCanManager = Depends(get_zlg_can_manager),
):
    queue = zlg_can_manager.get_queue(chn)
    if queue is None:
        raise HTTPException(status_code=404, detail=f"通道 {chn} 未找到")

    async def event_generator():
        while True:
            if await request.is_disconnected():
                print(f"客户端已断开连接 (通道: {chn})")
                break
            try:
                data = await asyncio.wait_for(queue.get(), timeout=60.0)
                yield json.dumps(data)
            except asyncio.TimeoutError:
                print(f"通道: {chn} 超时未收到消息，关闭连接")
                break
            
    return EventSourceResponse(event_generator())
