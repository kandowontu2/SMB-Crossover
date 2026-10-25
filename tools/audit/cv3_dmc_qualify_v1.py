"""Bind narrow CV3 injury source/CPU/native paired qualification receipts."""
from pathlib import Path
import argparse,csv,hashlib,json
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);a=p.parse_args();d=a.packet
 before=read(d/'proposal-v1/prepare.json');cpu=read(d/'cpu-v3/proof.json');flagoff=read(d/'flagoff-v1/proof.json');assert cpu['passed']and flagoff['passed'];native=[];matched=[]
 for name in('grant','alucard','sypha','simon','link'):
  dirs=[d/f'native-{name}-baseline-v1',d/f'native-{name}-v1'];old,new=[read(q/'native-proof.json')for q in dirs]
  assert all(q['passed']for q in(old,new));assert new['ROM_sha256']==before['candidate_ROM_sha256']and old['ROM_sha256']==before['baseline_ROM_sha256']
  if name in('grant','alucard'):assert all(not q['sourceExact']for q in old['cases'])and all(q['sourceExact']for q in new['cases'])
  else:
   for x,y in zip(old['cases'],new['cases']):
    apu=lambda q:[(r['age'],r['register'],r['value'])for r in q['apu']if r['register']not in(0x4014,0x4016)]
    assert x['name']==y['name']and apu(x)==apu(y)and x['durationUpdates']==y['durationUpdates'],name
  c=[]
  for path in dirs:
   rows=[{k:int(v)for k,v in r.items()}for r in csv.DictReader((path/'cadence.csv').open())if int(r['case'])==2]
   c.append(dict(frames=len(rows),zero_update_frames=sum(q['updates']==0 for q in rows),draws=sum(q['draws']for q in rows),updates=sum(q['updates']for q in rows)))
  assert c[0]['updates']==c[1]['updates']==180 and c[0]['draws']==c[1]['draws']
  if name not in('grant','alucard'):assert c[0]==c[1]
  matched.append(dict(character=name,before=c[0],after=c[1],extra_wall_frames=c[1]['frames']-c[0]['frames']))
  native.append(dict(character=name,cases=len(new['cases']),real_injuries=sum(q['realInjuries']for q in new['cases']),hardware_DMC_starts=sum(q['dmcStarts']for q in new['cases']),min_SP=new['min_sp'],candidate_receipt_sha256=sha(dirs[1]/'native-proof.json'),baseline_receipt_sha256=sha(dirs[0]/'native-proof.json')))
 result=dict(passed=True,accepted=False,candidate_ROM_sha256=before['candidate_ROM_sha256'],baseline_ROM_sha256=before['baseline_ROM_sha256'],changed_bytes=before['changed_bytes'],changed_banks=before['changed_banks'],source_manifest_sha256=sha(d/'proposal-v1/prepare.json'),source_capacity_sha256=sha(d/'capacity-source-v1/proof.json'),CPU_receipt_sha256=sha(d/'cpu-v3/proof.json'),ordinary_build_receipt_sha256=sha(d/'flagoff-v1/proof.json'),native=native,native_candidate_cases=sum(q['cases']for q in native),native_baseline_cases=sum(q['cases']for q in native),matched_pressure=matched,added_pressure_cost='Alucard +1 wall/zero-update frame in270 while retaining91draws/180updates; Grant and all unchanged controls no pressure cadence loss.',limitations=['Sypha native sourceExact means unchanged no-DMC control; her authentic distinct source75 remains missing.','Original72 primary sample/storage/priority remains unimplemented.','Noise28-update cue remains accepted ae97; pending-native Alucard injury verifies active noise/DMC coexistence, not a new complete noise-cue timing suite.','Native explicitly staged actor contact arenas; no campaign or identical waveform claim.'],tool_sha256=sha(__file__))
 (d/'qualification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
