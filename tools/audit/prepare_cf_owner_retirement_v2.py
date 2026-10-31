"""Current66 owner-boundary CF retirement, before menu publish/scene writes."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load,address,location
from prepare_cv3_dmc_mirror import prepare
P=R/'build/cf-bt-shared-transport-v3';O=R/'build/cf-owner-retirement-v2';J=O/'joint'
L=R/'build/contra-force-checkpoint-loader-cart-v1/joint'
H=R/'build/contra-force-checkpoint-loader-qualified-v1/handoff.json'
RH=R/'build/contra-force-retire-qualified-v1/handoff.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n')
def bound(q):
 for f,h in q['bindings'].items():assert sha(f)==h,('immutable predecessor',f)
def main():
 assert not O.exists();O.mkdir();logs=[]
 try:
  parent=json.loads((P/'handoff.json').read_text());bound(parent)
  for p in[H,RH]:bound(json.loads(p.read_text()))
  shutil.copytree(P/'joint',J)
  for p in J.rglob('*'):
   if p.is_file()and p.suffix.lower()in['.s','.asm','.inc','.cfg']:
    p.write_text(p.read_text().replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix()))
  p=J/'cf-loader.s';s=(L/'cf-loader.s').read_text().replace(str(L),str(J)).replace(L.as_posix(),J.as_posix());p.write_text(s)
  p=J/'cf-retire.s';p.write_bytes((R/'tools/reference/contra_force_retire_proposal_v2.s').read_bytes())
  cfg=(J/'private.cfg').read_text();old='CF_GUARD_POST:start=$bfbd,size=$43,type=ro,file=%O,fill=yes,fillval=$ff,bank=$45;'
  new='CF_RETIRE_MEM:start=$bfbd,size=$24,type=ro,file=%O,fill=yes,fillval=$ff,bank=$45;\n CF_GUARD_POST:start=$bfe1,size=$1f,type=ro,file=%O,fill=yes,fillval=$ff,bank=$45;'
  assert cfg.count(old)==1;cfg=cfg.replace(old,new).replace('CF_ROM_GUARD:load=CF_GUARD_MEM,type=ro;','CF_ROM_GUARD:load=CF_GUARD_MEM,type=ro;\n CF_RETIRE_PROPOSAL:load=CF_RETIRE_MEM,type=ro;');(J/'private.cfg').write_text(cfg)
  p=J/'src/character_select.s';s=p.read_text();s='.import CfRetire\n'+s
  old='  farcall BwMenuResolve,jmp\n  .res 16,$ea'
  new='''  ; Retire CF before Fm/Cm can publish the next owner. CfRetire preserves
  ; sourceA and has no inner SFC, so reuse the first call's saved sourceA.
  farcall CfRetire
  lda #<BwMenuResolve
  sta FarcallJmpTarget_SMC+1
  lda #>BwMenuResolve
  sta FarcallJmpTarget_SMC+2
  lda #.lobyte(.bank(BwMenuResolve)|$80)
  jmp FarCallCommon
  .res 1,$ea'''
  assert s.count(old)==1;p.write_text(s.replace(old,new))
  p=J/'bowser/cold.s';s=p.read_text();s='.import CfRetire\n'+s
  old='BwScene:\n BwFar S2InitScreenPrepare,jsr'
  new='''BwScene:
 ; Sole production ingress is the genuine InitScreen SFC. Its nativeA is
 ; already in SafecallA; retire before S2/Qw/Ar/Fw can overwrite any bank.
 lda #<CfRetire
 sta FarcallJmpTarget_SMC+1
 lda #>CfRetire
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(CfRetire)|$80)
 jsr FarCallCommon
 jsr BwSceneNativePrepared'''
  assert s.count(old)==1;s=s.replace(old,new)
  old='.assert *<=$b400,lderror,"A88 actual name-patch+late lives budget"'
  new='''; Existing15B own tail. The original nativeA remains SFC-saved because
; CfRetire preservesA/SMC; reuse the callerJSR frame for the original child.
BwSceneNativePrepared:
 lda #<S2InitScreenPrepare
 sta FarcallJmpTarget_SMC+1
 lda #>S2InitScreenPrepare
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(S2InitScreenPrepare)|$80)
 jmp FarCallCommon
.assert *=$b400,lderror,"Exact A88 existing15B tail funding"'''
  assert s.count(old)==1;p.write_text(s.replace(old,new))
  # BwStatusName/BwColors are untouched. The rejected AXY-preservation
  # assumption is not used for funding; every old label/byte remains fixed.
  def run(name,c):
   guard=validate(c,O,cwd=R);p=subprocess.run(c,cwd=R,text=True,capture_output=True)
   q=dict(command=c,cwd=str(R),output_guard=guard,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
   logs.append(q);save(O/(name+'.json'),q);save(O/'commands.json',logs);assert p.returncode==0,(name,p.stderr)
  c=json.loads((P/'main-build.json').read_text())['command'][:]
  for i,x in enumerate(c):
   if x.startswith(str(P/'joint')):c[i]=x.replace(str(P/'joint'),str(J))
  c[c.index('-o')+1]=str(J/'main.o');c[c.index('--create-full-dep')+1]=str(J/'main.dep');c[-1]=str(J/'entrypoint.s')
  run('main-build',c)
  ca=R/'tools/Windows/cc65/bin/ca65.exe'
  for name,p in[('cold',J/'bowser/cold.s'),('cf-loader',J/'cf-loader.s'),('cf-retire',J/'cf-retire.s')]:
   obj=p.with_suffix('.o');run(name+'-build',[str(ca),'--cpu','6502x','-g','-I',str(J/'bowser'),'-I',str(J),'-I',str(J/'src'),'-I',str(R),'--create-full-dep',str(obj.with_suffix('.dep')),'-o',str(obj),str(p)])
  c=json.loads((P/'final-link.json').read_text())['command'][:]
  for i,x in enumerate(c):
   if x in[str(P/'joint/main.o'),str(P/'joint/cf-loader.o')]:c[i]=str(J/Path(x).name)
   elif Path(x).name=='cold.o'and Path(x).parent.name=='bowser':
    assert parent['bindings'].get(str(Path(x).resolve()))==sha(x),('actual linked cold producer',x)
    c[i]=str(J/'bowser/cold.o')
  c.append(str(J/'cf-retire.o'))
  for flag in['-C','-Ln','-o','-m']:c[c.index(flag)+1]=str(J/Path(c[c.index(flag)+1]).name)
  c[c.index('--ld-args')+1]='--dbgfile,'+str(J/'candidate.dbg')
  run('final-link',c);prepare(R,J/'candidate.nes')
  b,old=load(J/'candidate.nes'),load(P/'joint/candidate.nes')
  for n in['MenuResolveCharacter','QueueSelection','DrawSelectionPreview','BwScene','BwStatusName','BwColdPrepare','BwColdDraw','BwBtResolve','BwStartFlags','HuResolve','HuEntryBase','CfLoaderProposal','CfLoaderCoreProposal','CfLoaderExpectedCookie','CfOrBtCheck']:
   assert(address(b,n),location(b,n))==(address(old,n),location(old,n)),n
  assert(address(b,'CfRetire'),address(b,'BwSceneNativePrepared'))==(0xbfbd,0xb3f1)
  assert b['raw'][location(b,'BwStatusName'):location(b,'BwSceneNativePrepared')]==old['raw'][location(old,'BwStatusName'):16+88*8192+0x13f1]
  for n in['bowser.bin','ram3.bin','code.bin','data.bin']:
   p=J/'sideoutputs/candidate'/({'bowser.bin':'04-bowser.bin','ram3.bin':'01-ram3.bin','code.bin':'02-code.bin','data.bin':'03-data.bin'}[n])
   assert sha(p)==sha(P/'joint'/n);shutil.copyfile(p,J/n)
  for n in['ff-cookie.bin','cf-cookie.bin','cf-stream.bin']:assert sha(J/n)==sha(P/'joint'/n),n
  allowed=[(location(b,'MenuResolveCharacter'),location(b,'MenuResolveCharacter')+34),
   (16+88*8192+0x1334,16+88*8192+0x1400),
   (16+69*8192+0x1fbd,16+69*8192+0x1fe1),
   (16+78*8192+0xe68,16+78*8192+0xf96)]
  delta=[i for i,(a,z)in enumerate(zip(old['raw'],b['raw']))if a!=z]
  assert all(any(lo<=i<hi for lo,hi in allowed)for i in delta)
  bound(parent)
  stage=dict(source=True,status='OWNER_RETIREMENT_SOURCE_TARGETED_CONTROLS_PENDING',candidate=sha(J/'candidate.nes'),parent=parent['candidate'],joint=str(J),ready=66,CF_pending=True,BT_pending=True,native=False,installed=False,admitted=False,
   changed_bytes=len(delta),allowed_ranges=allowed,all_publicPCs_preserved=True,menu_bytes=34,scene_A88_used=204,scene_A88_granted=204,
   CfRetire_before_scene_inner_FF_BW_writes=True,actual_coverage_proof_pending=True,CF_cold_graphics_palette_runtime_complete=False,
   bindings={str(p.resolve()):sha(p)for p in[Path(__file__),P/'handoff.json',H,RH,J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'private.cfg',J/'src/character_select.s',J/'bowser/cold.s',J/'cf-loader.s',J/'cf-retire.s',J/'main.o',J/'bowser/cold.o',J/'cf-loader.o',J/'cf-retire.o']})
  save(O/'source-stage.json',stage);save(J/'source-stage.json',stage)
  print(json.dumps({k:v for k,v in stage.items()if k not in['bindings','allowed_ranges']}))
 except Exception as e:save(O/'negative.json',dict(passed=False,error=repr(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
