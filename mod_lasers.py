import BigWorld
import Account
import Vehicle
from PlayerEvents import g_playerEvents
from debug_utils import *

g_color = True
g_entries = {}

def initLasers():
    global g_entries
    if hasattr(BigWorld.player(), 'isOnArena'):
        if BigWorld.player().isOnArena:
            playerHealth = BigWorld.player().vehicleTypeDescriptor.maxHealth
            for vehicle in BigWorld.entities.values():
                if type(vehicle) is Vehicle.Vehicle:
                    if vehicle.isAlive():
                        if vehicle.publicInfo['team'] is not BigWorld.player().team:
                            if not g_entries.has_key(vehicle.id):
                                if g_color:
                                    shotsToKill = playerHealth / vehicle.typeDescriptor.gun['shots'][0]['shell']['damage'][0]
                                    if shotsToKill < 3.0:
                                        laserColor = 'red'
                                    elif shotsToKill > 8.0:
                                        laserColor = 'green'
                                    else:
                                        laserColor = 'yellow'
                                else:
                                    laserColor = 'red'
                                va = vehicle.appearance
                                newModel = BigWorld.Model('objects/lasers/laser_%s.model' % laserColor)
                                servo = BigWorld.Servo(va.modelsDesc['gun']['model'].node('Gun'))
                                newModel.addMotor(servo)
                                g_entries[vehicle.id] = dict({'model': newModel, 'vehicle': vehicle, 'lasttime': BigWorld.time()})
                                vehicle.addModel(newModel)
                            else:
                                g_entries[vehicle.id]['lasttime'] = BigWorld.time()
            currentTime = BigWorld.time()
            for k in g_entries.keys():
                if g_entries[k]['lasttime'] + 0.5 < currentTime:
                    ModelToDel = g_entries[k]
                    try:
                        ModelToDel['vehicle'].delModel(ModelToDel['model'])
                    except:
                        pass
                    del g_entries[k]
    if type(BigWorld.player()) is not Account.PlayerAccount:
        BigWorld.callback(0.2, lambda : initLasers())

def reloadLasers():
    global g_entries
    aih = BigWorld.player().inputHandler
    if not hasattr(aih, 'ctrl'):
        BigWorld.callback(0.2, lambda : reloadLasers())
    else:
        g_entries = {}
        initLasers()

g_playerEvents.onAvatarReady += reloadLasers

