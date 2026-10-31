"""Source-linked PRIVATE experimental CF P1 kernel + exact59B native-first hook."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare
P=R/'build/cf-cold-warm-palette-source-v1';K=R/'build/contra-force-p1-kernel-v1';O=R/'build/contra-force-p1-cart-v2';J=O/'joint'
G=R/'docs/qa/checkpoints/2026-10-31/contra-force-p1-experimental-resources/root-review-and-reservations.json';A=G.with_name('native-first-amendment-v2.json')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n')
def bound(p):
 d=json.loads(Path(p).read_text())
 for f,h in d['bindings'].items():assert sha(f)==h,f
 return d
def main():
 assert not O.exists();J.mkdir(parents=True);logs=[]
 try:
  parent=bound(P/'handoff.json');kernel=bound(K/'build-proof.json');bound(G);bound(A)
  assert parent['candidate']=='ef2f11e232ec878c277245c3802bcf8a415415e38507c26feefaef3744c1bee1'
  recipe=json.loads((P/'final-link.json').read_text())['command'];objs=[v for v in recipe if Path(v).suffix=='.o']
  for f in objs:assert parent['bindings'].get(str(Path(f).resolve()))==sha(f),f
  def cfg(name):
   s=(P/'joint/private.cfg').read_text();i=0
   def replace(m):
    nonlocal i
    if m[1]in['','%O']:return m[0]
    z=J/'sideoutputs'/name/('%02d-'%i+Path(m[1]).name);i+=1;z.parent.mkdir(parents=True,exist_ok=True);return 'file="'+z.as_posix()+'"'
   return re.sub(r'file\s*=\s*"([^"]*)"',replace,s)
  def run(name,cmd):
   g=validate(cmd,O,cwd=R);z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);q=dict(command=cmd,cwd=str(R),output_guard=g,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr);logs.append(q);save(O/(name+'.json'),q);save(O/'commands.json',logs);assert z.returncode==0,(name,z.stderr)
  def link(name,objects):
   p=J/(name+'.cfg');p.write_text(cfg(name));cmd=recipe[:]
   for flag,value in [('-C',p),('-Ln',J/(name+'.lbl')),('-o',J/(name+'.nes')),('-m',J/(name+'.map'))]:cmd[cmd.index(flag)+1]=str(value)
   cmd[cmd.index('--ld-args')+1]='--dbgfile,'+str(J/(name+'.dbg'));cmd=[objects.get(x,x)for x in cmd];run(name+'-link',cmd);prepare(R,J/(name+'.nes'))
  link('baseline',{});assert sha(J/'baseline.nes')==parent['candidate']
  payload=[]
  for i in [1,2,3]:
   b=bytearray((K/('ram%d.bin'%i)).read_bytes());b.extend([0]*(8192-len(b)));assert len(b)==8192
   if i in[2,3]:b[0x1fe0:]=bytes(32)
   (J/('cf-ram%d.bin'%i)).write_bytes(b);payload.append(b)
  data=b''.join(payload);(J/'cf-stream.bin').write_bytes(data);cookie=bytes([167,31,0,2])+hashlib.sha256(data).digest()[:12];(J/'cf-cookie.bin').write_bytes(cookie)
  for n in ['cf-loader','cf-guard','cf-retire']:
   text=(P/'joint'/(n+'.s')).read_text();text=text.replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix());(J/(n+'.s')).write_text(text)
  (J/'cf-carrier.s').write_text('.segment "CF_CARRIER"\n.incbin "'+(J/'cf-stream.bin').as_posix()+'"\n.segment "CF_BODY_CHR"\n.incbin "'+(R/'build/contra-force-body-pack-v3/atlas.chr').as_posix()+'"\n.segment "CF_SHOT_CHR"\n.incbin "'+(R/'build/contra-force-shot-pack-v1/atlas.chr').as_posix()+'"\n')
  # Exact consumed FF source, never a guessed source copy or binary overlay.
  loader_obj=next(Path(v)for v in objs if v.endswith('ff-lives-body-palette-v1\\joint\\loader.o'))
  pal_obj=next(Path(v)for v in objs if Path(v).name=='ff-palette.o')
  for obj in [loader_obj,pal_obj]:assert parent['bindings'][str(obj.with_suffix('.s').resolve())]==sha(obj.with_suffix('.s'))
  (J/'loader.s').write_bytes(loader_obj.with_suffix('.s').read_bytes());(J/'ff-cookie.bin').write_bytes((loader_obj.parent/'ff-cookie.bin').read_bytes())
  # Loader include directory contains all exact own FF interface includes.
  for n in ['ff-epoch-rom.inc']:
   old=(loader_obj.parent/n).read_text();needle='FfMuxRomNative:\n pla\n plp\n sta SafecallA_SMC+1';assert old.count(needle)==1
   (J/n).write_text(old.replace(needle,'FfMuxRomNative:\n pla\n plp\n.export FfMuxNativeTail\nFfMuxNativeTail:\n sta SafecallA_SMC+1'))
  old=pal_obj.with_suffix('.s').read_text();src=(R/'tools/reference/contra_force_p1_shared_factor_proposal_v3.s').read_text();body=src.split('CfSharedDrawSelect:\n',1)[1].split('CfSharedDrawSelectEnd:',1)[0]
  old=old.replace('.import FfMuxNativeROM','.import FfMuxNativeROM,FfMuxNativeTail,BtServiceVeneers')
  old,count=re.subn(r'\.proc FwNativeDrawAll\n[\s\S]*?\.endproc',lambda m:'.proc FwNativeDrawAll\n'+body+'.assert *-FwNativeDrawAll=59,error,"Approved59B native-first CFlate"\n.endproc',old,count=1);assert count==1
  (J/'ff-palette.s').write_text(old)
  ca=R/'tools/Windows/cc65/bin/ca65.exe';rebound={}
  for n in ['cf-loader','cf-guard','cf-retire','cf-carrier','loader','ff-palette']:
   cmd=[str(ca),'--cpu','6502x','-g','-I',str(J),'-I',str(loader_obj.parent),'-I',str(R),'--create-full-dep',str(J/(n+'.dep')),'-o',str(J/(n+'.o')),str(J/(n+'.s'))];run(n+'-build',cmd)
   old_obj=loader_obj if n=='loader'else pal_obj if n=='ff-palette'else next(Path(v)for v in objs if Path(v).name==n+'.o')
   rebound[str(old_obj)]=str(J/(n+'.o'))
  link('candidate',rebound)
  b=qualified(J/'candidate.nes');a=qualified(P/'joint/candidate.nes')
  assert address(b,'FwNativeDrawAll')==0xb3c5 and address(b,'FwNativeDrawAllEnd')==0xb400
  assert address(b,'FfMuxNativeTail')==address(a,'FfMuxRomNative')+2
  spans=[(location(b,'FwNativeDrawAll'),59),(location(b,'CfExternalCookie'),16),(location(b,'CfLoaderExpectedCookie'),16),(16+128*8192+935*1024,24*1024)]
  diff=[i for i,(x,y)in enumerate(zip(a['raw'],b['raw']))if x!=y];assert all(any(lo<=i<lo+n for lo,n in spans)for i in diff)
  assert b['raw'][:16]==a['raw'][:16]
  for n in ['CfOrBtCheck','CfLoaderProposal','CfRetire','BtServiceVeneers','FwLoad','FwMuxMenuResolve','FwSceneInit','MenuResolveCharacter','ArGenResolve','QwSceneInit','BwBtResolve']:
   assert address(a,n)==address(b,n),n
  bound(P/'handoff.json');bound(K/'build-proof.json');bound(G);bound(A)
  out=dict(passed=True,source=True,native=False,ready=False,admitted=False,parent=parent['candidate'],candidate=sha(J/'candidate.nes'),kernel=str(K),cookie=cookie.hex(),changed_bytes=len(diff),allowed_changed_envelopes=spans,
   shared59_native_first_late_only=True,zero_byte_native_tail_label=True,no_new_PRG_CHR_OAM=True,unqualified=['Actual nativeDraw and firstA2/auth/sourcegroups/PPU','StaleCFP1 hardware cleanup on invalidcookie','All lifecycle,callback6 phasebit,foreign66 andrealISR obligations'],
   bindings={**parent['bindings'],str((P/'handoff.json').resolve()):sha(P/'handoff.json'),str((K/'build-proof.json').resolve()):sha(K/'build-proof.json'),str(G.resolve()):sha(G),str(A.resolve()):sha(A),str(Path(__file__).resolve()):sha(__file__),**{str(p.resolve()):sha(p)for p in O.rglob('*')if p.is_file()}})
  save(O/'source-stage.json',out);print(json.dumps(dict(path=str(O/'source-stage.json'),sha256=sha(O/'source-stage.json'),candidate=out['candidate'],changed=len(diff))),flush=True)
 except Exception as e:save(O/'negative.json',dict(passed=False,error=repr(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
