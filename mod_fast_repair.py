import BigWorld, ResMgr, Keys, random
from functools import partial
from Avatar import PlayerAvatar
from gui.Scaleform.daapi.view.meta.DamagePanelMeta import DamagePanelMeta
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import dependency
from constants import ARENA_PERIOD
from debug_utils import *

g_trackRepairKey = Keys.KEY_SPACE
g_repairKey = Keys.KEY_4
g_healKey = Keys.KEY_5
g_dev_state = {}
g_guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
g_repair_list = ['engine', 'ammoBay', 'gun', 'turretRotator', 'surveyingDevice', 'radio', 'rightTrack', 'leftTrack']
g_heal_list = ['commander', 'gunner1', 'gunner2', 'driver', 'loader1', 'loader2']
g_repair_critical =  ['engine', 'ammoBay', 'gun', 'turretRotator']
g_repair_destroyed = ['engine', 'gun', 'turretRotator', 'surveyingDevice']

LOG_DEBUG = LOG_NOTE

def repair(tag, entityName, timeout = 0.0):
    ctrl = g_guiSessionProvider.shared.equipments
    if ctrl is None:
        LOG_DEBUG('no equipments to repair')
        return
    BigWorld.callback(timeout, partial(ctrl.changeSettingByTag, tag, entityName, BigWorld.player()))
    LOG_DEBUG('apply %s to %s' % (tag, entityName))

'''
def new_as_setFireInVehicleS(self, isInFire):
    old_as_setFireInVehicleS(self, isInFire)
    repair('extinguisher', None, 1 + random.random());

old_as_setFireInVehicleS = DamagePanelMeta.as_setFireInVehicleS
DamagePanelMeta.as_setFireInVehicleS = new_as_setFireInVehicleS
'''

def new_as_updateDeviceStateS(self, deviceName, deviceState):
    global g_dev_state
    LOG_DEBUG('%s ==> %s:' % (deviceName, deviceState))
    g_dev_state[deviceName] = deviceState
    old_as_updateDeviceStateS(self, deviceName, deviceState) #FIXME Exception: PyGFxValue - Failed to invoke method as_updateDeviceState

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
            LOG_DEBUG('g_dev_state: ' % g_dev_state)
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

def new_onArenaPeriodChange(current, period, periodEndTime, periodLength, periodAdditionalInfo):
    old_onArenaPeriodChange(current, period, periodEndTime, periodLength, periodAdditionalInfo)
    global g_dev_state
    if period == ARENA_PERIOD.BATTLE:
        LOG_DEBUG('ARENA_PERIOD.BATTLE')
        g_dev_state = {}
    elif period == ARENA_PERIOD.AFTERBATTLE:
        LOG_DEBUG('ARENA_PERIOD.AFTERBATTLE')
        g_dev_state = {}

old_onArenaPeriodChange = PlayerAvatar._PlayerAvatar__onArenaPeriodChange
PlayerAvatar._PlayerAvatar__onArenaPeriodChange = new_onArenaPeriodChange

BigWorld.logInfo('NOTE', 'package loaded: mod_fast_repair', None)

