import BigWorld
import Keys
import ResMgr
from gui.app_loader import g_appLoader
from AvatarInputHandler import AvatarInputHandler
from Avatar import PlayerAvatar
import BattleReplay
from debug_utils import *


g_Tundra = True
g_FullTundra = False

old_onControlModeChanged = AvatarInputHandler.onControlModeChanged
def new_onControlModeChanged(self, eMode, **args):
    global g_Tundra
    global g_FullTundra
    old_onControlModeChanged(self, eMode, **args)
    if eMode == 'sniper':
        if g_Tundra:
            BigWorld.wg_setTreeHidingRadius(750, 0)
            BigWorld.wg_enableTreeTransparency(False)
        else:
            BigWorld.wg_setTreeHidingRadius(12, 15)
            BigWorld.wg_enableTreeTransparency(True)
    elif g_FullTundra:
        BigWorld.wg_enableTreeHiding(True)
        BigWorld.wg_setTreeHidingRadius(750, 0)
        BigWorld.wg_enableTreeTransparency(False)
    else:
        BigWorld.wg_enableTreeHiding(False)
        BigWorld.wg_enableTreeTransparency(True)


old_handleKey = PlayerAvatar.handleKey
def new_handleKey(self, isDown, key, mods):
    global g_Tundra
    global g_FullTundra
    if key == Keys.KEY_F2 and mods == 0 and isDown:
        if g_appLoader.getDefBattleApp() is not None:
            player = BigWorld.player()
            if player.inputHandler.ctrl == player.inputHandler.ctrls['sniper']:
                if g_Tundra:
                    BigWorld.wg_setTreeHidingRadius(12, 15)
                    BigWorld.wg_enableTreeTransparency(True)
                    g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', 'Tundra OFF', 'red'])
                    g_Tundra = False
                else:
                    BigWorld.wg_setTreeHidingRadius(750, 0)
                    BigWorld.wg_enableTreeTransparency(False)
                    _appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', 'Tundra ON', 'gold'])
                    g_Tundra = True
            elif g_FullTundra:
                BigWorld.wg_enableTreeHiding(False)
                BigWorld.wg_enableTreeTransparency(True)
                g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', 'TundraFull OFF', 'red'])
                g_FullTundra = False
            else:
                BigWorld.wg_enableTreeHiding(True)
                BigWorld.wg_setTreeHidingRadius(750, 0)
                BigWorld.wg_enableTreeTransparency(False)
                g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', 'TundraFull ON', 'gold'])
                g_FullTundra = True
            self.soundNotifications.play('chat_shortcut_common_fx')
            return True
    return old_handleKey(self, isDown, key, mods)


old_onEnterWorld = PlayerAvatar.onEnterWorld
def new_onEnterWorld(self, prereqs):
    global g_Tundra
    global g_FullTundra
    old_onEnterWorld(self, prereqs)
    g_Tundra = True
    g_FullTundra = False
    BigWorld.wg_enableTreeHiding(False)
    BigWorld.wg_enableTreeTransparency(True)


AvatarInputHandler.onControlModeChanged = new_onControlModeChanged
PlayerAvatar.handleKey = new_handleKey
PlayerAvatar.onEnterWorld = new_onEnterWorld


init = lambda : None
fini = lambda : None
onAccountBecomePlayer = lambda : None
onAccountBecomeNonPlayer = lambda : None
onAvatarBecomePlayer = lambda : None
onAccountShowGUI = lambda ctx : None

