import BigWorld
import Keys
from functools import partial
from Avatar import PlayerAvatar
from gui.Scaleform.Battle import DamagePanel
from gui.battle_control import g_sessionProvider
from debug_utils import *
devName = None
devState = None


def new_as_updateDeviceStateS(self, deviceName, deviceState):
    global devName
    global devState
    old_as_updateDeviceStateS(self, deviceName, deviceState)
    devName = deviceName
    devState = deviceState


def new_handleKey(self, isDown, key, mods):
    global devName
    global devState
    player = BigWorld.player()
    if player and player.isOnArena:
        if player.inputHandler and key == Keys.KEY_SPACE:
            if devName in ('chassis', 'rightTrack', 'leftTrack') and devState == 'destroyed':
                BigWorld.callback(0.09, partial(g_sessionProvider.getEquipmentsCtrl().changeSettingByTag, 'repairkit', devName, BigWorld.player()))
                LOG_NOTE('track repaired')
    return old_handleKey(self, isDown, key, mods)


old_as_updateDeviceStateS = DamagePanel.as_updateDeviceStateS
DamagePanel.as_updateDeviceStateS = new_as_updateDeviceStateS
old_handleKey = PlayerAvatar.handleKey
PlayerAvatar.handleKey = new_handleKey

