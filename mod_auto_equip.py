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
g_autoEquip = True
g_returnCrew = True


def equipOptionalDevices(curVehicle):
    if g_xmlSetting[curVehicle.name]:
        for slotIdx in range(0, 3):
            device = curVehicle.descriptor.optionalDevices[slotIdx]
            if not device:
                deviceCompactDescr = g_xmlSetting[curVehicle.name].readInt('slot' + str(slotIdx + 1), 0)
                if deviceCompactDescr is not 0:
                    BigWorld.player().inventory.equipOptionalDevice(curVehicle.invID, deviceCompactDescr, slotIdx, False, None)
                    LOG_NOTE('equip', curVehicle.name, slotIdx, deviceCompactDescr)


def removeAllOptionalDevicesFromVehicle(vehicle):
    if vehicle and not (vehicle.isInBattle or vehicle.isLocked):
        for slotIdx in range(0, 3):
            device = vehicle.descriptor.optionalDevices[slotIdx]
            if device and device.removable:
                BigWorld.player().inventory.equipOptionalDevice(vehicle.invID, 0, slotIdx, False, None)
                LOG_NOTE('remove:', vehicle.name, slotIdx, device.name)


def removeAllOptionalDevices(curVehicle):
    vehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
    for vehicle in vehicles:
        if curVehicle.intCD != vehicle.intCD:
            removeAllOptionalDevicesFromVehicle(vehicle)


def returnCrew(curVehicle):
    if not curVehicle.isCrewFull:
        BigWorld.player().inventory.returnCrew(curVehicle.invID, None)
        LOG_NOTE('return crew: %s' % curVehicle.name)


def equipCurrentVehicle():
    if g_vAppearance is not None:
        if g_vAppearance._VehicleAppearance__isLoaded:
            if g_currentVehicle.isInHangar():
                curVehicle = g_currentVehicle.item
                #LOG_NOTE('try to equip: %s' % curVehicle.name)
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


def saveDeviceOnVehicle(vehicle, deviceId, slotId, isRemove):
    LOG_NOTE('save', vehicle.name, slotId, deviceId)
    g_xmlSetting.write(vehicle.name, '')
    if isRemove:
        g_xmlSetting[vehicle.name].writeInt('slot' + str(slotId + 1), 0)
    else:
        g_xmlSetting[vehicle.name].writeInt('slot' + str(slotId + 1), int(deviceId))
    g_xmlSetting.save()


def new_setVehicleModule(self, newId, slotIdx, oldId, isRemove):
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
    global g_autoEquip
    global g_returnCrew
    global g_prevVehicleID
    global g_started
    global old_setVehicleModule
    global old_recreateVehicle
    if g_started: return
    g_xmlSetting = ResMgr.openSection('scripts/client/gui/mods/mod_auto_equip.xml', True)
    if g_xmlSetting:
        g_autoEquip = g_xmlSetting.readBool('autoEquip', True)
        g_returnCrew = g_xmlSetting.readBool('returnCrew', True)
    else:
        g_xmlSetting.writeBool('autoEquip', True)
        g_xmlSetting.writeBool('returnCrew', True)
        g_xmlSetting.save()
    g_prevVehicleID = g_currentVehicle.item.intCD
    old_setVehicleModule = AmmunitionPanel.setVehicleModule
    AmmunitionPanel.setVehicleModule = new_setVehicleModule
    old_recreateVehicle = ClientHangarSpace.recreateVehicle
    ClientHangarSpace.recreateVehicle = new_recreateVehicle
    SystemMessages.pushMessage('Hangar Mod 0.9.10 started')
    g_started = True

