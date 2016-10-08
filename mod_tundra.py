import BigWorld
import Keys
from Avatar import PlayerAvatar
from AvatarInputHandler import AvatarInputHandler
from debug_utils import *

#INFO: Error in module 'gui.mods.mod_wotspeak_tundra': cannot import name DestructiblesManagerStaticModel
#DestructiblesManager

def initTrees():
    BigWorld.wg_enableTreeHiding(False)
    BigWorld.wg_enableTreeTransparency(True)

def new_startGUI(self):
    old_startGUI(self)
    BigWorld.callback(0.2, initTrees)

old_startGUI = PlayerAvatar._PlayerAvatar__startGUI
PlayerAvatar._PlayerAvatar__startGUI = new_startGUI

def new_destroyGUI(self):
    BigWorld.wg_enableTreeHiding(False)
    BigWorld.wg_enableTreeTransparency(True)
    old_destroyGUI(self)

old_destroyGUI = PlayerAvatar._PlayerAvatar__destroyGUI
PlayerAvatar._PlayerAvatar__destroyGUI = new_destroyGUI

def new_onControlModeChanged(current, eMode, **args):
    old_onControlModeChanged(current, eMode, **args)
    if eMode == 'sniper':
        BigWorld.wg_setTreeHidingRadius(600, 0.0)
        BigWorld.wg_enableTreeTransparency(False)
    else:
        BigWorld.wg_setTreeHidingRadius(15.0, 10.0)
        BigWorld.wg_enableTreeTransparency(True)

old_onControlModeChanged = AvatarInputHandler.onControlModeChanged
AvatarInputHandler.onControlModeChanged = new_onControlModeChanged

def new_PlayerHandleKey(current, isDown, key, mods):
    if hasattr(BigWorld.player(), 'arena'):
        if key == Keys.KEY_LALT:
            player = BigWorld.player()
            if player.inputHandler.ctrl == player.inputHandler.ctrls['sniper']:
                if isDown:
                    BigWorld.wg_setTreeHidingRadius(15.0, 15.0)
                    BigWorld.wg_enableTreeTransparency(True)
                else:
                    BigWorld.wg_setTreeHidingRadius(600, 0.0)
                    BigWorld.wg_enableTreeTransparency(False)
            else:
                if isDown:
                    BigWorld.wg_enableTreeHiding(True)
                    BigWorld.wg_setTreeHidingRadius(600, 0.0)
                    BigWorld.wg_enableTreeTransparency(False)
                else:
                    BigWorld.wg_enableTreeHiding(False)
                    BigWorld.wg_enableTreeTransparency(True)
    return old_PlayerHandleKey(current, isDown, key, mods)

old_PlayerHandleKey = PlayerAvatar.handleKey
PlayerAvatar.handleKey = new_PlayerHandleKey

