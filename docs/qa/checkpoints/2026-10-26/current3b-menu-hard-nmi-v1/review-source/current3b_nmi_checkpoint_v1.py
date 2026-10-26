"""Small Git-ready evidence checkpoint only; never stages/builds/launches/installs."""
from pathlib import Path
import argparse, gzip, hashlib, json
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def get(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,z):assert not p.exists();p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();O=a.output.resolve();assert O.is_relative_to((ROOT/'docs/qa/checkpoints').resolve());O.mkdir(parents=True,exist_ok=False)
 final=D/'current3b-nmi-regression-final-v1';assert sha(final/'proof.json')=='c4e92772493e92c2c1b49687ff71b790530d28f45fdb8ff3f6186c1dcf8d68f0';f=get(final/'proof.json');assert f['passed']is False and f['mechanical_regression_passed']and not f['exact_all_frame_RGB_identity_gate_passed']
 bindings=get(final/'bindings.json');assert len(bindings)==4542 and all(sha(path)==h for path,h in bindings.items())
 ready=D/'current3b-nmi-regression-ready-v2';prepared=D/'current3b-nmi-regression-prepared-v1';menu=prepared/'menu/baseline-early';hard=prepared/'hard1f';baseline=D/'root-clean731-hard1f-v1/fixture';visual=D/'current3b-menu375-readonly-v1';rgb=D/'current3b-nmi-menu-result-v1';root_review=D/'root-current-roster-composition-v1/ROOT-native-review-v1.json'
 assert sha(root_review)=='c842502ee190ad7e211a812b99d66bf94cf2f6d3b31fc9a4b2b94f63243e19e2';assert get(hard/'proof.json')['cases'][0]['dmcStarts']==0
 entries=[]
 def copy(src,name,role,compressed=False):
  src=Path(src);dest=O/name;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();raw=src.read_bytes();dest.write_bytes(gzip.compress(raw,mtime=0)if compressed else raw)
  assert(gzip.decompress(dest.read_bytes())if compressed else dest.read_bytes())==raw
  entries.append(dict(file=name,role=role,original_external_or_repository_file=str(src.resolve()),original_sha256=sha(src),payload_sha256=sha(dest),payload_bytes=dest.stat().st_size,encoding='gzip; exact original bytes after decompression'if compressed else'exact original bytes'))
 copy(final/'proof.json','receipts/final-native-components.json','Exact final receipt:mechanicalPASS, original all-frameRGB_FALSE')
 copy(final/'bindings.json','receipts/final-4542-bindings.json.gz','Complete frozen external artifact manifest; many named payloads intentionally external',True)
 for name in ['native-result.json','hud-native-result.json','scroll-native-result.json','lifecycle-native-result.json','lifecycle-init-native-result.json','hud-lease-native-result.json','menu-timing-native-result.json','regression-launch.json','regression-result.json']:
  copy(menu/name,'menu/'+name,'Exact actual3b menu1800 native receipt/consumed launch')
 for src,name in [(hard/'proof.json','actual-game-proof.json'),(hard/'regression-result.json','regression-result.json'),(hard/'regression-launch.json','regression-launch.json'),(hard/'regression-comparison/proof.json','source-hardware-cadence-proof.json'),(hard/'source-register-image.csv','source-register-image.csv'),(hard/'requests.csv','requests.csv'),(hard/'dmc-fetch.csv','dmc-fetch.csv'),(hard/'apu.csv','apu.csv'),(hard/'cadence.csv','cadence.csv')]:
  copy(src,'hard1f/'+name,'Exact Hard1F240 actual native/source/hardware/cadence evidence; DMCstarts0')
 copy(hard/'regression-comparison/source-model.json','hard1f/source-model.json.gz','Exact280tick/280flush original-executable oracle, raw400F retained',True)
 for name in ['proof.json','apu.csv','cadence.csv']:
  copy(baseline/name,'historical731-Hard1F/'+name,'Historical731 baseline, not retagged as3b')
 copy(D/'parodius-menu-clean731-native-final-v1/proof.json','historical731-menu/proof.json','Historical731 menu final proof1300completedDMAs, separate source/visual scope')
 copy(rgb/'proof.json','RGB-FALSE/original-all-frame-identity-proof.json','Exact original FALSE retained')
 copy(rgb/'counts-and-timing.json','RGB-FALSE/counts-and-timing.json','Exact baseline/current counters, all matching')
 copy(rgb/'raw-frame-comparison.json','RGB-FALSE/all1651-frame-hash-comparison.json.gz','Exact full raw-frame comparison metadata; NO raw frame media',True)
 for name in ['proof.json','bindings.json','actual-observations-and-source.json','all39-differing-pixels.json','actual-whole375-before-after.png']:
  copy(visual/name,'frame375/'+name,'Exact27-fact attribution/one actual wholeframe pair; missing early-store fields explicit')
 copy(root_review,'ROOT-independent-native-review.json','Exact ROOT independent judgment accepts forced-blank difference for this menu regression; not all-roster adoption')
 for name in ['readiness.json','command.json','seal.json','ROOT-menu-grant.json','ROOT-hard1f-grant.json']:
  copy(ready/name,'preparation/'+name,'Exact reviewed readiness/commands/two consumed grant receipts; MUST NOT rerun')
 for name in ['current3b_nmi_regression_run_v1.py','current3b_nmi_menu_result_v1.py','current3b_menu375_readonly_v1.py','current3b_nmi_regression_final_v1.py','current3b_nmi_checkpoint_v1.py']:
  copy(ROOT/'tools/audit'/name,'review-source/'+name,'Frozen launcher/read-only comparison/packaging source; dependencies/external fixtures not bundled')
 copy(ROOT/'docs/qa/current3b-nmi-regression-native-2026-10-26.txt','native-scope-report.txt','Exact finite component report with Hard actualDMC0 and missing early375 writes')
 readme='''Combined3b menu + Hard1F regression checkpoint

Exact candidate:3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287
This checkpoint contains existing evidence only. No new native/build/settings,
source/default/Downloads/Git operations were performed to create it.

MENU1800:the original six guards plus ungated timing PASS.1122updates,
1000semanticDMAs,1300completedfull256DMAs,945safeenables,0late/0mismatch,
minSP197; original allfourship/cancel/title/reentry controls retained.

EXACT RGB IDENTITY:FALSE remains unchanged.1650/1651 complete raw frames match
the historical731 capture. Frame375 differs39pixels at the forced-blank
purple-to-black initialization boundary, first255,39. The actual whole pair
is frame375/actual-whole375-before-after.png, with a contrasting separator.
Both actual startPPUstate/palette/CHR/OAM match, mask6/BGoff/spritesoff; the
ungated enable logger records no render-enable375. Exact early RAM and
pre440 PPUMASK/PPUDATA write timestamps were not captured. No first-store
cause is fabricated and no automatic visualPASS replaces the FALSE.

ROOT independently viewed the actual pair and accepted this forced-blank
timing discrepancy for THIS menu regression. See its exact separate review.
That judgment is neither the automated identity result nor full-roster or
final adoption. The ROOT review includes separately scoped Bass context;
that context is not an additional test performed by this checkpoint.

HARD1F240:actual numericHard1,240updates/168draws,280source ticks and280complete
mixerflushes,850identical checked raw APUstores. Strict cadence matches731:
no cumulative draw-prefix deferrals, same longest no-draw/no-update2.
Seven real source1F requests.168strictcompletedDMA/166originalcompleteDMA
checks/3360hardwareCHRchecks/minSP203. Existing1F adapter order is declared;
raw400F/hardware values are not masked.

HARD ACTUAL DMC STARTS=0; SOURCE PAYLOAD CHECKS=0. Retained DMC guards do not
constitute new active-DMC fetch or waveform qualification. This is the
original staged noise-pressure control, not natural level completion.

Both grants were consumed once, sequentially; zero retries, workers released.
No new acceptance gate,39pixel patch, all-roster campaign/item/graphics/music
completion, reduced-lag, or adoption claim is introduced.

Review map:review-files.json identifies every payload's role, original path,
and exact SHA. *.json.gz files decompress to the exact original JSON bytes;
Python gzip.decompress(Path(file).read_bytes()) can be used for inspection.
checkpoint.json binds the review map and package manifest.

REPRODUCTION LIMITS
This is a compact evidence checkpoint, not a self-contained emulator fixture.
ROMs/debug symbols, original CV3 ROM/NSF/DMC samples, emulator binaries/settings,
complete generated native Lua/configuration and raw frame/video/audio captures
are deliberately excluded. The native Lua configuration includes authenticated
sample metadata, so it is not copied here. Full frozen external paths and
hashes are retained in receipts/final-4542-bindings.json.gz. Original source
oracles and static observer dependencies remain in the repository/external
archive at those bindings. Executable test reproduction needs those exact
external assets and a NEW explicit grant/new output fixture: existing grants
and one-shot paths are consumed and must never be rerun. Packaged source is
for review; its imports/reference paths are not rewritten to imply portability.
The baseline731 receipts remain historical; no native result is retagged.

No raw media bundle is included. The only image is the requested actual375
whole before/after pair, rendered directly from the two frozen raw frames.
'''
 (O/'README.txt').write_bytes(readme.encode())
 put(O/'review-files.json',entries)
 manifest={f.relative_to(O).as_posix():dict(bytes=f.stat().st_size,sha256=sha(f))for f in sorted(O.rglob('*'))if f.is_file()};put(O/'manifest.json',manifest)
 put(O/'checkpoint.json',dict(checkpoint_created=True,evidence_only=True,ROM_sha256=f['ROM_sha256'],native_mechanical_components_pass=True,original_all_frame_RGB_identity_pass=False,ROOT_forced_blank_transition_acceptance='Exact independent judgment in ROOT-independent-native-review.json; not an automatic gate change or all-roster adoption.',Hard_actual_DMC_starts=0,Hard_source_payload_checks=0,launches=2,retries=0,native_workers_released=True,new_native_build_source_settings_Git_operations=False,original_final_proof_sha256=sha(final/'proof.json'),original_ROOT_review_sha256=sha(root_review),review_files_sha256=sha(O/'review-files.json'),manifest_sha256=sha(O/'manifest.json'),raw_media_bundles_included=False,external_reproduction_limits='README.txt'))
 size=sum(p.stat().st_size for p in O.rglob('*')if p.is_file());assert size<1_000_000,size
 for name,row in manifest.items():assert sha(O/name)==row['sha256']and(O/name).stat().st_size==row['bytes']
 print(json.dumps(dict(checkpoint=str(O),files=sum(1 for p in O.rglob('*')if p.is_file()),bytes=size,checkpoint_sha256=sha(O/'checkpoint.json'),manifest_sha256=sha(O/'manifest.json'),review_files_sha256=sha(O/'review-files.json')),indent=2))
if __name__=='__main__':main()
