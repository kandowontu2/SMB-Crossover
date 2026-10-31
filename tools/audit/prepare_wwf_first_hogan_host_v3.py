"""Granted, inert first-Hogan physical layout/loader on genuine current a126."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load,address,location
from prepare_cv3_dmc_mirror import prepare
O=R/'build/wwf-first-hogan-host-v3';J=O/'joint'
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
  (J/'aliases.s').write_text(aliases)
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
  (J/'owner.s').write_text(owner)
  (J/'expected.s').write_text(f'.segment "WF_ROM_A"\n.export WfExpectedCookie\nWfExpectedCookie:.incbin "{(J/"cookie.bin").as_posix()}"\n')
  cfg=f'''MEMORY {{
 A1:start=$a000,size=$2000,bank=1,type=ro,file="{(J/'a1.bin').as_posix()}",fill=yes,fillval=0;
 A3:start=$a000,size=$2000,bank=3,type=ro,file="{(J/'a3.bin').as_posix()}",fill=yes,fillval=0;
 C2:start=$c000,size=$2000,bank=2,type=rw,file="{(J/'c2.bin').as_posix()}",fill=yes,fillval=0;
 ROMA:start=$a936,size=$eca,bank=$60,type=ro,file="{(J/'resident-a.bin').as_posix()}",fill=yes,fillval=$ff;
 ROMC:start=$d800,size=$800,bank=$60,type=ro,file="{(J/'resident-c.bin').as_posix()}",fill=yes,fillval=$ff;
}}
SEGMENTS {{
 WF_A1_INACTIVE:load=A1,type=ro;
 WF_VM:load=A3,type=ro; WF_TABLE:load=A3,type=ro; WF_SCRIPTS:load=A3,type=ro;
 WF_RAM3_COOKIE:load=A3,type=ro,start=$bfe0;
 WF_STATE:load=C2,type=bss; WF_HOST_CONTEXT:load=C2,type=bss; WF_PROXY_CONTEXT:load=C2,type=bss;
 WF_DESCRIPTORS:load=C2,type=ro; WF_HOGAN_METADATA:load=C2,type=ro;
 WF_FRAME_RECOVERY:load=C2,type=ro; WF_HELPERS:load=C2,type=ro; WF_HOST_CODE:load=C2,type=ro;
 WF_SELECTED_CONTACT:load=C2,type=ro; WF_PROXY_RESET:load=C2,type=ro; WF_PRIVATE:load=C2,type=bss;
 WF_OWNER_STATE:load=C2,type=bss; WF_UNBOUND_CALLBACKS:load=C2,type=ro;
 WF_OWNER_COOKIE:load=C2,type=ro,start=$dfe0;
 WF_ROM_A:load=ROMA,type=ro; WF_RESIDENT_PROXY:load=ROMA,type=ro; WF_ROM_C:load=ROMC,type=ro;
}}
'''
  cfg=cfg.replace('MEMORY {','MEMORY { NATIVEPUB:start=$a03d,size=1,bank=$3e,type=ro,file=\"\";').replace('SEGMENTS {','SEGMENTS { WF_NATIVE_ALIAS:load=NATIVEPUB,type=ro;')
  (J/'cache.cfg').write_text(cfg)
  # Metadata-only prelink imports pin true current values. Final host link
  # uses genuine current objects/exports, never this numeric alias producer.
  symbols={k:int(v,16)for v,k in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(P/'candidate.lbl').read_text())}
  imports={}
  for source in [proxy,owner]:
   for zp,names in re.findall(r'(?m)^\.import(zp)?\s+([^\n]+)',source):
    for n in names.split(','):
     n=n.strip()
     if n in symbols:imports[n]=bool(zp)
  # Existing source helper/VM scoped imports are actual current R0..7.
  numeric=['.segment \"WF_NATIVE_ALIAS\"\n.export X5PublishChr\nX5PublishChr:.byte 0\n']
  for n,zp in imports.items():
   if n=='X5PublishChr':continue
   numeric.append(f'.export{"zp"if zp else""} {n}:=${symbols[n]:04x}\n')
  (J/'native-imports.s').write_text(''.join(numeric))
  names=['vm','data','helpers','contact','recovery','host','proxy','aliases','selected-extra','owner','expected']
  ca=R/'tools/Windows/cc65/bin/ca65.exe';ld=R/'tools/Windows/cc65/bin/ld65.exe'
  def run(name,cmd):
   guard=validate(cmd,O,cwd=R)
   for output in guard['outputs']:Path(output['path']).parent.mkdir(parents=True,exist_ok=True)
   z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);log=O/(name+'.json');save(log,dict(command=cmd,output_guard=guard,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr));logs.append(log);assert z.returncode==0,(name,z.stderr)
  def compile(n):run(n+'-build',[str(ca),'-g',str(J/(n+'.s')),'-o',str(J/(n+'.o')),'-l',str(J/(n+'.lst')),'--create-dep',str(J/(n+'.dep'))])
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
  hostcfg=re.sub(pattern,lambda m:m[1]+'\n WF_RESIDENT_A:start=$a936,size=$eca,bank=$60,type=ro,file=%O,fill=yes,fillval=$ff;\n WF_RESIDENT_C:start=$d800,size=$800,bank=$60,type=ro,file=%O,fill=yes,fillval=$ff;',hostcfg,count=1)
  def split(name,start,size,parts):
   nonlocal hostcfg
   pat=rf'(?m)^\s*{name}:\s*start=\${start:x},size=\${size:x},[^\n]*;'
   assert len(re.findall(pat,hostcfg,re.I))==1,name
   hostcfg=re.sub(pat,'\n'.join(f' {n}:start=${a:x},size=${s:x},type=ro,file=%O,fill=yes,fillval=0;'for n,a,s in parts),hostcfg,count=1,flags=re.I)
  split('M3_CHR_MEM_RETAINED_UNUSED_TAIL',546*1024,58*1024,[('WF_BODY_MEM',546*1024,17*1024),('M3_WWF_UNALLOCATED',563*1024,41*1024)])
  split('TMNT_CHR_MEM_RETAINED_UNUSED_TAIL',629*1024,39*1024,[('WF_TEMPLATE_MEM',629*1024,24*1024),('WF_METADATA_MEM',653*1024,2*1024),('TMNT_WWF_UNALLOCATED',655*1024,13*1024)])
  # Reuse actual source segment declarations with new physical/selected MEMORYs.
  cache_segments=cfg.split('SEGMENTS {',1)[1].rsplit('}',1)[0].replace(' WF_NATIVE_ALIAS:load=NATIVEPUB,type=ro;','')
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
  parents=[Path(p)for p in cmd if p.endswith('.o')]
  cmd +=[str(J/(n+'.o'))for n in names+['stream']]
  run('final-link',cmd);prepare(R,J/'candidate.nes')
  now=(J/'candidate.nes').read_bytes();assert len(now)==len(old)
  labels=lambda p:{k:int(v,16)for v,k in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',p.read_text())}
  oldlabels=labels(P/'candidate.lbl');newlabels=labels(J/'candidate.lbl')
  assert all(newlabels[k]==v for k,v in oldlabels.items()),'Foreign endpoint moved'
  for pre,post in [('a1.bin','final-a1.bin'),('c2.bin','final-c2.bin'),('a3.bin','final-a3.bin')]:assert (J/pre).read_bytes()==(J/post).read_bytes(),post
  spans=[(16+96*8192+0x936,16+97*8192)]+[(16+1048576+a*1024,16+1048576+z*1024)for a,z in [(546,563),(629,655)]]
  diff=[i for i,(a,b)in enumerate(zip(old,now))if a!=b];assert all(any(a<=i<z for a,z in spans)for i in diff)
  proof=dict(source=True,inert=True,native=False,installed=False,readiness_unchanged=True,parent=sha(P/'candidate.nes'),candidate=sha(J/'candidate.nes'),resource_contract=sha(G),all_parent_labels_exact=True,changed_bytes=len(diff),allowed_physical_spans=spans,first_Hogan=dict(original_id=5,poses=31,body_pages=17,original_body_page_indexes=pages,metadata_bytes=1687),labels={n:v for n,v in newlabels.items()if n.startswith(('Wf','Wp'))},cookie=list(cookie),template_sha256=sha(J/'template.bin'),unbuilt_audio_A1_is_nonexecuting_zero=True,unbound_VM_callbacks_trap=True,limits=['No host/common/menu/audio gate installed. Only first-Hogan owner/loader/auth/retire and guarded constructor/native-proxy APIs are callable.','No frame API is exposed: original RingClamp/RingBounds/AI/audio boundaries remain explicit traps in this physical cache rather than donor-lab oracle aliases or gameplay substitutes.','Prior-owner retirement via actual outer5FFF protocol remains a documented caller obligation; this private source does invalidate C2 and raw3 validity before every copy.','Epoch-notify hooks remain uninstalled. No native/menu readiness claim.'])
  proof['bindings']={str(p.resolve()):sha(p)for p in [Path(__file__),G,artpath,artpath.parent/'wrestlers-pages.chr',P/'candidate.nes',P/'candidate.dbg',P/'candidate.lbl',P.parent/'final-link.json',*parents,*logs,*[p for p in J.iterdir()if p.is_file()]]}
  save(O/'source-stage.json',proof);print(json.dumps({k:proof[k]for k in ['source','candidate','changed_bytes','first_Hogan']}))
 except Exception as e:save(O/'negative.json',dict(passed=False,error=repr(e),traceback=traceback.format_exc()));raise

if __name__=='__main__':main()
