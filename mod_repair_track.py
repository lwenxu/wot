import BigWorld
import Keys
import Math
import CommandMapping
from debug_utils import *
from functools import partial
from Avatar import PlayerAvatar
from gui.Scaleform.Battle import DamagePanel
from gui.battle_control import g_sessionProvider
global devName
global devState
global _


old_updateDeviceState = DamagePanel._updateDeviceState
def new_updateDeviceState(self, value):
    global devName
    global devState
    global _
    old_updateDeviceState(self, value)
    devName, devState, _ = value
DamagePanel._updateDeviceState = new_updateDeviceState

old_handleKey = PlayerAvatar.handleKey
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
PlayerAvatar.handleKey = new_handleKey


init = lambda : None
fini = lambda : None
onAccountBecomePlayer = lambda : None
onAccountBecomeNonPlayer = lambda : None
onAvatarBecomePlayer = lambda : None
onAccountShowGUI = lambda ctx : None
