"""Build a private original-Shinobi actor/native-terrain/render graft component.

Reads the compact existing source proof and local donor. No whole archive,
cartridge, shared source, mapper allocation or selectable menu is modified.
"""
from pathlib import Path
import collections,hashlib,json,math,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import recover_shinobi_component_1101_v2 as S
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
from private_build_outputs_v1 import validate
from py65.disassembler import Disassembler
O=R/'build/shinobi-owning-graft-1101-v1';V=R/'build/shinobi-component-1101-v2'
BASE=R/'build/kirby-approach-owner-1101-v3/candidate.nes'
PIN='367266d2ec4e62fcefc15fffb3a05095a16060ad52f9d68348f213d94b31268c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def labels(p):return{name.lstrip('.'):int(a,16)for a,name in re.findall(r'^al ([0-9a-fA-F]+) (\S+)',p.read_text(),re.M)}
def save(p,q):p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')

def art(m):
    chrdata=(V/'source-body.chr').read_bytes();poses=json.loads((V/'pose-packets.json').read_text())['poses']
    patterns=[];pattern_ids={};packets={};parts=[];raster=hashlib.sha256()
    def pix(tile,x,y):return((chrdata[tile*16+y]>>(7-x))&1)|(((chrdata[tile*16+y+8]>>(7-x))&1)<<1)
    def image8(sprites):
      out={}
      for y,t,a,x in sprites:
       for yy in range(8):
        for xx in range(8):
         v=pix(t,7-xx if a&64 else xx,7-yy if a&128 else yy)
         if v and 0<=x+xx<256 and 0<=y+1+yy<240:out.setdefault((x+xx,y+1+yy),(a&3,v))
      return out
    def image16(rows):
      out={}
      for x,y,t,a in rows:
       p=patterns[t]
       for yy in range(16):
        for xx in range(8):
         py=15-yy if a&128 else yy;px=7-xx if a&64 else xx;tile=py//8*16
         v=((p[tile+py%8]>>(7-px))&1)|(((p[tile+py%8+8]>>(7-px))&1)<<1)
         if v and 0<=x+xx<256 and 0<=y+1+yy<240:out.setdefault((x+xx,y+1+yy),(a&3,v))
      return out
    for pose in poses:
      sprites=[pose['OAM'][i:i+4]for i in range(0,len(pose['OAM']),4)];used=set();rows=[]
      for i,s in enumerate(sprites):
       if i in used:continue
       used.add(i);low=None
       for j,z in enumerate(sprites):
        if j not in used and s[3]==z[3]and z[0]==s[0]+8 and s[2]==z[2]:low=z;used.add(j);break
       pair=[chrdata[s[1]*16:s[1]*16+16],chrdata[low[1]*16:low[1]*16+16]if low else bytes(16)]
       if s[2]&128:pair.reverse()
       key=b''.join(pair)
       if key not in pattern_ids:pattern_ids[key]=len(patterns);patterns.append(key)
       rows.append([s[3],s[0],pattern_ids[key],s[2]])
      before=image8(sprites);after=image16(rows)
      assert before==after,('Packed native priority/raster mismatch',pose['pose'],pose['frame'],pose['facing'],len(before),len(after))
      raster.update(repr(sorted(after.items())).encode())
      key=(pose['pose'],pose['frame'],pose['facing']);names=[]
      # Native header BPL requires <=124 bytes. Its allocator emits each
      # descriptor in reverse order; reverse our records to preserve source.
      for j in range(0,len(rows),31):
       chunk=rows[j:j+31];name=f'ShNativeP{key[0]:02X}_{key[1]}_{key[2]}_{j//31}';names.append(name)
       data=[len(chunk)*4]
       for x,y,t,a in reversed(chunk):data.extend([t*2+1,a,(y-224)&255,(x-128)&255])
       assert data[0]<128 and data[0]%4==0
       if key[2]==0:parts.append((name,data))
      packets[key]=names
    assert len(patterns)==96 and len(patterns)*32==3072
    source=['.segment "SHINOBI_META"'];_,_,arts=S.art_graph(m)
    for z in arts:
      timer=z['timer'];source.append(f'ShHeader_{z["header"]:04X}: .byte {z["count"]},{m.memory[z["header"]+1]}')
      source.append('.word '+(f'ShTimer_{timer:04X}'if timer else'0'))
    timers={z['timer']:z['count']for z in arts if z['timer']}
    for at,n in sorted(timers.items()):source.append(f'ShTimer_{at:04X}: .byte '+','.join(str(v)for v in m.memory[at:at+n]))
    bypose={z['pose']:z for z in arts};source+=['ShPosePointers:']
    source.extend('.word ShHeader_'+f'{bypose.get(i,arts[0])["header"]:04X}'for i in range(96))
    source+=['ShOriginalHeaderLo: .byte '+','.join(str(bypose.get(i,arts[0])['header']&255)for i in range(96))]
    source+=['ShNativePoseOrdinal: .byte '+','.join(str(S.POSES.index(i))if i in S.POSES else'255'for i in range(96))]
    base=[];k=0
    for z in arts:base.append(k);k+=z['count']
    assert k==26
    source+=['ShNativeFrameBase: .byte '+','.join(map(str,base)),'ShNativeFramePointers:']
    for z in arts:
      for frame in range(z['count']):
       names=packets[z['pose'],frame,0];assert 1<=len(names)<=2
       source.append('.word '+names[0]+','+(names[1]if len(names)>1 else'0'))
    for name,data in parts:source.append(name+': .byte '+','.join(map(str,data)))
    for pose in poses:
      if pose['facing']:continue
      left=next(z for z in poses if(z['pose'],z['frame'],z['facing'])==(pose['pose'],pose['frame'],4))
      a=[pose['OAM'][i:i+4]for i in range(0,len(pose['OAM']),4)];b=[left['OAM'][i:i+4]for i in range(0,len(left['OAM']),4)]
      assert{(255-x,y):v for(x,y),v in image8(a).items()}==image8(b),('Facing mirror raster',pose['pose'],pose['frame'])
    return '\n'.join(source)+'\n',b''.join(patterns),dict(original_source_pose_packets=len(poses),native_unique_8x16_pairs=96,CHR_bytes=3072,CHR_pages=3,native_descriptor_bytes=sum(len(z)for _,z in parts),native_packets=len(parts),source_priority_and_all_opaque_pixels_exact=True,original_both_facing_priority_rasters_verified=True,stored_facing_packets='Right only; left descriptor uses dx=-dx-8, attribute XOR40 in granted C880..C900 transient staging.',priority_model='Original OAM forward priority; native descriptor records reversed for actual descending emitter. Large packets split at31 sprites.',raster_sha256=raster.hexdigest(),original_timer_NULL_initial_header_low_preserved=True,unread_original_packet_pointers_omitted=True)

