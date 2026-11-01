"""Extend the successful mushroom route through the opening pipe section."""
from pathlib import Path
import prepare_mario_the_tank_pickup_1101_v3 as V
def main():
    original=V.N.prepare
    def prepare(output,rom,c,refs,**kw):
        c=c.replace('local routeStep=0','local routeStep=0\nlocal jumpTicks=0')
        c=c.replace(" emu.setInput(pad,0)",""" if phase=='walk' and age>600 and r('GameEngineSubroutine')==8 then
  pad={right=true,b=true}
  if r('Player_State')==0 and jumpTicks==0 then jumpTicks=24 end
  if jumpTicks>0 then pad.a=true;jumpTicks=jumpTicks-1 end
 end
 emu.setInput(pad,0)""")
        c=c.replace('age==300 or age==400','age==900 or age==1200')
        c=c.replace('age>=600 or','age>=2000 or').replace('frame>1500','frame>2800')
        kw['scope']='Controller-only mushroom route extended through opening pipes. Reports natural mushroom status only; does not assert stage completion.'
        return original(output.with_name('probe4'),rom,c,[*refs,Path(__file__)],**kw)
    V.N.prepare=prepare;V.main()
if __name__=='__main__':main()
