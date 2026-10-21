"""Independently audit the D Bill clear and retain actual E transfer negatives."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-ice-integrated-e'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
FIELDS='frame poll world level area areaType x y yHigh state vx vy power engine mode task lives camera buttons'.split()
def rows(p):
    with p.open(newline='')as f:return list(csv.DictReader(f))
def files(p):return{q.name:dict(bytes=q.stat().st_size,sha256=sha(q))for q in p.iterdir()if q.is_file()}
def main():
    out=H/'route-review-ba.json';assert not out.exists()
    phase=V/'specialist-bill-lance-current-d-a/phase-freeze-m.json'
    assert sha(phase)=='3f6f2ace3ac3edf609953256158691c17ea0a0f986dace81dce5ac4eee467292'
    f=json.loads(phase.read_text());assert len(f['files'])==843
    for n,h in f['files'].items():assert sha(R/n)==h,n
    preserved=[]
    for n,z in f['preserved_freezes'].items():
        q=R/n;assert sha(q)==z['sha256'];p=json.loads(q.read_text());assert len(p['files'])==z['verified_files']
        for k,h in p['files'].items():assert sha(R/k)==h,k
        preserved.append(dict(path=n,sha256=sha(q),files=len(p['files'])))
    d=R/'build/checkpoints/roster-audit-v49-sophia-head-axis-d/manifest.json';dc=json.loads(d.read_text())
    for n,h in dc['source_hashes'].items():assert sha(Path(f['source_directory'])/n)==h,n
    for b in dc['builds']:
        for z in b['artifacts'].values():assert sha(R/z['frozen_path'])==z['sha256']
    accepted=f['accepted']['Bill_Easy_MMC5'];p=R/accepted['proof'];m=json.loads((p/'manifest.json').read_text())
    assert sha(p/'manifest.json')==accepted['manifest_sha256']
    assert m['verified_through_2_2']and m['full_frame_audit']and m['controller_only']and not m['memory_or_register_writes']and not m['config']['record']
    assert m['result']['cleared']and m['result']['all_six_stages']and m['result']['frames']==39517 and not m['result']['deaths']
    assert sha(p/'smb-crossover-mmc5.nes')==m['rom_sha256']=='1d84dbb52d73a6748c8663c2bc44b09ac303b7a3e31b78119dfe3e57811f468a'
    hand=R/accepted['handoff'];assert sha(hand)==accepted['sha256'];hr=json.loads(hand.read_text())
    before=R/hr['comparison']['reference'];a,b=rows(before/'trace.csv'),rows(p/'trace.csv')
    assert len(a)==len(b)==39517 and all(all(x[k]==y[k]for k in FIELDS)for x,y in zip(a,b))
    native_fields=hr['comparison']['native_telemetry_fields'];a,b=rows(before/'bill-telemetry.csv'),rows(p/'bill-telemetry.csv')
    assert len(a)==len(b)==39018 and all(all(x[k]==y[k]for k in native_fields)for x,y in zip(a,b))
    assert (p/'inputs.csv').read_bytes()==(before/'inputs.csv').read_bytes()
    assert sha(p/'inputs.csv')==accepted['input_sha256']=='0c69e9a4dbcf08ae05a84bea956ed3a2595e3045cbc902ada451e72b5f4606ab'
    identity=json.loads((p/'ordinary-identity.json').read_text());assert identity==accepted['identity']
    end=[x for x in rows(p/'trace.csv')if x['world']=='1'and x['level']=='2'and x['engine']=='8'and x['mode']=='1'and x['task']=='3']
    assert len(end)>=25 and end[0]['x']=='40'and end[-1]['x']=='70'
    assert accepted['support_unknown']==0
    actual_bill=dict(status='PASS_ROOT_REHASHED_D_MMC5_BILL_FULL_FIXED_CLEAR',phase_sha256=sha(phase),
      frozen_files_rehashed=843,preserved_freezes=preserved,manifest_sha256=sha(p/'manifest.json'),identity=identity,
      result=m['result'],movement_rows_exact=39517,native_rows_exact=39018,movement_fields=FIELDS,
      native_fields=native_fields,next_level=dict(rows=len(end),x=[40,70]),
      full_audit_streams={n:dict(bytes=(p/n).stat().st_size,sha256=sha(p/n))for n in 'inputs.csv trace.csv events.csv render.csv oam.csv chr.csv scroll-writes.csv audio-events.csv stomp-events.csv'.split()},
      all_files=files(p),limits='D/Easy0 only, not E, damage-free, all-arsenal, source enemy geometry or final movie.')
    progress=json.loads((H/'route-progress-ba.json').read_text());assert progress['status']=='BOTH_ACTUAL_E_TRANSFERS_TERMINAL'
    pre=json.loads((H/'route-preparation-ba.json').read_text());transfers=[]
    for z in progress['results']:
        mp=z['mapper'];p=R/f'build/roster-through-2-2/root49-e-samus-transfer-a-2-v0-{mp}'
        old=R/pre['parents'][mp]['path'];m=json.loads((p/'manifest.json').read_text())
        assert sha(p/'manifest.json')==z['manifest_sha256']
        assert not m['verified_through_2_2']and m['result']['failure']=='death'and m['full_frame_audit']and not m['memory_or_register_writes']
        assert m['controller_only']and not m['config']['record']
        assert rows(p/'inputs.csv')==rows(old/'inputs.csv')[:len(rows(p/'inputs.csv'))]
        a,b=rows(old/'trace.csv'),rows(p/'trace.csv');first=None
        for x,y in zip(a,b):
            if any(x[k]!=y[k]for k in FIELDS):
                first=dict(frame=int(y['frame']),fields={k:[x[k],y[k]]for k in FIELDS if x[k]!=y[k]},
                  skipped_NMIs=[int(x['nmiSkipped']),int(y['nmiSkipped'])]);break
        assert first is not None
        transfers.append(dict(mapper=mp,result=m['result'],first19field_difference_vs_D=first,
          actual_E_ROM_sha256=m['rom_sha256'],identity=json.loads((p/'current-c-identity.json').read_text()),
          files=files(p),runtime_bug_proven=False,
          next='Bind completed-update and actual input-producer timing before changing movement or collision.'))
    report=dict(status='PASS_D_BILL_MMC5_PROOF_REVIEW_TWO_ACTUAL_E_SAMUS_TRANSFER_NEGATIVES_RETAINED',
      script_sha256=sha(__file__),Bill_D_MMC5=actual_bill,Samus_E_transfers=transfers,
      E_routes_admitted=0,all_roster_complete=False,all_arsenal_complete=False,final_recordings_complete=False,goal_complete=False)
    out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],sha256=sha(out),E_negatives=[dict(mapper=z['mapper'],result=z['result'],first=z['first19field_difference_vs_D'])for z in transfers])))
if __name__=='__main__':main()
