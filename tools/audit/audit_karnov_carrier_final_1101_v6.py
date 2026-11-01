"""Current-image compiled CHR ownership and publication closure audit."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys,zipfile

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from private_build_outputs_v1 import validate
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
import check_hogan_current_bounded_v1 as Menu

P=R/'build/karnov-host-resource-base-1101-v1'
O=R/'build/karnov-carrier-final-1101-v6'
PIN='0162287ebf5b8fcb8a84dcf108a0d0930c4dc9d6e68928c4804bd774712e1a6c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')

def assemble(record_only=False):
 assert sha(P/'candidate.nes')==PIN
 cmd=json.loads((P/'terrain-main-build.json').read_text())['command'][:]
 for flag,name in[('-o','main.o'),('-l','main.lst'),('--create-full-dep','main.dep'),('--create-dep','main.dep')]:
  if flag in cmd:cmd[cmd.index(flag)+1]=str(O/name)
 if '-l' not in cmd:cmd[1:1]=['-l',str(O/'main.lst')]
 if not any(f in cmd for f in['--create-full-dep','--create-dep']):cmd[1:1]=['--create-full-dep',str(O/'main.dep')]
 if not record_only:
  guard=validate(cmd,O,cwd=R)
  run=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
  receipt=dict(command=cmd,guard=guard,returncode=run.returncode,stderr=run.stderr)
  save(O/'main-build.json',receipt);assert run.returncode==0,run.stderr
 old=(P/'main.o').read_bytes();new=(O/'main.o').read_bytes()
 # cc65 object17: the sole OPT_DATETIME LEB128 field follows translatorID.
 # No code, expression, relocation, symbol, line or source-file byte differs.
 assert old[96:100]==new[96:100]==bytes([2,2,34,64])
 diff=[i for i,(a,b)in enumerate(zip(old,new))if a!=b]
 same=len(old)==len(new)and old[:100]==new[:100]and old[105:]==new[105:]
 q=dict(passed=same,current_ROM_sha256=PIN,object_exact_except_OPT_DATETIME=same,
  datetime_field=[100,105],different_bytes=diff,
  source_object_sha256=sha(P/'main.o'),assembled_object_sha256=sha(O/'main.o'),
  listing_bytes=(O/'main.lst').stat().st_size,
  bindings={str(p.resolve()):sha(p)for p in[Path(__file__),P/'candidate.nes',P/'candidate.dbg',P/'main.o',P/'entrypoint.s',P/'terrain-main-build.json',O/'main.o',O/'main.lst',O/'main.dep',O/'main-build.json']})
 save(O/'main-reproduction.json',q)
 print(json.dumps({k:q[k]for k in['passed','object_exact_except_OPT_DATETIME','different_bytes','listing_bytes']}))
 assert same,'Current exact main source object did not reproduce'

def relink():
 assert sha(P/'candidate.nes')==PIN
 proof=json.loads((O/'main-reproduction.json').read_text());assert proof['passed']
 cfg=(P/'candidate.cfg').read_text();count=0
 def output(m):
  nonlocal count
  if m[1]in['','%O']:return m[0]
  count+=1
  return 'file="'+(O/'sideoutputs'/(str(count).zfill(3)+'-'+Path(m[1]).name)).as_posix()+'"'
 (O/'candidate.cfg').write_text(re.sub(r'file\s*=\s*"([^"\r\n]*)"',output,cfg),encoding='utf-8')
 cmd=json.loads((P/'terrain-final-link.json').read_text())['command'][:]
 cmd[cmd.index(str(P/'main.o'))]=str(O/'main.o')
 for flag,name in[('-C','candidate.cfg'),('-o','candidate.nes'),('-Ln','candidate.lbl'),('-m','candidate.map')]:
  cmd[cmd.index(flag)+1]=str(O/name)
 cmd[cmd.index('--ld-args')+1]='--dbgfile,'+str(O/'candidate-full.dbg')
 guard=validate(cmd,O,cwd=R)
 for z in guard['outputs']:Path(z['path']).parent.mkdir(parents=True,exist_ok=True)
 run=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
 save(O/'full-link.json',dict(command=cmd,guard=guard,returncode=run.returncode,stderr=run.stderr))
 assert run.returncode==0,run.stderr
 (O/'candidate-full.dbg').replace(O/'candidate.dbg')
 from prepare_cv3_dmc_mirror import prepare
 prepare(R,O/'candidate.nes')
 assert sha(O/'candidate.nes')==PIN,'Exact current candidate did not reproduce'
 files=[Path(p)for p in cmd if p.endswith('.o')]
 q=dict(passed=True,current_ROM_sha256=PIN,full_debug_bytes=(O/'candidate.dbg').stat().st_size,
  no_dependencies_copied=True,objects={p.as_posix():sha(p)for p in files},
  bindings={str(p.resolve()):sha(p)for p in[P/'candidate.nes',P/'candidate.dbg',P/'candidate.cfg',P/'terrain-final-link.json',O/'candidate.nes',O/'candidate.dbg',O/'candidate.cfg',O/'full-link.json',Path(__file__)]})
 save(O/'current-reproduction.json',q)
 print(json.dumps({k:q[k]for k in['passed','current_ROM_sha256','full_debug_bytes']}))

def compiled_census():
 assert sha(O/'candidate.nes')==PIN
 b=scoped_load(O/'candidate.nes');spans={};files={};lines=[]
 for line in (O/'candidate.dbg').read_text().splitlines():
  kind,_,tail=line.partition('\t')
  if kind not in['span','file','line']:continue
  q=dict(re.findall(r'(\w+)=("[^"\n]*"|[^,\n]+)',tail))
  if kind=='span':spans[q['id']]=q
  elif kind=='file':files[q['id']]=q
  elif 'span'in q:lines.append(q)
 memory={};wanted={};storeops={0x8d:'STA',0x9d:'STA',0x99:'STA',0x8e:'STX',0x8c:'STY',0xee:'INC',0xfe:'INC',0xce:'DEC',0xde:'DEC',0x0e:'ASL',0x1e:'ASL',0x4e:'LSR',0x5e:'LSR',0x2e:'ROL',0x3e:'ROL',0x6e:'ROR',0x7e:'ROR'}
 ranges=[('ordinary',address(b,'CurrentCHRBank'),12),('modes',address(b,'X5ChrMode'),16),('body_alias',address(b,'SmChrBank'),1),('special_low',address(b,'SsChrPhysical'),1),('HUD_low',address(b,'InvHudPhysical'),1),('hardware',0x5120,12),('upper_latch',0x5130,1)]
 for key,q in spans.items():
  size=int(q['size'],0);g=b['segs'][q['seg']]
  if size not in[2,3]or'ooffs'not in g or int(g['start'],0)>=65536:continue
  name=Path(g['oname'].strip('"'))
  if name not in memory:memory[name]=name.read_bytes()
  at=int(g['ooffs'],0)+int(q['start'],0);code=memory[name][at:at+size]
  if len(code)!=size:continue
  if size==2 and code[0]in[0x81,0x91]:
   wanted[key]=dict(op='STA',kind='indirect',operand=code[1],ranges=[])
  elif size==3 and code[0]in storeops:
   target=code[1]+256*code[2];high=target+(255 if code[0]in[0x9d,0x99,0xfe,0xde,0x1e,0x5e,0x3e,0x7e] else 0)
   hit=[n for n,lo,sz in ranges if target<lo+sz and high>=lo]
   if not hit:continue
   wanted[key]=dict(op=storeops[code[0]],kind='absolute_indexed'if high!=target else'absolute',operand=target,ranges=hit)
  else:continue
  wanted[key].update(segment=g['name'].strip('"'),offset=int(q['start'],0),PC=int(g['start'],0)+int(q['start'],0),bytes=code.hex(),source=[])
 for line in lines:
  for key in line['span'].split('+'):
   if key in wanted:wanted[key]['source'].append((line['file'],int(line['line'])))
 archive=zipfile.ZipFile(R/'build/_recovery/legacy-sources-2026-10-31.zip')
 index={q['path']:q for q in json.loads(archive.read('index.json'))};sourcecache={};sourcebindings={}
 def source(fid):
  ref=files[fid];path=Path(ref['name'].strip('"'))
  if path not in sourcecache:
   if path.is_file():data=path.read_bytes();origin='current-live'
   else:
    assert path.is_relative_to(R/'build'),path
    row=index[path.relative_to(R/'build').as_posix()];data=archive.read('objects/'+row['sha256']);origin='indexed-recovery'
    assert hashlib.sha256(data).hexdigest()==row['sha256']
   assert len(data)==int(ref['size']),(path,len(data),ref['size'])
   sourcecache[path]=data.decode('utf-8',errors='replace').splitlines()
   sourcebindings[path.as_posix()]=dict(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),origin=origin)
  return path,sourcecache[path]
 instructions=[];data=[];unclassified=[]
 for q in wanted.values():
  witnesses=[];other=[]
  for fid,n in q.pop('source'):
   path,text=source(fid)
   if not 1<=n<=len(text):continue
   line=text[n-1].split(';',1)[0].strip()
   row=dict(path=path.as_posix(),line=n,text=line,clause='\n'.join(text[max(0,n-7):min(len(text),n+3)]))
   if re.match(r'(?:(?:[\w@]+|::[\w@]+)?:\s*)?'+q['op']+r'\b',line,re.I):witnesses.append(row)
   else:other.append(row)
  if witnesses:q['witnesses']=witnesses;instructions.append(q)
  elif other and all(not re.search(r'\b(?:sta|stx|sty|inc|dec|asl|lsr|rol|ror)\b',x['text'],re.I)for x in other):
   q['witnesses']=other;data.append(q)
  else:q['witnesses']=other;unclassified.append(q)
 result=dict(passed=not unclassified,current_ROM_sha256=PIN,spans=len(spans),source_instruction_writer_spans=len(instructions),
  source_data_false_opcode_spans=len(data),unclassified=unclassified,writers=instructions,data_false_opcodes=data,source_bindings=sourcebindings,
  ranges=[dict(name=n,start=a,bytes=z)for n,a,z in ranges],
  bindings={str(p.resolve()):sha(p)for p in[Path(__file__),O/'candidate.nes',O/'candidate.dbg',O/'current-reproduction.json']})
 save(O/'compiled-writers.json',result)
 print(json.dumps(dict(passed=result['passed'],writer_spans=len(instructions),indirect=sum(q['kind']=='indirect'for q in instructions),data_false_opcodes=len(data),unclassified=len(unclassified))))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--assemble',action='store_true');ap.add_argument('--record-only',action='store_true');ap.add_argument('--relink',action='store_true');ap.add_argument('--census',action='store_true');a=ap.parse_args()
 O.mkdir(exist_ok=True)
 if a.assemble or a.record_only:assemble(a.record_only)
 if a.relink:relink()
 if a.census:compiled_census()

if __name__=='__main__':main()