def geometry(m,lo=0xd1bc,hi=0xd2f3):
    d=Disassembler(m);out=[];a=lo
    while a<hi:
      n,text=d.instruction_at(a);mn,mode=m.disassemble[m.memory[a]]
      arg=(m.memory[a+1]+(m.memory[a+2]*256 if n==3 else 0))if n>1 else None
      if mode=='rel':text='j'+mn.lower()[1:]+' '+f'Sh_{(a+2+(arg if arg<128 else arg-256))&65535:04X}'
      elif mode in['abs','abx','aby','zpg','zpx','zpy','iny','inx','ind']:
       if mn in['JSR','JMP']:target='ShNativeQuery'if arg==0xd2f3 else f'Sh_{arg:04X}'
       elif mode=='iny'and arg==0x10:target='ShScratch+$00'
       elif arg<4:target=f'ShScratch+${arg:02x}'
       else:assert arg<0x800,(hex(a),text);target=f'ShState+${arg:04x}'
       text=re.sub(r'\$[0-9a-fA-F]+',target,text,count=1)
      out.append(f'Sh_{a:04X}: {text} ; original geometry${a:04X}');a+=n
    assert a==hi
    return '\n'.join(out)+'\n'

def kernel(m):
    code,external,ram,reads,words=S.graph(m);immediate,streams=S.scripts(m,code,words)
    # Only the original8x8 emitter and its unused whole-OAM hide leaf are
    # replaced by the native8x16 stage. Authentic animator/state remains.
    omitted=lambda a:0x83fc<=a<0x8623 or 0x805a<=a<0x806c
    required={a+i for a,z in code.items()if not omitted(a)for i in range(z['size'])}
    required|={a+i for a in words for i in range(2)}
    for lo,hi in[(0x834b,0x836f),(0xa368,0xa372),(0xa7d1,0xa7de),(0xc9a0,0xc9c0)]:required.update(range(lo,hi))
    sizes={0:2,1:2,2:3,3:1,4:1,5:2,6:1,7:2,8:2,9:2,10:1,11:1,12:2,13:2}
    for commands in streams.values():
      for a,op in commands:
       n=1 if op<0x80 or op>=0x8e or op in[0x8a,0x8b]else sizes[op&15]
       required.update(range(a,a+n))
    lines=[]
    for line in S.emit(m,code,dict(words),immediate,True).splitlines():
      if line.startswith('.segment'):lines.append('.segment "SHINOBI_KERNEL"');continue
      match=re.match(r'Sh_([0-9A-F]{4})[: ]',line)
      if match and int(match[1],16)not in required:continue
      line=line.replace('LDA $e620,Y','LDA ShPosePointers,Y').replace('LDA $e621,Y','LDA ShPosePointers+1,Y')
      if line.startswith('Sh_83EC:'):line='Sh_83EC: JSR ShReadInitialTimer ; original NULL timer semantics'
      if line.startswith('Sh_839C:'):line='Sh_839C: JSR ShReadNextTimer ; no native NMI scratch read'
      line=line.replace('JSR Sh_83FC','JSR ShNativeDrawObject')
      lines.append(line)
    out='\n'.join(lines)+'\n'+geometry(m)+geometry(m,0x8ec1,0x8f0a)+geometry(m,0xa154,0xa196)+geometry(m,0xe2dd,0xe2e4)+geometry(m,0xd98a,0xda1b)
    aliases={0xd213:'Sh_D213',0xd225:'Sh_D225',0xd25f:'Sh_D25F',0xd2a4:'Sh_D2A4',0xd1bc:'Sh_D1BC',0xfbdb:'ShNativeEvent',0xfb33:'ShViewportRight',0xfb3f:'ShViewportLeft',0x8ec1:'Sh_8EC1',0x8eed:'Sh_8EED',0xe2dd:'Sh_E2DD',0xd3ad:'ShNativeShotContact'}
    roots=[m.WordAt(a)for a in range(0x9b94,0x9bba,2)]
    head='.setcpu "6502"\n.macpack longbranch\nShState=$c000\nShScratch=$03\n'
    for a in sorted(external):head+=f'ShExternal_{a:04X}='+aliases.get(a,f'${a:04x}')+'\n'
    tail='''
.segment "SHINOBI_KERNEL"
ShViewportRight:
ShViewportLeft:
 lda #1
 sta ShState+$0054
 lda #0
 sta ShState+$0050
 rts
ShActorRoots: .word '''+','.join(f'Sh_{a:04X}'for a in roots)+'\n'
    return head,out,tail,dict(original_instructions=len(code),retained_instructions=sum(not omitted(a)for a in code),original_reachable_instruction_bytes=sum(z['size']for z in code.values()),pruned_bytes=sum(hi-lo for lo,hi in S.SPANS)-len(required),terrain_original_geometry_bytes=0xd2f3-0xd1bc,added_original_leaves=[[0x8ec1,0x8f0a],[0xa154,0xa196],[0xe2dd,0xe2e4]],source_Main_phase='Genuine9AA0 phase increment and9B60 A154 countdown retained at accepted update boundaries; native NPC contact adaption remains pending.',source_state_bytes=2048,foreground_scratch=[3,7],native_NMI_scratch=[0,3],replaced_renderer_range=[0x83fc,0x8623],callbacks={f'{a:04X}':aliases.get(a,'UNRESOLVED_NATIVE_SERVICE')for a in sorted(external)})

