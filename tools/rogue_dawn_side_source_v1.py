"""Genuine original horizontal scan, with an explicit external floor boundary."""
from pathlib import Path
import itertools,json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
import rogue_dawn_map_v1 as ref
from py65.devices.mpu6502 import MPU
O=R/'docs/qa/rogue-dawn-original-side-extent-2026-10-29.json'

def scan(raw,y,radius,left,flags):
 m=bytearray(ref.cpu_image(raw,lower_bank=2));m[0x301]=radius;m[0x302]=4
 # Both genuine side gateways test only an aligned horizontal edge.
 m[0x30d]=y;m[0x30e]=92;m[0x4b]=0;m[0x49]=0;m[0x55]=1
 c=MPU(memory=m,pc=0xe88b if left else 0xe880);c.sp=224;c.p=flags;c.stPushWord(0x5aff)
 path=[];samples=[]
 for _ in range(2000):
  if c.pc==0x5b00:break
  path.append(c.pc)
  if c.pc==0xe0fb:
   # Actual E89F..E8F0 row count and E90F/E96A/E98E room coordinates run.
   # Only the named original room decoder/property boundary is external.
   row=m[2]&0xf8;samples.append(row);c.a=0 if row>=208 else 0xa0
   c.pc=(c.stPopWord()+1)&65535;continue
  if c.pc==0x95c0:
   c.pc=(c.stPopWord()+1)&65535;continue
  if c.pc==0xd651:
   c.p=(c.p&~1)|int(c.a>=0xa0);c.pc=(c.stPopWord()+1)&65535;continue
  assert m[c.pc]!=0,hex(c.pc)
  c.step()
 else:raise AssertionError('Original horizontal scan timeout')
 expected=list(range((y-radius)&0xf8,((y+radius-1)&0xf8)+1,8))
 blocked=any(a>=208 for a in expected)
 if blocked:expected=expected[:next(i for i,a in enumerate(expected)if a>=208)+1]
 assert samples==expected,(y,radius,left,samples,expected)
 assert bool(c.p&1)==(not blocked)
 return dict(centerY=y,radiusY=radius,facing='left'if left else'right',flags=flags,
  half_open_extent=[y-radius,y+radius],actual_original_cell_rows=samples,
  carry_clear_blocked=blocked,source_path=[hex(a)for a in path])

def main():
 assert not O.exists(),'Frozen original proof'
 raw=ref.ROM.read_bytes();assert ref.digest(raw)==ref.EXPECTED
 rows=[scan(raw,208-r+d,r,left,p)for r,d,left,p in itertools.product([4,8,15],[-1,0,1],[False,True],[0x30,0x31,0x70,0x71])]
 out=dict(passed=True,source_CPU_only=True,native_run=False,cases=len(rows),rows=rows,
  finding='Actual E89F/E8A3/E8AD/E8CE calculates every 8px row intersecting [center-radius,center+radius). At center193/radius15 the final row is200, not208; a floor at208 is not a side wall. One pixel of actual overlap reaches208 and blocks.',
  boundary='Real original E880/E88B through E7DE/E96A/E98E scan executes. E0FB room decoding, 95C0 room reaction and D651 solid-property classification are explicit external legal floor208 callbacks, not fabricated source room RAM or native snapshots.',
  bindings=[ref.binding(p)for p in[Path(__file__),ref.ROM,R/'src/rogue_dawn_host_floor_v4.s']])
 O.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(rows),report=ref.binding(O))))
if __name__=='__main__':main()
