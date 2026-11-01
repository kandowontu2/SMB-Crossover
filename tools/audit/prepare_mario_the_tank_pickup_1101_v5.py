"""Stop route exploration at a lost life rather than following an automatic restart."""
from pathlib import Path
import prepare_mario_the_tank_pickup_1101_v4 as V
def main():
    original=V.V.N.prepare
    def prepare(output,rom,c,refs,**kw):
        c=c.replace('local jumpTicks=0','local jumpTicks=0\nlocal initialLives=nil')
        c=c.replace("shot('gameplay-entry');phase='walk'", "initialLives=r('NumberofLives');shot('gameplay-entry');phase='walk'")
        c=c.replace("if age>=2000 or r('GameEngineSubroutine')==11 then", "if age>=2000 or r('NumberofLives')~=initialLives or r('GameEngineSubroutine')==11 then")
        c=c.replace('"full_stage":false,"trace"', '"full_stage":false,"lost_life":%s,"trace"')
        c=c.replace("maxStatus,x,table.concat(trace,','))", "maxStatus,x,tostring(r('NumberofLives')~=initialLives),table.concat(trace,','))")
        return original(output.with_name('probe5'),rom,c,[*refs,Path(__file__)],**kw)
    V.V.N.prepare=prepare;V.main()
if __name__=='__main__':main()
