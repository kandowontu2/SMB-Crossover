"""Same earned mushroom controls, new qualified native pickup bridge; never run Mesen."""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_native_power_1103_v56 as P
from prepare_selected_native_packet_v1 import prepare,sha
O,R=P.O,P.R
def main():
 q=json.loads((O/'mini-host-v56.json').read_text());irq=json.loads((O/'native-power-v57-ISR.json').read_text())
 assert q['passed']and irq['passed']and irq['kernel_SHA256']==q['SHA256']
 rom=R/'build/mini-power-candidate-root-1103-v56/mini-power.nes';assert sha(rom)==q['expected_memory_only_ROM_SHA256']
 prior=O/'earned-mushroom55';ready=json.loads((prior/'ready.json').read_text());negative=prior/'capture/result.json'
 n=json.loads(negative.read_text());assert not n['passed']and n['earned_power']['native_calls']['HandlePowerUpCollision']>0
 text=(prior/'controller.lua').read_text();old=json.loads((P.P.HOST/'mini-host-v48.json').read_text())
 assert text.count(P.P.PIN)==1 and text.count(old['SHA256'])==1
 text=text.replace(P.P.PIN,q['expected_memory_only_ROM_SHA256']).replace(old['SHA256'],q['SHA256'])
 # Original proven Main/draw/head hook instructions did not move; validate
 # actual new carrier bytes rather than borrowing obsolete hook metadata.
 data=(O/'mini-host-v56.bin').read_bytes();original=(P.P.HOST/'mini-host-v48.bin').read_bytes()
 for name in ['MiniHostMain','MiniStep','MiniAnimate','MiniHostBox','MiniNativeDraw','MiniHostHead']:
  pc=q['labels'][name];assert pc==old['labels'][name]and data[pc-0xa000:pc-0xa000+4]==original[pc-0xa000:pc-0xa000+4]
 anchor="   power.completed=true;power.script_mushroom_wait_frames=30;power.original_transition_timing_qualified=false"
 assert text.count(anchor)==1
 text=text.replace(anchor,"""   check((power.native_calls.MarioSourcePowerupCollision or 0)==1,'Exactly one real whole native collection')
   check((power.native_calls.GuestBeginPowerup or 0)==1,'Exactly one real native power constructor')
   check((power.native_calls.GuestPowerupUpdate or 0)==60 and r('GuestPowerupAge')==60,'All60 actual native power updates complete')
   check(power_item()==nil and power.item_lost~=nil,'Actual earned item consumed')
"""+anchor)
 sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
 from lupa.lua54 import LuaRuntime
 assert LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
 report=O/'earned-power-v58.json';report.write_text(json.dumps(dict(passed=True,prepared_only=True,ROM_SHA256=sha(rom),kernel_SHA256=q['SHA256'],controller_inputs_unchanged=True,retained_negative=negative.relative_to(R).as_posix(),scope='Same54/55 earned block jump and actual mushroom chase. Require one real whole consume/constructor, all60 actual native updates, earned tier1/standing6x15/sourcepowered poses and10 steadyupdates. No seeding, no RAM writes; original30/35 timing/directflower2/projectile fidelity remains unqualified.'),indent=2)+'\n')
 refs=[Path(p)for p in ready['bindings']if Path(p).suffix not in ['.nes']and not Path(p).is_relative_to(R/'docs')]
 refs +=[Path(__file__),negative,report,O/'mini-host-v56.json',O/'mini-host-v56.bin',O/'native-power-v57-ISR.json']
 prepare(O/'earned-mushroom58',rom,text,refs,expected=q['expected_memory_only_ROM_SHA256'],timeout=180,allow_interactive=True,scope='Private hardware qualification of minimal native pickup bridge on exact9d291. Sameearned55 controls; real block release/immature/mature/wholeconsume1/constructor1/update60/tier1/6x15/sourcepoweredposes required. ExistingOAMrotation/reservation/CHR968/PPUpixels/RGB/lives checks retained. TwoPNG/9000physical bound. No claim of original30/35 transformation timing or directflower2/fireprojectiles. Rootalone runs Mesen.')
if __name__=='__main__':main()
