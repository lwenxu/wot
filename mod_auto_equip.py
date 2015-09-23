import BigWorld
import ResMgr
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.hangar.AmmunitionPanel import AmmunitionPanel
from gui.ClientHangarSpace import ClientHangarSpace, _VehicleAppearance
from gui.shared import g_itemsCache, REQ_CRITERIA
from debug_utils import *
from gui import SystemMessages
g_xmlSetting = None
g_prevVehicleID = None
g_started = False
g_vAppearance = None

def equipOptionalDevicesOnVehicle(vehicle):
    global g_xmlSetting
    try:
        if g_xmlSetting[vehicle.name]:
            for slotIdx in range(0, 3):
                device = vehicle.descriptor.optionalDevices[slotIdx]
                if not device:
                    deviceCompactDescr = g_xmlSetting[vehicle.name].readInt('slot' + str(slotIdx + 1), 0)
                    if deviceCompactDescr is not 0:
                        BigWorld.player().inventory.equipOptionalDevice(vehicle.invID, deviceCompactDescr, slotIdx, False, None)
                        #LOG_NOTE('equip', vehicle.name, slotIdx, deviceCompactDescr)
    except:
        LOG_CURRENT_EXCEPTION()


def removeAllOptionalDevicesFromVehicle(vehicle):
    try:
        if vehicle and not (vehicle.isInBattle or vehicle.isLocked):
            for slotIdx in range(0, 3):
                device = vehicle.descriptor.optionalDevices[slotIdx]
                if device and device.removable:
                    BigWorld.player().inventory.equipOptionalDevice(vehicle.invID, 0, slotIdx, False, None)
                    #LOG_NOTE('remove:', vehicle.name, slotIdx, device.name)
    except:
        LOG_CURRENT_EXCEPTION()


def removeAllOptionalDevices(curVehicle):
    vehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
    for vehicle in vehicles:
        if curVehicle is not vehicle:
            removeAllOptionalDevicesFromVehicle(vehicle)


def equipCurrentVehicle():
    global g_vAppearance
    if g_vAppearance is not None:
        if g_vAppearance._VehicleAppearance__isLoaded:
            if g_currentVehicle.isInHangar:
                curVehicle = g_currentVehicle.item
                #LOG_NOTE('try to equip: %s' % curVehicle.name)
                removeAllOptionalDevices(curVehicle)
                equipOptionalDevicesOnVehicle(curVehicle)
        else:
            BigWorld.callback(0.2, equipCurrentVehicle)


def new_recreateVehicle(self, vDesc, vState, onVehicleLoadedCallback):
    global old_recreateVehicle
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


def saveDeviceOnVehicle(vehicle, deviceId, slotId, isRemove):
    #LOG_NOTE('save', vehicle.name, slotId, deviceId)
    g_xmlSetting.write(vehicle.name, '')
    if isRemove:
        g_xmlSetting[vehicle.name].writeInt('slot' + str(slotId + 1), 0)
    else:
        g_xmlSetting[vehicle.name].writeInt('slot' + str(slotId + 1), int(deviceId))
    g_xmlSetting.save()


def new_setVehicleModule(self, newId, slotIdx, oldId, isRemove):
    global old_setVehicleModule
    old_setVehicleModule(self, newId, slotIdx, oldId, isRemove)
    vehicle = g_currentVehicle.item
    saveDeviceOnVehicle(vehicle, newId, slotIdx, isRemove)


init = lambda : None
fini = lambda : None
onAccountBecomePlayer = lambda : None
onAccountBecomeNonPlayer = lambda : None
onAvatarBecomePlayer = lambda : None


def onAccountShowGUI(ctx):
    global g_xmlSetting
    global g_prevVehicleID
    global g_started
    global old_setVehicleModule
    global old_recreateVehicle
    if g_started: return
    g_xmlSetting = ResMgr.openSection('scripts/client/gui/mods/mod_auto_equip.xml', True)
    if not g_xmlSetting:
        g_xmlSetting.save()
    g_prevVehicleID = g_currentVehicle.item.intCD
    old_setVehicleModule = AmmunitionPanel.setVehicleModule
    AmmunitionPanel.setVehicleModule = new_setVehicleModule
    old_recreateVehicle = ClientHangarSpace.recreateVehicle
    ClientHangarSpace.recreateVehicle = new_recreateVehicle
    SystemMessages.pushMessage('AutoEquip 0.9.10 started')
    g_started = True

