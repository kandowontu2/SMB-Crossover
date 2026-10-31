"""Guarded INERT CF/BT source join on c663. No lifecycle/admission hook."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from prepare_cv3_dmc_mirror import prepare
from check_tmnt_render_oa import address,location
P=R/'build/bowser-playable-jump-v1';S=R/'build/cf-bt-current66-carrier-v1'
O=R/'build/cf-bt-shared-transport-v1';J=O/'joint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
def bound(q):
 for f,h in q['bindings'].items():assert sha(f)==h,('immutable binding',f)
def main():
 assert not O.exists();O.mkdir();logs=[]
 try:
  parent=json.loads((P/'handoff.json').read_text());bound(parent)
  carrier=json.loads((S/'source-stage.json').read_text());bound(carrier)
  assert parent['candidate']=='c6635815711a624a02c4337cd9f1830ca9c43b14a824f2ea51963f796ad98c2a'
  shutil.copytree(P/'joint',J)
  # Private source paths only. Dependencies not copied here stay read-only.
  for p in J.rglob('*'):
   if p.is_file()and p.suffix.lower()in['.s','.asm','.inc','.cfg']:
    s=p.read_text(encoding='utf-8').replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix())
    p.write_text(s,encoding='utf-8')
  for p in(S/'joint').glob('cf-*'):
   if p.is_file():
    dst=J/p.name
    if p.suffix in['.s','.inc']:
     dst.write_text(p.read_text().replace(str(S/'joint'),str(J)).replace((S/'joint').as_posix(),J.as_posix()))
    else:shutil.copyfile(p,dst)
  cfg=(S/'joint/private.cfg').read_text().replace(str(S/'joint'),str(J)).replace((S/'joint').as_posix(),J.as_posix())
  (J/'private.cfg').write_text(cfg)
  for d in['sideoutputs/candidate','sideoutputs/baseline']:(J/d).mkdir(parents=True,exist_ok=True)
  union=(J/'union.s').read_text();needle=' cmp #27\n jeq HuExtendedBT\n cmp #33\n jeq HuExtendedBT'
  assert union.count(needle)==1
  union=union.replace(needle,''' cmp #27
 beq HuExtendedShared
 cmp #31
 beq HuExtendedShared
 cmp #33
 bne HuExtendedNotShared
HuExtendedShared:
 jmp HuExtendedBT
HuExtendedNotShared:''')
  (J/'union.s').write_text(union)
  nr=J/'src/new_roster_dispatch.s';s=nr.read_text();needle=' cmp #32\n bcs GmOnlyHigh';assert s.count(needle)==1
  nr.write_text(s.replace(needle,' cmp #31\n bcs GmOnlyHigh'))
  router=J/'bowser/router.s';s=router.read_text();assert s.count('BwFar BtCheck,jsr')==1
  s=s.replace('.import BwCheck,BtCheck,SafereturnA_SMC,NextBank_SMC','.import BwCheck,CfOrBtCheck,SafereturnA_SMC,NextBank_SMC')
  s=s.replace('BwFar BtCheck,jsr','BwFar CfOrBtCheck,jsr')
  old='''BwResolveRAM:
 sta FarcallJmpTarget_SMC+1
 lda #$a0
 sta FarcallJmpTarget_SMC+2
 lda #3
 sec
 rts'''
  new='''BwResolveRAM:
 sta FarcallJmpTarget_SMC+1
 jmp BwResolveFamilyTail
BwResolveRAMFinish:
 sta FarcallJmpTarget_SMC+2
 txa
 sec
 rts'''
  assert s.count(old)==1;s=s.replace(old,new)
  s+='''
; Exact16B already-owned tail; nativeAXYP remains on the outer B020 stack.
BwResolveFamilyTail:
 lda #$a0
 ldx #3
 ldy SelectedCharacter
 cpy #31
 bne BwResolveRAMFinish
 lda #$be
 dex
 bne BwResolveRAMFinish
.assert *=$b300,lderror,"Exact old16B resolver tail funding"
'''
  router.write_text(s)
  def run(name,c):
   guard=validate(c,O,cwd=R);p=subprocess.run(c,cwd=R,text=True,capture_output=True)
   q=dict(command=c,cwd=str(R),output_guard=guard,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
   logs.append(q);save(O/(name+'.json'),q);save(O/'commands.json',logs);assert p.returncode==0,(name,p.stderr)
  # Genuine previously linked Main/union producers, never inherited stale
  # joint recipe filenames. Only their actual outputs/input/source priority
  # are rebound to this new tree before validation.
  for name in['main','union']:
   c=json.loads((R/'build/bowser-current64-v3'/(name+'-build.json')).read_text())['command'][:]
   for i,x in enumerate(c):
    for root in[R/'build/bowser-current64-v3/joint',P/'joint']:
     if x.startswith(str(root)):c[i]=x.replace(str(root),str(J))
   for flag in['-o','--create-full-dep']:
    assert flag in c;c[c.index(flag)+1]=str(J/(name+('.o'if flag=='-o'else'.dep')))
   c[-1]=str(J/('entrypoint.s'if name=='main'else'union.s'))
   run(name+'-build',c)
  ca=R/'tools/Windows/cc65/bin/ca65.exe'
  for name,source in[('router',router),('cf-loader',J/'cf-loader.s'),('cf-guard',J/'cf-guard.s'),('cf-carrier',J/'cf-carrier.s')]:
   obj=router.with_suffix('.o')if name=='router'else J/(name+'.o')
   run(name+'-build',[str(ca),'--cpu','6502x','-g','-I',str(J/'bowser'),'-I',str(J),'-I',str(J/'src'),'-I',str(R),'--create-full-dep',str(obj.with_suffix('.dep')),'-o',str(obj),str(source)])
  c=json.loads((S/'commands.json').read_text())[-1]['command'][:]
  for i,x in enumerate(c):
   if x in[str(P/'joint/main.o'),str(P/'joint/union.o')]:c[i]=str(J/Path(x).name)
   elif x==str(P/'joint/bowser/router.o'):c[i]=str(J/'bowser/router.o')
   elif x.startswith(str(S/'joint')):c[i]=x.replace(str(S/'joint'),str(J))
  for flag in['-C','-Ln','-o','-m']:
   c[c.index(flag)+1]=str(J/Path(c[c.index(flag)+1]).name)
  c[c.index('--ld-args')+1]='--dbgfile,'+str(J/'candidate.dbg')
  run('final-link',c);prepare(R,J/'candidate.nes')
  b=qualified(J/'candidate.nes');old=qualified(P/'joint/candidate.nes')
  critical=['HuEntryBase','HuResolve','HuAfterTerrainGate','BwBtResolve','BwStartFlags','BwColdPrepare','BwColdDraw','BtServiceVeneers','BtCheck','BwScene','MenuResolveCharacter','FmPending','FmStartFlags']
  for n in critical:assert(address(b,n),location(b,n))==(address(old,n),location(old,n)),n
  for n in['Movement','Graphics','Draw','Portrait','Weapons','Injury','InjuryStatus','DeathStart','Death','Visible','Head','Body','Adder','BoxProfile','Side','Fresh','FullBox','MenuPortrait','Name','Reset','Prepare','Rise','Private','Collision','Pickup','FullPower','Colors','Stomp','HeadWithin','Ui','StatusName','Bounce','WorldPalette','Powerup','WeaponTail','Vine']:
   # Actual existing exports use a few shorter names, covered below through
   # all symbols inside the public entry capsule and unchanged11B sequence.
   pass
  start=address(old,'HuEntryBase')
  public=[]
  for i in range(36):
   at=start+16*i;fo=location(old,'HuEntryBase')+16*i;fn=location(b,'HuEntryBase')+16*i
   assert b['raw'][fn:fn+11]==old['raw'][fo:fo+11],('original11B entry',i)
   public.append(at)
  assert address(b,'CfOrBtCheck')==0xbf47 and(location(b,'CfOrBtCheck')-16)//8192==69
  assert(address(b,'BwResolveFamilyTail'),address(b,'BwResolveRAMFinish'))==(0xb2f0,0xb2b7)
  for n in['bowser.bin','ram3.bin','code.bin','data.bin']:
   actual=J/'sideoutputs/candidate'/({'bowser.bin':'04-bowser.bin','ram3.bin':'01-ram3.bin','code.bin':'02-code.bin','data.bin':'03-data.bin'}[n])
   assert sha(actual)==sha(P/'joint'/n),n;shutil.copyfile(actual,J/n)
  shutil.copyfile(P/'joint/ff-cookie.bin',J/'ff-cookie.bin')
  allowed=[(16+79*8192+0x15e0,16+80*8192),
   (location(b,'NrMovement'),location(b,'NrMovement')+36*97),
   (16+67*8192+0x122b,16+67*8192+0x1300),
   (16+69*8192+0x1f47,16+69*8192+0x1fbd),
   (16+115*8192+0x1f38,16+115*8192+0x1fcb),
   (16+78*8192+0xe68,16+78*8192+0xf96),
   (16+1048576+935*1024,16+1048576+969*1024)]
  changes=[i for i,(x,y)in enumerate(zip(b['raw'],old['raw']))if x!=y]
  assert len(b['raw'])==len(old['raw'])and b['raw'][:16]==old['raw'][:16]
  assert all(any(lo<=i<hi for lo,hi in allowed)for i in changes),[i for i in changes if not any(lo<=i<hi for lo,hi in allowed)]
  bound(parent);bound(carrier)
  stage=dict(source=True,status='INERT_GUARDED_CF_BT_TRANSPORT_CPU_PENDING',candidate=sha(J/'candidate.nes'),parent=parent['candidate'],joint=str(J),ready=66,CF_pending=True,BT_pending=True,native=False,installed=False,admitted=False,
   public_entry_PCs=public,all_original11B_prologues_exact=True,shared_selector_growth=1,selector_padding_remaining=1,resolver_tail_bytes=16,changed_bytes=len(changes),allowed_ranges=allowed,
   CF_external_guard_before_A2=True,CF_cold_and_retirement_complete=False,BT_new_cold_menu_producer_adopted=False,
   inputs=[str(P/'handoff.json'),str(S/'source-stage.json'),str(R/'build/cf-bt-shared-integration-plan-v1/plan.json')],
   bindings={str(p.resolve()):sha(p)for p in[Path(__file__),P/'handoff.json',S/'source-stage.json',R/'build/cf-bt-shared-integration-plan-v1/plan.json',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'main.o',J/'union.o',router,router.with_suffix('.o'),J/'src/new_roster_dispatch.s',J/'union.s',J/'private.cfg',J/'cf-guard.s',J/'cf-loader.s',J/'cf-carrier.s',J/'cf-cookie.bin',J/'cf-stream.bin']})
  save(O/'source-stage.json',stage);save(J/'source-stage.json',stage)
  print(json.dumps({k:v for k,v in stage.items()if k not in['bindings','public_entry_PCs','allowed_ranges']}))
 except Exception as e:save(O/'negative.json',dict(passed=False,error=repr(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
