"""Inspect the collision profile actually consumed by native terrain code."""
from pathlib import Path
import prepare_metal_storm_collision_trace_1101_v16 as V
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
def main():
    original=V.prepare
    def prepare(output,rom,c,refs,**kw):
        b=qualified(rom);hooks=''
        c=c.replace('or id<7','or id<9')
        for i,name in [(9,'GBBAdr'),(10,'BlockBufferColli_Side')]:
            pc=address(b,name);bank=((location(b,name)-16)//8192)|128
            assert pc<0xa000 and bank==254
            hooks+=f"emu.addMemoryCallback(function() event({i}) end,emu.callbackType.exec,{pc})\n"
        c=c.replace('local function shot',hooks+'local function shot')
        return original(output.with_name('fixed-probe-trace'),rom,c,[*refs,Path(__file__)],**kw)
    V.prepare=prepare;V.main()
if __name__=='__main__':main()
