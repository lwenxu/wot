import BigWorld
import ResMgr
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.hangar.AmmunitionPanel import AmmunitionPanel
from gui.ClientHangarSpace import ClientHangarSpace
from gui.shared import g_itemsCache, REQ_CRITERIA
from adisp import process
from debug_utils import *
from gui import SystemMessages
old_setVehicleModule = None
old_recreateVehicle = None
g_xmlSetting = None
g_prevVehicle = None
g_started = False


def equipAllRemovableDevicesOnVehicle(vehicle):
    global g_xmlSetting
    try:
        if g_xmlSetting[vehicle.name]:
            for slotIdx in range(0, 3):
                device = vehicle.descriptor.optionalDevices[slotIdx]
                if not device:
                    deviceCompactDescr = g_xmlSetting[vehicle.name].readInt('slot' + str(slotIdx + 1), 0)
                    if deviceCompactDescr is not 0:
                        BigWorld.player().inventory.equipOptionalDevice(vehicle.invID, deviceCompactDescr, slotIdx, False, None)
                        LOG_DEBUG('equip', vehicle.name, slotIdx, deviceCompactDescr)
    except:
        LOG_CURRENT_EXCEPTION()
        pass


def removeAllRemovableDevicesFromAllVehicle(curVehicle):
    try:
        vehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
        for vehicle in vehicles:
            if curVehicle is not vehicle:
                if vehicle and not (vehicle.isInBattle or vehicle.isLocked):
                    for slotIdx in range(0, 3):
                        device = vehicle.descriptor.optionalDevices[slotIdx]
                        if device and device.removable:
                            BigWorld.player().inventory.equipOptionalDevice(vehicle.invID, 0, slotIdx, False, None)
    except:
        LOG_CURRENT_EXCEPTION()
        pass


def equipCurrentVehicle():
    global g_prevVehicle
    if g_currentVehicle.isInHangar:
        curVehicle = g_currentVehicle.item
        if g_prevVehicle is not curVehicle:
            if g_prevVehicle and curVehicle:
                if g_prevVehicle.name is not curVehicle.name:
                    removeAllRemovableDevicesFromAllVehicle(curVehicle)
                    equipAllRemovableDevicesOnVehicle(curVehicle)
            g_prevVehicle = curVehicle


def new_recreateVehicle(self, vDesc, vState, onVehicleLoadedCallback):
    old_recreateVehicle(self, vDesc, vState, onVehicleLoadedCallback)
    equipCurrentVehicle()


def saveDeviceOnVehicle(vehicle, deviceId, slotId, isRemove):
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


def onAccountShowGUI(ctx):
    global old_setVehicleModule
    global old_recreateVehicle
    global g_xmlSetting
    global g_prevVehicle
    global g_started
    msg = __name__ + ' 0.9.10 started'

    if g_started:
        return
    g_xmlSetting = ResMgr.openSection('scripts/client/gui/mods/mod_auto_equip.xml', True)
    if not g_xmlSetting:
        g_xmlSetting.save()
    old_setVehicleModule = AmmunitionPanel.setVehicleModule
    AmmunitionPanel.setVehicleModule = new_setVehicleModule
    old_recreateVehicle = ClientHangarSpace.recreateVehicle
    ClientHangarSpace.recreateVehicle = new_recreateVehicle
    SystemMessages.pushMessage(msg)
    LOG_NOTE(msg)
    if g_currentVehicle.isInHangar:
        g_prevVehicle = g_currentVehicle.item
    g_started = True


init = lambda : None
fini = lambda : None
onAccountBecomePlayer = lambda : None
onAccountBecomeNonPlayer = lambda : None
onAvatarBecomePlayer = lambda : None
#onAccountShowGUI = lambda ctx : None

