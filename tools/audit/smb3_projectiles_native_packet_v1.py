"""Check exact-hash native/source/flag-off receipts and assemble review packet."""
from pathlib import Path
import argparse,hashlib,json
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,required=True);a=p.parse_args();d=a.evidence
 read=lambda n:json.loads((d/n).read_text())
 prep=read('composed49-v2/prepare.json');cpu=read('composed49-cpu-v1/proof.json');flags=read('composed49-flagoff-v1/proof.json');original=read('original-hammer-lifetime-final-v2/proof.json')
 assert sha(d/'composed49-v2/candidate.nes')==prep['candidate_sha256']==cpu['ROM_sha256']
 assert cpu['passed']and sum(cpu['checks'].values())==1248
 assert flags['passed']and all(q['byte_identical']for q in flags['results'])
 assert original['passed']and original['actual_original_updates']==8
 assert original['driver_sha256']==sha(ROOT/'tools/audit/smb3_projectiles_native_source_v1.py')
 runs=[];dependencies=None
 for name,variant in [('composed49-baseline-native-v1',None),('composed49-mario-native-v1',0),('composed49-luigi-native-v1',1)]:
  q=read(name+'/native-proof.json');assert q['emulator_exit']==0 and len(q['cases'])==40
  hashes={k:q[k]for k in ['fixture_sha256','runner_sha256','imported_NMI_guard_source_sha256','emulator_sha256']}
  if dependencies is None:dependencies=hashes
  assert hashes==dependencies,'Native qualification dependencies changed between paired runs'
  assert q['fixture_sha256']==sha(ROOT/'tools/audit/smb3_projectiles_native_v1.lua')
  assert q['runner_sha256']==sha(ROOT/'tools/audit/smb3_projectiles_native_v1.py')
  if variant is None:
   assert q['ROM_sha256']==prep['parent_sha256']and not q['passed']and q['failed_cases']==20
   expected={r['name']for r in q['cases']if r['enemy']==45 or(r['enemy']==2 and r['kind']==2)}
   assert {r['name']for r in q['cases']if not r['passed']}==expected
  else:
   assert q['ROM_sha256']==prep['candidate_sha256']and q['passed']and q['failed_cases']==0
   assert all(r['passed']and r['launches']==1 for r in q['cases'])
   assert all((r['sfx2']&128)!=0 and r['hp_after']==0 for r in q['cases']if r['enemy']==45 and r['hp_before']==1)
  runs.append(dict(folder=name,variant=variant,ROM_sha256=q['ROM_sha256'],passed=q['passed'],expected_negative=variant is None,
                   cases=len(q['cases']),failed_cases=q['failed_cases'],PPU_snapshots=len(q['physical_PPU_files']),
                   nmis=q['nmis'],irq_scroll_writes=q['irq_scroll_writes'],min_sp=q['min_sp'],
                   hardware_chr_window_checks=q['hardware_chr_window_checks'],body_oam_checks=q['body_oam_checks'],
                   shot_oam_checks=q['shot_oam_checks'],complete_dma_checks=q['complete_dma_checks']))
 sheet=Image.new('RGB',(3*256,2*260),(24,28,36));draw=ImageDraw.Draw(sheet)
 for row,(case,age,label)in enumerate([(4,12,'Buzzy / hammer'),(9,30,'Bowser / fire / last HP')]):
  for col,(folder,title)in enumerate([('composed49-baseline-native-v1','BASELINE 49'),('composed49-mario-native-v1','REPAIR / MARIO'),('composed49-luigi-native-v1','REPAIR / LUIGI')]):
   files=sorted((d/folder).glob(f'case-{case:02d}-age-{age:02d}-*.png'));assert files
   with Image.open(files[0])as image:sheet.paste(image,(col*256,row*260+20))
   draw.text((col*256+2,row*260+2),title+' / '+label,fill='white')
 sheet.save(d/'final-comparison.png')
 files=[d/'composed49-v2/prepare.json',d/'composed49-v2/implementation.patch',d/'composed49-cpu-v1/proof.json',d/'composed49-flagoff-v1/proof.json',d/'original-hammer-lifetime-final-v2/proof.json',d/'final-comparison.png']
 files +=[d/r['folder']/'native-proof.json'for r in runs]
 report=dict(passed=True,accepted=False,goal_complete=False,parent_sha256=prep['parent_sha256'],candidate_sha256=prep['candidate_sha256'],
             source_changes=prep['source_changes'],changed_PRG_banks=[90],changed_bytes=51,CPU_components=1248,
             native_positive_cases=80,native_paired_negative_cases=40,source_consecutive_original_updates=8,
             original_hammer_lifetime='Active through each repeated overlap; boss counter decrements once/update without new hurt state/timer. Source35-hit balance differs from native SMB1 five-HP adaptation.',
             ordinary_mappers_byte_identical=True,runs=runs,files={str(p.relative_to(d)):sha(p)for p in files},
             dependencies=dependencies,driver_sha256=sha(Path(__file__)),
             limits='Staged native combat qualification. Forms/enemies/terrain/behavior are explicitly seeded after genuine cold menu/alternate selection; protected player and pinned living Bowser. No natural power acquisition, 1-1/castle traversal, every terrain/Bowser phase, acoustic comparison, physical-console or complete-game guarantee. Human PPU review is sampled; automated source-descriptor/OAM/CHR ownership checks cover recorded native publications.')
 (d/'final-packet.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(passed=True,candidate_sha256=report['candidate_sha256'],native_positive_cases=80,negative_cases=40,PPU_snapshots=sum(r['PPU_snapshots']for r in runs),packet_sha256=sha(d/'final-packet.json')),indent=2))
if __name__=='__main__':main()
