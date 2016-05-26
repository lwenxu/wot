import BigWorld
import GUI
import constants
from Vehicle import Vehicle
from VehicleAppearance import VehicleAppearance, StippleManager, _VEHICLE_DISAPPEAR_TIME
from functools import partial
from debug_utils import *

g_delay = 15
g_distance = 350
g_shadows_list = []

def new_addStippleModel(self, vehID):
    global g_shadows_list
    model = self._StippleManager__stippleToAddDescs[vehID][0]
    if False:
        callbackID = BigWorld.callback(0.0, partial(self._StippleManager__addStippleModel, vehID))
        self._StippleManager__stippleToAddDescs[vehID] = (model, callbackID)
        return
    del self._StippleManager__stippleToAddDescs[vehID]
    BigWorld.player().addModel(model)
    vehicle = BigWorld.player().arena.vehicles.get(vehID)
    if vehicle['isAlive'] and BigWorld.player().team != vehicle['team']:
        vehicleType = unicode(vehicle['vehicleType'].type.shortUserString, 'utf-8')
        TransBoundingBox = GUI.BoundingBox('objects/shadow/null.dds')
        TransBoundingBox.size = (0.05, 0.05)
        TransBoundingBox.source = model.bounds
        GUI.addRoot(TransBoundingBox)
        g_shadows_list.append({'time': BigWorld.time(), 'bb': TransBoundingBox})
        BigWorld.callback(g_delay, delBoundingBox)
        callbackID = BigWorld.callback(g_delay, partial(self._StippleManager__removeStippleModel, vehID))
    else:
        callbackID = BigWorld.callback(_VEHICLE_DISAPPEAR_TIME, partial(self._StippleManager__removeStippleModel, vehID))
    self._StippleManager__stippleDescs[vehID] = (model, callbackID)

VehicleAppearance = StippleManager._StippleManager__addStippleModel
StippleManager._StippleManager__addStippleModel = new_addStippleModel

def delBoundingBox():
    global g_shadows_list
    for value in g_shadows_list:
        if BigWorld.time() - value['time'] >= g_delay:
            GUI.delRoot(value['bb'])
            g_shadows_list.remove(value)

