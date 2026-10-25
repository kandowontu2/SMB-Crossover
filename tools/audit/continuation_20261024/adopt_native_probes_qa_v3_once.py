from pathlib import Path
import datetime,hashlib,json,os,shutil
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;P=D/'native-probes-qa-v2';packet=P/'packet-current-v3';S=packet/'source';O=P/'adoption-v3';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();receipt=R/'build/verification/native-probes-qa/proof.json';checkpoint=R/'build/checkpoints/native-probes-qa/checkpoint.json';assert not receipt.exists()and not checkpoint.exists(),'One-shot source adoption already recorded'
m=json.loads((packet/'packet.json').read_text());assert m['passed']and m['source_only_roundtrip_exact']and m['ordinary_flag_off_unchanged']and len(m['source_files'])==1220
assert all(sha(S/n)==h for n,h in m['source_files'].items());digest=sha(P/'candidate.nes');assert digest==m['ROM_sha256']=='054d9e33a84f628947b0dea15914ba2aae7796ca610a25548eab96407064384a'
evidence={}
for label,name in [('roster','full-roster-aggregate-v1/proof.json'),('components','items-v1/proof.json'),('CPU_legacy','cpu-v1/proof.json'),('CPU_others','cpu-other-v1/proof.json'),('native_guards','guards-v1/proof.json'),('profile','profile-v1/proof.json'),('matched_scene','matched-benchmark-v2/proof.json')]:
 p=P/name;q=json.loads(p.read_text());assert q['passed'];assert q.get('ROM_sha256',digest)==digest or label=='matched_scene';evidence[label]=dict(path=str(p),sha256=sha(p))
roster=json.loads((P/'full-roster-aggregate-v1/proof.json').read_text());assert roster['cases']==38 and len(roster['identities'])==37
p=P/'entry-v1/results.json';q=json.loads(p.read_text());assert q['rom_sha256']==digest and q['identities']==37 and len(q['results'])==37 and all(r['exit']==0 for r in q['results'].values());evidence['cold_entries']=dict(path=str(p),sha256=sha(p))
compat=R/'build/verification/mmc3-tools-current-v18/proof.json';q=json.loads(compat.read_text());assert q['passed']and q['adopted'];evidence['current_MMC3_compatibility']=dict(path=str(compat),sha256=sha(compat))
changes={n:dict(before=sha(R/n)if(R/n).exists()else None,after=h)for n,h in m['source_files'].items()if not(R/n).exists()or sha(R/n)!=h};assert set(changes)=={'src/characters.s','src/megaman_weapons.s'},changes
parent=json.loads((D/'ryu-head-packet-v5/packet.json').read_text());assert all(changes[n]['before']==parent['source_files'][n]for n in changes)
a=(R/'build/checkpoints/native-head-pz/candidate.nes').read_bytes();b=(P/'candidate.nes').read_bytes();assert len(a)==len(b);diff=[i for i,(x,y)in enumerate(zip(a,b))if x!=y];assert len(diff)==54 and set((i-16)//8192 for i in diff)=={126,127}
occupied=sum(os.stat(Path(dp)/n,follow_symlinks=False).st_size for dp,dn,ns in os.walk(R,followlinks=False)for n in ns);growth=sum((S/n).stat().st_size-(R/n).stat().st_size for n in changes);assert occupied+growth+20000<30_000_000_000
for n in changes:p=O/'root-before'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/n,p)
try:
 for n in changes:shutil.copy2(S/n,R/n)
 assert all(sha(R/n)==h for n,h in m['source_files'].items())
 proof=dict(passed=True,adopted=True,goal_complete=False,adopted_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),ROM_sha256=digest,parent_ROM_sha256=sha(R/'build/checkpoints/native-head-pz/candidate.nes'),changes=changes,changed_ROM_bytes=54,changed_PRG_banks=[126,127],new_RAM_bytes=0,new_CHR_bytes=0,new_OAM_bytes=0,evidence=evidence,current_source_file_count=1220,current_source_packet=str(packet/'source.zip'),current_source_packet_sha256=sha(packet/'source.zip'),current_ROM=str(P/'candidate.nes'),ordinary_flag_off_unchanged=True,public_releases_installed=False,workspace_bytes_before=occupied,source_byte_growth=growth,scope='Adopt only the qualified native-query CPU shortcut.38 strict independently replayed zero-death1-1 cases cover37 identities with selected modes, plus26 component cases,37 cold entries and bounded CPU/NMI proofs. Matched scenes show CPU savings for legacy families,116 extra cycles/update for the owning-family fallback example and no material throughput gain in those stationary scenes. This is not complete lag removal, all abilities/refill/SFX/expiry/source fidelity, both-mode/shortcut campaigns, MMC3 campaigns or physical hardware qualification.')
 receipt.parent.mkdir(parents=True,exist_ok=True);receipt.write_text(json.dumps(proof,indent=2));checkpoint.parent.mkdir(parents=True,exist_ok=True);checkpoint.write_text(json.dumps(dict(ROM=str(P/'candidate.nes'),ROM_sha256=digest,source_packet=str(packet/'source.zip'),source_packet_sha256=sha(packet/'source.zip'),adoption_proof=str(receipt),external_storage_reason='Retain native lossless evidence and keep workspace below30GB'),indent=2));(O/'proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(dict(adopted=True,ROM_sha256=digest,changes=list(changes),cases=38,identities=37,workspace_bytes_before=occupied,source_growth=growth)),flush=True)
except BaseException:
 for n in changes:shutil.copy2(O/'root-before'/n,R/n)
 raise
