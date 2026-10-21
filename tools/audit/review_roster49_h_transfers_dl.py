"""Independent current H route identities, inputs, endpoint and physical DMA review."""
from pathlib import Path
import collections,csv,datetime,hashlib,json,zipfile
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-h-roster-transfer-dg'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
rows=lambda p:list(csv.DictReader(Path(p).open(newline='')))
def hardware(d,frames):
 render=rows(d/'render.csv');oam=rows(d/'oam.csv');dma={int(z['frame']):z for z in render if int(z['dmaCount'])}
 assert [int(z['frame'])for z in render]==list(range(500,frames+1))
 assert len(oam)==sum(int(z['dmaCount'])for z in render)and [int(z['frame'])+1 for z in oam]==list(dma)
 peak=over=0
 for q in oam:
  raw=bytes.fromhex(q['oamHex']);assert len(raw)==256
  visible=hud=0;edges=collections.Counter()
  for i in range(0,256,4):
   y=raw[i]+1
   if y<240:
    visible+=1;hud+=y<32;lo,hi=max(32,y),min(240,y+16)
    if lo<hi:edges[lo]+=1;edges[hi]-=1
  value=maximum=0
  for y in range(32,240):value+=edges[y];maximum=max(maximum,value)
  assert(visible,hud,maximum)==(int(q['visible']),int(q['hudSprites']),int(q['maxSprites']))
  assert int(dma[int(q['frame'])+1]['maxSprites'])==maximum
  peak=max(peak,maximum);over+=maximum>8
 return dict(render_rows=len(render),actual_DMA=len(oam),max_sprites=peak,over8_snapshots=over,lagNmi_flagged=sum(int(z['lagNmi'])!=0 for z in render),APU_writes=sum(int(z['apuWrites'])for z in render))
