import BigWorld
import Keys
from Avatar import PlayerAvatar
from AvatarInputHandler import AvatarInputHandler
from debug_utils import *

g_tundra = False

def new_onControlModeChanged(current, eMode, **args):
    global g_tundra
    old_onControlModeChanged(current, eMode, **args)
    if eMode == 'sniper':
        BigWorld.wg_setTreeHidingRadius(750, 0)
        BigWorld.wg_enableTreeTransparency(False)
        g_tundra = True
    else:
        BigWorld.wg_enableTreeHiding(False)
        BigWorld.wg_enableTreeTransparency(True)
        g_tundra = False

old_onControlModeChanged = AvatarInputHandler.onControlModeChanged
AvatarInputHandler.onControlModeChanged = new_onControlModeChanged

def new_PlayerHandleKey(current, isDown, key, mods):
    if hasattr(BigWorld.player(), 'arena'):
        if key == Keys.KEY_LALT:
            player = BigWorld.player()
            if player.inputHandler.ctrl == player.inputHandler.ctrls['sniper']:
                if (isDown and g_tundra) or (not isDown and not g_tundra):
                    BigWorld.wg_setTreeHidingRadius(750, 0)
                    BigWorld.wg_enableTreeTransparency(False)
                else:
                    BigWorld.wg_setTreeHidingRadius(12, 15)
                    BigWorld.wg_enableTreeTransparency(True)
            else:
                if isDown:
                    BigWorld.wg_enableTreeHiding(True)
                    BigWorld.wg_setTreeHidingRadius(750, 0)
                    BigWorld.wg_enableTreeTransparency(False)
                else:
                    BigWorld.wg_enableTreeHiding(False)
                    BigWorld.wg_enableTreeTransparency(True)
    return old_PlayerHandleKey(current, isDown, key, mods)

old_PlayerHandleKey = PlayerAvatar.handleKey
PlayerAvatar.handleKey = new_PlayerHandleKey

