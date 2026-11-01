"""Compact, explicitly unintegrated combat source/proof handoff."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2];O=R/'build/karnov-combat-component-1101-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')

def main():
 a=json.loads((O/'assembly-stage.json').read_text());q=json.loads((O/'combat-CPU-controls.json').read_text())
 assert a['passed']and q['passed']and q['runtime_ID']==34
 for proof in [a,q]:
  for p,h in proof['bindings'].items():assert sha(p)==h,p
 assert a['kernel_bytes']==12 and a['resident_bytes']==1040 and a['context_C2']==[0xc840,0xc860]
 assert[a['native_imports']['R'+str(i)]for i in range(8)]==list(range(3,11))
 for n in ['GetBlockBufferAddr','BlockBumpedChk','RelativeEnemyPosition','GetEnemyOffscreenBits','SprObjectCollisionCore','HandleEnemyFBallCol']:
  assert a['native_imports']['KC_'+n+'_BANK']==254
 assert q['minimum_service_ISR_SP']-0x7b>=12
 text=f'''# Karnov native contacts, proposed C2 component

This is an independently assembled/tested component. It changes no parent
ROM, loader, service table, menu or installed nightly. CPU fixtures explicitly
load the new1040B worker and12B wrapper. Parent input is
`{a['parent_ROM_sha256']}`.

## Placement and admission contracts

- Proposed selected-C2 code C900..CD0F (1040B), below D000 copied metasprites.
  This is a private-WRAM code proposal, **not a funded ROM/carrier lease**.
  Root must prove the carrier, copy and verify code before publishing the C2
  cookie, and include source bytes in the new authenticated revision.
- Wrapper/reset uses12B at the parent KrKernelEnd in selected A3. Reassemble
  against final source placement; existing source payloads are not copied.
- Private foreground context C840..C85F is32B. It does not overlap pickup
  C860..C864. Block and enemy-only temporaries deliberately share bytes.
- Alias genuine weapons service4 and weapon-tail34 to KrCombat. Call only
  after source actor/weapons movement. This pass never advances source clocks
  or projectile positions. It accepts actual runtime34, readyA7, OperMode1,
  engine8, unpaused, and this frame's completed movement epoch. Own epoch gate
  makes4+34 once-only. Call KrCombatReset at construction/explicit shot reset.
- Native A9 effect-core adapter executes from C2, saves only old CurrentBank
  on the stack, publishes A9 shadow/hardware, calls the actual native head
  effect core and restores A. The outer authenticated dispatcher owns SMC
  restoration. Fixed-window native targets use asserted fixed JSRs. Native
  A0 box and A8 block-slot owners keep genuine FarCallCommon ingress.

## Source and host collision boundaries

Original source slots are not interchangeable: weapon0 uses0/9/18, weapon1
adds3/12/21, weapon2 adds6/15/24. The contact pass filters those columns.
Weapon8 uses record0 only; its phase bytes are not projectile records.
Normal impact uses original `(status & C0)|18`; original source update owns
all decay. Boomerang retains original motion flags and damages each canonical
native enemy slot once per throw. A reused enemy slot during that throw stays
masked; generation tracking is not implemented.

Original source viewport X is converted using the camera sampled before motion;
current native camera supplies enemy relative boxes. A center(+4,+4) native map
cell and8x8 native enemy box are explicit SMB adaptations. Native owners retain
ground/pipe protection, terrain52 parsing, busy block-slot protection, brick
debris/question rewards, Bowser aliases/HP, native immunities, defeat/score and
SFX. Complete foreground R0..R7, ObjectOffset, borrowed native box and player
proxy fields are restored. NMI scratch0..2 is never borrowed by this source.

## Verification and remaining gates

- {q['nine_shot_six_enemy_direction_cases']} nine-slot/direction/native-enemy-slot contacts.
- {q['block_proxy_cases']} brick/question proxy cases across pages, X/Y; exact native block
  and score-popup origins; ground/pipe/hidden/coin/terrain52 safety.
- {q['original_impact_decay_cases']} legal impact cases, {q['original_impact_decay_updates']} updates compared against the
  actual original executable. No invented velocity/timer.
- {q['real_ISR_cuts']} real IRQ/NMI service cuts preserve complete SMC, live ABI and source
  banks. Native NMI may consume the already-verified SFX queue normally.
- Service entry SP224 minimum ISR SP{q['minimum_service_ISR_SP']}: exactly
  {q['service_ISR_bytes_above_SMC']} bytes above the highest SMC byte7B, meeting12B service-level reserve.

**Actual Main entry stack depth is not proved here.** Root must run full Main
cuts after service composition; one byte of spare reserve beyond the required
12 is not permission to ignore extra Main nesting. No native emulator,
full-level, acoustic, health/earned-progression or nightly qualification.

Earlier development routes using an extra BillRare/native FarCall wrapper or
the legacy raw7+alt fixture had inadequate stack reserve. Those are rejected
designs, not supported entry points. Current source explicitly rejects raw7
effects, removes redundant fixed-window far calls, and uses actual runtime34.

No PRG lease was inferred from FF bytes. A proposed LinkGfx tail was rejected
when full linked ownership revealed BILL_ORBIT_6. All existing parent ROM and
source files remain untouched.
'''
 (O/'HANDOFF.md').write_text(text,encoding='utf-8')
 files=[Path(__file__).resolve(),R/'tools/reference/karnov_combat_1101_v2.inc',R/'tools/audit/build_karnov_combat_component_1101_v2.py',R/'tools/audit/check_karnov_combat_component_1101_v2.py']+[O/n for n in ['component.s','component.cfg','bindings.s','component.lbl','component.dbg','kernel.bin','resident.bin','assembly-stage.json','combat-CPU-controls.json','build-commands.json','HANDOFF.md']]
 save(O/'handoff.json',dict(passed=True,source_CPU_only=True,native=False,installed=False,parent_ROM_sha256=a['parent_ROM_sha256'],code_C2=[0xc900,0xcd10],context_C2=[0xc840,0xc860],A3_wrapper_bytes=12,carrier_funded=False,loader_implemented=False,Main_stack_qualified=False,service_ISR_minimum_SP=q['minimum_service_ISR_SP'],service_ISR_bytes_above_SMC=q['service_ISR_bytes_above_SMC'],proof=dict(contact_cases=108,block_cases=108,decay_updates=432,real_ISR_cuts=q['real_ISR_cuts']),bindings={str(p.resolve()):sha(p)for p in files}))
 files.append(O/'handoff.json')
 z=O/'source-and-proof.zip'
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as out:
  for p in files:out.write(p,p.relative_to(R).as_posix())
 save(O/'publication.json',dict(passed=True,path=z.as_posix(),sha256=sha(z),bytes=z.stat().st_size,members=len(files),root_build_modified=False,installed=False))
 print(json.dumps(dict(passed=True,path=z.as_posix(),sha256=sha(z),bytes=z.stat().st_size,members=len(files))))

if __name__=='__main__':main()
