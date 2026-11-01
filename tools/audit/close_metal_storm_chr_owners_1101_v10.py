"""Close replaced Karnov owner domains from exact frozen source and code leaves."""
from pathlib import Path
import hashlib,json,re,sys,zipfile
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'tools/audit'),str(ROOT/'tools')]
from arthur_cache_host_controls_v1 import OverlayMemory
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU
OUT=ROOT/'build/metal-storm-chr-closure-1101-v10';V8=ROOT/'build/metal-storm-resource-host-1101-v8'
PACK=ROOT/'docs/qa/checkpoints/2026-11-01/karnov-hud-nightly-v9/source.zip';PACK_SHA='ae5e53e01d7796f6d5beab97668b4f02a270c5dc60027d1cda181b6dfe11f777'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
TARGETS=set([247,248,249,250]+list(range(494,503))+list(range(827,832)))
def main():
 cp=OUT/'current-consumer-inputs.json';cur=json.loads(cp.read_text());domains=json.loads((OUT/'source-domains.json').read_text());seams=json.loads((OUT/'publication-CPU-controls.json').read_text());assert domains['passed']and seams['passed'];assert sha(PACK)==PACK_SHA
 raw=(ROOT/'build/kirby-owner-main-1101-v2/candidate.nes').read_bytes();assert hashlib.sha256(raw).hexdigest()==cur['current_ROM_sha256'];owner=cur['current_owner_link'];assert owner['passed']and owner['all_segment_layouts_exact']and owner['base_ROM_sha256']=='99bf88c8d971f1305f965a21833703c7a11aafa6a24febd9f3bfb7c87ba4bbda'
 with zipfile.ZipFile(PACK)as z:
  manifest=json.loads(z.read('files.json'));used={}
  def read(name,binary=False):
   data=z.read(name);assert hashlib.sha256(data).hexdigest()==manifest[name]['sha256'];used[name]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest());return data if binary else data.decode()
  resident=read('host/kr-resident.inc');carrier=read('host/kr-loader-carrier-v6.inc');offsets=read('host/kr-loader-offsets-v6.inc');kernel_source=read('host/kr-kernel.s');render=read('host/kr-render.inc');hud=read('host/kr-hud-host-v9.inc');menu=read('host/kr-menu.inc');meta=read('host/kr-pose-meta.bin',True)
  regression=read('verification/regression-controls.json',True);reg=json.loads(regression);hud_controls=json.loads(read('verification/hud-controls.json',True));assert reg['passed']and hud_controls['passed']and hud_controls['ROM_sha256']==owner['base_ROM_sha256']
 assert 'cmp #12\n bne KrCopyRow'in resident and'lda #0\n sta R2'in resident and'inc R2'in resident
 assert 'KrCarrierMap:\n ldx R2\n lda #1\n cpx #8'in carrier and'adc #99'in carrier and'adc #143'in carrier
 assert 'and #31\n sta KrPoseIndex\n sta KrChrIndex'in render and'lda KrPosePage,x\n clc\n adc #<407'in render
 assert 'lda #<410\n ldx #>410\n ldy #3'in render
 assert len(meta)==1345 and set(meta[128:160])<=set(range(5)) and set(meta[128:160])==set(range(5))
 assert 'KrHudPhysicalLow=$ff'in hud and'KrHudPhysicalHigh=3'in hud
 assert 'lda #KrHudPhysicalLow\n sta InvHudPhysical\n lda #KrHudPhysicalHigh\n sta X5HudChrUpper'in hud
 assert 'lda #<408'in menu and'sta SmChrBank'in menu
 # The12 changed old instructions all reside in the already root-owned ROM29
 # Karnov lease. Two other old PCs are displaced within its authenticated RAM3
 # image. None is an unexplained change to another family or generic publisher.
 resident_interval=hud_controls['owners']['allowed_intervals'][0];assert resident_interval==[243264,245696]
 changed=cur['changed_inherited_writers'];assert len(changed)==14
 for r in changed:
  if r['segment']=='CHAR_SELECT':assert resident_interval[0]<=r['file_offset']<resident_interval[1]
  else:assert r['segment']=='KR_KERNEL'and r['file_offset']<8192
 assert sum(r['segment']=='CHAR_SELECT'for r in changed)==12
 # Execute the exact current native carrier-map leaf, located by its full
 # source-verified instruction body inside that sole owned lease.
 pattern=bytes.fromhex('a605a901e0089002a9038d30518a90026963698f8d2b5160')
 start=raw.find(pattern,*resident_interval);assert start>=0 and raw.find(pattern,start+1,resident_interval[1])<0
 pc=0xa000+((start-16)&8191);bank=(start-16)//8192
 w=json.loads((V8/'native-witness.json').read_text());syms=dict(w['syms']);syms.update(cur['syms']);b=dict(raw=raw,syms=syms,segs=cur['segments']);rows=[]
 for row in range(12):
  m=OverlayMemory(b);m.raw_page(1,128|bank);m.raw_page(2,215);m[address(b,'CurrentBank')]=128|bank;m[address(b,'CurrentBankC')]=215;m[5]=row;c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=85,7,91,0x71,224;c.stPushWord(0x5ffe)
  for _ in range(100):
   if c.pc==0x5fff:break
   c.step()
  else:raise AssertionError('Carrier map CPU bound')
  page=m.chr_latches[11];assert page==(399+row if row<8 else 1011+row)and page not in TARGETS
  rows.append(dict(row=row,physical_page=page))
 # Verify actual renderer and HUD constants in their current emitted images.
 kernel_path=next(Path(p)for p in cur['readonly_image_inputs']if Path(p).name=='kr-kernel.bin');kernel=kernel_path.read_bytes();assert hashlib.sha256(kernel).hexdigest()==cur['readonly_image_inputs'][str(kernel_path)]['sha256']
 bodypattern=bytes.fromhex('ae24c8bd80d0186997a201a000');at=kernel.find(bodypattern);assert at>=0
 shotpattern=bytes.fromhex('a99aa201a003');shotat=kernel.find(shotpattern,at);assert shotat>=at and shotat-at<64
 low=address(b,'InvHudPhysical');upper=address(b,'X5HudChrUpper');wide=address(b,'X5WideChrActive');reload=address(b,'ReloadCHRBank');active=address(b,'InvHudActive')
 def sta(a):return bytes([141,a&255,a>>8])
 hudpattern=bytes([169,255])+sta(low)+bytes([169,3])+sta(upper)+bytes([169,1])+sta(wide)+sta(reload)+bytes([169,233])+sta(active)
 hudlo,hudhi=1048592+1019*1024,1048592+1023*1024;hudat=raw.find(hudpattern,hudlo,hudhi);assert hudat>=hudlo
 live_domains=dict(cold_actor=[r['physical_page']for r in rows],body=sorted({407+x for x in meta[128:160]}),shot=[410],cold_body=[408],HUD=[1023])
 assert not TARGETS.intersection(p for pages in live_domains.values()for p in pages)
 # All original831 unchanged instructions retain their previous explicit
 # zero/array/indirect/graphics-source ABI classification. The14 changed PCs
 # are replaced by the exact bound selected-owner source domains above, not
 # relabeled as an absence of stores at their historical byte positions.
 evidence=dict(passed=True,current_ROM_sha256=cur['current_ROM_sha256'],source_packet=str(PACK.resolve()),source_packet_sha256=PACK_SHA,source_members_read=used,existing_global_writers_unchanged=831,replaced_owner_records=14,ROM29_replaced_positions=[r['file_offset']for r in changed if r['segment']=='CHAR_SELECT'],RAM3_displaced_positions=[r['file_offset']for r in changed if r['segment']=='KR_KERNEL'],resident_owned_interval=resident_interval,current_native_carrier_map=dict(PC=pc,file_offset=start,hex=pattern.hex(),all12rows=rows),current_actor_render_leaf=dict(offset=at,hex=bodypattern.hex(),pose_page_values=sorted(set(meta[128:160]))),current_shot_render_leaf=dict(offset=shotat,hex=shotpattern.hex()),current_HUD_lease_leaf=dict(carrier_file_offset=hudat,hex=hudpattern.hex()),actual_domain_pages=live_domains,other_owner_bytes_preserved_by_current_Kirby_owner=owner['all_other_linked_objects_read_only'],scope='Exact frozen current99 Karnov semantic source + actual c864 leaf bytes/finite ranges replace14 old instruction positions. Existing full loader/HUD Main receipts are bound from packet; no new emulator/admission/resource claim.')
 (OUT/'replaced-owner-controls.json').write_text(json.dumps(evidence,indent=2)+'\n')
 result=dict(passed=True,consumer_closure_passed=True,resource_granted=False,native=False,installed=False,current_ROM_sha256=cur['current_ROM_sha256'],proposed_Metal_pages=[247,248,249,250,494,495,496,497,498,499,500,827,828,829,830,831],proposed_Tank_pages=[501,502],still_owned_gap_page511=True,all_existing_legal_consumers_disjoint=True,proof_parts=dict(current_source_tables=25,typed_publisher_callers=43,inherited_writers_exact=831,replaced_Karnov_owner_records=14,typed_instruction_cuts=seams['actual_typed_setter_instruction_cuts'],native_Mario_clear_restore_instruction_cuts=seams['actual_native_Mario_menu_clear_restore_cuts'],actual_NMI_returns=seams['real_NMI_returns'],IRQ='Existing source-resolved IRQ low0 yields0/256/512/768 for any upper latch; no candidate.'),conditions=['Root must explicitly grant these physical resources before any integrated scatter write','Only the named source-valid menu/actor/table/index and established constructor/stack ABI domains are covered; arbitrary corruptRAM is not authorized','Inherited zero/indirect/array classification stays scoped to original frozen source and current identical instructions; new owners need a new audit','Any future CHR publisher/loader/menu or source-table change must invalidate/recheck this result','Metal art still requires intentional selected-player P0 adaptation and disclosed star/flower phase0 exception','Actual Metal/Tank loader/Main/ISR/controller/native admission remains separate'],scope='Current-c864 source/compiled-consumer and instruction-publication closure for proposed pages only. No allocation from blank bytes, resource grant, native emulator/hardware/timing/full-stage or selectable-character admission.',bindings={str(p.resolve()):sha(p)for p in[Path(__file__),cp,OUT/'source-domains.json',OUT/'publication-CPU-controls.json',OUT/'replaced-owner-controls.json',PACK]})
 (OUT/'consumer-closure.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in['bindings','conditions']}))
if __name__=='__main__':main()
