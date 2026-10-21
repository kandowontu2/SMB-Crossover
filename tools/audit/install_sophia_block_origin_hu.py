"""Publish the bounded Sophia fix with a recoverable source/artifact backup."""
from pathlib import Path
import datetime,hashlib,json,os,shutil,sys,zipfile
R=Path(__file__).resolve().parents[2];V=R/'build/verification';O=V/'root49-sophia-block-shift-hn';A=V/'root49-sophia-block-adoption-hu';K=R/'build/checkpoints/roster-audit-v49-sophia-block-origin-hu'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def atomic(path,data):
 temp=path.with_name(path.name+'.hu.tmp');assert not temp.exists();temp.write_bytes(data);os.replace(temp,path)
def main():
 assert not A.exists()and not K.exists()
 parent=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(parent)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c';h=read(parent)
 refs={'build-review-hp.json':'3af159d963334a6e5f9d1155a6a9fec4dca280467e14c67f8e017e77668e79d0','native-review-hr.json':'c5943b62b2068d3b048f691551b309bb0272e73965e30a0d3a691978d55c48bf','compiled-abi-hs.json':'5e965bb9f9f4d643b79a102766559ea88bb75db999cbddc2bb5d80d889c4343f','foreign-review-ht.json':'e7dd05de332d8feaad9440c2cb748f9ea6ad4f5fd48c68c65591cc228351f657'}
 for n,digest in refs.items():assert sha(O/n)==digest
 for name in ['native-review-hr.json','foreign-review-ht.json']:
  z=read(O/name);assert z['status'].startswith('PASS_')and all(g['exit']==0 for g in z['groups'])
  for g in z['groups']:
   for n,q in g['files'].items():assert sha(O/n)==q['sha256']and(O/n).stat().st_size==q['bytes']
 prep=read(O/'build-preparation-hp.json');assert sha(O/'build-preparation-hp.json')==read(O/'build-review-hp.json')['preparation_sha256']
 entries=dict(prep['source']);entries.update({'build/generated/'+n:digest for n,digest in prep['generated'].items()})
 changes=[n for n,digest in prep['source'].items()if digest!=h['source_hashes'][n]];assert changes==['src/bill_native_rare.s']
 before=dict(h['source_hashes']);before.update({'build/generated/'+n:digest for n,digest in h['generated11'].items()})
 for b in h['builds']:
  for q in b['artifacts'].values():before[q['path']]=q['sha256']
 for n,digest in before.items():assert sha(R/n)==digest,n
 for n,digest in entries.items():assert sha(O/'source'/n)==digest,n
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+120000000<100000000000
 A.mkdir();K.mkdir(parents=True)
 backup=A/'before-main-h.zip'
 with zipfile.ZipFile(backup,'x',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for n in before:z.write(R/n,n)
 with zipfile.ZipFile(backup)as z:
  assert len(z.namelist())==len(before)
  for n,digest in before.items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
 sourcezip=K/'source.zip'
 with zipfile.ZipFile(sourcezip,'x',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for n in entries:z.write(O/'source'/n,n)
 with zipfile.ZipFile(sourcezip)as z:
  for n,digest in entries.items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
 primary=[];baselines=[]
 for b in read(O/'build-review-hp.json')['builds']:
  rom=R/b['rom'];assert sha(rom)==b['sha256'];artifacts={}
  for ext in ['nes','dbg','lbl','map']:
   p=rom.with_suffix('.'+ext);dest=K/p.name;shutil.copyfile(p,dest);assert sha(p)==sha(dest)
   artifacts[ext]=dict(path='build/'+p.name,frozen_path=str(dest.relative_to(R)),bytes=p.stat().st_size,sha256=sha(p))
  (baselines if b['baseline']else primary).append(dict(mapper=b['mapper'],artifacts=artifacts))
 manifest=dict(status='PREPARED_PROVISIONAL_SOPHIA_BLOCK_ORIGIN_HU',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),publisher_sha256=sha(__file__),parent_checkpoint=dict(path=str(parent.relative_to(R)),sha256=sha(parent)),backup=dict(path=str(backup.relative_to(R)),sha256=sha(backup),files=len(before)),source_hashes=prep['source'],generated11=prep['generated'],source_changes=changes,generated_changes=[],source_directory=str(O/'source'),source_archive=dict(path=str(sourcezip.relative_to(R)),sha256=sha(sourcezip)),builds=primary,baseline_builds=baselines,admission_references={str((O/n).relative_to(R)):digest for n,digest in refs.items()},full_suite=h['full_suite'],limits=h['limits']+['HU changes exactly42 bytes on each mapper: a40-byte appended bank9 helper and a two-byte JSR operand. All old global PCs/RAM/header/CHR and both baseline ROMs are literalH.','64 authored native jump cases pass Easy/Hard and bothmappers with actual OAM halves, same-cell coins/mushroom and native bump queue requests.12 unchanged boot/block/weapon controls pass.2688 compiled helper cases preserve AXYP/banks/allRAM and all native ordered writes except three admitted origin fields and two precisely addressed popped stack bytes.','All14 accepted base routes and four retained movies remain H proofs. No automatic transfer toHU or fullgoal/release certification. PrivateK/Land/HUD/Ryu/visibleWater are not inHU.'],main_changed=False,accepted_release=False,goal_complete=False)
 target=K/'manifest.json';atomic(target,(json.dumps(manifest,indent=2)+'\n').encode('utf-8'))
 for n,digest in before.items():assert sha(R/n)==digest
 for n in changes:shutil.copyfile(O/'source'/n,R/n)
 for b in primary:
  for q in b['artifacts'].values():shutil.copyfile(R/q['frozen_path'],R/q['path'])
 for n,digest in entries.items():assert sha(R/n)==digest
 for b in primary:
  for q in b['artifacts'].values():assert sha(R/q['path'])==q['sha256']
 manifest.update(status='INSTALLED_PROVISIONAL_WORKING_SOPHIA_BLOCK_ORIGIN_HU',main_changed=True);atomic(target,(json.dumps(manifest,indent=2)+'\n').encode('utf-8'))
 doc=R/'docs/qa/sophia-block-origin-v49.md';assert not doc.exists()
 doc.write_text('Sophia block-origin correction, 21 October 2026\n\nThe supplied video shows a head-struck coin brick moving sideways during its bounce. The old native fixture reproduces a contact at world X112 with bounce X96. Sophia\'s wider source head can reach a neighboring cell while the old block constructor derives its X from Mario\'s center.\n\nThe correction uses the accepted source head query\'s actual column and page for the bouncing block, coin, or emerging power-up. Projectile-authored origins and fallback contacts retain the existing constructor. The same-cell replacement remains unchanged.\n\nBoth updated playable ROMs are installed in build/smb-crossover-mmc3.nes and build/smb-crossover-mmc5.nes. Frozen checkpoint: build/checkpoints/roster-audit-v49-sophia-block-origin-hu/manifest.json.\n\nValidation:64 native controller-jump cases across Easy/Hard and both mappers, including left/right edges, page crossings, question blocks, mushrooms, multi-coin bricks, ordinary brick bumps, actual OAM halves and bump queue requests.12 unchanged boot and other-character/projectile checks pass.2688 compiled helper controls preserve old registers, mapper state and complete RAM except the three intended origin bytes and two individually asserted popped stack cells. Both baseline ROMs are literal H; each playable ROM differs by42 bytes.\n\nThis is a targeted provisional fix. Existing H playthroughs retain their original ROM identity; full integrated roster/arsenal/performance and final recordings remain open. The initial failing H collision and HQ test-oracle omission are retained separately.\n',encoding='utf-8')
 report=dict(status='PASS_INSTALLED_PROVISIONAL_HU_REHASHED_SOURCE_AND_PRIMARY_ARTIFACTS',checkpoint=dict(path=str(target.relative_to(R)),sha256=sha(target)),source_changes=changes,primary_ROMS={b['mapper']:b['artifacts']['nes']['sha256']for b in primary},evidence=manifest['admission_references'],backup_sha256=sha(backup),QA_sha256=sha(doc),workspace_bytes=workspace_bytes(R),global_cap=100000000000,goal_complete=False)
 (A/'review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 assert workspace_bytes(A)+workspace_bytes(K)+20000000<120000000
 print(json.dumps(dict(checkpoint_sha256=sha(target),adoption_sha256=sha(A/'review.json'),ROMs=report['primary_ROMS'],workspace_bytes=report['workspace_bytes'])),flush=True)
if __name__=='__main__':main()
