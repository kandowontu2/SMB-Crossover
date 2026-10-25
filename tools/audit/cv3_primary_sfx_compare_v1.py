"""Compare frozen native cadence/music receipts without rerunning an emulator."""
from pathlib import Path
import argparse,csv,hashlib,json
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def proof(p):return json.loads((p/'native-proof.json').read_text())
def cadence(p):return [{k:int(v)for k,v in r.items()}for r in csv.DictReader((p/'cadence.csv').open())]
def writes(c,noise=True):return [(r['register'],r['value'])for r in c['apu']if r['register']<=0x4013 and(noise or r['register']not in(0x400c,0x400d,0x400e,0x400f))]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);a=p.parse_args();d=a.packet
 oldp,newp=d/'native-baseline-full-v2',d/'native-wrapper-full-v6';old,new=proof(oldp),proof(newp)
 before,after=cadence(oldp),cadence(newp);assert len(before)==len(after)
 matches=[]
 for x,y in zip(old['cases'],new['cases']):
  assert x['name']==y['name']and x['durationUpdates']==y['durationUpdates']
  if x['q']['kind']=='pressure':continue
  assert writes(x,False)==writes(y,False),x['name']
  if x['q']['kind']=='legacy':assert writes(x)==writes(y)
  matches.append(dict(case=x['name'],non_noise_writes_exact=len(writes(y,False)),legacy_full_writes_exact=len(writes(y))if x['q']['kind']=='legacy'else None))
 counts=lambda rows:dict(wall_frames=len(rows),zero_update_frames=sum(r['updates']==0 for r in rows),draws=sum(r['draws']for r in rows),updates=sum(r['updates']for r in rows))
 b,a2=counts(before),counts(after);assert a2['zero_update_frames']<=b['zero_update_frames']and a2['draws']>=b['draws']
 bp,ap=counts([r for r in before if r['case']==15]),counts([r for r in after if r['case']==15]);assert ap['draws']>=bp['draws']
 bills=[proof(d/n)for n in('native-bill-baseline-v2','native-bill-wrapper-v7')]
 for x,y in zip(*[q['cases']for q in bills]):
  hardware=lambda c:[(r['age'],r['register'],r['value'])for r in c['apu']if r['register']not in(0x4014,0x4016)]
  assert x['name']==y['name']and hardware(x)==hardware(y)and x['audioCycles']==y['audioCycles']
 bc,ac=[counts(cadence(d/n))for n in('native-bill-baseline-v2','native-bill-wrapper-v7')];assert bc==ac
 native=[new,proof(d/'native-wrapper-controls-v7'),bills[1]];assert all(q['passed']and q['ROM_sha256']==new['ROM_sha256']for q in native)
 result=dict(passed=True,accepted=False,candidate_ROM_sha256=new['ROM_sha256'],baseline_ROM_sha256=old['ROM_sha256'],matched_native_before=b,matched_native_after=a2,pressure_before=bp,pressure_after=ap,matched_nonpressure_music=matches,non_noise_writes_exact=sum(r['non_noise_writes_exact']for r in matches),Bill_cadence_exact=ac,Bill_hardware_APU_and_audio_cycles_exact=True,baseline_missing_source_cue_cases=[c['name']for c in old['cases']if c.get('sourceExact')is False],native_cases_on_exact_candidate=sum(len(q['cases'])for q in native),source_receipts={str(q.relative_to(d)):sha(q)for q in[d/'alucard-wrapper-v7/source-final.json',oldp/'native-proof.json',newp/'native-proof.json',d/'native-wrapper-controls-v7/native-proof.json',d/'native-bill-wrapper-v7/native-proof.json',d/'final-cpu-v2/proof.json',d/'flagoff-wrapper-v7/proof.json']},tool_sha256=sha(__file__),scope='Matched explicit arenas and exact original noise register update schedule; no full-roster/campaign or identical waveform claim. Melodic comparison uses ordered register/value pairs, excluding controller/OAM traffic and wall timestamps; noise source timing is independently asserted in native fixtures.')
 (d/'final-qualification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
