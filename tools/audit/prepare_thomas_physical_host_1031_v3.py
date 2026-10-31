"""True object/source link of owned Thomas payload; no shared hook changes."""
from pathlib import Path
import hashlib,json,math,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
import thomas_original_cpu_1031_v1 as T
P=R/'build/thomas-host-boundary-1031-v2';A=R/'build/thomas-sparse-template-1031-v1'
J=R/'build/contra-force-world-roles-1031-v2/joint';O=R/'build/thomas-physical-host-1031-v9'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
dump=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def main():
 assert not O.exists();S=O/'source';S.mkdir(parents=True);(O/'sideoutputs').mkdir()
 assert sha(J/'candidate.nes')=='a12661c1ddad2e15a8ce0589e86b5510703fd390e6346a982b14a6be0b742e3c'
 pstage=json.loads((P/'source-stage.json').read_text())
 for p,h in pstage['bindings'].items():assert sha(p)==h,p
 def private_labels(text,prefix):
  for name in sorted(set(re.findall(r'^([A-Za-z_]\w*):',text,re.M)),key=len,reverse=True):
   if not name.startswith(('Th','Thomas')):text=re.sub(r'\b'+name+r'\b',prefix+name,text)
  return text
 cache=private_labels((R/'tools/reference/thomas_cache_host_1031_v3.s').read_text(),'ThCache')
 (S/'cache.s').write_text(cache,encoding='utf-8')
 core=(P/'source/component.s').read_text().replace('.segment "CODE"','.segment "THOMAS_KERNEL"')
 # Source specialization to the only admitted original damage target X6.
 # Exact live instruction bodies remain; unreachable enemy branches/data APIs
 # are removed rather than linked to a lab trap or unrelated original address.
 removed=[];kept=[]
 for line in core.splitlines():
  m=re.match(r'ThHealth_([0-9A-F]{4}):',line)
  if m and any(lo<=int(m[1],16)<hi for lo,hi in [(0xc4b4,0xc4e5),(0xc54d,0xc5bc),(0xc5c2,0xc5fc)]):removed.append(line);continue
  kept.append(line)
 core='\n'.join(kept)+'\n'
 # Remaining CPX branches are source X6 contracts. Remove now-unused imports.
 for name in re.findall(r'\.import (ThomasOriginal_\w+)',core):
  if len(re.findall(r'\b'+name+r'\b',core))==1:core=re.sub(r' ?\.import '+name+r'\n','',core)
 assert 'ThomasOriginal_B243'not in core
 (S/'component.s').write_text(core,encoding='utf-8');dump(O/'unadmitted-enemy-source-removed.json',removed)
 deps=(P/'source/dependencies.s').read_text().replace('.segment "CODE"','.segment "THOMAS_KERNEL"')
 deps=deps.replace('.export ThomasOriginal_B243\nThomasOriginal_B243: brk\n','')
 (S/'dependencies.s').write_text(deps,encoding='utf-8')
 host=private_labels((P/'source/host.s').read_text(),'ThBoundary').replace('.segment "CODE"','.segment "THOMAS_KERNEL"')
 host+='\n.export ThAllKernelEnd\nThAllKernelEnd:\n';(S/'boundary.s').write_text(host,encoding='utf-8')
 # These are true linker expressions over the existing imported host symbols,
 # not numeric native entry aliases or a prebuilt lab import object.
 banks=sorted(set(re.findall(r'\.import Bank_([^\n]+)',host)))
 banknames=[]
 for row in banks:banknames.extend('Bank_'+n.strip()if not n.strip().startswith('Bank_')else n.strip()for n in row.split(','))
 banktext=''
 for name in sorted(set(banknames)):
  target=name[5:];banktext+=f'.import {target}\n.export {name}\n{name}=.lobyte(.bank({target})|$80)\n'
 (S/'banks.s').write_text(banktext,encoding='utf-8')
 metadata=bytearray((A/'metadata.bin').read_bytes())
 cursor=0
 for pose in json.loads((A/'pose-packing.json').read_text())['poses']:
  count=metadata[cursor]
  for at in range(cursor+1,cursor+1+count,4):
   y,tile,attr,x=metadata[at:at+4];metadata[at:at+4]=bytes([tile,attr,y,x])
  cursor+=1+count
 assert cursor==1026
 metadata=bytes(metadata);(S/'metadata.bin').write_bytes(metadata)
 (S/'native-charmap.inc').write_text((R/'inc/charmap.inc').read_text(),encoding='utf-8')
 desc=(A/'native-descriptors.bin').read_bytes();n=len(desc)
 (S/'metadata.s').write_text(f'.segment "THOMAS_STATE_META"\nThPoseData:\n.incbin "metadata.bin"\n.export ThDescriptorLo,ThDescriptorHi,ThPoseWindows\nThDescriptorLo=ThPoseData+{n}\nThDescriptorHi=ThDescriptorLo+42\nThPoseWindows=ThDescriptorHi+42\n',encoding='utf-8')
 first=json.loads((A/'pose-packing.json').read_text())['poses'][0]
 firstbytes=metadata[:1+first['parts']*4];(S/'standing.inc').write_text('.byte '+','.join(f'${v:02X}'for v in firstbytes)+'\n',encoding='utf-8')
 (S/'resident.s').write_text(private_labels((R/'tools/reference/thomas_resident_1031_v3.s').read_text(),'ThRom'),encoding='utf-8')
 (S/'cookie.bin').write_bytes(bytes(16));(S/'carrier.chr').write_bytes(bytes(16384))
 (S/'carrier.s').write_text('.segment "THOMAS_CHR"\n.incbin "carrier.chr"\n',encoding='utf-8')
 cfg=(J/'candidate.cfg').read_text()
 cfg=cfg.replace('X5_NEW_55: start=$c000, size=$2000, type=ro, file=%O, fill=yes, fillval=$ff, bank=$55;',
  'X5_NEW_55: start=$c000,size=$133a,type=ro,file=%O,fill=yes,fillval=$ff,bank=$55;\n TH_RES_LOAD:start=$d33a,size=$5c6,type=ro,file=%O,fill=yes,fillval=$ff,bank=$55;\n TH_55_POST:start=$d900,size=$700,type=ro,file=%O,fill=yes,fillval=$ff,bank=$55;')
 cfg=cfg.replace('ROGUE_AUDIO_PAGES_1: load=X5_NEW_55','ROGUE_AUDIO_PAGES_1: load=TH_55_POST')
 cfg=cfg.replace('CD_CHR_MEM: start=$67000,size=$c000,type=ro,fill=yes,file=%O,fillval=$00;',
  'CD_CHR_MEM:start=$67000,size=$3800,type=ro,fill=yes,file=%O,fillval=$00;\n TH_CHR_MEM:start=$6a800,size=$4000,type=ro,fill=yes,file=%O,fillval=$00;\n CD_CHR_POST:start=$6e800,size=$4800,type=ro,fill=yes,file=%O,fillval=$00;')
 assert 'TH_RES_LOAD:'in cfg and 'TH_CHR_MEM:'in cfg
 # Rebind every inherited MEMORY side file before invoking any compiler.
 side=0
 def sidefile(m):
  nonlocal side
  value=m[1]
  if not value:return m[0]
  side+=1;return 'file="'+(O/f'sideoutputs/{side:02d}-{Path(value).name}').as_posix()+'"'
 cfg=re.sub(r'file\s*=\s*"([^"\n]*)"',sidefile,cfg)
 where=cfg.index('SEGMENTS')
 cfg=cfg[:where].rstrip()[:-1]+f'\n TH_RES_RUN:start=$b33a,size=$5c6,type=ro,file="",bank=$55;\n TH_KERNEL_MEM:start=$a000,size=$2000,type=ro,file="{(O/"kernel.bin").as_posix()}",fill=yes,fillval=$ff,bank=3;\n TH_STATE_MEM:start=$c000,size=$2000,type=ro,file="{(O/"state.bin").as_posix()}",fill=yes,fillval=$00,bank=2;\n}}\n'+cfg[where:]
 newsegs='\n THOMAS_RESIDENT:load=TH_RES_LOAD,run=TH_RES_RUN,type=ro;\n THOMAS_KERNEL:load=TH_KERNEL_MEM,type=ro;\n THOMAS_STATE_META:load=TH_STATE_MEM,type=ro,start=$d000;\n THOMAS_CHR:load=TH_CHR_MEM,type=ro;\n'
 cfg,count=re.subn(r'\n}\s*SYMBOLS\s*{',lambda m:newsegs+'}\nSYMBOLS {',cfg,count=1);assert count==1
 (O/'candidate.cfg').write_text(cfg,encoding='utf-8')
 cc=R/'tools/Windows/cc65/bin';commands=[]
 def run(cmd):
  guard=validate(cmd,O,cwd=S);p=subprocess.run(list(map(str,cmd)),cwd=S,capture_output=True,text=True)
  commands.append(dict(command=list(map(str,cmd)),guard=guard,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr));dump(O/'build-commands.json',commands)
  assert not p.returncode,p.stderr
 def assemble(name):run([cc/'ca65.exe',S/f'{name}.s','-g','-o',O/f'{name}.o','-l',O/f'{name}.lst','--create-full-dep',O/f'{name}.dep'])
 own=['cache','component','dependencies','boundary','banks','metadata','resident','tables','carrier']
 def tables(codepages):
  body=426+codepages+2
  chrrows=list(range(426,426+codepages))+[255]*(8-codepages)+[255]*4+[426+codepages,426+codepages+1]+[255]*2
  text='.segment "THOMAS_RESIDENT"\n.export ThLoadBank,ThLoadHigh,ThLoadCHR,ThLoadFill,ThBodyPage,ThAllResidentEnd\n'
  for name,values in [('ThLoadBank',[3]*8+[2]*8),('ThLoadHigh',[0xc0+4*i for i in range(8)]*2),('ThLoadCHR',chrrows),('ThLoadFill',[255]*8+[0]*8)]:text+=name+':.byte '+','.join(str(v&255)for v in values)+'\n'
  text+=f'ThBodyPage={body}\nThAllResidentEnd:\n.assert ThAllResidentEnd<=$b900,lderror,"All resident tables within1478B"\n'
  (S/'tables.s').write_text(text,encoding='utf-8');assemble('tables');return body
 body=tables(6)
 for name in own:
  if name!='tables':assemble(name)
 original=json.loads((J.parent/'final-link.json').read_text())['command'];inputs=[Path(v)for v in original if str(v).lower().endswith('.o')]
 def link(name):
  cmd=[cc/'cl65.exe','--cpu','6502x','-t','nes','-C',O/'candidate.cfg','-Ln',O/'candidate.lbl','--ld-args','--dbgfile,'+str(O/'candidate.dbg'),'-o',O/'candidate.nes',*inputs,*[O/f'{n}.o'for n in own]]
  run(cmd);dump(O/f'{name}-link.json',commands[-1])
 link('preflight');s=T.labels(O/'candidate.lbl');pages=math.ceil((s['ThAllKernelEnd']-0xa000)/1024)
 if pages!=6:body=tables(pages);link('sized')
 kernel=(O/'kernel.bin').read_bytes();state=(O/'state.bin').read_bytes()
 # a126's parent recipe calls a post-link mirror builder. Reproduce the exact
 # inherited125 product through assembled source, using THIS final127 source
 # output plus its two declared native DMC assets and existing manager object.
 # There is no byte write to the linked cartridge after the linker completes.
 raw=(O/'candidate.nes').read_bytes();fixed=raw[16+127*8192:16+128*8192]
 assert fixed==(J/'candidate.nes').read_bytes()[16+127*8192:16+128*8192]
 assert 'SamusAudioCold'not in s and s['Cv3DmcManagerEnd']==0xdb8a
 (S/'fixed127.bin').write_bytes(fixed)
 mirror='.setcpu "6502"\n; Native private managerEnd DB8A authenticated from actual DBG before/after source link.\n.segment "TH_E125_PREFIX"\n.incbin "fixed127.bin",0,$1140\n.incbin "'+(R/'audio/cv3/primary72.dmc').as_posix()+'"\n.incbin "fixed127.bin",$1581,$3f\n.incbin "'+(R/'audio/cv3/sypha75.dmc').as_posix()+'"\n.incbin "fixed127.bin",$1681,$476\n.segment "TH_E125_AFTER_MANAGER"\n.incbin "fixed127.bin",$1b8a,$287\n.segment "TH_E125_END"\n.incbin "fixed127.bin",$1e11,$1ef\n'
 # 1E11-1B8A=287; first prefix remains1AF7 exactly.
 (S/'mirror.s').write_text(mirror,encoding='utf-8')
 cfg=cfg.replace('\n}\nSYMBOLS {','\n TH_E125_PREFIX:load=X5_NEW_7D,type=ro;\n TH_E125_AFTER_MANAGER:load=CV3_DMC_C,type=ro,start=$db8a;\n TH_E125_END:load=CV3_DMC_TAIL,type=ro;\n}\nSYMBOLS {',1)
 (O/'candidate.cfg').write_text(cfg,encoding='utf-8');assemble('mirror');own.append('mirror')
 cookie=bytes([167,10,64,1])+hashlib.sha256(kernel+state).digest()[:12]
 (S/'cookie.bin').write_bytes(cookie)
 carrier=kernel[:pages*1024]+state[0x1000:0x1800]+(A/'body.chr').read_bytes()
 assert len(carrier)<=16384;(S/'carrier.chr').write_bytes(carrier+bytes(16384-len(carrier)))
 assemble('resident');assemble('carrier');link('final')
 assert (O/'kernel.bin').read_bytes()==kernel and(O/'state.bin').read_bytes()==state
 s=T.labels(O/'candidate.lbl');old=T.labels(J/'candidate.lbl')
 assert all(s[n]==v for n,v in old.items()),[(n,v,s.get(n))for n,v in old.items()if s.get(n)!=v][:12]
 before=(J/'candidate.nes').read_bytes();after=(O/'candidate.nes').read_bytes();diff=[i for i,(a,z)in enumerate(zip(before,after))if a!=z]
 assert len(before)==len(after)
 assert all(701258<=i<702736 or 1048592+426*1024<=i<1048592+442*1024 for i in diff)
 dump(O/'source-stage.json',dict(passed=True,source_only=True,native=False,shared_hook_changes=False,pending=True,
  host_parent_sha256=sha(J/'candidate.nes'),candidate_sha256=sha(O/'candidate.nes'),code_bytes=s['ThAllKernelEnd']-0xa000,resident_bytes=s['ThAllResidentEnd']-0xb33a,
  code_pages=pages,body_first_page=body,total_CHR_pages_used=len(carrier)//1024,changed_bytes=len(diff),old_resolved_labels_preserved=len(old),
  source_specialization='Only admitted native damageX6; unadmitted enemy-only bodies/B243 trap removed atsource. No hostnative entry aliases; trueexistingobjects+live bankexpressions linked.',
  own_C_mapping_contract='ThDispatch admits selected10/FmAlts40 exact and completebothcookies, establishesC2 before A3; selectedpayload callbacks returnC2. This requires actual caller closure before shared hook approval.',
  bindings={str(p):sha(p)for p in [Path(__file__),P/'source-stage.json',A/'source-stage.json',J/'candidate.nes',J/'candidate.cfg',J.parent/'final-link.json',R/'tools/reference/thomas_resident_1031_v3.s',R/'tools/reference/thomas_cache_host_1031_v3.s',R/'tools/audit/private_build_outputs_v1.py']+inputs+[p for p in O.rglob('*')if p.is_file()]}))
 print(json.dumps(dict(result='SOURCE_LINKED',ROM=sha(O/'candidate.nes'),kernel=s['ThAllKernelEnd']-0xa000,resident=s['ThAllResidentEnd']-0xb33a,pages=len(carrier)//1024,stage=sha(O/'source-stage.json'))))
if __name__=='__main__':main()
