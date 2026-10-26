"""Compact reviewed fixture-only source readiness, originalFALSE retained; no native launch."""
from pathlib import Path
import argparse,hashlib,json,shutil
from final_item_abilities_static_prepare_v2 import D,ROOT
from final_item_abilities_remaining731_run_v1 import verify_manifest
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 ready=D/'current3b112-bass-isolated-ready-v2';r=json.loads((ready/'proof.json').read_text());assert r['prepared']and not r['native_run'];verify_manifest(ready/'manifest.json')
 for q in r['profiles']:assert not(Path(q['output'])/'launch.json').exists()
 report=ROOT/'docs/qa/final-inventory-successor3b112-isolated-source-2026-10-26.txt'
 report.write_text('''Fixture-only3b112 Bass successor SOURCE readiness - NO native grant/run
2026-10-26

ROM3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287 unchanged. Same frozen16plans each Easy0/Hard1; old3759FALSE and earlier731/69ae/30a1FALSEs remain immutable. No game/default/settings/Git edits or new native launches. Hard remains unrun; Easy requires a new separate grant.

Why this is a correction
Actual old source debit3555 proves KICK4to0; actual contact3559 still0. Captured HUD0003558..3564 then native earned credits to040 invalidate final stock==0, not the source ability. Original complete arena setup omitted four InvDrop slots, so prior earned capsules also survived case boundaries. New live enemy drop RNG/HP/behavior is untouched. No fake high HP or drop suppression.

Exact fixture changes
1. At every declared component setup, before changes log current selected stock/refill/remaining and four actual drop kinds/positions. Complete B-only reset clears all four slots'11InvDrop arrays plus4AvDropItem bytes (48bytes), refill/tick/amount/TimerControl and existing declared player/enemy/shot seeds. No drop is erased during native funded play. This is explicit arena initialization, not an acquisition/lifecycle claim.
2. Funded InventorySpend keeps its original before-cost=after/carry assertion and now logs the actual accepted debit reachingzero. It must cumulatively spend at least seededstock; final balance must equal seededstock minus all accepted native debits plus actual earned refill increments. Missingzero, unaccountedcredit or wrongselecteditem fail. A later legal credit does not undo the zero witness.
3. One added startup-only actual InventoryUiTick hook observes full genuine return through the qualified static dispatcher. Any funded stock increase requires currentindex, incomingtick1, exact+4 capped112, remainingminus4/tick3 and genuine completion/index state. Each credit is logged/captured. It uses no emulated writes and changes no sourceCPU timing. Original InventorySpend assertion still catches improper debits.
4. Empty/refusal explicitly initializes selectedammo0 with no drops/refill; unchanged original zero/pool/held/kick refusal assertions remain. Fundedcreditedstock is transparently replaced only at this new isolated B component. Fundedsetupseed and pool112 policy remain unchanged.

What stays literal
All non-gallery Lua bytes after configuration remain exact, including original controller/case set/targets/ability input windows/caps/failure/deadline/E008full256/fullPPU/CHR/IRQ31/5SMC/stack/APU/defaultactualNTblank oracle, completion/finalizers and850..950read-only diagnostics. Gallery reverse-normalizes exactly to old module by the seven bound substitutions. No original spend/carry/contact/charged/orbit/pool/cleanup/refusal guards deleted. One new InventoryUiTick hook is genuinely compiled metadata; all RAM added symbols bind actual linked addresses. No RNG/HP/outcome or mode injection added. Full generated script loads with73startupcallbacks, dispatcherLAST,3endFramecallbacks and no runtime API registration.

Source/mock checks
Twelve finite positive/negative controls per profile (24total): zero debit witness; native0to40 balance; reject missingzero/unaccountedcredit/wrongrefillindex/wrongtick/wrongdelta/creditwithoutzero/wrongitem; all48dropbytes boundaryreset; explicitzero/refillclear; funded4/pool112 preserved. These are synthetic source mechanics, not actual native outcomes. Exact same3b compiled InventoryRefillAmount plus fullUiTick source8/40 controls are bound separately. Original180compiled source ability/effect controls and unchanged strict protocol retain their original hashes in parentready, never retagged as new native.
First isolated preparer v1failed a mock setup because the test current object omitted empty spawns/spends arrays; no emulator launched. V2changes that test object only, real Lua transformation is identical; v1partial outputs/source retained. Prior offline analyzerv1also retains its stale112 expectation error independently.

Runtime and scope
Fresh isolated copies of the original deterministic hardware8sprite/noSave settings are bound, usercontext8a439 and worker627cd unchanged. These B-only seeded scenes test use/cost/graphics/contact/pool/exhaust/refusal/cleanup, not acquisition. First profile must pass actual rawDMA/PPU/effect/HUD/readability review before Hard or adoption; no automaticnext/retries. ARMquestionblock/BALANCE/everyitem/globaltiming/flicker/sourcefidelity/audio waveform remain open.

D=C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py.
Ready D/current3b112-bass-isolated-ready-v2/proof.json; exactfixture-only.patch/source-controls.json/seed-policy-addendum.json bind the finite difference. Originalnegative D/current3b112-bass-gallery-negative-final-v1/proof.json.
Stable one-shot commands (NOT granted by readiness):
python -B tools/audit/final_inventory_successor_gallery_run_v1.py --ready "C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/current3b112-bass-isolated-ready-v2" --profile bass-easy --native-grant
python -B tools/audit/final_inventory_successor_gallery_run_v1.py --ready "C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/current3b112-bass-isolated-ready-v2" --profile bass-hard --native-grant
''',encoding='utf-8')
 cp=ROOT/'docs/qa/checkpoints/2026-10-26/inventory-successor3b112-isolated-source';cp.mkdir(parents=True,exist_ok=False)
 for src,name in[(ready/'proof.json','unlaunched-readiness.json'),(ready/'source-controls.json','fixture-source-controls.json'),(ready/'seed-policy-addendum.json','seed-policy-addendum.json')]:shutil.copy2(src,cp/name)
 (cp/'README.txt').write_text('Fixture-only isolated funded debit/earned-credit and explicit zero-refusal successor. Original3759FALSE retained; no game patch/nativegrant/run/Hard/adoption. Actualsource/inputs/strictguards preserved except documented controlled setup and corrected balance oracle. Rawruntime/captures external.\n',encoding='utf-8')
 payload=[report,*(f for f in cp.iterdir()if f.is_file())];put(cp/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),bytes=f.stat().st_size,sha256=sha(f))for f in sorted(payload,key=str)]))
 files=set(payload+[cp/'manifest.json',Path(__file__),ROOT/'tools/audit/final_inventory_successor_isolated_prepare_v1.py',ROOT/'tools/audit/final_inventory_successor_isolated_prepare_v2.py',ready/'proof.json',ready/'manifest.json',ready/'fixture-only.patch',ready/'exact-transformations.json',ready/'source-controls.json',ready/'seed-policy-addendum.json',D/'current3b112-bass-gallery-negative-final-v1/proof.json',D/'current3b112-bass-gallery-negative-final-v1/manifest.json',D/'current3b112-bass-gallery-negative-v2/compiled-refill-controls.json'])
 files.update(f for f in(D/'current3b112-bass-isolated-ready-v1').rglob('*')if f.is_file())
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),bytes=f.stat().st_size,sha256=sha(f))for f in sorted(files,key=str)]));put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,native_granted=False,ROM_sha256=r['ROM_sha256'],readiness_sha256=sha(ready/'proof.json'),readiness_manifest_sha256=sha(ready/'manifest.json'),readiness_bindings=r['manifest_bindings'],manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),report_sha256=sha(report),checkpoint_manifest_sha256=sha(cp/'manifest.json'),original_native_FALSE_preserved=True,Hard_unrun=True));verify_manifest(a.output/'manifest.json')
 print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),report_sha256=sha(report),checkpoint_manifest_sha256=sha(cp/'manifest.json'),readiness_sha256=sha(ready/'proof.json')),indent=2))
if __name__=='__main__':main()
