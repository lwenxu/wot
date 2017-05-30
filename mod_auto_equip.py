import BigWorld
import ResMgr
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.hangar.AmmunitionPanel import AmmunitionPanel
from gui.Scaleform.daapi.view.lobby.hangar.TmenXpPanel import TmenXpPanel
from gui.shared.utils.requesters import REQ_CRITERIA
from skeletons.gui.shared import IItemsCache
from helpers import dependency
from debug_utils import *

LOG_DEBUG = LOG_NOTE
g_settings = None

def equip_optional_devices(current):
    if g_settings[current.name]:
        for slotIdx in range(0, 3):
            device = current.descriptor.optionalDevices[slotIdx]
            if not device:
                deviceCompactDescr = g_settings[current.name].readInt('slot' + str(slotIdx + 1), 0)
                if deviceCompactDescr is not 0:
                    BigWorld.player().inventory.equipOptionalDevice(current.invID, deviceCompactDescr, slotIdx, False, None)
                    LOG_DEBUG('equip', current.name, slotIdx, deviceCompactDescr)

def remove_optional_devices_from_vehicle(vehicle):
    if vehicle and not (vehicle.isInBattle or vehicle.isLocked):
        for slotIdx in range(0, 3):
            device = vehicle.descriptor.optionalDevices[slotIdx]
            if device and device.removable:
                BigWorld.player().inventory.equipOptionalDevice(vehicle.invID, 0, slotIdx, False, None)
                LOG_DEBUG('remove:', vehicle.name, slotIdx, device.name)

def remove_optional_devices(current):
    itemsCache = dependency.instance(IItemsCache)
    vehicles = itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
    for vehicle in vehicles:
        if current.intCD != vehicle.intCD:
            remove_optional_devices_from_vehicle(vehicle)

def return_crew(current):
    if not current.isCrewFull:
        BigWorld.player().inventory.return_crew(current.invID, None)
        LOG_DEBUG('return crew: %s' % current.name)

def equip_current_vehicle():
    if g_currentVehicle.isInHangar():
        current = g_currentVehicle.item
        LOG_DEBUG('try to equip: %s' % current.name)
        remove_optional_devices(current)
        equip_optional_devices(current)
        return_crew(current)

#vehicle is changed, equip it
def new_TmenXpPanel_onVehicleChange(*args, **kwargs):
    equip_current_vehicle()
    old_TmenXpPanel_onVehicleChange(*args, **kwargs)

old_TmenXpPanel_onVehicleChange = TmenXpPanel._onVehicleChange
TmenXpPanel._onVehicleChange = new_TmenXpPanel_onVehicleChange

def save_device(vehicle, deviceId, slotIdx):
    LOG_DEBUG('save', vehicle.name, slotIdx, deviceId)
    g_settings.write(vehicle.name, '')
    g_settings[vehicle.name].writeInt('slot' + str(slotIdx + 1), int(deviceId))
    g_settings.save()

#device is changed on current vehicle, save it
def new_AmmunitionPanel_as_setDataS(self, data):
    vehicle = g_currentVehicle.item
    for info in data['devices']:
        if info['slotType'] == 'optionalDevice':
            LOG_DEBUG('device: id=%d, slotIndex=%d, removable=%s' % (info['id'], info['slotIndex'], info['removable']))
            slotIdx = info['slotIndex']
            deviceId = info['id']
            if info['removable']:
                #TODO check real changes
                save_device(vehicle, deviceId, slotIdx)
    old_AmmunitionPanel_as_setDataS(self, data)

old_AmmunitionPanel_as_setDataS = AmmunitionPanel.as_setDataS
AmmunitionPanel.as_setDataS = new_AmmunitionPanel_as_setDataS

g_settings = ResMgr.openSection('scripts/client/gui/mods/mod_auto_equip.xml', True)
if not g_settings:
    g_settings.save()
BigWorld.logInfo('NOTE', 'package loaded: mod_auto_equip', None)

