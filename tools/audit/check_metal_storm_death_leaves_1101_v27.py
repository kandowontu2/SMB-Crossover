"""Differential original death initialization and full explosion sequence."""
import hashlib,itertools,json,subprocess
import metal_storm_cpu_1101_v2 as M
from private_build_outputs_v1 import validate
O=M.ROOT/'build/metal-storm-death-leaves-1101-v27'
REF=M.ROOT/'tools/reference/metal_storm_death_leaves_1101_v27.inc'

def main():
 O.mkdir(exist_ok=True)
 (O/'death.s').write_text('MsState=$6000\n'+REF.read_text())
 (O/'death.cfg').write_text('MEMORY { H:start=$9000,size=$400,file=%O; } SEGMENTS { CODE:load=H,type=ro; }')
 cc=M.ROOT/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe','-g',O/'death.s','-o',O/'death.o'],[cc/'ld65.exe','-C',O/'death.cfg',O/'death.o','-o',O/'death.bin','-Ln',O/'death.lbl']]:
  cmd=list(map(str,cmd));validate(cmd,O,cwd=M.ROOT)
  p=subprocess.run(cmd,capture_output=True,text=True);assert p.returncode==0,p.stderr
 sy={line.split()[2].lstrip('.'):int(line.split()[1],16) for line in (O/'death.lbl').read_text().splitlines()}
 code=(O/'death.bin').read_bytes();bus=M.Bus();bus.regs[6:8]=[0,1];bus.map();rom=bytes(bus)
 def run(state,port,tick=False):
  mem=bytearray(rom);base=0x6000 if port else 0;mem[base:base+2048]=state
  if port:mem[0x9000:0x9000+len(code)]=code
  pc=sy['Ms27DeathAnimate' if tick else 'Ms27DeathInit'] if port else (0x96ec if tick else 0x966a)
  c=M.NesMPU(memory=mem,pc=pc);c.a,c.x,c.y,c.p,c.sp=85,7,91,0x71,224;c.stPushWord(0x5ffe)
  for _ in range(400):
   if c.pc==0x5fff:break
   assert mem[c.pc]!=0,hex(c.pc);c.step()
  else:raise AssertionError('death leaf bound')
  assert c.sp==224
  return bytes(mem[base:base+2048]),(c.a,c.x,c.y,c.p&0xcf)
 def same(state,tick=False):
  a,ar=run(state,False,tick);b,br=run(state,True,tick)
  assert ar==br,(ar,br)
  assert a[:256]+a[512:]==b[:256]+b[512:]
  return b
 count=0
 for x,y,wrap,high in itertools.product([0,15,16,120,255],[0,15,16,128,239,240,255],[0,1],[0,1,255]):
  state=bytearray((i*17+3)&255 for i in range(2048));state[0x480]=x;state[0x4b0]=y;state[0x50]=wrap;state[0x498]=high;state[0x4c8]=high;state[0x35]=1
  same(state);count+=1
 state=bytearray(2048);state[0x480]=120;state[0x4b0]=144;state[0x35]=1
 state=same(state);poses=[]
 for tick in range(48):
  state=same(state,True)
  poses.append([state[0x4e0],state[0x4f8]])
  assert state[0x35]==(3 if tick==47 else 2)
 assert state[0x53]==60 and state[0x4e0]==4 and state[0x4f8]==0
 q=dict(passed=True,donor_sha256=M.EXPECTED,source_sha256=hashlib.sha256(REF.read_bytes()).hexdigest(),relocated_bytes=len(code),initializer_cases=count,explosion_updates=48,poses=poses,host_wired=False,scope='Original bank0 initialization and explosion animation CPU equivalence. Moving-platform adjustment, pre-explosion freeze, post-explosion wait, native life-loss handoff and graphics are not integrated by this test.')
 (O/'death-CPU.json').write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps({k:v for k,v in q.items() if k!='poses'}))
if __name__=='__main__':main()
