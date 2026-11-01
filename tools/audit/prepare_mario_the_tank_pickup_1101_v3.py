"""Clear the first Goomba, return beneath the mushroom, then pursue it."""
from pathlib import Path
import prepare_mario_the_tank_pickup_1101_v1 as N
def main():
    original=N.prepare
    def prepare(output,rom,c,refs,**kw):
        c=c.replace('local trace,maxStatus={},0','local trace,maxStatus={},0\nlocal routeStep=0')
        c=c.replace("if x<330 then pad.right=true end\n  if x>=290 and x<350 then pad.a=true end", """if age<=200 then
   if x<330 then pad.right=true end
   if x>=290 and x<350 then pad.a=true end
  elseif routeStep==0 then
   pad.left=true
   if x<=350 then routeStep=1 end
  elseif routeStep==1 then
   pad.a=true;pad.right=true
   if r('Player_State')==0 and x>350 then routeStep=2 end
  elseif x<410 then pad.right=true end""")
        c=c.replace('age==100 or age==200','age==300 or age==400')
        c=c.replace('age>=360','age>=600').replace('frame>1200','frame>1500')
        return original(output.with_name('probe3'),rom,c,[*refs,Path(__file__)],**kw)
    N.prepare=prepare;N.main()
if __name__=='__main__':main()
