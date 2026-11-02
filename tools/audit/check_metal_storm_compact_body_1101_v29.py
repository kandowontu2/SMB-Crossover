"""Compare old/new compiled body renderer outputs across every source pose."""
import itertools,json,re
import prepare_metal_storm_compact_body_1101_v29 as P
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU

def main():
 bundles=[]
 for root in [P.BASE,P.O]:
  b=scoped_load(root/'candidate.nes')
  labels={m[2]:int(m[1],16) for line in (root/'component.lbl').read_text().splitlines() if (m:=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)',line))}
  seed=M.fresh(b);seed.raw_page(1,3);seed.raw_page(2,2)
  for bank,at,file in [(3,0,'native-actor.bin'),(2,0xd00,'native-render.bin'),(2,0x1ba0,'native-extra.bin')]:
   data=(root/file).read_bytes();seed.ram[bank][at:at+len(data)]=data
  cookie=(root/'native-cookie.bin').read_bytes()
  for bank in [2,3]:seed.ram[bank][0x1fe0:0x1ff0]=cookie
  M.put(seed,CurrentBank=3,CurrentBankC=2,SelectedCharacter=35,OperMode=1,GameEngineSubroutine=8,CurrentOAMOffset=0,GuestOamRotationActive=0,RgOamRotation=0,SsChrActive=0,InvHudActive=0,X5WideChrActive=0,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,Player_SprAttrib=0)
  seed.ram[2][0x800]=167
  for i in range(12):seed[address(b,'CurrentCHRBank')+i]=20+i;seed[address(b,'X5ChrMode')+i]=0
  seed[0x200:0x300]=bytes([240,0,0,0])*64
  bundles.append((b,labels,seed))
 poses=json.loads((P.P.R/'build/metal-storm-render-host-1101-v7/art.json').read_text())['body_packets']
 cases=0;cycles=[0,0]
 for pose,world,camera,offset in itertools.product(poses,[(128,112),(260,176)], [0,32],[0,216]):
  results=[]
  for index,(b,labels,seed) in enumerate(bundles):
   m=M.fork(seed);M.put(m,ScreenLeft_X_Pos=camera,CurrentOAMOffset=offset)
   for a,v in {0x510:128,0x480:world[0]&255,0x498:world[0]>>8,0x4b0:world[1],0x4c8:0,0x4e0:pose['state'],0x4f8:pose['frame'],0x540:pose['facing']|pose['gravity']}.items():m.ram[2][a]=v
   c=NesMPU(memory=m,pc=labels['MsRenderDraw']);c.a,c.x,c.y,c.p,c.sp=85,7,91,0x71,224;c.stPushWord(0x5ffe)
   for _ in range(30000):
    if c.pc==0x5fff:break
    assert m[c.pc]!=0,(index,hex(c.pc));c.step()
   else:raise AssertionError('render bound')
   assert c.sp==224
   cycles[index]=max(cycles[index],c.processorCycles)
   results.append((bytes(m[0x200:0x300]),tuple(m.chr_latches),M.get(m,'CurrentOAMOffset'),c.a,c.x,c.y,c.p&0xcf,tuple(m.rawtags)))
  assert results[0]==results[1],(pose['state'],pose['frame'],world,camera,offset)
  cases+=1
 q=dict(passed=True,ROM_sha256=P.P.sha(P.O/'candidate.nes'),baseline_ROM_sha256=P.P.sha(P.BASE/'candidate.nes'),compiled_renderer_cases=cases,pose_contexts=len(poses),max_cycles=cycles,renderer_bytes_recovered=590,scope='Actual native OAM/CHR helper execution with seeded authenticated cache. Every original body pose/facing/gravity, two positions, two camera offsets and two OAM occupancies compared byte-for-byte. Not cold loader or native Mesen gameplay proof.')
 (P.O/'body-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
