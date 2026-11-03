"""Source-bound frontend admission proposal and exact resolver consumer, actual complete menu differentials."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_current_cold_1102_v98 as C
import audit_bub_menu_frontend_1102_v1 as F
from inventory_playable_menu_1101_v3 import menu_name
M,O=C.N,C.O;address,location=C.I.address,C.I.location


def view(m,normalize=False):
 native=bytearray(m[0x200:0x800])
 if normalize:
  at=address(m.bundle,'VRAM_Buffer1');end=M.get(m,'VRAM_Buffer1_Offset');i=0
  while i<end:
   hi,lo,length=m[at+i:at+i+3];n=length&63
   if ((hi<<8)|lo)==0x2328 and n==16 and m[at+i+4]==63:native[at+i+4-0x200]=36
   i+=3+(1 if length&64 else n)
 return([bytes(z)for z in m.ram],bytes(m[:0x100]),bytes(native),bytes(m[0x15a:0x17b]),bytes((0 if normalize and i==0x6002 else m[i])for i in range(0x5fe0,0x8000)),m.rawtags[:],list(m.ppu_log))


def seed(base,slot):
 m=M.fresh(base);M.put(m,CrossoverMenuIndex=slot,CmActive=0);m[0x5ffe]=0
 F.invoke(m,'MenuResolveCharacter');F.invoke(m,'QueueSelection');return m


def main():
 old,manifest=C.image();raw=old['raw'];post=bytearray(raw);patches=[]
 neg=O/'frontend-negative-v109.json';keep=O/'frontend-aliased-mask-negative-v109.json'
 if neg.exists()and 'Start mask leaked' in neg.read_text()and not keep.exists():keep.write_bytes(neg.read_bytes())
 at=16+76*8192+0x1ff3;assert raw[at:at+8]==bytes.fromhex('2079b99002c91960')
 post[at+6]=26;patches.append(dict(physical_PRG=76,CPU_half_open=[0xbff9,0xbffa],file_offset=at+6,old_hex='19',new_hex='1a',source_field='Existing8B playable-pending helper CMP immediate cutoff25â†’26. FmPending itself remains byte-identical for original atlas/name routing.'))
 start=location(old,'FmStartRetireFlags');body=raw[start:start+74];needle=bytes([10,31,9,26,255,23,30,28,25]);assert body.count(needle)==1
 index=body.index(needle)+4;assert raw[start+index]==255;post[start+index]=29
 patches.append(dict(physical_PRG=(start-16)//8192,CPU_half_open=[address(old,'FmStartRetireFlags')+index,address(old,'FmStartRetireFlags')+index+1],file_offset=start+index,old_hex='ff',new_hex='1d',source_field='Existing74B Start-retirement family-mask slot table: dormantalt16 row255â†’slot29. Keep onlyFmAlts&16 for slot29; other masks/instructions unchanged.'))
 # Bind the actual LDA absolute,Y/AND FmAlts/STA FmAlts consumer.
 operand=body.index(bytes.fromhex('2de55f'))-2;assert body[operand-1]==0xb9
 mask_cpu=int.from_bytes(body[operand:operand+2],'little');mask_at=start+mask_cpu-address(old,'FmStartRetireFlags')+4
 assert raw[mask_at]==0, (mask_at-start,hex(mask_cpu),body.hex())
 post[mask_at]=16;patches.append(dict(physical_PRG=(start-16)//8192,CPU_half_open=[mask_cpu+4,mask_cpu+5],file_offset=mask_at,old_hex='00',new_hex='10',source_field='Same74B dormant row4 actual altsMask00 to16; slotFF to29 alone clears Prince identity, preserved106negative.'))
 goperand=body.index(bytes.fromhex('2de85f'))-2;assert body[goperand-1]==0xb9
 group_cpu=int.from_bytes(body[goperand:goperand+2],'little');group_at=start+group_cpu-address(old,'FmStartRetireFlags')
 assert group_at==mask_at and raw[group_at:group_at+11]==bytes.fromhex('000000000020180780eaea')
 assert address(old,'FmCfHelperEnd')==address(old,'FmStartRetireFlags')+74 and body[-2:]==bytes.fromhex('eaea')
 post[start+goperand]=((group_cpu+1)&255)
 patches.append(dict(physical_PRG=(start-16)//8192,CPU_half_open=[address(old,'FmStartRetireFlags')+goperand,address(old,'FmStartRetireFlags')+goperand+1],file_offset=start+goperand,old_hex=bytes([group_cpu&255]).hex(),new_hex=bytes([(group_cpu+1)&255]).hex(),source_field='Existing74B overlapping masks: groups absolute,Y base moves+1; preserves all9group masks while zero overlap reduces5 to4.'))
 replacement=bytes.fromhex('0020180780');post[group_at+5:group_at+10]=replacement
 patches.append(dict(physical_PRG=(start-16)//8192,CPU_half_open=[group_cpu+5,group_cpu+10],file_offset=group_at+5,old_hex=raw[group_at+5:group_at+10].hex(),new_hex=replacement.hex(),source_field='Same74B group-tail data shifts right1, consumes one of two finalEA within declared74B function/FmCfHelperEnd. No executable or downstream address growth; allactualY0..8 group masks unchanged.'))
 fallback=body.index(bytes.fromhex('a004b9'));assert body.count(bytes.fromhex('a004b9'))==1
 post[start+fallback+1]=9;patches.append(dict(physical_PRG=(start-16)//8192,CPU_half_open=[address(old,'FmStartRetireFlags')+fallback+1,address(old,'FmStartRetireFlags')+fallback+2],file_offset=start+fallback+1,old_hex='04',new_hex='09',source_field='Existing fallback LDY4 becomesLDY9 because row4 nowPrince; both fallback masks9 arezero. Search still scans only nine declaredslots0..8.'))
 assert post[group_at+1+9]==0xea and post[mask_at-4+9]==0
 post[group_at+10]=0;patches.append(dict(physical_PRG=(start-16)//8192,CPU_half_open=[group_cpu+10,group_cpu+11],file_offset=group_at+10,old_hex='ea',new_hex='00',source_field='Final byte inside same74B function is fallbackGroups9=0; fallbackAlts9 overlaps existing zeroGroups4. Consumes the second terminalEA; all other addresses fixed.'))
 m=seed(old,29);M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0);F.invoke(m,'CrossoverMenuInput');name,cells=menu_name(m)
 assert name=='<3F>PRINCE PERSIA'and cells.count(63)==1 and cells[1]==63 and raw.count(bytes(cells))==1
 record=raw.index(bytes(cells));assert record==location(old,'FmNames')+25*16
 post[record+1]=36;patches.append(dict(physical_PRG=(record-16)//8192,CPU_half_open=[address(old,'FmNames')+401,address(old,'FmNames')+402],file_offset=record+1,old_hex='3f',new_hex='24',source_field='Actual FmQueueName index25 fixed16B row tile1: unplayable diamond/star63 toblank36; all15othername cells/portrait data remain.'))
 qa=location(old,'FmQueueName');code=raw[qa:qa+100];pairs=[i for i in range(len(code)-4)if code[i:i+2]==bytes([0xb1,address(old,'R2')])and code[i+2]==0x9d];assert len(pairs)==1
 copy_pc=address(old,'FmQueueName')+pairs[0];reads=[];writes=[];M.put(m,VRAM_Buffer1_Offset=0)
 def watch(c):
  if c.memory.rawtags[1]!=204:return
  if c.pc==copy_pc:
   ptr=c.memory[address(old,'R2')]|c.memory[address(old,'R3')]<<8;reads.append((ptr+c.y,c.memory[(ptr+c.y)&65535]))
  if c.pc==copy_pc+2:writes.append(c.a)
 F.invoke(m,'QueueSelection',watch=watch);assert reads[1]==(address(old,'FmNames')+401,63)and writes==cells
 marker_reader=dict(FmQueueName_Copy_PC=copy_pc,indirect_reads=reads,VRAM_name_cells=writes,marker_index=1,other15cells_unchanged=True)
 resolver=16+65*8192+0x1077;before=bytes.fromhex('08ade55f29100a0d0973c91dd076a9258d0260d06f');after=bytes.fromhex('08e01dd07fade55f2910c910a92569008d0260d06f')
 assert len(before)==len(after)==21 and raw[resolver:resolver+21]==before and raw[16+65*8192+0x10fb:16+65*8192+0x1100]==bytes.fromhex('28ad026060')
 post[resolver:resolver+21]=after;patches.append(dict(physical_PRG=65,CPU_half_open=[0xb077,0xb08c],file_offset=resolver,old_hex=before.hex(),new_hex=after.hex(),source_field='Existing21B family resolver. Actual X=menuindex except nativeMarioVariant0..7 ingress from CmHostResolveCharacter; CPX29 gates native slot29, sourceFmAlts16 setscarry thenLDA37/ADC0 chooses37/38. PHP and existingB0FB PLP/LDASelected/RTS preserve foreignAXYP.'))
 original_invoke=F.invoke;ingress=[]
 def traced_invoke(m,name,**kw):
  previous=kw.pop('watch',None)
  def trace(c):
   if c.pc==0xb077 and c.memory.rawtags[1]==193:
    slot=M.get(c.memory,'CrossoverMenuIndex');assert (c.x==29)==(slot==29),('Actual resolver slot29 X predicate',name,c.x,slot)
    ingress.append((slot,c.x,c.memory[0x5fe5]))
   if previous:previous(c)
  return original_invoke(m,name,watch=trace,**kw)
 F.invoke=traced_invoke
 new=dict(old,raw=bytes(post));rows=[];foreign=own=edges=0
 variants=sorted(n for n,s in old['syms'].items()if 'Variant'in n and '::'not in n and 0<=int(s['val'],0)<0x8000 and not n.startswith('.'))
 for slot in range(32):
  pair=[seed(b,slot)for b in [old,new]];seen=set()
  for cycle in range(32):
   a,b=pair;name,cells=menu_name(a);nname,ncells=menu_name(b);rawid=M.get(a,'SelectedCharacter')
   signature=(name,rawid,a[0x5fe5],a[0x5fe8],a[0x5ffe],tuple(M.get(a,n)for n in variants))
   if signature in seen:break
   seen.add(signature);prince=slot==29 and bool(a[0x5fe5]&16);expected=cells[:]
   if prince:expected[1]=36
   assert expected==ncells and (M.get(b,'SelectedCharacter')==38 if prince else rawid==M.get(b,'SelectedCharacter')) and view(a,prince)==view(b,prince)
   assert 63 not in ncells
   ra=F.invoke(a,'FmPending');rb=F.invoke(b,'FmPending');assert ra==rb and view(a,prince)==view(b,prince)
   prince=slot==29 and bool(a[0x5fe5]&16);assert prince==('PRINCE'in name)
   if prince:assert rawid==0 and M.get(b,'SelectedCharacter')==38 and ra['P']&1 and ra['A']==25
   for key in [16,128]:
    choices=[]
    for initial in pair:
     m=M.fork(initial);M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=key,SavedJoypad2Bits=0);z=F.invoke(m,'CrossoverMenuInput');choices.append((m,z))
    x,zx=choices[0];y,zy=choices[1]
    if prince:
     assert M.get(x,'CrossoverMenuState')==2 and M.get(y,'CrossoverMenuState')==0 and M.get(y,'SelectedCharacter')==38 and y[0x5fe5]==16 and not y[0x5fe8];own+=1
    else:assert zx==zy and view(x)==view(y),('Foreign menu mismatch',slot,cycle,name,key);foreign+=1
   # Actual masked Select+confirm targets the next profile, not the initial
   # displayed profile. Exâ†’Prince is an intended new confirmation boundary.
   for key in [48,160,176]:
    choices=[]
    for initial in pair:
     m=M.fork(initial);M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=key,SavedJoypad2Bits=0);z=F.invoke(m,'CrossoverMenuInput');choices.append((m,z))
    x,zx=choices[0];y,zy=choices[1]
    targets_prince=slot==29 and 'PRINCE'in menu_name(y)[0]
    if targets_prince:assert M.get(x,'CrossoverMenuState')==2 and M.get(y,'CrossoverMenuState')==0 and M.get(y,'SelectedCharacter')==38,(slot,cycle,name,key,[(M.get(m,'CrossoverMenuState'),M.get(m,'SelectedCharacter'),m[0x5fe5],menu_name(m))for m in [x,y]])
    else:assert zx==zy and view(x)==view(y),('Foreign simultaneous mismatch',slot,cycle,name,key)
    edges+=1
   rows.append(dict(slot=slot,cycle=cycle,name=name,raw=rawid,FmAlts=a[0x5fe5],FmGroups=a[0x5fe8],pending_name_index=ra['A'],pending_atlas_route=bool(ra['P']&1),new_Prince=prince))
   for m in pair:
    M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0);F.invoke(m,'CrossoverMenuInput')
  else:raise AssertionError(('Menu cycle bound',slot))
 assert len({(r['slot'],r['name'])for r in rows})==93
 assert len(rows)==94 and sum(r['new_Prince']for r in rows)==1 and foreign==186 and own==2,(len(rows),foreign,own,{slot:[r['name']for r in rows if r['slot']==slot]for slot in range(32)})
 masks=0
 for slot in range(32):
  templates=[seed(b,slot)for b in [old,new]]
  for alts in range(256):
   pair=[M.fork(m)for m in templates]
   for m in pair:M.put(m,FmAlts=alts,FmGroups=255)
   ra=F.invoke(pair[0],'FmStartRetireFlags',a=83,x=slot,y=109,p=0xe1);rb=F.invoke(pair[1],'FmStartRetireFlags',a=83,x=slot,y=109,p=0xe1)
   assert ra==rb
   if slot==29:
    assert pair[0][0x5fe5]==0 and pair[1][0x5fe5]==alts&16 and pair[1][0x5fe8]==0
    pair[1][0x5fe5]=0
   assert view(pair[0])==view(pair[1]),('Start mask leaked',slot,alts);masks+=1
 q=dict(passed=True,proposal_only=True,menu_admission_granted=False,ROM_written=False,installed=False,parent_memory_SHA256=manifest['expected_memory_only_SHA256'],expected_memory_only_SHA256=hashlib.sha256(post).hexdigest(),patches=patches,total_changed_bytes=sum(a!=z for a,z in zip(raw,post)),actual_named_states=len(rows),foreign_machine_states=93,unique_named_profiles=len({(r['slot'],r['name'])for r in rows}),foreign_unique_named_profiles=92,foreign_Start_A_pairs=foreign,Prince_Start_A_cases=own,actual_Select_confirm_cases=edges,all256_FmAlts_all32_Start_mask_cases=masks,full_FmPending_and_authentic_portrait_unchanged=True,marker_reader=marker_reader,actual_resolver_X_contract_checks=len(ingress),actual_resolver_nonindex_X=sorted({(slot,x)for slot,x,alts in ingress if x!=slot}),resolver_entry_X29_iff_menuindex29=True,frontend_descriptor=dict(slot=29,selector_field='FmAlts5FE5 bit16',raw_ID=38,existing_pending_name_index=25,authentic_static_portrait_route='FmPending retains C1/A25 and its exact existing source atlas/name. Readiness admits it and only its name marker becomesblank; authenticletters/portrait/allocation unchanged.',playable_readiness='76:BFF3 existing helper threshold25â†’26; valid existing other92namedprofiles retain exact full menu output/AXYP/SP.',Start_identity='Current74B mask table dormantalt16 slotFFâ†’slot1D; keepFmAlts16 only on29 andclearallotherfamily/group bits normally.',component_manifest='post-return-manifest-v97.json',original_donor_SHA256='5f14d4d31cc588ddcdfb2b4d46eb7051b06d02655c9208037ef7ae137c4740e4'),rows=rows,scope='Separate same-footprint frontend measurement: four scalar fields plus existing21B resolver. Actual94-machine-state/93-named-profile menu/Select/name/Start/A and simultaneous maskedSelect-confirm;93foreignmachine states/92namedprofiles preserve native/fullSRAM/private/SMC/mapper/PPU/AXYP/SP. Existing16bit Prince identity survives ordinary Start. No menu admission, ROM emission or installation; root review/native first before adoption.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'post-return-manifest-v97.json',R/'tools/audit/prepare_mr_gimmick_family_1102_v18.py',R/'tools/reference/menu_input_1101_v3.inc',R/'src/full_roster_menu.s',R/'tools/audit/prepare_battletoads_menu_lease_v7.py']})
 F.invoke=original_invoke
 (O/'frontend-proposal-v109.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['rows','bindings','frontend_descriptor']}))


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'frontend-negative-v109.json').write_text(json.dumps(dict(passed=False,proposal_only=True,exception=repr(error)),indent=2)+'\n');raise
