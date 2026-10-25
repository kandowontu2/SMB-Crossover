from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;M=D/'ryu-head-oversized-mmc3-v12';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rom=sha(M/'candidate.nes')
entries=json.loads((M/'entry-all-v2/results.json').read_text());assert entries['ROM_sha256']==rom and len(entries['results'])==37 and all(r['exit']==0 for r in entries['results'].values())
checks=[]
for setting in ('off','on'):
 p=M/f'menu-v1/source-sprite-{setting}/pixel-proof.json';q=json.loads(p.read_text());assert q['passed']and q['ROM_sha256']==rom and len(q['stable_identity_pixels'])==37 and q['transition_frames']==2928 and not q['bad_frames'];checks.append(dict(path=str(p),sha256=sha(p)))
for relative in ('cache-key-cpu-v1/proof.json','zelda-pause-v1/build/verification/proof.json'):
 p=M/relative;q=json.loads(p.read_text());assert q['passed'];checks.append(dict(path=str(p),sha256=sha(p)))
for name in entries['results']:
 p=M/'entry-all-v2'/name.lower().replace(' ','-')/'build/verification/cache-proof.json';q=json.loads(p.read_text());assert q['boot_chr_bytes_verified']==262144 and q['no_MMC5_or_ExRAM_writes'];checks.append(dict(path=str(p),sha256=sha(p)))
q=dict(scoped_checks_passed=True,goal_complete=False,adopted=False,ROM_sha256=rom,exact_header_length_bytes=(M/'candidate.nes').stat().st_size,controller_only_cold_entries=37,pixel_exact_menu_poses=74,browsing_frames=5856,blank_or_mixed_portrait_frames=0,all_native_terrain_actor_preservation_checks_passed=True,checks=checks,remaining=['Full1-1 and shortcut/hard campaigns on this mapper','Whole weapon/item/upgrade/refill/SFX/fidelity matrix','Auxiliary source-pair adjacency and animation/overload proof beyond sampled cold movement','Independent source-bundle roundtrip, canonical tool integration and release installation','Physical cartridge verification'],scope='Current private oversized-MMC3 candidate only. Does not certify full campaigns or promote the release. Earlier failed private candidates remain retained. Cache CPU helper tests are distinct from native integration.')
(M/'scoped-proof.json').write_text(json.dumps(q,indent=2));print(json.dumps({k:v for k,v in q.items()if k not in('checks','remaining')}))
