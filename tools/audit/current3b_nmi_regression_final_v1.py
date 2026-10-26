"""Freeze two consumed grants and their separate actual/visual outcomes; no new run."""
from pathlib import Path
import argparse, hashlib, json
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def get(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,z):assert not p.exists(),p;p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 ready=a.ready/'readiness.json';assert sha(ready)=='d093f142f4301dab015bc2d4f4483a2f66561d774c97d74555d3be10d4b24b33';r=get(ready);bindings=get(a.ready/'bindings.json');assert len(bindings)==1156 and all(sha(f)==h for f,h in bindings.items())
 grants={'ROOT-menu-grant.json':'c2c6f94bceed891097278a30614aab6b813f9b52c2ea4bbb97eea28f8f8b877d','ROOT-hard1f-grant.json':'54a5dfa9d681c6a5e76e8663d5a2a9d8e3804580f090dc0ce9f31c562d44dd47'}
 for f,h in grants.items():assert sha(a.ready/f)==h;bindings[str(a.ready/f)]=h
 menu=Path(r['profiles'][0]['output']);hard=Path(r['profiles'][1]['output']);mr=get(menu/'regression-result.json');hr=get(hard/'regression-result.json');game=get(hard/'proof.json');case=game['cases'][0];comparison=get(hard/'regression-comparison/proof.json')
 assert mr['passed']and mr['all_original_six_and_additive_timing']and hr['passed']and comparison['passed'];assert game['passed']and game['updates']==240 and game['draws']==168 and case['modeReadback']==1
 pixel=D/'current3b-nmi-menu-result-v1/proof.json';assert sha(pixel)=='62e6d0cb10402917b64a21e22061a4aa91d2f7294d797ac21d75354371fcb1e4';assert get(pixel)['passed']is False and get(pixel)['different_frames']==[375]
 attribution=D/'current3b-menu375-readonly-v1/proof.json';assert sha(attribution)=='4afd412ce144050d4594489d76c33e7aebe65918a56bc5189399536b2e950bc4';assert get(attribution)['forced_blank375_proven_by_actual_start_mask_and_ungated_enable_log']
 for receipt in [pixel,attribution]:
  z=get(receipt);catalog=receipt.parent/'bindings.json';assert sha(catalog)==z['bindings_sha256'];entries=get(catalog)
  for f,h in entries.items():assert sha(f)==h;bindings[f]=h
  bindings[str(catalog)]=sha(catalog);bindings[str(receipt)]=sha(receipt)
 for folder in [hard,a.ready]:
  for f in folder.rglob('*'):
   if f.is_file():bindings[str(f.resolve())]=sha(f)
 report=ROOT/'docs/qa/current3b-nmi-regression-native-2026-10-26.txt';assert not report.exists()
 report.write_bytes(('Combined3b NMI regressions:two consumed one-shot grants, no source/install change\n\n'
 f'ROM:{r["ROM_sha256"]}\nReady:{ready} SHAd093f142f4301dab015bc2d4f4483a2f66561d774c97d74555d3be10d4b24b33\n\n'
 'MENU1800:original six guard components plus ungated timing PASS. ActualEasy0, allfourship controller/cancel/reentry, terminalvariant1.1122updates/1000semanticDMAs/1300completedfull256DMAs/945scoped-safeenables/0late/0hardwaremismatch/minSP197 match731 totals. No retry; worker released.\n\n'
 'EXACT MENU RGB IDENTITY GATE:FALSE retained.1650/1651 complete raw frames match731;375 differs39RGBpixels, first255,39 black→RGB146/144/255. Actual start375 has identical complete PPUstate/palette/CHR/hardware, mask6/BGoff/spritesoff. Every disabled→enabled mask transition is logged, none375; nextenable376 scan257dot258before/228after. One actual wholeframe pair was viewed and supplied toROOT. It shows a blank purple→black initialization stripe, not active menu/gameplay. Exact early DisableScreenFlag/CrossoverMenuState/NmiDisable numeric snapshots and individual pre440PPUMASK/PPUDATA store stamps are absent; source palette phase is supported, precise first-store cause is unproved. No automatic harmless/visualPASS conclusion.\n\n'
 'HARD1F240:actualHard1, original staged pressure controller/actors/caps and full source/owner/hardware/timing/cadence guards PASS.240updates/168totaldraws match731.280cadence rows/167CSVdraws, longest no-draw/no-update2, zero cumulative draw-prefix deferrals; complete Gameproof totals remain separate.280authenticated original effect ticks/280fullmixerflushes/850identical unmasked APUwrites. Seven real queued source1Frequests;195source-image writes.168strict completedDMA,166original complete-DMA checks,3360hardwareCHRchecks,280NMIs,560IRQscrollwrites,minSP203.\n\n'
 'DMCscope:existing DMC guards remain, but this1F noise-pressure profile actually launches zero DMC samples (dmcStarts0/sourcePayloadChecks0). It is not new active-DMC fetch or waveform qualification. Original1F adapter image order remains declared unchanged; raw400F/hardware values are not masked.\n\n'
 'Both settings hashes unchanged; exactlytwo separately approved launches, one sequential worker, zero retries; all grants now consumed/released. No production/default/settings/Git/Downloads mutation, native reattempt or new screenshot/checkpoint bundle. Original native negatives and the exactRGB_FALSE remain immutable. ROOT adoption/visual review remains separate.\n\n'
 f'Final frozen manifest:{a.output/"proof.json"}\n').encode())
 for f in [Path(__file__).resolve(),ready,report,menu/'regression-result.json',hard/'regression-result.json',hard/'regression-comparison/proof.json']:bindings[str(f)]=sha(f)
 put(a.output/'bindings.json',bindings)
 put(a.output/'proof.json',dict(passed=False,native_run=True,source_changed=False,adopted=False,ROM_sha256=r['ROM_sha256'],launches=2,retries=0,worker_released=True,native_menu_original_six_and_timing_pass=True,native_Hard1F_original_guards_source_hardware_cadence_pass=True,mechanical_regression_passed=True,exact_all_frame_RGB_identity_gate_passed=False,menu_original_RGB_FALSE_preserved=str(pixel),blank_transition_attribution=str(attribution),hard_updates=240,hard_draws=168,hard_source_ticks=280,hard_identical_unmasked_APU_stores=850,hard_actual_DMC_starts=case['dmcStarts'],hard_original_payload_checks=case['sourcePayloadChecks'],menu_completed256_DMAs=1300,menu_scoped_safe_enables=945,bindings=len(bindings),bindings_sha256=sha(a.output/'bindings.json'),report=str(report),report_sha256=sha(report),scope='Final exact3b finite component evidence. Mechanical/source/hardware controls pass; all-frame byte-identity diagnosis remains FALSE on forced-blank transition375. No source change, new run or automatic visual/adoption verdict.'))
 print(json.dumps(dict(proof=str(a.output/'proof.json'),sha256=sha(a.output/'proof.json'),bindings=len(bindings),report_sha256=sha(report)),indent=2))
if __name__=='__main__':main()
