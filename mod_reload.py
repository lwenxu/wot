import BigWorld
import ResMgr
import Vehicle
from messenger import MessengerEntry
from Avatar import PlayerAvatar
from Account import PlayerAccount
from gui import SystemMessages
from gui.Scaleform.Battle import Battle
from gui.app_loader import g_appLoader
import constants
from constants import ARENA_PERIOD
from debug_utils import *
from functools import partial


SWF_FILE_NAME = 'marker_red.swf'

class ReloadMarkers(object):

    def __init__(self):
        self.name = 'MetaTarge'
        self.arenaPeriod = False
        self.startTime = 0
        self.extTanks = {}
        self.visible_list = []
        self.enemies_list = {}
        self.allies_list = {}
        self.timer_list = {}
        self.mod_markers = {}
        self.shoot_timer_list = {}
        self.timeOutReload = {}
        self.config()
        self.module()
        BigWorld.logInfo(self.name, 'mod is started', None)

    def config(self):
        self.active = True
        self.allies = False
        self.alliesAtStart = False
        self.unvisible = True
        self.bonusBrotherhood = True
        self.bonusStimulator = False
        self.bonusAuto = True
        self.timeOutAutoReload = True
        self.timeOutReloadDelay = 3.0
        self.timeReloadCorrect = 0.0
        self.SWF_FILE_NAME_ENEMIES = 'marker_red.swf'
        self.SWF_FILE_NAME_ALLIES = 'marker_green.swf'
        self.marker_timeUpdate = 0.5
        self.marker_timeCorrect = 0.5
        self.config = ResMgr.openSection('scripts/client/gui/mods/mod_reload.xml')
        if self.config:
            self.allies = self.config.readBool('allies', False)
            self.alliesAtStart = self.config.readBool('alliesAtStart', self.allies)
            self.unvisible = self.config.readBool('unvisible', True)
            self.bonusBrotherhood = self.config.readBool('bonusBrotherhood', True)
            self.bonusStimulator = self.config.readBool('bonusStimulator', False)
            self.bonusAuto = self.config.readBool('bonusAuto', True)
            self.timeOutAutoReload = self.config.readBool('timeOutAutoReload', True)
            self.timeOutReloadDelay = self.config.readFloat('timeOutReloadDelay', 3.0)
            self.timeReloadCorrect = self.config.readFloat('timeReloadCorrect', 0.0)
            self.SWF_FILE_NAME_ENEMIES = self.config.readString('enemiesMarker', 'marker_red.swf')
            self.SWF_FILE_NAME_ALLIES = self.config.readString('alliesMarker', 'marker_green.swf')
            self.marker_timeUpdate = self.config.readFloat('marker_timeUpdate', 0.5)
            self.marker_timeCorrect = self.config.readFloat('marker_timeCorrect', 0.5)
        else:
            LOG_WARNING('config not found')
        return

    def clear(self):
        self.visible_list = []
        self.enemies_list = {}
        self.allies_list = {}
        self.timer_list = {}
        self.mod_markers = {}
        self.extTanks = {}
        self.shoot_timer_list = {}
        self.timeOutReload = {}
        self.startTime = 0

    def module(self):
       
        def isRemaining(id):
            return isBattleOn() and isAlive(id) and not isPlayer(id)

        def isPlayer(id):
            return BigWorld.player().playerVehicleID == id

        def isBattleOn():
            return hasattr(BigWorld.player(), 'arena')

        def isAlive(id):
            if isBattleOn():
                return BigWorld.player().arena.vehicles.get(id)['isAlive']
            else:
                return False

        def isFriend(id):
            return isBattleOn() and BigWorld.player().arena.vehicles[BigWorld.player().playerVehicleID]['team'] == BigWorld.player().arena.vehicles[id]['team']

        def new_showTracer(current, shooterID, shotID, isRicochet, effectsIndex, refStartPoint, velocity, gravity, maxShotDist):
            old_showTracer(current, shooterID, shotID, isRicochet, effectsIndex, refStartPoint, velocity, gravity, maxShotDist)
            __Reloading__Marker_Action(shooterID)

        old_showTracer = PlayerAvatar.showTracer
        PlayerAvatar.showTracer = new_showTracer

        def __Reloading__Marker_Action(id):
            global SWF_FILE_NAME
            if isRemaining(id):
                reload_time = __calculateReload(id)
                if reload_time > 1.0 and self.active:
                    flashID = str(''.join([str(id), 'vehicleMarkersManager']))
                    if not isFriend(id):
                        SWF_FILE_NAME = self.SWF_FILE_NAME_ENEMIES
                    else:
                        SWF_FILE_NAME = self.SWF_FILE_NAME_ALLIES
                    Mod_Marker = _VehicleMarkersManager()
                    self.mod_markers[flashID] = Mod_Marker
                    Mod_Marker.start(flashID)
                    try:
                        mm_handle = Mod_Marker.createMarker(BigWorld.entity(id))
                        if mm_handle is not None:
                            enout = BigWorld.time() + reload_time + self.marker_timeCorrect
                            Mod_Marker.showActionMarker(mm_handle, 'attack', int(reload_time))
                    except:
                        return
                    finally:

                        def marker_check():
                            try:
                                stop_mark = True
                                if isRemaining(id) and self.active and not (isFriend(id) and not self.allies):
                                    if BigWorld.time() < enout:
                                        if self.mod_markers[flashID] == Mod_Marker:
                                            stop_mark = False
                                if stop_mark or not self.unvisible and id not in self.visible_list:
                                    Mod_Marker.destroy_light(flashID)
                                else:
                                    BigWorld.callback(self.marker_timeUpdate, marker_check)
                            except:
                                Mod_Marker.destroy_light(flashID)

                        marker_check()

        def __GetBonus(id):
            try:
                ventil_bonus = False
                rammer_bonus = False
                comander = 100
                loader = 100
                veh = BigWorld.player().arena.vehicles.get(id)
                for item in veh['vehicleType'].optionalDevices:
                    if item is not None and 'improvedVentilation' in item.name:
                        ventil_bonus = True
                    if item is not None and 'Rammer' in item.name:
                        rammer_bonus = True
                        continue
                bonusVBS = 0
                if ventil_bonus:
                    bonusVBS += 5
                arena_type = BigWorld.player().arena.guiType
                is_prof_arena = (arena_type == constants.ARENA_GUI_TYPE.COMPANY)
                if self.bonusBrotherhood or (self.bonusAuto and is_prof_arena):
                    bonusVBS += 5
                if self.bonusStimulator or (self.bonusAuto and is_prof_arena):
                    bonusVBS += 10
                comander_bonus = comander + bonusVBS
                loader_bonus = comander_bonus * 0.1 + bonusVBS + loader
                bonus = 1 / (1 + (loader_bonus - 100) * 0.00434294482)
                if rammer_bonus:
                    bonus *= 0.9
                return bonus
            except:
                return 1

        def __timeOutNoShoot(id):
            if id in self.timeOutReload:
                del self.timeOutReload[id]
            if id in self.shoot_timer_list:
                timer = BigWorld.time() - self.shoot_timer_list[id]
                veh = BigWorld.player().arena.vehicles.get(id)
                #shortUserString = veh['vehicleType'].type.shortUserString
                reloadTime = veh['vehicleType'].gun['reloadTime']
                ammo = self.extTanks[id]['ammo']
                if not isFriend(id):
                    self.enemies_list.update({id: {'ammo': ammo, 'time': self.shoot_timer_list[id]}})
                else:
                    self.allies_list.update({id: {'ammo': ammo, 'time': self.shoot_timer_list[id]}})

        def __calculateReload(id):
            try:
                veh = BigWorld.player().arena.vehicles.get(id)
                #shortUserString = veh['vehicleType'].type.shortUserString
                reloadTime = veh['vehicleType'].gun['reloadTime']
                bonusReloadTime = reloadTime * __GetBonus(id)
                time = BigWorld.time()
                battleTime = time - self.startTime
                if bonusReloadTime > battleTime:
                    bonusReloadTime -= battleTime
                    return bonusReloadTime
                if id in self.timer_list:
                    if not self.timer_list[id]['shootFlag']:
                        reloadTimeResidue = bonusReloadTime - (time - self.timer_list[id]['time'])
                        if reloadTimeResidue > 0:
                            if id in self.timer_list:
                                del self.timer_list[id]
                            return reloadTimeResidue
                if id not in self.extTanks:
                    if not isFriend(id):
                        self.enemies_list[id]['time'] = time
                    else:
                        self.allies_list[id]['time'] = time
                    self.timer_list.update({id: {'time': time, 'shootFlag': True}})
                    return bonusReloadTime
                if self.timeOutAutoReload:
                    self.shoot_timer_list.update({id: time})
                    if id in self.timeOutReload:
                        BigWorld.cancelCallback(self.timeOutReload[id])
                    self.timeOutReload.update({id: BigWorld.callback(self.extTanks[id]['reloadTime'] * __GetBonus(id) + self.timeOutReloadDelay, partial(__timeOutNoShoot, id))})
                if not isFriend(id):
                    ammo = self.enemies_list[id]['ammo']
                    if ammo > 1:
                        ammo -= 1
                        bonusReloadTime = self.extTanks[id]['clipReloadTime']
                    else:
                        self.timer_list.update({id: {'time': time, 'shootFlag': True}})
                        ammo = self.extTanks[id]['ammo']
                        if id in self.shoot_timer_list:
                            del self.shoot_timer_list[id]
                    self.enemies_list.update({id: {'ammo': ammo, 'time': time}})
                if isFriend(id):
                    ammo = self.allies_list[id]['ammo']
                    if ammo > 1:
                        ammo -= 1
                        bonusReloadTime = self.extTanks[id]['clipReloadTime']
                    else:
                        self.timer_list.update({id: {'time': time, 'shootFlag': True}})
                        ammo = self.extTanks[id]['ammo']
                        if id in self.shoot_timer_list:
                            del self.shoot_timer_list[id]
                    self.allies_list.update({id: {'ammo': ammo, 'time': time}})
                return bonusReloadTime
            except:
                return 0

        def new_vehicle_onEnterWorld(current, vehicle):
            old_vehicle_onEnterWorld(current, vehicle)
            if not self.arenaPeriod:
                return
            if not isAlive(vehicle.id) or isPlayer(vehicle.id):
                return
            id = vehicle.id
            if id not in self.visible_list:
                self.visible_list.append(id)
            veh = BigWorld.player().arena.vehicles.get(id)
            #shortUserString = veh['vehicleType'].type.shortUserString
            reloadTime = veh['vehicleType'].gun['reloadTime']
            clip = veh['vehicleType'].gun['clip']
            burst = veh['vehicleType'].gun['burst']
            if clip[0] > 1:
                if id not in self.extTanks:
                    self.extTanks.update({id: {'reloadTime': reloadTime, 'clipReloadTime': clip[1], 'ammo': clip[0]}})
            time = BigWorld.time()
            battleTime = time - self.startTime
            bonusReloadTime = reloadTime * __GetBonus(id)
            if id in self.timer_list:
                reloadTimeResidue = bonusReloadTime - (time - self.timer_list[id]['time'])
                if reloadTimeResidue > 0:
                    self.timer_list[id]['shootFlag'] = False
                    __Reloading__Marker_Action(id)
                    return
            if not isFriend(id):
                if id not in self.enemies_list:
                    ammo = 1
                    self.enemies_list.update({id: {'ammo': ammo, 'time': time - bonusReloadTime}})
                if id in self.extTanks:
                    rlt = bonusReloadTime
                    bonusReloadTime = self.extTanks[id]['clipReloadTime']
                    timer = time - self.enemies_list[id]['time']
                    if timer >= bonusReloadTime - self.timeReloadCorrect:
                        ammo = self.extTanks[id]['ammo']
                        self.enemies_list[id]['ammo'] = ammo
                        bonusReloadTime = rlt
            if isFriend(id):
                if id not in self.allies_list:
                    ammo = 1
                    self.allies_list.update({id: {'ammo': ammo, 'time': time - bonusReloadTime}})
                if id in self.extTanks:
                    rlt = bonusReloadTime
                    bonusReloadTime = self.extTanks[id]['clipReloadTime']
                    timer = time - self.allies_list[id]['time']
                    if timer >= bonusReloadTime - self.timeReloadCorrect:
                        ammo = self.extTanks[id]['ammo']
                        self.allies_list[id]['ammo'] = ammo
                        bonusReloadTime = rlt
            if bonusReloadTime > battleTime:
                __Reloading__Marker_Action(id)
        
        old_vehicle_onEnterWorld = PlayerAvatar.vehicle_onEnterWorld
        PlayerAvatar.vehicle_onEnterWorld = new_vehicle_onEnterWorld

        def new_vehicle_onLeaveWorld(current, vehicle):
            old_vehicle_onLeaveWorld(current, vehicle)
            id = vehicle.id
            if id in self.visible_list:
                self.visible_list.remove(id)
 
        old_vehicle_onLeaveWorld = PlayerAvatar.vehicle_onLeaveWorld
        PlayerAvatar.vehicle_onLeaveWorld = new_vehicle_onLeaveWorld

        def __onVehicleKilled(targetID, atackerID, *args):
            id = targetID
            if id in self.visible_list:
                self.visible_list.remove(id)
            if self.enemies_list.has_key(id):
                del self.enemies_list[id]
            if self.allies_list.has_key(id):
                del self.allies_list[id]
            if self.timer_list.has_key(id):
                del self.timer_list[id]
            if self.shoot_timer_list.has_key(id):
                del self.shoot_timer_list[id]

        def new_startBattle(current):
            BigWorld.player().arena.onVehicleKilled += __onVehicleKilled
            self.arenaPeriod = False
            self.clear()
            old_startBattle(current)

        old_startBattle = Battle.afterCreate
        Battle.afterCreate = new_startBattle

        def new_stopBattle(current):
            BigWorld.player().arena.onVehicleKilled -= __onVehicleKilled
            self.arenaPeriod = False
            self.clear()
            old_stopBattle(current)

        old_stopBattle = Battle.beforeDelete
        Battle.beforeDelete = new_stopBattle

        def vehicles_to_list():
            for id, entityVehicle in BigWorld.entities.items():
                if isinstance(entityVehicle, Vehicle.Vehicle) and not isPlayer(id):
                    veh = BigWorld.player().arena.vehicles.get(id)
                    #shortUserString = veh['vehicleType'].type.shortUserString
                    reloadTime = veh['vehicleType'].gun['reloadTime']
                    clip = veh['vehicleType'].gun['clip']
                    if clip[0] > 1:
                        self.extTanks.update({id: {'reloadTime': reloadTime, 'clipReloadTime': clip[1], 'ammo': clip[0]}})
                    if id not in self.visible_list:
                        self.visible_list.append(id)
                    if not isFriend(id):
                        if id not in self.enemies_list:
                            ammo = 1
                            self.enemies_list.update({id: {'ammo': ammo, 'time': 0}})
                        if id in self.extTanks:
                            ammo = self.extTanks[id]['ammo']
                            self.enemies_list[id]['ammo'] = ammo
                    if isFriend(id):
                        if id not in self.allies_list:
                            ammo = 1
                            self.allies_list.update({id: {'ammo': ammo, 'time': 0}})
                        if id in self.extTanks:
                            ammo = self.extTanks[id]['ammo']
                            self.allies_list[id]['ammo'] = ammo

        def new_onArenaPeriodChange(current, period, periodEndTime, periodLength, periodAdditionalInfo):
            old_onArenaPeriodChange(current, period, periodEndTime, periodLength, periodAdditionalInfo)
            if period == ARENA_PERIOD.PREBATTLE:
                vehicles_to_list()
            if period == ARENA_PERIOD.BATTLE:
                self.arenaPeriod = True
                self.startTime = BigWorld.time()
                if self.alliesAtStart:
                    for id in self.allies_list:
                        __Reloading__Marker_Action(id)

        old_onArenaPeriodChange = PlayerAvatar._PlayerAvatar__onArenaPeriodChange
        PlayerAvatar._PlayerAvatar__onArenaPeriodChange = new_onArenaPeriodChange

