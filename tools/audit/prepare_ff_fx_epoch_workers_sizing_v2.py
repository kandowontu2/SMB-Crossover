"""Unlinked ABI-corrected sizing: native C publication precedes RAM3 entry."""
from pathlib import Path
import json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_ff_joint_source_v1 as B
from private_build_outputs_v1 import validate
O=R/'build/ff-fx-epoch-workers-sizing-v2'

def main():
    O.mkdir(exist_ok=False)
    p=R/'tools/reference/ff_fx_epoch_workers_proposal_v1.s';s=p.read_text()
    first='''FfMuxNativeLate:
 ; This is the genuine original native DrawAll target, exactly once.
 sta SafecallA_SMC+1
 lda #<DrawAllMetasprites
 sta FarcallJmpTarget_SMC+1
 lda #>DrawAllMetasprites
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(DrawAllMetasprites)|$80)
 jsr FarCallCommon
 MP_SAVE'''
    assert s.count(first)==1
    s=s.replace(first,'FfMuxNativeLate:\n ; Genuine native DrawAll already completed in ROM A62.\n MP_SAVE')
    B.write(O/'workers.s',s)
    p2=R/'tools/reference/ff_fx_epoch_rom_proposal_v1.s';s=p2.read_text()
    needle=''' pla
 plp
 MP_WORKER FfMuxNativeLate'''
    replacement=''' pla
 plp
 ; Complete original DrawAll BEFORE capturing its genuine output C bank.
 ; FwCallEnter then preserves that actual publication while filtering OAM.
 sta SafecallA_SMC+1
 lda #<DrawAllMetasprites
 sta FarcallJmpTarget_SMC+1
 lda #>DrawAllMetasprites
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(DrawAllMetasprites)|$80)
 jsr FarCallCommon
 MP_WORKER FfMuxNativeLate'''
    assert s.count(needle)==1
    s=s.replace(needle,replacement).replace('=52,error','=70,error').replace('selector52B','selector70B')
    s=s.replace('=80,error','=98,error').replace('80B of proposed104B','98B of granted104B')
    B.write(O/'rom.s',s)
    allsizes={}
    for name in ['workers','rom']:
        cmd=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'-g','--cpu','6502x','--create-full-dep',str(O/(name+'.dep')),'-o',str(O/(name+'.o')),str(O/(name+'.s'))]
        B.save(O/(name+'-validated-outputs.json'),validate(cmd,O,cwd=R));B.run(O,cmd,name+'-compile')
        q=subprocess.run([str(R/'tools/Windows/cc65/bin/od65.exe'),'--dump-segments',str(O/(name+'.o'))],cwd=R,text=True,capture_output=True)
        assert q.returncode==0
        allsizes[name]={n:int(z)for n,z in re.findall(r'Name:\s*"([^"]+)"\s*Flags:[^\n]*\s*Size:\s*(\d+)',q.stdout)if int(z)}
    B.save(O/'sizing.json',dict(passed=True,unlinked=True,installed=False,aliases_executed=False,
        sizes=allsizes,retained_prior_design='First80B ROM prototype would incorrectly restore pre-DrawAll C through FwCallEnter. No cartridge was linked/executed with that design.',
        packing={'BECF..BFE0':['FF_EPOCH_MAIN','FF_EPOCH_HEARTBEAT'],'A289..A300':['FF_EPOCH_CLASSIFY'],
            'B68B..B700':['FF_EPOCH_PACKET'],'A6E5..A700':['FF_EPOCH_COLORS'],'BFF0..C000':['FF_EPOCH_TABLES']},
        bindings={str(f.resolve()):B.sha(f)for f in[Path(__file__),p,p2]+[f for f in O.rglob('*')if f.is_file()]}))
    print(json.dumps(allsizes),flush=True)

if __name__=='__main__':main()
