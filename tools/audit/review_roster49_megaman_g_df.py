"""Root independent frozen G Mega Man route, support and actual DMA review."""
from pathlib import Path
import collections,csv,datetime,hashlib,importlib.util,json,subprocess,sys,zipfile
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'agent49-megaman-bass-current-g-a';J=V/'root49-megaman-g-root-review-df'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=lambda p:list(csv.DictReader(Path(p).open(newline='')))
def main():
 assert not J.exists();J.mkdir()
 f=H/'megaman-freeze-aa.json';assert sha(f)=='f5d5415dc3d840232cbe2b9516d9c361e7eb2440adc3fe6dd054bd09c339788a';j=json.loads(f.read_text())
 def rehash(mapping):
  count=0
  for n,v in mapping.items():
   if isinstance(v,dict)and 'sha256'in v and 'bytes'in v:
    p=R/n;assert p.stat().st_size==v['bytes']and sha(p)==v['sha256'],n;count+=1
   else:count+=rehash(v)
  return count
 counts={n:rehash(j[n])for n in['proofs','retained_negative_runs','receipts','artifacts']};assert counts==dict(proofs=58,retained_negative_runs=423,receipts=160,artifacts=8),counts
 cp=R/j['checkpoint'];assert sha(cp)==j['checkpoint_sha256']=='feacfe9cf513d6c57dde8a4f2990e0bbd6c14ecda533d971747ad0011cee0fd0';c=json.loads(cp.read_text());S=Path(c['source_directory']);archive=R/c['source_archive']['path'];assert sha(archive)==j['source_archive']['sha256']
 expected=dict(c['source_hashes']);expected.update({'build/generated/'+n:h for n,h in c['generated11'].items()});assert len(expected)==469
 with zipfile.ZipFile(archive)as z:
  assert set(z.namelist())==set(expected)
  for n,h in expected.items():assert hashlib.sha256(z.read(n)).hexdigest()==h and sha(S/n)==h,n
 D=R/'build/roster-through-2-2/agent49-currentg-mm-fixed-v-1-v0-mmc3';U=R/'build/roster-through-2-2/agent49-currentg-mm-water-u-1-v0-mmc3'
 for tool,args in [('review_fixed.py',['--fixed',str(D.relative_to(R)),'--proposal',str(U.relative_to(R)),'--output',str(J/'fixed-review.json')]),('audit_mm_support.py',['--source',str(D.relative_to(R)),'--output',str(J/'support-review.json')])]:
  q=subprocess.run([sys.executable,str(H/tool)]+args,cwd=R,capture_output=True,text=True);(J/(tool+'.log')).write_text(q.stdout+q.stderr);assert q.returncode==0,q.stdout+q.stderr
 # Strengthen the specialist support oracle with actual compiled solid bits
 # and parsed A joined at the exact native movement-entry CPU cycle.
 sp=importlib.util.spec_from_file_location('G_MM_root_DF',V/'agent49g-samus-crouch-fix-proposal-b/image.py');mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);im=mod.Image(cp.parent/'smb-crossover-mmc3.nes');h=im.hook('MTileAttribute');attrs=im.raw[h['rom_offset']:h['rom_offset']+256]
 support=rows(D/'mm-fresh-ground-entry.csv');movement=rows(D/'movement-input.csv');bycycle={q['cycle']:q for q in movement};assert len(bycycle)==len(movement)
 static=platforms=0
 for q in support:
  m=bycycle[q['cycle']];assert q['held']==m['held']and q['previousAB']==m['previous']and int(m['ab'])&128 and not int(m['previous'])&128
  a,b=int(q['footL']),int(q['footR'])
  if a or b:assert int(q['y'])%16==0 and any(attrs[t]&1 for t in[a,b]);static+=1
  else:platforms+=1
 assert len(support)==194 and static==187 and platforms==7
 state=rows(D/'mm-source-state.csv');assert len(state)==32019 and all(q['char']=='1'and q['behavior']=='0'for q in state)
 for n in ['policy.lua','harness.lua','audit.lua']:
  s=(D/n).read_text();assert not any(w in s for w in['emu.write(','emu.setState(','emu.loadSavestate'])
 for n in ['observer-mm.lua','fixed-mm-observer.lua','observer-mm-support.lua','injury-observer.lua']:
  s=(H/n).read_text();assert not any(w in s for w in['emu.write(','emu.setState(','emu.loadSavestate'])
 for group in ['hooks-mmc3.json','injury-hooks-mmc3.json','pickup-hooks-mmc3.json']:
  q=H/group
  if q.exists():
   binding=json.loads(q.read_text())
   for h in binding.values():
    if isinstance(h,dict)and 'rom_offset'in h:assert list(im.raw[h['rom_offset']:h['rom_offset']+8])==h['bytes']and(h['rom_offset']-16)//8192==h['physical_bank']
 render=rows(D/'render.csv');dma={int(q['frame']):q for q in render if int(q['dmaCount'])};oam=rows(D/'oam.csv');assert len(oam)==sum(int(q['dmaCount'])for q in render)==21379
 assert [int(q['frame'])+1 for q in oam]==list(dma)
 overload=0;peak=0
 for q in oam:
  raw=bytes.fromhex(q['oamHex']);assert len(raw)==256;visible=hud=0;edge=collections.Counter()
  for i in range(0,256,4):
   top=raw[i]+1
   if top<240:
    visible+=1;hud+=top<32;lo,hi=max(32,top),min(240,top+16)
    if lo<hi:edge[lo]+=1;edge[hi]-=1
  value=maximum=0
  for y in range(32,240):value+=edge[y];maximum=max(maximum,value)
  assert(visible,hud,maximum)==(int(q['visible']),int(q['hudSprites']),int(q['maxSprites']))and int(dma[int(q['frame'])+1]['maxSprites'])==maximum
  peak=max(peak,maximum);overload+=maximum>8
 t=rows(D/'trace.csv');result=json.loads((D/'result.json').read_text());post=[q for q in t if int(q['frame'])>=result['stage_entries']['1-2']];assert len(post)==25 and post[0]['buttons']=='0'and all(q['buttons']=='1'for q in post[1:])and post[0]['x']=='40'and post[-1]['x']=='61'
 inputs=rows(D/'inputs.csv');actual=[q for q in inputs if int(q['frame'])>=result['stage_entries']['1-2']];assert len(actual)==24 and all(q['mask']=='1'for q in actual)
 hw=json.loads((H/'hardware-review-y2.json').read_text());assert sha(H/'hardware-review-y2.json')=='3d47f99ebb21b2e2e44dfb0b2f815a73ce99e3617b595894a21280a5b8067b18'and hw['actual_dma_snapshots']==len(oam)
 frozen=json.loads((J/'fixed-review.json').read_text());stomp=frozen['stomp'];assert stomp['illegal_guest_events']==stomp['resident_opcode_mismatches']==0 and stomp['allowed_mode_1_0_guest_events']==8
 report=dict(status='PASS_ROOT_FROZEN_G_EASY_MEGAMAN_MMC3_FULL_FIXED_REVIEW',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),freeze_sha256=sha(f),source_checkpoint_sha256=sha(cp),source_files=458,generated_files=11,catalogue_files=counts,result=result,core_inputs_trace_events_literal_U_V=True,fresh_ground_A_entries=dict(total=194,parsed_A_cycle_join=True,compiled_solid_static=static,live_native_platforms=platforms),hardware=dict(physical_render_rows=len(render),actual_DMA_snapshots=len(oam),peak_sprites=peak,over8_snapshots=overload,actual_APU_writes=sum(int(q['apuWrites'])for q in render),flagged_lagNmi=sum(int(q['lagNmi'])!=0 for q in render)),real_2_3=dict(native_rows=25,public_Right_polls=24,neutral_entry_row=True,x=[40,61]),ordinary_equipment_observations=frozen['streams']['mm-source-state.csv'],natural_pickups=frozen['streams']['natural-pickups.csv'],stomp=stomp,root_subreviews={n:sha(J/n)for n in['fixed-review.json','support-review.json']},working_main_revision='H',limits=j['limits']+['Original G proof remains G; working H is not automatically inferred.','All194 raw-A support entries independently join actual parsed A at the same CPU cycle; this certifies source entry support, not universal Flash bitmap or all collision parity.','Configured16px OAM model decoded completely; no new PPUCTRL bus trace or pixel/audio final-media claim.'],goal_complete=False)
 out=V/'root49-megaman-g-full-review-df.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],files=counts,source=458,generated=11,DMA=len(oam),sha256=sha(out))))
if __name__=='__main__':main()
