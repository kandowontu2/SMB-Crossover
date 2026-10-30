"""Source-built uncalled-marker control: same corrected shared graphics row."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_ff_joint_source_v1 as B
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import location
from prepare_cv3_dmc_mirror import prepare
P=R/'build/ff-fx-world-marker-proposal-v2';O=R/'build/ff-fx-world-marker-reference-v1'

def run(d,cmd,phase):
    B.save(d/(phase+'-validated-outputs.json'),validate(cmd,O,cwd=R));B.run(d,cmd,phase)

def main():
    assert not O.exists();h=json.loads((P/'source-closure.json').read_text());files=set()
    for p,s in h['bindings'].items():assert B.sha(p)==s,p;files.add(Path(p))
    O.mkdir();d=O/'joint';d.mkdir()
    for f in(P/'joint').rglob('*'):
        if f.is_file()and f.suffix in['.s','.inc','.cfg','.chr','.bin']:
            q=d/f.relative_to(P/'joint');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(f.read_bytes())
    p=d/'src/metasprite_engine.s';s=p.read_text()
    a='''::FwNativeFlashProbe:
  cmp #22
  bne SamusFreezeFlashOwner
  jsr FfMuxWorldDraw
  rts
  .res 3,$ea
'''
    z='''::FwNativeFlashProbe:
  cmp #22
  beq NativeFlash
  jmp SamusFreezeFlashOwner
  .res 4,$ea
'''
    assert s.count(a)==1;B.write(p,s.replace('.import FfMuxWorldDraw\n','').replace(a,z))
    p=d/'private.cfg';B.write(p,p.read_text().replace((P/'joint').as_posix(),d.as_posix()))
    cmd=json.loads((P/'joint/main-build.json').read_text())['command']
    run(d,[v.replace(str(P/'joint'),str(d))for v in cmd],'main-build')
    cmd=json.loads((P/'joint/final-link.json').read_text())['command']
    cmd=[v.replace(str(P/'joint/candidate'),str(d/'candidate')).replace(str(P/'joint/private.cfg'),str(d/'private.cfg')).replace(str(P/'joint/main.o'),str(d/'main.o'))for v in cmd]
    run(d,cmd,'final-link');prepare(R,d/'candidate.nes')
    old=qualified(P/'joint/candidate.nes');new=qualified(d/'candidate.nes');at=location(new,'FwNativeFlashProbe')
    dif=[i for i,(a,z)in enumerate(zip(old['raw'],new['raw']))if a!=z]
    assert all(at<=i<at+11 for i in dif)
    files|={Path(__file__),P/'source-closure.json'}|{Path(v)for v in cmd if v.endswith('.o')}|{f for f in O.rglob('*')if f.is_file()}
    B.save(O/'source-closure.json',dict(passed=True,native=False,admitted=False,reference_only=True,
        candidate_sha256=B.sha(d/'candidate.nes'),marker_sha256=B.sha(P/'joint/candidate.nes'),
        only_changed_source='Original native flash probe; unused marker data identical, no runtime marker call.',changed_bytes=len(dif),
        bindings={str(f.resolve()):B.sha(f)for f in sorted(files)}))
    print(json.dumps(dict(passed=True,ROM=B.sha(d/'candidate.nes'),changed_bytes=len(dif))),flush=True)

if __name__=='__main__':main()
