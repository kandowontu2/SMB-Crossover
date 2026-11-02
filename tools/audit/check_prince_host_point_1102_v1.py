"""Actual native BlockBufferCollision differential for owned Prince point leaf."""
from pathlib import Path
import hashlib,json,re,subprocess
import audit_prince_pool_1102_v1 as A
import check_hogan_current_bounded_v1 as M
from private_build_outputs_v1 import validate
R,O=A.R,A.O
ROM=R/'build/excitebike-pose-1101-v3/current4.nes'
SHA='cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8'


def main():
 assert A.sha(ROM)==SHA;b=A.scoped_load(ROM);seed=M.fresh(b)
 src=R/'tools/reference/prince_host_point_1102_v1.s'
 pre=''.join(f'{n}=${A.address(b,n):04x}\n'for n in ['BlockBufferAddr','Block_Buffer_1','MTileAttribute'])
 asm=O/'host-point.s';asm.write_text(pre+src.read_text());cfg=O/'host-point.cfg'
 cfg.write_text('MEMORY{M:start=$b9c1,size=$61f,file=%O;}SEGMENTS{HOST:load=M,type=ro;}')
 cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe',asm,'-o',O/'host-point.o'],[cc/'ld65.exe','-C',cfg,O/'host-point.o','-o',O/'host-point.bin','-Ln',O/'host-point.lbl']]:
  cmd=list(map(str,cmd));validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
 code=(O/'host-point.bin').read_bytes();lab={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'host-point.lbl').read_text(),re.M)}
 start=0xb9c1;assert start+len(code)<=0xbfe0
 xadd=b['raw'][A.location(b,'BlockBuffer_X_Adder')];yadd=b['raw'][A.location(b,'BlockBuffer_Y_Adder')]
 costs=[];cases=0
 def leaf(m,x,y):
  m.ram[3][start-0xa000:start-0xa000+len(code)]=code;m.raw_page(1,3);M.put(m,CurrentBank=3)
  for n,v in [('PpQueryX',x),('PpQueryY',y)]:m[lab[n]]=v&255;m[lab[n]+1]=v>>8
  before=bytes(m[:0x8000]);maps=m.rawtags[:];old2=bytes(m.ram[2]);old3=bytes(m.ram[3]);ppu=(m.ppu_addr,m.toggle,m.buffer,m.ppu_reads,bytes(m.vram));c=M.NesMPU(memory=m,pc=lab['PpHostReadPoint']);c.a=85;c.x=0x5a;c.y=0xc7;c.p=0x71;c.sp=224;c.stPushWord(0x5aff);minimum=224
  for _ in range(500):
   if c.pc==0x5b00:break
   minimum=min(minimum,c.sp);assert m[c.pc]!=0,hex(c.pc);c.step()
  else:raise AssertionError('Native point primitive bound')
  assert(c.x,c.y,c.sp)==(0x5a,0xc7,224)
  assert bytes(m.ram[2])==old2 and m.rawtags==maps
  assert bytes(m.ram[3][:start-0xa000])==old3[:start-0xa000]and bytes(m.ram[3][start-0xa000+len(code):])==old3[start-0xa000+len(code):]
  assert ppu==(m.ppu_addr,m.toggle,m.buffer,m.ppu_reads,bytes(m.vram))
  diff=[i for i in [*range(0x2000),*range(0x6000,0x8000)]if m[i]!=before[i]and not 0x101+minimum<=i<0x1e0]
  assert not diff,('Host application/ZP scratch changed',[(hex(i),before[i],m[i])for i in diff][:10],[(n,v)for n,v in m.__dict__.items()if isinstance(v,int)])
  return c.a,c.p&1,c.processorCycles
 attr=A.location(b,'MTileAttribute');base=A.address(b,'Block_Buffer_1');second=A.address(b,'Block_Buffer_2')
 for page in [0,1,2,255]:
  for col in [0,15]:
   for row in [0,1,12]:
    x=page*256+16*col;y=32+16*row;at=(base if page&1==0 else second)+col+16*row
    for tile in range(256):
     m=M.fork(seed);m[at]=tile
     # Genuine native collision selects the coordinate using its current,
     # immutable object adder tables, including page carry at x0.
     player=(x-xadd)&65535;M.put(m,Player_X_Position=player&255,Player_PageLoc=player>>8,Player_Y_Position=(y-yadd)&255)
     native=M.invoke(m,'BlockBufferCollision',a=0,x=0,y=0)
     assert native['A']==tile,(page,col,row,tile,native['A'])
     raw,solid,cy=leaf(m,x,y);want=bool(b['raw'][attr+tile]&1)
     assert(raw,solid)==((tile,1)if want else(0,0)),(page,col,row,tile,raw,solid,want)
     costs.append(cy);cases+=1
 empty=0
 for y in [0,1,31,240,255,256,511,65535]:
  m=M.fork(seed);a,c,cy=leaf(m,255,y);assert(a,c)==(0,0);empty+=1
 q=dict(passed=True,source_CPU_only=True,native_emulator=False,ROM_SHA256=SHA,component_bytes=len(code),code_half_open=[start,start+len(code)],remaining_before_BFE0_header=0xbfe0-start-len(code),actual_native_BlockBufferCollision_pairs=cases,all256_native_metatiles=True,native_adder_bytes=dict(X=xadd,Y=yadd),both_buffer_pages_and_carry_edges=True,offscreen_Y_cases=empty,CPU=[min(costs),max(costs)],host_ZP_application_and_RAM2_preserved=True,scope='Real current fixed native BlockBufferCollision/GetBlockBufferAddr and MTileAttribute authority. Compiled ownedRAM3 primitive independently selects native buffers and returns native solid metatiles; no host active-RAM scratch or old ArTemp is borrowed. This is a terrain primitive, not the21 original world environment bindings, mapped-owner admission, IRQ/raster or full campaign.',bindings={str(p.relative_to(R)):A.sha(p)for p in[Path(__file__),src,ROM,O/'fall-contact-core.bin']})
 (O/'host-point-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
