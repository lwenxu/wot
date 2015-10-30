import BigWorld
import ResMgr
import Math
import Vehicle
from Avatar import PlayerAvatar
from Account import PlayerAccount
from gui.Scaleform.Battle import Battle
from constants import ARENA_PERIOD
from gui.app_loader import g_appLoader
from debug_utils import *

g_visible_list = []
g_edged_list = []

def showBattleMsg(msg, color = 'red'):
    if g_appLoader.getDefBattleApp() is not None:
        g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', msg, color])

def addEdge(id):
    target = BigWorld.entity(id)
    #FIXME read cfg and ...
    BigWorld.wgSetEdgeDetectColors((Math.Vector4(0.5, 0.5, 0.5, 1), Math.Vector4(1.0, 0.07, 0.027, 1), Math.Vector4(0.488, 0.839, 0.023, 1), Math.Vector4(0.9, 0.8, 0.1, 1)))
    BigWorld.wgAddEdgeDetectEntity(target, 3, 2, False)

def delEdge(id):
    target = BigWorld.entity(id)
    BigWorld.wgDelEdgeDetectEntity(target)

def new_targetBlur(current, prevEntity):
    old_targetBlur(current, prevEntity)
    if prevEntity.id in g_edged_list:
        BigWorld.wgAddEdgeDetectEntity(prevEntity, 3, 2, False)

old_targetBlur = PlayerAvatar.targetBlur
PlayerAvatar.targetBlur = new_targetBlur

def new_targetFocus(current, entity):
    if entity.id in g_edged_list:
        BigWorld.wgDelEdgeDetectEntity(entity)
    old_targetFocus(current, entity)

old_targetFocus = PlayerAvatar.targetFocus
PlayerAvatar.targetFocus = new_targetFocus

def vehicleDistance(id):
    return (BigWorld.player().position - BigWorld.entity(id).position).length

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
            if id not in g_edged_list:
                addEdge(id)
                g_edged_list.append(id)
                #veh = BigWorld.player().arena.vehicles.get(id)
                #showBattleMsg('addEdge: %s (%s): %sm' % (veh['name'], veh['vehicleType'].type.shortUserString, int(vehicleDistance(id))))
        else:
            if id in g_edged_list:
                delEdge(id)
                g_edged_list.remove(id)
                #veh = BigWorld.player().arena.vehicles.get(id)
                #showBattleMsg('delEdge: %s (%s): %sm' % (veh['name'], veh['vehicleType'].type.shortUserString, int(vehicleDistance(id))))
    if hasattr(BigWorld.player(), 'arena'):
        BigWorld.callback(0.2, lambda : checkCollides())

def new_onArenaPeriodChange(current, period, periodEndTime, periodLength, periodAdditionalInfo):
    old_onArenaPeriodChange(current, period, periodEndTime, periodLength, periodAdditionalInfo)
    #if period == ARENA_PERIOD.PREBATTLE:
    if period == ARENA_PERIOD.BATTLE:
        BigWorld.callback(0.2, lambda : checkCollides())

old_onArenaPeriodChange = PlayerAvatar._PlayerAvatar__onArenaPeriodChange
PlayerAvatar._PlayerAvatar__onArenaPeriodChange = new_onArenaPeriodChange

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
    old_vehicle_onLeaveWorld(current, vehicle)
    id = vehicle.id
    if id in g_visible_list:
        g_visible_list.remove(id)
    if id in g_edged_list:
        delEdge(id)
        g_edged_list.remove(id)

old_vehicle_onLeaveWorld = PlayerAvatar.vehicle_onLeaveWorld
PlayerAvatar.vehicle_onLeaveWorld = new_vehicle_onLeaveWorld

def onVehicleKilled(targetID, atackerID, *args):
    id = targetID
    if id in g_visible_list:
        g_visible_list.remove(id)
    if id in g_edged_list:
        delEdge(id)
        g_edged_list.remove(id)

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

