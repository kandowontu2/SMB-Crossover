"""Exact emitted57B classifier and genuine existing native-tail setup ABI proof."""
from pathlib import Path
import hashlib,itertools,json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
P=R/'build/contra-force-palette-names-cart-v2';O=R/'build/contra-force-p1-classifier-controls-v1';S=R/'tools/reference/contra_force_p1_shared_factor_proposal_v2.s'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();out=dict(passed=False,native=False,linked_cart_or_grant=False)
 try:
  b=qualified(P/'joint/candidate.nes');tail=address(b,'FfMuxRomNative')+2;ta=location(b,'FfMuxRomNative')+2
  text=''
  for n in ['SelectedCharacter','SmFreezeRenderState','FfMuxNativeROM','FarCallCommon','SafecallA_SMC','FarcallJmpTarget_SMC']:
   text+='.export '+n+'\n'+n+'=$%04x\n'%address(b,n)
  text+='.export FfMuxNativeTail\nFfMuxNativeTail=$%04x\n'%tail
  mem='MEMORY { MODEL:start=$4000,size=$100,type=ro,file="%O";\n';segs='SEGMENTS { CF_SHARED_DRAW_FACTOR_PROPOSAL:load=MODEL,type=ro;\n'
  for i,n in enumerate(['SamusFreezeRenderFinish','BtServiceVeneers']):
   bank=(location(b,n)-16)//8192;pc=address(b,n)
   text+='.export '+n+'\n.segment "SYM%d"\n'%i+n+': .res 1\n';mem+=' S%d:start=$%04x,size=1,type=ro,bank=%d,file="";\n'%(i,pc,bank);segs+=' SYM%d:load=S%d,type=ro;\n'%(i,i)
  (O/'imports.s').write_text(text);(O/'model.cfg').write_text(mem+'}\n'+segs+'}\n')
  ca=R/'tools/Windows/cc65/bin/ca65.exe';ld=ca.with_name('ld65.exe');cmds=[]
  for name,src in [('proposal',S),('imports',O/'imports.s')]:cmds.append([str(ca),'--cpu','6502x','-g','--create-full-dep',str(O/(name+'.dep')),'-o',str(O/(name+'.o')),str(src)])
  cmds.append([str(ld),'-C',str(O/'model.cfg'),'-o',str(O/'model.bin'),'--dbgfile',str(O/'model.dbg'),'-Ln',str(O/'model.lbl'),'-m',str(O/'model.map'),str(O/'proposal.o'),str(O/'imports.o')])
  logs=[]
  for cmd in cmds:
   g=validate(cmd,O,cwd=O);q=subprocess.run(cmd,cwd=O,capture_output=True,text=True);logs.append(dict(command=cmd,cwd=str(O),output_guard=g,returncode=q.returncode,stdout=q.stdout,stderr=q.stderr));assert q.returncode==0,logs[-1]
  (O/'compile.json').write_text(json.dumps(logs,indent=2)+'\n');code=(O/'model.bin').read_bytes();assert len(code)==57
  labels={n:int(v,16)for v,n in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(O/'model.lbl').read_text())}
  m=[0]*65536;m[0x4000:0x4039]=code;c=NesMPU(memory=m,pc=0x4000);rows=0;cycles=set()
  flags=[p for p in range(256)if p&0x30==0x30];selected=address(b,'SelectedCharacter');state=address(b,'SmFreezeRenderState')
  for raw,p,v,a in itertools.product(range(256),flags,[0,1,128,255],[0,87,255]):
   m[selected]=raw;m[state]=v;c.pc=0x4000;c.a,c.x,c.y,c.p,c.sp=a,0xa9,0x63,p,0xe0;c.processorCycles=0
   done=(labels['CF']+3)if raw==31 else 0x400a
   for _ in range(6):
    if c.pc==done:break
    c.step()
   assert c.pc==done and[c.a,c.x,c.y,c.p,c.sp]==[v,169,99,(p&125)|(128 if v&128 else 0)|(2 if v==0 else 0),224],(raw,p,v,a,c.pc,c.a,c.p)
   cycles.add(c.processorCycles);rows+=1
  # Compare actual current inline18B setup with the actual same-bank18B
  # native tail body. Only JSR-vs-JMP opcode at byte15 differs.
  bridge=location(b,'FwNativeDrawAll');old=b['raw'][bridge+5:bridge+23];near=b['raw'][ta:ta+18]
  assert old[:15]==near[:15]and old[15]==32 and near[15]==76 and old[16:]==near[16:]
  smc=next(s for s in b['segs'].values()if s['name']=='"SMCCODE"');lo=int(smc['start'],0);count=int(smc['size'],0);assert count==33
  m[0x5000:0x5012]=old;m[tail:tail+18]=near;m[0x5100:0x5103]=[32,tail&255,tail>>8];pairs=0
  for p,a in itertools.product(flags,range(256)):
   results=[]
   for start in [0x5000,0x5100]:
    m[lo:lo+33]=[0xad]*33;c.pc=start;c.a,c.x,c.y,c.p,c.sp=a,169,99,p,224;c.processorCycles=0
    for _ in range(12):
     if c.pc==address(b,'FarCallCommon'):break
     c.step()
    assert c.pc==address(b,'FarCallCommon')and c.sp==222
    results.append(([c.a,c.x,c.y,c.p,c.sp],bytes(m[lo:lo+33]),c.processorCycles))
   assert results[0][:2]==results[1][:2] and results[1][2]-results[0][2]==3,(p,a,results);pairs+=1
  out.update(passed=True,actual_emitted_bytes=code.hex(),all256raw_64flags_4states_3incomingA_classifier_cases=rows,exact_originalA_XY_P_and_no_status_stack=True,classifier_cycles=sorted(cycles),actual_old_vs_near_tail_source_setup_pairs=pairs,setup_SMC_AXYP_depth_exact=True,near_tail_additional_cycles=3,
   scope='Abstract source-linked57B CPU model with actual native imports and exact current tail bytes; stops at original State-load phase or real SFC entry. No shared cart adoption, complete nativeDrawAll, ISR or palette-owner qualification is claimed.')
 except Exception as e:out.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  files=[Path(__file__),S,P/'source-stage.json',P/'joint/candidate.nes',P/'joint/candidate.dbg',R/'build/contra-force-p1-shared-factor-proposal-v3/proposal.json',R/'tools/audit/private_build_outputs_v1.py',*[p for p in O.iterdir()if p.is_file()]]
  out['bindings']={str(p.resolve()):sha(p)for p in files};p=O/'controls.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=out['passed'],error=out.get('error'),cases=out.get('all256raw_64flags_4states_3incomingA_classifier_cases'))),flush=True)
if __name__=='__main__':main()

