import BigWorld
import Keys
import GUI
import constants
import ResMgr
from Avatar import PlayerAvatar
from Vehicle import Vehicle
from VehicleAppearance import VehicleAppearance, StippleManager, _VEHICLE_DISAPPEAR_TIME
from gui.app_loader import g_appLoader
from debug_utils import *
from functools import partial
g_key = Keys.KEY_NUMPAD5
g_disappearDelay = 20
g_disappearDelayEnabled = True
g_disappearCaption = True
g_times = []

g_xmlConfig = ResMgr.openSection('scripts/client/gui/mods/mod_shadow.xml')
if g_xmlConfig:
    g_disappearDelay = g_xmlConfig.readInt('delay', g_disappearDelay)
    if g_disappearDelay > 0:
        g_disappearDelayEnabled = g_xmlConfig.readBool('active', True)
    else:
        g_disappearDelayEnabled = False
    g_key = getattr(Keys, g_xmlConfig.readString('key', 'KEY_NUMPAD5'))
    g_disappearCaption = g_xmlConfig.readBool('caption', True)
    LOG_NOTE('config is loaded')


def new_handleKey(self, isDown, key, mods):
    global g_disappearDelayEnabled
    global g_key
    if key == g_key and mods == 0 and isDown:
        if g_appLoader.getDefBattleApp() is not None:
            if g_disappearDelayEnabled:
                g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', 'Shadow OFF', 'red'])
                g_disappearDelayEnabled = False
            else:
                g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', 'Shadow ON', 'gold'])
                g_disappearDelayEnabled = True
            self.soundNotifications.play('chat_shortcut_common_fx')
            return True
    return old_handleKey(self, isDown, key, mods)


old_handleKey = PlayerAvatar.handleKey
PlayerAvatar.handleKey = new_handleKey


def new_addStippleModel(self, vehID):
    global g_times
    global g_disappearDelay
    global g_disappearDelayEnabled
    global g_disappearCaption
    stippleModel = self._StippleManager__stippleToAddDescs[vehID][0]
    if stippleModel.attached:
        CallAddStippleMode = BigWorld.callback(0.0, partial(self._StippleManager__addStippleModel, vehID))
        self._StippleManager__stippleToAddDescs[vehID] = (stippleModel, CallAddStippleMode)
        return
    del self._StippleManager__stippleToAddDescs[vehID]
    BigWorld.player().addModel(stippleModel)
    vehicle = BigWorld.player().arena.vehicles.get(vehID)
    if g_disappearDelayEnabled and BigWorld.player().team != vehicle['team']:
        if g_disappearCaption:
            vehicleType = unicode(vehicle['vehicleType'].type.shortUserString, 'utf-8')
            TransBoundingBox = GUI.BoundingBox('objects/shadow/null.dds')
            TransBoundingBox.size = (0.05, 0.05)
            my_info = '\\cFF4949FF;' + vehicleType
            TransBoundingBox.my_string = GUI.Text(my_info)
            TransBoundingBox.my_string.colourFormatting = True
            TransBoundingBox.my_string.colour = (255, 0, 0, 255)
            TransBoundingBox.my_string.font = 'hpmp_panel.font'
            TransBoundingBox.my_string.horizontalPositionMode = TransBoundingBox.my_string.verticalPositionMode = 'CLIP'
            TransBoundingBox.my_string.widthMode = TransBoundingBox.my_string.heightMode = 'PIXEL'
            TransBoundingBox.my_string.verticalAnchor = 'CENTER'
            TransBoundingBox.my_string.horizontalAnchor = 'CENTER'
            TransBoundingBox.source = stippleModel.bounds
            TransBoundingBox.my_string.position = (0.5, 0.75, 0)
            GUI.addRoot(TransBoundingBox)
            g_times.append({'time': BigWorld.time(), 'bb': TransBoundingBox})
            BigWorld.callback(g_disappearDelay, delBoundingBox)
        CallAddStippleMode = BigWorld.callback(g_disappearDelay, partial(self._StippleManager__removeStippleModel, vehID))
    else:
        CallAddStippleMode = BigWorld.callback(_VEHICLE_DISAPPEAR_TIME, partial(self._StippleManager__removeStippleModel, vehID))
    self._StippleManager__stippleDescs[vehID] = (stippleModel, CallAddStippleMode)


def delBoundingBox():
    global g_times
    global g_disappearDelay
    for value in g_times:
        if BigWorld.time() - value['time'] >= g_disappearDelay:
            GUI.delRoot(value['bb'])
            g_times.remove(value)


VehicleAppearance = StippleManager._StippleManager__addStippleModel
if g_disappearDelayEnabled:
    StippleManager._StippleManager__addStippleModel = new_addStippleModel

