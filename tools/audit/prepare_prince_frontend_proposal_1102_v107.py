"""Four source-field frontend proposal bytes, actual complete menu differentials."""
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
 return([bytes(z)for z in m.ram],bytes(m[:0x100]),bytes(native),bytes(m[0x15a:0x17b]),bytes(m[0x5fe0:0x8000]),m.rawtags[:],list(m.ppu_log))


def seed(base,slot):
 m=M.fresh(base);M.put(m,CrossoverMenuIndex=slot,CmActive=0);m[0x5ffe]=0
 F.invoke(m,'MenuResolveCharacter');F.invoke(m,'QueueSelection');return m


def main():
 old,manifest=C.image();raw=old['raw'];post=bytearray(raw);patches=[]
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
   assert expected==ncells and rawid==M.get(b,'SelectedCharacter') and view(a,prince)==view(b,prince)
   assert 63 not in ncells
   ra=F.invoke(a,'FmPending');rb=F.invoke(b,'FmPending');assert ra==rb and view(a,prince)==view(b,prince)
   prince=slot==29 and bool(a[0x5fe5]&16);assert prince==('PRINCE'in name)
   if prince:assert rawid==38 and ra['P']&1 and ra['A']==25
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
 assert len(rows)==95 and sum(r['new_Prince']for r in rows)==1 and foreign==188 and own==2,(len(rows),foreign,own)
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
 q=dict(passed=True,proposal_only=True,menu_admission_granted=False,ROM_written=False,installed=False,parent_memory_SHA256=manifest['expected_memory_only_SHA256'],expected_memory_only_SHA256=hashlib.sha256(post).hexdigest(),patches=patches,total_changed_bytes=sum(a!=z for a,z in zip(raw,post)),actual_named_states=len(rows),foreign_named_states=94,foreign_Start_A_pairs=foreign,Prince_Start_A_cases=own,actual_Select_confirm_cases=edges,all256_FmAlts_all32_Start_mask_cases=masks,full_FmPending_and_authentic_portrait_unchanged=True,marker_reader=marker_reader,frontend_descriptor=dict(slot=29,selector_field='FmAlts5FE5 bit16',raw_ID=38,existing_pending_name_index=25,authentic_static_portrait_route='FmPending retains C1/A25 and its exact existing source atlas/name. Readiness admits it and only its name marker becomesblank; authenticletters/portrait/allocation unchanged.',playable_readiness='76:BFF3 existing helper threshold25â†’26; valid existing other94states retain exact full menu output/AXYP/SP.',Start_identity='Current74B mask table dormantalt16 slotFFâ†’slot1D; keepFmAlts16 only on29 andclearallotherfamily/group bits normally.',component_manifest='post-return-manifest-v97.json',original_donor_SHA256='5f14d4d31cc588ddcdfb2b4d46eb7051b06d02655c9208037ef7ae137c4740e4'),rows=rows,scope='Separate four-byte same-footprint frontend measurement only. Actual95-state menu/Select/name/Start/A and simultaneous maskedSelect-confirm;94foreign states preserve native/fullSRAM/private/SMC/mapper/PPU/AXYP/SP. Existing16bit Prince identity survives ordinary Start. No menu admission, ROM emission or installation; root review/native first before adoption.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'post-return-manifest-v97.json',R/'tools/audit/prepare_mr_gimmick_family_1102_v18.py',R/'tools/reference/menu_input_1101_v3.inc',R/'src/full_roster_menu.s',R/'tools/audit/prepare_battletoads_menu_lease_v7.py']})
 (O/'frontend-proposal-v107.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['rows','bindings','frontend_descriptor']}))


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'frontend-negative-v107.json').write_text(json.dumps(dict(passed=False,proposal_only=True,exception=repr(error)),indent=2)+'\n');raise
