"""Independently decode the actual H Scrooge fixed replay and freeze its scope."""
from pathlib import Path
import csv,datetime,hashlib,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
rows=lambda p:list(csv.DictReader(Path(p).open(newline='')))

def main():
 out=V/'root49-scrooge-h-root-review-em.json';assert not out.exists()
 phase=V/'root49-scrooge-g-review-h-transfer-ej'
 review=phase/'review.json';assert sha(review)=='0c1abb5bb74ea8b1cb6704a5893f8567064d4f641c2ad08b3dade237264d5c1e'
 q=read(review);assert q['exit']==0 and q['verified']
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json'
 assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
 c=read(cp);s=Path(c['source_directory'])
 for n,h in c['source_hashes'].items():assert sha(R/n)==sha(s/n)==h,n
 for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==sha(s/'build/generated'/n)==h,n
 assert (len(c['source_hashes']),len(c['generated11']))==(458,11)
 for b in c['builds']:
  for a in b['artifacts'].values():assert sha(R/a['path'])==sha(R/a['frozen_path'])==a['sha256']
 hand=V/'specialist-mario-luigi-scrooge-current-g-a/milestone-handoff-scrooge-al.json'
 assert sha(hand)=='0372d9fc12a1d10cc0d5c6b44805edefbca8c7d8e9bbae9dccdfe89739c3f548'
 source=R/read(hand)['proof'];d=(R/q['H_manifest']).parent;m=read(d/'manifest.json')
 assert sha(d/'manifest.json')==q['H_manifest_sha256']
 assert m['rom_sha256']==sha(d/'smb-crossover-mmc3.nes')=='df226ab7be27a0f0b9231c1a66ac16200ba487ee041be10308dd6757343a8d6f'
 assert m['controller_only'] and m['full_frame_audit'] and not m['memory_or_register_writes'] and m['verified_through_2_2']
 assert m['config']['replay'] and not m['config']['prefix'] and not m['config']['record']
 assert m['result']==read(source/'manifest.json')['result']==q['result']
 assert m['result']['cleared'] and m['result']['all_six_stages'] and m['result']['deaths']==0 and m['result']['failure'] is None
 assert len(q['streams'])==11
 for n,z in q['streams'].items():assert sha(d/n)==sha(source/n)==z['H_sha256']==z['G_sha256'] and z['literal']
 for n in ['policy.lua','harness.lua','audit.lua']:
  assert not any(t in (d/n).read_text() for t in ['emu.write(','emu.setState(','emu.loadSavestate'])
 t=rows(d/'trace.csv');inputs=rows(d/'inputs.csv');assert len(t)==21742 and len(inputs)==21741
 stages={}
 for z in t:
  if (z['engine'],z['mode'],z['task'])==('8','1','3'):stages.setdefault(z['world']+'-'+z['level'],int(z['frame']))
 assert set(stages)>={'0-0','0-1','0-2','0-3','1-0','1-1','1-2'}
 tail=[z for z in t if int(z['frame'])>=stages['1-2']]
 assert len(tail)==25 and tail[0]['x']=='40' and tail[-1]['x']=='76'
 assert all((z['world'],z['level'],z['engine'],z['mode'],z['task'])==('1','2','8','1','3') for z in tail)
 sys.path.insert(0,str(R/'tools/audit'));from review_roster49_h_transfers_dl import hardware
 hw=hardware(d,21742);assert hw['actual_DMA']==20271
 catalog={str(p.relative_to(R)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in d.rglob('*') if p.is_file()}
 catalogue=phase/'root-H-catalog-em.json';assert not catalogue.exists();catalogue.write_text(json.dumps(catalog,indent=2)+'\n')
 report=dict(status='PASS_ROOT_ACTUAL_H_SCROOGE_MMC3_FULL_BASE_ROUTE',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),main_rehashed=dict(source=458,generated=11,artifacts=8),transfer_review_sha256=sha(review),G_root_review_sha256=sha(phase/'G-root-review.json'),manifest=q['H_manifest'],manifest_sha256=sha(d/'manifest.json'),identity=12,variant=0,behavior='Easy0',mapper='mmc3',actual_execution_revision='H',result=m['result'],real_2_3=dict(rows=25,x=[40,76]),literal_streams=list(q['streams']),hardware=hw,raw_catalog=dict(path=str(catalogue.relative_to(R)),sha256=sha(catalogue),files=len(catalog)),limits=q['source_limits']+['Actual H replay independently decoded; the original G support/corner/spring/source/tier limits remain. No new final movie or complete intrinsic/tier/arsenal claim.'],goal_complete=False)
 out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],sha256=sha(out),hardware=hw)))
if __name__=='__main__':main()
