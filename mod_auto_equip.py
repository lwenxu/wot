import BigWorld
import ResMgr
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.hangar.AmmunitionPanel import AmmunitionPanel
from gui.shared import g_itemsCache, REQ_CRITERIA
from gui.shared.utils.requesters.deprecated import Requester
from adisp import process
from debug_utils import *
from gui import SystemMessages


g_or_setVehicleModule = None
g_xmlSetting = None
g_prevVehicle = None


def getDeviceInventoryCounts(inventoryDevices, device):
    invCount = 0
    try:
        invCount = inventoryDevices[inventoryDevices.index(device)].count
    except Exception:
        pass

    return invCount


def equipAllRemovableDevicesOnVehicle(vehicle):
    global g_xmlSetting

    def callback(resultID):
        pass

    if g_xmlSetting[vehicle.name]:
        for slotIdx in range(0, 3):
            device = vehicle.descriptor.optionalDevices[slotIdx]
            if not device:
                deviceCompactDescr = g_xmlSetting[vehicle.name].readInt('slot' + str(slotIdx + 1), 0)
                if deviceCompactDescr is not 0:
                    BigWorld.player().inventory.equipOptionalDevice(vehicle.invID, deviceCompactDescr, slotIdx, False, callback)


@process
def removeAllRemovableDevicesFromAllVehicle(curVehicle):

    def callback(resultID):
        pass

    deviceAllInventory = yield Requester('optionalDevice').getFromInventory()
    alreadyRemoved = []
    vehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
    for vehicle in vehicles:
        if curVehicle is not vehicle:
            if not vehicle.isInBattle:
                for slotIdx in range(0, 3):
                    device = vehicle.descriptor.optionalDevices[slotIdx]
                    if device and device.removable:
                        devCount = getDeviceInventoryCounts(deviceAllInventory, device)
                        if devCount is 0 and device.compactDescr not in alreadyRemoved:
                            BigWorld.player().inventory.equipOptionalDevice(vehicle.invID, 0, slotIdx, False, callback)
                            alreadyRemoved.append(device.compactDescr)


def onCurrentVehicleChanged(prevVehicle, curVehicle):
    removeAllRemovableDevicesFromAllVehicle(curVehicle)
    equipAllRemovableDevicesOnVehicle(curVehicle)


def vehicleCheckCallback():
    global g_prevVehicle
    if g_currentVehicle.isInHangar:
        curVehicle = g_currentVehicle.item
        if g_prevVehicle is not curVehicle:
            if g_prevVehicle and curVehicle:
                if g_prevVehicle.name is not curVehicle.name:
                    onCurrentVehicleChanged(g_prevVehicle, curVehicle)
            g_prevVehicle = curVehicle
    BigWorld.callback(0.1, vehicleCheckCallback)


def saveDeviceOnVehicle(vehicle, deviceId, slotId, isRemove):
    g_xmlSetting.write(vehicle.name, '')
    if isRemove:
        g_xmlSetting[vehicle.name].writeInt('slot' + str(slotId + 1), 0)
    else:
        g_xmlSetting[vehicle.name].writeInt('slot' + str(slotId + 1), int(deviceId))
    g_xmlSetting.save()


def hook_setVehicleModule(self, newId, slotIdx, oldId, isRemove):
    global g_or_setVehicleModule
    g_or_setVehicleModule(self, newId, slotIdx, oldId, isRemove)
    vehicle = g_currentVehicle.item
    saveDeviceOnVehicle(vehicle, newId, slotIdx, isRemove)


g_started = False

def onAccountShowGUI(ctx):
    global g_or_setVehicleModule
    global g_xmlSetting
    global g_started
    sys_msg = "mod_auto_equip 0.9.10 started"

    if g_started:
        return
    g_xmlSetting = ResMgr.openSection('scripts/client/gui/mods/mod_auto_equip.xml', True)
    if not g_xmlSetting:
        g_xmlSetting.save()
    g_or_setVehicleModule = AmmunitionPanel.setVehicleModule
    AmmunitionPanel.setVehicleModule = hook_setVehicleModule
    vehicleCheckCallback()
    SystemMessages.pushMessage(sys_msg)
    LOG_NOTE(sys_msg)
    g_started = True


init = lambda : None
fini = lambda : None
onAccountBecomePlayer = lambda : None
onAccountBecomeNonPlayer = lambda : None
onAvatarBecomePlayer = lambda : None
#onAccountShowGUI = lambda ctx : None

