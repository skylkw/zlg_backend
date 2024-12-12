import asyncio
import json
from fastapi import APIRouter, Request, HTTPException, Depends
from sse_starlette.sse import EventSourceResponse
from dependencies import get_zlg_can_manager
import utils
from zlg.manager import ZLGCanManager
from utils.logger import logger

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
        while not await request.is_disconnected():
            try:
                data = await asyncio.wait_for(queue.get(), timeout=60.0)
                yield json.dumps(data)
            except asyncio.TimeoutError:
                logger.warning(f"通道 {chn} 无数据")
                break
        logger.info(f"通道 {chn} 断开连接")

    return EventSourceResponse(event_generator())
