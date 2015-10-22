import BigWorld
from Vehicle import Vehicle
from Avatar import PlayerAvatar
from debug_utils import *

def addEdge(vehicle):
    if isinstance(vehicle, Vehicle):
        if vehicle.isStarted and not vehicle.isPlayer and vehicle.isAlive():
            if vehicle.publicInfo['team'] is not BigWorld.player().team:
                vehicle.drawEdge(0, 0, False)
                #LOG_DEBUG("add edge %d" % vehicle.id)

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

