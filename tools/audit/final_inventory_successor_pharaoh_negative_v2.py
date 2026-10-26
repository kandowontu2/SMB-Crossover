"""Compact preservation of isolated3b PHARAOH observer-omission firstFALSE; no replay."""
from pathlib import Path
import argparse,csv,hashlib,json,shutil
from PIL import Image,ImageDraw
from final_item_abilities_static_prepare_v2 import D,ROOT
from final_item_abilities_remaining731_run_v1 import verify_manifest
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 ready=D/'current3b112-bass-isolated-ready-v2';verify_manifest(ready/'manifest.json');native=ready/'profiles/bass-easy/native';nativeproof=json.loads((native/'proof.json').read_text());assert nativeproof['passed']is False and nativeproof['runner_exit']==1 and nativeproof['dependencies_unchanged'];assert not(ready/'profiles/bass-hard/native/launch.json').exists()
 failure=json.loads((native/'first-failure.json').read_text());assert failure['phase']==dict(phase='funded',name='pharaoh-face1')and failure['message']=='Actual source debit exhausts at least seeded stock to zero'
 es=[json.loads(s)for s in(native/'events.jsonl').read_text().splitlines()];case=[q for q in es if q['case']==9];spend=[q for q in case if q['kind']=='actual-source-spend'];assert len(spend)==1 and spend[0]['data']['before']==12 and spend[0]['data']['after']==8 and spend[0]['data']['cost']==4
 contact=next(q for q in case if q['kind']=='actual-source-contact');assert contact['wall']==2996 and contact['data']['ammo']==0 and any(q['type']==14 for q in contact['data']['shots']);assert not any(q['kind']=='actual-funded-refill-credit'for q in es)
 b=scoped_load(native/'candidate.nes');base=location(b,'SpecialWeapons::ReleaseBalloon');pc=address(b,'SpecialWeapons::ReleaseBalloon');code=b['raw'][base:location(b,'SpecialWeapons::ChargedReady')];store=bytes([0x9d,address(b,'InvAmmo')&255,address(b,'InvAmmo')>>8]);store_delta=code.index(store);assert pc+store_delta==0xaad2 and (base-16)//8192==60
 cpucases=json.loads((D/'current3b112-bass-gallery-ready-v1/assembled-cpu-controls.json').read_text());charged=[q for q in cpucases['rows']if q.get('kind')=='charged-release'];assert len(charged)==16 and all(q['after']==max(0,q['before']-8)for q in charged)
 frames=list(csv.DictReader((native/'actual-ppu-index.csv').open(newline='')));assert len(frames)==3119 and(native/'actual-ppu.argb').stat().st_size==len(frames)*245760
 # Independent raw fullhardware validation remains separate from observer failure.
 dma=starts=pending=safe=0;last=None
 for line in(native/'ability-dma-epochs.jsonl').open():
  q=json.loads(line)
  if q['kind']=='completed-DMA-before-render-enable':
   assert q['id']==dma+1 and len(q['source'])==len(q['hardware'])==256 and q['source']==q['hardware']and not q['differences']and len(q['writes'])==256
   assert q['start']['pc']==0xe005 and q['complete']['pc']==0xe008 and q['start']['oamaddr']==q['complete']['oamaddr']==0 and q['start']['mask']&24==q['complete']['mask']&24==0
   assert all(w['value']==q['source'][i]and w['stamp']['oamaddr']==i and w['stamp']['mask']&24==0 for i,w in enumerate(q['writes']));dma+=1;last=q
  elif q['kind']=='startFrame-hardware':
   starts+=1;pending+=bool(q.get('pending_dma_id'));assert len(q['hardware'])==256
   if q.get('completed_dma_id')and not q.get('pending_dma_id'):assert q['completed_dma_id']==last['id']and q['hardware']==last['source']
  elif q['kind']=='actual-PPUMASK-write'and q['scoped']and q['enabling']:
   safe+=1;s=q['stamp'];assert q['safe']and(241<=s['scanline']<=260 or s['scanline']==-1 and s['cycle']<=274)
 assert(dma,starts,pending,safe)==(2631,3119,1,2378)
 caps=[q for q in es if q['kind']=='ppu-frame-captured'];raw=(native/'actual-ppu.argb').open('rb')
 def data(n):raw.seek((n-1)*245760);z=raw.read(245760);assert len(z)==245760;return z
 lastcaps={q['data']['name']:q for q in caps}
 for name,q in lastcaps.items():assert(native/(name+'.argb')).read_bytes()==data(q['wall'])
 selected=sorted({2910,2916,2940,2975,2993,2994,2995,2996,2997,3000,3118,3119});placements=[]
 for n in selected:
  f=a.output/f'actual-{n:06}.png';Image.frombytes('RGBA',(256,240),data(n),'raw','BGRA').convert('RGB').save(f);placements.append(dict(path=str(f),sha256=sha(f),ordinal=n,actual_PPU=frames[n-1],raw_sha256=hashlib.sha256(data(n)).hexdigest()))
 im=Image.new('RGB',(1088,840),(32,32,32));draw=ImageDraw.Draw(im)
 for i,q in enumerate(placements):x=i%4*272;y=i//4*280;im.paste(Image.open(q['path']),(x,y+32));draw.text((x+2,y+4),f'Actual PPU {q["actual_PPU"]["ppu_frame"]}',fill='white')
 im.save(a.output/'pharaoh-actual-whole-PPU.png');put(a.output/'frame-selection.json',placements)
 attribution=dict(passed=False,attribution_passed=True,native_aggregate_remains_FALSE=True,ROM_sha256=nativeproof['ROM_sha256'],actual_numeric_mode=0,native_proof_sha256=sha(native/'proof.json'),failure=failure,actual_case9_events=case,observed_initial_debit=spend[0],actual_zero_contact=contact,actual_charged_release_spawn=[q for q in case if q['kind']=='actual-special-spawn'and q['data']['type']==14],direct_source_owner=dict(name='SpecialWeapons::ReleaseBalloon',physical_bank=60,entry=pc,bytes=list(code),store_pc=pc+store_delta,store_bytes=list(store),write_callback_nextPC=0xaad5,actual_index=148,policy='noninvincible release subtract8/clamp0 directly after InventoryIndex4; bypasses InventorySpend',actual_native_store_not_instrumented=True),bound_compiled_full_release_cases=charged,complete256DMAs=dma,data_writes=dma*256,startFrame_snapshots=starts,pending_starts=pending,safe_scoped_enables=safe,fullPPU_frames=len(frames),raw_bytes=len(frames)*245760,case_capture_events=len(caps),case_capture_names=len(lastcaps),all_original_casefiles_match_last_raw_event=True,source_credits_observed=0,Hard_unrun=True,native_worker_released=True,agent_visual_review=False,conclusion='New debit ledger observes only InventorySpend4 and misses genuine direct8 release; actual charged projectile/contact/stock0 source behavior agrees. Fixture observer omission, no game defect established.',limits=['OriginalFALSE remains; no success summaries/full16cases/Hard.','First8case component phases observed before PHARAOH stop; no KICK/FLAME/WATER new coverage.','Raw directAAD2 store at2994 was not hooked; actual zero witnessed at2996 contact plus source/compiled release control is not retagged as native direct-write proof.','No duplication/replay/fullcapture regeneration;12selected actualframes only.','B-only seeds, original failed packets unchanged; no acquisition/globaltiming/flicker/FPS/sourcefidelity/waveform/adoption claim.'])
 put(a.output/'attribution.json',attribution)
 files=set(f for f in native.iterdir()if f.is_file());files.update(f for f in a.output.iterdir()if f.is_file());files.update([Path(__file__),ready/'proof.json',ready/'manifest.json',D/'current3b112-bass-gallery-ready-v1/assembled-cpu-controls.json',D/'root-current-roster-composition-v1/source/src/special_weapons.s']);put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),bytes=f.stat().st_size,sha256=sha(f))for f in sorted(files,key=str)]));put(a.output/'proof.json',dict(passed=False,preservation_passed=True,ROM_sha256=nativeproof['ROM_sha256'],native_aggregate_remains_FALSE=True,attribution_sha256=sha(a.output/'attribution.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),native_worker_released=True,Hard_unrun=True,agent_visual_review=False));verify_manifest(a.output/'manifest.json');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),sheet=str(a.output/'pharaoh-actual-whole-PPU.png')),indent=2))
if __name__=='__main__':main()
