import BigWorld, ResMgr, Keys, random
from functools import partial
from Avatar import PlayerAvatar
from gui.Scaleform.daapi.view.battle.damage_panel import DamagePanel
from gui.battle_control import g_sessionProvider
from items import vehicles
from debug_utils import *

g_trackRepairKey = Keys.KEY_SPACE
g_repairKey = Keys.KEY_NONE
g_healKey = Keys.KEY_NONE
g_auto_extinguisher = True
g_dev_state = {}
g_repair_list = {} # ['engine', 'ammoBay', 'gun', 'turretRotator', 'surveyingDevice', 'radio', 'rightTrack', 'leftTrack']
g_heal_list = {} # ['commander', 'radioman', 'driver', 'gunner', 'loader']
g_repair_critical =  ['engine', 'ammoBay', 'gun', 'radio']
g_repair_destroyed = ['engine', 'gun', 'turretRotator', 'surveyingDevice', 'radio', 'rightTrack', 'leftTrack']

for classTag in vehicles.VEHICLE_CLASS_TAGS:
    g_repair_list[classTag] = []
    g_heal_list[classTag] = []

g_xml = ResMgr.openSection('scripts/client/gui/mods/mod_fast_repair.xml')
if g_xml:
    g_auto_extinguisher = g_xml.readBool('autoExtinguisher', True)
    g_trackRepairKey = getattr(Keys, g_xml.readString('trackRepairKey', 'KEY_SPACE'))
    g_repairKey = getattr(Keys, g_xml.readString('repairKey', 'KEY_NONE'))
    g_healKey = getattr(Keys, g_xml.readString('healKey', 'KEY_NONE'))
    for classTag in vehicles.VEHICLE_CLASS_TAGS:
        str_list = g_xml.readString('%s/repair' % classTag)
        if str_list:
            g_repair_list[classTag] = str_list.split(',')
        str_list = g_xml.readString('%s/heal' % classTag)
        if str_list:
            g_heal_list[classTag] = str_list.split(',')

LOG_NOTE('extinguisher: %s' % g_auto_extinguisher)
LOG_NOTE('repair: %s' % g_repair_list)
LOG_NOTE('heal: %s' % g_heal_list)

def new_as_setFireInVehicleS(self, bool):
    old_as_setFireInVehicleS(self, bool)
    BigWorld.callback(random.random(), partial(g_sessionProvider.getEquipmentsCtrl().changeSettingByTag, 'extinguisher', None, BigWorld.player()))
    LOG_NOTE('fire extinguished')
    return

if g_auto_extinguisher:
    old_as_setFireInVehicleS = DamagePanel.as_setFireInVehicleS
    DamagePanel.as_setFireInVehicleS = new_as_setFireInVehicleS

def repair(deviceName, deviceState):
    if (deviceState == 'critical' and deviceName in g_repair_critical) or (deviceState == 'destroyed' and deviceName in g_repair_destroyed):
        BigWorld.callback(0.01, partial(g_sessionProvider.getEquipmentsCtrl().changeSettingByTag, 'repairkit', deviceName, BigWorld.player()))
        LOG_NOTE('%s repaired' % deviceName)

def heal(deviceName, deviceState):
    if deviceState in ('critical', 'destroyed'):
        BigWorld.callback(0.01, partial(g_sessionProvider.getEquipmentsCtrl().changeSettingByTag, 'medkit', deviceName, BigWorld.player()))
        LOG_NOTE('%s healed' % deviceName)

def getClassTag():
    vehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
    if vehicle and vehicle.isStarted:
        return vehicles.getVehicleClass(vehicle.typeDescriptor.type.compactDescr)
    return None

def new_as_updateDeviceStateS(self, deviceName, deviceState):
    global g_dev_state
    old_as_updateDeviceStateS(self, deviceName, deviceState)
    g_dev_state[deviceName] = deviceState

    #auto repair
    if g_repairKey == Keys.KEY_DEBUG:
        classTag = getClassTag()
        if classTag:
            if deviceName in g_repair_list[classTag]:
                repair(deviceName, deviceState)
                return
    #auto heal
    if g_healKey == Keys.KEY_DEBUG:
        classTag = getClassTag()
        if classTag:
            if deviceName in g_heal_list[classTag]:
                heal(deviceName, deviceState)
                return

old_as_updateDeviceStateS = DamagePanel.as_updateDeviceStateS
DamagePanel.as_updateDeviceStateS = new_as_updateDeviceStateS

def new_handleKey(self, isDown, key, mods):
    player = BigWorld.player()
    if player and player.isOnArena and player.inputHandler:
        # fast track repair
        if key == g_trackRepairKey:
            for deviceName in ['rightTrack', 'leftTrack']:
                if g_dev_state.has_key(deviceName):
                    repair(deviceName, g_dev_state[deviceName])
                    return True
        # fast repair
        if key == g_repairKey:
            classTag = getClassTag()
            if classTag:
                for deviceName in g_repair_list[classTag]:
                    if g_dev_state.has_key(deviceName):
                        repair(deviceName, g_dev_state[deviceName])
                        return True
        # fast heal
        if key == g_healKey:
            classTag = getClassTag()
            if classTag:
                for deviceName in g_heal_list[classTag]:
                    if g_dev_state.has_key(deviceName):
                        heal(deviceName, g_dev_state[deviceName])
                        return True
    return old_handleKey(self, isDown, key, mods)

old_handleKey = PlayerAvatar.handleKey
PlayerAvatar.handleKey = new_handleKey

