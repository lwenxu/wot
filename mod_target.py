import BigWorld, ResMgr, Math, Keys
from Avatar import PlayerAvatar
from Account import PlayerAccount
from gui import SystemMessages
from gui.Scaleform.Flash import Flash
from gui.Scaleform.Minimap import Minimap
from gui.Scaleform.Battle import Battle
from tutorial.gui.Scaleform.battle.legacy import ScaleformLayout
from tutorial.gui.Scaleform.battle.layout import BattleLayout


class DirectionBox(object):

    def __init__(self):
        self.directionOption()
        self.directionModule()

    def directionConfig(self):
        self.directionRecord = {}
        self.directionDerive = {}
        self.directionConfig = ResMgr.openSection('scripts/client/mods/ModificationDirection.xml')
        if self.directionConfig:
            self.directionRecord['directionEnable'] = self.directionConfig.readInt('directionEnable', 1)
            self.directionRecord['directionMethod'] = self.directionConfig.readInt('directionMethod', 1)
            self.directionRecord['directionSquare'] = self.directionConfig.readInt('directionSquare', 500)
            self.directionRecord['directionNumber'] = self.directionConfig.readInt('directionNumber', 1)
            self.directionRecord['directionLength'] = self.directionConfig.readInt('directionLength', 1)
            self.directionRecord['directionPushed'] = getattr(Keys, self.directionConfig.readString('directionPushed', 'KEY_0'), None)
            self.directionRecord['directionReload'] = getattr(Keys, self.directionConfig.readString('directionReload', 'KEY_1'), None)
            self.directionRecord['directionButton'] = getattr(Keys, self.directionConfig.readString('directionButton', 'KEY_2'), None)

    def directionOption(self):
        self.directionRecord = {'directionEnable': 1,
         'directionMethod': 1,
         'directionSquare': 620,
         'directionNumber': 1,
         'directionLength': 1}

    def directionModule(self):
        pre_notifyEnterWorld = PlayerAvatar.onEnterWorld

        def new_notifyEnterWorld(current, prereqs):
            pre_notifyEnterWorld(current, prereqs)
            self.directionValues(current)
            self.directionParams(current)

        PlayerAvatar.onEnterWorld = new_notifyEnterWorld
        pre_notifyLeaveWorld = PlayerAvatar.onLeaveWorld

        def new_notifyLeaveWorld(current):
            pre_notifyLeaveWorld(current)
            if self.vehicleIndicate:
                self.directionRemove(self.currentIndicate)

        PlayerAvatar.onLeaveWorld = new_notifyLeaveWorld
        pre_notifyVehicleStart = Minimap.notifyVehicleStart

        def new_notifyVehicleStart(current, vInfo, guiProps):
            pre_notifyVehicleStart(current, vInfo, guiProps)
            vehicleID = vInfo.vehicleID
            if self.arenaPlayer.team is not self.arenaArenas.vehicles[vehicleID]['team'] and self.arenaArenas.vehicles[self.arenaPlayer.playerVehicleID]['isAlive']:
                if self.vehicleDistance(vehicleID) > self.directionRecord['directionSquare']:
                    self.directionBounce(vehicleID)
                if self.vehicleDistance(vehicleID) < self.directionRecord['directionSquare']:
                    if len(self.vehicleIndicate) == 0:
                        self.directionAppend(vehicleID)
                    if len(self.vehicleIndicate) == 1:
                        if self.vehicleDistance(vehicleID) < self.currentDistance:
                            self.directionMethod(vehicleID)
                        if self.vehicleDistance(vehicleID) > self.currentDistance:
                            self.directionBounce(vehicleID)

        Minimap.notifyVehicleStart = new_notifyVehicleStart
        pre_notifyVehicleStop = Minimap.notifyVehicleStop

        def new_notifyVehicleStop(current, vehicleID):
            pre_notifyVehicleStop(current, vehicleID)
            if self.arenaPlayer.team is not self.arenaArenas.vehicles[vehicleID]['team'] and self.arenaArenas.vehicles[self.arenaPlayer.playerVehicleID]['isAlive']:
                if vehicleID in self.vehicleBouncing:
                    del self.vehicleBouncing[vehicleID]
                if vehicleID in self.vehicleIndicate:
                    self.directionRemove(self.currentIndicate)
                    self.directionDelete(vehicleID)
                    self.directionRefine(vehicleID)

        Minimap.notifyVehicleStop = new_notifyVehicleStop

        def __onVehicleKilled(targetID, atackerID, *args):
            if self.arenaPlayer.team is not self.arenaArenas.vehicles[targetID]['team'] and self.arenaArenas.vehicles[self.arenaPlayer.playerVehicleID]['isAlive']:
                if targetID in self.vehicleBouncing:
                    del self.vehicleBouncing[targetID]
                if targetID in self.vehicleIndicate:
                    self.directionRemove(self.currentIndicate)
                    self.directionDelete(targetID)
                    self.directionRefine(targetID)

        def new_startBattle(current):
            BigWorld.player().arena.onVehicleKilled += __onVehicleKilled
            old_startBattle(current)

        def new_stopBattle(current):
            BigWorld.player().arena.onVehicleKilled -= __onVehicleKilled
            old_stopBattle(current)

        old_startBattle = Battle.afterCreate
        Battle.afterCreate = new_startBattle
        old_stopBattle = Battle.beforeDelete
        Battle.beforeDelete = new_stopBattle

    def directionBounce(self, callback):
        if callback not in self.vehicleBouncing:
            self.vehicleBouncing[callback] = BigWorld.time()

    def directionSelect(self, callback):
        if callback not in self.vehicleIndicate:
            self.vehicleIndicate[callback] = BigWorld.time()

    def directionParams(self, callback):
        self.vehicleIndicate = {}
        self.vehicleBouncing = {}
        self.currentCarriage = None
        self.currentDistance = None
        self.currentPosition = None
        self.currentIndicate = None
        self.callbackWilling = None
        self.callbackProcess = None
        self.indicatorShaped = None
        return

    def directionValues(self, callback):
        self.arenaPlayer = BigWorld.player()
        self.arenaSquads = self.arenaPlayer.team
        self.arenaArenas = self.arenaPlayer.arena
        self.arenaSpaces = self.arenaPlayer.spaceID
        self.arenaEntity = self.arenaPlayer.vehicle
        self.arenaRotate = self.arenaPlayer.gunRotator
        self.arenaHandle = self.arenaPlayer.inputHandler
        self.arenaSource = self.arenaPlayer.playerVehicleID

    def directionEntity(self, callback):
        return BigWorld.entity(callback)

    def directionCollid(self, callback):
        if BigWorld.wg_collideSegment(self.arenaSpaces, self.directionMatrix(self.directionEntity(callback)), self.directionMatrix(self.directionEntity(self.arenaPlayer.playerVehicleID)), False) == None:
            return 1
        elif BigWorld.wg_collideSegment(self.arenaSpaces, self.directionMatrix(self.directionEntity(callback)), self.directionMatrix(self.directionEntity(self.arenaPlayer.playerVehicleID)), False) != None:
            return 0
        #else:
        #    return

    def directionMethod(self, callback):
        if len(self.vehicleIndicate) == 0:
            self.directionAppend(callback)
        if len(self.vehicleIndicate) == 1:
            self.directionRelock(callback)

    def directionRelock(self, callback):
        self.directionRemove(self.currentIndicate)
        self.directionDelete(self.currentCarriage)
        self.directionRefine(self.currentCarriage)
        self.directionAppend(callback)

    def directionAppend(self, callback):
        self.directionRevers(callback)
        self.directionSystem(callback)

    def directionMatrix(self, callback):
        return callback.appearance.modelsDesc['gun']['model'].position

    def directionRevers(self, callback):
        if self.vehicleDecimate(callback) == 1:
            self.scaleformID = BattleLayout(ScaleformLayout)
            self.indicatorID = self.scaleformID._getDirectionIndicator()
            self.currentCarriage = callback
            self.currentDistance = self.vehicleDistance(callback)
            self.currentPosition = self.directionEntity(callback).position
            self.currentIndicate = self.indicatorID
            self.indicatorID.setDistance(self.currentDistance)
            self.indicatorID.track(self.directionEntity(callback).position)
            self.directionShapes(callback)
            self.directionSelect(callback)
            self.directionBounce(callback)
        if self.vehicleDecimate(callback) == 0:
            if callback in self.vehicleBouncing:
                del self.vehicleBouncing[callback]
            if callback in self.vehicleIndicate:
                self.directionRemove(self.currentIndicate)
                self.directionDelete(callback)
                self.directionRefine(callback)

    def directionRemove(self, callback):
        callback.remove()

    def directionShapes(self, callback):
        if self.indicatorShaped != None:
            if self.directionCollid(callback) == 1:
                self.directionShaped = 'red'
            if self.directionCollid(callback) == 0:
                self.directionShaped = 'green'
            if self.indicatorShaped == self.directionShaped:
                pass
            if self.indicatorShaped != self.directionShaped:
                self.indicatorShaped = self.directionShaped
                self.indicatorID.setShape(self.indicatorShaped)
        if self.indicatorShaped == None:
            if self.directionCollid(callback) == 1:
                self.indicatorShaped = self.directionShaped = 'red'
            if self.directionCollid(callback) == 0:
                self.indicatorShaped = self.directionShaped = 'green'
            if self.indicatorShaped:
                self.indicatorID.setShape(self.indicatorShaped)
        return

    def directionUpdate(self, callback):
        if self.vehicleDistance(callback) < self.directionRecord['directionSquare']:
            self.currentDistance = self.vehicleDistance(callback)
            self.distantPosition = self.directionEntity(callback).position
            self.directionShapes(callback)
            self.directionSearch(self.distantPosition)
            self.currentIndicate.setDistance(self.currentDistance)
        if self.vehicleDistance(callback) > self.directionRecord['directionSquare']:
            self.directionRemove(self.currentIndicate)
            self.directionDelete(callback)
            self.directionRefine(callback)

    def directionSearch(self, callback):
        if (self.currentPosition - callback).length > 10:
            self.currentPosition = callback
            self.currentIndicate.track(callback)

    def vehicleDecimate(self, callback):
        if self.directionEntity(callback).isAlive() == 1:
            return 1
        if self.directionEntity(callback).isAlive() == 0:
            return 0

    def vehicleResearch(self, callback):
        if self.directionEntity(callback).publicInfo.team == self.arenaPlayer.team:
            return 0
        if self.directionEntity(callback).publicInfo.team != self.arenaPlayer.team:
            return 1

    def directionDelete(self, callback):
        del self.vehicleIndicate[callback]

    def directionRefine(self, callback):
        self.currentCarriage = None
        self.currentDistance = None
        self.currentPosition = None
        self.currentIndicate = None
        self.indicatorShaped = None
        return

    def vehicleDistance(self, callback):
        return (self.arenaPlayer.position - self.directionEntity(callback).position).length

    def directionSystem(self, callback):
        if self.callbackProcess is None:
            self.directionRepeat(callback)
        return

    def directionVerife(self, callback):
        if len(self.vehicleBouncing) == 0:
            self.callbackProcess = None
        return

    def directionRepeat(self, callback):
        if not self.arenaArenas.vehicles[self.arenaPlayer.playerVehicleID]['isAlive']:
            if len(self.vehicleIndicate) == 0:
                self.directionParams(self.currentIndicate)
            if len(self.vehicleIndicate) == 1:
                self.directionRemove(self.currentIndicate)
                self.directionParams(self.currentIndicate)
            return
        for vehicleID in self.vehicleBouncing.keys():
            if vehicleID == self.currentCarriage:
                self.directionUpdate(vehicleID)
            if vehicleID != self.currentCarriage:
                if len(self.vehicleIndicate) == 0:
                    if self.vehicleDistance(vehicleID) < self.directionRecord['directionSquare']:
                        self.directionAppend(vehicleID)
                    if self.vehicleDistance(vehicleID) > self.directionRecord['directionSquare']:
                        pass
                if len(self.vehicleIndicate) == 1:
                    if self.vehicleDistance(vehicleID) < self.currentDistance:
                        self.directionRelock(vehicleID)
                    if self.vehicleDistance(vehicleID) > self.currentDistance:
                        pass

        if len(self.vehicleBouncing) > 0:
            self.callbackProcess = BigWorld.callback(0.2, lambda : self.directionRepeat(callback))
        if len(self.vehicleBouncing) < 1:
            self.callbackProcess = BigWorld.callback(0.2, lambda : self.directionVerife(callback))


DB = DirectionBox()

