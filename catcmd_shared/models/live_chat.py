from pydantic import BaseModel, Field
from typing import Optional, Literal, Annotated, Union
from datetime import datetime
from typing import Type, Dict, Optional
import shlex


_REGISTRY: Dict[str, Type["ChatCmd"]] = {}

def register(cls: Type["ChatCmd"]) -> Type["ChatCmd"]:
    _REGISTRY[cls.command_literal()] = cls
    return cls


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

    def command_literal(self) -> str:
        raise NotImplementedError

    def parse_args(self, tail: list[str]) -> dict:
        raise NotImplementedError
    
    def from_raw(self, raw: str) -> "ChatCmd":
        parts = shlex.split(raw)
        if not parts:
            raise ValueError("Empty command")
        cmd_token, tail = parts[0], parts[1:]
        model: Optional[Type[ChatCmd]] = _REGISTRY.get(cmd_token)
        if not model:
            raise ValueError(f"Unknown command: {cmd_token}")
        data = {"command": cmd_token, **model.parse_args(tail)}
        return model.model_validate(data)

@register
class CmdTTS(ChatCmd):
    command: Literal["!tts"]
    voice: str
    text: str

    @classmethod
    def command_literal(cls) -> str:
        return "!tts"

    @classmethod
    def parse_args(cls, tail: list[str]) -> dict:
        if len(tail) < 2:
            raise ValueError("Usage: !tts <voice_name> <text>")
        return {"voice": tail[0], "text": tail[1]}



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