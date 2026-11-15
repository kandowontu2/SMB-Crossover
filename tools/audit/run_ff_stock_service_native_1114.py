"""Single-queue native stock proofs on exactae66, reusing one Lua slot."""
from hashlib import sha256
import argparse,json
from pathlib import Path

import replay_ff_natural_stock_service_current_1114 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
FACTORY_SHA='0ce579b23cc1c2b8ebba484644f17979012e1670059cf76ed30e8a8681b2b7db'


def player(p):
    fields=('updates','completed','frame','x','y','engine','state','power','earned','charges','lives',
            'star','active','timer','life_lease','variant')
    return{k:p[k]for k in fields if k in p}


def event(e):
    if not e:return None
    q={k:e[k]for k in('actor','slot','score','cue','music','actual_FF_entries','timer')if k in e}
    for k in('player','after'):
        if k in e:q[k]=player(e[k])
    if 'before'in e:q['before']=event(e['before'])
    return q


def execute(key,lua):
    assert len(lua)==64 and all(c in'0123456789abcdef'for c in lua)
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==FACTORY_SHA
    guard=check(F.ROM);raw=F.ROM.read_bytes();assert sha256(raw).hexdigest()==F.PIN
    text=F.controller(raw,key);assert sha256(text.encode()).hexdigest()==lua
    assert{p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    image=(OUT/'candidate.nes').read_bytes()
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,F.ROM,OUT/'capture',F.PIN,240)
    assert q['script_SHA256']==lua and not q['images']and q['outputs_written']==0
    assert F.ROM.read_bytes()==raw and check(F.ROM)==guard
    assert(OUT/'candidate.nes').read_bytes()==image
    r=q['receipt'];s=r.get('stock_star'if key.endswith('-star')else'stock_oneup',{})
    details={k:event(s.get(k))for k in('born','mature','collector','collected','credit','score_awarded')}
    details.update(actual_entry_count=s.get('actual_FF_entries'),strictly_post_event_entries=s.get('resume'),
                   final_score=s.get('final_score'))
    return dict(passed=q['passed'],identity=key,ROM_SHA256=q['ROM_SHA256'],
        script_SHA256=q['script_SHA256'],receipt_SHA256=q['receipt_SHA256'],
        actual_Mesen=True,actual_Downloads_launch=True,seconds=q['seconds'],reason=r.get('reason'),
        completed_Main=r.get('completed_Main'),physical_frames=r.get('physical_frames'),
        actual_FF_entries=r.get('calls',{}).get('CurrentFFWorker'),stock=details,
        mushroom_ticks=r.get('mushroom',{}).get('ticks'),flower_ticks=r.get('flower',{}).get('ticks'),
        terminal=player(r.get('terminal',{})),images=0,outputs=0,ROM_changed=False,
        scope='Named-class natural stock acquisition and strictly post-event movement; no fullstage/audio/art/expiry/protected-hit claim')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--identity',nargs='+',choices=F.IDENTITIES,required=True)
    p.add_argument('--expected-lua',nargs='+',required=True)
    a=p.parse_args();assert len(a.identity)==len(a.expected_lua)
    for key,lua in zip(a.identity,a.expected_lua,strict=True):
        q=execute(key,lua)
        print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
        assert q['passed'],'Current named-class stock remains native-unqualified'
