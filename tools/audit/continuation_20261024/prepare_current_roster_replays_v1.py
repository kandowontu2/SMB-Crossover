from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;out=D/'current-roster-index-v1';out.mkdir(exist_ok=False);digest='70480630828a92839938b18b3e4f73acd8f9255879b2174df00f41c2e6cf98c9'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sources=['known-routes-v3/discover-results.json','remaining-routes-v1/discover-results.json','remaining-routes-v2/discover-results.json','remaining-routes-v3/discover-results.json','remaining-routes-v4/discover-results.json','turtle-routes-v1/discover-results.json'];pairs={}
for source in sources:
 p=D/source;q=json.loads(p.read_text());assert q['complete']and q['ROM_sha256']==digest
 for row in q['runs']:
  if not row['passed']:continue
  folder=Path(row['folder']);m=json.loads((folder/'manifest.json').read_text());assert sha(folder/'manifest.json')==row['manifest_sha256']and m['ROM_sha256']==digest and m['result']['cleared']and m['result']['deaths']==0 and m['chr_commit']['passed']
  pairs.setdefault((row['identity'],row['mode']),row)
selected={}
for (name,mode),row in pairs.items():
 if name not in selected or(mode=='easy'and selected[name]['mode']=='hard'):selected[name]=row
assert len(selected)==36 and 'bass'not in selected
mega=D/'megaman-ledge-replay-v1/review-megaman-easy/proof.json';q=json.loads(mega.read_text());assert q['passed']and q['ROM_sha256']==digest
selected.pop('megaman');assert len(selected)==35
index=dict(ROM_sha256=digest,phase='discover',runs=list(selected.values()),existing_same_hash_qualified=dict(identity='megaman',mode='easy',proof=str(mega),proof_sha256=sha(mega)),pending_identities=['bass'],source_indexes=[dict(path=str(D/n),sha256=sha(D/n))for n in sources],scope='One actual current-ROM clean discovery per identity, Easy preferred when available. Mega Man is already independently qualified on this exact hash; Bass remains pending. These35selected discoveries require fresh independent direct replay and physical-frame review; no old-hash coverage is relabeled.')
(out/'index.json').write_text(json.dumps(index,indent=2)+'\n');print(json.dumps(dict(new_cases=len(selected),existing_qualified=1,pending=['bass'])))
