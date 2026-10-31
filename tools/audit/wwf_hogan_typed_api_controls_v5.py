"""All real36 ingress paths preserve the native callback contract."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import wwf_hogan_runtime_controls_v3 as V
from ff_wram_host_isr_v4 import clone
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
H=V.H;T=V.T;J=R/'build/wwf-hogan-natural-source-v15/joint';O=R/'build/wwf-hogan-typed-api-controls-v5'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def call(m,pc,bank,p):
 b=m.bundle;m[address(b,'SafecallA_SMC')+1]=85
 m[address(b,'FarcallJmpTarget_SMC')+1]=pc&255;m[address(b,'FarcallJmpTarget_SMC')+2]=pc>>8
 c=NesMPU(memory=m,pc=address(b,'FarCallCommon'));c.a,c.x,c.y,c.p,c.sp=bank,7,91,p,224;c.stPushWord(0x5aff)
 expected=[]
 def capture(mem,cpu,step):
  if cpu.pc==address(b,'WfDetachRuntime'):
   expected.extend(mem[0x101+cpu.sp:0x101+cpu.sp+21])
 result=H.finish(m,c,capture)
 if expected:
  at=address(b,'WfDetachedFrame')-0xc000;expected[2]=H.get(m,'ReloadCHRBank')
  assert list(m.ram[2][at:at+21])==expected,('Exact saved physical caller frame',pc)
 return result

def app(m,c):
 shadow={address(m.bundle,n)for n in ['CurrentBank','CurrentBankC']}
 at=address(m.bundle,'WfDetachedFrame')-0xc000
 frame_addresses=set(range(address(m.bundle,'WfDetachedFrame'),address(m.bundle,'WfDetachedFrameEnd')))
 # These21 bytes are the exact verified *transport* frame above. Different
 # real callers can have different prior SFC operands. No source/application
 # field, code byte, cookie or other cache data is projected out.
 images=[bytes(v)for v in m.ram];images[2]=images[2][:at]+images[2][at+21:]
 return ((c.a,c.x,c.y,c.p,c.sp),images,[(a,v)for a,v in m.writes if a not in shadow and(a<256 or 0x200<=a<0x5100 or 0x5200<=a<0x8000)],[(bank,at,v)for bank,at,v in m.ram_writes if bank!=2 or 0xc000+at not in frame_addresses],m.rawtags[:])

def main():
 assert not O.exists();O.mkdir();q=dict(passed=False,native=False,rows=[])
 try:
  b=T.qualified(J/'candidate.nes');V.J=J;base=V.make(b)
  at=location(b,'WfResolveTargets');targets=[tuple(b['raw'][at+3*i:at+3*i+3])for i in range(36)]
  typed=address(b,'HuEntryBase');typedbank=((location(b,'HuEntryBase')-16)//8192)|128
  for slot,bits in itertools.product(range(36),range(64)):
   p=0x30|(bits&15)|((bits&48)<<2);pair=[];cost=[]
   for direct in [False,True]:
    m,_=clone(base,NesMPU(memory=base));m.writes.clear();m.ram_writes.clear()
    lo,hi,bank=targets[slot];pc=(lo+256*hi)if direct else typed+16*slot
    c,low=call(m,pc,bank if direct else typedbank,p);pair.append(app(m,c));cost.append(c.processorCycles)
   assert pair[0]==pair[1],('Native callback AXYP/writes/maps',slot,bits,pair[0][0],pair[1][0])
   q['rows'].append([slot,bits,cost[0]-cost[1],low])
  # Direct32 must really be the original native world palette producer;
  # direct19 really is original JnReset, with own transient reset deferred
  # to the authenticated forcedblank scene instead of another SFC frame.
  for slot,name in [(10,'BlockBufferColli_Head'),(14,'BlockBufferColli_Side'),(19,'JnResetDispatch'),(28,'PlayerHeadWithinTerrain'),(32,'HuNativeWorldPalette')]:
   lo,hi,bank=targets[slot];assert lo+256*hi==address(b,name)and bank==((location(b,name)-16)//8192)|128
  rejects=0
  for index,slot in itertools.product(range(16),[0,1,2]):
   m,_=clone(base,NesMPU(memory=base));m.ram[2][0x1fe0+index]^=1;image=bytes(m.ram[2]);executed=[]
   def no_guest(mem,cpu,step):
    if 0xc000<=cpu.pc<0xe000 and mem.rawtags[2]==2:executed.append(cpu.pc)
   c=H.start(m,'HuEntryBase',p=0xf9);pc=typed+16*slot
   m[address(b,'FarcallJmpTarget_SMC')+1]=pc&255;m[address(b,'FarcallJmpTarget_SMC')+2]=pc>>8
   H.finish(m,c,no_guest);assert not executed and bytes(m.ram[2])==image and not c.p&1;rejects+=1
  q.update(passed=True,candidate=sha(J/'candidate.nes'),exact_detached_transport_frame_each_route=True,transport_frame_bytes=21,actual36_all64flags=len(q['rows']),poisoned_typed_before_first_guest=rejects,CPU='NesMPU binary ADC/SBC with D retained',native_query_outputs_and_application_order_exact=True,full_AXYP_SP_maps_and_RAM_exact=True)
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(V.__file__),J/'candidate.nes',J/'candidate.dbg',J.parent/'source-stage.json']}
  (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q.get(k)for k in['passed','candidate','actual36_all64flags','poisoned_typed_before_first_guest','error']}))
if __name__=='__main__':main()
