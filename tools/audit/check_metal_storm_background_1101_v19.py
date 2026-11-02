"""Execute the assembled palette uploader across areas and queue boundaries."""
import itertools,json,re
import prepare_metal_storm_background_1101_v19 as P
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU

def main():
 q=json.loads((P.O/'assembly.json').read_text())
 for p,h in q['bindings'].items():assert P.sha(p)==h,p
 b=scoped_load(P.O/'candidate.nes');seed=M.fresh(b)
 labels={m[2]:int(m[1],16) for line in (P.O/'component.lbl').read_text().splitlines() if (m:=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)',line))}
 render=(P.O/'native-render.bin').read_bytes();seed.ram[2][0xd00:0xd00+len(render)]=render
 seed.raw_page(2,2);bg=bytes.fromhex(q['native_background_bytes']);count=0
 for area,ctrl,off in itertools.product(range(4),range(8),[0,65,71,72,80]):
  m=M.fork(seed);M.put(m,AreaType=area,BackgroundColorCtrl=ctrl,VRAM_Buffer1_Offset=off)
  start=address(b,'VRAM_Buffer1');m[start:start+84]=[0x55]*84
  for i in range(8):m[i]=i*17
  zp=bytes(m[:8]);c=NesMPU(memory=m,pc=labels['MsRenderColors']);c.a,c.x,c.y,c.p,c.sp=85,7,91,0x70,224;c.stPushWord(0x5afe)
  for _ in range(2000):
   if c.pc==0x5aff:break
   assert m[c.pc]!=0,hex(c.pc);c.step()
  else:raise AssertionError('palette bound')
  assert c.sp==224 and (c.a,c.x,c.y)==(85,7,91) and bytes(m[:8])==zp
  expected=bytearray([0x55]*84)
  if off<72:expected[off:off+8]=bytes([0x3f,0x10,4,bg[ctrl or area],38,32,15,0])
  assert bytes(m[start:start+84])==expected,(area,ctrl,off)
  assert M.get(m,'VRAM_Buffer1_Offset')==off+(7 if off<72 else 0)
  count+=1
 result=dict(passed=True,ROM_sha256=q['ROM_sha256'],palette_queue_cases=count,scope='Actual renderer opcodes, area colors, boundary refusal, AX/Y and zero-page preservation. Native smoke separately checks cold-loader fingerprint and display.')
 (P.O/'palette-CPU.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
