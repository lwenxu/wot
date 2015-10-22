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

g_active = True
g_key = Keys.KEY_NUMPAD5
g_delay = 20
g_xmlConfig = ResMgr.openSection('scripts/client/gui/mods/mod_shadow.xml')
if g_xmlConfig:
    g_delay = g_xmlConfig.readInt('delay', g_delay)
    if g_delay > 0:
        g_active = g_xmlConfig.readBool('active', True)
    else:
        g_active = False
    g_key = getattr(Keys, g_xmlConfig.readString('key', 'KEY_NUMPAD5'))
    LOG_NOTE('config is loaded')

def new_handleKey(self, isDown, key, mods):
    global g_active
    if key == g_key and mods == 0 and isDown:
        if g_appLoader.getDefBattleApp() is not None:
            if g_active:
                g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', 'Shadow OFF', 'red'])
                g_active = False
            else:
                g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', 'Shadow ON', 'gold'])
                g_active = True
            self.soundNotifications.play('chat_shortcut_common_fx')
            return True
    return old_handleKey(self, isDown, key, mods)

old_handleKey = PlayerAvatar.handleKey
PlayerAvatar.handleKey = new_handleKey

g_shadows_list = []

def new_addStippleModel(self, vehID):
    global g_shadows_list
    model = self._StippleManager__stippleToAddDescs[vehID][0]
    if model.attached:
        callbackID = BigWorld.callback(0.0, partial(self._StippleManager__addStippleModel, vehID))
        self._StippleManager__stippleToAddDescs[vehID] = (model, callbackID)
        return
    del self._StippleManager__stippleToAddDescs[vehID]
    BigWorld.player().addModel(model)
    vehicle = BigWorld.player().arena.vehicles.get(vehID)
    if g_active and vehicle['isAlive'] and BigWorld.player().team != vehicle['team']:
        vehicleType = unicode(vehicle['vehicleType'].type.shortUserString, 'utf-8')
        TransBoundingBox = GUI.BoundingBox('objects/shadow/null.dds')
        TransBoundingBox.size = (0.05, 0.05)
        '''
        #ERROR: AttributeError: GUI.Text: The requested font does not exist.
        TransBoundingBox.shadowText = GUI.Text('\\cFF4949FF;' + vehicleType)
        TransBoundingBox.shadowText.colourFormatting = True
        TransBoundingBox.shadowText.colour = (255, 0, 0, 255)
        TransBoundingBox.shadowText.font = 'hpmp_panel.font'
        TransBoundingBox.shadowText.horizontalPositionMode = 'CLIP'
        TransBoundingBox.shadowText.verticalPositionMode = 'CLIP'
        TransBoundingBox.shadowText.widthMode = 'PIXEL'
        TransBoundingBox.shadowText.heightMode = 'PIXEL'
        TransBoundingBox.shadowText.verticalAnchor = 'CENTER'
        TransBoundingBox.shadowText.horizontalAnchor = 'CENTER'
        TransBoundingBox.shadowText.position = (0.5, 0.75, 0)
        '''
        TransBoundingBox.source = model.bounds
        GUI.addRoot(TransBoundingBox)
        g_shadows_list.append({'time': BigWorld.time(), 'bb': TransBoundingBox, 'id': vehID})
        #LOG_DEBUG('add %d' % vehID)
        BigWorld.callback(g_delay, delBoundingBox)
        callbackID = BigWorld.callback(g_delay, partial(self._StippleManager__removeStippleModel, vehID))
    else:
        callbackID = BigWorld.callback(_VEHICLE_DISAPPEAR_TIME, partial(self._StippleManager__removeStippleModel, vehID))
    self._StippleManager__stippleDescs[vehID] = (model, callbackID)

def delBoundingBox():
    global g_shadows_list
    for value in g_shadows_list:
        if BigWorld.time() - value['time'] >= g_delay:
            #LOG_DEBUG('del %d' % value['id'])
            GUI.delRoot(value['bb'])
            g_shadows_list.remove(value)

VehicleAppearance = StippleManager._StippleManager__addStippleModel
StippleManager._StippleManager__addStippleModel = new_addStippleModel


