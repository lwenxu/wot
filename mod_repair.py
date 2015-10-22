import BigWorld
import Keys
from functools import partial
from Avatar import PlayerAvatar
from gui.Scaleform.daapi.view.battle.damage_panel import DamagePanel
from gui.battle_control import g_sessionProvider
from debug_utils import *

def new_as_setFireInVehicleS(self, bool):
    old_as_setFireInVehicleS(self, bool)
    BigWorld.callback(0.01, partial(g_sessionProvider.getEquipmentsCtrl().changeSettingByTag, 'extinguisher', None, BigWorld.player()))
    LOG_NOTE('fire extinguished')
    return

old_as_setFireInVehicleS = DamagePanel.as_setFireInVehicleS
DamagePanel.as_setFireInVehicleS = new_as_setFireInVehicleS

g_dev_state = {}
g_auto_repair = ['ammoBay']
g_repair_critical =  ['engine', 'ammoBay', 'gun', 'radio']
g_repair_destroyed = ['engine', 'gun', 'turretRotator', 'surveyingDevice', 'radio']
# ['engine', 'ammoBay', 'gun', 'turretRotator', 'surveyingDevice', 'radio']

def new_as_updateDeviceStateS(self, deviceName, deviceState):
    global g_dev_state
    old_as_updateDeviceStateS(self, deviceName, deviceState)
    g_dev_state[deviceName] = deviceState
    if deviceState == 'critical' and deviceName in g_auto_repair and deviceName in g_repair_critical:
        BigWorld.callback(0.01, partial(g_sessionProvider.getEquipmentsCtrl().changeSettingByTag, 'repairkit', deviceName, BigWorld.player()))
        LOG_NOTE('%s repaired' % deviceName)
        return
    if deviceState == 'destroyed' and deviceName in g_auto_repair and deviceName in g_repair_destroyed:
        BigWorld.callback(0.01, partial(g_sessionProvider.getEquipmentsCtrl().changeSettingByTag, 'repairkit', deviceName, BigWorld.player()))
        LOG_NOTE('%s repaired' % deviceName)
        return

old_as_updateDeviceStateS = DamagePanel.as_updateDeviceStateS
DamagePanel.as_updateDeviceStateS = new_as_updateDeviceStateS

def new_handleKey(self, isDown, key, mods):
    player = BigWorld.player()
    if player and player.isOnArena:
        if player.inputHandler and key == Keys.KEY_SPACE:
            for deviceName in ('chassis', 'rightTrack', 'leftTrack', 'engine'):
                if g_dev_state.has_key(deviceName):
                    if g_dev_state[deviceName] == 'destroyed':
                        BigWorld.callback(0.01, partial(g_sessionProvider.getEquipmentsCtrl().changeSettingByTag, 'repairkit', deviceName, BigWorld.player()))
                        LOG_NOTE('%s repaired' % deviceName)
                        return True
    return old_handleKey(self, isDown, key, mods)

old_handleKey = PlayerAvatar.handleKey
PlayerAvatar.handleKey = new_handleKey

