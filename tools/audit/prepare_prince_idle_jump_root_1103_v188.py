"""Use the original standing-jump input gate; preserve the earlier braking negative."""
from pathlib import Path
import prepare_prince_current_body_root_1103_v185 as P

original=P.prepare
def prepare(output,rom,controller,refs,**kwargs):
    old="elseif part=='reversed-rest'and advances-partAdvance>=2 then"
    assert controller.count(old)==1
    controller=controller.replace(old,old.replace('>=2 then',">=2 and ps(0x618)==0 and ps(0x617)==15 and ps(0x6c0)==0 then"))
    old="if part=='source-jump'and advances-partAdvance<2 then return{'a'}end;"
    assert controller.count(old)==1
    controller=controller.replace(old,"if part=='source-jump'and not jumpStarted then return{'a'}end;")
    old='local jumpMinY,jumpImage=nil,false'
    assert controller.count(old)==1
    controller=controller.replace(old,old+'\nlocal jumpStarted=false')
    old="elseif part=='source-jump'then\n  jumpMinY="
    assert controller.count(old)==1
    controller=controller.replace(old,"elseif part=='source-jump'then\n  if ps(0x616)==3 or r('Player_Y_Position')<initialY-2 then jumpStarted=true end\n  require(jumpStarted or advances-partAdvance<16,'Bounded original idle15/mode0 standing A admission')\n  jumpMinY=")
    kwargs['scope']+=' Distinct188 waits for the actual original idle15/mode0/A-lock0, holds A until real action3/takeoff; prior braking13 negative retained. No game code or state writes.'
    return original(output,rom,controller,[*refs,Path(__file__)],**kwargs)

if __name__=='__main__':
    P.prepare=prepare
    P.main()
