"""Admit actual D Mario/Luigi clears and retain seven older-tape negatives."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-d-remaining-routes-ax'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
    with p.open(newline='')as f:return list(csv.DictReader(f))
FIELDS='frame poll world level area areaType x y yHigh state vx vy power engine mode task lives camera buttons'.split()
STREAMS='inputs.csv trace.csv events.csv render.csv oam.csv chr.csv scroll-writes.csv audio-events.csv stomp-events.csv'.split()
def main():
    out=H/'review.json';assert not out.exists()
    pre=json.loads((H/'preparation.json').read_text());status=json.loads((H/'progress.json').read_text())
    assert status['status']=='ALL_CANDIDATES_TERMINAL'and len(status['results'])==9
    proofs=[]
    for source,s in zip(pre['parents'],status['results']):
        p=R/f"build/roster-through-2-2/root49-d-roster-ax-{source['character']}-v0-mmc3";old=R/source['path']
        assert sha(old/'manifest.json')==source['manifest_sha256']and sha(old/'inputs.csv')==source['inputs_sha256']
        m=json.loads((p/'manifest.json').read_text());assert sha(p/'manifest.json')==s['manifest_sha256']
        assert m['rom_sha256']==pre['ROM_sha256']==sha(p/'smb-crossover-mmc3.nes')
        assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']and not m['config']['record']
        a,b=rows(old/'trace.csv'),rows(p/'trace.csv');oldinputs,inputs=rows(old/'inputs.csv'),rows(p/'inputs.csv')
        assert inputs==oldinputs[:len(inputs)]
        identity=json.loads((p/'current-c-identity.json').read_text())
        assert identity['character']==source['character']and identity['behavior']==0 and identity['outlinesOff']==1
        first=None
        for x,y in zip(a,b):
            if any(x[k]!=y[k]for k in FIELDS):
                first=dict(frame=int(y['frame']),fields={k:[x[k],y[k]]for k in FIELDS if x[k]!=y[k]},
                  skipped_NMIs=[int(x['nmiSkipped']),int(y['nmiSkipped'])]);break
        if s['verified']:
            assert source['character']in[0,8]and first is None and len(a)==len(b)
            assert m['result']['all_six_stages']and m['result']['deaths']==0
            exact={n:(p/n).read_bytes()==(old/n).read_bytes()for n in STREAMS};assert all(exact.values()),exact
            end=[x for x in b if x['world']=='1'and x['level']=='2'and x['engine']=='8'and x['mode']=='1'and x['task']=='3']
            assert len(end)>=25 and end[0]['x']=='40'and int(end[-1]['x'])>40
            assert all(int(x['buttons'])&1 for x in end[-24:])
        else:
            assert not m['verified_through_2_2']and m['result']['failure']=='death'and first is not None
            exact=None
        proofs.append(dict(character=source['character'],name=source['name'],revision='D',mapper='mmc3',identity=identity,
          full_clear=s['verified'],result=m['result'],first19field_difference_vs_older_tape=first,
          whole_nine_streams_literal=exact,parent=source,
          actual_next_level_response=(dict(active_frames=len(end),x=[int(end[0]['x']),int(end[-1]['x'])])if s['verified']else None),
          files={n.name:dict(bytes=n.stat().st_size,sha256=sha(n))for n in p.iterdir()if n.is_file()},
          source_runtime_bug_proven=False,arsenal_complete=False,final_recording=False))
    result=dict(status='TWO_ACTUAL_D_FULL_CLEARS_SEVEN_OLDER_TAPE_TRANSFER_NEGATIVES_RETAINED',script_sha256=sha(__file__),
      preparation_sha256=sha(H/'preparation.json'),proofs=proofs,
      limits=['Passing Mario/Luigi full hardware/audio streams are literal to currentC, with actual D ROM and ordinary menu identity.',
       'Seven older tapes die on currentD. First divergence and NMI counts are evidence, not automatic physics, enemy, or mapper defect diagnoses.',
       'Parent behavior/default semantics and exact first differing completed update must be checked before adapting controls or modifying runtime.',
       'These are full-audit controller tests, not final movies or all-arsenal source-parity proof.'],goal_complete=False)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],sha256=sha(out))))
if __name__=='__main__':main()
