"""Private owning Metal composition; never installs or admits a menu identity."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from prepare_cv3_dmc_mirror import prepare as mirror
O=R/'build/metal-storm-owning-graft-1101-v11';J=R/'build/kirby-owner-main-1101-v2'
V7=R/'build/metal-storm-render-host-1101-v7';V8=R/'build/metal-storm-resource-host-1101-v8';V9=R/'build/metal-storm-coexistence-1101-v9';V10=R/'build/metal-storm-chr-closure-1101-v10'
REF=R/'tools/reference/metal_storm_owning_graft_1101_v11.inc'
PIN='c864e46a8f333ab7a936c8d8f330944041a3eff12bc6dd4d9ba96892144ff3c7'
PACKET=R/'docs/qa/checkpoints/2026-11-01/kirby-owner-nightly-v2/source.zip'
GRANT=R/'docs/qa/checkpoints/2026-11-01/metal-storm-chr-resources-v10/resource-grant.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
HOLES=[('GATE',78,0xb6d,147),('ENTRY',95,0x580,128),('WORK',37,0x1f89,119),('CHECK',21,0x1f8a,118),('AUTH',25,0x1f9e,98),('ZERO',116,0xf87,121),('COPY',36,0x1f46,122),('MAP',34,0x1d9e,98),('FINISH',99,0x176e,146)]
PAGES=[247,248,249,250,827,828,829,830,831,500,494]

def once(t,a,b):
 assert t.count(a)==1,a
 return t.replace(a,b)

def command(cmd):
 cmd=list(map(str,cmd));g=validate(cmd,O,cwd=R);p=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
 q=dict(command=cmd,guard=g,returncode=p.returncode,stderr=p.stderr)
 assert p.returncode==0,p.stderr
 return q

def memory_rows(cfg):
 # MEMORY grammar in this exact owning CFG is simple declarations; comments
 # must be removed before summing physical output regions (commented records
 # otherwise create fake owners and shift the CHR file offset).
 clean=re.sub(r'#[^\n]*','',cfg);rows=[];off=0
 for block in re.findall(r'\bMEMORY\s*\{(.*?)\}',clean,re.S):
  for n,v in re.findall(r'(\w+)\s*:\s*([^;]+);',block):
   if not re.search(r'file\s*=\s*%O\b',v):continue
   def num(k):
    m=re.search(r'\b'+k+r'\s*=\s*([^,]+)',v);assert m,(n,k,v)
    expression=re.sub(r'\$([0-9a-fA-F]+)',lambda z:str(int(z[1],16)),m[1]).strip()
    assert re.fullmatch(r'[0-9+\- ]+',expression),(n,k,expression)
    return eval(expression,{'__builtins__':{}},{})
   z=num('size');rows.append(dict(name=n,offset=off,end=off+z,start=num('start'),size=z,clause=v))
   off+=z
 assert off==2097168,off
 return rows

def audit(cfg,raw):
 captured=json.loads((V10/'current-consumer-inputs.json').read_text());assert captured['current_ROM_sha256']==PIN
 segs=[]
 for s in captured['segments'].values():
  if 'ooffs'in s and Path(s.get('oname','').strip('"')).resolve()==(J/'candidate.nes').resolve():
   at=int(s['ooffs'],0);segs.append((at,at+int(s['size'],0),s))
 rows=memory_rows(cfg);out=[]
 for role,bank,pos,size in HOLES:
  lo=16+bank*8192+pos;hi=lo+size
  owners=[x for x in rows if x['offset']<=lo<hi<=x['end']];assert len(owners)==1,(role,owners)
  owner=owners[0];inter=[s['name']for a,z,s in segs if a<hi and z>lo]
  assert not inter and raw[lo:hi]==b'\xff'*size,(role,inter)
  before=max(((a,z,s)for a,z,s in segs if z<=lo and (z-17)//8192==bank),key=lambda x:x[1])
  after=min(((a,z,s)for a,z,s in segs if a>=hi and(a-16)//8192==bank),key=lambda x:x[0],default=None)
  out.append(dict(role=role,bank=bank,physical_offset=pos,A_PC=0xa000+pos,bytes=size,file_interval=[lo,hi],memory_owner=owner,
   preceding_segment=dict(name=before[2]['name'],start=before[0],end=before[1]),following_segment=None if after is None else dict(name=after[2]['name'],start=after[0],end=after[1]),
   segment_intersections=inter,preimage_sha256=hashlib.sha256(raw[lo:hi]).hexdigest(),grant=False))
 return out

def split_cfg(cfg,holes):
 for h in holes:
  owner=h['memory_owner'];n=owner['name'];pos=h['file_interval'][0]-owner['offset'];size=h['bytes'];before=pos;after=owner['size']-pos-size
  pat=r'(?m)^\s*'+re.escape(n)+r'\s*:\s*[^;]+;';hits=list(re.finditer(pat,cfg));assert len(hits)==1,n
  # Keep the named original region and its old run-address origin. All compiled
  # owner segments fit before the leased padding; interior post data retains
  # its old run-address through a separately named memory region.
  clause=owner['clause'];left=re.sub(r'(size\s*=\s*)(\$[0-9a-fA-F]+|\d+)',lambda m:m[1]+f'${before:x}',clause)
  new=(f'\n{n}:{left};'if before else'')+f'\nMS11_{h["role"]}_MEM:start=${h["A_PC"]:x},size=${size:x},bank=${h["bank"]:x},type=ro,file=%O,fill=yes,fillval=$ff;'
  if after:
   right=clause
   for key,value in [('start',owner['start']+pos+size),('size',after)]:right=re.sub(r'('+key+r'\s*=\s*)(\$[0-9a-fA-F]+|\d+)',lambda m:m[1]+f'${value:x}',right)
   new+=f'\n{n}_MS11_POST:{right};'
   # A post fragment exists only for Entry/COPY/ZERO/MAP/FINISH interior
   # padding. Their old explicit segment starts are preserved and rehomed.
   lo=h['file_interval'][1];postend=owner['end'];capture=json.loads((V10/'current-consumer-inputs.json').read_text())
   for s in capture['segments'].values():
    if 'ooffs'not in s or not s.get('oname','').endswith('candidate.nes"'):continue
    at=int(s['ooffs'],0)
    if lo<=at<postend:
     seg=s['name'].strip('"');p=r'(\b'+re.escape(seg)+r'\s*:\s*load\s*=\s*)'+re.escape(n)+r'\b'
     cfg,count=re.subn(p,lambda m:m[1]+n+'_MS11_POST',cfg);assert count==1,(n,seg,count)
  cfg=cfg[:hits[0].start()]+new+cfg[hits[0].end():] if False else re.sub(pat,lambda m:new,cfg,count=1)
 extra=[]
 for h in holes:extra.append(f'MS11_{h["role"]}:load=MS11_{h["role"]}_MEM,type=ro;')
 # Side images are code owners, not cartridge copies. Actual CHR carriers are
 # assembled into the granted physical pages by MS11_IMAGES and privateCV3.
 cfg+='\nMEMORY { MS11_ACTOR_MEM:start=$a000,size=$1fe0,bank=3,type=ro,file="'+(O/'actor.bin').as_posix()+'"; MS11_RENDER_MEM:start=$cd00,size=$12e0,bank=2,type=ro,file="'+(O/'render.bin').as_posix()+'"; }\n'
 cfg+='SEGMENTS { '+''.join(extra)+' MS11_ACTOR:load=MS11_ACTOR_MEM,type=ro; MS11_RENDER:load=MS11_RENDER_MEM,type=ro; MS11_LOW_CHR:load=CHR,type=ro,start=$3dc00; MS11_HIGH_CHR:load=BW_BODY_POST,type=ro,start=$cec00; }\n'
 return cfg

def main():
 assert sha(J/'candidate.nes')==PIN;raw=(J/'candidate.nes').read_bytes();O.mkdir(parents=True,exist_ok=True)
 assert sha(PACKET)=='e465b2c73a0e0ce9a36f55ad3cac648bdf2ec6b1e198c8763974be419688c847'
 grant=json.loads(GRANT.read_text());assert grant['CHR_pages_granted']and not grant['PRG_gates_granted']and not grant['RAM_runtime_lease_granted']
 assert set(PAGES+list(range(495,500)))==set(grant['Metal_pages'])
 for p,h in json.loads((J/'owner-link.json').read_text())['bindings'].items():
  if p.endswith('.o'):assert sha(p)==h,p
 for v in[V7,V8,V9,V10]:
  stage=json.loads((v/'source-stage.json').read_text());assert stage['passed']and sha(v/'source-proof.zip')==stage['archive_sha256']
 cfg=(J/'candidate.cfg').read_text();holes=audit(cfg,raw)
 assert not any(h['bank']==125 for h in holes)
 (O/'ownership.json').write_text(json.dumps(dict(passed=True,CHR_granted=True,PRG_granted=False,RAM_granted=False,native=False,installed=False,baseline=PIN,holes=holes,excluded125='Fixed-E/DMC postlink mirror, exact unchanged current bytes required',coordinated_Tank31_released=True),indent=2)+'\n')
 loader=(R/'tools/reference/metal_storm_resource_host_1101_v8.inc').read_text()
 loader=loader.replace('.segment "GATE"','.segment "MS11_GATE"')
 for h in holes:
  if h['role']!='GATE':loader=loader.replace('.segment "MS8_'+h['role']+'"','.segment "MS11_'+h['role']+'"')
 loader=once(loader,'Ms8Far Ms8Copy,95','Ms8Far Ms8Copy,36')
 loader=loader.replace('831,1023,494','831,500,494')
 loader=once(loader,'Ms8GateAuth:\n','Ms11EmitUpdateEntry\nMs8GateAuth:\n')
 loader=once(loader,' bcc Ms8GateBad\n lda $c800',' bcc Ms8GateBad\n Ms11SelectUpdateBeforeReady\n lda $c800')
 loader=once(loader,'Ms8GateGraphics:\n','Ms11EmitUpdateCall\nMs8GateGraphics:\n')
 (O/'loader.inc').write_text(loader)
 render=(V9/'renderer-palette.inc').read_text().replace('.segment "RENDER"','.segment "MS11_RENDER"')
 (O/'renderer.inc').write_text(render+'\nMs11EmitUpdate\n')
 actor=(V7/'actor.s').read_text().replace('.segment "CODE"','.segment "MS11_ACTOR"').replace('.import MsObjectLifecycle','').replace('.macpack longbranch','')
 (O/'actor.s').write_text(actor)
 symbols=(V9/'red-white-black-symbols.s').read_text();names=re.findall(r'^\.export(?:zp)? (\w+)=',symbols,re.M)
 aliases={n:'Ms11Host_'+n for n in names if not n.startswith(('Ms','MS_'))}
 pre=''.join(f'.define {n} {alias}\n'for n,alias in aliases.items())
 # Public APIs resolve against validated current addresses through private
 # aliases; root globals are not redefined by this component object.
 base='.setcpu "6502"\n.macpack longbranch\n'+pre+'.include "metal_storm_owning_graft_1101_v11.inc"\n.include "actor.s"\n.include "renderer.inc"\n.include "loader.inc"\n'+symbols
 # MsState was imported by the separate renderer object; the combined unit
 # already defines it and may not import its own local symbol.
 base=base.replace('.import MsState,MsLifeUnsupported','.import MsLifeUnsupported')
 # .global is an import only when the symbol stays undefined in this module.
 # Here it retains the original absolute/zp address-size declarations while
 # permitting one owning object with source constants defined at its end.
 # Inline only this small Metal component, never the native dependency tree.
 included={}
 def expand(text):
  def include(m):
   name=m[1];hits=[p/name for p in[O,V7,R/'build/metal-storm-objects-host-1101-v6',R/'build/metal-storm-terrain-host-1101-v5',R/'tools/reference']if(p/name).exists()];assert hits,name
   p=hits[0];included[str(p.resolve())]=sha(p);return '; Bound include '+str(p)+'\n'+expand(p.read_text())
  return re.sub(r'^\s*\.include "([^"]+)"\s*$',include,text,flags=re.M)
 base=expand(base).replace('.importzp ','.globalzp ').replace('.import ','.global ')
 (O/'component.s').write_text(base)
 (O/'cookie.bin').write_bytes(bytes(16))
 cc=R/'tools/Windows/cc65/bin';cmds=[]
 def compile_component(images=False):
  text=base
  if images:text+='\n.segment "MS11_LOW_CHR"\n.incbin "carrier-pack.bin",0,$1000\n.segment "MS11_HIGH_CHR"\n.incbin "carrier-pack.bin",$1000,$1400\n'
  (O/'component.s').write_text(text)
  c=[cc/'ca65.exe','-g','-I',O,'-I',V7,'-I',R/'build/metal-storm-objects-host-1101-v6','-I',R/'build/metal-storm-terrain-host-1101-v5','-I',R/'tools/reference','--bin-include-dir',O,'--bin-include-dir',V7,O/'component.s','-o',O/'component.o'];cmds.append(command(c))
 def isolated_link():
  mem=[f'MS11_ACTOR_MEM:start=$a000,size=$1fe0,bank=3,file="{(O/"actor.bin").as_posix()}";',f'MS11_RENDER_MEM:start=$cd00,size=$12e0,bank=2,file="{(O/"render.bin").as_posix()}";'];seg=['MS11_ACTOR:load=MS11_ACTOR_MEM,type=ro;','MS11_RENDER:load=MS11_RENDER_MEM,type=ro;']
  for h in holes:
   n='MS11_'+h['role'];mem.append(f'{n}_MEM:start=${h["A_PC"]:x},size=${h["bytes"]:x},bank={h["bank"]},file="{(O/(h["role"].lower()+".bin")).as_posix()}";');seg.append(f'{n}:load={n}_MEM,type=ro;')
  (O/'component.cfg').write_text('MEMORY{'+''.join(mem)+'}SEGMENTS{'+''.join(seg)+'}\n')
  cmds.append(command([cc/'ld65.exe','-C',O/'component.cfg',O/'component.o','-o',O/'unused.bin','-Ln',O/'component.lbl']))
 compile_component();isolated_link()
 actor=(O/'actor.bin').read_bytes();render=(O/'render.bin').read_bytes();art=(V9/'red-white-black.chr').read_bytes()
 assert actor==(V9/'red-white-black-actor.bin').read_bytes()
 expected=(V9/'red-white-black-render.bin').read_bytes();assert render[:len(expected)]==expected
 cookie=bytes([0xa7,35,11])+hashlib.sha256(actor+render+art+loader.encode()+REF.read_bytes()+PIN.encode()).digest()[:13];(O/'cookie.bin').write_bytes(cookie)
 compile_component();isolated_link();assert actor==(O/'actor.bin').read_bytes()and render==(O/'render.bin').read_bytes()
 image=bytearray([255])*8192;image[:len(actor)]=actor;image[0x1fe0:0x1ff0]=bytes(16);carriers=bytes(image)+render+bytes(3072-len(render));assert len(carriers)==11264
 # Physical high carrier pages827..831 contain actor rows4..7 then render0.
 (O/'carrier-pack.bin').write_bytes(carriers)
 (O/'cv3-granted-pages.bin').write_bytes(carriers[10240:11264]+art+carriers[9216:10240])
 with zipfile.ZipFile(PACKET)as z:entry_bytes=z.read('host/entrypoint.s')
 old_binding=json.loads((J/'owner-link.json').read_text())['bindings'];entry_path=next(p for p in old_binding if p.endswith('entrypoint.s'))
 assert hashlib.sha256(entry_bytes).hexdigest()==old_binding[entry_path]
 (O/'entrypoint.s').write_bytes(entry_bytes)
 cv3path=R/'build/bt-ready-menu-1031-v2/joint/src/cv3.s';cv3=cv3path.read_text()
 cv3=once(cv3,'.incbin "chr/characters/cv3.chr"','.incbin "chr/characters/cv3.chr",0,$8800\n.incbin "cv3-granted-pages.bin"\n.incbin "chr/characters/cv3.chr",$a400,$5c00')
 (O/'cv3.s').write_text(cv3)
 compile_component(images=True)
 maincmd=json.loads((J/'main-build.json').read_text())['command'].copy();maincmd[1:1]=['-I',str(O),'--bin-include-dir',str(O)]
 for key,target in[('-o','main.o'),('--create-full-dep','main.dep')]:maincmd[maincmd.index(key)+1]=str(O/target)
 maincmd[-1]=str(O/'entrypoint.s')
 if '--reuse-main'in sys.argv:
  mainreceipt=json.loads((O/'main-build.json').read_text());assert mainreceipt['command']==maincmd and mainreceipt['returncode']==0
  assert mainreceipt['private_CV3_image_sha256']==sha(O/'cv3-granted-pages.bin'),'Main-owned image changed; recompile Main'
  assert (O/'main.o').exists()and(O/'main.dep').exists()
 else:
  mainreceipt=command(maincmd);mainreceipt['private_CV3_image_sha256']=sha(O/'cv3-granted-pages.bin');(O/'main-build.json').write_text(json.dumps(mainreceipt,indent=2)+'\n')
 config=split_cfg(cfg,holes).replace(str(J).replace('\\','/'),str(O).replace('\\','/')).replace(str(J),str(O));(O/'candidate.cfg').write_text(config)
 for target in re.findall(r'file="([^"]+)"',config):
  if target and target!='%O':
   p=Path(target).resolve();assert p.is_relative_to(O.resolve());p.parent.mkdir(parents=True,exist_ok=True)
 link=json.loads((J/'link.json').read_text())['command'].copy()
 link[link.index('-C')+1]=str(O/'candidate.cfg');link[link.index(str(J/'main.o'))]=str(O/'main.o')
 for key,target in[('-o','candidate.nes'),('-Ln','candidate.lbl'),('-m','candidate.map')]:link[link.index(key)+1]=str(O/target)
 link[link.index('--ld-args')+1]='--dbgfile,'+str(O/'candidate.dbg');link.append(str(O/'component.o'))
 linkreceipt=command(link);(O/'link.json').write_text(json.dumps(linkreceipt,indent=2)+'\n')
 dbg=O/'candidate.dbg';keep={b'version',b'info',b'file',b'lib',b'mod',b'seg',b'scope',b'sym'};dbg.write_bytes(b''.join(l for l in dbg.read_bytes().splitlines(keepends=True)if l.split(b'\t',1)[0]in keep))
 mirror(R,O/'candidate.nes');new=(O/'candidate.nes').read_bytes();assert len(new)==len(raw)
 allowed=[h['file_interval']for h in holes]+[[1048592+p*1024,1048592+(p+1)*1024]for p in grant['Metal_pages']]
 changes=[i for i,(a,b)in enumerate(zip(raw,new))if a!=b];assert changes and all(any(a<=i<z for a,z in allowed)for i in changes),'Unowned byte changed'
 assert raw[16+125*8192:16+126*8192]==new[16+125*8192:16+126*8192]
 old=qualified(J/'candidate.nes');bound=qualified(O/'candidate.nes')
 def symbols_by_id(path):
  out={}
  for line in path.read_text().splitlines():
   if line.startswith('sym\t'):
    s=dict(re.findall(r'(\w+)=("[^"]*"|[^,]+)',line[4:]));out[s['id']]={k:s.get(k)for k in['name','val','seg','addrsize','scope','type']}
  return out
 oldsymbols=symbols_by_id(J/'candidate.dbg');newsymbols=symbols_by_id(O/'candidate.dbg')
 moved=[(i,s,newsymbols.get(i))for i,s in oldsymbols.items()if newsymbols.get(i)!=s]
 assert not moved,moved[:20]
 oldlayout={s['name']:(s['start'],s['size'],s.get('ooffs'))for s in old['segs'].values()}
 assert all((s['start'],s['size'],s.get('ooffs'))==oldlayout[s['name']]for s in bound['segs'].values()if s['name']in oldlayout)
 fragments=[]
 for h in holes:
  data=(O/(h['role'].lower()+'.bin')).read_bytes();assert new[h['file_interval'][0]:h['file_interval'][0]+len(data)]==data
  fragments.append(dict(role=h['role'],bank=h['bank'],PC=h['A_PC'],bytes=len(data),remaining=h['bytes']-len(data)))
 deps=[Path(p)for p in link if p.endswith('.o')and Path(p).resolve()not in[O/'main.o',O/'component.o']]
 inputs=[Path(__file__),REF,PACKET,GRANT,J/'owner-link.json',J/'candidate.nes',J/'candidate.cfg',J/'main-build.json',J/'link.json',V10/'current-consumer-inputs.json',V7/'actor.s',V9/'renderer-palette.inc',V9/'red-white-black-symbols.s',V9/'red-white-black.chr',R/'tools/reference/metal_storm_resource_host_1101_v8.inc',cv3path,O/'component.s',O/'loader.inc',O/'renderer.inc',O/'actor.s',O/'entrypoint.s',O/'cv3.s',O/'candidate.cfg',O/'main.dep',O/'cookie.bin']+deps
 labels={m[2]:int(m[1],16)for l in(O/'component.lbl').read_text().splitlines()if(m:=re.fullmatch(r'al ([0-9a-fA-F]+) \.(\S+)',l))}
 result=dict(passed=True,private_owning_relink=True,menu_admitted=False,native=False,installed=False,PRG_granted=False,RAM_granted=False,CHR_granted=True,baseline=PIN,ROM_sha256=sha(O/'candidate.nes'),actor_bytes=len(actor),renderer_bytes=len(render),fragments=fragments,labels=labels,cookie=cookie.hex(),changed_bytes=len(changes),all_old_public_values_preserved=True,all_old_segment_layouts_preserved=True,fixed125_exact=True,disjoint_Tank_bank31_vacated=True,commands=cmds,bindings={str(p.resolve()):sha(p)for p in inputs},scope='Actual source-owned Main/CV3/carrier and9fragment relink into private c864 successor. No root/native/menu activation. Original source callback ports and lifecycle transition hooks remain unadmitted.')
 (O/'owning-link.json').write_text(json.dumps(result,indent=2)+'\n');assert sha(J/'candidate.nes')==PIN
 print(json.dumps({k:v for k,v in result.items()if k not in['commands','bindings','labels']}))
if __name__=='__main__':main()
