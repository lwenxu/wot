import BigWorld, SoundGroups, Math
from Avatar import PlayerAvatar
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.battle.shared import indicators
from debug_utils import *
#LOG_DEBUG = LOG_NOTE

g_battle = False
g_target_list = []
g_indicator = None
g_indicator_color = ''
g_indicator_id = 0

def addIndicator(id, distance, color = 'green'):
    global g_indicator
    global g_indicator_id
    global g_indicator_color
    g_indicator = indicators.createDirectIndicator()
    g_indicator.setShape(color) #'red' or 'green'
    g_indicator.setDistance(distance)
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

def vehicleVisible(id):
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
    nearest_id = 0
    nearest_dist = 150
    visible_id = 0
    visible_dist = 565
    #find target
    for id in g_target_list:
        distance = vehicleDistance(id)
        if distance < nearest_dist:
            nearest_id = id
            nearest_dist = distance
        if vehicleVisible(id):
            if distance < visible_dist:
                visible_id = id
                visible_dist = distance
    #found visible target
    if visible_id != 0:
        if visible_id != g_indicator_id or g_indicator_color != 'red':
            LOG_DEBUG('found visible: id=%s, distance=%s' % (visible_id, int(visible_dist)))
            delIndicator()
            addIndicator(visible_id, visible_dist, 'red')
        else:
            trackIndicator()
    #found nearest target
    elif nearest_id != 0: 
        if nearest_id != g_indicator_id or g_indicator_color != 'green':
            LOG_DEBUG('found nearest: id=%s, distance=%s' % (nearest_id, int(nearest_dist)))
            delIndicator()
            addIndicator(nearest_id, nearest_dist, 'green')
        else:
            trackIndicator()
    else:
        delIndicator()
    BigWorld.callback(0.5, checkTargets)

def isFriend(id):
    return BigWorld.player().arena.vehicles[BigWorld.player().playerVehicleID]['team'] == BigWorld.player().arena.vehicles[id]['team']

def new_vehicle_onEnterWorld(current, vehicle):
    old_vehicle_onEnterWorld(current, vehicle)
    if not g_battle: return
    id = vehicle.id
    if not isFriend(id):
        if vehicleDistance(id) < 150:
            sound = SoundGroups.g_instance.getSound2D('lightbulb_02')
            BigWorld.callback(0.0, sound.play)
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
    if id == BigWorld.player().playerVehicleID:
        stopBattle()
    if id in g_target_list:
        LOG_DEBUG('removed: %s' % id)
        g_target_list.remove(id)
        if id == g_indicator_id:
            delIndicator()

def startBattle():
    global g_battle
    global g_target_list
    g_battle = True
    g_target_list = []
    checkTargets()

def stopBattle():
    global g_battle
    global g_target_list
    g_battle = False
    g_target_list = []
    delIndicator()

def new_onArenaPeriodChange(current, period, periodEndTime, periodLength, periodAdditionalInfo):
    old_onArenaPeriodChange(current, period, periodEndTime, periodLength, periodAdditionalInfo)
    if period == ARENA_PERIOD.BATTLE:
        BigWorld.player().arena.onVehicleKilled += onVehicleKilled
        startBattle()
    elif period == ARENA_PERIOD.AFTERBATTLE:
        BigWorld.player().arena.onVehicleKilled -= onVehicleKilled
        stopBattle()

old_onArenaPeriodChange = PlayerAvatar._PlayerAvatar__onArenaPeriodChange
PlayerAvatar._PlayerAvatar__onArenaPeriodChange = new_onArenaPeriodChange

BigWorld.logInfo('NOTE', 'package loaded: mod_target', None)
