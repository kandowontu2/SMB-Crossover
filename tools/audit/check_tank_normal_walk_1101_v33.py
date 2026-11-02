import json
import prepare_tank_normal_walk_1101_v33 as P
import check_hogan_current_bounded_v1 as M
from verify_native_relocation import NesMPU

def main():
 b=P.scoped_load(P.O/'candidate.nes');q=json.loads((P.O/'assembly.json').read_text());native=int.from_bytes(bytes.fromhex(q['old_call'])[4:5]+bytes.fromhex(q['old_call'])[9:10],'little')
 for variant in range(256):
  m=M.fresh(b);M.put(m,SelectedCharacter=0,MarioVariant=variant,MegaManShotPose=9)
  pc=q['helper_PC'];m[P.address(b,'SafecallA_SMC')+1]=variant;m[P.address(b,'FarcallJmpTarget_SMC')+1]=pc&255;m[P.address(b,'FarcallJmpTarget_SMC')+2]=pc>>8
  c=NesMPU(memory=m,pc=P.address(b,'FarCallCommon'));c.a,c.x,c.y,c.p,c.sp=210,7,91,0x71,224;c.stPushWord(0x5ffe)
  for _ in range(400):
   if c.pc==native and m.rawtags[1]==129:break
   assert m[c.pc]!=0,hex(c.pc);c.step()
  else:raise AssertionError('wrapper bound')
  assert M.get(m,'MegaManShotPose')==(0 if variant==7 else 9),variant
  assert c.x==7 and c.y==91
 old=json.loads((P.R/'build/tank-walk-modes-1101-v32/native/capture/walk-trace.json').read_text())
 new=json.loads((P.O/'native/capture/walk-trace.json').read_text())
 assert len(old)==len(new)==72
 assert all(r['pose'] in [2,3,4] for r in new[1:])
 # World OAM begins after the24-byte body+shoe reservation. The observed
 # projectile's coordinates, tile, attributes and absence/presence match.
 assert all(a['oam'][48:]==b['oam'][48:] for a,b in zip(old[1:],new[1:]))
 binding=json.loads((P.O/'native/capture/binding.json').read_text());assert binding['ROM_sha256']==q['ROM_sha256'] and binding['exit_code']==0
 result=dict(passed=True,ROM_sha256=q['ROM_sha256'],selector_cases=256,native_walk_frames=71,normal_walk_with_and_without_B=True,observed_projectile_OAM_preserved=True,scope='Actual helper dispatch plus native cold selection/powered walk fixture. Persistent shoe glow and broader playthrough remain unfinished.')
 (P.O/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
