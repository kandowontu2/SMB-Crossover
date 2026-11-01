"""Add explicit release frames and a bounded position trace to Karnov route."""
from pathlib import Path
import prepare_karnov_stage_route_1101_v1 as V
def main():
    original=V.K.prepare
    def prepare(output,rom,controller,refs,**kw):
        controller=controller.replace('local maxX,gameFrames,lives,jumpAge=0,0,nil,0',
            "local maxX,gameFrames,lives,jumpAge=0,0,nil,0\nlocal release=0\nlocal trace=assert(io.open(OUTPUT..'positions.csv','w'));trace:write('frame,x,y,state,yspeed,jump,release\\n')")
        controller=controller.replace("if r('Player_State')==0 and jumpAge==0 then jumpAge=24 end", "if r('Player_State')==0 and jumpAge==0 and release==0 then jumpAge=36 end")
        controller=controller.replace('if jumpAge>0 then pad.a=true;jumpAge=jumpAge-1 end',
            'if jumpAge>0 then pad.a=true;jumpAge=jumpAge-1;if jumpAge==0 then release=8 end elseif release>0 then release=release-1 end')
        controller=controller.replace("local won=r('LevelNumber')~=0", "if gameFrames%10==0 then trace:write(string.format('%d,%d,%d,%d,%d,%d,%d\\n',gameFrames,x,r('Player_Y_Position'),r('Player_State'),r('Player_Y_Speed'),jumpAge,release));trace:flush()end\n  local won=r('LevelNumber')~=0")
        controller=controller.replace("shot('stage-endpoint')", "trace:close();shot('stage-endpoint')")
        return original(output,rom,controller,[*refs,Path(__file__)],**kw)
    V.K.prepare=prepare;V.main()
if __name__=='__main__':main()
