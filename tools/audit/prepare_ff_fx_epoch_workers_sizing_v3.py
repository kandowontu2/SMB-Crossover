"""Bind genuine absolute SmPosePtr; never pretend it is a zero-page pair."""
from pathlib import Path
import json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_ff_joint_source_v1 as B
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address
P=R/'build/ff-fx-epoch-workers-sizing-v2';O=R/'build/ff-fx-epoch-workers-sizing-v3'

def main():
    O.mkdir(exist_ok=False)
    source=(P/'workers.s').read_text()
    assert source.count('.importzp R0,R1,R2,R3,R4,R5,R6,R7,SmPosePtr')==1
    source=source.replace('.importzp R0,R1,R2,R3,R4,R5,R6,R7,SmPosePtr',
        '.importzp R0,R1,R2,R3,R4,R5,R6,R7\n.import SmPosePtr')
    needle=' ldy #0\n lda (SmPosePtr),y'
    assert source.count(needle)==1
    source=source.replace(needle,' lda SmPosePtr\n sta R0\n lda SmPosePtr+1\n sta R1\n ldy #0\n lda (R0),y')
    B.write(O/'workers.s',source);(O/'rom.s').write_bytes((P/'rom.s').read_bytes())
    b=qualified(R/'build/ff-fx-world-marker-proposal-v2/joint/candidate.nes');assert address(b,'SmPosePtr')==0x6b06
    sizes={}
    for name in ['workers','rom']:
        cmd=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'-g','--cpu','6502x','--create-full-dep',str(O/(name+'.dep')),'-o',str(O/(name+'.o')),str(O/(name+'.s'))]
        B.save(O/(name+'-validated-outputs.json'),validate(cmd,O,cwd=R));B.run(O,cmd,name+'-compile')
        q=subprocess.run([str(R/'tools/Windows/cc65/bin/od65.exe'),'--dump-segments',str(O/(name+'.o'))],cwd=R,text=True,capture_output=True);assert q.returncode==0
        sizes[name]={n:int(z)for n,z in re.findall(r'Name:\s*"([^"]+)"\s*Flags:[^\n]*\s*Size:\s*(\d+)',q.stdout)if int(z)}
    B.save(O/'sizing.json',dict(passed=True,unlinked=True,installed=False,aliases_executed=False,sizes=sizes,
        genuineSmPosePtr=0x6b06,retained_design_negatives=['v1 would discard native outputC; v2 incorrectly declared absoluteSmPosePtr aszp. Neither linked nor executed.'],
        packing={'BECF..BFE0':['FF_EPOCH_MAIN','FF_EPOCH_HEARTBEAT'],'A289..A300':['FF_EPOCH_CLASSIFY'],'B68B..B700':['FF_EPOCH_PACKET'],
            'A6E5..A700':['FF_EPOCH_COLORS'],'BFF0..C000':['FF_EPOCH_TABLES']},
        bindings={str(f.resolve()):B.sha(f)for f in[Path(__file__),P/'sizing.json']+[f for f in O.rglob('*')if f.is_file()]}))
    print(json.dumps(sizes),flush=True)

if __name__=='__main__':main()
