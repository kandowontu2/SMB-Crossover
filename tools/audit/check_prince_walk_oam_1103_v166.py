"""Actual wholeMain native OAM against unchanged original Prince poses."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_backdrop_native_1103_v160 as V
N,O,I=V.N,V.O,V.I


def main():
 e,m,lab=V.first8();base=m.bundle;art=json.loads((O/'source-art.json').read_text());poses={(p['source_frame'],p['source_facing']):p for p in art['poses']};pc=I.address(base,'MetaspriteRenderLoop');bank=((I.location(base,'MetaspriteRenderLoop')-16)//8192)|128
 actual=N.NesMPU;pending=None;rows=[];epoch=0;parts=0
 class Trace(actual):
  def step(self):
   nonlocal pending,parts
   mem=self.memory;tag=mem.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else None
   if pending is not None and(self.pc,self.sp)==pending['ret']:
    row=pending;pending=None;pose=row['pose'];pages=sorted({p['pattern_pair']//32 for p in pose['parts_8x16']})
    for i,p in enumerate(pose['parts_8x16']):
     at=(row['prefix']+row['rotation']+4*i)&255;got=bytes(mem[0x200+at:0x204+at]);x=row['anchorX']+p['x'];y=row['anchorY']+p['y']-1
     if not(0<=x<256 and 0<=y<256):assert got[0]==248
     else:
      tile=pages.index(p['pattern_pair']//32)*64+(p['pattern_pair']%32)*2;assert got==bytes([y,tile,p['attribute'],x]),(epoch,pose['source_frame'],p,got,[y,tile,p['attribute'],x])
     parts+=1
    rows.append(dict(epoch=epoch,frame=pose['source_frame'],facing=pose['source_facing'],nativeY=row['nativeY'],sourceY=row['sourceY'],anchorY=row['anchorY'],anchorX=row['anchorX'],delta=row['delta'],parts=len(pose['parts_8x16']),all_original_native_OAM_exact=True))
   if(self.pc,tag)==(pc,bank)and N.get(mem,'R0')+256*N.get(mem,'R1')==0xc200:
    assert pending is None;frame=mem.ram[2][0x617];face=mem.ram[2][0x615];pose=poses[frame,face];x=N.get(mem,'R4')+256*N.get(mem,'R5');x=x-65536 if x&32768 else x;y=N.get(mem,'R6')+256*N.get(mem,'R7')-256
    ret=((mem[0x101+self.sp]|mem[0x102+self.sp]<<8)+1)&65535
    pending=dict(ret=(ret,self.sp+2),pose=pose,anchorX=x,anchorY=y,nativeY=N.get(mem,'Player_Y_Position'),sourceY=mem.ram[2][0x611],delta=mem.ram[2][0x88],prefix=N.get(mem,'CurrentOAMOffset'),rotation=N.get(mem,'RgOamRotation')if N.get(mem,'GuestOamRotationActive')else 0)
   return super().step()
 N.NesMPU=Trace
 try:
  for epoch in range(49):
   if epoch:m.controller_pad=1;N.put(m,SavedJoypad1Bits=1,SavedJoypadBits=1)
   e['run'](m,'GameLoop',lab);assert pending is None
 finally:N.NesMPU=actual
 assert rows and all(r['anchorY']==205 and r['sourceY']==128 for r in rows)
 q=dict(passed=True,CPU_only=True,source_code_injected=False,ROM_written=False,memory_SHA256=V.M.image()[1]['expected_memory_only_SHA256'],actual_native_body_draws=len(rows),actual_original_OAM_parts_compared=parts,source_anchorY=[min(r['anchorY']for r in rows),max(r['anchorY']for r in rows)],native_playerY=sorted({r['nativeY']for r in rows}),source_pose_delta=sorted({r['delta']for r in rows}),rows=rows,scope='Actual159 first8/49wholeGameLoops call genuine nativeMetaspriteRenderLoop from real PrinceDraw. Every emitted source part immediately compares exact original pixelposition/tile/attribute/order, including actual OAM rotation. RenderY is stable205/sourceY128 and independent of nativePlayerY; original walking poseDelta3/4/5 varies nativecollisionanchor. Grounded nativeY177 still reachescompletedMain in163 and is not reclassified as fixed. This proof establishes no added bodyanchor displacement beyond original pose differences; actual Mesen visual/world/gameplay remains pending.',bindings={p.relative_to(R).as_posix():V.M.sha(p.read_bytes())for p in [Path(__file__),Path(V.__file__),O/'backdrop-manifest-v159.json',O/'source-art.json',O/'pose-grid-native-CPU-v38.json',O/'grounded-order-v163.json',R/'tools/reference/prince_host_lifecycle_1102_v12.s',R/'tools/reference/prince_host_render_1102_v1.s']})
 (O/'walk-oam-CPU-v166.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','rows']}))


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'walk-oam-negative-v166.json').write_text(json.dumps(dict(passed=False,exception=repr(error)),indent=2)+'\n');raise
