from pydantic import BaseModel, Field
from typing import Optional, Literal, Annotated, Union
from datetime import datetime

class ChatMsg(BaseModel):
    msg_id: str
    id_platform: str 
    platform: Literal["twitch", "youtube", "discord"]
    username: str
    msg: str
    timestamp:datetime


class ChatCmd(BaseModel):
    id: str
    id_platform: str
    platform: Literal["twitch", "youtube", "discord"]
    username: str
    cmd: str
    timestamp: datetime

class CmdDiscord(ChatCmd):
    command: Literal["discord"]

class CmdW(ChatCmd):
    command: Literal["w"]

class CmdL(ChatCmd):
    command: Literal["l"]

class CmdPoints(ChatCmd):
    command: Literal["points"]

class CmdSoundboard(ChatCmd):
    command: Literal["soundboard"]
    args: Optional[dict] = None


CmdUnion = Annotated[
    Union[
        CmdDiscord, CmdW, CmdL, CmdPoints, CmdSoundboard,
    ],
    Field(discriminator="command"),
]


class LiveChatMsg(BaseModel):
    msg_id: str
    platform: Literal["twitch", "youtube", "discord"]
    id_platform: str 
    username: str
    msg: str
    timestamp:datetime