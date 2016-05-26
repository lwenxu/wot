import BigWorld
import ResMgr
import Math
from Vehicle import Vehicle
from Avatar import PlayerAvatar
from AvatarInputHandler import AvatarInputHandler
from constants import ARENA_PERIOD
from gui.app_loader import g_appLoader
from tutorial.gui.Scaleform.battle.legacy import ScaleformLayout
from tutorial.gui.Scaleform.battle.layout import BattleLayout
from debug_utils import *

g_battle = False
g_vehicle_list = []
g_focused_id = -1

'''
def showBattleMsg(msg, color = 'green'):
    if g_appLoader.getDefBattleApp() is not None:
        g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', msg, color])

def addIndicator(id, color = 'red'):
    global g_indicator
    g_indicator = BattleLayout(ScaleformLayout)._getDirectionIndicator()
    g_indicator.setShape(color) #'red' or 'green'
    g_indicator.setDistance(vehicleDistance(id))
    g_indicator.track(BigWorld.entity(id).position)

def trackIndicator(id):
    g_indicator.setDistance(vehicleDistance(id))
    g_indicator.track(BigWorld.entity(id).position)

def delIndicator():
    g_indicator.remove()

def vehicleDistance(id):
    return (BigWorld.player().position - BigWorld.entity(id).position).length

def isCollide(id):
    target = BigWorld.entity(id)
    target_pos = target.appearance.modelsDesc['gun']['model'].position
    player = BigWorld.entity(BigWorld.player().playerVehicleID)
    player_pos = player.appearance.modelsDesc['gun']['model'].position
    if BigWorld.wg_collideSegment(BigWorld.player().spaceID, target_pos, player_pos, 128) == None:
        return True
    else:
        return False
'''

def addEdge(vehicle):
    if isinstance(vehicle, Vehicle):
        if vehicle.isStarted and not vehicle.isPlayer and vehicle.isAlive():
            if vehicle.publicInfo['team'] is not BigWorld.player().team:
                BigWorld.wgSetEdgeDetectColors((Math.Vector4(0.5, 0.5, 0.5, 1), Math.Vector4(1.0, 0.07, 0.027, 1), Math.Vector4(0.488, 0.839, 0.023, 1), Math.Vector4(0.9, 0.8, 0.1, 1)))
                BigWorld.wgAddEdgeDetectEntity(vehicle, 3, 2, False)

def delEdge(vehicle):
    BigWorld.wgDelEdgeDetectEntity(vehicle)

def isSniperMode():
    player = BigWorld.player()
    if player.inputHandler.ctrl == player.inputHandler.ctrls['sniper']:
        return True
    return False

def new_startVisual(current):
    old_startVisual(current)
    g_vehicle_list.append(current.id)
    if isSniperMode():
        addEdge(current)

old_startVisual = Vehicle.startVisual
Vehicle.startVisual = new_startVisual

def new_stopVisual(current):
    old_stopVisual(current)
    g_vehicle_list.remove(current.id)
    if isSniperMode():
        delEdge(current)

old_stopVisual = Vehicle.stopVisual
Vehicle.stopVisual = new_stopVisual

def new_targetBlur(current, prevEntity):
    global g_focused_id
    g_focused_id = -1
    old_targetBlur(current, prevEntity)
    if isSniperMode():
        addEdge(prevEntity)

old_targetBlur = PlayerAvatar.targetBlur
PlayerAvatar.targetBlur = new_targetBlur

def new_targetFocus(current, entity):
    global g_focused_id
    g_focused_id = current.id
    if isSniperMode():
        delEdge(entity)
    old_targetFocus(current, entity)

old_targetFocus = PlayerAvatar.targetFocus
PlayerAvatar.targetFocus = new_targetFocus

def onVehicleKilled(targetID, atackerID, *args):
    g_vehicle_list.remove(targetID)
    vehicle = BigWorld.entity(targetID)
    if vehicle and vehicle.isStarted and not vehicle.isPlayer:
        if vehicle.publicInfo['team'] is not BigWorld.player().team:
            if isSniperMode():
                delEdge(vehicle)

def new_onArenaPeriodChange(current, period, periodEndTime, periodLength, periodAdditionalInfo):
    old_onArenaPeriodChange(current, period, periodEndTime, periodLength, periodAdditionalInfo)
    global g_battle
    if period == ARENA_PERIOD.BATTLE:
        BigWorld.player().arena.onVehicleKilled += onVehicleKilled
        g_battle = True
    elif period == ARENA_PERIOD.AFTERBATTLE:
        BigWorld.player().arena.onVehicleKilled -= onVehicleKilled
        g_battle = False

old_onArenaPeriodChange = PlayerAvatar._PlayerAvatar__onArenaPeriodChange
PlayerAvatar._PlayerAvatar__onArenaPeriodChange = new_onArenaPeriodChange

def new_onControlModeChanged(current, eMode, **args):
    global g_tundra
    old_onControlModeChanged(current, eMode, **args)
    if eMode == 'sniper':
        for id in g_vehicle_list:
            if id != g_focused_id:
                addEdge(BigWorld.entity(id))
    else:
        for id in g_vehicle_list:
            if id != g_focused_id:
                delEdge(BigWorld.entity(id))

old_onControlModeChanged = AvatarInputHandler.onControlModeChanged
AvatarInputHandler.onControlModeChanged = new_onControlModeChanged

