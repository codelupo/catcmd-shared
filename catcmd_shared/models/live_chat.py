from pydantic import BaseModel, Field, model_validator, StringConstraints
from typing import Optional, Literal, Annotated, Union
from datetime import datetime, timedelta, timezone
from typing import Type, Dict, Optional, List
import shlex
import re

from catcmd_shared.models.user import ViewerLevel

_REGISTRY: Dict[str, Type["ChatCmd"]] = {}

def register(cls: Type["ChatCmd"]) -> Type["ChatCmd"]:
    for cmd_lit in cls.command_literal():
        _REGISTRY[cmd_lit] = cls
    return cls


class ChatCmd(BaseModel):
    cost: int = 0
    min_level: ViewerLevel = ViewerLevel.viewer
    cd_viewer: int = 0
    cd_global: int = 0

    @classmethod
    def command_literal(cls) -> List[str]:
        raise NotImplementedError

    @classmethod
    def parse_args(cls, tail: list[str]) -> dict:
        raise NotImplementedError
    
    @classmethod
    def from_raw(cls, raw_dict: Dict) -> "ChatCmd":
        msg = raw_dict['msg']
        parts = shlex.split(msg)
        cmd_token, tail = parts[0], parts[1:]
        if cmd_token[0] != "!":
            return None
        cmd_token = cmd_token[1:]

        model: Optional[Type[ChatCmd]] = _REGISTRY.get(cmd_token)
        if not model:
            raise ValueError(f"Unknown command: {cmd_token}")
        data = {"command": cmd_token, **model.parse_args(tail)}
        return model.model_validate(data)


@register
class CmdDiscord(ChatCmd):
    command: Literal["discord"]

    @classmethod
    def command_literal(cls) -> List[str]:
        return ["discord"]

    @classmethod
    def parse_args(cls, tail: list[str]) -> dict:
        return {}
    

@register
class CmdShowPolls(ChatCmd):
    command: Literal["showpolls"]

    @classmethod
    def command_literal(cls) -> List[str]:
        return ["showpolls"]

    @classmethod
    def parse_args(cls, tail: list[str]) -> dict:
        return {}


@register
class CmdNewPoll(ChatCmd):
    command: Literal["newpoll"]
    name: Annotated[str, StringConstraints(min_length=1, max_length=8)]
    desc: Annotated[str, StringConstraints(min_length=1, max_length=40)]
    options: List[str]
    close_date: datetime
    min_level: ViewerLevel = ViewerLevel.mod

    @classmethod
    def command_literal(cls) -> List[str]:
        return ["newpoll"]

    @classmethod
    def parse_args(cls, tail: list[str]) -> dict:
        return validate_poll(tail)


@register
class CmdNewPred(ChatCmd):
    command: Literal["newpred"]
    name: Annotated[str, StringConstraints(min_length=1, max_length=8)]
    desc: Annotated[str, StringConstraints(min_length=1, max_length=40)]
    options: List[str]
    close_date: datetime
    min_level: ViewerLevel = ViewerLevel.mod

    @classmethod
    def command_literal(cls) -> List[str]:
        return ["newpred"]

    @classmethod
    def parse_args(cls, tail: list[str]) -> dict:
        return validate_poll(tail)


@register
class CmdEndPoll(ChatCmd):
    command: Literal["endpoll"]
    name: Annotated[str, StringConstraints(min_length=1, max_length=8)]
    min_level: ViewerLevel = ViewerLevel.mod

    @classmethod
    def command_literal(cls) -> List[str]:
        return ["endpoll"]

    @classmethod
    def parse_args(cls, tail: list[str]) -> dict:
        return {"name": tail[0]}
    

@register
class CmdEndPred(ChatCmd):
    command: Literal["endpred"]
    name: Annotated[str, StringConstraints(min_length=1, max_length=8)]
    won_option: int
    min_level: ViewerLevel = ViewerLevel.mod

    @classmethod
    def command_literal(cls) -> List[str]:
        return ["endpred"]

    @classmethod
    def parse_args(cls, tail: list[str]) -> dict:
        if len(tail) < 2:
            raise ValueError("Usage: !endpred <name> <won option>")
        return {"name": tail[0], "won_option": tail[1]}
    

