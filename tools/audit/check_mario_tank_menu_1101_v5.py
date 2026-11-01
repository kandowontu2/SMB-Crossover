"""Current90 native menu identities plus new Tank cycle/conditional cache exit."""
from pathlib import Path
import hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_mario_tank_visible_1101_v5 import O,P,PIN
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
import check_hogan_current_bounded_v1 as M
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 old=scoped_load(P/'candidate.nes');assert sha(old['raw'])==PIN;new=dict(old,raw=(O/'candidate.nes').read_bytes());cookie=(O/'cookie.bin').read_bytes()
 counts=[7,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,4,4,4,2,2,4,1,2,8,1,2,1,6,2,4,2]
 a=M.fresh(old);b=M.fresh(new);cases=0;draw=0
 def persistent(m):
  # Name pointers and finalfarcall target are native draw-local scratch.
  # Every payload bank, scene/health/gear/lives/options byte, OAM and VRAM
  # packet remains part of the exact full-state comparison.
  omit=set(range(0x100,0x200))|set(range(0x2000,0x5c00))|set(range(address(old,'R0'),address(old,'R0')+8))|{address(old,n)for n in['CurrentBank','CurrentBankC','safecall_a']}
  return bytes(v for i,v in enumerate(m[:0x8000])if i not in omit),[bytes(r)for r in m.ram]
 for slot,count in enumerate(counts):
  left=M.fork(a);right=M.fork(b)
  for m in [left,right]:
   M.put(m,CrossoverMenuIndex=slot);M.invoke(m,'MenuResolveCharacter');M.invoke(m,'QueueSelection');M.invoke(m,'DrawSelectionPreview')
  for variant in range(count):
   if variant:
    for m in [left,right]:M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0);M.invoke(m,'CrossoverMenuInput')
   assert persistent(left)==persistent(right),('Current90 full native menu mismatch',slot,variant)
   for name in ['SelectedCharacter','MarioVariant','FmAlts','CrossoverMenuIndex','CrossoverMenuState']:assert M.get(left,name)==M.get(right,name)
   pending=bool(M.invoke(right,'FmPending')['P']&1);oldpending=bool(M.invoke(left,'FmPending')['P']&1);assert pending==oldpending
   for buttons,flags in itertools.product([16,128],[0x30,0x31,0x71,0xf9]):
    x=M.fork(left);y=M.fork(right)
    for m in [x,y]:M.put(m,CrossoverMenuButtons=0,SavedJoypad1Bits=buttons,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0);M.invoke(m,'CrossoverMenuInput',p=flags)
    assert persistent(x)==persistent(y),(slot,variant,buttons,flags,'NativeStart admission')
    draw+=1
   cases+=1
 assert cases==90 and draw==720
 # A normal Select away from Tank always traverses the real resolver and
 # cancels only our complete header before any next character constructor.
 retired=0
 for complete,buttons in itertools.product([False,True],[1,2,4,8,32]):
  m=M.fork(b);M.put(m,CrossoverMenuIndex=0,MarioVariant=7);M.invoke(m,'MenuResolveCharacter');M.invoke(m,'QueueSelection');m.ram[2][0x1fe0:0x1ff0]=cookie
  if not complete:m.ram[2][0x1fe3]^=1
  before=bytes(m.ram[2]);M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=buttons,SavedJoypad2Bits=0);M.invoke(m,'CrossoverMenuInput')
  # No-op Dpad direction at a boundary may leave selection unchanged; then
  # no cache owner changed and retaining a complete header is correct.
  changed=M.get(m,'SelectedCharacter')!=0 or M.get(m,'MarioVariant')!=7
  if changed and complete:assert m.ram[2][0x1fe0]==0
  else:assert m.ram[2][0x1fe0]==before[0x1fe0]
  assert bytes(m.ram[2][:0x1fe0])+bytes(m.ram[2][0x1fe1:])==before[:0x1fe0]+before[0x1fe1:]
  retired+=1
 q=dict(passed=True,base_ROM_sha256=PIN,current_ROM_sha256=sha(new['raw']),old_native_menu_identities=cases,old_exact_Start_control_cases=draw,complete_or_incomplete_Tank_exit_cases=retired,all_old_persistent_health_gear_lives_options_scene_and_payload_state_exact=True,intended_old_menu_local_difference='Toad/Peach R2/R3 name pointer moves fromBFE0 toB0D0; emitted glyph bytes unchanged.',added_Tank_private=True,full_owning_relink=False,native_Mesen=False,installed=False,bindings={str(Path(__file__).relative_to(R)):sha(Path(__file__).read_bytes())})
 (O/'menu-CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
