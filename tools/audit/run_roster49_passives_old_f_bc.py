"""Retain the unmodified legacy Ice/passive assertion failure on current F."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-f-samus-passives-bc'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert not H.exists();H.mkdir()
    cp=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json';c=json.loads(cp.read_text());assert sha(cp)=='c0f31e09027aad704fc539e95adc0a53abb035fef647206b61bb10d94c8068e2'
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    original=R/'tests/samus-passives-202.lua';(H/'original-samus-passives-202.lua').write_bytes(original.read_bytes())
    dependencies={n:sha(R/n)for n in ['tests/samus-passives-202.lua','tests/menu-bootstrap.lua','tools/run_mesen.py','tools/audit/run_mesen_isolated.py','reference/crossover2/extracted/scripts/com/smbc/enemies/Enemy.as']}
    (H/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),checkpoint_sha256=sha(cp),dependencies=dependencies,phase_cap=120000000,reserve=20000000,global_cap=70000000000,
      hypothesis='Current F first-freeze source-order admission does not apply ordinary damage, whereas legacy fixture expects75-40=35. Execute original fixture first without changing it.',
      scope='Explicit Hard native enemy/actor fixture; state writes are authored setup. Not a controller-only route.'),indent=2)+'\n')
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    assert workspace_bytes(R)+10000000<70000000000
    rom=cp.parent/'smb-crossover-mmc3.nes';o=H/'old-mmc3';o.mkdir()
    q=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(o),str(original),str(rom),'--timeout','60'],cwd=R,capture_output=True,text=True)
    (H/'old-mmc3-host.log').write_text(q.stdout+q.stderr)
    for n,h in dependencies.items():assert sha(R/n)==h,n
    r=dict(exit=q.returncode,rom_sha256=sha(rom),preparation_sha256=sha(H/'preparation.json'),host_log_sha256=sha(H/'old-mmc3-host.log'),files={p.name:sha(p)for p in o.iterdir()if p.is_file()},goal_complete=False)
    (H/'old-mmc3-result.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
