import BigWorld
import Keys
import ResMgr
from gui.app_loader import g_appLoader
from AvatarInputHandler import AvatarInputHandler
from Avatar import PlayerAvatar
from debug_utils import *

g_tundra = True
g_fullTundra = False
g_key = Keys.KEY_NUMPAD2
g_xmlConfig = ResMgr.openSection('scripts/client/gui/mods/mod_tundra.xml')
if g_xmlConfig:
    g_key = getattr(Keys, g_xmlConfig.readString('key', 'KEY_NUMPAD2'))
    g_tundra = g_xmlConfig.readBool('active', True)
    LOG_NOTE('config is loaded')

def new_onControlModeChanged(self, eMode, **args):
    old_onControlModeChanged(self, eMode, **args)
    if eMode == 'sniper':
        if g_tundra:
            BigWorld.wg_setTreeHidingRadius(750, 0)
            BigWorld.wg_enableTreeTransparency(False)
        else:
            BigWorld.wg_setTreeHidingRadius(12, 15)
            BigWorld.wg_enableTreeTransparency(True)
    elif g_fullTundra:
        BigWorld.wg_enableTreeHiding(True)
        BigWorld.wg_setTreeHidingRadius(750, 0)
        BigWorld.wg_enableTreeTransparency(False)
    else:
        BigWorld.wg_enableTreeHiding(False)
        BigWorld.wg_enableTreeTransparency(True)

old_onControlModeChanged = AvatarInputHandler.onControlModeChanged
AvatarInputHandler.onControlModeChanged = new_onControlModeChanged

def new_handleKey(self, isDown, key, mods):
    global g_tundra
    global g_fullTundra
    if key == g_key and mods == 0 and isDown:
        if g_appLoader.getDefBattleApp() is not None:
            player = BigWorld.player()
            if player.inputHandler.ctrl == player.inputHandler.ctrls['sniper']:
                if g_tundra:
                    BigWorld.wg_setTreeHidingRadius(12, 15)
                    BigWorld.wg_enableTreeTransparency(True)
                    g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', 'Tundra OFF', 'red'])
                    g_tundra = False
                else:
                    BigWorld.wg_setTreeHidingRadius(750, 0)
                    BigWorld.wg_enableTreeTransparency(False)
                    g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', 'Tundra ON', 'gold'])
                    g_tundra = True
            elif g_fullTundra:
                BigWorld.wg_enableTreeHiding(False)
                BigWorld.wg_enableTreeTransparency(True)
                g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', 'TundraFull OFF', 'red'])
                g_fullTundra = False
            else:
                BigWorld.wg_enableTreeHiding(True)
                BigWorld.wg_setTreeHidingRadius(750, 0)
                BigWorld.wg_enableTreeTransparency(False)
                g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', 'TundraFull ON', 'gold'])
                g_fullTundra = True
            self.soundNotifications.play('chat_shortcut_common_fx')
            return True
    return old_handleKey(self, isDown, key, mods)

old_handleKey = PlayerAvatar.handleKey
PlayerAvatar.handleKey = new_handleKey

def new_onEnterWorld(self, prereqs):
    global g_fullTundra
    old_onEnterWorld(self, prereqs)
    g_fullTundra = False
    BigWorld.wg_enableTreeHiding(False)
    BigWorld.wg_enableTreeTransparency(True)

old_onEnterWorld = PlayerAvatar.onEnterWorld
PlayerAvatar.onEnterWorld = new_onEnterWorld

