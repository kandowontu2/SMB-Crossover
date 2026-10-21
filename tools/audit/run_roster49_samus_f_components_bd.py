"""Run unchanged native Samus component fixtures on the immutable F ROMs."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-f-samus-components-bd'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert not H.exists();H.mkdir()
    cp=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json';assert sha(cp)=='c0f31e09027aad704fc539e95adc0a53abb035fef647206b61bb10d94c8068e2';c=json.loads(cp.read_text())
    fixtures=['samus-energy-drops-202','samus-weapon-families','samus-world-sfx']
    names=[f'tests/{n}.lua'for n in fixtures]+['tests/remaining-energy-drops.lua','tests/guest-world-sfx.lua','tests/menu-bootstrap.lua','tools/run_mesen.py','tools/audit/run_mesen_isolated.py']
    dependencies={n:sha(R/n)for n in names}
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    size=workspace_bytes(R);assert size+100000000<70000000000
    prep=dict(script_sha256=sha(__file__),checkpoint_sha256=sha(cp),dependencies=dependencies,workspace_before=size,global_cap=70000000000,phase_cap=120000000,reserve=20000000,
      explicit_fixture_mode='Hard1, selected by existing menu-bootstrap. Authored state, ownership and forced RNG; not an ordinary controller route or natural RNG sample.',production_source_edits=False)
    (H/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n')
    groups=[]
    for mapper in ['mmc3','mmc5']:
        for fixture in fixtures:
            for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
            for n,h in dependencies.items():assert sha(R/n)==h,n
            owned=sum(p.stat().st_size for p in H.rglob('*')if p.is_file());assert owned+20000000+20000000<120000000
            out=H/f'{mapper}-{fixture}';out.mkdir()
            q=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(R/f'tests/{fixture}.lua'),str(cp.parent/f'smb-crossover-{mapper}.nes'),'--timeout','90'],cwd=R,capture_output=True,text=True)
            log=H/f'{mapper}-{fixture}-host.log';log.write_text(q.stdout+q.stderr)
            item=dict(mapper=mapper,fixture=fixture,exit=q.returncode,host_log_sha256=sha(log),files={str(p.relative_to(H)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in out.rglob('*')if p.is_file()})
            groups.append(item);(H/'partial.json').write_text(json.dumps(groups,indent=2)+'\n');print(mapper,fixture,'exit',q.returncode,flush=True)
    report=dict(status='PASS_CURRENT_F_SAMUS_COMPONENT_FIXTURES_BOTH_MAPS'if all(g['exit']==0 for g in groups)else'RETAINED_CURRENT_F_SAMUS_COMPONENT_FAILURES',script_sha256=sha(__file__),preparation_sha256=sha(H/'preparation.json'),groups=groups,
      assertion_scopes={
        'samus-energy-drops-202':'Authored owned missile state, real controller missile kill, forced RNG roll, distinct world ammo item, later selection change and walking collection restore original pool by2; not unbiased drop-rate sampling or natural upgrade acquisition.',
        'samus-weapon-families':'Continuously authored three beam forms and three bomb explosions. Each spatial slot receives real hardware OAM time in each24-update window; not controller creation, hit damage or pixel-perfect graphics validation.',
        'samus-world-sfx':'Authored world sound queues assert APU channel ownership/output/release/restoration, MMC5 expansion coexistence, pause/unpause. Not actual block/coin event generation or waveform listening.'},
      production_ROM_changed=False,all_arsenal_complete=False,final_recordings_complete=False,goal_complete=False)
    for n,h in dependencies.items():assert sha(R/n)==h,n
    dst=H/'review.json';dst.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],sha(dst),flush=True)
    return 0 if all(g['exit']==0 for g in groups)else 1
if __name__=='__main__':raise SystemExit(main())
