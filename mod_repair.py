import BigWorld, ResMgr, Keys
from functools import partial
from Avatar import PlayerAvatar
from gui.Scaleform.daapi.view.battle.damage_panel import DamagePanel
from gui.battle_control import g_sessionProvider
from items import vehicles
from debug_utils import *

g_key = Keys.KEY_SPACE
g_auto_extinguisher = True
g_dev_state = {}
#['engine', 'ammoBay', 'gun', 'turretRotator', 'surveyingDevice', 'radio']
#['commander', 'radioman', 'driver', 'gunner', 'loader']
g_auto_repair = {}
g_auto_repair['all'] = ['ammoBay']
g_auto_heal = {}
g_auto_heal['all'] = ['loader']
for classTag in vehicles.VEHICLE_CLASS_TAGS:
    g_auto_repair[classTag] = g_auto_repair['all']
    g_auto_heal[classTag] = g_auto_heal['all']
g_repair_critical =  ['engine', 'ammoBay', 'gun', 'radio']
g_repair_destroyed = ['engine', 'gun', 'turretRotator', 'surveyingDevice', 'radio']
g_xml = ResMgr.openSection('scripts/client/gui/mods/mod_repair.xml')
if g_xml:
    g_auto_extinguisher = g_xml.readBool('autoExtinguisher', True)
    g_key = getattr(Keys, g_xml.readString('fastRepairKey', 'KEY_SPACE'))
    str_list = g_xml.readString('autoRepair')
    if str_list: g_auto_repair['all'] = str_list.split(',')
    str_list = g_xml.readString('autoHeal')
    if str_list: g_auto_heal['all'] = str_list.split(',')
    for classTag in vehicles.VEHICLE_CLASS_TAGS:
        str_list = g_xml.readString('%s/autoRepair' % classTag)
        if str_list: g_auto_repair[classTag] = str_list.split(',')
        else: g_auto_repair[classTag] = g_auto_repair['all']
        str_list = g_xml.readString('%s/autoHeal' % classTag)
        if str_list: g_auto_heal[classTag] = str_list.split(',')
        else: g_auto_heal[classTag] = g_auto_heal['all']
LOG_NOTE('autoExtinguisher: %s' % g_auto_extinguisher)
LOG_NOTE('autoRepair: %s' % g_auto_repair)
LOG_NOTE('autoHeal: %s' % g_auto_heal)

def new_as_setFireInVehicleS(self, bool):
    old_as_setFireInVehicleS(self, bool)
    BigWorld.callback(0.01, partial(g_sessionProvider.getEquipmentsCtrl().changeSettingByTag, 'extinguisher', None, BigWorld.player()))
    LOG_NOTE('fire extinguished')
    return

if g_auto_extinguisher:
    old_as_setFireInVehicleS = DamagePanel.as_setFireInVehicleS
    DamagePanel.as_setFireInVehicleS = new_as_setFireInVehicleS


def new_as_updateDeviceStateS(self, deviceName, deviceState):
    global g_dev_state
    old_as_updateDeviceStateS(self, deviceName, deviceState)
    g_dev_state[deviceName] = deviceState
    vehicleClass = 'all'
    vehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
    if vehicle and vehicle.isStarted:
        vehicleClass = vehicles.getVehicleClass(vehicle.typeDescriptor.type.compactDescr)
    if deviceState == 'critical' and deviceName in g_auto_repair[vehicleClass] and deviceName in g_repair_critical:
        BigWorld.callback(0.01, partial(g_sessionProvider.getEquipmentsCtrl().changeSettingByTag, 'repairkit', deviceName, BigWorld.player()))
        LOG_NOTE('%s repaired' % deviceName)
        return
    elif deviceState == 'destroyed' and deviceName in g_auto_repair[vehicleClass] and deviceName in g_repair_destroyed:
        BigWorld.callback(0.01, partial(g_sessionProvider.getEquipmentsCtrl().changeSettingByTag, 'repairkit', deviceName, BigWorld.player()))
        LOG_NOTE('%s repaired' % deviceName)
        return
    elif deviceState in ('critical', 'destroyed') and deviceName in g_auto_heal[vehicleClass]:
        BigWorld.callback(0.01, partial(g_sessionProvider.getEquipmentsCtrl().changeSettingByTag, 'medkit', deviceName, BigWorld.player()))
        LOG_NOTE('%s healed' % deviceName)
        return

old_as_updateDeviceStateS = DamagePanel.as_updateDeviceStateS
DamagePanel.as_updateDeviceStateS = new_as_updateDeviceStateS

def new_handleKey(self, isDown, key, mods):
    player = BigWorld.player()
    if player and player.isOnArena:
        if player.inputHandler and key == g_key:
            for deviceName in ('chassis', 'rightTrack', 'leftTrack', 'engine'):
                if g_dev_state.has_key(deviceName):
                    if g_dev_state[deviceName] == 'destroyed':
                        BigWorld.callback(0.01, partial(g_sessionProvider.getEquipmentsCtrl().changeSettingByTag, 'repairkit', deviceName, BigWorld.player()))
                        LOG_NOTE('%s repaired' % deviceName)
                        return True
    return old_handleKey(self, isDown, key, mods)

old_handleKey = PlayerAvatar.handleKey
PlayerAvatar.handleKey = new_handleKey

