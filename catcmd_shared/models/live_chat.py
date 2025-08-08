from pydantic import BaseModel, Field
from typing import Optional, Literal, Annotated, Union
from datetime import datetime

class ChatMsg(BaseModel):
    msg_id: str
    platform: Literal["twitch", "youtube", "discord"]
    user_id: str 
    username: str
    msg: str
    timestamp:datetime


class ChatCmd(BaseModel):
    id: str
    platform: Literal["twitch", "youtube", "discord"]
    user_id: str
    username: str
    cmd: str
    timestamp: datetime

class CmdDiscord(ChatCmd):
    id: Literal["discord"]
    args: Optional[str] = None

CmdUnion = Annotated[
    Union[CmdDiscord, ],
    Field(discriminator="command"),
]


class LiveChatMsg(BaseModel):
    msg_id: str
    platform: Literal["twitch", "youtube", "discord"]
    user_id: str 
    username: str
    msg: str
    timestamp:datetime