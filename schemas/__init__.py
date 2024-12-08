from pydantic import BaseModel
from typing import Optional, Any


class StatusResponse(BaseModel):
    status: str
    data: Optional[Any] = None
    message: Optional[str] = None
