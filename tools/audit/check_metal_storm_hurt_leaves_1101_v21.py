"""Differential original/relocated injury leaves, bounded in-memory fixtures."""
import hashlib,itertools,json,re,subprocess
import metal_storm_cpu_1101_v2 as M
from verify_native_relocation import NesMPU
from private_build_outputs_v1 import validate
O=M.ROOT/'build/metal-storm-hurt-1101-v21'
REF=M.ROOT/'tools/reference/metal_storm_hurt_leaves_1101_v21.inc'

def main():
 O.mkdir(exist_ok=True)
 (O/'leaves.s').write_text(REF.read_text().replace('.import MsState','MsState=$6000'))
 (O/'leaves.cfg').write_text('MEMORY { H:start=$9000,size=$100,file=%O; } SEGMENTS { CODE:load=H,type=ro; }')
 cc=M.ROOT/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe',O/'leaves.s','-o',O/'leaves.o'],[cc/'ld65.exe','-C',O/'leaves.cfg',O/'leaves.o','-o',O/'leaves.bin','-Ln',O/'leaves.lbl']]:
  cmd=list(map(str,cmd));validate(cmd,O,cwd=M.ROOT);p=subprocess.run(cmd,capture_output=True,text=True);assert p.returncode==0,p.stderr
 labels={m[2]:int(m[1],16) for line in (O/'leaves.lbl').read_text().splitlines() if (m:=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)',line))}
 donor=M.Bus();donor.regs[6:8]=[0,1];donor.map();rom=bytes(donor);code=(O/'leaves.bin').read_bytes()
 def run(initial,port,entry,end,a):
  mem=bytearray(rom);base=0x6000 if port else 0
  mem[base:base+2048]=initial
  if port:mem[0x9000:0x9000+len(code)]=code
  c=NesMPU(memory=mem,pc=labels[entry] if port else entry);c.a=a;c.x=4;c.y=7;c.p=0x71;c.sp=224;c.stPushWord(0x5ffe)
  for _ in range(100):
   if c.pc==(0x5fff if port else end):break
   assert mem[c.pc]!=0,hex(c.pc);c.step()
  else:raise AssertionError('leaf bound')
  return bytes(mem[base:base+2048]),(c.a,c.x,c.y,c.p&0xcf)
 count=0;digest=hashlib.sha256()
 for clock,face in itertools.product(range(256),[0,1,0x80,0xc7]):
  initial=bytearray(2048);initial[0x33]=clock;initial[0x540]=face
  a,ar=run(initial,False,0x9548,0x9567,clock);b,br=run(initial,True,'Ms21HurtBlink',0,clock)
  assert ar==br and a[:0x100]+a[0x200:]==b[:0x100]+b[0x200:]
  digest.update(b);count+=1
 for scene,subscene,armor in itertools.product([0,1,7,255],[0,3,128,255],[0,128]):
  initial=bytearray(2048);initial[0x750]=scene;initial[0x751]=subscene;initial[0x5d0]=armor;initial[0x528]=9
  a,ar=run(initial,False,0x95bb,0x95d6,85);b,br=run(initial,True,'Ms21ArmorReturn',0,85)
  assert ar==br and a[:0x100]+a[0x200:]==b[:0x100]+b[0x200:]
  assert b[0x74b]==180 and b[0x5d0]==0 and b[0x34]==scene and b[0x35]==subscene
  digest.update(b);count+=1
 q=dict(passed=True,donor_sha256=M.EXPECTED,source_sha256=hashlib.sha256(REF.read_bytes()).hexdigest(),relocated_bytes=len(code),differential_cases=count,aggregate_sha256=digest.hexdigest(),host_wired=False,scope='Original instruction boundaries compared with relocated private-state leaves. Host scene timing, enemy effects, audio, death and injury admission remain pending.')
 (O/'leaves-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
