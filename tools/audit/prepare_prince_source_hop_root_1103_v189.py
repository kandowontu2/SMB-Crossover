"""Require the measured original6px source/2px native standing hop."""
from pathlib import Path
import prepare_prince_idle_jump_root_1103_v188 as J

original=J.original
def finalize(output,rom,controller,refs,**kwargs):
    old='local jumpStarted=false'
    assert controller.count(old)==1
    controller=controller.replace(old,old+'\nlocal jumpSourceStart,jumpSourceMin=nil,nil')
    old="completePart();beginPart('source-jump');initialY=r('Player_Y_Position')"
    assert controller.count(old)==1
    controller=controller.replace(old,old+';jumpSourceStart=ps(0x611);jumpSourceMin=jumpSourceStart')
    old="elseif part=='source-jump'then\n"
    assert controller.count(old)==1
    controller=controller.replace(old,old+'  jumpSourceMin=math.min(jumpSourceMin,ps(0x611))\n')
    assert controller.count('jumpMinY<initialY-8')==2
    controller=controller.replace('jumpMinY<initialY-8','jumpMinY<=initialY-2')
    old="and r('Player_State')==0 and math.abs(r('Player_Y_Position')-initialY)<=2"
    assert controller.count(old)==1
    controller=controller.replace(old,"and jumpSourceMin<=jumpSourceStart-6 and ps(0x618)==0 and ps(0x617)==15 "+old)
    old='native_reservation_reads=reservationReads,full_stage=false'
    assert controller.count(old)==1
    controller=controller.replace(old,'native_reservation_reads=reservationReads,jump_source_start=jumpSourceStart,jump_source_min=jumpSourceMin,jump_native_min=jumpMinY,full_stage=false')
    kwargs['scope']+=' Source190 measured original standing action3 has6px actor lift and2px physical-foot lift; require both plus original mode0/pose15 return. This replaces an invalid8px fixture threshold, preserving actual takeoff/landing assertions.'
    return original(output,rom,controller,[*refs,Path(__file__),J.P.R/'build/prince-control-recipe-1103-v190/control-recipe.json'],**kwargs)

if __name__=='__main__':
    J.original=finalize
    J.P.prepare=J.prepare
    J.P.main()
