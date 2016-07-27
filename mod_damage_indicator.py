from gui.Scaleform.daapi.view.battle.shared.indicators import _DamageIndicator

def new_getDuration(self):
    return 10.0 

old_getDuration = _DamageIndicator.getDuration
_DamageIndicator.getDuration = new_getDuration
