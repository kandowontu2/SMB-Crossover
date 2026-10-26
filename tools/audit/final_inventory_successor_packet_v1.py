"""Freeze final3b112 source-ready galleries, no native permission or launch."""
from pathlib import Path
import argparse,hashlib,json,shutil
from final_item_abilities_static_prepare_v2 import D,ROOT
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);ready=D/'current3b112-bass-gallery-ready-v1';source=D/'root-current-roster-composition-v1';z=json.loads((ready/'proof.json').read_text());assert z['prepared']and not z['native_run']
 for q in z['profiles']:assert not(Path(q['output'])/'launch.json').exists()
 report=ROOT/'docs/qa/final-inventory-successor3b112-source-2026-10-26.txt';report.write_text('''Finalcombined3b112 Bassgallery SOURCE readiness - NO native launch
2026-10-26
ROM3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287.
Sourcefreeze D/root-current-roster-composition-v1/ROOT-source-readiness.json SHAa332aec91cb2b16f8064c2423b2e0f3d5bbc9603325c0e06e4f0965d0386c220 is authoritative. All869frozen sourceinputs and15ROOTbindings independently rehashed. ComponentC950/A957 keep their exacthashes/scopes. FinalROM is exact7aad exceptbank66 from9ee; ROOT fresh152fullNMI/68fullHUD andordinaryd444/f4ffd sourcecontrols pass. These are not finalnativegallery or FPS claims. No standalone7aadnative-ready wascreated.

Two finite same16plan profiles prepared: BassEasy0 first, BassHard1 onlyafterseparateROOTgrant/review. One worker/oneattempt/profile, no retry/automaticnext. CompleteB-only seeded inventory/resources/actors/arena policy remainsoriginal; no acquisition claim. Defaultfreebuster andseven specials bothfacings withrealcontrollerselection/cost/contact/pool/exhaust/refusal/cleanup remainunchanged. BALANCE/ARMquestionblock remainexcluded.

EntireLua body AFTER configuration is byteexact to qualified30a1 script, includingall original mechanics/inputpolicy/caps/stop/finalizer/staticcallback/E008full256/actualPPU/IRQ31/CHR/5SMC/stack/deadline/defaultNTblankglyphoracle andcorrectedread-only diagnostic850..950. OnlyROM/source/config/hook/RAM metadata refreshed fromactual3b112linked debug/bytes. Allrecord/header/name/cost/icon sourceexpectations checked againstactualROM. Bothscripts have72startupcallbacks/finalstaticdispatcher last/3endFrame callbacks andrawdiagnosticbeforestrictdeadline. Focusboundarymodels849/850/945/950/951 pass; no emulatedwrites/APIregistration added.

Freshfinalhash180compiled sourceeffect/cost/pool/selection/damage controls,8staticreturn and13DMAprotocol controls pass. Originaldefaultbehaviororacle isliteralunchanged; its originalpositive/negativecontrols remainbound ratherthanretaggednewnative. Actualall256hardware/fullPPU/HUD/effect/CHRepochs/cadence/sourcecontact/audio scope mustbeobservedaftergrant. Components andcorrectedsource do NOTclose old731/69ae/30a1FALSEs, which remainimmutable.

Portableeffectivehardware8sprites/adaptiveoff/runahead0/noextrascanlines/AllZeros/nonrandom/noSave/currentworker+usercontext hashes boundfresh. No userconfig/primarysource/default/Downloads/Git mutation. Currentinstalledparent641 isunchanged bypreparation. C reports exactorderedwrites/palettereads/joypadvaluesandcounts, not everyCPU IOread;9ee450had402draws equalparent, notFPSgain; nonbasicremainderadds6CPU/shot. TinyHUD/bodyvisibility/fullitems/campaign/sourcefidelity remainopen.

D=C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py.
Ready D/current3b112-bass-gallery-ready-v1/proof.json andmanifest.json.
ONE-SHOT stablecommands (NOgrantfromreadiness):
python -B tools/audit/final_inventory_successor_gallery_run_v1.py --ready "C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/current3b112-bass-gallery-ready-v1" --profile bass-easy --native-grant
python -B tools/audit/final_inventory_successor_gallery_run_v1.py --ready "C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/current3b112-bass-gallery-ready-v1" --profile bass-hard --native-grant
''',encoding='utf-8')
 cp=ROOT/'docs/qa/checkpoints/2026-10-26/inventory-successor3b112-source';cp.mkdir(parents=True,exist_ok=False)
 for src,name in[(source/'ROOT-source-readiness.json','ROOT-combined-source-readiness.json'),(ready/'proof.json','unlaunched-readiness.json'),(ready/'source-controls.json','static-source-controls.json')]:shutil.copy2(src,cp/name)
 (cp/'README.txt').write_text('Finalcombined3b112 source/mockgalleryreadiness ONLY. No nativegrant/launch; Easyfirst thenconditionalHard. AlloldFALSEs retained; componentsnotretagged. Raw/runtime/settings/artifactsexternal. See namedreport and exactbindings.\n',encoding='utf-8')
 payload=[report,*(f for f in cp.iterdir()if f.is_file())];put(cp/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),bytes=f.stat().st_size,sha256=sha(f))for f in sorted(payload,key=str)]))
 files=set(payload+[cp/'manifest.json',Path(__file__),ready/'proof.json',ready/'manifest.json',source/'ROOT-source-readiness.json',source/'ROOT-bindings.json',ROOT/'tools/audit/final_inventory_successor_gallery_ready_v1.py',ROOT/'tools/audit/final_inventory_successor_gallery_run_v1.py'])
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),bytes=f.stat().st_size,sha256=sha(f))for f in sorted(files,key=str)]))
 proof=dict(passed=True,source_only=True,native_run=False,native_granted=False,ROM_sha256=z['ROM_sha256'],readiness_sha256=sha(ready/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),report_sha256=sha(report),checkpoint_manifest_sha256=sha(cp/'manifest.json'),limits='No nativefinalhash/graphics/deadline/gallery/adoption claim. Exact oldfailures/components/source scopes retained.')
 put(a.output/'proof.json',proof)
 for q in json.loads((a.output/'manifest.json').read_text())['bindings']:assert sha(q['path'])==q['sha256']
 print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),report_sha256=sha(report),checkpoint_manifest_sha256=sha(cp/'manifest.json')),indent=2))
if __name__=='__main__':main()
