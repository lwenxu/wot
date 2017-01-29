import BigWorld, ResMgr, Math
from Avatar import PlayerAvatar
from constants import ARENA_PERIOD
from gui.app_loader import g_appLoader
from gui.Scaleform.daapi.view.battle.shared import indicators
from debug_utils import *
#LOG_DEBUG = LOG_NOTE

g_max_distance = 300
g_battle = False
g_target_list = []
g_indicator = None
g_indicator_color = ''
g_indicator_id = 0

def showBattleMsg(msg, color = 'green'):
    if g_appLoader.getDefBattleApp() is not None:
        g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', msg, color])

def addIndicator(id, color = 'green'):
    global g_indicator
    global g_indicator_id
    global g_indicator_color
    g_indicator = indicators.createDirectIndicator()
    g_indicator.setShape(color) #'red' or 'green'
    g_indicator.setDistance(vehicleDistance(id))
    g_indicator.track(BigWorld.entity(id).position)
    g_indicator_id = id
    g_indicator_color = color

def trackIndicator():
    g_indicator.setDistance(vehicleDistance(g_indicator_id))
    g_indicator.track(BigWorld.entity(g_indicator_id).position)

def delIndicator():
    global g_indicator_id
    global g_indicator_color
    if g_indicator_id:
        g_indicator.remove()
        g_indicator_id = 0
        g_indicator_color = ''

def vehicleDistance(id):
    return (BigWorld.player().position - BigWorld.entity(id).position).length

def vehicleGunPosition(id):
    vehicle = BigWorld.entity(id)
    model = vehicle.appearance.compoundModel
    node = model.node('HP_gunFire')
    if node:
        gun_matr = Math.Matrix(node)
        gun_pos = gun_matr.translation
        return gun_pos
    return None

def isCollide(id):
    target_pos = vehicleGunPosition(id)
    player_pos = vehicleGunPosition(BigWorld.player().playerVehicleID)
    if target_pos and player_pos:
        if BigWorld.wg_collideSegment(BigWorld.player().spaceID, target_pos, player_pos, 128) == None:
            return True
        else:
            return False
    else:
        return False

def checkTargets():
    if not g_battle: return
    red_id = 0
    red_dist = 600
    green_id = 0
    green_dist = g_max_distance

    #find nearest target
    for id in g_target_list:
        distance = vehicleDistance(id)
        if distance < green_dist:
            green_id = id
            green_dist = distance
        if isCollide(id):
            LOG_DEBUG('collide: id=%s, distance=%s' % (id, int(distance)))
            if distance < red_dist:
                red_id = id
                red_dist = distance

    #found new red indicator
    if red_id != 0:
        if red_id != g_indicator_id or g_indicator_color != 'red':
            LOG_DEBUG('found red: id=%s, distance=%s' % (red_id, int(red_dist)))
            delIndicator()
            addIndicator(red_id, 'red')
        else:
            trackIndicator()

    #found new green indicator
    elif green_id != 0: 
        if green_id != g_indicator_id or g_indicator_color != 'green':
            LOG_DEBUG('found green: id=%s, distance=%s' % (green_id, int(green_dist)))
            delIndicator()
            addIndicator(green_id, 'green')
        else:
            trackIndicator()
    else:
        delIndicator()

    BigWorld.callback(0.2, checkTargets)

def isFriend(id):
    return BigWorld.player().arena.vehicles[BigWorld.player().playerVehicleID]['team'] == BigWorld.player().arena.vehicles[id]['team']

def new_vehicle_onEnterWorld(current, vehicle):
    old_vehicle_onEnterWorld(current, vehicle)
    if not g_battle: return
    id = vehicle.id
    if not isFriend(id):
        if id not in g_target_list:
            LOG_DEBUG('added: %s' % id)
            g_target_list.append(id)

old_vehicle_onEnterWorld = PlayerAvatar.vehicle_onEnterWorld
PlayerAvatar.vehicle_onEnterWorld = new_vehicle_onEnterWorld

def new_vehicle_onLeaveWorld(current, vehicle):
    old_vehicle_onLeaveWorld(current, vehicle)
    id = vehicle.id
    if id in g_target_list:
        LOG_DEBUG('removed: %s' % id)
        g_target_list.remove(id)

old_vehicle_onLeaveWorld = PlayerAvatar.vehicle_onLeaveWorld
PlayerAvatar.vehicle_onLeaveWorld = new_vehicle_onLeaveWorld

def onVehicleKilled(targetID, atackerID, *args):
    id = targetID
    if id in g_target_list:
        LOG_DEBUG('removed: %s' % id)
        g_target_list.remove(id)
        if id == g_indicator_id:
            delIndicator()

def new_onArenaPeriodChange(current, period, periodEndTime, periodLength, periodAdditionalInfo):
    old_onArenaPeriodChange(current, period, periodEndTime, periodLength, periodAdditionalInfo)
    global g_battle
    global g_target_list
    if period == ARENA_PERIOD.BATTLE:
        BigWorld.player().arena.onVehicleKilled += onVehicleKilled
        g_battle = True
        g_target_list = []
        checkTargets()
    elif period == ARENA_PERIOD.AFTERBATTLE:
        BigWorld.player().arena.onVehicleKilled -= onVehicleKilled
        g_battle = False
        g_target_list = []
        delIndicator()

old_onArenaPeriodChange = PlayerAvatar._PlayerAvatar__onArenaPeriodChange
PlayerAvatar._PlayerAvatar__onArenaPeriodChange = new_onArenaPeriodChange

