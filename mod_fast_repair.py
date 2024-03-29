import BigWorld, Keys
from Avatar import PlayerAvatar
from gui.Scaleform.daapi.view.meta.DamagePanelMeta import DamagePanelMeta
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
from constants import ARENA_PERIOD
from debug_utils import *
#LOG_DEBUG = LOG_NOTE

g_fast_key = Keys.KEY_SPACE
g_repair_key = Keys.KEY_4
g_heal_key = Keys.KEY_5
g_fired = False
g_damaged = set([])
g_destroyed = set([])
g_heal_all = set(['commander', 'gunner1', 'gunner2', 'driver', 'loader1', 'loader2'])
g_repair_all = set(['engine', 'ammoBay', 'gun', 'turretRotator', 'surveyingDevice', 'radio', 'rightTrack', 'leftTrack'])
g_repair_fast = set(['rightTrack', 'leftTrack', 'chassis'])
g_repair_damaged =  set(['engine', 'ammoBay', 'gun', 'turretRotator'])
g_repair_destroyed = set(['engine', 'gun', 'turretRotator', 'surveyingDevice'])
g_ConsumablesPanel = None


def repair(device):
    LOG_DEBUG('repairing %s' % device)
    g_ConsumablesPanel._ConsumablesPanel__handleEquipmentPressed(1275, device) #repairkit

def heal(device):
    LOG_DEBUG('healing %s' % device)
    g_ConsumablesPanel._ConsumablesPanel__handleEquipmentPressed(763, device) #medkit

def extinguish():
    LOG_DEBUG('extinguishing the fire')
    g_ConsumablesPanel._ConsumablesPanel__handleEquipmentPressed(251) #extinguisher
    global g_fired
    g_fired = False

def new_onEquipmentAdded(self, int_cd, item):
    old_onEquipmentAdded(self, int_cd, item)
    global g_ConsumablesPanel
    g_ConsumablesPanel = self

old_onEquipmentAdded = ConsumablesPanel._ConsumablesPanel__onEquipmentAdded
ConsumablesPanel._ConsumablesPanel__onEquipmentAdded = new_onEquipmentAdded

def new_as_setFireInVehicleS(self, isInFire):
    old_as_setFireInVehicleS(self, isInFire)
    global g_fired
    g_fired = True

old_as_setFireInVehicleS = DamagePanelMeta.as_setFireInVehicleS
DamagePanelMeta.as_setFireInVehicleS = new_as_setFireInVehicleS

def new_as_updateDeviceStateS(self, deviceName, deviceState):
    LOG_DEBUG('%s ==> %s:' % (deviceName, deviceState))
    if deviceState == 'critical':
        g_damaged.add(deviceName)
    elif deviceState == 'destroyed':
        g_destroyed.add(deviceName)
    elif deviceState == 'normal':
        g_damaged.discard(deviceName)
        g_destroyed.discard(deviceName)
    old_as_updateDeviceStateS(self, deviceName, deviceState)

old_as_updateDeviceStateS = DamagePanelMeta.as_updateDeviceStateS
DamagePanelMeta.as_updateDeviceStateS = new_as_updateDeviceStateS

def new_handleKey(self, isDown, key, mods):
    player = BigWorld.player()
    if player and player.isOnArena and player.inputHandler:
        # fast action
        if key == g_fast_key:
            if g_fired:
                extinguish()
                return True
            devices = g_repair_fast & g_destroyed
            if len(devices) == 1:
                repair(devices.pop())
                return True
        # fast repair
        if key == g_repair_key:
            devices = (g_repair_damaged & g_damaged) | (g_repair_destroyed & g_destroyed)
            if len(devices) == 1:
                repair(devices.pop())
                return True
        # fast heal
        if key == g_heal_key:
            devices = g_heal_all & g_destroyed
            if len(devices) == 1:
                heal(devices.pop())
                return True
    return old_handleKey(self, isDown, key, mods)

old_handleKey = PlayerAvatar.handleKey
PlayerAvatar.handleKey = new_handleKey

def new_onArenaPeriodChange(current, period, periodEndTime, periodLength, periodAdditionalInfo):
    old_onArenaPeriodChange(current, period, periodEndTime, periodLength, periodAdditionalInfo)
    if period == ARENA_PERIOD.BATTLE or period == ARENA_PERIOD.AFTERBATTLE:
        g_damaged.clear()
        g_destroyed.clear()

old_onArenaPeriodChange = PlayerAvatar._PlayerAvatar__onArenaPeriodChange
PlayerAvatar._PlayerAvatar__onArenaPeriodChange = new_onArenaPeriodChange

BigWorld.logInfo('NOTE', 'package loaded: mod_fast_repair', None)
