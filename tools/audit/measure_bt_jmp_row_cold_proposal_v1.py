"""Actual object bytes/listing + current incoming SFC target witnesses."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
from py65.disassembler import Disassembler
from py65.devices.mpu6502 import MPU
import cf_preload_name_caller_controls_v2 as A
T,C,V=A.T,A.C,A.V
P=R/'build/cf-preload-name-source-v1/joint';O=R/'build/bt-jmp-row-cold-proposal-v1';S=R/'tools/reference/bt_jmp_row_cold_proposal_v1.s'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,proposal_only=True,native=False,source_candidate_not_modified=True)
 try:
  cmd=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502x','-g','-l',str(O/'post-source.lst'),'--create-full-dep',str(O/'post.dep'),'-o',str(O/'post.o'),str(S)];guard=validate(cmd,O,cwd=R);z=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
  (O/'build.json').write_text(json.dumps(dict(command=cmd,output_guard=guard,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr),indent=2)+'\n');assert z.returncode==0,z.stderr
  od=subprocess.run([str(R/'tools/Windows/cc65/bin/od65.exe'),'--dump-segments','--dump-imports',str(O/'post.o')],capture_output=True,text=True,check=True).stdout;(O/'post-object.txt').write_text(od)
  b=qualified(P/'candidate.nes');pc=address(b,'BtServiceVeneers');offset=location(b,'BtServiceVeneers');count=211
  cpu=MPU(memory=[0]*65536);cpu.memory[pc:pc+count]=b['raw'][offset:offset+count];dis=Disassembler(cpu);rows=[];cursor=pc
  while cursor<pc+count:
   size,text=dis.instruction_at(cursor);rows.append(dict(PC=hex(cursor),bytes=bytes(cpu.memory[cursor:cursor+size]).hex(),instruction=text));cursor+=size
  (O/'pre-disassembly.json').write_text(json.dumps(rows,indent=2)+'\n')
  # These are actual unchanged old source invocations. They witness the
  # target operand is still present at BtRouter BEFORE the old row decode.
  # No post-proposal code is executed or labelled qualified by this tool.
  V.select(P);witness=[]
  for raw in[27,31,33]:
   for service in range(37):
    m=T.Bus();T.put(m,SelectedCharacter=raw,FmGroups=0,OperMode=0,FamilyMainCommit=1);m.ram[2][0x1fe0]=0;m.ram[3][0x1fe0]=0
    target=address(b,'BtServiceVeneers')+3*service;c=C.start(m,target,(location(b,'BtServiceVeneers')-16)//8192|128)
    seen=[]
    def watch(cpu,step):
     if cpu.pc==address(b,'BtRouter')and m.rawtags[1]==0xd7:
      lo=m[address(b,'FarcallJmpTarget_SMC')+1];hi=m[address(b,'FarcallJmpTarget_SMC')+2]
      assert lo+256*hi==target and((lo-address(b,'BtServiceVeneers'))&255)==3*service
      seen.append(dict(raw=raw,service=service,step=step,PC=hex(cpu.pc),target=hex(lo+256*hi),source_SP=cpu.sp,actual_row_return=bytes(m[cpu.sp+0x101:cpu.sp+0x103]).hex()))
    T.finish(m,c,watch)
    assert len(seen)==(1 if service<36 else 0);witness+=seen
  main=json.loads((R/'build/cf-preload-name-source-v1/final-link.json').read_text())['command'];objects=[Path(x)for x in main if x.endswith('.o')];importers=[]
  for obj in objects:
   text=subprocess.run([str(R/'tools/Windows/cc65/bin/od65.exe'),'--dump-imports',str(obj)],capture_output=True,text=True,check=True).stdout
   if re.search(r'Name:\s+"(BtServiceVeneers|BwServiceVeneers|BtRouter)"',text):importers.append(str(obj))
  q.update(passed=True,current211_to_proposed223_of224=True,public_table_slot36_worker_offsets=[0,108,110],actual_old_target_witnesses=witness,actual_importing_objects=importers,
   before='36JSRtable; old decoder $0105,X derives rowreturn; original nativeAXYP on4savedbytes above ownrowreturn.',
   after='36JMPtable; targetLo captured before any nestedcall/SMCwrite; nativeAXYP saved identically, ownrowreturn absent. Success restores4nativebytes then tailsSFC+3; failure restoresAXYP withCclear then RTS. Original SFCworker return and oldA mapping frame remain.',
   flags='Gate/decoder flags dead while nativeP saved. Cold17/26 bank and high imported from actual owned source with linkasserts. Default genuine resolver returnsvalidC; originalP restored beforeworker, sourceA inSafecallA; SFCimposes originalNZfromA. Bad clears only savedC. Xtemporary never replaces nativeX.',
   blockers=['Post-source.lst/post.o are actual assembled bytes with unresolved true-import relocations; no linked postdisassembly or execution yet. Parent must authorize a disposable true-source link to produce actual post bytes before adoption.','This prototype funds ROM17/26 only. Ownsource32/nativeworld contract stillrequires actualcall-order/consumer solution before functional BT admission.','Accepted loader must have actual priorCFretirement; loader itself doesnotinvalidateC2. No blanketdirectAPI protection claimed.'],
   required=['Real all36publicSFCcalls + privateCfLoadIfCold15 and natural common27/31/33 workerentry before targetcapture','All flags/rawowners/cookies, fullcallbackAXYP/SP/all33SMC/R0..7/page1/rawmaps/sourcecontinuation','Real normal/lag/pausedNMI+legalIRQ at capture/mapper/return including publishedshadowgap','Current66 Main/menu/BW+CF cold/warm parity; CFandBTpending until naturalpipeline +rootnative'])
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 files=[Path(__file__),S,O/'build.json',O/'post.o',O/'post.dep',O/'post-source.lst',O/'post-object.txt',O/'pre-disassembly.json',P/'candidate.nes',P/'candidate.dbg',P/'bt/router.s',P/'bowser/router.s',P/'cf-cold-warm.s',R/'build/cf-preload-name-source-v1/handoff.json']
 q['bindings']={str(p.resolve()):sha(p)for p in files if p.exists()};(O/'proposal.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['actual_old_target_witnesses','bindings']}));assert q['passed']
if __name__=='__main__':main()
