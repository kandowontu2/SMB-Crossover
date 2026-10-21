"""Rehash the final four-proof D packet and independently compare Lance Z to X."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'specialist-bill-lance-current-d-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
    with p.open(newline='')as f:return list(csv.DictReader(f))
def main():
    out=V/'root49-lance-d-mmc5-review-az.json';assert not out.exists()
    ab=H/'phase-handoff-ab.json';assert sha(ab)=='67e84ab2a62f019ed171b6896f7cb893bc8a1a85a7a01b7f9849e97185648edd';a=json.loads(ab.read_text())
    index=R/a['catalogue'];assert sha(index)==a['catalogue_sha256']=='dc9740fa3d7833bae3b5026fbcb834c5301b7a4afd79937f4f915bf64086bba5';f=json.loads(index.read_text())
    assert len(f['files'])==1686
    for n,h in f['files'].items():assert sha(R/n)==h,n
    preserved=[]
    for n,z in f['preserved_freezes'].items():
        q=R/n;assert sha(q)==z['sha256'];j=json.loads(q.read_text());assert len(j['files'])==z['verified_files']
        for k,h in j['files'].items():assert sha(R/k)==h,k
        preserved.append(dict(path=n,sha256=sha(q),files=len(j['files'])))
    cp=R/f['checkpoint'];assert sha(cp)==f['checkpoint_sha256'];d=json.loads(cp.read_text())
    for n,h in d['source_hashes'].items():assert sha(Path(f['source_directory'])/n)==h,n
    for b in d['builds']:
        for z in b['artifacts'].values():assert sha(R/z['frozen_path'])==z['sha256']
    accepted=f['accepted']['Lance_Easy_MMC5'];handoff=R/accepted['handoff'];assert sha(handoff)==accepted['sha256'];r=json.loads(handoff.read_text())
    x=R/r['comparison']['reference'];z=R/accepted['proof'];mx=json.loads((x/'manifest.json').read_text());mz=json.loads((z/'manifest.json').read_text())
    assert sha(z/'manifest.json')==accepted['manifest_sha256']
    assert mz['verified_through_2_2']and mz['full_frame_audit']and not mz['memory_or_register_writes']and mz['controller_only']and not mz['config']['record']
    assert mz['config']['character']==3 and mz['config']['variant']==1
    assert mz['result']['frames']==33044 and mz['result']['polls']==33043 and mz['result']['all_six_stages']and mz['result']['cleared']and not mz['result']['deaths']
    assert sha(x/'inputs.csv')==sha(z/'inputs.csv')==accepted['input_sha256']=='8f7fdd01292c057854949b3341936c6f4f10f15c324408cccdf3b036fcc00307'
    assert sha(z/'smb-crossover-mmc5.nes')==mz['rom_sha256']=='1d84dbb52d73a6748c8663c2bc44b09ac303b7a3e31b78119dfe3e57811f468a'
    fields=r['comparison']['fields'];xt,zt=rows(x/'trace.csv'),rows(z/'trace.csv');assert len(xt)==len(zt)==33044
    assert all(all(v[k]==w[k]for k in fields)for v,w in zip(xt,zt))
    native=r['comparison']['native_telemetry_fields'];xn,zn=rows(x/'bill-telemetry.csv'),rows(z/'bill-telemetry.csv')
    assert len(xn)==len(zn)==32545 and all(all(v[k]==w[k]for k in native)for v,w in zip(xn,zn))
    assert json.loads((z/'ordinary-identity.json').read_text())==accepted['identity']
    end=[q for q in zt if q['world']=='1'and q['level']=='2'and q['engine']=='8'and q['mode']=='1'and q['task']=='3']
    assert len(end)==25 and end[0]['frame']=='33020'and end[0]['x']=='40'and end[-1]['x']=='70'
    events=[json.loads(t)for t in(z/'bill-native-events.jsonl').read_text().splitlines()]
    attempted=sorted({q['frame']for q in events if q['event']=='InjurePlayer'});forced=sorted({q['frame']for q in events if q['event']=='ForceInjury'})
    assert attempted==[7893,27508,27643]and forced==[7893,27508]
    qualification=H/'injury-qualification-ab.json';assert sha(qualification)=='569092e44ebcb50c413b4d433954ca77cf3c7865c2cc31135d1b0a05032122b0'
    stomp=json.loads((z/'stomp-summary.json').read_text());assert stomp['illegal_guest_events']==0 and stomp['resident_opcode_mismatches']==0
    report=dict(status='PASS_ROOT_REHASHED_D_LANCE_MMC5_FULL_FIXED_CLEAR_AND_FINAL_FOUR_PROOF_PACKET',
      script_sha256=sha(__file__),handoff_AB_sha256=sha(ab),freeze_AA_sha256=sha(index),files_rehashed=1686,preserved_freezes=preserved,
      source_files_rehashed=455,frozen_primary_artifacts_rehashed=8,result=mz['result'],identity=accepted['identity'],
      movement_rows_exact=33044,movement_fields=fields,native_rows_exact=32545,native_fields=native,
      next_level_control=dict(rows=25,x=[40,70]),stomps=stomp,
      injury_qualification=dict(attempted_entries=attempted,ForceInjury_entries=forced,
        non_damaging_entry=27643,invulnerability_counter_not_sampled=True,qualification_sha256=sha(qualification)),
      streams={n:dict(bytes=(z/n).stat().st_size,sha256=sha(z/n))for n in 'inputs.csv trace.csv events.csv render.csv oam.csv chr.csv scroll-writes.csv audio-events.csv stomp-events.csv'.split()},
      limits=['Actual immutable D/Easy only; no F or Hard full-route retag.',
        'Zero-death, not damage-free or every item/weapon/attack/upgrade.',
        'Full hardware audit is Z; X discovery is not automatically a full hardware control.',
        'Native enemy integer proxies do not establish source fractional/bitmap/AI identity; no final movie/audio review.'],goal_complete=False)
    out.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],sha(out),flush=True)
if __name__=='__main__':main()