@register
class CmdCancelPred(ChatCmd):
    command: Literal["cancelpred"]
    name: Annotated[str, StringConstraints(min_length=1, max_length=8)]
    min_level: ViewerLevel = ViewerLevel.mod

    @classmethod
    def command_literal(cls) -> List[str]:
        return ["cancelpred"]

    @classmethod
    def parse_args(cls, tail: list[str]) -> dict:
        if len(tail) < 1:
            raise ValueError("Usage: !cancelpred <name> <won option>")
        return {"name": tail[0]}
    

@register
class CmdVote(ChatCmd):
    # TODO: allow only numbers
    command: Literal["vote"]
    name: Optional[str] = None
    option: Annotated[int, Field(ge=1, le=5)] # 1 <=  x <= 5
    pred_points: Optional[int] = None

    @classmethod
    def command_literal(cls) -> List[str]:
        return ["vote"]

    @classmethod
    def parse_args(cls, tail: list[str]) -> dict:
        if len(tail) < 1:
            raise ValueError("Usage: !vote (<name>) <option> (<points>)")

        if len(tail) == 3:
            return {"name": tail[0], "option": tail[1], "pred_points": tail[2],}
        elif len(tail) == 2:
            if tail[0].isdigit():
                return {"option": tail[0], "pred_points": tail[2]}
            else:
                return {"name": tail[0], "option": tail[0]}
        elif len(tail) == 1: 
            return {"option": tail[0]}
        

@register
class CmdLurk(ChatCmd):
    command: Literal["lurk"]

    @classmethod
    def command_literal(cls) -> List[str]:
        return ["lurk"]

    @classmethod
    def parse_args(cls, tail: list[str]) -> dict:
        return {}


@register
class CmdPyTest(ChatCmd):
    command: Literal["pytest"]

    @classmethod
    def command_literal(cls) -> List[str]:
        return ["pytest"]

    @classmethod
    def parse_args(cls, tail: list[str]) -> dict:
        return {}
    

@register
class CmdPoints(ChatCmd):
    command: Literal["points", "biscuits"]

    @classmethod
    def command_literal(cls) -> List[str]:
        return ["points", "biscuits"]

    @classmethod
    def parse_args(cls, tail: list[str]) -> dict:
        return {}


@register
class CmdStats(ChatCmd):
    command: Literal["stats"]

    @classmethod
    def command_literal(cls) -> List[str]:
        return ["stats"]

    @classmethod
    def parse_args(cls, tail: list[str]) -> dict:
        return {}


@register
class CmdRoulette(ChatCmd):
    command: Literal["roulette", "gamble"]
    amount: str
    min: int = 50
    cd_viewer: int = 15

    @classmethod
    def command_literal(cls) -> List[str]:
        return ["roulette", "gamble"]

    @classmethod
    def parse_args(cls, tail: list[str]) -> dict:
        if len(tail) < 1:
            raise ValueError("Usage: !roulette <amount>")
        
        if tail[0] == "all":
            return {"amount": tail[0]}
        elif tail[0].isdigit == False:
            raise ValueError("Allowed amount is a number or \"all\"")
        amount = tail[0]
        if int(amount) < cls.min:
            raise ValueError(f"Min {cls.min} biscuits")


@register
class CmdTTS(ChatCmd):
    command: Literal["tts"]
    voice: str = "default"
    text: Annotated[str, StringConstraints(min_length=5, max_length=250)]
    cost: int = 1000
    cs_global: int = 30

    @classmethod
    def command_literal(cls) -> List[str]:
        return ["tts"]

    @classmethod
    def parse_args(cls, tail: list[str]) -> dict:
        if len(tail) == 1:
            return {"text": tail[1]}
        elif len(tail) == 2:
            return {"voice": tail[0], "text": tail[1]}
        else:
            raise ValueError("Usage: !tts <voice_name> <text>")


@register
class CmdSoundboard(ChatCmd):
    command: Literal["soundboard", "sb"]
    sound: Literal[
        "9000", "meow", "wawa", "xeno", "spongebob_horn", "ring", "dun_dunnn", 
        "few_moments_later", "noot", "noot_horror",
    ]
    cost: int = 500
    cd_global: int = 15

    @classmethod
    def command_literal(cls) -> List[str]:
        return ["soundboard", "sb"]

    @classmethod
    def parse_args(cls, tail: list[str]) -> dict:
        if len(tail) < 1:
            raise ValueError("Usage: !soundboard <sound>")
        return {"sound": tail[0]}
    

