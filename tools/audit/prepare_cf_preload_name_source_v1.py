"""Link measured19+31+1 source repack in exact existing A67 owned51B."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare
P=R/'build/cf-cold-warm-palette-source-v1';O=R/'build/cf-preload-name-source-v1';J=O/'joint';M=R/'build/cf-name-fallback-factor-proposal-v2/proposal.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n')

def bound(p):
 q=json.loads(Path(p).read_text())
 for f,h in q['bindings'].items():assert sha(f)==h,('frozen input',f)
 return q

def main():
 assert not O.exists();O.mkdir();logs=[]
 try:
  parent=bound(P/'handoff.json');proposal=bound(M);assert proposal['passed']
  assert parent['candidate']=='ef2f11e232ec878c277245c3802bcf8a415415e38507c26feefaef3744c1bee1'
  assert sha(M)=='246cc165ec7c5ade53bf981969edae8a0d44408d58cce33d64e8ef3da4b8d812'
  shutil.copytree(P/'joint',J)
  p=J/'private.cfg';p.write_text(p.read_text().replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix()))
  p=J/'bowser/router.s';s=p.read_text();lo=s.index('BwResolveColdNative:');hi=s.index('; Exact16B already-owned tail;',lo)
  new='''BwResolveColdNative:
 ldx #1
 cmp #45
 beq BwResolveROM
 ldx #3
 cmp #54
 beq BwResolveROM
 inx
 cmp #57
 beq BwResolveROM
 clc
 rts
BwCfSceneLoad:
 ; Sole private caller has already saved nativeAXYP. These X/Y are
 ; target metadata, not source/native gameplay parameters.
 lda SelectedCharacter
 cmp #31
 beq Cf
 lda #<BwLoad
 ldx #>BwLoad
 ldy #.lobyte(.bank(BwLoad)|$80)
 bne Publish
Cf:
 lda #<CfLoadIfCold
 ldx #>CfLoadIfCold
 ldy #.lobyte(.bank(CfLoadIfCold)|$80)
Publish:
 sta FarcallJmpTarget_SMC+1
 stx FarcallJmpTarget_SMC+2
 tya
 jmp FarCallCommon
.assert BwCfSceneLoad-BwResolveColdNative=19,error,"Exact19B 15/18/19 fallback"
.assert *-BwCfSceneLoad=31,error,"Exact31B private selected loader"
 nop
.assert .lobyte(.bank(BwLoad)|$80)<>0,lderror,"Selected ROM metadata branch always"
'''
  p.write_text(s[:lo]+new+s[hi:])
  def run(n,cmd):
   guard=validate(cmd,O,cwd=R);z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);q=dict(command=cmd,cwd=str(R),output_guard=guard,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr);logs.append(q);save(O/(n+'.json'),q);save(O/'commands.json',logs);assert z.returncode==0,(n,z.stderr)
  ca=R/'tools/Windows/cc65/bin/ca65.exe'
  for n in['router','cold']:
   src=J/'bowser'/(n+'.s');obj=src.with_suffix('.o');run(n+'-build',[str(ca),'--cpu','6502x','-g','-I',str(J/'bowser'),'-I',str(J),'-I',str(J/'src'),'-I',str(R),'--create-full-dep',str(obj.with_suffix('.dep')),'-o',str(obj),str(src)])
  cmd=json.loads((P/'final-link.json').read_text())['command'][:];rebound={}
  for i,x in enumerate(cmd):
   p=Path(x)
   if p.suffix=='.o'and p.parent.name=='bowser'and p.stem in['router','cold']:
    assert parent['bindings'].get(str(p.resolve()))==sha(p),p;cmd[i]=str(J/'bowser'/p.name);rebound[p.stem]=str(p)
  assert len(rebound)==2
  for flag in['-C','-Ln','-o','-m']:cmd[cmd.index(flag)+1]=str(J/Path(cmd[cmd.index(flag)+1]).name)
  cmd[cmd.index('--ld-args')+1]='--dbgfile,'+str(J/'candidate.dbg');run('final-link',cmd);prepare(R,J/'candidate.nes')
  a,b=map(qualified,[P/'joint/candidate.nes',J/'candidate.nes'])
  for n in['BtServiceVeneers','BtRouter','BtServiceUnavailable','BwBtResolve','BwResolveColdNative','BwResolveFamilyTail','BwScene','BwSceneDone','BwSceneNativePrepared','MenuResolveCharacter','FmStartFlags','FmStartIdentityFlags','CfSceneRetireForeign','CfLoadIfCold','CfOrBtCheck','CfRetire']:
   assert(address(a,n),location(a,n))==(address(b,n),location(b,n)),n
  assert address(a,'BwCfSceneLoad')==0xb2cb and address(b,'BwCfSceneLoad')==0xb2d0
  for n,side in[('bowser.bin','04-bowser.bin'),('ram3.bin','01-ram3.bin'),('code.bin','02-code.bin'),('data.bin','03-data.bin')]:
   f=J/'sideoutputs/candidate'/side;assert sha(f)==sha(P/'joint'/n),n;shutil.copyfile(f,J/n)
  for n in['ff-cookie.bin','cf-stream.bin','cf-cookie.bin']:assert sha(J/n)==sha(P/'joint'/n),n
  spans=[(location(b,'BwResolveColdNative'),51),(location(b,'BwScene'),0xb400-address(b,'BwScene'))]
  changed=[i for i,(x,y)in enumerate(zip(a['raw'],b['raw']))if x!=y];assert changed and all(any(lo<=i<lo+size for lo,size in spans)for i in changed)
  assert a['raw'][:16]==b['raw'][:16]and a['raw'][16+128*8192:]==b['raw'][16+128*8192:]
  stage=dict(source=True,status='PENDING_LINKED_19_31_NAME_FACTOR_CONTROLS',candidate=sha(J/'candidate.nes'),parent=parent['candidate'],joint=str(J),ready=66,CF_pending=True,BT_pending=True,native=False,installed=False,admitted=False,old_owned51_used=[19,31,1],private_helper_relocation=dict(symbol='BwCfSceneLoad',old='B2CB',new='B2D0',sole_actual_importer=str(J/'bowser/cold.o')),actual_rebuilt_objects=rebound,changed_bytes=len(changed),exact_changed_envelopes=spans,no_new_span_state_shared_P1_or_NMI_hook=True,
   bindings={str(p.resolve()):sha(p)for p in[Path(__file__),P/'handoff.json',M,J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'private.cfg',J/'bowser/router.s',J/'bowser/router.o',J/'bowser/router.dep',J/'bowser/cold.s',J/'bowser/cold.o',J/'bowser/cold.dep',O/'final-link.json']})
  save(O/'source-stage.json',stage);save(J/'source-stage.json',stage);bound(P/'handoff.json');print(json.dumps({k:v for k,v in stage.items()if k!='bindings'}))
 except Exception as e:save(O/'negative.json',dict(passed=False,error=repr(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
