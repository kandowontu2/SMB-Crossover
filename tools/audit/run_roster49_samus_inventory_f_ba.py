"""Re-execute the unchanged explicit Hard inventory fixture on both current ROMs."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-f-samus-inventory-ba'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert not H.exists();H.mkdir()
    cp=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json';c=json.loads(cp.read_text())
    assert sha(cp)=='c0f31e09027aad704fc539e95adc0a53abb035fef647206b61bb10d94c8068e2'
    deps=['tests/samus-inventory-202.lua','tests/remaining-inventory.lua','tests/menu-bootstrap.lua','tools/run_mesen.py','tools/audit/run_mesen_isolated.py']
    dep_hashes={n:sha(R/n)for n in deps}
    (H/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),checkpoint_sha256=sha(cp),dependencies=dep_hashes,
      scope='Existing explicit Hard/mature-private-pickup collision and controller-attack fixture. Authored map/ammo/inventory state writes; not ordinary item generation, route, or final movie.',
      phase_cap=120000000,reserve=20000000,global_cap=70000000000),indent=2)+'\n')
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    groups=[]
    for b in c['builds']:
        mapper=b['mapper'];o=H/mapper;o.mkdir()
        for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
        for n,h in dep_hashes.items():assert sha(R/n)==h,n
        rom=R/b['artifacts']['nes']['frozen_path'];assert sha(rom)==b['artifacts']['nes']['sha256']
        total=workspace_bytes(R);size=sum(p.stat().st_size for p in H.rglob('*')if p.is_file())
        assert size+10000000+20000000<120000000 and total+10000000<70000000000
        args=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(o),str(R/'tests/samus-inventory-202.lua'),str(rom),'--timeout','60']
        q=subprocess.run(args,cwd=R,capture_output=True,text=True)
        log=H/f'native-{mapper}.log';log.write_text(q.stdout+q.stderr)
        groups.append(dict(mapper=mapper,exit=q.returncode,rom_sha256=sha(rom),host_log_sha256=sha(log),files={str(p.relative_to(H)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in o.rglob('*')if p.is_file()}))
        (H/f'result-{mapper}.json').write_text(json.dumps(groups[-1],indent=2)+'\n')
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    for n,h in dep_hashes.items():assert sha(R/n)==h,n
    result=dict(status='PASS_UNCHANGED_HARD_SAMUS_INVENTORY_FIXTURE_BOTH_CURRENT_F_MAPPERS'if all(g['exit']==0 for g in groups)else'RETAINED_HARD_SAMUS_INVENTORY_FIXTURE_NEGATIVE',groups=groups,
      preparation_sha256=sha(H/'preparation.json'),cases_each=6,
      asserted_scope='Six distinct mature private pickups via native collision; controller Morph/B missile and Ice/Wave spawn paths; missile shared-ammo cost. Mushroom/Long is an explicit initial ownership bit, passive pickup bits have no full contact-effect assertion here.',
      limits=['State-seeded arena, not ordinary eligible block reveal or natural enemy drops.','No complete all-enemy/contact/ammo/SFX/graphics/source-parity or lag proof.','Per-case screenshots retained for separate visual inspection; no final recordings.'],goal_complete=False,main_changed=False)
    (H/'review.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],sha(H/'review.json'),flush=True)
    return 0 if all(g['exit']==0 for g in groups)else 1
if __name__=='__main__':raise SystemExit(main())
