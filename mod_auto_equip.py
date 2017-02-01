import BigWorld, ResMgr
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from gui.Scaleform.daapi.view.lobby.shared.fitting_select_popover import FittingSelectPopover
from gui.ClientHangarSpace import ClientHangarSpace, _VehicleAppearance
from gui.shared import g_itemsCache
from gui.shared.utils.requesters import REQ_CRITERIA
from debug_utils import *
#LOG_DEBUG = LOG_NOTE

g_xmlSetting = None
g_prevVehicleID = None
g_autoEquip = True
g_returnCrew = True
g_vAppearance = None

def equipOptionalDevices(curVehicle):
    if g_xmlSetting[curVehicle.name]:
        for slotIdx in range(0, 3):
            device = curVehicle.descriptor.optionalDevices[slotIdx]
            if not device:
                deviceCompactDescr = g_xmlSetting[curVehicle.name].readInt('slot' + str(slotIdx + 1), 0)
                if deviceCompactDescr is not 0:
                    BigWorld.player().inventory.equipOptionalDevice(curVehicle.invID, deviceCompactDescr, slotIdx, False, None)
                    LOG_DEBUG('equip', curVehicle.name, slotIdx, deviceCompactDescr)

def removeAllOptionalDevicesFromVehicle(vehicle):
    if vehicle and not (vehicle.isInBattle or vehicle.isLocked):
        for slotIdx in range(0, 3):
            device = vehicle.descriptor.optionalDevices[slotIdx]
            if device and device.removable:
                BigWorld.player().inventory.equipOptionalDevice(vehicle.invID, 0, slotIdx, False, None)
                LOG_DEBUG('remove:', vehicle.name, slotIdx, device.name)

def removeAllOptionalDevices(curVehicle):
    vehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
    for vehicle in vehicles:
        if curVehicle.intCD != vehicle.intCD:
            removeAllOptionalDevicesFromVehicle(vehicle)

def returnCrew(curVehicle):
    if not curVehicle.isCrewFull:
        BigWorld.player().inventory.returnCrew(curVehicle.invID, None)
        LOG_DEBUG('return crew: %s' % curVehicle.name)

def equipCurrentVehicle():
    if g_vAppearance is not None:
        if g_vAppearance._VehicleAppearance__isLoaded:
            if g_currentVehicle.isInHangar():
                curVehicle = g_currentVehicle.item
                #LOG_DEBUG('try to equip: %s' % curVehicle.name)
                if g_autoEquip:
                    removeAllOptionalDevices(curVehicle)
                    equipOptionalDevices(curVehicle)
                if g_returnCrew:
                    returnCrew(curVehicle)
        else:
            BigWorld.callback(0.2, equipCurrentVehicle)

def new_recreateVehicle(self, vDesc, vState, onVehicleLoadedCallback):
    old_recreateVehicle(self, vDesc, vState, onVehicleLoadedCallback)
    try:
        global g_vAppearance
        g_vAppearance = self._ClientHangarSpace__vAppearance
        global g_prevVehicleID
        if g_prevVehicleID != g_currentVehicle.item.intCD:
            g_prevVehicleID = g_currentVehicle.item.intCD
            equipCurrentVehicle()
    except:
        LOG_CURRENT_EXCEPTION()

def saveDeviceOnVehicle(vehicle, deviceId, slotIdx, isRemove):
    device = g_itemsCache.items.getItemByCD(int(deviceId))
    if device and device.isRemovable:
        LOG_DEBUG('save', vehicle.name, slotIdx, deviceId)
        g_xmlSetting.write(vehicle.name, '')
        if isRemove:
            g_xmlSetting[vehicle.name].writeInt('slot' + str(slotIdx + 1), 0)
        else:
            g_xmlSetting[vehicle.name].writeInt('slot' + str(slotIdx + 1), int(deviceId))
        g_xmlSetting.save()

def new_setVehicleModule(self, newId, oldId, isRemove):
    if not g_currentPreviewVehicle.isPresent():
        slotIdx = self._FittingSelectPopover__logicProvider._slotIndex
        LOG_DEBUG('setVehicleModule: newId=%d, oldId=%d, isRemove=%s, slotIndex=%d' % (newId, oldId, isRemove, slotIdx))
        vehicle = g_currentVehicle.item
        saveDeviceOnVehicle(vehicle, newId, slotIdx, isRemove)
    old_setVehicleModule(self, newId, oldId, isRemove)

init = lambda : None
fini = lambda : None
onAccountBecomePlayer = lambda : None
onAccountBecomeNonPlayer = lambda : None
onAvatarBecomePlayer = lambda : None
g_gui_started = False

def onAccountShowGUI(ctx):
    global g_xmlSetting
    global g_prevVehicleID
    global g_gui_started
    global old_setVehicleModule
    global old_recreateVehicle
    if g_gui_started: return
    g_xmlSetting = ResMgr.openSection('scripts/client/gui/mods/mod_auto_equip.xml', True)
    if not g_xmlSetting:
        g_xmlSetting.save()
    g_prevVehicleID = g_currentVehicle.item.intCD
    old_setVehicleModule = FittingSelectPopover.setVehicleModule
    FittingSelectPopover.setVehicleModule = new_setVehicleModule
    old_recreateVehicle = ClientHangarSpace.recreateVehicle
    ClientHangarSpace.recreateVehicle = new_recreateVehicle
    g_gui_started = True

BigWorld.logInfo('NOTE', 'package loaded: mod_auto_equip', None)
