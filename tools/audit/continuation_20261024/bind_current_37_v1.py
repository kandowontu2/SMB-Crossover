from pathlib import Path
import csv,hashlib,json
D=Path(__file__).resolve().parent;digest='70480630828a92839938b18b3e4f73acd8f9255879b2174df00f41c2e6cf98c9'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=D/'current-discovery-37-v1.json';q=json.loads(source.read_text());assert q['passed']and len(q['runs'])==37;rows=[]
for row in q['runs']:
 folder=Path(row['folder']);m=json.loads((folder/'manifest.json').read_text());assert m['ROM_sha256']==digest and m['exit']==0 and not m['fixed_replay']and m['result']['cleared']and m['result']['deaths']==0 and m['chr_commit']['passed']
 assert m['config']['name']==row['identity']and m['config']['behavior']==row['mode']and not m['config']['segmented']and not m['config']['allowDeaths']
 assert sha(folder/'policy.lua')==m['policy_sha256']
 assert 'emu.write('not in(folder/'policy.lua').read_text()and'dofile('not in(folder/'policy.lua').read_text()
 trace=list(csv.DictReader((folder/'trace.csv').open()));assert trace[-1]['world']=='0'and trace[-1]['level']=='1'and trace[-1]['engine']=='8'
 files={name:sha(folder/name)for name in ['manifest.json','run.lua','policy.lua','harness.lua','audit.lua','inputs.csv','trace.csv','chr-commit.json']}
 rows.append(dict(identity=row['identity'],mode=row['mode'],passed=True,folder=str(folder),frames=m['result']['frames'],deaths=0,actual_gameplay_areas=sorted({(int(x['world']),int(x['level']),int(x['area']),int(x['areaType']))for x in trace if x['engine']=='8'}),files=files))
assert len({x['identity']for x in rows})==37
out=dict(passed=True,goal_complete=False,ROM_sha256=digest,current_cold_menu_zero_death_1_1_identities=37,source_index_sha256=sha(source),driver_sha256=sha(Path(__file__)),runs=rows,scope='Every listed actual same-hash controller discovery starts through native cold menus, uses no state-writing policy or segmented/death recovery, clears1-1zero-death and reaches movable1-2. All selected frozen policies/input/state/CHR observations are bound. Difficulty modes and native areas are explicit; not all74mode pairs, two route variants, every item, strict independent physical replay or human visual completion.')
(D/'current-37-bindings-v1.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(passed=True,identities=37,total_frames=sum(x['frames']for x in rows))))
