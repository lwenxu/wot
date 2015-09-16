import BigWorld
import Keys
import ResMgr
from gui.app_loader import g_appLoader
from AvatarInputHandler import AvatarInputHandler
from Avatar import PlayerAvatar
import BattleReplay
from debug_utils import *


PlayerAvatar.enableTundra = True
PlayerAvatar.enableFullTundra = False
g_xml = ResMgr.openSection('scripts/client/gui/mods/tundra.xml')
if g_xml:
    if g_xml.has_key('key'):
        PlayerAvatar.Key_Tundra2 = getattr(Keys, g_xml.readString('key'))
else:
    PlayerAvatar.Key_Tundra2 = Keys.KEY_F2


old_onControlModeChanged = AvatarInputHandler.onControlModeChanged
def new_onControlModeChanged(self, eMode, **args):
    old_onControlModeChanged(self, eMode, **args)
    if eMode == 'sniper':
        if PlayerAvatar.enableTundra:
            BigWorld.wg_setTreeHidingRadius(750, 0)
            BigWorld.wg_enableTreeTransparency(False)
        else:
            BigWorld.wg_setTreeHidingRadius(12, 15)
            BigWorld.wg_enableTreeTransparency(True)
    elif PlayerAvatar.enableFullTundra:
        BigWorld.wg_enableTreeHiding(True)
        BigWorld.wg_setTreeHidingRadius(750, 0)
        BigWorld.wg_enableTreeTransparency(False)
    else:
        BigWorld.wg_enableTreeHiding(False)
        BigWorld.wg_enableTreeTransparency(True)
    return self.new_onControlModeChanged


old_handleKey = PlayerAvatar.handleKey
def new_handleKey(self, isDown, key, mods):
    if key == PlayerAvatar.Key_Tundra2 and mods == 0 and isDown:
        if g_appLoader.getDefBattleApp() is not None:
            player = BigWorld.player()
            if player.inputHandler.ctrl == player.inputHandler.ctrls['sniper']:
                if PlayerAvatar.enableTundra:
                    BigWorld.wg_setTreeHidingRadius(12, 15)
                    BigWorld.wg_enableTreeTransparency(True)
                    g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', 'Tundra OFF', 'red'])
                    PlayerAvatar.enableTundra = False
                else:
                    BigWorld.wg_setTreeHidingRadius(750, 0)
                    BigWorld.wg_enableTreeTransparency(False)
                    _appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', 'Tundra  ON', 'gold'])
                    PlayerAvatar.enableTundra = True
            elif PlayerAvatar.enableFullTundra:
                BigWorld.wg_enableTreeHiding(False)
                BigWorld.wg_enableTreeTransparency(True)
                g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', 'TundraFull OFF', 'red'])
                PlayerAvatar.enableFullTundra = False
            else:
                BigWorld.wg_enableTreeHiding(True)
                BigWorld.wg_setTreeHidingRadius(750, 0)
                BigWorld.wg_enableTreeTransparency(False)
                g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', 'TundraFull  ON', 'gold'])
                PlayerAvatar.enableFullTundra = True
            self.soundNotifications.play('chat_shortcut_common_fx')
            return True
    return old_handleKey(self, isDown, key, mods)


old_onEnterWorld = PlayerAvatar.onEnterWorld
def new_onEnterWorld(self, prereqs):
    old_onEnterWorld(self, prereqs)
    PlayerAvatar.enableTundra = True
    PlayerAvatar.enableFullTundra = False
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

