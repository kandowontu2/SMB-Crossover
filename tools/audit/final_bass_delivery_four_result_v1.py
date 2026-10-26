"""Compact actual four-delivery review; preserve native FALSEs. No emulator."""
from pathlib import Path
import argparse,csv,hashlib,json,shutil
from PIL import Image,ImageDraw
from final_item_abilities_remaining731_run_v1 import verify_manifest
from final_item_abilities_static_prepare_v2 import ROOT,D
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from final_bass_delivery_run_v1 import SHA
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')

def water_controls(b):
 rows=[]
 def setup():
  q=Arena(b,9);q.put(CrossoverBehaviorVersion=0,Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=176,ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0);q.set('InvOwnedLo',149,9);q.set('InvSelected',7,9);q.set('InvAmmo',112,151);return q
 for pulse in [70,120]:
  q=setup();samples=[];gone=None
  for t in range(650):
   q.put(InvFresh=64 if t in[0,pulse]else 0,SavedJoypadBits=64 if t<7 or pulse<=t<pulse+5 else 0)
   hidden=sum(q.get('SsHidden',i)!=0 for i in range(10)if q.get('RgShotType',i)==17);q.invoke('SpecialWeapons')
   if t in[0,69,70,74,82,119,120,124,182,649]:samples.append(dict(call=t+1,fixture_age=t+5,hidden_before=hidden,hidden_after=sum(q.get('SsHidden',i)!=0 for i in range(10)if q.get('RgShotType',i)==17),shots=sum(q.get('RgShotType',i)==17 for i in range(10)),expanding=q.get('SsWaterExpand'),radius=q.get('SsWaterRadius'),ammo=q.get('InvAmmo',151)))
   if t>0 and all(q.get('RgShotType',i)==0 for i in range(10))and gone is None:gone=t
  if pulse==70:assert gone is None and samples[2]['hidden_before']>0 and samples[2]['expanding']==0
  else:assert gone==182 and next(x for x in samples if x['fixture_age']==125)['expanding']==1
  assert q.get('InvAmmo',151)==96
  rows.append(dict(kind='complete-SpecialWeapons-native-Water-input-and-update',second_press_fixture_age=pulse+5,cleanup_after_first_press=gone,samples=samples,scope='Isolated actual CPU. Explicit ownership/stock/scene/InvFresh seeds here, not a native acquisition. Source actor hidden trajectory derives from genuine eight-ball creation.'))
 for hidden in [0,1]:
  q=setup()
  for t in range(121):q.put(InvFresh=64 if t==0 else 0,SavedJoypadBits=64 if t<7 else 0);q.invoke('SpecialWeapons')
  assert all(q.get('SsHidden',i)==0 for i in range(10)if q.get('RgShotType',i)==17)
  if hidden:
   slot=next(i for i in range(10)if q.get('RgShotType',i)==17);q.set('SsHidden',1,slot)
  q.invoke('SpecialWeapons::MegaAttack');assert q.get('SsWaterExpand')==(0 if hidden else 1)and q.get('InvAmmo',151)==96
  rows.append(dict(kind='complete-native-MegaAttack-Water',one_hidden=bool(hidden),expand=q.get('SsWaterExpand'),ammo=96))
 q=setup()
 for t in range(121):q.put(InvFresh=64 if t==0 else 0,SavedJoypadBits=64 if t<7 else 0);q.invoke('SpecialWeapons')
 q.put(InvFresh=0,SavedJoypadBits=64);q.invoke('SpecialWeapons');assert q.get('SsWaterExpand')==0
 q.put(InvFresh=64,SavedJoypadBits=64);q.invoke('SpecialWeapons');assert q.get('SsWaterExpand')==1 and q.get('InvAmmo',151)==96
 rows.append(dict(kind='complete-native-fresh-edge-gate',held_without_edge_refused=True,new_edge_expands=True,existing_shield_no_second_debit=True))
 return dict(passed=True,ROM_sha256=SHA,cases=len(rows),rows=rows,source='WaterCheck returns if any17 remains SsHidden; only a new InvFresh B edge after all are visible expands. Orbit radius180 clears. The prior age75 controller pulse is a legal refusal; shield persistence is intended until later valid expansion/selection/contact. Native hidden flags at that early edge were not logged, so CPU reproduction and actual images are stated separately.')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--seal-reviewed',action='store_true');a=p.parse_args()
 if a.seal_reviewed:
  verify_manifest(a.output/'pending-manifest.json');facts=json.loads((a.output/'facts.json').read_text());sheets=json.loads((a.output/'sheets.json').read_text());review=dict(passed=True,agent_visual_review=True,ROM_sha256=SHA,actual_wholeframe_placements=sum(len(x['placements'])for x in sheets),sheets=sheets,scope='Agent inspected every listed wholeframe. Four actual physical deliveries and source-specific observed uses, sparse staged scenes; no allframe/allpixel/sourceaudio/campaign/Hard/BALANCE claim. Source pointer and CHR checks are not a substitute for opaque pixel fidelity.',observations=['Mushroom reveals/rises above block; explicit post-rise downward contact and hosted transform are visible.','METAL/PHARAOH/WATER use distinct actual world icons and selected HUD/effects. Dense tiny HUD remains a readability limit.','No obvious new terrain displacement/green-block/whole-background-wrap anomaly in selected sparse scenes. Eight-sprite/weapon-body visibility limits remain open.','Native whole-profile outcome is exactly the field native_whole_profile_passed; earlier FALSEs are immutable.'])
  put(a.output/'agent-visual-review.json',review)
  cp=ROOT/'docs/qa/checkpoints/2026-10-26'/a.output.name;cp.mkdir(parents=True,exist_ok=False)
  for name in ['facts.json','agent-visual-review.json','sheets.json']:
   if name!='sheets.json':shutil.copy2(a.output/name,cp/name)
  if(a.output/'water-source-controls.json').exists():shutil.copy2(a.output/'water-source-controls.json',cp/'water-source-controls.json')
  for q in sheets:shutil.copy2(q['path'],cp/Path(q['path']).name)
  refs=[]
  for f in [a.ready/'proof.json',a.ready/'manifest.json',a.ready/'ROOT-grant.json',Path(facts['native_proof']),a.output/'pending-manifest.json',D/'current3b112-bass-delivery-preparation-v2/native/proof.json',D/'current3b112-bass-delivery-rise-ready-v4/native/proof.json']:
   refs.append(dict(path=str(f),bytes=f.stat().st_size,sha256=sha(f)))
  put(cp/'external-evidence.json',refs)
  (cp/'README.txt').write_text('One exact3b Easy physical-delivery profile. Actual outcome retained; no game/ROM/reference/settings payload. RawPPU/inputs/runtime/source/earlierFALSEs remain external, with hashes. Staged scene and post-rise actor alignment explicit. No Hard/BALANCE/allitems/fullgoal claim.\n',encoding='utf-8')
  assert sum(q.stat().st_size for q in cp.rglob('*')if q.is_file())<1000000
  put(cp/'manifest.json',dict(bindings=[dict(path=str(q.resolve()),bytes=q.stat().st_size,sha256=sha(q))for q in sorted(cp.iterdir())if q.is_file()]));assert sum(q.stat().st_size for q in cp.rglob('*')if q.is_file())<1000000
  files={q for q in a.output.iterdir()if q.is_file()};files.update(q for q in cp.iterdir()if q.is_file());files.add(Path(__file__));put(a.output/'manifest.json',dict(bindings=[dict(path=str(q.resolve()),bytes=q.stat().st_size,sha256=sha(q))for q in sorted(files,key=str)]));put(a.output/'proof.json',dict(passed=True,interpretation_only=True,native_whole_profile_passed=facts['native_whole_profile_passed'],original_native_FALSE_preserved=not facts['native_whole_profile_passed'],ROM_sha256=SHA,actual_numeric_mode=0,actual_physical_collections=facts['actual_physical_collections'],agent_visual_review=True,manifest_sha256=sha(a.output/'manifest.json'),checkpoint_manifest_sha256=sha(cp/'manifest.json'),checkpoint_bytes=sum(q.stat().st_size for q in cp.iterdir()if q.is_file()),native_worker_released=True,goal_complete=False));verify_manifest(a.output/'manifest.json');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),checkpoint_manifest_sha256=sha(cp/'manifest.json'),checkpoint_bytes=sum(q.stat().st_size for q in cp.iterdir()if q.is_file())),indent=2));return
 a.output.mkdir(parents=True,exist_ok=False);verify_manifest(a.ready/'manifest.json');ready=json.loads((a.ready/'proof.json').read_text());native=Path(ready['output']);n=json.loads((native/'proof.json').read_text());assert n['dependencies_unchanged']and n['ROM_sha256']==SHA
 events=[json.loads(s)for s in(native/'events.jsonl').read_text().splitlines()];frames=list(csv.DictReader((native/'actual-ppu-index.csv').open(newline='')));assert len(frames)*245760==(native/'actual-ppu.argb').stat().st_size;assert [int(x['ordinal'])for x in frames]==list(range(1,len(frames)+1));assert all(int(x['mode'])==0 for x in frames if int(x['updates'])>0)
 prepared=[x for x in events if x['kind']=='actual-reward-prepared'];completed=[x for x in events if x['kind']=='physical-reward-completed'];endpoints=[x for x in events if x['kind']=='actual-rise-endpoint'];collects=[x for x in events if x['kind']=='actual-physical-collect'];phaseAfter=[x for x in events if x['kind']=='delivery-phase'and x['phase']=='score-release'];caps=[x for x in events if x['kind']=='ppu-frame-captured']
 assert len(prepared)==len(collects)==len(phaseAfter)==4 and prepared[0]['data']['item']==0 and len({x['data']['item']for x in prepared})==4
 for x in endpoints:
  z=x['data'];assert z['entryCount']==z['acceptedReturns']==z['phaseWrites']==48 and z['yWrites']==16 and z['terminal']['y']==136 and z['terminal']['state']==128 and z['startY']==z['revealY']==152
 physical=[]
 for i,q in enumerate(prepared,1):
  item=q['data']['item'];after=next(x for x in phaseAfter if x['case']==i);assert after['data']['owned']==q['data']['before']|(1<<item)
  physical.append(dict(reward=i,item=item,untouched_PRNG=q['data']['prng'],actual_prepare=q,actual_collect=next(x for x in collects if x['case']==i),after_assertion_continuation=after,completed_full_reward=any(x['case']==i for x in completed),rise_endpoint=next((x for x in endpoints if x['case']==i),None),actual_spends=[x for x in events if x['case']==i and x['kind']=='actual-acquired-use-debit']))
 complete=starts=safe=pending=0;last=None
 for line in(native/'ability-dma-epochs.jsonl').open():
  q=json.loads(line)
  if q['kind']=='completed-DMA-before-render-enable':
   complete+=1;assert q['id']==complete and q['source']==q['hardware']and len(q['source'])==256 and len(q['writes'])==256 and not q['differences'];assert q['start']['oamaddr']==q['complete']['oamaddr']==0 and q['start']['mask']&24==q['complete']['mask']&24==0
   assert all(w['stamp']['oamaddr']==i and w['stamp']['mask']&24==0 and w['value']==q['source'][i]for i,w in enumerate(q['writes']));last=q
  elif q['kind']=='startFrame-hardware':
   starts+=1;pending+=bool(q.get('pending_dma_id'))
   if q.get('completed_dma_id')and not q.get('pending_dma_id'):assert q['hardware']==last['source']and q['completed_dma_id']==last['id']
  elif q['kind']=='actual-PPUMASK-write'and q['scoped']and q['enabling']:
   safe+=1;assert q['safe']and(241<=q['stamp']['scanline']<=260 or q['stamp']['scanline']==-1 and q['stamp']['cycle']<=274)
 raw=(native/'actual-ppu.argb').open('rb')
 def data(i):raw.seek((i-1)*245760);z=raw.read(245760);assert len(z)==245760;return z
 for q in caps:assert(native/(q['data']['name']+'.argb')).read_bytes()==data(q['wall'])
 selection=[]
 for i in range(1,5):
  for suffix in ['block','reveal','mature','collected','selected-HUD','effect','cleanup']:
   q=next((x for x in caps if x['data']['name']==f'reward-{i}-{suffix}'),None)
   if q:selection.append((q['wall'],f'reward{i} {suffix}'))
  reveal=next(x for x in caps if x['data']['name']==f'reward-{i}-reveal');selection.append((reveal['wall']+24,f'reward{i} rising sample'))
  if i==1:
   for suffix in ['transform-6','transform-30']:
    q=next(x for x in caps if x['data']['name']=='reward-1-'+suffix);selection.append((q['wall'],'mushroom '+suffix))
 base=next(x['update']for x in events if x['kind']=='delivery-phase'and x['case']==4 and x['phase']=='use')
 for age in[75,125,649]:
  q=next((x for x in frames if x['phase']=='use'and int(x['updates'])>=base+age),None)
  if q:selection.append((int(q['ordinal']),f'WATER use age~{age}'))
 sheets=[]
 for start in range(0,len(selection),12):
  im=Image.new('RGB',(1088,840),(32,32,32));draw=ImageDraw.Draw(im);placements=[]
  for k,(i,label)in enumerate(selection[start:start+12]):
   picture=Image.frombytes('RGBA',(256,240),data(i),'raw','BGRA').convert('RGB');x=k%4*272;y=k//4*280;im.paste(picture,(x,y+32));draw.text((x+2,y+1),f'PPU{frames[i-1]["ppu_frame"]} / ordinal{i}',fill='white');draw.text((x+2,y+15),label,fill='white');placements.append(dict(ordinal=i,label=label,raw_sha256=hashlib.sha256(data(i)).hexdigest(),actual_PPU=frames[i-1],x=x,y=y+32,width=256,height=240))
  f=a.output/f'whole-PPU-{start//12+1:02}.png';im.save(f);sheets.append(dict(path=str(f),sha256=sha(f),placements=placements))
 put(a.output/'sheets.json',sheets)
 failure=json.loads((native/'first-failure.json').read_text())if(native/'first-failure.json').exists()else None
 facts=dict(ROM_sha256=SHA,native_proof=str(native/'proof.json'),native_proof_sha256=sha(native/'proof.json'),native_whole_profile_passed=n['passed'],native_runner_exit=n['runner_exit'],actual_numeric_mode=0,actual_physical_collections=4,actual_reward_list=[q['data']['item']for q in prepared],full_reward_units_completed=len(completed),mushroom_transform_updates=completed[0]['data']['transformCalls'],physical_rows=physical,first_failure=failure,full_PPU_frames=len(frames),raw_bytes=(native/'actual-ppu.argb').stat().st_size,raw_sha256=sha(native/'actual-ppu.argb'),index_sha256=sha(native/'actual-ppu-index.csv'),complete256DMAs=complete,actual2004writes=complete*256,startFrames=starts,classified_pending=pending,safe_scoped_enables=safe,observed_last_update=int(frames[-1]['updates']),global_NMI_minSP_not_recoverable_without_terminal_summary=not n['passed'],native_worker_released=True,scope='A4actual physical deliveries with explicit visible/logical scene+post-rise contact placement; three private48return/48INC/16DEC/16pixel mature endpoints. NumericEasy0 only. Source-specific observed selection/use/debit; full unit result is literal native_whole_profile_passed. No BALANCE/Hard/completeitem/globalNMI/FPS/allpixel/audiofidelity claim.')
 put(a.output/'facts.json',facts)
 b=scoped_load(native/'candidate.nes');put(a.output/'water-source-controls.json',water_controls(b))
 files={Path(__file__),a.ready/'proof.json',a.ready/'manifest.json',native/'proof.json'};files.update(q for q in native.iterdir()if q.is_file());files.update(q for q in a.output.iterdir()if q.is_file());put(a.output/'pending-manifest.json',dict(bindings=[dict(path=str(q.resolve()),bytes=q.stat().st_size,sha256=sha(q))for q in sorted(files,key=str)]));verify_manifest(a.output/'pending-manifest.json');print(json.dumps(dict(derived=True,native_passed=n['passed'],facts_sha256=sha(a.output/'facts.json'),sheets=len(sheets),placements=len(selection),water_controls_sha256=sha(a.output/'water-source-controls.json')),indent=2))

if __name__=='__main__':main()
