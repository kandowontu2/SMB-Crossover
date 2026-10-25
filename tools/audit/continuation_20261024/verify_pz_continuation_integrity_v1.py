from pathlib import Path
import json,hashlib,os,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;Q=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-head-pz')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=json.loads((D/'ryu-head-packet-v5/packet.json').read_text());bad=[n for n,h in p['source_files'].items()if not (R/n).is_file()or sha(R/n)!=h];assert not bad,bad
receipt=json.loads((R/'build/verification/native-head-pz/proof.json').read_text());assert all(sha(R/'build'/n)==h for n,h in receipt['unchanged_public_ROMs'].items())
assert sha(R/'Player Guide/SMB-Crossover-Players-Guide-NU.pdf')==receipt['guide_sha256']
size=sum(e.stat().st_size for path,dirs,files in os.walk(R)for f in files if (e:=Path(path)/f).is_file());assert size<30_000_000_000,size
b=json.loads((Q/'background-v1/proof.json').read_text());assert b['scan_complete']and len(b['runs'])==36 and b['candidate_events']==0
q=dict(passed=True,source_files=1217,source_unchanged=True,public_four_ROMs_unchanged=True,guide_unchanged=True,workspace_bytes=size,full_roster_proof_sha256=sha(Q/'full-roster-aggregate-v2/proof.json'),native_components_proof_sha256=sha(Q/'items-v1/proof.json'),background_physical_PNGs=sum(r['frames']for r in b['runs']),background_eligible_triples=sum(r['triples']for r in b['runs']),background_candidates=0,scope='Root source/public/guide integrity and source-associated exact receipts. Narrow diagnostic background coverage excludes persistent/sprite/longer defects; goal remains incomplete.')
(Q/'continuation-integrity-v1.json').write_text(json.dumps(q,indent=2));print(json.dumps(q))
