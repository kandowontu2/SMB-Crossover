"""Disposable exact223B B020 source experiment; no readiness change."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare
from py65.disassembler import Disassembler
from py65.devices.mpu6502 import MPU
P=R/'build/bt-current-cf-component-v2';O=R/'build/bt-jmp-row-cold-source-v1';J=O/'joint'
S=R/'tools/reference/bt_jmp_row_cold_proposal_v1.s';Q=R/'build/bt-jmp-row-cold-proposal-v1/proposal.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n')

def main():
 assert not O.exists();O.mkdir();logs=[]
 try:
  parent=json.loads((P/'source-stage.json').read_text())
  for f,h in parent['bindings'].items():assert sha(f)==h,('immutable component input',f)
  assert parent['candidate']=='8961be0a5c51ca091efdddea07c122a0c7a8204e1eb071b2cd001bba4a7c9f8c'
  assert sha(Q)=='9969ec888862395cebbba121e642a623a104d4216aa2880578b461d8c49b0020'
  proposal=json.loads(Q.read_text());assert proposal['passed']
  for f,h in proposal['bindings'].items():assert sha(f)==h,('immutable proposal input',f)
  shutil.copytree(P/'joint',J);(J/'bt/router.s').write_bytes(S.read_bytes())
  cfg=J/'private.cfg';cfg.write_text(cfg.read_text().replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix()))
  def run(n,cmd):
   guard=validate(cmd,O,cwd=R);z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);q=dict(command=cmd,cwd=str(R),output_guard=guard,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr);logs.append(q);save(O/(n+'.json'),q);save(O/'commands.json',logs);assert z.returncode==0,(n,z.stderr)
  run('router-build',[str(R/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502x','-g','-l',str(J/'bt/router.lst'),'--create-full-dep',str(J/'bt/router.dep'),'-o',str(J/'bt/router.o'),str(J/'bt/router.s')])
  cmd=json.loads((P/'final-link.json').read_text())['command'][:];rebound=[]
  for i,x in enumerate(cmd):
   p=Path(x)
   if p.suffix=='.o'and p.parent.name=='bt'and p.stem=='router':rebound.append(str(p));cmd[i]=str(J/'bt/router.o')
  assert len(rebound)==1,rebound
  for flag in['-C','-Ln','-o','-m']:cmd[cmd.index(flag)+1]=str(J/Path(cmd[cmd.index(flag)+1]).name)
  cmd[cmd.index('--ld-args')+1]='--dbgfile,'+str(J/'candidate.dbg');run('final-link',cmd);prepare(R,J/'candidate.nes')
  old,b=map(qualified,[P/'joint/candidate.nes',J/'candidate.nes'])
  for n,want in[('BtServiceVeneers',0xb020),('BwServiceVeneers',0xb020),('BtServiceUnavailable',0xb08c),('BtRouter',0xb08e)]:
   assert address(old,n)==address(b,n)==want and location(old,n)==location(b,n),n
  for n in['BtCheck','BtLoad','BtColdPortrait','BtColdColors','BwBtResolve','BwScene','BwCfSceneLoad','CfLoadIfCold','CfOrBtCheck','CfRetire','BmFresh','BmColors','FmPending','FmToggle','FmStartFlags']:
   assert(address(old,n),location(old,n))==(address(b,n),location(b,n)),n
  lo=location(b,'BtServiceVeneers');changed=[i for i,(x,y)in enumerate(zip(old['raw'],b['raw']))if x!=y]
  assert changed and all(lo<=i<lo+224 for i in changed)
  assert old['raw'][:16]==b['raw'][:16] and old['raw'][16+128*8192:]==b['raw'][16+128*8192:]
  for n in['bt/cache.bin','bt/cookie.bin','cf-stream.bin','cf-cookie.bin','bowser.bin','ram3.bin','code.bin','data.bin','ff-cookie.bin']:
   assert sha(J/n)==sha(P/'joint'/n),n
  actual=b['raw'][lo:lo+223];assert actual[:108]==bytes([0x4c,0x8e,0xb0])*36 and actual[108:110]==bytes([0x18,0x60])
  assert b['raw'][lo+223]==255
  cpu=MPU(memory=[0]*65536);cpu.memory[0xb020:0xb020+223]=actual;dis=Disassembler(cpu);rows=[];pc=0xb020
  while pc<0xb020+223:
   size,text=dis.instruction_at(pc);rows.append(dict(PC=hex(pc),bytes=bytes(cpu.memory[pc:pc+size]).hex(),instruction=text));pc+=size
  save(O/'post-disassembly.json',rows)
  source_labels={n:dict(PC=address(b,n),ROM_offset=location(b,n))for n in['BtServiceVeneers','BtServiceUnavailable','BtRouter','BtColdPortrait','BtColdColors','BwBtResolve','FarcallJmpTarget_SMC','SafecallA_SMC','NextBank_SMC','FarCallCommon']}
  q=dict(source=True,status='EXPERIMENTAL_223B_JMP_ROW_LINKED_NO_ADOPTION',candidate=sha(J/'candidate.nes'),parent=parent['candidate'],joint=str(J),ready=66,CF_pending=True,BT_pending=True,native=False,installed=False,proposal=sha(Q),proposal_source=sha(S),actual_router_bytes=223,allocated_router_bytes=224,changed_bytes=len(changed),labels=source_labels,actual_rebound_router_importer=rebound,all_other_ROM_header_CHR_payload_cookies_exact=True,
   pending=['Actual new worker-entry/callback/allflags/vector ABI qualification','BT native world32 path and real prior-CF-retirement proof','No current68 M3 source, experimental P1, readiness or native changes'])
  files=[Path(__file__),S,Q,P/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'private.cfg',J/'bt/router.s',J/'bt/router.o',J/'bt/router.lst',J/'bt/router.dep',O/'router-build.json',O/'final-link.json',O/'post-disassembly.json']
  q['bindings']={str(p.resolve()):sha(p)for p in files};save(O/'source-stage.json',q);save(J/'source-stage.json',q)
  for f,h in parent['bindings'].items():assert sha(f)==h,('immutable component after link',f)
  print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))
 except Exception as e:save(O/'negative.json',dict(passed=False,error=repr(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