def main():
 out=V/'root49-h-route-root-review-dl.json';assert not out.exists()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c';c=read(cp);s=Path(c['source_directory'])
 for n,h in c['source_hashes'].items():assert sha(R/n)==sha(s/n)==h,n
 for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==sha(s/'build/generated'/n)==h,n
 assert(len(c['source_hashes']),len(c['generated11']))==(458,11)
 artifacts={}
 for b in c['builds']:
  for n,a in b['artifacts'].items():assert sha(R/a['path'])==sha(R/a['frozen_path'])==a['sha256'];artifacts[b['mapper']+'/'+n]=a['sha256']
 review=J/'review.json';assert sha(review)=='e6b84b04f17a3a874faef982a983c5f1478f74ebb6ad6a5ddbca269d99499d96';j=read(review);assert j['status']=='PASS_FOUR_ACTUAL_H_MMC3_COMPLETE_FIXED_TRANSFERS'
 prep=read(J/'preparation.json');assert sha(J/'preparation.json')==j['preparation_sha256']
 sourcecases={z['name']:z for z in prep['cases']};names=['inputs.csv','trace.csv','events.csv','render.csv','oam.csv','chr.csv','scroll-writes.csv','audio-events.csv','stomp-events.csv'];accepted=[];catalog={}
 for q in j['results']:
  d=(R/q['manifest']).parent;source=R/sourcecases[q['character']]['source'];m=read(d/'manifest.json');sm=read(source/'manifest.json');result=m['result'];assert sha(d/'manifest.json')==q['manifest_sha256']
  assert m['rom_sha256']==sha(d/'smb-crossover-mmc3.nes')=='df226ab7be27a0f0b9231c1a66ac16200ba487ee041be10308dd6757343a8d6f'
  assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']and m['verified_through_2_2']
  assert m['config']['replay']and not m['config']['prefix']and not m['config']['record']
  assert result['cleared']and result['all_six_stages']and result['deaths']==0 and result['failure']is None and result==sm['result']
  assert set(q['canonical'])==set(names)
  for n in names:
   assert (d/n).read_bytes()==(source/n).read_bytes()and sha(d/n)==q['canonical'][n]['sha256']
  for n,z in q['extra'].items():assert(d/n).read_bytes()==(source/n).read_bytes()and sha(d/n)==z['sha256']
  for n in['policy.lua','harness.lua','audit.lua']:
   assert not any(t in(d/n).read_text()for t in['emu.write(','emu.setState(','emu.loadSavestate'])
  t=rows(d/'trace.csv');inputs=rows(d/'inputs.csv');assert len(t)==result['frames']and len(inputs)==result['polls']and len(t[0])==21
  stages={}
  for z in t:
   if(z['engine'],z['mode'],z['task'])==('8','1','3'):stages.setdefault(z['world']+'-'+z['level'],int(z['frame']))
  assert set(stages)>={'0-0','0-1','0-2','0-3','1-0','1-1','1-2'}
  tail=[z for z in t if int(z['frame'])>=stages['1-2']];assert len(tail)==25 and tail[0]['x']=='40'and int(tail[-1]['x'])>40
  assert all((z['world'],z['level'],z['mode'],z['task'],z['engine'])==('1','2','1','3','8')for z in tail)
  hw=hardware(d,result['frames'])
  for p in d.rglob('*'):
   if p.is_file():catalog[str(p.relative_to(R))]=dict(bytes=p.stat().st_size,sha256=sha(p))
  accepted.append(dict(character=q['character'],identity=q['selected'],mapper='mmc3',execution_revision='H',manifest=q['manifest'],manifest_sha256=sha(d/'manifest.json'),result=result,real_2_3=dict(rows=25,Right_input_polls=sum(int(z['frame'])>=stages['1-2']and z['mask']=='1'for z in inputs),x=[40,int(tail[-1]['x'])]),hardware=hw,whole_canonical_G_H_literal=names))
 assert len(accepted)==4
 # H MMC5 is an exact full-binary identity of G.  This links the immutable
 # prior G executions; it does not invent new H native sessions.
 old=R/'build/checkpoints/roster-audit-v49-samus-head-axis-g/manifest.json';assert sha(old)=='feacfe9cf513d6c57dde8a4f2990e0bbd6c14ecda533d971747ad0011cee0fd0'
 assert(old.parent/'smb-crossover-mmc5.nes').read_bytes()==(cp.parent/'smb-crossover-mmc5.nes').read_bytes()
 ml=V/'specialist-mario-luigi-scrooge-current-g-a/milestone-handoff-j.json';assert sha(ml)=='dbe7c1fba625f744d11accbbbcef22d39440fa8010ff7977b508428f08569ca7'
 linked=[]
 for ident in[0,8]:
  entry=read(ml)['accepted'][str(ident)+'/Easy/mmc5'];receipt=R/entry['receipt'];z=read(receipt);d=R/z['proof'];m=read(d/'manifest.json')
  assert m['verified_through_2_2']and m['rom_sha256']==sha(cp.parent/'smb-crossover-mmc5.nes')
  linked.append(dict(identity=ident,mapper='mmc5',original_execution_revision='G',current_H_binary_identical=True,new_H_native_execution=False,receipt=str(receipt.relative_to(R)),receipt_sha256=sha(receipt),manifest=str((d/'manifest.json').relative_to(R)),manifest_sha256=sha(d/'manifest.json')))
 catalogue=J/'root-catalog-dl.json';assert not catalogue.exists();catalogue.write_text(json.dumps(catalog,indent=2)+'\n')
 report=dict(status='PASS_ROOT_FOUR_ACTUAL_H_MMC3_BASE_ROUTES_AND_TWO_LITERAL_MMC5_LINKS',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),source_files=458,generated_files=11,primary_artifacts=artifacts,source_G_review_sha256={'mario_luigi_link':'ed8e80955df544744f0b1cc704e2db34faceb22b4bc3b40e495e52b58718cfe9','megaman':'676f12af4a21437cfbfccc22c18db38b00265babe58ee0ab0d0cec7561d4c656'},accepted_actual_H=accepted,exact_ROM_links=linked,raw_catalog=dict(path=str(catalogue.relative_to(R)),sha256=sha(catalogue),files=len(catalog)),limits=['Only actual specified identities/mappers/Easy base routes. All original sourceG limitations retained.','Configured16px OAM scanline model decoded completely, not universal pixel/SFX or whole-source fidelity.','No complete every66 inventory, original1-1 variants/enemies/items or final audio/video inspection claim.','MMC5 literal full-ROM links are explicit prior G native executions, not new H native recordings.'],goal_complete=False)
 out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],sha256=sha(out),raw_files=len(catalog),actual_DMA=sum(z['hardware']['actual_DMA']for z in accepted))))
if __name__=='__main__':main()
