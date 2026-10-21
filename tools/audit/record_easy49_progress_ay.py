"""Persist working E, exact earlier clears, retained negatives and the unshrunk goal."""
from pathlib import Path
import datetime,hashlib,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def footprint(paths):
    files=set()
    for p in paths:
        if p.is_dir():files.update(q for q in p.rglob('*')if q.is_file())
        elif p.is_file():files.add(p)
    return dict(files=len(files),bytes=sum(q.stat().st_size for q in files))
def main():
    out=V/'root-current49-progress-ay.json';assert not out.exists()
    cp=R/'build/checkpoints/roster-audit-v49-ice-over-sophia-e/manifest.json'
    assert sha(cp)=='65072e56ce25e03e748248cb1efdc51312378e23d099259261bc02d71a76d64b';c=json.loads(cp.read_text())
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==h,n
    for b in c['builds']:
        for q in b['artifacts'].values():assert sha(R/q['path'])==sha(R/q['frozen_path'])==q['sha256']
    assert len(c['source_hashes'])==457 and len(c['generated11'])==11
    refs=['root-current49-progress-ax.json','root49-goal-coverage-ay.json',
      'root49-current-d-transfers-a/t-discovery-freeze-ay.json','root49-current-d-transfers-a/samus-mmc5-review-ay.json',
      'root49-parent-modes-review-ay.json','root49-ice-state-review-ay/review.json',
      'agent49-samus-bill-arsenal-a/ice-state-freeze-dj/freeze.json',
      'root49-ice-integrated-e/preparation.json','root49-ice-integrated-e/build-review.json',
      'root49-ice-integrated-e/root-review-az/review.json','root49-ice-integrated-e/freeze-az.json',
      'root49-ice-integrated-e/install-host-negative-az.json','root49-ice-adoption-e/preparation.json',
      'root49-main-ice-e-smoke/review.json','root49-ice-integrated-e/route-review-ba.json',
      'specialist-bill-lance-current-d-a/phase-freeze-m.json',
      'specialist-bill-lance-current-d-a/phase-census-m.json',
      'specialist-bill-lance-current-d-a/enemy-id-correction-j.json']
    references={n:dict(sha256=sha(V/n),bytes=(V/n).stat().st_size)for n in refs}
    base=list((R/'build/roster-through-2-2').glob('root49-current-d-samus-*'))+list((R/'build/roster-through-2-2').glob('root49-d-samus-m5-*'))
    external=lambda dirs:[V/f"smb-crossover-{'mmc3'if p.name.endswith('mmc3')else'mmc5'}-run-{p.name}.log"for p in dirs]
    own=footprint([V/'root49-current-d-transfers-a']+base+external(base))
    ebase=list((R/'build/roster-through-2-2').glob('root49-e-samus-transfer-a-*'))
    e=footprint([V/'root49-ice-integrated-e']+ebase+external(ebase))
    bpaths=list((R/'build/roster-through-2-2').glob('root49-d-roster-ax-*'))
    batch=footprint([V/'root49-d-remaining-routes-ax']+bpaths+external(bpaths))
    assert own['bytes']<1000000000 and e['bytes']+50000000<500000000 and batch['bytes']<1000000000
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    size=workspace_bytes(R);assert size<70000000000
    result=dict(status='PROGRESS_ICE_E_INSTALLED_D_SAMUS_AND_BILL_MMC5_FULL_CLEARS_E_TRANSFERS_OPEN',
      utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),
      current_goal_turn_classification='progress',wrong_chat_report='Contra backwards-slide report withdrawn; no work assigned for it. Neutral thanks/apology does not cancel the active goal.',
      checkpoint=dict(path=str(cp.relative_to(R)),sha256=sha(cp)),
      shared_main=dict(source_files_rehashed=457,generated_rehashed=11,primary_artifacts_rehashed=8,
        changed_sources_from_D=c['source_changes'],preserved_D_files=c['preserved_D'],smokes_passed=2),
      ROMs={b['mapper']:b['artifacts']['nes']['sha256']for b in c['builds']},references=references,
      completed_evidence=[
        'ActualD/MMC5 Samus completefixed27659/all6/zero-death; ten wholeCSV streams and24 bounded rawsnapshots literal to discoveryT.',
        'ActualD/MMC5 Bill completefixed39517/all6/zero-death; root rehashes843-fileDfreeze/1988-fileCfreeze and independently compares39517 movement+39018 native rows.',
        'Seven exact650-frame original-ROM mode probes: six actualEasy0; Linkpre-options symbol unavailable. Blanketmode mismatch diagnosis contradicted.',
        'Root rehashes229frozenDJreceipts/457sources and reexecutesall8source/native/palette/ABI/cost reports to identical hashes.',
        'PrivateE4builds pass; exact1208-byte owned patch permapper commutes overD, preservesD optimizedfeet andSophiahead.',
        'All6actualE nativegroups pass; four frozen compiled reviewers reexecute exact fullregister/RAM/stack/mapper/orderedwrites and source lifecycle/NSF/palette/NMI protocols.',
        'Einstalled with actualD474-file backup; all457sources/11generated/8primary artifacts rehash; private and actualmain bothmapper startup/control/floor checks pass.'
      ],
      explicit_negatives=dict(E_Samus_MMC3=dict(death=8174,stage='1-2',first_movement_difference=1203,skipped_NMIs=[28,32]),
        E_Samus_MMC5=dict(death=3920,stage='1-1',first_movement_difference=2236,skipped_NMIs=[35,39]),
        diagnosis='Actual completed-update/input-producer timing remains unbound; fixed-tape failures alone do not prove a physics/contact bug.',
        installer_host_negative='Exit text is printed to host stdout after native log write. Initial mistaken in-log assertion retained before mutation; real exits were0 and loghash/exit receipts bind admission.'),
      performance=c['cost'],source_fidelity_limits=c['limits'],
      root_live_native_handles=[],root_native_batch_status='E native6 terminal0; rootcompiled4 terminal0; mainsmokes2 terminal0; E routebatch22558 closed0 withtwo retained native deaths.',
      specialists=dict(
        link_simon_ryu='ImmutableD Sophia: ACclears2-1/2-2entry19032; ADdefeatsfirstBlooper. AE/AF/AG finitetarget/aim negatives retained, currentpreparation keeps90 travelband after blockedfireline diagnosis. Root approves1.25GBphase/100MBreserve/global70GB.',
        mario_luigi_scrooge_s2='Dthreeproofs frozenphaseM; LanceD/MMC5 Nfails1-1at2317/first1431, noinjurybeforefall. Oordinarysupportedprefixfeedback live3167. Phase~400MB/1GB/100MBreserve.',
        samus_contra_s2='DJfrozen/installedE; now explicitD MM/Bass ordinary-route phase. First1398actualmovemententries matcholdMM, sampledinputdifference1399 retained. ActualGameCore inputcopy clock investigation; currentKrealownedlift route live7944. Phase169MB/1GB/100MBreserve.'),
      budget=dict(workspace_bytes=size,global_cap_bytes=70000000000,root_D_phase=own,root_E_phase=e,root_D_batch_phase=batch,
        root_D_cap=1000000000,root_D_reserve=100000000,root_E_cap=500000000,root_E_reserve=50000000,
        Sophia_extension=dict(previous=1000000000,current=1250000000,reserve=100000000,
          reason='Actual806576014B + conservative60MB discovery +60MBfinal replay +100MBreserve exceeds1GB; explicitly authorized extension recorded before AF launch.'),
        retains_all_lossless_captures_and_negatives=True,source_of_cap='Explicit user: retain lossless captures; raise cap. Original30GB superseded.'),
      regressions=dict(legacy_native_passed=688,legacy_native_failed=73,separate_stock_Mario_comparison_failed=True,full_suite_passed=False,
        scope='Original predecessor-B broadsuite remains scopedB, no automaticD/E whole-suite pass and no waiver of retained failures.'),
      next_actions=[
        'Recover actualE Samus routes using bound completed-update/input-producer controls; no retaggingD proofs.',
        'Finish ordinaryD Sophia water and independentfixed fullclear; preserve every failed control and exact source collision qualifications.',
        'Finish LanceD/MMC5; MM/BassD realupdate-clock recovery, then remaining identities including Scrooge1-2 lifts and Linkpre-options distinction.',
        'Measure and optimize remaining lag, including activefreeze/OAM costs, and finish every attack/weapon/upgrade on actual final integration.',
        'Complete all14 identities/66inventoryentry obligations plus originalshortcut/nonshortcut scope; record/inspect retained lossless finalmovies only after final integration.'
      ],
      QA=dict(path='docs/qa/easy-hard-legacy-v49.md',sha256=sha(R/'docs/qa/easy-hard-legacy-v49.md')),
      all_roster_complete=False,all_arsenal_complete=False,final_recordings_complete=False,goal_status='active',accepted_release=False,goal_complete=False)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],sha256=sha(out),workspace_bytes=size,root_D_phase=own,root_E_phase=e,root_D_batch=batch)))
if __name__=='__main__':main()
