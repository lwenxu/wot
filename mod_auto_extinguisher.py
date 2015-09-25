import BigWorld
from functools import partial
from gui.Scaleform.daapi.view.battle.damage_panel import DamagePanel
from gui.battle_control import g_sessionProvider
from debug_utils import *


def new_as_setFireInVehicleS(self, bool):
    old_as_setFireInVehicleS(self, bool)
    BigWorld.callback(0.01, partial(g_sessionProvider.getEquipmentsCtrl().changeSettingByTag, 'extinguisher', None, BigWorld.player()))
    LOG_NOTE('fire extinguished')
    return


old_as_setFireInVehicleS = DamagePanel.as_setFireInVehicleS
DamagePanel.as_setFireInVehicleS = new_as_setFireInVehicleS

