import BigWorld
import Keys
from functools import partial
from Avatar import PlayerAvatar
from gui.Scaleform.daapi.view.battle.damage_panel import DamagePanel
from gui.battle_control import g_sessionProvider
from debug_utils import *
g_devName = None
g_devState = None

def new_as_setFireInVehicleS(self, bool):
    old_as_setFireInVehicleS(self, bool)
    BigWorld.callback(0.01, partial(g_sessionProvider.getEquipmentsCtrl().changeSettingByTag, 'extinguisher', None, BigWorld.player()))
    LOG_NOTE('fire extinguished')
    return

old_as_setFireInVehicleS = DamagePanel.as_setFireInVehicleS
DamagePanel.as_setFireInVehicleS = new_as_setFireInVehicleS

def new_as_updateDeviceStateS(self, deviceName, deviceState):
    global g_devName
    global g_devState
    old_as_updateDeviceStateS(self, deviceName, deviceState)
    g_devName = deviceName
    g_devState = deviceState

old_as_updateDeviceStateS = DamagePanel.as_updateDeviceStateS
DamagePanel.as_updateDeviceStateS = new_as_updateDeviceStateS

def new_handleKey(self, isDown, key, mods):
    player = BigWorld.player()
    if player and player.isOnArena:
        if player.inputHandler and key == Keys.KEY_SPACE:
            if g_devName in ('chassis', 'rightTrack', 'leftTrack') and g_devState == 'destroyed':
                BigWorld.callback(0.01, partial(g_sessionProvider.getEquipmentsCtrl().changeSettingByTag, 'repairkit', g_devName, BigWorld.player()))
                LOG_NOTE('track repaired')
                return True
    return old_handleKey(self, isDown, key, mods)

old_handleKey = PlayerAvatar.handleKey
PlayerAvatar.handleKey = new_handleKey

