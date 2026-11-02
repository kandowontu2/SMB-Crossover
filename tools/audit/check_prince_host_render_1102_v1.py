"""Execute actual native CHR setters and metasprite emitter for Prince poses."""
from pathlib import Path
import hashlib,json,re,subprocess
import audit_prince_pool_1102_v1 as A
import check_hogan_current_bounded_v1 as M
from private_build_outputs_v1 import validate
R,O=A.R,A.O
ROM=R/'build/excitebike-pose-1101-v3/current4.nes'
SHA='cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8'


def main():
 assert A.sha(ROM)==SHA;b=A.scoped_load(ROM);seed=M.fresh(b)
 proof=json.loads((O/'contact-CPU.json').read_text());assert proof['passed']
 core=json.loads((O/'contact-recovery.json').read_text());start=int(core['compact_code_image_half_open'][1],16)
 # Original indirect RAM operands are solely the translated script read and
 # command-vector jump. Every static indexed state operand is conservatively
 # expanded through all256 possible indices, regardless of live player slot.
 touched=set();indirect=[]
 for at,v in core['instructions'].items():
  if v['mode']in ['inx','iny','ind']:indirect.append((at,v['mn'],v['mode'],v['value']))
  if v['mn']in ['JMP','JSR']or v['mode']not in ['abs','zpg','abx','aby','zpx','zpy']or v['value']>=2048:continue
  touched.update(range(v['value'],v['value']+(256 if v['mode']in ['abx','aby','zpx','zpy']else 1)))
 assert indirect and all((mn=='LDA'and mode=='iny'and atv==0x21)or(mn=='JMP'and mode=='ind'and atv==0x23)for at,mn,mode,atv in indirect)
 assert not touched&set(range(0x200,0x235))
 src=R/'tools/reference/prince_host_render_1102_v1.s'
 names=['R0','R1','R3','R4','CurrentOAMOffset','GuestOamRotationActive','RgOamRotation','NextBank_SMC','SafecallA_SMC','FarcallJmpTarget_SMC','SafereturnA_SMC','FarCallCommon','X5SetPhysicalChr','MetaspriteRenderLoop']
 pre='PpState=$c000\n'+''.join(f'{n}=${A.address(b,n):04x}\n'for n in names)
 pre+=''.join(f'Bank_{n}=${((A.location(b,n)-16)//8192)|128:02x}\n'for n in ['X5SetPhysicalChr','MetaspriteRenderLoop'])
 text=src.read_text();sites=[]
 def mark(m):
  n=f'PpRenderBranch{len(sites)}';sites.append((n,m[1],m[2]));return n+':\n '+m[0].strip()
 text=re.sub(r'(?m)^ j(eq|ne|cc|cs|mi|pl|vc|vs) (\w+)$',mark,text)
 text+='\nPhysicalLo:\n .byte '+','.join(f'${p&255:02x}'for p in A.POOL[:31])+'\nPhysicalHi:\n .byte '+','.join(str(p>>8)for p in A.POOL[:31])+'\n'
 text+=' .export '+','.join([*[n for n,_,_ in sites],*[t for _,_,t in sites]])+'\n'
 asm=O/'host-render.s';cfg=O/'host-render.cfg';cfg.write_text(f'MEMORY{{M:start=${start:04x},size=${0xbfe0-start:x},file=%O;}}SEGMENTS{{RENDER:load=M,type=ro;}}')
 cc=R/'tools/Windows/cc65/bin';relaxed=[]
 for _ in range(10):
  asm.write_text(pre+text)
  for cmd in [[cc/'ca65.exe',asm,'-o',O/'host-render.o'],[cc/'ld65.exe','-C',cfg,O/'host-render.o','-o',O/'host-render.bin','-Ln',O/'host-render.lbl']]:
   cmd=list(map(str,cmd));validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
  lab={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'host-render.lbl').read_text(),re.M)};changes=[]
  for label,cond,target in sites:
   old=f'{label}:\n j{cond} {target}'
   if old in text and -128<=lab[target]-lab[label]-2<=127:changes.append((old,f'{label}:\n b{cond} {target}',label))
  if not changes:break
  for old,new,label in changes:text=text.replace(old,new,1);relaxed.append(label)
 else:raise AssertionError('Renderer branch relaxation bound')
 blob=(O/'host-render.bin').read_bytes();art=json.loads((O/'source-art.json').read_text());meta=(O/'prince-pose-packets.bin').read_bytes()
 costs=[];cases=0;minimum=224;published=set();pending_mapper_cuts=[]
 smc=[A.address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','FarcallJmpTarget_SMC','SafereturnA_SMC']];smc.insert(3,A.address(b,'FarcallJmpTarget_SMC')+2)
 def draw(pose,x=128,y=112,prefix=4,rotation=0,interrupt=None):
  nonlocal minimum
  m=M.fork(seed);m.ram[3][start-0xa000:start-0xa000+len(blob)]=blob;m.ram[2][0x800:0x800+len(meta)]=meta
  m.raw_page(1,3);m.raw_page(2,2);M.put(m,CurrentBank=3,CurrentBankC=2,CurrentOAMOffset=prefix,GuestOamRotationActive=int(bool(rotation)),RgOamRotation=rotation,NmiDisable=1,ReloadCHRBank=0)
  m[0xc617]=pose['source_frame'];m[0xc615]=pose['source_facing'];m[0xc611]=128
  for n,v in [('PpRenderX',x&65535),('PpRenderY',(y+256)&65535)]:m[lab[n]]=v&255;m[lab[n]+1]=v>>8
  before=bytes(m[:0x8000]);state=bytes(m.ram[2]);maps=m.rawtags[:];old3=bytes(m.ram[3]);ppu=(m.ppu_addr,m.toggle,m.buffer,m.ppu_reads,bytes(m.vram));oldsmc=[m[a]for a in smc]
  c=M.NesMPU(memory=m,pc=lab['PpHostDraw']);c.a=85;c.x=0x5a;c.y=0xc7;c.p=0x71;c.sp=224;c.stPushWord(0x5aff);low=c.sp;calls=[];entries=[];cuts=set();injected=False
  for _ in range(12000):
   if c.pc==0x5b00:break
   low=min(low,c.sp)
   cut=(c.pc,c.sp,m.rawtags[1]);cuts.add(cut)
   if interrupt is not None and not injected and cut==interrupt[1]:
    injected=True;regs=(c.a,c.x,c.y,c.p,c.sp,c.pc);mapping=m.rawtags[:];private=[bytes(m.ram[k])for k in [2,3]];scratch=bytes(m[:256]);smcstate=bytes(m[0x15a:0x17b]);assert not c.p&4
    c.irq()if interrupt[0]=='IRQ'else c.nmi()
    for _ in range(200000):
     low=min(low,c.sp)
     if c.pc==regs[5]and c.sp==regs[4]:break
     assert m[c.pc]!=0,('Real ISR BRK',interrupt,hex(c.pc));c.step()
    else:raise AssertionError(('Real ISR return bound',interrupt))
    # Real NMI audio owns ZP0/1. The renderer borrows only foregroundR0..R7;
    # those and every private/SMC/mapper byte must survive the native ISR.
    r0=A.address(b,'R0')
    mapper_ok=mapping==m.rawtags
    if not mapper_ok:
     # FarCallCommon stores CurrentBank immediately before STA5115. A
     # native NMI at precisely that boundary restores the pending bank early;
     # the interrupted instruction then performs the exact same store. Its
     # full foreground continuation/OAM/return mapping is still compared.
     assert bytes(m[c.pc:c.pc+3])==bytes([0x8d,0x15,0x51])and m.rawtags[1]==M.get(m,'CurrentBank')and all(mapping[i]==m.rawtags[i]for i in [0,2,3]),('Unexpected ISR mapper difference',interrupt,mapping,m.rawtags)
     pending_mapper_cuts.append(dict(kind=interrupt[0],PC=c.pc,SP=c.sp,before=mapping[1],after=m.rawtags[1],next_instruction='STA $5115; identical pending CurrentBank value'))
     mapper_ok=True
    assert regs==(c.a,c.x,c.y,c.p,c.sp,c.pc)and mapper_ok and private==[bytes(m.ram[k])for k in [2,3]]and scratch[r0:r0+8]==bytes(m[r0:r0+8])and smcstate==bytes(m[0x15a:0x17b]),('Real ISR changed interrupted foreground',interrupt)
   for n in ['X5SetPhysicalChr','MetaspriteRenderLoop']:
    if c.pc==A.address(b,n)and m.rawtags[1]==((A.location(b,n)-16)//8192)|128:
     calls.append(n)
     if n=='MetaspriteRenderLoop':
      ptr=M.get(m,'R0')+256*M.get(m,'R1');entries.append([ptr,m[ptr],list(m[A.address(b,'R0'):A.address(b,'R0')+8]),m.rawtags[:]])
   assert m[c.pc]!=0,(hex(c.pc),m.rawtags);c.step()
  else:raise AssertionError('Prince renderer instruction bound')
  minimum=min(minimum,low);assert(c.a,c.x,c.y,c.p&254,c.sp)==(85,0x5a,0xc7,0x70,224)
  geometry={0x4bc,0x4c3,0x6f1,0x70f}
  assert all(m.ram[2][i]==v for i,v in enumerate(state)if i not in geometry and not 0x200<=i<0x235)and m.rawtags==maps and[m[a]for a in smc]==oldsmc
  if interrupt is None:assert ppu==(m.ppu_addr,m.toggle,m.buffer,m.ppu_reads,bytes(m.vram))
  else:assert ppu[-1]==bytes(m.vram),'ISR unexpectedly wrote native VRAM in busy/IRQ fixture'
  assert bytes(m.ram[3][:start-0xa000])==old3[:start-0xa000]and bytes(m.ram[3][start-0xa000+len(blob):])==old3[start-0xa000+len(blob):]
  parts=pose['parts_8x16'];n=len(parts);valid=prefix%4==0 and rotation%4==0 and prefix+4*n<256
  assert bool(c.p&1)==valid,(pose['source_frame'],prefix,rotation,c.p)
  if not valid:
   assert not calls and M.get(m,'CurrentOAMOffset')==prefix and bytes(m[0x200:0x300])==before[0x200:0x300];return
  pages=sorted({p['pattern_pair']//32 for p in parts});assert calls==['X5SetPhysicalChr']*len(pages)+['MetaspriteRenderLoop'],calls
  g=pose['source_projection_geometry'];assert m[0xc70f]==g['native_070F']and m[0xc6f1]==(128+g['native_06F1_minus_anchor_y'])&255 and m[0xc4bc]==(g['native_06F1_minus_anchor_y']-3)&255 and m[0xc4c3]==g['native_04C3']
  for window,page in enumerate(pages):
   physical=(M.get(m,'X5ChrMode',window)&3)*256+M.get(m,'CurrentCHRBank',window);assert physical==A.POOL[page];published.add(physical)
  for i,p in enumerate(parts):
   at=(prefix+rotation+4*i)&255;rec=bytes(m[0x200+at:0x204+at]);px=x+p['x'];py=y+p['y']-1
   if not(0<=px<256 and 0<=py<256):assert rec[0]==248,(pose['source_frame'],x,y,p,rec)
   else:
    tile=pages.index(p['pattern_pair']//32)*64+(p['pattern_pair']%32)*2
    assert rec==bytes([py,tile,p['attribute'],px]),(pose['source_frame'],pose['source_facing'],p,rec,[py,tile,p['attribute'],px],list(m[lab['PpNativePacket']:lab['PpNativePacket']+53]),entries,M.get(m,'CurrentOAMOffset'))
  assert M.get(m,'CurrentOAMOffset')==prefix+4*n
  # Exact allowed native effects are OAM/cursor and pending CHR ownership.
  allowed={A.address(b,'CurrentOAMOffset'),A.address(b,'X5WideChrActive'),A.address(b,'ReloadCHRBank')}
  allowed.update(range(A.address(b,'CurrentCHRBank'),A.address(b,'CurrentCHRBank')+12));allowed.update(range(A.address(b,'X5ChrMode'),A.address(b,'X5ChrMode')+12))
  diff=[a for a in [*range(0x100),*range(0x300,0x2000),*range(0x6000,0x8000)]if m[a]!=before[a]and a not in allowed]
  if interrupt is None:
   assert not diff,('Foreign application state changed',[(hex(a),before[a],m[a])for a in diff][:12])
   costs.append(c.processorCycles)
  if interrupt is not None:assert injected
  return m,c,cuts
 for pose in art['poses']:draw(pose);cases+=1
 edges=0
 for frame in [15,40,118,238]:
  for pose in [p for p in art['poses']if p['source_frame']==frame]:
   for x,y in [(-256,112),(-8,31),(0,0),(250,224),(256,240)]:
    for prefix,rotation in [(0,0),(196,4),(200,252),(204,0),(252,0),(25,0),(4,1)]:draw(pose,x,y,prefix,rotation);edges+=1
 widest=max(art['poses'],key=lambda p:(len({v['pattern_pair']//32 for v in p['parts_8x16']}),len(p['parts_8x16'])))
 m,c,cuts=draw(widest);ISRcases=0;by={}
 for kind in ['IRQ','lagNMI']:
  for cut in sorted(cuts):draw(widest,interrupt=(kind,cut));ISRcases+=1;by[kind]=by.get(kind,0)+1
 M.consume(m)
 pages=sorted({p['pattern_pair']//32 for p in widest['parts_8x16']})
 assert all(m.chr_latches[i]==A.POOL[page]for i,page in enumerate(pages))
 q=dict(passed=True,source_CPU_only=True,native_emulator=False,host_ROM_created=False,ROM_SHA256=SHA,component_bytes=len(blob),code_half_open=[start,start+len(blob)],remaining_before_BFE0=0xbfe0-start-len(blob),source_facing_poses=cases,edge_capacity_alignment_cases=edges,physical_body_pages=sorted(published),maximum_source_sprites=13,actual_native_setter_and_metasprite_emitter=True,full_source_pixels_order_attributes_and_geometry=True,host_AXYP_except_C_and_ZP_source_live_RAM2_SMC_mapper_PPU_preserved=True,source_OAM_scratch_half_open=[0xc200,0xc235],source_OAM_scratch_closure=dict(all_256_indices_conservative=True,source_static_operand_bytes=len(touched),only_indirect_operands=indirect,no_source_instruction_can_read_or_write_packet=True),CPU=[min(costs),max(costs)],minimum_SP=minimum,local_branches_shortened=len(relaxed),scope='Independent authenticated-caller leaf only; exact nativeCHR setter queues physical pages and genuine native metasprite emitter writes OAM. C200..C235 holds53B native packet in unused original OAM, within the conditional source-state grant; all source-live state is preserved. Renderer inputs are declared screen anchors; source/native coordinate export, owner/IRQ admission and native raster remain unqualified.',bindings={str(p.relative_to(R)):A.sha(p)for p in[Path(__file__),src,ROM,O/'contact-core.bin',O/'source-art.json',O/'prince-pose-packets.bin']})
 q['actual_IRQ_lagNMI_instruction_SP_cuts']=dict(total=ISRcases,by_kind=by,distinct_reached_instruction_SP_cuts=len(cuts),maximum_pages_pose=widest['source_frame'],full_owned_packet_code_state_and_foreground_context_preserved=True)
 q['actual_IRQ_lagNMI_instruction_SP_cuts']['native_pending_mapper_store_boundaries']=pending_mapper_cuts
 q['actual_completed_NMI_physical_CHR_publication']=True
 q['source_projection_geometry_lifetimes']=dict(original_writer_sites={'04BC':'bank4:B3C2 vertical frame offset','04C3':'bank4:B3E0 scaled vertical offset','070F':'bank4:B3EB width/horizontal projection witness','06F1':'bank4:B3F3 source actorY plus vertical offset plus3'},exact_fields_written_by_native_leaf=['04BC','04C3','070F','06F1'],all408_pose_values_match_original_renderer=True,source_actorY_independent_of_host_renderY=True,core_direct_readers={'04BC':['7:C86F'],'04C3':[],'070F':[],'06F1':[]},core_04BC_overwrites=['7:C7A7','7:C7B8'],next_frame_rule='The Up/climb scan resets04BC to0 at C7A7, then may set1 for the above-room case at C7B8, before its sole direct C86F read. Native drawing nevertheless exports the authentic renderer values for future source/host geometry consumers.',packet_lifetime='C200..C235 is written only during owned draw, remains mapped throughout genuine FarCallCommon/native emitter, and is disposable after the emitter returns; no recovered source direct/indexed/data-indirect operand can observe it. Full state is zeroed before live initialization, not after draw.')
 (O/'host-render-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
