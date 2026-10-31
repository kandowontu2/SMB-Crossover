"""Source-only CF lives delta correction on the exact coherent BT/CF cart."""
from pathlib import Path
import hashlib, json, re, subprocess, sys, traceback

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare

P=R/'build/bt-cf-coherent-source-1031-v1'
H=R/'docs/qa/checkpoints/2026-10-31/bt-cf-coherent-source-v1/handoff.json'
K=R/'build/contra-force-p1-kernel-v1'
C=R/'build/contra-force-p1-coherent-cart-v2'
O=R/'build/contra-force-lives-position-1031-v1'
J=O/'joint';N=O/'kernel'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def write(p,s):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def save(p,q):write(p,json.dumps(q,indent=2)+'\n')
def bound(p):
 q=json.loads(p.read_text())
 for f,h in q['bindings'].items():assert sha(f)==h,('Immutable input changed',f)
 return q
def run(name,cmd,cwd):
 guard=validate(cmd,O,cwd=cwd)
 for output in guard['outputs']:Path(output['path']).parent.mkdir(parents=True,exist_ok=True)
 z=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True)
 save(O/(name+'.json'),dict(command=cmd,cwd=str(cwd),output_guard=guard,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr))
 assert z.returncode==0,(name,z.stderr)
def labels(p):return{n:int(v,16)for v,n in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',p.read_text())}

def main():
 assert not O.exists();O.mkdir();J.mkdir();N.mkdir()
 try:
  parent=bound(H);ks=bound(K/'build-proof.json');bound(P/'source-stage.json')
  assert parent['candidate']==sha(P/'joint/candidate.nes')=='e538d2b809b1dac9b70a0a1b23a1b33b3d361297b25fac0b556d8eae5c7721ed'
  oldlogs=json.loads((K/'build-log.json').read_text())
  ca=next(q['command']for q in oldlogs if q['command'][-1]==str(K/'render.s'))
  old=(K/'render.s').read_text();a='adc #56                     ; body center beside native lives x3, below WORLD'
  assert old.count(a)==1
  write(N/'render.s',old.replace(a,'adc #0                      ; native PlayerY88 + original body center16 aligns lives x3'))
  # All genuine unmodified component objects remain immutable inputs.
  cmd=ca[:]
  for flag,path in [('--create-full-dep',N/'render.dep'),('-o',N/'render.o')]:cmd[cmd.index(flag)+1]=str(path)
  cmd[-1]=str(N/'render.s');run('kernel-render-build',cmd,N)
  write(N/'runtime.cfg',(K/'runtime.cfg').read_text())
  cmd=oldlogs[-1]['command'][:]
  for flag,path in [('-C',N/'runtime.cfg'),('-o',N/'unused.bin'),('--dbgfile',N/'runtime.dbg'),('-Ln',N/'runtime.lbl'),('-m',N/'runtime.map')]:cmd[cmd.index(flag)+1]=str(path)
  cmd=[str(N/'render.o')if x==str(K/'render.o')else x for x in cmd]
  run('kernel-link',cmd,N)
  assert labels(N/'runtime.lbl')==labels(K/'runtime.lbl'),'Private source PCs moved'
  assert (N/'ram1.bin').read_bytes()==(K/'ram1.bin').read_bytes()
  assert (N/'ram2.bin').read_bytes()==(K/'ram2.bin').read_bytes()
  before=(K/'ram3.bin').read_bytes();after=(N/'ram3.bin').read_bytes()
  diffs=[i for i,(x,y)in enumerate(zip(before,after))if x!=y]
  assert len(diffs)==1 and before[diffs[0]]==56 and after[diffs[0]]==0
  assert before[diffs[0]-1]==0x69
  images=[]
  for i in(1,2,3):
   data=bytearray((N/f'ram{i}.bin').read_bytes());data.extend(bytes(8192-len(data)))
   if i in(2,3):data[0x1fe0:]=bytes(32)
   images.append(data)
  stream=b''.join(images);cookie=bytes([167,31,0,2])+hashlib.sha256(stream).digest()[:12]
  (J/'cf-stream.bin').write_bytes(stream);(J/'cf-cookie.bin').write_bytes(cookie)
  for name in('cf-loader','cf-guard','cf-carrier'):
   text=(C/'joint'/f'{name}.s').read_text()
   text=re.sub(r'\.incbin\s+"[^\"]*cf-cookie\.bin"',lambda m:'.incbin "'+(J/'cf-cookie.bin').as_posix()+'"',text)
   text=re.sub(r'\.incbin\s+"[^\"]*cf-stream\.bin"',lambda m:'.incbin "'+(J/'cf-stream.bin').as_posix()+'"',text)
   write(J/f'{name}.s',text)
   oldcmd=json.loads((C/f'{name}-build.json').read_text())['command']
   cmd=oldcmd[:]
   for flag,path in [('--create-full-dep',J/f'{name}.dep'),('-o',J/f'{name}.o')]:cmd[cmd.index(flag)+1]=str(path)
   cmd[-1]=str(J/f'{name}.s');run(name+'-build',cmd,R)
  cfg=(P/'joint/candidate.cfg').read_text()
  # Retarget every actual side-output, leaving all native MEMORY geometry exact.
  cfg=re.sub(r'file="([^\"]+)"',lambda m:'file="'+(J/'sideoutputs'/Path(m[1]).name).as_posix()+'"',cfg)
  write(J/'candidate.cfg',cfg)
  cmd=json.loads((P/'final-link.json').read_text())['command'][:]
  for flag,path in [('-C',J/'candidate.cfg'),('-Ln',J/'candidate.lbl'),('-o',J/'candidate.nes')]:cmd[cmd.index(flag)+1]=str(path)
  cmd[cmd.index('--ld-args')+1]='--dbgfile,'+str(J/'candidate.dbg')
  for i,x in enumerate(cmd):
   if Path(x).suffix.lower()=='.o'and Path(x).name in('cf-loader.o','cf-guard.o','cf-carrier.o'):cmd[i]=str(J/Path(x).name)
  run('final-link',cmd,R);prepare(R,J/'candidate.nes')
  b=qualified(P/'joint/candidate.nes');n=qualified(J/'candidate.nes');raw=n['raw'];base=b['raw'];oracle=bytearray(base)
  # Verification only: product above was assembled/linked from genuine sources.
  cs=16+128*8192+935*1024;oracle[cs:cs+24576]=stream
  for name in('CfExternalCookie','CfLoaderExpectedCookie'):
   p=location(b,name);oracle[p:p+16]=cookie
  assert raw==oracle,'Source output differs from the exact own byte oracle'
  public=[]
  for name,s in b['syms'].items():
   if s.get('type')=='lab'and 'seg'in s and name in n['syms']:
    assert(address(b,name),location(b,name))==(address(n,name),location(n,name)),name
    public.append(name)
  assert raw[:16]==base[:16]
  # Only the owned carrier changed in CHR; native body/menu/art remain exact.
  assert raw[16+128*8192:cs]==base[16+128*8192:cs]and raw[cs+24576:]==base[cs+24576:]
  paths=[Path(__file__),H,P/'source-stage.json',P/'final-link.json',K/'build-proof.json',K/'build-log.json',K/'render.s',K/'runtime.cfg',K/'runtime.lbl',
         J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'candidate.cfg',*[p for p in N.iterdir()if p.is_file()],
         *[p for p in J.iterdir()if p.is_file()and p.name.startswith('cf-')],*O.glob('*-build.json'),O/'kernel-link.json',O/'final-link.json']
  stage=dict(passed=True,source=True,native=False,installed=False,parent=sha(P/'joint/candidate.nes'),candidate=sha(J/'candidate.nes'),
             only_semantic_change='CfHostPortrait lives-only ADC #56 -> #0; original source +16 center retained',
             payload_difference=dict(bank=3,offset=diffs[0],before=56,after=0),cookie=cookie.hex(),source_byte_oracle_equal=True,
             all_matched_public_PC_locations_exact=len(public),all_menu_BT_M3_shared59_restore67_gameplay_bytes_exact=True,
             bindings={str(p.resolve()):sha(p)for p in paths})
  save(O/'source-stage.json',stage)
  print(json.dumps(dict(candidate=stage['candidate'],cookie=cookie.hex(),payload_diff=stage['payload_difference'],stage=str(O/'source-stage.json'),sha256=sha(O/'source-stage.json'))),flush=True)
 except Exception as e:
  save(O/'negative.json',dict(passed=False,error=repr(e),traceback=traceback.format_exc()));raise

if __name__=='__main__':main()
