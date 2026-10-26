"""Freeze the observed PitEasy component and explicit agent selected-frame review."""
from pathlib import Path
import argparse,csv,hashlib,json,shutil
from final_item_abilities_pit731_run_v1 import verify_manifest
from final_item_abilities_static_prepare_v2 import CURRENT,D,ROOT
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--review',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 q=json.loads((a.ready/'proof.json').read_text());native=Path(q['output']);n=json.loads((native/'native-abilities.json').read_text());r=json.loads((a.review/'proof.json').read_text());assert r['passed'] and r['ROM_sha256']==CURRENT
 ready_count=verify_manifest(a.ready/'manifest.json');review_count=verify_manifest(a.review/'manifest.json')
 put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
 audio=list(csv.DictReader((native/'apu.csv').open()));audio_count=sum(0x4000<=int(z['register'])<=0x4013 or int(z['register'])in[0x4015,0x4017]for z in audio)
 assert len(audio)==10422 and audio_count==4353
 visual=dict(passed=True,ROM_sha256=CURRENT,agent_visual_review=True,actual_selected_whole_frames=129,selected_placements=129,sheets=r['sheets'],findings=[dict(status='no_obvious_anomaly_in_selected_windows',scope='All12sheets/129selected wholeframes inspected: both real item emergence/contact/60-update transforms;6both-facing hammer windows;lower-tier flight refusal;full/partial flight,exhaust,landing,recharge/cleanup. No obvious displaced/green background tiles,whole-background wrap,HUD corruption or ability failure in this sample.')],limitations=['Selected129frames, not all2339actualframes or allposes/sourcepixels.','First arena images can retain an older native OAM publication while staged world/player state has changed; actual saved epoch is retained, not relabeled current-body source.','No original source-art/audio/waveform fidelity, no crowd/8sprite stress closure or no-flicker verdict.','Two physical acquisitions only; no third cap-flower,ordinary B-arrow pool/hit,injury/reacquisition,star/1up or Hard coverage.'])
 put(a.output/'visual-review.json',visual)
 component=dict(identity='Pit',actual_mode='easy',actual_numeric_mode=0,ROM_sha256=CURRENT,track='A+B',native_receipt=str(native/'proof.json'),native_receipt_sha256=sha(native/'proof.json'),A_observed=['real mushroom reveal/rise/contact0→1','real flower reveal/rise/contact1→2','no-premature-grant','two60committed-update transformations'],A_setup='Staged visible/logical world; explicit mature-actor contact alignment only after full native rise.',B_observed=['hammer tiers0/1/2 bothfacings,6real native Goomba hits/defeats and cleanup','tier0/1 fresh airborne A refuses flight','tier2 full60fuel/exactFE8000lift/exhaust/land60recharge/nextgroundjump','tier2 partial19fuel/release/land60recharge'],B_setup='Guarded native update arena/player/motion/pool/protection resets and actual valid Goomba targets, no tier/fuel/flight/outcome writes.',complete_powerup_cell=False,remaining=['capped pickup','ordinary B-arrow firing/contact/pool at tiers','star/1up','damage/downgrade/reacquisition','Hard','full sourcepixel/audio fidelity'])
 put(a.output/'ledger-component.json',component)
 report=ROOT/'docs/qa/final-item-abilities-pit731-native-2026-10-26.txt';assert not report.exists()
 report.write_text(f'''Pit Easy acquired-ability pilot,2026-10-26

Observed component PASS on exact731:
{CURRENT}
ONE launch,exit0,no retry. Worker explicitly RELEASED. No production/default/
settings/Git changes. Other five profiles are unrun and not inferred.

Native receipt {native/'proof.json'}
SHA256 {sha(native/'proof.json')}
Readiness {a.ready/'proof.json'} SHA256 {sha(a.ready/'proof.json')}
Independent offline review {a.review/'proof.json'} SHA256 {sha(a.review/'proof.json')}

Actual Easy numeric0 cold readback; all10original plans complete. Two physical
head/block/reveal/fullrise/no-premature-grant pickups0→1→2 with120committed
transformation updates. Explicit post-rise contact alignment and guarded
world/player/motion/pool/protection/Goomba setup remain disclosed in seed-policy.
No tier/fuel/flight/reach/pogo or ability result injection. A is physical
delivery with stated setup; B is actual acquired-tier use in controlled arenas,
not an unassisted route or earned resource-depletion test.

Six hammer cases each produce one actual type38 enemy contact/defeat and native
cleanup, bothfacings across tiers0/1/2. Tier0/1 flight gates have real airborne
second A attempts,0burn andfuel60. Tier2 fullflight burns60updates to0, lifts
exactFE8000 before integration,exhausts,lands,recharges60 and launches again.
Partial flight burns19updates to41;actualA release cancels,ground recharges60.
Native result counts:2052updates/2051NMI/2052IRQ31stores/minSP203;
24612hardwareCHRbank-latchchecks and2022old publication-endFrame checks.

Full actual PPU:2339frames,574832640rawbytes, SHA256
7a8e551933a6a954431e05b58002f5cedef3076711fcd306156587c8caebf6be.
All43original case screenshots match their exact recorded endFrame raw slice.
Mapping is proved from actual recorder order/index/bytes, not guessed labels:
capture-event wall equals recorder ordinal; foreground sample wall maps to next
endFrame ordinalwall+1. Actual PPU frame/scanline/dot/CPU are retained perindex.
Body/source flags can precede displayed publication; sampled firstarena carry
is not silently reclassified as a new body image.

All2293completedDMA epochs are independently reparsed:587008actual data writes,
exact256source/hardware,0..255destinations,renderingdisabled throughout,E008
afterrealLDA/beforeSTA2001.2338startFrame snapshots/0pendingstarts;
1927scoped render-enables meet exactvblank241..260 orprerender<=274guard.
Original IRQ31/fiveSMC/banks/stack/CHR/publication and all ability assertions
passed unchanged. No broad global deadline/no-DMC/hardware-console claim.

Actual image review:all129selected wholePPUframes on12sheets independently
inspected by agent, with explicit frameplacements and source/DMA epoch binds.
No obvious graphic or ability defect in these pickup/transform/hammer/flight/
refusal/exhaust/recharge/cleanup windows. This is selected-frame inspection,
not all2339frames, sourceart/allpixel,allpose or no-flicker certification.
Review sheets {a.review}
Visual receipt {a.output/'visual-review.json'} SHA256 {sha(a.output/'visual-review.json')}

Audio reporting precision:oldapuWrites10422 is an unchanged4000..4017-range
counter, not10422pureaudio writes. Its CSV contains4353actualaudio-register
stores plus2023DMA4014 and4046controller4016 stores. No waveform, audibility,
SFX priority or original-audio fidelity claim is inferred from that counter.

Complete powerup cell remains OPEN:third cappedflower,ordinaryB-arrow firing/
hit/pool across tiers,star/1up,damage/downgrade/reacquisition,Hard and full
graphics/audio fidelity are not tested here. Current PitEasy narrow component
is supplied additively in ledger-component.json; old84/529 andmode-withdrawal
receipts remain exact and are never retagged current. No native grant remains.
''',encoding='utf-8')
 summary=dict(passed=True,component_only=True,goal_complete=False,ROM_sha256=CURRENT,identity='Pit',actual_numeric_mode=0,native_launches=1,retries=0,native_worker_released=True,native_proof_sha256=sha(native/'proof.json'),ready_sha256=sha(a.ready/'proof.json'),review_sha256=sha(a.review/'proof.json'),ready_bindings_verified=ready_count,review_bindings_verified=review_count,actual_full_PPU_frames=2339,completed_full256_DMA=2293,startFrame_snapshots=2338,scoped_safe_enables=1927,selected_agent_reviewed_frames=129,visual_review_sha256=sha(a.output/'visual-review.json'),ledger_component_sha256=sha(a.output/'ledger-component.json'),report_sha256=sha(report),complete_powerup_cell=False)
 put(a.output/'summary.json',summary)
 checkpoint=ROOT/'docs/qa/checkpoints/2026-10-26/pit-easy731-acquired-abilities';checkpoint.mkdir(parents=True,exist_ok=False)
 for n0 in ['summary.json','visual-review.json','ledger-component.json']:shutil.copy2(a.output/n0,checkpoint/n0)
 (checkpoint/'README.txt').write_text('Narrow current731 PitEasy A physical delivery/B controlled acquired use component. One launch,10plans,two real pickups,two60transforms. No Hard/otherprofiles/allitem/sourceaudio/art/no-flicker claim. Binary captures remain external; source/native/review hashes and explicit sheet placements are in the bound external packet.\n',encoding='utf-8')
 files=[Path(__file__),report,a.output/'summary.json',a.output/'visual-review.json',a.output/'ledger-component.json',a.ready/'proof.json',a.ready/'manifest.json',a.review/'proof.json',a.review/'manifest.json',native/'proof.json']+[p for p in checkpoint.iterdir()if p.is_file()]
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(f),sha256=sha(f),bytes=f.stat().st_size)for f in files]))
 put(checkpoint/'manifest.json',dict(bindings=[dict(path=str(f),sha256=sha(f),bytes=f.stat().st_size)for f in checkpoint.iterdir()if f.is_file()]))
 final=dict(**summary,manifest_sha256=sha(a.output/'manifest.json'),checkpoint_manifest_sha256=sha(checkpoint/'manifest.json'))
 put(a.output/'proof.json',final);print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),report_sha256=sha(report),checkpoint_manifest_sha256=sha(checkpoint/'manifest.json')),indent=2))

if __name__=='__main__':main()
