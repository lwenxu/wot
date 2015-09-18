import BigWorld
import Keys
from functools import partial
from Avatar import PlayerAvatar
from gui.Scaleform.Battle import DamagePanel
from gui.battle_control import g_sessionProvider
from debug_utils import *
global devName
global devState
global _


def new_updateDeviceState(self, value):
    global devName
    global devState
    global _
    old_updateDeviceState(self, value)
    devName, devState, _ = value


def new_handleKey(self, isDown, key, mods):
    global devName
    global devState
    global _
    old_handleKey(self, isDown, key, mods)
    player = BigWorld.player()
    if player and player.isOnArena:
        if player.inputHandler and key == Keys.KEY_SPACE:
            if devName in ('chassis', 'rightTrack', 'leftTrack') and devState == 'destroyed':
                BigWorld.callback(0.09, partial(g_sessionProvider.getEquipmentsCtrl().changeSettingByTag, 'repairkit', devName, BigWorld.player()))
                LOG_NOTE('track repaired')


old_updateDeviceState = DamagePanel._updateDeviceState
DamagePanel._updateDeviceState = new_updateDeviceState
old_handleKey = PlayerAvatar.handleKey
PlayerAvatar.handleKey = new_handleKey


init = lambda : None
fini = lambda : None
onAccountBecomePlayer = lambda : None
onAccountBecomeNonPlayer = lambda : None
onAvatarBecomePlayer = lambda : None
onAccountShowGUI = lambda ctx : None

