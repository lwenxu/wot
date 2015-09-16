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


old_startVisual = Vehicle.startVisual;
def new_startVisual(current):
    old_startVisual(current)
    addEdge(current)


old_stopVisual = Vehicle.stopVisual
def new_stopVisual(current):
    old_stopVisual(current)
    BigWorld.wgDelEdgeDetectEntity(current)


old_targetBlur = PlayerAvatar.targetBlur
def new_targetBlur(current, prevEntity):
    old_targetBlur(current, prevEntity)
    addEdge(prevEntity)


old_targetFocus = PlayerAvatar.targetFocus
def new_targetFocus(current, entity):
    BigWorld.wgDelEdgeDetectEntity(entity)
    old_targetFocus(current, entity)


Vehicle.startVisual = new_startVisual
Vehicle.stopVisual = new_stopVisual
PlayerAvatar.targetBlur = new_targetBlur
PlayerAvatar.targetFocus = new_targetFocus


init = lambda : None
fini = lambda : None
onAccountBecomePlayer = lambda : None
onAccountBecomeNonPlayer = lambda : None
onAvatarBecomePlayer = lambda : None
onAccountShowGUI = lambda ctx : None

