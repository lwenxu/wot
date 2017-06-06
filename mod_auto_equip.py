import BigWorld
import ResMgr
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.hangar.AmmunitionPanel import AmmunitionPanel
from gui.Scaleform.daapi.view.lobby.hangar.TmenXpPanel import TmenXpPanel
from gui.shared.utils.requesters import REQ_CRITERIA
from skeletons.gui.shared import IItemsCache
from helpers import dependency
from debug_utils import *

#LOG_DEBUG = LOG_NOTE
g_settings = None

def equip_optional_devices(current):
    if g_settings[current.name]:
        for slot_idx in range(0, 3):
            device = current.descriptor.optionalDevices[slot_idx]
            if not device:
                device_id = read_device(current, slot_idx)
                if device_id != -1:
                    BigWorld.player().inventory.equipOptionalDevice(current.invID, device_id, slot_idx, False, None)
                    LOG_DEBUG('equip: %s, slot=%d, id=%d' % (current.name, slot_idx, device_id))

def remove_optional_devices_from_vehicle(vehicle):
    if vehicle and not (vehicle.isInBattle or vehicle.isLocked):
        for slot_idx in range(0, 3):
            device = vehicle.descriptor.optionalDevices[slot_idx]
            if device and device.removable:
                BigWorld.player().inventory.equipOptionalDevice(vehicle.invID, 0, slot_idx, False, None)
                LOG_DEBUG('remove: %s, slot=%d, device=%s' % (vehicle.name, slot_idx, device.name))

def remove_optional_devices(current):
    itemsCache = dependency.instance(IItemsCache)
    vehicles = itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
    for vehicle in vehicles:
        if current.intCD != vehicle.intCD:
            remove_optional_devices_from_vehicle(vehicle)

def return_crew(current):
    if not current.isCrewFull:
        BigWorld.player().inventory.returnCrew(current.invID, None)
        LOG_DEBUG('return crew: %s' % current.name)

def equip_current_vehicle():
    if g_currentVehicle.isInHangar():
        current = g_currentVehicle.item
        LOG_DEBUG('try to equip: %s' % current.name)
        remove_optional_devices(current)
        equip_optional_devices(current)

def new_TmenXpPanel_onVehicleChange(*args, **kwargs):
    old_TmenXpPanel_onVehicleChange(*args, **kwargs)
    equip_current_vehicle()

old_TmenXpPanel_onVehicleChange = TmenXpPanel._onVehicleChange
TmenXpPanel._onVehicleChange = new_TmenXpPanel_onVehicleChange

def read_device(vehicle, slot_idx):
    return g_settings[vehicle.name].readInt('slot' + str(slot_idx + 1), -1)

def save_device(vehicle, device_id, slot_idx):
    LOG_DEBUG('save %s, slot=%d, id=%d' % (vehicle.name, slot_idx, device_id))
    g_settings.write(vehicle.name, '')
    g_settings[vehicle.name].writeInt('slot' + str(slot_idx + 1), int(device_id))
    g_settings.save()

def new_AmmunitionPanel_as_setDataS(self, data):
    old_AmmunitionPanel_as_setDataS(self, data)
    vehicle = g_currentVehicle.item
    for info in data['devices']:
        if info['slotType'] == 'optionalDevice':
            LOG_DEBUG('device: id=%d, slot=%d, removable=%s' % (info['id'], info['slotIndex'], info['removable']))
            slot_idx = info['slotIndex']
            device_id = info['id']
            if info['removable']:
                #TODO check real changes
                #if device_id != read_device(vehicle, slot_idx):
                save_device(vehicle, device_id, slot_idx)

old_AmmunitionPanel_as_setDataS = AmmunitionPanel.as_setDataS
AmmunitionPanel.as_setDataS = new_AmmunitionPanel_as_setDataS

g_settings = ResMgr.openSection('scripts/client/gui/mods/mod_auto_equip.xml', True)
if not g_settings:
    g_settings.save()
BigWorld.logInfo('NOTE', 'package loaded: mod_auto_equip', None)

