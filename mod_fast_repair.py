import BigWorld, ResMgr, Keys, random
from Avatar import PlayerAvatar
from gui.Scaleform.daapi.view.meta.DamagePanelMeta import DamagePanelMeta
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
from constants import ARENA_PERIOD
from debug_utils import *

g_fastKey = Keys.KEY_SPACE
g_repairKey = Keys.KEY_4
g_healKey = Keys.KEY_5
g_fired = False
g_damaged = set([])
g_destroyed = set([])
g_repair_list = set(['engine', 'ammoBay', 'gun', 'turretRotator', 'surveyingDevice', 'radio', 'rightTrack', 'leftTrack'])
g_heal_list = set(['commander', 'gunner1', 'gunner2', 'driver', 'loader1', 'loader2'])
g_repair_fast = set(['rightTrack', 'leftTrack', 'chassis'])
g_repair_damaged =  set(['engine', 'ammoBay', 'gun', 'turretRotator'])
g_repair_destroyed = set(['engine', 'gun', 'turretRotator', 'surveyingDevice'])
g_ConsumablesPanel = None

LOG_DEBUG = LOG_NOTE

def repair(device):
    LOG_DEBUG('repairing %s' % device)
    g_ConsumablesPanel._ConsumablesPanel__handleEquipmentPressed(1275, device) #repairkit
    g_damaged.remove(device)
    g_destroyed.remove(device)

def heal(device):
    LOG_DEBUG('healing %s' % device)
    g_ConsumablesPanel._ConsumablesPanel__handleEquipmentPressed(763, device) #medkit
    g_damaged.remove(device)
    g_destroyed.remove(device)

def extinguish():
    g_ConsumablesPanel._ConsumablesPanel__handleEquipmentPressed(251) #extinguisher
    global g_fired
    g_fired = False
    LOG_DEBUG('fire extinguished')

def new_onEquipmentAdded(self, int_cd, item):
    old_onEquipmentAdded(self, int_cd, item)
    global g_ConsumablesPanel
    g_ConsumablesPanel = self
    LOG_DEBUG('added: %s: %s' % (int_cd, item))

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
    if deviceState == 'critical': g_damaged.add(deviceName)
    if deviceState == 'destroyed': g_destroyed.add(deviceName)
    old_as_updateDeviceStateS(self, deviceName, deviceState)

old_as_updateDeviceStateS = DamagePanelMeta.as_updateDeviceStateS
DamagePanelMeta.as_updateDeviceStateS = new_as_updateDeviceStateS

def new_handleKey(self, isDown, key, mods):
    player = BigWorld.player()
    if player and player.isOnArena and player.inputHandler:
        # fast action
        if key == g_fastKey:
            if g_fired:
                extinguish()
                return True
            devices = g_repair_fast & g_repair_destroyed
            LOG_DEBUG('devices to repair: %s' % devices)
            if len(devices) == 1:
                repair(devices.pop())
                return True
        # fast repair
        if key == g_repairKey:
            devices = (g_damaged & g_repair_damaged) | (g_destroyed & g_repair_destroyed)
            LOG_DEBUG('devices to repair: %s' % devices)
            if len(devices) == 1:
                repair(devices.pop())
                return True
        # fast heal
        if key == g_healKey:
            devices = g_destroyed & g_heal_list
            LOG_DEBUG('devices to repair: %s' % devices)
            if len(devices) == 1:
                heal(devices.pop())
                return True
    return old_handleKey(self, isDown, key, mods)

old_handleKey = PlayerAvatar.handleKey
PlayerAvatar.handleKey = new_handleKey

def new_onArenaPeriodChange(current, period, periodEndTime, periodLength, periodAdditionalInfo):
    old_onArenaPeriodChange(current, period, periodEndTime, periodLength, periodAdditionalInfo)
    global g_damaged, g_destroyed
    if period == ARENA_PERIOD.BATTLE or period == ARENA_PERIOD.AFTERBATTLE:
        LOG_DEBUG('clearing lists')
        g_damaged.clear()
        g_destroyed.clear()

old_onArenaPeriodChange = PlayerAvatar._PlayerAvatar__onArenaPeriodChange
PlayerAvatar._PlayerAvatar__onArenaPeriodChange = new_onArenaPeriodChange

BigWorld.logInfo('NOTE', 'package loaded: mod_fast_repair', None)