RM = ReloadMarkers()


import weakref
import GUI
from gui.Scaleform.Flash import Flash

class _VehicleMarkersManager(Flash):
    __FLASH_CLASS = 'Flash'
    __FLASH_PATH = 'objects/reload'
    __FLASH_ARGS = None

    def __init__(self):
        Flash.__init__(self, SWF_FILE_NAME, self.__FLASH_CLASS, self.__FLASH_ARGS, self.__FLASH_PATH)
        self.component.wg_inputKeyMode = 2
        self.component.drawWithRestrictedViewPort = False
        self.movie.backgroundAlpha = 0
        self.__parentUI = weakref.proxy(g_appLoader.getDefBattleApp())
        self.__parentUIcomp = self.__parentUI.component
        self.__ownUI = None
        return

    def start(self, flashID):
        self.active(True)
        self.__ownUI = GUI.WGVehicleMarkersCanvasFlash(self.movie)
        self.__ownUI.wg_inputKeyMode = 2
        self.__ownUIProxy = weakref.proxy(self.__ownUI)
        self.__parentUIcomp.addChild(self.__ownUI, flashID)

    def destroy_light(self, flashID):
        self.__parentUI = None
        self.__ownUI = None
        self.close()
        return

    def destroy(self, flashID):
        if self.__parentUIcomp is not None:
            if hasattr(self.__parentUIcomp, flashID):
                setattr(self.__parentUIcomp, flashID, None)
        self.__parentUI = None
        self.__ownUI = None
        self.close()
        return

    def createMarker(self, vProxy):
        mProv = vProxy.model.node('HP_gui')
        handle = self.__ownUI.addMarker(mProv, 'VehicleMarkerEnemy')
        self.invokeMarker(handle, 'init', [])
        return handle

    def showActionMarker(self, handle, newState = '', time_value = 0):
        self.invokeMarker(handle, 'showActionMarker', [newState, time_value])

    def invokeMarker(self, handle, function, args = None):
        if handle != -1:
            if args is None:
                args = []
            self.__ownUI.markerInvoke(handle, (function, args))
        return

