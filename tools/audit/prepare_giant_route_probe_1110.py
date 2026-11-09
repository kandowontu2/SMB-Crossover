"""Read-only late-pit samples with the existing Giant controller unchanged."""
import argparse
from pathlib import Path
import prepare_mega_giant_f33_native_1110 as G
from prepare_selected_native_packet_v1 import prepare,sha


def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--output',type=Path,required=True)
 p.add_argument('--rom',type=Path,required=True)
 a=p.parse_args(); digest=sha(a.rom); source=G.controller(digest)
 b=G.Q.C.bundle(G.BASE.read_bytes())
 at=source.index('\n-- Actual Select')
 extra='\n'.join(f'C.ram.{n}={G.Q.C.address(b,n)}' for n in ('Player_Y_HighPos','Block_State','InjuryTimer'))
 source=source[:at]+'\n'+extra+source[at:]
 source=source.replace('local frame, updates, draws, lag','local probe,lastProbe={},-1\nlocal frame, updates, draws, lag',1)
 source=source.replace('terminal=state(),body=body,flag=flag,','terminal=state(),probe=probe,body=body,flag=flag,',1)
 at=source.index('local function choose()')
 source=source[:at]+'''local function sample()
 if x()<2370 or x()>2630 or lastProbe==updates or #probe>=250 then return end
 lastProbe=updates
 local row=state()
 row.vx=r('Player_X_Speed');row.vy=r('Player_Y_Speed');row.yp=r('Player_Y_HighPos')
 row.motion=r('Player_State');row.pad=r('A_B_Buttons');row.previous=r('PreviousA_B_Buttons')
 row.timer=r('TimerControl');row.status=r('PlayerStatus');row.injury=r('InjuryTimer')
 row.blocks={r('Block_State'),r('Block_State',1)}
 probe[#probe+1]=row
end

'''+source[at:]
 source=source.replace('if entered and playing() and owner() then observeSecondPipe() end',
                       'if entered and playing() and owner() then observeSecondPipe();sample() end',1)
 prepare(a.output,a.rom,source,{Path(__file__),Path(G.__file__),G.SOURCE,G.PROOF,G.ROUTE},
         expected=digest,timeout=240,allow_interactive=True,
         rom_symbols=(G.BASE.with_suffix('.lbl'),G.BASE.with_suffix('.dbg')),
         scope='Original Giant controller unchanged; bounded late-pit state observations only.')


if __name__=='__main__':main()
