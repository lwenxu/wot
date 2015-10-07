import BigWorld
from Vehicle import Vehicle
from Avatar import PlayerAvatar
from debug_utils import *


def addEdge(vehicle):
    if isinstance(vehicle, Vehicle):
        if vehicle.isStarted:
            if not vehicle.isPlayer:
                if vehicle.isAlive():
                    if vehicle.publicInfo['team'] is not BigWorld.player().team:
                        BigWorld.wgAddEdgeDetectEntity(vehicle, 0, False)


def new_startVisual(current):
    old_startVisual(current)
    addEdge(current)


def new_stopVisual(current):
    old_stopVisual(current)
    BigWorld.wgDelEdgeDetectEntity(current)


def new_targetBlur(current, prevEntity):
    old_targetBlur(current, prevEntity)
    addEdge(prevEntity)


def new_targetFocus(current, entity):
    BigWorld.wgDelEdgeDetectEntity(entity)
    old_targetFocus(current, entity)


old_startVisual = Vehicle.startVisual
Vehicle.startVisual = new_startVisual
old_stopVisual = Vehicle.stopVisual
Vehicle.stopVisual = new_stopVisual
old_targetBlur = PlayerAvatar.targetBlur
PlayerAvatar.targetBlur = new_targetBlur
old_targetFocus = PlayerAvatar.targetFocus
PlayerAvatar.targetFocus = new_targetFocus

