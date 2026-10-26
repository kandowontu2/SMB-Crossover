"""Seal the eight-case Samus Hard source proposal; never starts an emulator."""
from pathlib import Path
import argparse, ast, hashlib, json, sys
from final_samus_hard_gallery_source_v1 import D, ROOT, PARENT, SHA
from final_item_abilities_remaining731_run_v1 import verify_manifest
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,x:p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-prepared',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
 a.output.mkdir(parents=True,exist_ok=False);verify_manifest(a.source_prepared/'manifest.json')
 previous=json.loads((a.source_prepared/'proof.json').read_text());assert previous['passed']and previous['source_only']and previous['ROM_sha256']==SHA
 inventory=PARENT/'source-manifest.json';original=json.loads((PARENT/'ROOT-source-readiness.json').read_text());assert sha(inventory)==original['source_manifest_sha256']
 files={inventory,PARENT/'ROOT-source-readiness.json',PARENT/'ROOT-bindings.json',Path(sys.executable)}
 source=json.loads(inventory.read_text());assert len(source)==869
 for name,digest in source.items():
  q=PARENT/'source'/name;assert sha(q)==digest,(name,digest,sha(q));files.add(q)
 controls=json.loads((a.source_prepared/'assembled-gateway-controls.json').read_text());assert controls['passed']and controls['cases']==27
 plans=json.loads((a.source_prepared/'plans.json').read_text());assert plans['lane']=='B controlled real-engine ability use'and not plans['acquisition']and len(plans['plans'])==8 and plans['actual_mode_required']==1
 expected=['starting-short','long-beam','Morph-bombs','missile-Special','Ice','Wave','Varia','Screw'];assert[x['name']for x in plans['plans']]==expected
 hooks=json.loads((a.source_prepared/'compiled-owner-hooks.json').read_text());assert len(hooks)>30
 report=ROOT/'docs/qa/final-samus-hard-gallery-source-2026-10-26.txt'
 report.write_text('''Samus Hard: finite controlled ability gallery source proposal
26 October 2026. Source/assembled CPU only; no Mesen launch or grant.

Exact current parent
3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287
D/root-current-roster-composition-v1/candidate.nes and source.
D = C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py.
ROOT source receipt a332aec91cb2b16f8064c2423b2e0f3d5bbc9603325c0e06e4f0965d0386c220;
all 869 source inputs independently rehashed. No game/source/default/settings/Git changes.

The eight proposed B cases, all numeric Hard1 / Samus2
1 Short: starting unpowered beam; short age12 expiry, normal terrain/contact,
  three shared slots, horizontal both facings and Up.
2 Long: ownership129 (mushroom + Long); range beyond short lifetime, terrain,
  real target contact, three shared slots, actual muzzle/body/shot pixels.
3 Morph/bombs: ownership131; first Down crouch, fresh second Down gated Morph,
  actual exit clearance; separate three bombs, explosion at58 and expiry82,
  boost, block/enemy effects and ball/explosion/SFX observation.
4 Missile: ownership133, seeded2 rounds; real paused direction chooses local2,
  live Select fires Special directly even with default selected. B remains beam.
  One-unit paid admission, actual debit-to0 and clean0 refusal; shared pool
  admission/refusal, actual contact/expiry/HUD. No invented Bass cycle behavior.
5 Ice: ownership137; B produces shared type46, actual ordinary target freeze,
  STOP/blue publication, source360-update thaw, second-hit freeze removal before
  damage, resistant targets and shared pool/terrain/natural shot cleanup.
6 Wave: ownership145; B produces native type3, real page-crossing sinusoid,
  original question-block bypass versus Long impact, target hit/offscreen expiry.
7 Varia: ownership161; real firebar protection plus ordinary-contact negative,
  actual existing third-form body/palette. It does not grant general immunity.
8 Screw: ownership193; real directional jump/spin/body contact, contact-dictionary
  repeat suppression, landing/nonspin/unowned/Bowser/projectile exclusions,
  actual flip art and source one-shot sound latch. No ammo cost is invented.

Explicit seeds and limits
Each case has complete declared legal native GameLoop-boundary scene/player
motion/fractions/previous-input/pool/actor/resource initialization. Resource and
owned-bit seeds are B-use controls, never physical acquisition. Target actors
are full legal actors positioned relative to the actual live effect/body, with
real AI/gravity/contact/damage thereafter; no enemy HP/outcome forcing. Reset
between cases is fixture isolation and is never counted as native cleanup.
No tier, item, actor or controller is being tested by a native run in this packet.

Full owner proof before proposed hooks
27 actual assembled gateway cases /229 complete CPU calls, no mechanics stubs.
Actual RlUiDispatch reaches InventoryUiTick for fresh input; full
ProcFireball_Bubble reaches Z2RemainingWeaponsGate -> RemainingWeapons and then
SamusWeapons. B goes via AvSamusPrimary; Ice uses RemainingWeapons::Spawn,
ordinary/Long/Wave use SamusWeapons::Spawn -> SamusBeamType. Missile goes via
RemainingWeapons::SamusInput -> FireOwned -> InventorySpend -> Spawn.
PlayerMovementSubs reaches SamusMovement and native Morph/Bomb owners.
The actual FirebarCollision path enters GuestInjuryStart only without Varia.
GuestBodyContactBridge traverses the real family wrappers to GuestBodyContact;
the valid Screw case reaches SpinDamage -> MegaManWeapons::DamageEnemy.
PlayerGfxHandler reaches SamusGraphics -> GuestVisualStatus -> RemainingPower.
Every observed owner has its genuine PC/bank/entry-SP/return-PC/return-SP/bank
and complete returned AXYP recorded. These are CPU calls, not native IRQ proof.

The qualified fixed startup return dispatcher and E008 eight-byte post-DMA
protocol will be reused. E005 is explicitly pre-transfer and cannot certify
hardware completion. The inherited literal IRQ31/5SMC/bank/SP/CHR guards and
full raw PPU/DMA logging remain required. Actual legacy ChrPhysicalMap must
be respected for Samus body pages, not an expanded-only page assumption.
The old Samus CHR observer dynamically registers returns and is reference-only;
it must not be executed unchanged. No new generic framework is proposed.

Historical evidence kept at its original hashes
054d Samus mature-actor record has eight grants but only Missile/Ice declared
attacks. It establishes neither natural block emergence nor all passive effects.
The 55 ->84 Wave16 native controls and source/CPU repairs are historical, not
current3b receipts. Old source modes/art/audio limits remain explicit.
Easy is the separate classic Short -> Long -> Wave three-tier policy. Nothing
here relabels modern Hard inventory or seeded B use as Easy or acquisition.
Pinned2.02 obtainable array has Morph/Missile/Ice/Wave/Varia/Screw; mushroom
gives Long. High Jump/missile expansion icons/constants are dormant in that
array, so random acquisition of them is not an expected missing normal item.

Presentation boundary
Current Varia selects the inherited third form/suitless art. Pinned2.02 uses
Power/Varia suit palette rows; that is an explicit existing presentation policy
difference. This gallery will authenticate current supplied art/pixels and
report it, not silently replace it or claim exact2.02 skin fidelity.
Freeze blue uses NES quantization and palette-sharing opportunities; a source
pointer/CHR match alone will not prove opaque-pixel visibility. Every actual
effect/HUD/contact window will require saved full PPU images and agent review.
Queued SFX and actual APU writes can be asserted; waveform/listening fidelity,
all-items/Hard physical acquisition, campaign, global timing and no-flicker are
not certified by this source packet.

Next implementation gate
This is a concrete eight-case plan and verified owner inventory, not native
launch readiness. Implement one scoped mechanics module on the qualified
existing observer/runtime; qualify its exact source/return/controller and
phase-reset expectations before any frozen one-shot command or native grant.
No additional native worker is reserved.
''',encoding='utf-8')
 files.add(report)
 files.update(q for q in a.source_prepared.iterdir()if q.is_file())
 # Pin the actual imported CPU implementation and its local dependencies.
 todo=[Path(__file__),ROOT/'tools/audit/final_samus_hard_gallery_source_v1.py'];seen=set()
 while todo:
  f=todo.pop()
  if f in seen:continue
  seen.add(f);files.add(f)
  for n in ast.walk(ast.parse(f.read_text(encoding='utf-8-sig'))):
   names=[n.module]if isinstance(n,ast.ImportFrom)else[x.name for x in n.names]if isinstance(n,ast.Import)else[]
   for name in names:
    if name:
     q=ROOT/'tools/audit'/(name.split('.')[0]+'.py')
     if q.exists():todo.append(q)
 for name,module in sys.modules.copy().items():
  if name.startswith('py65')and getattr(module,'__file__',None):files.add(Path(module.__file__))
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),bytes=f.stat().st_size,sha256=sha(f))for f in sorted(files,key=str)]))
 proof=dict(passed=True,source_only=True,native_run=False,native_launch_ready=False,native_worker_reserved=False,ROM_sha256=SHA,mode_required=1,B_cases=8,acquisition=False,complete_assembled_gateway_cases=27,complete_CPU_calls=sum(len(r['calls'])for r in controls['rows']),verified_parent_source_inputs=len(source),manifest_sha256=sha(a.output/'manifest.json'),report_sha256=sha(report),source_prepared_proof_sha256=sha(a.source_prepared/'proof.json'),limitations=['No emulator or real controller/IRQ/PPU result.','Eight planned source-specific B cases remain to implement on the existing observer.','Hard Varia third-form/suitless policy difference disclosed; Easy three tiers separate.','Historical evidence immutable and not retagged current3b.'],goal_complete=False)
 put(a.output/'proof.json',proof);verify_manifest(a.output/'manifest.json')
 print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),report_sha256=sha(report),bindings=len(files)),indent=2))

if __name__=='__main__':main()
