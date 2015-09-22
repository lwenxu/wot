import BigWorld
import Math
import GUI
import ChatManager
import constants
import ResMgr
from Avatar import PlayerAvatar
from vehicle import Vehicle
from debug_utils import *
import math
from VehicleAppearance import VehicleAppearance, StippleManager, _VEHICLE_DISAPPEAR_TIME

myConf = {}
myConf['Delay'] = 20
cfg = ResMgr.openSection('scripts/client/gui/mods/mod_shadow.xml')
if cfg is None:
    LOG_ERROR('CONFIG NOT FOUND')
else:
    sec = cfg['Delay']
    if sec is not None:
        myConf['Delay'] = sec.asInt
PlayerAvatar.disappearDelayEnabled = True
PlayerAvatar.disappearCaption = True
PlayerAvatar.disappearDelay = myConf['Delay']
times = []


def new_addStippleModel(self, vehID):
    from functools import partial
    stippleModel = self._StippleManager__stippleToAddDescs[vehID][0]
    if stippleModel.attached:
        CallAddStippleMode = BigWorld.callback(0.0, partial(self._StippleManager__addStippleModel, vehID))
        self._StippleManager__stippleToAddDescs[vehID] = (stippleModel, CallAddStippleMode)
        return
    del self._StippleManager__stippleToAddDescs[vehID]
    BigWorld.player().addModel(stippleModel)
    vehicle = BigWorld.player().arena.vehicles.get(vehID)
    if PlayerAvatar.disappearDelayEnabled and BigWorld.player().team != vehicle['team']:
        if PlayerAvatar.disappearCaption:
            vehicleType = unicode(vehicle['vehicleType'].type.shortUserString, 'utf-8')
            TransBoundingBox = GUI.BoundingBox('objects/shadow/null.dds')
            TransBoundingBox.size = (0.05, 0.05)
            _info = '\\cFF4949FF;' + vehicleType
            TransBoundingBox.my_string = GUI.Text(_info)
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
            times.append({'time': BigWorld.time(), 'bb': TransBoundingBox})
            BigWorld.callback(myConf['Delay'], delBoundingBox)
        CallAddStippleMode = BigWorld.callback(myConf['Delay'], partial(self._StippleManager__removeStippleModel, vehID))
    else:
        CallAddStippleMode = BigWorld.callback(_VEHICLE_DISAPPEAR_TIME, partial(self._StippleManager__removeStippleModel, vehID))
    self._StippleManager__stippleDescs[vehID] = (stippleModel, CallAddStippleMode)


def delBoundingBox():
    for value in times:
        if BigWorld.time() - value['time'] >= myConf['Delay']:
            GUI.delRoot(value['bb'])
            times.remove(value)


VehicleAppearance = StippleManager._StippleManager__addStippleModel
if PlayerAvatar.disappearDelayEnabled:
    StippleManager._StippleManager__addStippleModel = new_addStippleModel

