"""Guarded pending CF cold/warm source join on frozen f523; no readiness."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare
P=R/'build/cf-owner-retirement-v2';O=R/'build/cf-cold-warm-source-v2';J=O/'joint'
G=R/'docs/qa/checkpoints/2026-10-31/contra-force-cold-warm-resources/root-review-and-reservations.json'
FIT=R/'build/cf-cold-existing-fit-proposal-v2';REVIEW=R/'build/battletoads-shared-owner-gate-review-v1/review.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n')
def bound(p):
 q=json.loads(Path(p).read_text())
 for f,h in q['bindings'].items():assert sha(f)==h,('frozen input',f)
 return q
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cf-handoff',required=True,type=Path);ap.add_argument('--cf-joint',required=True,type=Path);ap.add_argument('--extension-grant',required=True,type=Path);a=ap.parse_args()
 assert not O.exists();O.mkdir();logs=[]
 try:
  parent=bound(P/'handoff.json');own=bound(a.cf_handoff);grant=bound(G);extension=bound(a.extension_grant);fit=bound(FIT/'proposal.json');bound(REVIEW)
  assert sha(G)=='d5de8559aaf437ffa5be837013e26af841f6342ba6b14fc2236f2bbb3f7b42e5'
  assert sha(a.extension_grant)=='cf1c835e5955f0bda19513dcc93578bac3a0d0620ad7817db71f3a0346d5a413'
  assert parent['candidate']=='f5231061660c6b898554a86c429db8357bd80da71b8aa38525b09636a6eb8e5e'
  assert a.cf_joint.resolve()!=P.joinpath('joint').resolve()
  for n in['cf-loader.s','cf-guard.s','cf-carrier.s','cf-retire.s','cf-stream.bin','cf-cookie.bin']:
   assert own['bindings'].get(str((a.cf_joint/n).resolve()))==sha(a.cf_joint/n),('actual owned producer',n)
  shutil.copytree(P/'joint',J)
  for p in J.rglob('*'):
   if p.is_file()and p.suffix.lower()in['.s','.asm','.inc','.cfg']:
    p.write_text(p.read_text().replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix()))
  for n in['cf-loader.s','cf-guard.s','cf-carrier.s','cf-retire.s']:
   text=(a.cf_joint/n).read_text().replace(str(a.cf_joint),str(J)).replace(a.cf_joint.as_posix(),J.as_posix());(J/n).write_text(text)
  for n in['cf-stream.bin','cf-cookie.bin']:shutil.copyfile(a.cf_joint/n,J/n)
  (J/'cf-cold-warm.s').write_text((R/'tools/reference/cf_cold_warm_resource_proposal_v3.s').read_text().replace('; MEASUREMENT ONLY. Two currently ungranted spans; no host/cart allocation.','; Exact root-granted17+42B CF cold/warm adapters, source-linked here.')+'''
.assert .bank(CfSceneRetireForeign)=.bank(CfRetire),lderror,"Actual same-bank retire tail"
.assert .bank(CfLoadIfCold)=.bank(CfLoaderProposal),lderror,"Actual same-bank loader tail"
.assert CfSceneRetireForeign=$bfe1,lderror,"Granted17B start"
.assert CfLoadIfCold=$bfcb,lderror,"Granted42B helper start"
''')
  p=J/'private.cfg';s=p.read_text()
  old='CF_GUARD_POST:start=$bfe1,size=$1f,type=ro,file=%O,fill=yes,fillval=$ff,bank=$45;'
  new='CF_SCENE_RETIRE_MEM:start=$bfe1,size=$11,type=ro,file=%O,fill=yes,fillval=$ff,bank=$45;\n CF_GUARD_POST:start=$bff2,size=$e,type=ro,file=%O,fill=yes,fillval=$ff,bank=$45;'
  assert s.count(old)==1;s=s.replace(old,new)
  old='CF_BOOT_A_POST:start=$bfcb,size=$35,type=ro,file=%O,fill=yes,fillval=$ff,bank=$73;'
  new='CF_WARM_LOAD_MEM:start=$bfcb,size=$2a,type=ro,file=%O,fill=yes,fillval=$ff,bank=$73;\n CF_BOOT_A_POST:start=$bff5,size=$b,type=ro,file=%O,fill=yes,fillval=$ff,bank=$73;'
  assert s.count(old)==1;s=s.replace(old,new).replace('SEGMENTS {','SEGMENTS {\n CF_SCENE_RETIRE_PROPOSAL:load=CF_SCENE_RETIRE_MEM,type=ro;\n CF_WARM_LOAD_PROPOSAL:load=CF_WARM_LOAD_MEM,type=ro;');p.write_text(s)
  (J/'bowser/router.s').write_bytes((FIT/'joint/router.s').read_bytes());(J/'bt/router.s').write_bytes((FIT/'joint/bt-router.s').read_bytes())
  # One actual Main callsite, full51B original mask moved byte-equivalently.
  p=J/'entrypoint.s';s=p.read_text();assert s.count('.import BwScene,BwMenuResolve,BwStartFlags')==1;s=s.replace('.import BwScene,BwMenuResolve,BwStartFlags','.import BwScene,BwMenuResolve');p.write_text(s)
  p=J/'src/full_roster_menu.s';s=p.read_text();assert s.count('farcall BwStartFlags,jmp')==1;p.write_text(s.replace('farcall BwStartFlags,jmp','farcall FmStartIdentityFlags,jmp'))
  p=J/'src/cf_menu_body.inc';s=p.read_text();body=(FIT/'joint/start.s').read_text();body=body[body.index('FmStartIdentityFlags:'):]
  assert s.count('FmCfHelperEnd:')==1;p.write_text(s.replace('FmCfHelperEnd:',body+'\nFmCfHelperEnd:'))
  p=J/'bowser/cold.s';s=p.read_text();s=s.replace('.import CfRetire','.import CfSceneRetireForeign,BwCfSceneLoad,BtServiceVeneers')
  s=s.replace('#<CfRetire','#<CfSceneRetireForeign').replace('#>CfRetire','#>CfSceneRetireForeign').replace('.bank(CfRetire)','.bank(CfSceneRetireForeign)')
  old=''' lda SelectedCharacter
 cmp #27
 bne BwSceneDone
 BwFar BwLoad,jsr'''
  new=''' lda SelectedCharacter
 and #$fb                    ; exactly27/31, no other raw owner alias
 cmp #27
 bne BwSceneDone
 ; Private scene load consumes no nativeA argument. Original nativeAXYP
 ; is already saved above; reuse genuine SFC's saved sourceA here.
 lda #<BwCfSceneLoad
 sta FarcallJmpTarget_SMC+1
 lda #>BwCfSceneLoad
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(BwCfSceneLoad)|$80)
 jsr FarCallCommon
 nop                         ; +2 predicate, -3 redundant sourceA store
'''
  assert s.count(old)==1;s=s.replace(old,new)
  p.write_text(s)  # Original direct BwConstruct15B stays byteexact.
  def run(n,cmd):
   guard=validate(cmd,O,cwd=R);r=subprocess.run(cmd,cwd=R,capture_output=True,text=True);q=dict(command=cmd,cwd=str(R),output_guard=guard,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr);logs.append(q);save(O/(n+'.json'),q);save(O/'commands.json',logs);assert r.returncode==0,(n,r.stderr)
  cmd=json.loads((P/'main-build.json').read_text())['command'][:]
  for i,x in enumerate(cmd):
   if x.startswith(str(P/'joint')):cmd[i]=x.replace(str(P/'joint'),str(J))
  cmd[cmd.index('-o')+1]=str(J/'main.o');cmd[cmd.index('--create-full-dep')+1]=str(J/'main.dep');cmd[-1]=str(J/'entrypoint.s');run('main-build',cmd)
  ca=R/'tools/Windows/cc65/bin/ca65.exe'
  replacements={}
  for name,src in[('cold',J/'bowser/cold.s'),('bw-router',J/'bowser/router.s'),('bt-router',J/'bt/router.s'),*[(n,J/(n+'.s'))for n in['cf-loader','cf-guard','cf-carrier','cf-retire','cf-cold-warm']]]:
   obj=src.with_suffix('.o');run(name+'-build',[str(ca),'--cpu','6502x','-g','-I',str(J/'bowser'),'-I',str(J),'-I',str(J/'src'),'-I',str(R),'--create-full-dep',str(obj.with_suffix('.dep')),'-o',str(obj),str(src)]);replacements[(src.parent.name,src.stem)]=str(obj)
  cmd=json.loads((P/'final-link.json').read_text())['command'][:];counts={}
  for i,x in enumerate(cmd):
   path=Path(x)
   if path.suffix!='.o':continue
   key=(path.parent.name,path.stem)
   if path.stem=='main':cmd[i]=str(J/'main.o');continue
   match=None
   if path.parent.name in['bowser','bt']and key in replacements:match=replacements[key]
   elif path.stem in['cf-loader','cf-guard','cf-carrier','cf-retire']:match=str(J/(path.stem+'.o'))
   if match:assert parent['bindings'].get(str(path.resolve()))==sha(path),('actual linked object',path);cmd[i]=match;counts[match]=counts.get(match,0)+1
  assert all(counts.get(v)==1 for k,v in replacements.items()if k[1]!='cf-cold-warm'),counts
  cmd.append(str(J/'cf-cold-warm.o'))
  for flag in['-C','-Ln','-o','-m']:cmd[cmd.index(flag)+1]=str(J/Path(cmd[cmd.index(flag)+1]).name)
  cmd[cmd.index('--ld-args')+1]='--dbgfile,'+str(J/'candidate.dbg');run('final-link',cmd);prepare(R,J/'candidate.nes')
  old,b=qualified(P/'joint/candidate.nes'),qualified(J/'candidate.nes')
  for n in['MenuResolveCharacter','QueueSelection','DrawSelectionPreview','FmStartFlags','BwScene','BwStatusName','BwColdPrepare','BwColdDraw','BwBtResolve','BwResolveFamilyTail','BtServiceVeneers','BtServiceUnavailable','BtRouter','HuEntryBase','HuResolve','CfLoaderProposal','CfLoaderCoreProposal','CfLoaderExpectedCookie','CfOrBtCheck','CfRetire']:
   assert(address(b,n),location(b,n))==(address(old,n),location(old,n)),n
  assert 'BwStartFlags'not in b['syms']and address(b,'FmStartIdentityFlags')==0xb5cf
  for n,(expected,bank)in{'CfSceneRetireForeign':(0xbfe1,69),'CfLoadIfCold':(0xbfcb,115)}.items():assert(address(b,n),(location(b,n)-16)//8192)==(expected,bank)
  for n,side in[('bowser.bin','04-bowser.bin'),('ram3.bin','01-ram3.bin'),('code.bin','02-code.bin'),('data.bin','03-data.bin')]:
   output=J/'sideoutputs/candidate'/side;assert sha(output)==sha(P/'joint'/n);shutil.copyfile(output,J/n)
  for n in['ff-cookie.bin']:assert sha(J/n)==sha(P/'joint'/n)
  assert sha(J/'cf-stream.bin')==sha(a.cf_joint/'cf-stream.bin')and sha(J/'cf-cookie.bin')==sha(a.cf_joint/'cf-cookie.bin')
  stage=dict(source=True,status='PENDING_CF_COLD_WARM_SOURCE_TARGETED_CONTROLS_REQUIRED',candidate=sha(J/'candidate.nes'),parent=parent['candidate'],own_CF_candidate=own.get('candidate'),joint=str(J),ready=66,CF_pending=True,BT_pending=True,native=False,installed=False,admitted=False,new_ROM_grant=sha(G),extension_ROM_grant=sha(a.extension_grant),CF_policy_handoff=sha(a.cf_handoff),BT_gate_review=sha(REVIEW),menu_used=359,menu_grant=400,BT_router_used=211,BT_router_grant=224,A67_old51_repurposed_14plus37=True,
   bindings={str(p.resolve()):sha(p)for p in[Path(__file__),P/'handoff.json',a.cf_handoff,G,a.extension_grant,R/'tools/audit/prepare_cf_cold_warm_source_v1.py',R/'build/cf-cold-warm-source-v1/preparation-negative.json',REVIEW,FIT/'proposal.json',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'private.cfg',J/'src/full_roster_menu.s',J/'src/cf_menu_body.inc',J/'entrypoint.s',J/'bowser/cold.s',J/'bowser/router.s',J/'bt/router.s',J/'cf-cold-warm.s',J/'cf-stream.bin',J/'cf-cookie.bin',*J.glob('cf-*.o')]})
  save(O/'source-stage.json',stage);save(J/'source-stage.json',stage);bound(P/'handoff.json');bound(a.cf_handoff)
  print(json.dumps({k:v for k,v in stage.items()if k!='bindings'}))
 except Exception as e:save(O/'negative.json',dict(passed=False,error=repr(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
