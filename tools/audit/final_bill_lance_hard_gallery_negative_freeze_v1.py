"""Freeze first native Bill fixture failure and pending Lance, without retry."""
from pathlib import Path
import argparse,csv,json
from PIL import Image
from final_bill_lance_hard_gallery_source_v1 import D,ROOT,SHA,sha,put


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 packet=D/'final-bill-lance-hard-gallery-ready-v4';final=packet/'final-freeze-v1';native=packet/'profiles/bill-hard/native';lance=packet/'profiles/lance-hard/native'
 assert sha(final/'proof.json')=='c553b66c870341af670d38f87c71a8a60186ba56e97261e0192cde9f10214d19'
 assert sha(final/'ROOT-grant-bill-hard.json')=='3d9b417746db9267b3d46ac25f583544368c26fd9ec5fc089fed8d7b7507782e'
 assert sha(final/'ROOT-grant-lance-hard.json')=='0c28acffbac4c7f3e7497cc78b0177bf0378c008d5b8720c4cc8b8a88d53e442'
 run=json.loads((native/'proof.json').read_text());assert not run['passed']and run['native_run']and run['worker_released']and run['launches']==1 and run['retries']==0 and run['dependencies_unchanged']and run['ROM_sha256']==SHA
 assert not(lance/'launch.json').exists()and not(lance/'proof.json').exists()
 failure=json.loads((native/'first-failure.json').read_text());assert failure['message']=='Weapon upgrade remains the seeded mushroom form; no invented tier transform'
 cadence=list(csv.DictReader((native/'bill-cadence.csv').open(newline='')))
 assert len(cadence)==2 and [z['kind']for z in cadence]==['entry','finish']
 assert all(z['phase']=='settle'and z['update']=='1'and z['wall']=='395'for z in cadence)
 ppu=list(csv.DictReader((native/'actual-ppu-index.csv').open(newline='')))
 assert len(ppu)==395 and all(z['updates']=='0'and z['tier']=='0'for z in ppu)
 assert (native/'actual-ppu.argb').stat().st_size==395*245760
 assert (native/'events.jsonl').stat().st_size==0
 assert len(list(csv.DictReader((native/'apu.csv').open(newline=''))))==0
 counts=dict(complete256DMAs=0,startFrame_epochs=0,scoped_enables=0,late_scoped_enables=0)
 for line in(native/'ability-dma-epochs.jsonl').open():
  q=json.loads(line)
  if q['kind']=='completed-DMA-before-render-enable':
   counts['complete256DMAs']+=1
   assert q['id']==counts['complete256DMAs'] and q['page']==2 and len(q['source'])==len(q['hardware'])==len(q['writes'])==256 and q['source']==q['hardware']and not q['differences']
   assert q['start']['mask']&24==q['complete']['mask']&24==0 and q['start']['oamaddr']==q['complete']['oamaddr']==0
   for i,w in enumerate(q['writes']):assert w['stamp']['oamaddr']==i and w['stamp']['mask']&24==0 and w['value']==q['source'][i]
  elif q['kind']=='startFrame-hardware':counts['startFrame_epochs']+=1
  elif q['kind']=='actual-PPUMASK-write'and q['scoped']and q['enabling']:
   counts['scoped_enables']+=1
   if not q['safe']:counts['late_scoped_enables']+=1
 assert counts['late_scoped_enables']==0
 raw=(native/'first-failure.argb').read_bytes();assert len(raw)==245760
 Image.frombytes('RGBA',(256,240),raw,'raw','BGRA').convert('RGB').save(a.output/'actual-first-failure.png')
 module=(ROOT/'tools/audit/final_bill_lance_hard_gallery_native_v2.lua').read_text()
 assert module.index("phase='settle';age=0")<module.index("if phase=='settle'and age>=30 then")
 guard="assert(r('PlayerStatus')==1 and r('GuestPowerupActive')==0,'Weapon upgrade remains the seeded mushroom form; no invented tier transform')"
 assert module.index(guard)<module.index('if not current then return end')
 summary=dict(passed=False,freeze_complete=True,native_aggregate_remains_FALSE=True,ROM_sha256=SHA,
  actual_launches=1,retries=0,worker_released=True,Lance='PENDING / UNRUN: conditional grant not activated after Bill FALSE',
  first_failure=failure,observed_Main=cadence,complete_PPU_frames_before_failure=395,
  observed_cold_mode_at_last_complete_PPU=int(ppu[-1]['mode']),observed_tier_at_last_complete_PPU=int(ppu[-1]['tier']),
  no_case_setup_physical_grant_use_or_native_SFX_observed=True,partial_hardware=counts,
  classification='Fixture chronology: first GameLoop enters cold settle; powered-form assertion runs at its first finish, before the explicit age30 B-state seed. No case/setup/grant/use has begun. Not evidence of a ROM weapon defect.',
  limits='The first-failure image is the emulator buffer at a mid-frame assertion, not a separately completed frame396. Exact failure-time PlayerStatus/GuestPowerupActive RAM values were not logged; entry guard certifies cold tier0 and prior complete395PPU tier0. No late scene/ability/waveform/all-image or gallery acceptance.',
  next_step='Prepare a separate settle-aware fixture requiring actual cold tier0/no transform before seed; enforce powered-form guard only after the guarded seed. Add whole first-entry→29settle→age30seed→finish state-machine models. No new native grant or retry inferred.')
 put(a.output/'proof.json',summary)
 files={Path(__file__),final/'proof.json',final/'manifest.json',final/'ROOT-grant-bill-hard.json',final/'ROOT-grant-lance-hard.json',lance/'run.lua',lance/'config.json'}
 files.update(f for f in native.iterdir()if f.is_file());files.update(a.output.iterdir())
 bindings={Path(z['path']):z['sha256']for z in json.loads((final/'manifest.json').read_text())['bindings']}
 for f,h in bindings.items():assert sha(f)==h,f
 bindings.update({f:sha(f)for f in files})
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),sha256=h,bytes=f.stat().st_size)for f,h in sorted(bindings.items())]))
 print(json.dumps(dict(native_aggregate_remains_FALSE=True,freeze_complete=True,proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(bindings),partial_hardware=counts,Lance_unrun=True,worker_released=True)))


if __name__=='__main__':main()
