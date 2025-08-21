Store 
- Re-usable functions
- Pydantic definitions for communication.

Will not be launched as a service, instead imported where required.


# venv
## setup
python -m venv venv
source venv/bin/activate


# test
from catcmd_shared.models import live_chat
from catcmd_shared.models.user import ViewerLevel
from datetime import datetime


msg = {"id_msg": "aa", "id_platform": "bb", "platform": "twitch", "username": "aabb", "viewer_level": ViewerLevel.viewer}
msg['timestamp'] = datetime.now()


msg['msg'] =  '!soundboard xeno'
msg['msg'] = '!tts test "abcasdasdad"'

msg = live_chat.ChatMsg(**msg)
live_chat.ChatMsg.model_validate(msg)
live_chat.ChatCmd.from_raw(msg)



# TODO 
I need to allow multiple command literals 
I need to allow dynamic commands, .e.g 1 for voting on polls 