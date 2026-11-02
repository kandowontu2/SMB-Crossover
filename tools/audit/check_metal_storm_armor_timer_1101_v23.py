"""Verify the relocated donor timer and its full recovery sequence."""
import hashlib,itertools,json,re,subprocess
import metal_storm_cpu_1101_v2 as M
from verify_native_relocation import NesMPU
from private_build_outputs_v1 import validate
O=M.ROOT/'build/metal-storm-armor-timer-1101-v23'
REF=M.ROOT/'tools/reference/metal_storm_armor_timer_1101_v23.inc'

def main():
 O.mkdir(exist_ok=True);(O/'timer.s').write_text(REF.read_text().replace('.import MsState','MsState=$6000'))
 (O/'timer.cfg').write_text('MEMORY { H:start=$9000,size=$100,file=%O; } SEGMENTS { CODE:load=H,type=ro; }')
 cc=M.ROOT/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe',O/'timer.s','-o',O/'timer.o'],[cc/'ld65.exe','-C',O/'timer.cfg',O/'timer.o','-o',O/'timer.bin']]:
  cmd=list(map(str,cmd));validate(cmd,O,cwd=M.ROOT);p=subprocess.run(cmd,capture_output=True,text=True);assert p.returncode==0,p.stderr
 donor=M.Bus();donor.regs[6:8]=[4,5];donor.map();rom=bytes(donor);code=(O/'timer.bin').read_bytes()
 def run(initial,port):
  m=bytearray(rom);base=0x6000 if port else 0;m[base:base+2048]=initial
  if port:m[0x9000:0x9000+len(code)]=code
  c=NesMPU(memory=m,pc=0x9000 if port else 0x8471);c.a,c.x,c.y,c.p,c.sp=85,7,91,0x71,224;c.stPushWord(0x5ffe)
  for _ in range(100):
   if c.pc==0x5fff:break
   assert m[c.pc]!=0,hex(c.pc);c.step()
  else:raise AssertionError('timer bound')
  assert c.sp==224
  return bytes(m[base:base+2048]),(c.a,c.x,c.y,c.p&0xcf)
 def same(state):
  a,ar=run(state,False);b,br=run(state,True)
  assert ar==br and a[:0x100]+a[0x200:]==b[:0x100]+b[0x200:]
  return b
 count=0
 for timer,immune,visible in itertools.product(range(256),[0,1,128],[0,128]):
  state=bytearray(2048);state[0x74b]=timer;state[0x648]=immune;state[0x70]=visible;same(state);count+=1
 state=bytearray(2048);state[0x74b]=180;state[0x648]=128;state[0x70]=128
 for tick in range(180):
  state=same(state)
  assert state[0x74b]==179-tick and state[0x648]==(128 if tick<179 else 0)
 assert state[0x70]==128 and state[0x74e]==128
 q=dict(passed=True,donor_sha256=M.EXPECTED,source_sha256=hashlib.sha256(REF.read_bytes()).hexdigest(),source_span='bank4:8471..848F',relocated_bytes=len(code),differential_cases=count,recovery_sequence_updates=180,first_update_timer=179,host_wired=False,scope='Exact original CPU timer, wraparound, immunity and source70/074E flag writes. Visual meaning of70 is not proven by this test. Host once-per-frame integration and renderer behavior remain pending.')
 (O/'timer-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
