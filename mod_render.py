import BigWorld
from Vehicle import Vehicle
from Avatar import PlayerAvatar
from gui.Scaleform.Battle import Battle
from debug_utils import *

def addEdge(vehicle):
    if isinstance(vehicle, Vehicle):
        if vehicle.isStarted and not vehicle.isPlayer and vehicle.isAlive():
            if vehicle.publicInfo['team'] is not BigWorld.player().team:
                #LOG_DEBUG("add edge %d" % vehicle.id)
                BigWorld.wgAddEdgeDetectEntity(vehicle, 0, 0, False)

def new_startVisual(current):
    old_startVisual(current)
    addEdge(current)

old_startVisual = Vehicle.startVisual
Vehicle.startVisual = new_startVisual

def new_stopVisual(current):
    old_stopVisual(current)
    BigWorld.wgDelEdgeDetectEntity(current)

old_stopVisual = Vehicle.stopVisual
Vehicle.stopVisual = new_stopVisual

def new_targetBlur(current, prevEntity):
    old_targetBlur(current, prevEntity)
    addEdge(prevEntity)

old_targetBlur = PlayerAvatar.targetBlur
PlayerAvatar.targetBlur = new_targetBlur

def new_targetFocus(current, entity):
    BigWorld.wgDelEdgeDetectEntity(entity)
    old_targetFocus(current, entity)

old_targetFocus = PlayerAvatar.targetFocus
PlayerAvatar.targetFocus = new_targetFocus

def onVehicleKilled(targetID, atackerID, *args):
    vehicle = BigWorld.entity(targetID)
    if vehicle and vehicle.isStarted and not vehicle.isPlayer:
        if vehicle.publicInfo['team'] is not BigWorld.player().team:
            BigWorld.wgDelEdgeDetectEntity(vehicle)

def new_startBattle(current):
    BigWorld.player().arena.onVehicleKilled += onVehicleKilled
    old_startBattle(current)

old_startBattle = Battle.afterCreate
Battle.afterCreate = new_startBattle

def new_stopBattle(current):
    BigWorld.player().arena.onVehicleKilled -= onVehicleKilled
    old_stopBattle(current)

old_stopBattle = Battle.beforeDelete
Battle.beforeDelete = new_stopBattle
