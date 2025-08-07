from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime



class LiveChatMsg(BaseModel):
    msg_id: str
    platform: Literal["twitch", "youtube", "discord"]
    user_id: str 
    username: str
    msg: str
    timestamp:datetime