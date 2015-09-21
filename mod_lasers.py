import BigWorld
import Keys
import ResMgr
from Avatar import PlayerAvatar
from PlayerEvents import g_playerEvents
from gui.app_loader import g_appLoader
LaserModActive = True
entries = {}

def new_handleKey(self, isDown, key, mods):
    global LaserModActive
    if key == Keys.KEY_F3 and mods == 0 and isDown:
        if g_appLoader.getDefBattleApp() is not None:
            if LaserModActive:
                g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', 'Lasers OFF', 'red'])
                LaserModActive = False
            else:
                g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', 'Lasers ON', 'gold'])
                LaserModActive = True
            self.soundNotifications.play('chat_shortcut_common_fx')
            return True
    return old_handleKey(self, isDown, key, mods)


def initLasers():
    global entries
    global LaserModActive
    import Account
    if hasattr(BigWorld.player(), 'isOnArena'):
        if BigWorld.player().isOnArena:
            import Vehicle
            if LaserModActive:
                playerHealth = BigWorld.player().vehicleTypeDescriptor.maxHealth
                for v in BigWorld.entities.values():
                    if type(v) is Vehicle.Vehicle:
                        if v.isAlive():
                            if v.publicInfo['team'] is not BigWorld.player().team:
                                if not entries.has_key(v.id):
                                    shotsToKill = playerHealth / v.typeDescriptor.gun['shots'][0]['shell']['damage'][0]
                                    if shotsToKill < 3.0:
                                        laserColor = 'red'
                                    elif shotsToKill > 8.0:
                                        laserColor = 'green'
                                    else:
                                        laserColor = 'yellow'
                                    listi = v.appearance
                                    newModel = BigWorld.Model('objects/lasers/laser_%s.model' % laserColor)
                                    servo = BigWorld.Servo(listi.modelsDesc['gun']['model'].node('Gun'))
                                    newModel.addMotor(servo)
                                    entries[v.id] = dict({'model': newModel, 'vehicle': v, 'lasttime': BigWorld.time()})
                                    v.addModel(newModel)
                                else:
                                    entries[v.id]['lasttime'] = BigWorld.time()

            currentTime = BigWorld.time()
            for k in entries.keys():
                if entries[k]['lasttime'] + 0.5 < currentTime or not LaserModActive:
                    ModelToDel = entries[k]
                    try:
                        ModelToDel['vehicle'].delModel(ModelToDel['model'])
                    except:
                        pass

                    del entries[k]

    if type(BigWorld.player()) is not Account.PlayerAccount:
        BigWorld.callback(0.2, lambda : initLasers())
    return


def reloadLasers():
    global entries
    aih = BigWorld.player().inputHandler
    if not hasattr(aih, 'ctrl'):
        BigWorld.callback(0.2, lambda : reloadLasers())
    else:
        entries = {}
        initLasers()


g_playerEvents.onAvatarReady += reloadLasers
old_handleKey = PlayerAvatar.handleKey
PlayerAvatar.handleKey = new_handleKey


init = lambda : None
fini = lambda : None
onAccountBecomePlayer = lambda : None
onAccountBecomeNonPlayer = lambda : None
onAvatarBecomePlayer = lambda : None
onAccountShowGUI = lambda ctx : None

