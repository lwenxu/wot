import BigWorld, ResMgr, Keys, random
from functools import partial
from Avatar import PlayerAvatar
from gui.Scaleform.daapi.view.meta.DamagePanelMeta import DamagePanelMeta
from gui.battle_control import g_sessionProvider
from debug_utils import *

g_trackRepairKey = Keys.KEY_SPACE
g_repairKey = Keys.KEY_4
g_healKey = Keys.KEY_5
g_dev_state = {}
g_repair_list = ['engine', 'ammoBay', 'gun', 'turretRotator', 'surveyingDevice', 'radio', 'rightTrack', 'leftTrack']
g_heal_list = ['commander', 'radioman', 'driver', 'gunner', 'loader']
g_repair_critical =  ['engine', 'ammoBay', 'gun', 'radio']
g_repair_destroyed = ['engine', 'gun', 'turretRotator', 'surveyingDevice', 'radio', 'rightTrack', 'leftTrack']

LOG_DEBUG = LOG_NOTE

def repair(tag, entityName, timeout = 0.0):
    ctrl = g_sessionProvider.shared.equipments
    if ctrl is None:
        LOG_DEBUG('mod_fast_repair: no equipments to repair')
        return
    #result, error = ctrl.changeSettingByTag(tag, entityName, BigWorld.player())
    #if not result and error:
    #    LOG_DEBUG('mod_fast_repair: something goes wrong')
    #else:
    BigWorld.callback(timeout, partial(ctrl.changeSettingByTag, tag, entityName, BigWorld.player()))
    LOG_DEBUG('mod_fast_repair: apply %s to %s' % (tag, entityName))

def new_as_setFireInVehicleS(self, bool):
    old_as_setFireInVehicleS(self, bool)
    repair('extinguisher', None, random.random());

old_as_setFireInVehicleS = DamagePanelMeta.as_setFireInVehicleS
DamagePanelMeta.as_setFireInVehicleS = new_as_setFireInVehicleS

def new_as_updateDeviceStateS(self, deviceName, deviceState):
    global g_dev_state
    old_as_updateDeviceStateS(self, deviceName, deviceState)
    g_dev_state[deviceName] = deviceState
    LOG_DEBUG('mod_fast_repair: %s ==> %s:' % (deviceName, deviceState))

old_as_updateDeviceStateS = DamagePanelMeta.as_updateDeviceStateS
DamagePanelMeta.as_updateDeviceStateS = new_as_updateDeviceStateS

def new_handleKey(self, isDown, key, mods):
    player = BigWorld.player()
    if player and player.isOnArena and player.inputHandler:

        # fast track repair
        if key == g_trackRepairKey:
            for deviceName in ['rightTrack', 'leftTrack', 'engine']:
                if g_dev_state.has_key(deviceName):
                    if g_dev_state[deviceName] == 'destroyed':
                        repair('repairkit', deviceName)
                        return True

        # fast repair
        if key == g_repairKey:
            deviceToRepair = ''
            # find device to repair
            for deviceName,deviceState in g_dev_state.iteritems():
                if ((deviceState == 'critical' and deviceName in g_repair_critical) or
                    (deviceState == 'destroyed' and deviceName in g_repair_destroyed)):
                    if deviceToRepair:
                        deviceToRepair = ''
                        break
                    deviceToRepair = deviceName
            if deviceToRepair:
                repair('repairkit', deviceToRepair)
                return True

        # fast heal
        if key == g_healKey:
            deviceToRepair = ''
            # find crew member to repair
            for deviceName,deviceState in g_dev_state.iteritems():
                if deviceState == 'destroyed' and deviceName in g_heal_list:
                    if deviceToRepair:
                        deviceToRepair = ''
                        break
                    deviceToRepair = deviceName
            if deviceToRepair:
                repair('medkit', deviceToRepair)
                return True

    return old_handleKey(self, isDown, key, mods)

old_handleKey = PlayerAvatar.handleKey
PlayerAvatar.handleKey = new_handleKey

BigWorld.logInfo('NOTE', 'package loaded: mod_fast_repair', None)

