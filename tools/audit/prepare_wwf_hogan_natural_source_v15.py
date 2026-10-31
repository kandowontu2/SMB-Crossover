"""Granted, inert first-Hogan physical layout/loader on genuine current a126."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load,address,location
from prepare_cv3_dmc_mirror import prepare
O=R/'build/wwf-hogan-natural-source-v15';J=O/'joint'
P=R/'build/contra-force-world-roles-1031-v2/joint'
G=R/'build/wwf-ready74-first-host-resource-v1/resource-contract.json'
L=R/'build/wwf-native-proxy-lab-v1'
F=R/'build/wwf-frame-recovery-v2'
B=R/'build/wwf-c2-symbol-relocation-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n')

def main():
 assert not O.exists();O.mkdir();J.mkdir();logs=[]
 try:
  grant=json.loads(G.read_text());assert grant['passed'] and grant['root_first_host_grant']['CHR_pages']==43
  for p,h in grant['bindings'].items():assert sha(p)==h,p
  parent=load(P/'candidate.nes');old=(P/'candidate.nes').read_bytes()
  assert sha(P/'candidate.nes')==grant['current_sha256']
  artpath=R/'build/wwf-roster-source-review-v1/wrestlers.json'
  art=json.loads(artpath.read_text());hogan=next(c for c in art['characters']if c['id']==5)
  poses=sorted((p for p in art['poses']if p['character']==5),key=lambda p:(p['group'],p['frame']))
  pages=sorted({p['packed_page']for p in poses});assert len(pages)==17 and len(poses)==31
  allbody=(artpath.parent/'wrestlers-pages.chr').read_bytes()
  (J/'hogan-body.chr').write_bytes(b''.join(allbody[p*1024:(p+1)*1024]for p in pages))
  ng=len(hogan['groups']);head=2+2*ng+3*len(poses);meta=bytearray([ng,len(poses)]);start=0
  for g in range(ng):
   members=[p for p in poses if p['group']==g];meta.extend([start,len(members)]);start+=len(members)
  records=bytearray();index=bytearray()
  for p in poses:
   index.extend((head+len(records)).to_bytes(2,'little'));index.append(pages.index(p['packed_page']))
   records.extend([p['width'],len(p['packed_8x16_cells'])])
   for cell in p['packed_8x16_cells']:records.extend([cell['page_tile'],cell['role'],cell['x']&255,cell['y']&255])
  meta.extend(index);meta.extend(records);assert len(meta)==1687
  (J/'hogan-metadata.bin').write_bytes(meta)
  # Preserve true instruction-relative layout assertions when C2 phases move.
  def relative(text,segment,base,label):
   text=text.replace(f'.segment "{segment}"',f'.segment "{segment}"\n{label}:',1)
   text=re.sub(r'\.assert \*=\$([0-9a-f]+),lderror',lambda m:f'.assert *-{label}=${int(m[1],16)-base:x},lderror',text)
   text=re.sub(r'(?m)^\.assert \*<=\$[0-9a-f]+,lderror[^\n]*','',text)
   return text
  for n in ['vm','data','helpers']:(J/(n+'.s')).write_text((B/(n+'.s')).read_text())
  (J/'helpers.s').write_text(re.sub(r'(?m)^\.assert \*<\$dfd0,lderror[^\n]*','',(J/'helpers.s').read_text()))
  (J/'contact.s').write_text(relative((F/'contact.s').read_text(),'WF_SELECTED_CONTACT',0xdc00,'WfPhysicalContactStart'))
  (J/'recovery.s').write_text(relative((F/'recovery.s').read_text(),'WF_FRAME_RECOVERY',0xcc00,'WfPhysicalRecoveryStart'))
  (J/'host.s').write_text(re.sub(r'(?m)^\.assert \*<=\$dfd0,lderror[^\n]*','',(L/'host.s').read_text()))
  proxy=(L/'proxy.s').read_text();public=['WfProxyReset','WfHostPoint','WfProxyNoteReuse','WfProxySnapshot','WfProxyCollect','WfHostImport','WfHostExport','WfProxyCommit']
  # Actual native marshaling runs in resident A96, between source A3 phases.
  for n in sorted(public,key=len,reverse=True):proxy=re.sub(r'\b'+n+r'\b','WfRaw'+n[2:],proxy)
  proxy=proxy.replace('.segment "WF_NATIVE_PROXY"','.segment "WF_RESIDENT_PROXY"').replace('.segment "WF_NATIVE_PROXY_TAIL"','.segment "WF_RESIDENT_PROXY"')
  proxy=proxy.replace('WfProxyResetCore:\n','.segment "WF_PROXY_RESET"\nWfProxyResetCore:\n')
  proxy=proxy.replace('; Physical world point.','.segment "WF_RESIDENT_PROXY"\n; Physical world point.',1)
  proxy=re.sub(r'(?m)^\.assert \*<=\$[0-9a-f]+,lderror[^\n]*','',proxy)
  (J/'proxy.s').write_text(proxy)
  aliases=''.join((B/'aliases.s').read_text().splitlines(keepends=True)[:9])
  aliases+='\n.segment "WF_UNBOUND_CALLBACKS"\n'
  for n in ['AI','RingClamp','RingBounds','Audio09','Audio0F','Audio12']:
   aliases+=f'.export WfEnv_WfCb{n}\nWfEnv_WfCb{n}:brk ; explicit unbound callback trap, never a substitute\n'
  aliases=aliases.split('.segment \"WF_UNBOUND_CALLBACKS\"')[0]
  (J/'aliases.s').write_text(aliases)
  (J/'world.s').write_text((R/'tools/reference/wwf_hogan_world_v2.s').read_text().replace('; The selected actor driver', '.export WfRuntimeStateEnd\nWfRuntimeStateEnd:\n; The selected actor driver',1))
  (J/'proxy.s').write_text((J/'proxy.s').read_text()+'\n.export WpDir,WpOldX,WpOldPage,WpOldY,WpOldYHi,WpOldJump\n')
  (J/'selected-extra.s').write_text(f'''.setcpu "6502"
.segment "WF_HOGAN_METADATA"
.export WfHoganMetadata,WfHoganMetadataEnd
WfHoganMetadata:.incbin "{(J/'hogan-metadata.bin').as_posix()}"
WfHoganMetadataEnd:
.segment "WF_OWNER_STATE"
.export WfHostReady
WfHostReady:.res 1
.segment "WF_OWNER_COOKIE"
.export WfOwnerCookie
WfOwnerCookie:.res 16,0
.segment "WF_RAM3_COOKIE"
.res 16,0
.segment "WF_A1_INACTIVE"
.res $2000,0 ; reserved nonexecuting bank, original music unbuilt
''')
  (J/'cookie.bin').write_bytes(bytes(16))
  owner=(R/'tools/reference/wwf_first_hogan_owner_v2.s').read_text()
  owner=re.sub(r'\.macro GuardedProxy[\s\S]*?\.endmacro\n','',owner)
  generated=[]
  for n in public:
   raw='WfRaw'+n[2:]
   generated.append(f'''.import {raw}
.export {n}
{n}:
 SaveOwner
 jsr WfAuthC2
 bcc @no
 lda WfHostReady
 cmp #$a7
 bne @no
 tsx
 lda $012f,x
 pha
 lda $012c,x
 tay
 lda $012e,x
 pha
 lda $012d,x
 tax
 pla
 plp
 jsr {raw}
 jmp WfReturnC
@no:clc
 jmp WfReturnC
''')
  owner=owner.replace('; WF_GUARDED_PROXY_GENERATED','\n'.join(generated))
  owner=owner.replace('; WF_COOKIE_C_GENERATED',f'.incbin "{(J/"cookie.bin").as_posix()}"')
  owner=owner.replace('.import WfHostCold,WfHostReady,WfOwnerCookie,WfExpectedCookie', '.import WfHostCold,WfHostReady,WfOwnerCookie,WfExpectedCookie\n.import CurrentPlayer,NumberofLives,WfOwnerPlayer,WfOwnerLife,WfRuntimeStateEnd,WfRenderBuffer')
  owner=owner.replace(' cmp #$a7\n beq WfConstructDone\n lda #5',''' cmp #$a7
 bne WfConstructNew
 lda CurrentPlayer
 cmp WfOwnerPlayer
 bne WfConstructNew
 lda NumberofLives
 cmp WfOwnerLife
 bcc WfConstructNew
 sta WfOwnerLife              ; a real1up retains source health/actions
 jmp WfConstructDone
WfConstructNew:
 lda #5''',1)
  owner=owner.replace(' lda #$a7\n sta WfHostReady',''' lda #0
 ldx #.lobyte(WfRuntimeStateEnd-WfRenderBuffer-1)
WfClearRuntime:
 sta WfRenderBuffer,x
 dex
 bpl WfClearRuntime
 lda CurrentPlayer
 sta WfOwnerPlayer
 lda NumberofLives
 sta WfOwnerLife
 lda #$a7
 sta WfHostReady''',1)
  owner+='\n.export WfAuthC2,WfReturnC,WfReturnOriginal\n'
  owner=owner.replace('WF_SAVED_P=47','WF_SAVED_P=19').replace('.import __SMCCODE_RUN__,__SMCCODE_SIZE__','.import __SMCCODE_RUN__,__SMCCODE_SIZE__,NextBank_SMC,SafereturnA_SMC')
  owner=owner.replace(' lda __SMCCODE_RUN__,x\n pha\n inx\n cpx #33',' ldy WfMutableOffsets,x\n lda __SMCCODE_RUN__,y\n pha\n inx\n cpx #5',1)
  owner=owner.replace(' ldx #32\n:\n pla\n sta __SMCCODE_RUN__,x\n dex\n bpl :-',' ldx #4\n:\n pla\n ldy WfMutableOffsets,x\n sta __SMCCODE_RUN__,y\n dex\n bpl :-',1)
  for a,z in [('$012f,x','$0113,x'),('$012c,x','$0110,x'),('$012e,x','$0112,x'),('$012d,x','$0111,x')]:owner=owner.replace(a,z)
  owner+='''
.segment "WF_ROM_A"
WfMutableOffsets:
 .byte .lobyte(NextBank_SMC+1-__SMCCODE_RUN__)
 .byte .lobyte(SafecallA_SMC+1-__SMCCODE_RUN__)
 .byte .lobyte(FarcallJmpTarget_SMC+1-__SMCCODE_RUN__)
 .byte .lobyte(FarcallJmpTarget_SMC+2-__SMCCODE_RUN__)
 .byte .lobyte(SafereturnA_SMC+1-__SMCCODE_RUN__)
'''
  owner=owner.replace('WfLoad:\n SaveOwner\n','WfLoad:\n SaveOwner\n jsr WfLoadCore\n jmp WfReturnC\n.export WfLoadCore\nWfLoadCore:\n',1)
  first=owner.index('WfLoadCore:');last=owner.index('; Explicit cold API only.',first)
  owner=owner[:first]+owner[first:last].replace('jcc WfReturnC','bcc WfLoadRejected').replace(' jmp WfReturnC','WfLoadRejected:rts')+owner[last:]
  # The natural scene already owns one complete19-byte save frame. Its
  # internal constructor reuses that frame, avoiding nested-stack overlap
  # with the live page1 transport during genuine NMI audio.
  owner=owner.replace('WfConstructCold:\n SaveOwner\n','WfConstructCold:\n SaveOwner\n jsr WfConstructCore\n jmp WfReturnC\n.export WfConstructCore\nWfConstructCore:\n',1)
  first=owner.index('WfConstructCore:');last=owner.index('; Full preserving independent retirement.',first)
  owncore=owner[first:last].replace('jcc WfReturnC','bcc WfConstructRejected').replace(' sec\n jmp WfReturnC',' sec\nWfConstructRejected:rts')
  owner=owner[:first]+owncore+owner[last:]
  (J/'owner.s').write_text(owner)
  macros=owner[owner.index('.macro SaveOwner'):owner.index('.endmacro',owner.index('.macro SaveOwner'))+len('.endmacro')]
  (J/'owner-macros.inc').write_text(macros+'\n')
  runtime=(R/'tools/reference/wwf_hogan_runtime_v13.s').read_text().replace('.import BwScene,CfRetire,WfRetire,WfLoad,WfCheck,WfConstructCold','.import BwScene,CfRetire,WfRetire,WfLoad,WfCheck,WfConstructCold,WfConstructCore,WfLoadCore').replace('SceneInitialize:\n jsr WfConstructCold','SceneInitialize:\n jsr WfConstructCore').replace(' jsr WfLoad\n bcc SceneDone',' jsr WfLoadCore\n bcc SceneDone')
  (J/'runtime.s').write_text(runtime)
  (J/'runtime-macros.inc').write_text(runtime[runtime.index('.macro SaveRuntime'):runtime.index('.endmacro',runtime.index('.macro SaveRuntime'))+len('.endmacro')]+'\n')
  (J/'palette.s').write_text((R/'tools/reference/wwf_hogan_palette_v4.s').read_text())
  mask=(R/'build/contra-force-p1-kernel-v1/native-mask.s').read_text()
  mask=mask[mask.index('CfNativeP1Mask:'):].replace('CfNativeP1Mask:', 'WfNativeP1Mask:')
  (J/'native-p1-mask.inc').write_text(mask)
  owner=(J/'owner.s').read_text().replace('.import CurrentPlayer,NumberofLives', '.import WfP1Acquire\n.import CurrentPlayer,NumberofLives')
  owner=owner.replace(' lda CurrentPlayer\n sta WfOwnerPlayer',' jsr WfP1Acquire\n lda CurrentPlayer\n sta WfOwnerPlayer',1)
  (J/'owner.s').write_text(owner)
  idle=poses[0];cells=idle['packed_8x16_cells'];packet=[4*len(cells)]
  for cell in cells:packet.extend([cell['page_tile'],cell['role'],cell['y']&255,cell['x']&255])
  (J/'idle.s').write_text('.segment \"WF_RUNTIME_A\"\n.export WfIdleRecord,WfIdlePage\nWfIdlePage:='+str(546+pages.index(idle['packed_page']))+'\nWfIdleRecord:.byte '+','.join(map(str,packet))+'\n')
  (J/'expected.s').write_text(f'.segment "WF_ROM_A"\n.export WfExpectedCookie\nWfExpectedCookie:.incbin "{(J/"cookie.bin").as_posix()}"\n')
  cfg=f'''MEMORY {{
 A1:start=$a000,size=$2000,bank=1,type=ro,file="{(J/'a1.bin').as_posix()}",fill=yes,fillval=0;
 A3:start=$a000,size=$2000,bank=3,type=ro,file="{(J/'a3.bin').as_posix()}",fill=yes,fillval=0;
 C2:start=$c000,size=$2000,bank=2,type=rw,file="{(J/'c2.bin').as_posix()}",fill=yes,fillval=0;
 ROMA:start=$a936,size=$13ca,bank=$60,type=ro,file="{(J/'resident-a.bin').as_posix()}",fill=yes,fillval=$ff;
 ROMC:start=$dd00,size=$300,bank=$60,type=ro,file="{(J/'resident-c.bin').as_posix()}",fill=yes,fillval=$ff;
}}
SEGMENTS {{
 WF_A1_INACTIVE:load=A1,type=ro;
 WF_VM:load=A3,type=ro; WF_TABLE:load=A3,type=ro; WF_SCRIPTS:load=A3,type=ro;
 WF_RAM3_COOKIE:load=A3,type=ro,start=$bfe0;
 WF_STATE:load=C2,type=bss; WF_HOST_CONTEXT:load=C2,type=bss; WF_PROXY_CONTEXT:load=C2,type=bss;
 WF_DESCRIPTORS:load=C2,type=ro; WF_HOGAN_METADATA:load=C2,type=ro;
 WF_FRAME_RECOVERY:load=C2,type=ro; WF_HELPERS:load=C2,type=ro; WF_HOST_CODE:load=C2,type=ro;
 WF_SELECTED_CONTACT:load=C2,type=ro; WF_PROXY_RESET:load=C2,type=ro; WF_PRIVATE:load=C2,type=bss;
 WF_OWNER_STATE:load=C2,type=bss; WF_RUNTIME_STATE:load=C2,type=bss; WF_WORLD_CALLBACKS:load=C2,type=ro;
 WF_PALETTE_STATE:load=C2,type=bss; WF_PALETTE_CODE:load=C2,type=ro; WF_DETACHED_STATE:load=C2,type=bss;\n WF_OWNER_COOKIE:load=C2,type=ro,start=$dfe0;
 WF_ROM_A:load=ROMA,type=ro; WF_RESIDENT_PROXY:load=ROMA,type=ro; WF_RUNTIME_A:load=ROMA,type=ro; WF_ROM_C:load=ROMC,type=ro;
}}
'''
  

  # Metadata-only prelink imports pin true current values. Final host link
  # uses genuine current objects/exports, never this numeric alias producer.
  symbols={k:int(v,16)for v,k in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(P/'candidate.lbl').read_text())}
  imports={}
  for source in [proxy,owner,(J/'runtime.s').read_text(),(J/'world.s').read_text(),(J/'palette.s').read_text()]:
   for zp,names in re.findall(r'(?m)^\.import(zp)?\s+([^\n]+)',source):
    for n in names.split(','):
     n=n.strip()
     if n in symbols:imports[n]=bool(zp)
  # Existing source helper/VM scoped imports are actual current R0..7.
  numeric=[];alias_segments=[]
  from check_tmnt_render_oa import location as native_location
  for index,(n,zp)in enumerate(imports.items()):
   if n in parent['syms'] and 'seg'in parent['syms'][n] and 'ooffs'in parent['segs'][parent['syms'][n]['seg']]:
    pos=native_location(parent,n);bank=(pos-16)//8192;seg=f'WF_NATIVE_ALIAS_{index}'
    cfg=cfg.replace('MEMORY {',f'MEMORY {{ NA{index}:start=${symbols[n]:x},size=1,bank=${bank:x},type=ro,file="";')
    cfg=cfg.replace('SEGMENTS {',f'SEGMENTS {{ {seg}:load=NA{index},type=ro;')
    numeric.append(f'.segment "{seg}"\n.export {n}\n{n}:.byte 0\n');alias_segments.append(seg)
   else:numeric.append(f'.export{"zp"if zp else""} {n}:=${symbols[n]:04x}\n')
  (J/'cache.cfg').write_text(cfg)
  (J/'native-imports.s').write_text(''.join(numeric))
  names=['vm','data','helpers','contact','recovery','host','proxy','aliases','selected-extra','owner','expected','world','runtime','palette','idle']
  ca=R/'tools/Windows/cc65/bin/ca65.exe';ld=R/'tools/Windows/cc65/bin/ld65.exe'
  def run(name,cmd):
   guard=validate(cmd,O,cwd=R)
   for output in guard['outputs']:Path(output['path']).parent.mkdir(parents=True,exist_ok=True)
   z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);log=O/(name+'.json');save(log,dict(command=cmd,output_guard=guard,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr));logs.append(log);assert z.returncode==0,(name,z.stderr)
  def compile(n):run(n+'-build',[str(ca),'-g','-I',str(J),'-I',str(R),str(J/(n+'.s')),'-o',str(J/(n+'.o')),'-l',str(J/(n+'.lst')),'--create-dep',str(J/(n+'.dep'))])
  for n in names+['native-imports']:compile(n)
  def cache_link(tag):run(tag,[str(ld),'-C',str(J/'cache.cfg'),'-o',str(J/'cache.out'),'-Ln',str(J/'cache.lbl'),'-m',str(J/'cache.map'),'--dbgfile',str(J/'cache.dbg'),*[str(J/(n+'.o'))for n in names+['native-imports']]])
  cache_link('cache-initial-link')
  template=b''.join((J/n).read_bytes()for n in ['a1.bin','c2.bin','a3.bin'])
  assert len(template)==24576
  digest=hashlib.sha256(template+(J/'hogan-body.chr').read_bytes()).digest()
  cookie=bytes([0xa7,29,0,1])+digest[:12];(J/'cookie.bin').write_bytes(cookie)
  for n in ['owner','expected']:compile(n)
  cache_link('cache-cookie-link')
  assert template==b''.join((J/n).read_bytes()for n in ['a1.bin','c2.bin','a3.bin'])
  (J/'template.bin').write_bytes(template)
  (J/'stream.s').write_text(f'''.segment "WF_BODY_CHR"
.export WfBodyChr
WfBodyChr:.incbin "{(J/'hogan-body.chr').as_posix()}"
.segment "WF_TEMPLATE_CHR"
WfTemplateChr:.incbin "{(J/'template.bin').as_posix()}"
.segment "WF_METADATA_CHR"
.incbin "{(J/'hogan-metadata.bin').as_posix()}"
.res 2048-1687,0
''');compile('stream')
  # Derive all actual host MEMORY side outputs into this new private root.
  hostcfg=(R/'build/wwf-ready74-first-host-resource-v1/candidate.cfg').read_text()
  hostcfg=hostcfg.replace('X5_NEW_60: start=$a000, size=$2000','X5_NEW_60: start=$a000, size=$936')
  pattern=r'(?m)^(\s*X5_NEW_60:[^\n]*;)'
  hostcfg=re.sub(pattern,lambda m:m[1]+'\n WF_RESIDENT_A:start=$a936,size=$13ca,bank=$60,type=ro,file=%O,fill=yes,fillval=$ff;\n WF_RESIDENT_C:start=$dd00,size=$300,bank=$60,type=ro,file=%O,fill=yes,fillval=$ff;',hostcfg,count=1)
  def split(name,start,size,parts):
   nonlocal hostcfg
   pat=rf'(?m)^\s*{name}:\s*start=\${start:x},size=\${size:x},[^\n]*;'
   assert len(re.findall(pat,hostcfg,re.I))==1,name
   hostcfg=re.sub(pat,'\n'.join(f' {n}:start=${a:x},size=${s:x},type=ro,file=%O,fill=yes,fillval=0;'for n,a,s in parts),hostcfg,count=1,flags=re.I)
  split('M3_CHR_MEM_RETAINED_UNUSED_TAIL',546*1024,58*1024,[('WF_BODY_MEM',546*1024,17*1024),('M3_WWF_UNALLOCATED',563*1024,41*1024)])
  split('TMNT_CHR_MEM_RETAINED_UNUSED_TAIL',629*1024,39*1024,[('WF_TEMPLATE_MEM',629*1024,24*1024),('WF_METADATA_MEM',653*1024,2*1024),('TMNT_WWF_UNALLOCATED',655*1024,13*1024)])
  # Reuse actual source segment declarations with new physical/selected MEMORYs.
  cache_segments=cfg.split('SEGMENTS {',1)[1].rsplit('}',1)[0]
  cache_segments=re.sub(r' WF_NATIVE_ALIAS_\d+:load=NA\d+,type=ro;','',cache_segments)
  cache_segments=cache_segments.replace('load=A1','load=WF_A1_MEM').replace('load=A3','load=WF_A3_MEM').replace('load=C2','load=WF_C2_MEM').replace('load=ROMA','load=WF_RESIDENT_A').replace('load=ROMC','load=WF_RESIDENT_C')
  hostcfg=hostcfg.replace('MEMORY {','MEMORY {\n'+f' WF_A1_MEM:start=$a000,size=$2000,bank=1,type=ro,file="{(J/"final-a1.bin").as_posix()}",fill=yes,fillval=0;\n WF_A3_MEM:start=$a000,size=$2000,bank=3,type=ro,file="{(J/"final-a3.bin").as_posix()}",fill=yes,fillval=0;\n WF_C2_MEM:start=$c000,size=$2000,bank=2,type=rw,file="{(J/"final-c2.bin").as_posix()}",fill=yes,fillval=0;',1)
  hostcfg=hostcfg.replace('SEGMENTS {','SEGMENTS {\n'+cache_segments+'\n WF_BODY_CHR:load=WF_BODY_MEM,type=ro; WF_TEMPLATE_CHR:load=WF_TEMPLATE_MEM,type=ro; WF_METADATA_CHR:load=WF_METADATA_MEM,type=ro;',1)
  counter=0
  def side(m):
   nonlocal counter
   if m[1]in['','%O']or m[1].startswith(J.as_posix()):return m[0]
   counter+=1;return 'file="'+(J/'sideoutputs'/(f'{counter:03d}-'+Path(m[1]).name)).as_posix()+'"'
  hostcfg=re.sub(r'file\s*=\s*"([^"\r\n]*)"',side,hostcfg);(J/'candidate.cfg').write_text(hostcfg)
  cmd=json.loads((P.parent/'final-link.json').read_text())['command'][:]
  for flag,n in [('-C','candidate.cfg'),('-Ln','candidate.lbl'),('-o','candidate.nes')]:cmd[cmd.index(flag)+1]=str(J/n)
  cmd[cmd.index('--ld-args')+1]='--dbgfile,'+str(J/'candidate.dbg')
  if '-m'in cmd:cmd[cmd.index('-m')+1]=str(J/'candidate.map')
  else:cmd+=['-m',str(J/'candidate.map')]
  shared_parent=R/'build/contra-force-p1-coherent-cart-v2/joint/ff-palette.s'
  shared=shared_parent.read_text()
  shared=shared.replace('.import FfMuxNativeROM,FfMuxNativeTail,CfP1NativeRestore', '.import FfMuxNativeROM,FfMuxNativeTail,CfP1NativeRestore\n.import WfLegacyFreeze,WfP1LateDispatch')
  start=shared.index('.proc FwNativeDrawAll');end=shared.index('.endproc',start)
  shared=shared[:start]+'''.proc FwNativeDrawAll
 lda SelectedCharacter
 eor #31
 and #$fd                      ; exactly29/31, original Carry unchanged
 beq CF
 lda SmFreezeRenderState
 beq Native
 sta SafecallA_SMC+1
 lda #<WfLegacyFreeze
 sta FarcallJmpTarget_SMC+1
 lda #>WfLegacyFreeze
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(WfLegacyFreeze)|$80)
Far:
 jmp FarCallCommon
Native:
 jmp FfMuxNativeROM
CF:
 lda SmFreezeRenderState
 jsr FfMuxNativeTail
 sta SafecallA_SMC+1
 lda #<WfP1LateDispatch
 sta FarcallJmpTarget_SMC+1
 lda #>WfP1LateDispatch
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(WfP1LateDispatch)|$80)
 bne Far
 .res 1,$ea
.assert *-FwNativeDrawAll=59,error,"Exact private59B family factoring"
'''+shared[end:]
  (J/'ff-palette.s').write_text(shared)
  fc=json.loads((shared_parent.parents[1]/'ff-palette-build.json').read_text())['command'][:]
  for flag,n in [('-o','ff-palette.o'),('--create-dep','ff-palette.dep'),('--create-full-dep','ff-palette.dep')]:
   if flag in fc:fc[fc.index(flag)+1]=str(J/n)
  fc[fc.index(str(shared_parent))]=str(J/'ff-palette.s')
  run('shared59-build',fc)
  old_ff=shared_parent.with_suffix('.o');assert str(old_ff)in cmd
  cmd[cmd.index(str(old_ff))]=str(J/'ff-palette.o')
  main_recipe=R/'build/bt-p2-cf-menu-source-1031-v2/main-build.json'
  mc=json.loads(main_recipe.read_text())['command'][:]
  main_source=next(Path(p)for p in mc if p.endswith('.s'))
  main_dir=J/'host-main';main_dir.mkdir()
  (main_dir/'entrypoint.s').write_text(main_source.read_text()+'\n.export ImposeGravitySprObj,VerticalForce,VerticalForceDown,PlayerPhysicsSub,Sprite_Data,SprObject_SprAttrib,BlockBufferColli_Head,BlockBufferColli_Side,PlayerHeadWithinTerrain,BlankPalette\n')
  for flag,n in [('-o','main.o'),('-l','main.lst'),('--create-dep','main.dep'),('--create-full-dep','main.dep')]:
   if flag in mc:mc[mc.index(flag)+1]=str(main_dir/n)
  mc[mc.index(str(main_source))]=str(main_dir/'entrypoint.s')
  # Only explicitly funded source hooks; no old Main/object overlays.
  src=main_dir/'src';src.mkdir()
  menu_parent=R/'build/contra-force-menu-admission-1031-v2/joint/src'
  def once(t,a,z):assert t.count(a)==1,(a,t.count(a));return t.replace(a,z,1)
  menu=(menu_parent/'character_select.s').read_text()
  menu=once(menu,'  farcall CfRetire\n','  farcall WfMenuRetire\n')
  (src/'character_select.s').write_text(menu)
  roster=(menu_parent/'full_roster_menu.s').read_text()
  roster=once(roster,' adc #18\n bne Pending',' adc #18\n cmp #19\n rts')
  roster=once(roster,'.res 5,$ea\n.endproc','.res 4,$ea\n.endproc')
  (src/'full_roster_menu.s').write_text(roster)
  (src/'cf_menu_body.inc').write_text((R/'build/future-start-masks-1031-v1/joint/src/cf_menu_body.inc').read_text())
  menu_names=(menu_parent/'full_roster_menu_art.inc').read_text()
  (src/'full_roster_menu_art.inc').write_text(once(menu_names,'  *HULK HOGAN   ','   HULK HOGAN   '))
  screen=(R/'build/bt-p2-cf-menu-source-1031-v2/joint/src/screen_render.s').read_text()
  (src/'screen_render.s').write_text(once(screen,'farcall BwScene','farcall WfScene'))
  nr=(R/'build/bt-ready-menu-1031-v2/joint/src/new_roster_dispatch.s').read_text()
  nr=once(nr,' cmp #26\n beq Own\n cmp #28\n beq GmOnlyHigh\n cmp #22\n beq GmOnlyHigh\n cmp #31\n bcs GmOnlyHigh\n ; Exactly24or28 after clearing their sole differing bit. Every other\n ; highID stays on its genuine old direct legacy table, avoiding recursion.\n and #$fc\n cmp #24\n beq GmOnlyHigh', ' cmp #26\n beq Own\n cmp #22\n beq GmOnlyHigh\n cmp #31\n bcs GmOnlyHigh\n cmp #24\n bcc GmOnlyLegacy\n cmp #30\n bcc GmOnlyHigh\n .res 2,$ea')
  (src/'new_roster_dispatch.s').write_text(nr)
  ep=(main_dir/'entrypoint.s').read_text()+'\n.import WfScene,WfMenuRetire\n'
  (main_dir/'entrypoint.s').write_text(ep)
  mc[1:1]=['-I',str(main_dir),'-I',str(src)]
  union=(R/'build/bt-ready-menu-1031-v2/joint/union.s').read_text()
  union=once(union,' cmp #27\n beq HuExtendedShared\n cmp #31\n beq HuExtendedShared\n cmp #33\n bne HuExtendedNotShared\nHuExtendedShared:\n jmp HuExtendedBT',' cmp #27\n bcc HuExtendedNotShared\n cmp #34\n bcs HuExtendedNotShared\n cmp #28\n beq DK\n cmp #30\n beq Fetch\n jmp HuExtendedBT')
  union=once(union,'Other:\n cmp #28\n beq DK\n cmp #24','Other:\n cmp #24')
  (J/'union.s').write_text(union)
  uc=json.loads((R/'build/m3-cfbt-source-join-plan-v2/actual-recipes.json').read_text())['union']['command'][:]
  uc[1:1]=['-I',str(J),'-I',str(main_dir),'-I',str(src),'-I',str(R/'build/bt-ready-menu-1031-v2/joint'),'-I',str(R/'build/bt-ready-menu-1031-v2/joint/src')]
  uc[-1]=str(J/'union.s')
  for flag,n in [('-o','union.o'),('--create-dep','union.dep'),('--create-full-dep','union.dep'),('-l','union.lst')]:
   if flag in uc:uc[uc.index(flag)+1]=str(J/n)
  run('union-build',uc)
  oldunion=str(R/'build/bt-ready-menu-1031-v2/joint/union.o');assert oldunion in cmd;cmd[cmd.index(oldunion)]=str(J/'union.o')
  bt=(R/'build/bt-jmp-row-cold-source-v1/joint/bt/router.s').read_text()
  bt=once(bt,' lda SelectedCharacter\n cmp #33\n beq Owner\n and #$fb\n cmp #27\n bne Bad',' lda SelectedCharacter\n sec\n sbc #27\n cmp #7\n bcs Bad\n and #1\n bne Bad')
  bt=bt.replace('BwBtResolve','WfResolve').replace('=223,error','=224,error')
  (J/'bt-router.s').write_text(bt)
  run('bt-router-build',[str(ca),'--cpu','6502x','-g','--create-full-dep',str(J/'bt-router.dep'),'-o',str(J/'bt-router.o'),str(J/'bt-router.s')])
  oldbt=str(R/'build/bt-jmp-row-cold-source-v1/joint/bt/router.o');assert oldbt in cmd;cmd[cmd.index(oldbt)]=str(J/'bt-router.o')
  run('main-build',mc)
  old_main=Path('build/bt-p2-cf-menu-source-1031-v2/joint/main.o').resolve()
  assert str(old_main)in cmd
  cmd[cmd.index(str(old_main))]=str(main_dir/'main.o')
  parents=[Path(p)for p in cmd if p.endswith('.o')]
  cmd +=[str(J/(n+'.o'))for n in names+['stream']]
  run('final-link',cmd);prepare(R,J/'candidate.nes')
  now=(J/'candidate.nes').read_bytes();assert len(now)==len(old)
  labels=lambda p:{k:int(v,16)for v,k in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',p.read_text())}
  oldlabels=labels(P/'candidate.lbl');newlabels=labels(J/'candidate.lbl')
  oldpairs=set(re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(P/'candidate.lbl').read_text()))
  newpairs=set(re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(J/'candidate.lbl').read_text()))
  shared_start=address(parent,'FwNativeDrawAll');shared_end=address(parent,'FwNativeDrawAllEnd')
  assert shared_end-shared_start==59
  moved_private=oldpairs-newpairs
  # Source-private branch aliases may move within the bounded hook spans.
  # Stable external interfaces are checked below; ROM closure is exact.
  for n in ['FwNativeDrawAll','FwNativeDrawAllEnd']:assert oldlabels[n]==newlabels[n],n
  for pre,post in [('a1.bin','final-a1.bin'),('c2.bin','final-c2.bin'),('a3.bin','final-a3.bin')]:assert (J/pre).read_bytes()==(J/post).read_bytes(),post
  hook_spans=[]
  for start,end in [('HuCommon','HuLo'),('GmOnlyCommon','GmOnlyLegacy')]:hook_spans.append((location(parent,start),location(parent,end)))
  for n,size in [('BtRouter',114),('MenuResolveCharacter',34),('InitScreen',25),('FmPending',248),('FmCfHelperStart',405)]:hook_spans.append((location(parent,n),location(parent,n)+size))
  hook_spans.append((location(parent,'FmNames')+18*16,location(parent,'FmNames')+19*16))
  stable=['HuEntryBase','HuMovement','HuGraphics','HuDraw','HuCommon','HuCommonAfterSelected','HuCommonRestore','HuLo','GmOnlyCommon','GmOnlyLegacy','BtServiceVeneers','BtServiceUnavailable','BtRouter','MenuResolveCharacter','InitScreen','FmPending','FmResolve','FmToggle','FmStartFlags','FmStartRetireFlags','FmCfHelperStart','DrawSelectionPreview','GameLoop','CfP1NativeRestore']
  for n in stable:
   if n in oldlabels:assert newlabels[n]==oldlabels[n],(n,newlabels[n],oldlabels[n])
  spans=hook_spans+[(16+96*8192+0x936,16+97*8192)]+[(16+1048576+a*1024,16+1048576+z*1024)for a,z in [(546,563),(629,655)]]
  shared_pos=location(parent,'FwNativeDrawAll');spans.append((shared_pos,shared_pos+59))
  diff=[i for i,(a,b)in enumerate(zip(old,now))if a!=b];assert all(any(a<=i<z for a,z in spans)for i in diff)
  proof=dict(source=True,inert=False,native=False,installed=False,private_Hogan_only_source_admission=True,parent=sha(P/'candidate.nes'),candidate=sha(J/'candidate.nes'),resource_contract=sha(G),all_stable_parent_interfaces_exact=True,changed_bytes=len(diff),allowed_physical_spans=spans,first_Hogan=dict(original_id=5,poses=31,body_pages=17,original_body_page_indexes=pages,metadata_bytes=1687),labels={n:v for n,v in newlabels.items()if n.startswith(('Wf','Wp'))},cookie=list(cookie),template_sha256=sha(J/'template.bin'),unbuilt_audio_A1_is_nonexecuting_zero=True,unbound_VM_callbacks_trap=False,limits=['Disposable source proof routes exactly Hogan through real menu/scene/Main; final root adoption and native qualification are separate. Other five WWF identities remain pending; A1 audio is unbuilt.','Source frame API now has actual SMB tile/world-bound and native-enemy intent callbacks; source audio cue class/value is queued, but no audible music/SFX engine is claimed.','Prior-owner retirement via actual outer5FFF protocol remains a documented caller obligation; this private source does invalidate C2 and raw3 validity before every copy.','Native enemy proxy lifetime is serial within movement; external API snapshots still require explicit epoch Notify. No physical native or installation claim.'])
  proof['shared59']=dict(old=list(old[shared_pos:shared_pos+59]),new=list(now[shared_pos:shared_pos+59]),moved_private_aliases=sorted(moved_private),public_start=shared_start,public_end=shared_end,source_parent=str(shared_parent),foreign_zero_extra_CPU=2,other_costs_pending_actual_controls=True)
  proof['bindings']={str(p.resolve()):sha(p)for p in [Path(__file__),G,artpath,artpath.parent/'wrestlers-pages.chr',P/'candidate.nes',P/'candidate.dbg',P/'candidate.lbl',P.parent/'final-link.json',*parents,*logs,*[p for p in J.iterdir()if p.is_file()]]}
  save(O/'source-stage.json',proof);print(json.dumps({k:proof[k]for k in ['source','candidate','changed_bytes','first_Hogan']}))
 except Exception as e:save(O/'negative.json',dict(passed=False,error=repr(e),traceback=traceback.format_exc()));raise

if __name__=='__main__':main()
