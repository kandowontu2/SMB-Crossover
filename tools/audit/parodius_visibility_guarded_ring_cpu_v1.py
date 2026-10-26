"""Execute every physical ring start and both near-full/empty body cursors."""
from pathlib import Path
from collections import Counter
import argparse,hashlib,itertools,json
from check_tmnt_render_oa import address
from check_roll_renderer import Memory
from link_pit_rygar_sophia_audit_cpu import scoped_load
from verify_native_relocation import NesMPU
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for n in ['rom','body-config','safe-poses','output']:ap.add_argument('--'+n,type=Path,required=True)
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=scoped_load(a.rom);l=lambda n:address(b,n)
    records=list(json.loads(a.body_config.read_text())['body_sources'].values());safe={(r['pool'],r['frame'])for r in json.loads(a.safe_poses.read_text())}
    profiles=[(96,120,1,0,1,8),(4,120,1,0,1,8),(96,24,1,0,1,8),(96,120,1,1,1,8),(96,120,1,0,0,8),(96,120,1,0,1,7)]
    base=bytearray(65536);stop=0x5b00;sp=217;base[0x101+sp]=(stop-1)&255;base[0x102+sp]=(stop-1)>>8
    count=0;paths=Counter();deltas=[];end256=0
    for rec in records:
        ref=rec['refs'][0];supported=(ref['pool'],ref['frame'])in safe;size=len(rec['parts'])*4
        alt=l('PnGuardAlt_'+rec['label'])if supported else rec['pointer']
        for start,cursor,profile in itertools.product(range(0,256,4),[0,12,220-size],profiles):
            x,y,yhi,flip,rotation_on,engine=profile;mem=bytearray(base)
            vals=dict(CurrentBank=205,CurrentBankC=rec['bank']|128,SelectedCharacter=18,VvVariant=ref['variant'],PnPool=ref['pool'],PnFrame=ref['frame'],Player_X_Position=x,Player_Y_Position=y,Player_Y_HighPos=yhi,CurrentOAMOffset=cursor,RgOamRotation=(start-cursor)&255,GuestOamRotationActive=rotation_on,ObjectVerticalFlip=flip,GameEngineSubroutine=engine)
            for n,v in vals.items():mem[l(n)]=v
            # A previously selected alternate is deliberate input. Every known
            # unsupported/edge/wrap must recover its literal original default.
            mem[l('SmPosePtr')]=alt&255;mem[l('SmPosePtr')+1]=alt>>8
            bus=Memory(b['raw'],mem,{0x8000:126,0xa000:77,0xc000:rec['bank'],0xe000:127});c=NesMPU(memory=bus);c.pc=l('PnBodyOrderBankStub');c.sp=sp;c.a=rec['bank']|128;c.x=73;c.y=19;c.p=0x6d
            for steps in range(2000):
                if c.pc==stop:break
                c.step()
            else:raise AssertionError(('Unbounded selector',rec['label'],start,cursor,profile))
            expected=supported and engine==8 and rotation_on and not flip and 32<=x<224 and 64<=y<176 and yhi==1 and start+size<=256
            got=bus.data[l('SmPosePtr')]+256*bus.data[l('SmPosePtr')+1]
            assert got==(alt if expected else rec['pointer']),(rec['label'],start,cursor,profile,hex(got),expected)
            assert c.sp==sp+2 and bus.banks[0xa000]==77 and bus.banks[0xc000]==rec['bank']
            assert not any(at in [l(n)for n in ['VvTemp','VvTemp2','PnDrawFrame']]for at,v in bus.writes)
            paths['sorted'if expected else'original']+=1;count+=1
            if expected and start+size==256:end256+=1
    q=dict(passed=True,native_run=False,component_only=True,ROM_sha256=sha(a.rom),tool_sha256=sha(Path(__file__)),body_records=131,all64_physical_ring_starts=True,cursor_choices=3,guard_profiles=len(profiles),actual_CPU_selector_cases=count,paths=dict(paths),exact_end256_admissions=end256,literal_original_fallback_after_previous_alternate=True,bank_SP_exact=True,no_VvTemp_or_PnDrawFrame_writes=True,limits='Selector CPU component only; partial AXYP/R0/R1/R3 are intentionally not compared. Complete DrawAll proof separately establishes returned AXYP and nonstackRAM liveness. Initial logical cursor/rotation are synthetic legal full-body capacities, not native controller reachability. No PPU/audio/native cadence verdict.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
