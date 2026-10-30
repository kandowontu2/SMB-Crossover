"""Reject a faster route that skips an actual Final Fantasy palette service."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_upper_fx_windows_controls_1030_v2 as U
H=U.H;M=U.M;O=R/'build/new-roster-ui-fastpath-1030-v1';sha=U.sha


def main():
    out=O/'rejected-actual-FF-UI-negative.json';assert not out.exists()
    paths=[R/'build/current-character-composition-v2/joint/candidate.nes',O/'candidate.nes'];rows=[]
    for p in paths:
        b=H.C.qualified(p);m=M.setup(b)
        H.put(m,FfPaletteAck=1,GuestPowerupActive=0,StarInvincibleTimer=0,VRAM_Buffer1_Offset=0)
        hits=[]
        def observe(mem,c,i):
            if c.pc==H.address(b,'FwPaletteTick')and mem.rawtags[1]==190:hits.append(c.pc)
        c,_=H.invoke(m,'X5BounceUiDispatch',hook=observe)
        rows.append(dict(ROM_sha256=sha(p),actual_FwPaletteTick_calls=len(hits),
            queued_bytes=H.get(m,'VRAM_Buffer1_Offset'),palette_ack=H.get(m,'FfPaletteAck'),CPU=c.processorCycles))
    assert(rows[0]['actual_FwPaletteTick_calls'],rows[0]['queued_bytes'],rows[0]['palette_ack'])==(1,7,0)
    assert(rows[1]['actual_FwPaletteTick_calls'],rows[1]['queued_bytes'],rows[1]['palette_ack'])==(0,0,1)
    proof=dict(passed=False,reproduction_passed=True,candidate_rejected=True,native=False,installed=False,
        reason='Native inventory leaf skips genuine new-character UI services. FF loses its real palette tick/queue/ack despite lower CPU cost.',
        next_action='Preserve NrUi/source-service chain; only bypass irrelevant old Roll/Mac gates.',rows=rows,
        bindings={str(p.resolve()):sha(p)for p in[Path(__file__),Path(U.__file__),Path(H.__file__),Path(M.__file__),
            O/'source-closure.json',*paths,*[p.with_suffix('.dbg')for p in paths]]})
    out.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    print('REJECTED actual FF UI service regression; original assertions retained',flush=True)


if __name__=='__main__':main()
