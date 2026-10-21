"""Additive retained-evidence allowance for the diagnosed HUD repair."""
from pathlib import Path
import datetime,hashlib,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
prior=V/'root49-rygar-hud-allocation-gi.json'
assert sha(prior)=='9ad29c469ff5ee90777717395917919b735f5dea910d658b60b1ecfa897b03c7'
phase=V/'specialist-rygar-hud-h-a'
sys.path.insert(0,str(R/'tools/playthroughs'))
from roster_run import workspace_bytes
used=workspace_bytes(R);local=workspace_bytes(phase)
assert used+300000000-local<80000000000
out=V/'root49-rygar-hud-allocation-gr.json';assert not out.exists()
z=dict(status='ADDITIVE_RETAINED_HUD_REPAIR_SUCCESSOR_ALLOWANCE',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),prior_authority=str(prior.relative_to(R)),prior_sha256=sha(prior),owner='mario_luigi_scrooge_s2',phase=str(phase.relative_to(R)),prior_cap=220000000,new_cap=300000000,reserve=50000000,phase_bytes=local,global_bytes=used,global_cap=80000000000,forecast_reported=279000000,authority='User requested retained lossless evidence and a raised cap; no files are deleted. Root expands this bounded private diagnosis/repair phase within the existing global allowance.',scope='Preserve candidate timing-transfer and uninitialized-pending negatives; explicit pending initialization successor, efficient bounded HUD packet handling, both-map actual native overflow scene and measured foreground/NMI costs. No main install or universal lag claim. All prior GI requirements remain.',goal_complete=False)
out.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(path=str(out.relative_to(R)),sha256=sha(out),phase_bytes=local,global_bytes=used)))