def main():
    assert sha(BASE)==PIN and sha(S.ROM)==S.EXPECTED
    b=qualified(BASE);m=S.original_memory(S.ROM.read_bytes());O.mkdir(exist_ok=True)
    head,core,tail,scope=kernel(m);meta,chrdata,visual=art(m)
    host=['R0','R1','R2','R3','R4','R5','R6','R7','Block_Buffer_1','Block_Buffer_2','ScreenLeft_X_Pos','ScreenLeft_PageLoc','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State','PlayerFacingDir','Player_X_Scroll','Player_X_Speed','Player_Y_Speed','PlayerSize','CrouchingFlag','Player_SprAttrib','SavedJoypadBits','OperMode','GameEngineSubroutine','GamePauseStatus','FrameCounter','SafecallA_SMC','FarcallJmpTarget_SMC','FarCallCommon','MetaspriteRenderLoop','ObjectOffset','Enemy_Flag','Enemy_State','Enemy_ID','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','RelativeEnemyPosition','GetEnemyOffscreenBits','GetEnemyBoundBox','SprObjectCollisionCore','BoundingBox_UL_Corner','HandleEnemyFBallCol']
    assert[address(b,n)for n in['R0','R1','R2','R3']]==list(range(3,7))
    for n in host:head+=n+'=$'+f'{address(b,n):04x}'+'\n'
    for n in['DisableScreenFlag','Mirror_PPUMASK','NmiDisable','FamilyMainCommit']:head+=n+'=$'+f'{address(b,n):04x}'+'\n'
    head+='Bank_MetaspriteRenderLoop=$'+f'{((location(b,"MetaspriteRenderLoop")-16)//8192)|128:02x}'+'\n'
    head+='Bank_GetEnemyBoundBox=$'+f'{((location(b,"GetEnemyBoundBox")-16)//8192)|128:02x}'+'\n'
    for name in['RelativeEnemyPosition','GetEnemyOffscreenBits','SprObjectCollisionCore','HandleEnemyFBallCol']:assert 0x8000<=address(b,name)<0xa000,(name,'fixed import moved')
    shapes=[];shape_ids=[]
    for pose in S.POSES:
      m.memory[0x300]=pose;m.memory[0x30b]=0;m.x=0;m.pc=0xd93d;m.sp=239;m.stPushWord(0x5ffd)
      for step in range(1000):
       if m.pc==0x5ffe:break
       m.step()
      else:raise AssertionError('Original bbox lookup bound')
      pointer=m.memory[0x10]+256*m.memory[0x11];count=m.memory[0x12]
      if count!=1:assert pose==0x57;shape_ids.append(255);continue
      row=bytes(m.memory[pointer:pointer+6])
      if row not in shapes:shapes.append(row)
      shape_ids.append(shapes.index(row))
    assert len(shapes)==4
    meta+='ShOriginalBoxId:.byte '+','.join(map(str,shape_ids))+'\nShOriginalBoxOffsets:.byte 0,6,12,18\nShOriginalBoxData:.byte '+','.join(str(v)for row in shapes for v in row)+'\n'
    at=location(b,'MTileAttribute');meta+='ShNativeTileAttributes: .byte '+','.join(map(str,b['raw'][at:at+256]))+'\nShMetadataEnd:\n'
    (O/'source-kernel.inc').write_text(core,encoding='utf-8');(O/'native-metadata.inc').write_text(meta,encoding='utf-8');(O/'native-art.chr').write_bytes(chrdata)
    services=['ShReject']*37
    for i,name in{0:'ShHostMovement',2:'ShHostDraw',15:'ShHostConstruct'}.items():services[i]=name
    vector='.segment "SHINOBI_KERNEL"\n.export ShCacheServices\nShCacheServices:\n'+''.join(' jmp '+name+'\n'for name in services)+'ShReject:clc\n rts\n'
    entry=head+vector+'.include "source-kernel.inc"\n'+tail+'.include "shinobi_native_boundary_1101_v1.inc"\n.include "shinobi_native_combat_1101_v1.inc"\nShKernelEnd:\n.include "native-metadata.inc"\n'
    (O/'component.s').write_text(entry,encoding='utf-8')
    cfg='MEMORY { K:start=$a000,size=$2000,type=ro,file="'+str(O/'kernel.bin').replace('\\','/')+'",fill=yes; M:start=$d000,size=$1000,type=ro,file="'+str(O/'metadata.bin').replace('\\','/')+'",fill=yes; } SEGMENTS { SHINOBI_KERNEL:load=K,type=ro; SHINOBI_META:load=M,type=ro; }\n'
    (O/'component.cfg').write_text(cfg);cc=R/'tools/Windows/cc65/bin';commands=[];relaxed=[]
    for iteration in range(8):
      for cmd in[[str(cc/'ca65.exe'),'-g','-I',str(O),'-I',str(R/'tools/reference'),str(O/'component.s'),'-o',str(O/'component.o')],[str(cc/'ld65.exe'),'-C',str(O/'component.cfg'),str(O/'component.o'),'-o',str(O/'unused.bin'),'-Ln',str(O/'component.lbl'),'--dbgfile',str(O/'component.dbg')]]:
       validate(cmd,O,cwd=R);p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);commands.append(dict(command=cmd,returncode=p.returncode,stderr=p.stderr));assert p.returncode==0,p.stderr
      lab=labels(O/'component.lbl');changes=[]
      for mat in re.finditer(r'(?m)^(Sh_[0-9A-F]{4}): j(eq|ne|cc|cs|mi|pl) (Sh_[0-9A-F]{4})(.*)$',core):
       delta=lab[mat[3]]-(lab[mat[1]]+2)
       if -128<=delta<=127:changes.append((mat[0],f'{mat[1]}: b{mat[2]} {mat[3]}{mat[4]}',mat[1],delta))
      if not changes:break
      for old,new,name,delta in changes:assert core.count(old)==1;core=core.replace(old,new);relaxed.append(dict(label=name,initial_displacement=delta,saved_bytes=3))
      (O/'source-kernel.inc').write_text(core,encoding='utf-8')
    else:raise AssertionError('Branch relaxation did not converge')
    codebytes=lab['ShKernelEnd']-0xa000;metabytes=lab['ShMetadataEnd']-0xd000
    chr_grant=R/'docs/qa/checkpoints/2026-11-01/shinobi-chr-resource-grant.json';ram_grant=R/'docs/qa/checkpoints/2026-11-01/shinobi-identity-ram-grant.json'
    cg=json.loads(chr_grant.read_text());rg=json.loads(ram_grant.read_text())
    assert cg['grant']and rg['grant']and cg['baseline_ROM_sha256']==rg['baseline_ROM_sha256']==PIN
    assert set(cg['physical_CHR_1KB_pages'])=={503,504,505,506,507,508,509,510,513,515,516,517}
    assert codebytes<=rg['code_page_capacity']['reserved_bytes']==7168 and metabytes<=rg['metadata_page_capacity']['reserved_bytes']==2048
    assert rg['native_contact_transient']['CPU_half_open']==[0xc200,0xc20a]
    cookie=bytes([0xa7,36,1])+hashlib.sha256((O/'kernel.bin').read_bytes()[:7168]+(O/'metadata.bin').read_bytes()[:2048]+chrdata).digest()[:13]
    (O/'shinobi-cookie.bin').write_bytes(cookie)
    resident_imports=['SelectedCharacter','CurrentBankC','ReloadCHRBank','NextBank_SMC','SafecallA_SMC','FarcallJmpTarget_SMC','SafereturnA_SMC','FarCallCommon','OperMode','FamilyMainCommit','DisableScreenFlag','Mirror_PPUMASK','NmiDisable','X5PublishChr','Mirror_PPUCTRL','HorizontalScroll','VerticalScroll','R0','R1','R2']
    resident='.setcpu "6502"\n.macpack longbranch\n'+''.join(n+'=$'+f'{address(b,n):04x}'+'\n'for n in resident_imports)
    resident+='Bank_X5PublishChr=$'+f'{((location(b,"X5PublishChr")-16)//8192)|128:02x}'+'\nShCacheServices=$a000\n.include "shinobi_resident_loader_1101_v1.inc"\n.include "shinobi_resident_dispatch_1101_v1.inc"\n'
    (O/'resident.s').write_text(resident,encoding='utf-8')
    resident_cfg='MEMORY { R:start=$4000,size=$1000,type=ro,file="'+str(O/'resident.bin').replace('\\','/')+'"; } SEGMENTS { SHINOBI_RESIDENT:load=R,type=ro; }\n'
    (O/'resident.cfg').write_text(resident_cfg,encoding='utf-8')
    for cmd in[[str(cc/'ca65.exe'),'-g','-I',str(O),'-I',str(R/'tools/reference'),str(O/'resident.s'),'-o',str(O/'resident.o')],[str(cc/'ld65.exe'),'-C',str(O/'resident.cfg'),str(O/'resident.o'),'-o',str(O/'unused.bin'),'-Ln',str(O/'resident.lbl'),'--dbgfile',str(O/'resident.dbg')]]:
      validate(cmd,O,cwd=R);p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);commands.append(dict(command=cmd,returncode=p.returncode,stderr=p.stderr));assert p.returncode==0,p.stderr
    resident_lab=labels(O/'resident.lbl')
    q=dict(passed=True,source_component=True,host_integrated=False,native_emulator=False,installed=False,source_donor_sha256=S.EXPECTED,host_input_sha256=PIN,private_code_bytes=codebytes,private_metadata_bytes=metabytes,original_body_native_art_bytes=len(chrdata),carrier_pages=math.ceil(codebytes/1024)+math.ceil(metabytes/1024),displayed_art_pages=3,total_proposed_CHR_pages=math.ceil(codebytes/1024)+math.ceil(metabytes/1024)+3,resource_granted=False,private_CHR_RAM_granted=True,full_owning_ROM_resources_granted=False,state_and_context_proposal=dict(state=[0xc000,0xc800],context=[0xc800,0xc811],descriptor_stage=[0xc880,0xc900],contact_transient=[0xc200,0xc20a],metadata=[0xd000,0xd000+metabytes],code=[0xa000,0xa000+codebytes]),source=scope,art=visual,near_branch_relaxations=relaxed,commands=commands,
      resident_loader_proposal=dict(bytes=resident_lab['ShResidentEnd']-0x4000,dispatch_bytes=resident_lab['ShDispatchEnd']-resident_lab['ShServiceVeneers'],total=len((O/'resident.bin').read_bytes()),fixture_assembly_origin=0x4000,ROM_lease_granted=False,code_pages=[506,507,508,509,510,513,515],metadata_pages=[516,517],art_pages=[503,504,505],full_headers=[[0xbfe0,0xbff0],[0xdfe0,0xdff0]],identity=36,service_rows=37,implemented_rows=[0,2,15],dispatch_and_main_hooks_pending=True),
      required_before_admission=['Native NPC shadow publication/melee/body injury/death/earned-item/UI/audio services remain unresolved. Shot contact is an isolated native-boundary component with separate CPU evidence; duplicate-owner contacts currently decline. No Select/menu unlock is authorized by this component.','Resident ROM funding and actual owning loader/dispatch integration remain required. CHR and requested RAM have separate root grants.','Native main hooks must suppress legacy Ryu motion/render/weapons and integrate platform/pipe/head-effect/death lifecycle without erasing current Kirby367266 composition.','Actual native renderer/PPU deadline, source palette publication, original weapon palette alias, Main/ISR stack, recursive contact protection and controller qualification remain separate.'],
      bindings={str(p.resolve()):sha(p)for p in[Path(__file__),R/'tools/reference/shinobi_native_boundary_1101_v1.inc',R/'tools/reference/shinobi_native_combat_1101_v1.inc',R/'tools/reference/shinobi_resident_loader_1101_v1.inc',R/'tools/reference/shinobi_resident_dispatch_1101_v1.inc',R/'tools/audit/recover_shinobi_component_1101_v2.py',V/'handoff.json',V/'assembly.json',V/'pose-packets.json',V/'source-body.chr',BASE,BASE.with_suffix('.dbg'),chr_grant,ram_grant,O/'component.s',O/'source-kernel.inc',O/'native-metadata.inc',O/'native-art.chr',O/'component.cfg',O/'kernel.bin',O/'metadata.bin',O/'component.lbl',O/'component.dbg',O/'shinobi-cookie.bin',O/'resident.s',O/'resident.cfg',O/'resident.bin',O/'resident.lbl',O/'resident.dbg']})
    save(O/'assembly.json',q);print(json.dumps({k:v for k,v in q.items()if k not in['bindings','commands','source','near_branch_relaxations']}))

if __name__=='__main__':main()