@register
class CmdRMeme(ChatCmd):
    command: Literal["rmeme"]
    cost: int = 1000
    cd_global: int = 30

    @classmethod
    def command_literal(cls) -> List[str]:
        return ["rmeme"]

    @classmethod
    def parse_args(cls, tail: list[str]) -> dict:
        return {}
    

@register
class CmdW(ChatCmd):
    command: Literal["w"]

    @classmethod
    def command_literal(cls) -> List[str]:
        return ["w"]

    @classmethod
    def parse_args(cls, tail: list[str]) -> dict:
        return {}


@register
class CmdL(ChatCmd):
    command: Literal["l"]

    @classmethod
    def command_literal(cls) -> List[str]:
        return ["l"]

    @classmethod
    def parse_args(cls, tail: list[str]) -> dict:
        return {}

@register
class CmdLinkDiscord(ChatCmd):
    command: Literal["linkdiscord"]
    username: str
    cd_viewer: int = 30

    @classmethod
    def command_literal(cls) -> List[str]:
        return ["linkdiscord"]

    @classmethod
    def parse_args(cls, tail: list[str]) -> dict:
        if len(tail) < 1:
            raise ValueError("Usage: !linkdiscord <username>")
        return {"username": tail[0]}
    
@register
class CmdLinkAcc(ChatCmd):
    command: Literal["linkacc"]
    code: str

    @classmethod
    def command_literal(cls) -> List[str]:
        return ["linkacc"]

    @classmethod
    def parse_args(cls, tail: list[str]) -> dict:
        if len(tail) < 1:
            raise ValueError("Usage: !linkacc <username>")
        return {"code": tail[0]}


CmdUnion = Annotated[
    Union[
        CmdDiscord, CmdShowPolls, CmdNewPoll, CmdNewPred, CmdEndPoll, CmdEndPred,
        CmdCancelPred, CmdVote, CmdLurk, CmdPyTest, CmdPoints, CmdStats, CmdTTS, CmdRMeme, CmdSoundboard, 
        CmdW, CmdL, 
        CmdLinkDiscord, CmdLinkAcc, 
    ],
    Field(discriminator="command"),
]


class ChatMsg(BaseModel):
    id_msg: str
    id_platform: str 
    platform: Literal["twitch", "youtube", "discord"]
    username: str
    msg: str
    timestamp:datetime
    cmd: Optional[CmdUnion] = None
    viewer_level: ViewerLevel 

    @model_validator(mode="before")
    @classmethod
    def parse_cmd(cls, values):
        # we want to be able to process cmd seperately 
        # therefore if some value for cmd is given, then don't try to process it.
        if "cmd" not in values:
            values["cmd"] = ChatCmd.from_raw(values)
        return values
    
    @model_validator(mode="after")
    def check_permissions(self):
        if self.cmd and (self.viewer_level > self.cmd.min_level):
            raise ValueError(f"User doesn't have access to perform the cmd")
        return self
    

class LiveChatMsg(BaseModel):
    msg_id: str
    platform: Literal["twitch", "youtube", "discord"]
    id_platform: str 
    username: str
    msg: str
    timestamp:datetime
    

def validate_poll(tail):
    cmd_usage = "Usage: !tts name \"desc\" \"opt 1\" ... \"opt 5\" xhr"
    if len(tail) < 4:
        raise ValueError(cmd_usage)
    
    # remaining tail, excluding name, desc, duration
    options = tail[2:-1]
    for option in options:
        if len(option) > 40:
            raise ValueError("Poll option should be less than 40char.")

    # validate poll duration
    regex_res = re.fullmatch(r"(\d+)(day|hr|min)", tail[-1])
    if not regex_res:
        raise ValueError("Invalid duration format, e.g. 5hr, 5min, 5day")
    
    poll_dur, poll_dur_type = int(regex_res[1]), regex_res[2]
    timedelta_poll_dur = None
    if poll_dur_type == 'day':
        timedelta_poll_dur = timedelta(days=poll_dur)
    elif poll_dur_type == 'hr':
        timedelta_poll_dur = timedelta(hours=poll_dur)
    elif poll_dur_type == 'min':
        timedelta_poll_dur = timedelta(minutes=poll_dur)
    close_date = datetime.now(timezone.utc) + timedelta_poll_dur

    return {
        "name": tail[0], "desc": tail[1], "options": options, "close_date": close_date
    }
