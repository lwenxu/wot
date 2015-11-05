import BigWorld
import ResMgr
import Math
import Vehicle
from Avatar import PlayerAvatar
from constants import ARENA_PERIOD
from gui.app_loader import g_appLoader
from tutorial.gui.Scaleform.battle.legacy import ScaleformLayout
from tutorial.gui.Scaleform.battle.layout import BattleLayout
from debug_utils import *

g_visible_list = []
g_target_list = []
g_battle = False
g_indicator = None

def showBattleMsg(msg, color = 'red'):
    if g_appLoader.getDefBattleApp() is not None:
        g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', msg, color])

def vehicleDistance(id):
    return (BigWorld.player().position - BigWorld.entity(id).position).length

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

def addEdge(id):
    target = BigWorld.entity(id)
    if target:
        BigWorld.wgSetEdgeDetectColors((Math.Vector4(0.5, 0.5, 0.5, 1), Math.Vector4(1.0, 0.07, 0.027, 1), Math.Vector4(0.488, 0.839, 0.023, 1), Math.Vector4(0.9, 0.8, 0.1, 1)))
        BigWorld.wgAddEdgeDetectEntity(target, 3, 2, False)

def delEdge(id):
    target = BigWorld.entity(id)
    if target:
        BigWorld.wgDelEdgeDetectEntity(target)

def new_targetBlur(current, prevEntity):
    old_targetBlur(current, prevEntity)
    if prevEntity.id in g_target_list:
        BigWorld.wgAddEdgeDetectEntity(prevEntity, 3, 2, False)

old_targetBlur = PlayerAvatar.targetBlur
PlayerAvatar.targetBlur = new_targetBlur

def new_targetFocus(current, entity):
    #if entity.id in g_target_list:
    BigWorld.wgDelEdgeDetectEntity(entity)
    old_targetFocus(current, entity)

old_targetFocus = PlayerAvatar.targetFocus
PlayerAvatar.targetFocus = new_targetFocus

def isCollide(id):
    target = BigWorld.entity(id)
    target_pos = target.appearance.modelsDesc['gun']['model'].position
    player = BigWorld.entity(BigWorld.player().playerVehicleID)
    player_pos = player.appearance.modelsDesc['gun']['model'].position
    if BigWorld.wg_collideSegment(BigWorld.player().spaceID, target_pos, player_pos, False) == None:
        return True
    else:
        return False

def checkCollides():
    for id in g_visible_list:
        if isCollide(id):
            if id not in g_target_list:
                addEdge(id)
                g_target_list.append(id)
        else:
            if id in g_target_list:
                delEdge(id)
                g_target_list.remove(id)
    if g_battle:
        BigWorld.callback(0.2, checkCollides)

def new_vehicle_onEnterWorld(current, vehicle):
    old_vehicle_onEnterWorld(current, vehicle)
    if vehicle.isStarted and not vehicle.isPlayer and vehicle.isAlive():
        if vehicle.publicInfo['team'] is not BigWorld.player().team:
            id = vehicle.id
            if id not in g_visible_list:
                g_visible_list.append(id)
 
old_vehicle_onEnterWorld = PlayerAvatar.vehicle_onEnterWorld
PlayerAvatar.vehicle_onEnterWorld = new_vehicle_onEnterWorld

def new_vehicle_onLeaveWorld(current, vehicle):
    id = vehicle.id
    if id in g_visible_list:
        g_visible_list.remove(id)
    if id in g_target_list:
        g_target_list.remove(id)
        #delEdge(id)
    old_vehicle_onLeaveWorld(current, vehicle)

old_vehicle_onLeaveWorld = PlayerAvatar.vehicle_onLeaveWorld
PlayerAvatar.vehicle_onLeaveWorld = new_vehicle_onLeaveWorld

#PlayerAvatar.onVehicleEnterWorld += onVehicleEnterWorld
#PlayerAvatar.onVehicleLeaveWorld += onVehicleLeaveWorld

def onVehicleKilled(targetID, atackerID, *args):
    id = targetID
    if id in g_visible_list:
        g_visible_list.remove(id)
    if id in g_target_list:
        g_target_list.remove(id)
        delEdge(id)

def new_onArenaPeriodChange(current, period, periodEndTime, periodLength, periodAdditionalInfo):
    old_onArenaPeriodChange(current, period, periodEndTime, periodLength, periodAdditionalInfo)
    global g_visible_list, g_target_list, g_battle
    if period == ARENA_PERIOD.BATTLE:
        BigWorld.player().arena.onVehicleKilled += onVehicleKilled
        g_visible_list[:] = []
        g_target_list[:] = []
        g_battle = True
        checkCollides()
    elif period == ARENA_PERIOD.AFTERBATTLE:
        BigWorld.player().arena.onVehicleKilled -= onVehicleKilled
        g_battle = False
        g_visible_list[:] = []
        g_target_list[:] = []

old_onArenaPeriodChange = PlayerAvatar._PlayerAvatar__onArenaPeriodChange
PlayerAvatar._PlayerAvatar__onArenaPeriodChange = new_onArenaPeriodChange

