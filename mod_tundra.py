import BigWorld
import Keys
from Avatar import PlayerAvatar
from AvatarInputHandler import AvatarInputHandler
from debug_utils import *

def new_onControlModeChanged(current, eMode, **args):
    global g_tundra
    old_onControlModeChanged(current, eMode, **args)
    if eMode == 'sniper':
        BigWorld.wg_setTreeHidingRadius(1000, 0)
        BigWorld.wg_enableTreeTransparency(False)
    else:
        BigWorld.wg_enableTreeHiding(False)
        BigWorld.wg_enableTreeTransparency(True)

old_onControlModeChanged = AvatarInputHandler.onControlModeChanged
AvatarInputHandler.onControlModeChanged = new_onControlModeChanged

def new_PlayerHandleKey(current, isDown, key, mods):
    if hasattr(BigWorld.player(), 'arena'):
        if key == Keys.KEY_LALT:
            player = BigWorld.player()
            if player.inputHandler.ctrl == player.inputHandler.ctrls['sniper']:
                if isDown:
                    BigWorld.wg_setTreeHidingRadius(12, 15)
                    BigWorld.wg_enableTreeTransparency(True)
                else:
                    BigWorld.wg_setTreeHidingRadius(1000, 0)
                    BigWorld.wg_enableTreeTransparency(False)
            else:
                if isDown:
                    BigWorld.wg_enableTreeHiding(True)
                    BigWorld.wg_setTreeHidingRadius(1000, 0)
                    BigWorld.wg_enableTreeTransparency(False)
                else:
                    BigWorld.wg_enableTreeHiding(False)
                    BigWorld.wg_enableTreeTransparency(True)
    return old_PlayerHandleKey(current, isDown, key, mods)

old_PlayerHandleKey = PlayerAvatar.handleKey
PlayerAvatar.handleKey = new_PlayerHandleKey

