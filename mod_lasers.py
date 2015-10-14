import BigWorld
import Keys
import ResMgr
import Account
import Vehicle
from Avatar import PlayerAvatar
from PlayerEvents import g_playerEvents
from gui.app_loader import g_appLoader
from debug_utils import *

g_active = True
g_key = Keys.KEY_NUMPAD3
g_color = True
g_xmlConfig = ResMgr.openSection('scripts/client/gui/mods/mod_lasers.xml')
if g_xmlConfig:
    g_key = getattr(Keys, g_xmlConfig.readString('key', 'KEY_NUMPAD3'))
    g_active = g_xmlConfig.readBool('active', True)
    g_color = g_xmlConfig.readBool('color', True)
    LOG_NOTE('config is loaded')

def new_handleKey(self, isDown, key, mods):
    global g_active
    if key == g_key and mods == 0 and isDown:
        if g_appLoader.getDefBattleApp() is not None:
            if g_active:
                g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', 'Lasers OFF', 'red'])
                g_active = False
            else:
                g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', 'Lasers ON', 'gold'])
                g_active = True
            self.soundNotifications.play('chat_shortcut_common_fx')
            return True
    return old_handleKey(self, isDown, key, mods)

old_handleKey = PlayerAvatar.handleKey
PlayerAvatar.handleKey = new_handleKey

g_entries = {}

def initLasers():
    global g_entries
    if hasattr(BigWorld.player(), 'isOnArena'):
        if BigWorld.player().isOnArena:
            if g_active:
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
                                    listi = vehicle.appearance
                                    newModel = BigWorld.Model('objects/lasers/laser_%s.model' % laserColor)
                                    servo = BigWorld.Servo(listi.modelsDesc['gun']['model'].node('Gun'))
                                    newModel.addMotor(servo)
                                    g_entries[vehicle.id] = dict({'model': newModel, 'vehicle': vehicle, 'lasttime': BigWorld.time()})
                                    vehicle.addModel(newModel)
                                else:
                                    g_entries[vehicle.id]['lasttime'] = BigWorld.time()
            currentTime = BigWorld.time()
            for k in g_entries.keys():
                if g_entries[k]['lasttime'] + 0.5 < currentTime or not g_active:
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

