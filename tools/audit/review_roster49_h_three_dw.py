"""Root physical review of three actual F-to-H ordinary fixed replays."""
from pathlib import Path
import csv,hashlib,importlib.util,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-h-three-transfer-do'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def main():
 out=V/'root49-h-three-root-review-dw.json';assert not out.exists()
 review=J/'review.json';assert sha(review)=='a60d83cce3d47bda1215ba500a01da49e98319e05b1d5c9c3709bf95752a9261';j=read(review);assert j['status']=='PASS_THREE_ACTUAL_H_FIXED_TRANSFERS'
 assert sha(V/'root49-h-route-root-review-dl.json')=='5b64c4e044d51ea5f97e27ebb10082f3bd991c804c8203058e64c359774d9b4d'
 path=R/'tools/audit/review_roster49_h_transfers_dl.py';sp=importlib.util.spec_from_file_location('H_DMA_DW',path);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
 accepted=[];catalog={};rows=lambda p:list(csv.DictReader(p.open(newline='')))
 for q in j['results']:
  d=(R/q['manifest']).parent;s=R/q['source'];m=read(d/'manifest.json');z=m['result']
  assert sha(d/'manifest.json')==q['manifest_sha256']and sha(s/'manifest.json')==q['source_manifest_sha256']
  assert m['verified_through_2_2']and m['full_frame_audit']and m['controller_only']and not m['memory_or_register_writes']and not m['config']['record']and m['config']['replay']and not m['config']['prefix']
  assert z['cleared']and z['all_six_stages']and z['deaths']==0 and z['failure']is None and z==read(s/'result.json')
  assert m['rom_sha256']==sha(d/'smb-crossover-mmc3.nes')=='df226ab7be27a0f0b9231c1a66ac16200ba487ee041be10308dd6757343a8d6f'
  assert q['exit']==0 and len(q['streams'])==9 and q['all_literal']
  for n,v in(q['streams']|q['extra']).items():assert(d/n).read_bytes()==(s/n).read_bytes()and sha(d/n)==v['H_sha256']
  t=rows(d/'trace.csv');inputs=rows(d/'inputs.csv');assert len(t)==z['frames']and len(inputs)==z['polls']and len(t[0])==21
  stage={}
  for a in t:
   if(a['mode'],a['task'],a['engine'])==('1','3','8'):stage.setdefault(a['world']+'-'+a['level'],int(a['frame']))
  assert set(stage)>={'0-0','0-1','0-2','0-3','1-0','1-1','1-2'}
  tail=[a for a in t if int(a['frame'])>=stage['1-2']];assert len(tail)==25 and tail[0]['x']=='40'and int(tail[-1]['x'])>40
  assert all((a['world'],a['level'],a['mode'],a['task'],a['engine'])==('1','2','1','3','8')for a in tail)
  hw=mod.hardware(d,z['frames'])
  for p in d.rglob('*'):
   if p.is_file():catalog[str(p.relative_to(R))]=dict(bytes=p.stat().st_size,sha256=sha(p))
  accepted.append(dict(character=q['character'],identity=q['identity'],variant=q['variant'],mapper='mmc3',execution_revision='H',manifest=q['manifest'],manifest_sha256=sha(d/'manifest.json'),result=z,actual_hardware=hw,real_2_3=dict(rows=25,x=[40,int(tail[-1]['x'])]),literal_nine_F_H=True,source_F_manifest_sha256=sha(s/'manifest.json')))
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';c=read(cp);assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
 for n,h in c['source_hashes'].items():assert sha(R/n)==h
 for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==h
 for b in c['builds']:
  for a in b['artifacts'].values():assert sha(R/a['path'])==a['sha256']
 frozen=J/'root-catalog-dw.json';assert not frozen.exists();frozen.write_text(json.dumps(catalog,indent=2)+'\n')
 result=dict(status='PASS_ROOT_H_BILL_LANCE_SOPHIA_EASY_MMC3_FIXED_BASE_ROUTES',script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),source_F_root_reviews={'Bill_Lance':'82a5739180507824f70ce918e5df7111100b1c3dfeeb0f09eab3c0387faadaad','Sophia':'60d0999d8e19088b915984abdc9550e708bbd12b18cd8ef4569f3904f0864031'},actual_H=accepted,raw_catalog=dict(path=str(frozen.relative_to(R)),sha256=sha(frozen),files=len(catalog)),limits=['Original independently reviewed F movement, injury, support and source-fidelity limitations remain. H actual literal streams, not retroactive renaming of F packets.','Three Easy/MMC3 base routes; no Hard, MMC5, every weapon/acquisition, final recorded or pixel/SFX-source parity claim.','All14/66, remaining routes, every original1-1 variant/item/enemy and final retained movies remain required.'],goal_complete=False)
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(sha256=sha(out),DMA=sum(a['actual_hardware']['actual_DMA']for a in accepted),raw_files=len(catalog))))
if __name__=='__main__':main()
