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
        self.battlePeriod = False
        self.startTime = 0
        self.drum_tanks = {}
        self.visible_list = []
        self.enemies_list = {}
        self.allies_list = {}
        self.timer_list = {}
        self.markers = {}
        self.shoot_timer_list = {}
        self.timeoutReload = {}
        self.config()
        self.module()
        BigWorld.logInfo('NOTE', 'package loaded: mod_reload', None)

    def config(self):
        self.active = True
        self.allies = False
        self.alliesAtStart = False
        self.unvisible = True
        self.bonusBrotherhood = True
        self.bonusStimulator = False
        self.bonusAuto = True
        self.timeoutAutoReload = True
        self.timeoutReloadDelay = 3.0
        self.timeReloadCorrect = 0.0
        self.SWF_FILE_NAME_ENEMIES = 'marker_red.swf'
        self.SWF_FILE_NAME_ALLIES = 'marker_green.swf'
        self.marker_timeUpdate = 0.3
        self.marker_timeCorrect = 0.3
        self.config = ResMgr.openSection('scripts/client/gui/mods/mod_reload.xml')
        if self.config:
            self.allies = self.config.readBool('allies', False)
            self.alliesAtStart = self.config.readBool('alliesAtStart', self.allies)
            self.unvisible = self.config.readBool('unvisible', True)
            self.bonusBrotherhood = self.config.readBool('bonusBrotherhood', True)
            self.bonusStimulator = self.config.readBool('bonusStimulator', False)
            self.bonusAuto = self.config.readBool('bonusAuto', True)
            self.timeoutAutoReload = self.config.readBool('timeoutAutoReload', True)
            self.timeoutReloadDelay = self.config.readFloat('timeoutReloadDelay', 3.0)
            self.timeReloadCorrect = self.config.readFloat('timeReloadCorrect', 0.0)
            self.SWF_FILE_NAME_ENEMIES = self.config.readString('enemiesMarker', 'marker_red.swf')
            self.SWF_FILE_NAME_ALLIES = self.config.readString('alliesMarker', 'marker_green.swf')
            self.marker_timeUpdate = self.config.readFloat('marker_timeUpdate', 0.3)
            self.marker_timeCorrect = self.config.readFloat('marker_timeCorrect', 0.3)
        return

    def clear(self):
        self.visible_list = []
        self.enemies_list = {}
        self.allies_list = {}
        self.timer_list = {}
        self.markers = {}
        self.drum_tanks = {}
        self.shoot_timer_list = {}
        self.timeoutReload = {}
        self.startTime = 0

    def module(self):
       
        def isRemaining(id):
            return isBattleOn() and isAlive(id) and not isPlayer(id)

        def isPlayer(id):
            return BigWorld.player().playerVehicleID == id

        def isBattleOn():
            return hasattr(BigWorld.player(), 'arena')

        def isAlive(id):
            veh = BigWorld.player().arena.vehicles.get(id)
            if veh:
                return isBattleOn() and veh['isAlive']
            else:
                return False

        def isFriend(id):
            return isBattleOn() and BigWorld.player().arena.vehicles[BigWorld.player().playerVehicleID]['team'] == BigWorld.player().arena.vehicles[id]['team']

        def new_showTracer(current, shooterID, shotID, isRicochet, effectsIndex, refStartPoint, velocity, gravity, maxShotDist):
            old_showTracer(current, shooterID, shotID, isRicochet, effectsIndex, refStartPoint, velocity, gravity, maxShotDist)
            markerAction(shooterID)

        old_showTracer = PlayerAvatar.showTracer
        PlayerAvatar.showTracer = new_showTracer

        def markerAction(id):
            global SWF_FILE_NAME
            if isRemaining(id):
                reload_time = calculateReload(id)
                if reload_time > 1.0 and self.active:
                    flashID = str(''.join([str(id), 'vehicleMarkersManager']))
                    if not isFriend(id):
                        SWF_FILE_NAME = self.SWF_FILE_NAME_ENEMIES
                    else:
                        SWF_FILE_NAME = self.SWF_FILE_NAME_ALLIES
                    try:
                        marker = VehicleMarkersManager()
                        self.markers[flashID] = marker
                        marker.start(flashID)
                        marker_handle = marker.createMarker(BigWorld.entity(id))
                        if marker_handle is not None:
                            timeout = BigWorld.time() + reload_time + self.marker_timeCorrect
                            marker.showActionMarker(marker_handle, 'attack', int(reload_time))
                    except:
                        LOG_CURRENT_EXCEPTION()
                        return
                    finally:

                        def markerCheck():
                            try:
                                stop_mark = True
                                if isRemaining(id) and self.active and not (isFriend(id) and not self.allies):
                                    if BigWorld.time() < timeout:
                                        if self.markers[flashID] == marker:
                                            stop_mark = False
                                if stop_mark or not self.unvisible and id not in self.visible_list:
                                    marker.destroy_light(flashID)
                                else:
                                    BigWorld.callback(self.marker_timeUpdate, markerCheck)
                            except:
                                marker.destroy_light(flashID)

                        markerCheck()

        def getBonus(id):
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

        def timeoutNoShoot(id):
            if id in self.timeoutReload:
                del self.timeoutReload[id]
            if id in self.shoot_timer_list:
                timer = BigWorld.time() - self.shoot_timer_list[id]
                veh = BigWorld.player().arena.vehicles.get(id)
                reloadTime = veh['vehicleType'].gun['reloadTime']
                ammo = self.drum_tanks[id]['ammo']
                if not isFriend(id):
                    self.enemies_list.update({id: {'ammo': ammo, 'time': self.shoot_timer_list[id]}})
                else:
                    self.allies_list.update({id: {'ammo': ammo, 'time': self.shoot_timer_list[id]}})

        def calculateReload(id):
            try:
                veh = BigWorld.player().arena.vehicles.get(id)
                reloadTime = veh['vehicleType'].gun['reloadTime']
                bonusReloadTime = reloadTime * getBonus(id)
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
                if id not in self.drum_tanks:
                    if not isFriend(id):
                        self.enemies_list[id]['time'] = time
                    else:
                        self.allies_list[id]['time'] = time
                    self.timer_list.update({id: {'time': time, 'shootFlag': True}})
                    return bonusReloadTime
                if self.timeoutAutoReload:
                    self.shoot_timer_list.update({id: time})
                    if id in self.timeoutReload:
                        BigWorld.cancelCallback(self.timeoutReload[id])
                    self.timeoutReload.update({id: BigWorld.callback(self.drum_tanks[id]['reloadTime'] * getBonus(id) + self.timeoutReloadDelay, partial(timeoutNoShoot, id))})
                if not isFriend(id):
                    ammo = self.enemies_list[id]['ammo']
                    if ammo > 1:
                        ammo -= 1
                        bonusReloadTime = self.drum_tanks[id]['clipReloadTime']
                    else:
                        self.timer_list.update({id: {'time': time, 'shootFlag': True}})
                        ammo = self.drum_tanks[id]['ammo']
                        if id in self.shoot_timer_list:
                            del self.shoot_timer_list[id]
                    self.enemies_list.update({id: {'ammo': ammo, 'time': time}})
                if isFriend(id):
                    ammo = self.allies_list[id]['ammo']
                    if ammo > 1:
                        ammo -= 1
                        bonusReloadTime = self.drum_tanks[id]['clipReloadTime']
                    else:
                        self.timer_list.update({id: {'time': time, 'shootFlag': True}})
                        ammo = self.drum_tanks[id]['ammo']
                        if id in self.shoot_timer_list:
                            del self.shoot_timer_list[id]
                    self.allies_list.update({id: {'ammo': ammo, 'time': time}})
                return bonusReloadTime
            except:
                return 0

        def new_vehicle_onEnterWorld(current, vehicle):
            old_vehicle_onEnterWorld(current, vehicle)
            if not self.battlePeriod:
                return
            id = vehicle.id
            if not isAlive(id) or isPlayer(id):
                return
            if id not in self.visible_list:
                self.visible_list.append(id)
            veh = BigWorld.player().arena.vehicles.get(id)
            reloadTime = veh['vehicleType'].gun['reloadTime']
            clip = veh['vehicleType'].gun['clip']
            if clip[0] > 1:
                if id not in self.drum_tanks:
                    self.drum_tanks.update({id: {'reloadTime': reloadTime, 'clipReloadTime': clip[1], 'ammo': clip[0]}})
            time = BigWorld.time()
            battleTime = time - self.startTime
            bonusReloadTime = reloadTime * getBonus(id)
            if id in self.timer_list:
                reloadTimeResidue = bonusReloadTime - (time - self.timer_list[id]['time'])
                if reloadTimeResidue > 0:
                    self.timer_list[id]['shootFlag'] = False
                    markerAction(id)
                    return
            if not isFriend(id):
                if id not in self.enemies_list:
                    ammo = 1
                    self.enemies_list.update({id: {'ammo': ammo, 'time': time - bonusReloadTime}})
                if id in self.drum_tanks:
                    rlt = bonusReloadTime
                    bonusReloadTime = self.drum_tanks[id]['clipReloadTime']
                    timer = time - self.enemies_list[id]['time']
                    if timer >= bonusReloadTime - self.timeReloadCorrect:
                        ammo = self.drum_tanks[id]['ammo']
                        self.enemies_list[id]['ammo'] = ammo
                        bonusReloadTime = rlt
            if isFriend(id):
                if id not in self.allies_list:
                    ammo = 1
                    self.allies_list.update({id: {'ammo': ammo, 'time': time - bonusReloadTime}})
                if id in self.drum_tanks:
                    rlt = bonusReloadTime
                    bonusReloadTime = self.drum_tanks[id]['clipReloadTime']
                    timer = time - self.allies_list[id]['time']
                    if timer >= bonusReloadTime - self.timeReloadCorrect:
                        ammo = self.drum_tanks[id]['ammo']
                        self.allies_list[id]['ammo'] = ammo
                        bonusReloadTime = rlt
            if bonusReloadTime > battleTime:
                markerAction(id)
        
        old_vehicle_onEnterWorld = PlayerAvatar.vehicle_onEnterWorld
        PlayerAvatar.vehicle_onEnterWorld = new_vehicle_onEnterWorld

        def new_vehicle_onLeaveWorld(current, vehicle):
            old_vehicle_onLeaveWorld(current, vehicle)
            id = vehicle.id
            if id in self.visible_list:
                self.visible_list.remove(id)
 
        old_vehicle_onLeaveWorld = PlayerAvatar.vehicle_onLeaveWorld
        PlayerAvatar.vehicle_onLeaveWorld = new_vehicle_onLeaveWorld

        def onVehicleKilled(targetID, atackerID, *args):
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
            BigWorld.player().arena.onVehicleKilled += onVehicleKilled
            self.battlePeriod = False
            self.clear()
            old_startBattle(current)

        old_startBattle = Battle.afterCreate
        Battle.afterCreate = new_startBattle

        def new_stopBattle(current):
            BigWorld.player().arena.onVehicleKilled -= onVehicleKilled
            self.battlePeriod = False
            self.clear()
            old_stopBattle(current)

        old_stopBattle = Battle.beforeDelete
        Battle.beforeDelete = new_stopBattle

        def vehicles_to_list():
            for id, entityVehicle in BigWorld.entities.items():
                if isinstance(entityVehicle, Vehicle.Vehicle) and not isPlayer(id):
                    veh = BigWorld.player().arena.vehicles.get(id)
                    reloadTime = veh['vehicleType'].gun['reloadTime']
                    clip = veh['vehicleType'].gun['clip']
                    if clip[0] > 1:
                        self.drum_tanks.update({id: {'reloadTime': reloadTime, 'clipReloadTime': clip[1], 'ammo': clip[0]}})
                    if id not in self.visible_list:
                        self.visible_list.append(id)
                    if not isFriend(id):
                        if id not in self.enemies_list:
                            ammo = 1
                            self.enemies_list.update({id: {'ammo': ammo, 'time': 0}})
                        if id in self.drum_tanks:
                            ammo = self.drum_tanks[id]['ammo']
                            self.enemies_list[id]['ammo'] = ammo
                    if isFriend(id):
                        if id not in self.allies_list:
                            ammo = 1
                            self.allies_list.update({id: {'ammo': ammo, 'time': 0}})
                        if id in self.drum_tanks:
                            ammo = self.drum_tanks[id]['ammo']
                            self.allies_list[id]['ammo'] = ammo

        def new_onArenaPeriodChange(current, period, periodEndTime, periodLength, periodAdditionalInfo):
            old_onArenaPeriodChange(current, period, periodEndTime, periodLength, periodAdditionalInfo)
            if period == ARENA_PERIOD.PREBATTLE:
                vehicles_to_list()
            if period == ARENA_PERIOD.BATTLE:
                self.battlePeriod = True
                self.startTime = BigWorld.time()
                if self.alliesAtStart:
                    for id in self.allies_list:
                        markerAction(id)

        old_onArenaPeriodChange = PlayerAvatar._PlayerAvatar__onArenaPeriodChange
        PlayerAvatar._PlayerAvatar__onArenaPeriodChange = new_onArenaPeriodChange

RM = ReloadMarkers()


import weakref
import GUI
from gui.Scaleform.Flash import Flash

class VehicleMarkersManager(Flash):
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
        if not vProxy: return None
        if not vProxy.model: return None
        mProv = vProxy.model.node('HP_gui')
        handle = self.__ownUI.addMarker(mProv, 'VehicleMarkerEnemy')
        self.invokeMarker(handle, 'init')
        return handle

    def showActionMarker(self, handle, newState = '', time_value = 0):
        self.invokeMarker(handle, 'showActionMarker', [newState, time_value])

    def invokeMarker(self, handle, function, args = None):
        if handle != -1:
            self.__ownUI.markerInvoke(handle, (function, args))

