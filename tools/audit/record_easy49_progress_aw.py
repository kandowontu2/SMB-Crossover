"""Persist the actual working D repair, completed routes and open full goal."""
from pathlib import Path
import datetime,hashlib,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out=V/'root-current49-progress-aw.json';assert not out.exists()
    checkpoint=R/'build/checkpoints/roster-audit-v49-sophia-head-axis-d/manifest.json'
    assert sha(checkpoint)=='1fcbdec758e0a4c09e769f66b110d4d8d60b05cb11dffa55061bfc32bda55c88'
    c=json.loads(checkpoint.read_text());assert len(c['source_hashes'])==455
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==h
    for b in c['builds']:
        for h in b['artifacts'].values():assert sha(R/h['path'])==sha(R/h['frozen_path'])==h['sha256']
    files=['root49-sophia-head-axis-d/freeze-k.json','root49-sophia-head-adoption-a/preparation.json',
           'root49-current-c-transfers-a/full-route-review-a.json','root49-current-d-transfers-a/samus-review-a.json',
           'root49-samus-ice-order-review-b/review.json','root49-goal-coverage-aw.json',
           'agent-lsr-samus-current-c-route-a/freeze.json','agent-lsr-samus-current-c-route-a/route-review.json',
           'specialist-bill-combined-route-a/handoff-c-aj.json','root49-full-suite-admission-a.json',
           'root49-main-sophia-d-smoke/smb-crossover-mmc3-baseline.log',
           'root49-main-sophia-d-smoke/smb-crossover-mmc5-baseline.log','root-current49-progress-av.json']
    refs={n:dict(sha256=sha(V/n),bytes=(V/n).stat().st_size)for n in files}
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    size=workspace_bytes(R);assert size<70000000000
    result=dict(status='PROGRESS_WORKING_D_INSTALLED_SAMUS_D_MMC3_CLEAR_FULL_GOAL_ACTIVE',
                utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),
                previous_acknowledgement_turn_classification='no progress; neutral user thanks/wrong-chat correction did not cancel the goal',
                revalidation='Actual C source/artifacts, specific native handles and active goal inspected before work resumed.',
                current_goal_turn_classification='progress',
                checkpoint=dict(path=str(checkpoint.relative_to(R)),sha256=sha(checkpoint)),
                shared_main=dict(source_files_rehashed=455,generated_rehashed=11,primary_artifacts_rehashed=8,
                                 changed_sources_from_C=['src/sophia_source_terrain.s'],smokes_passed=2),
                ROMs={b['mapper']:b['artifacts']['nes']['sha256']for b in c['builds']},references=refs,
                concrete_progress=[
                    'CurrentC Mario andLuigi four actual full fixed zero-death clears frozen; all19 movement/controller fields exactly prior proofs.',
                    'Ordinary Sophia second-pipe head/side error bound to actual fractional contact, repaired complete normal-flat mirrored axis and remaining head-span handling.',
                    'PrivateC origin arithmetic/aliased negative-query hole retained and corrected inD, with explicit wholeRAM/stack/write oracle.',
                    'D27,926 arithmetic cases,96original+2split-ceiling,109actualfullcaller exactreexecutions,26foreign and8measuredcrowdscenes pass.',
                    'D independent fixed1-1 clears bothmappers. Full1-2andlater remain open; capturedfailedcontrollers retained.',
                    'ReviewedD installed with474-file actualC backup; source/header/RAM/CHR/audio/baselines unchanged outside exactbank5 whitelist.',
                    'Root rehashes103-file SamusC packet; actualD MMC3 full28809frame zero-death clear, all9wholeCSV literal toC. MMC5 transfer negative2351 retained, firstmovementdifference1253.',
                    'BillC MMC3 verifiedfull31773/zero-death clear; Lancecontroller progressespastcastle andinto2-1.',
                    'Root independently reruns frozenIceAQ predicates/nativecallers/order/layout/cost; noIce mainadoption. Successor actualSTOP/pool/sourceNSF24 implemented privately, palette native tests ongoing.',
                    '14identity/66inventoryentry full-goal index created without converting historical packets or partial routes into completion.'
                ],
                source_fidelity_limits=c['limits'],
                regressions=dict(legacy_native_passed=688,legacy_native_failed=73,separate_stock_Mario_comparison_failed=True,
                                 all73_same_first_failure_on_E=True,full_suite_passed=False,failed_fixtures_unchanged=True,
                                 scope='Original broad suite executesB, notD. D scoped repair validated separately; no automatic universal green claim.'),
                root_live_native_handles=[],
                specialists=dict(
                    link_simon_ryu='SamusC packet immutable. NewSophiaD ordinary-route phase1GB/100MB reserve: passive first1-2 negative owner/head/feet proof; latestreported89822, agent owns terminal audit/next.',
                    mario_luigi_scrooge_s2='BillC AJverified, LanceAQ reached2-1then1502pit. Actual supported jump diagnosis recorded; no active native at lastreport, ARcontroller preparation. Phase1,010,315,882B/1.25GB/100MB reserve.',
                    samus_contra_s2='PrivatepaletteBN fourbuilds/static PASS; actualMMC3 arena latestreported63297 includes fullfreeze/nonfrozenpaletteconflict/debris. Phase527,627,521B/800MB/50MB reserve beforelatest native. No mainchanges.'),
                budget=dict(workspace_bytes=size,global_cap_bytes=70000000000,retains_all_lossless_captures_and_negatives=True,
                            source_of_cap='User explicitly requested retaining lossless captures and raising the original30GB cap.',
                            explicit_phase_extensions=['Bill/Lance1GB→1.25GB,100MB finalreserve','Samus/Bill arsenal500MB→800MB,50MB finalreserve']),
                next_actions=[
                    'Finish source-correct SamusIce palette/lifecycle/SFX successor with strict ownership/ABI/native/cost evidence; independently compose overD preserving head/optimizedfeet.',
                    'Finish actualSophiaD andLance ordinary routes and independentfixedreplays, then explicit final-build transfers.',
                    'Investigate SamusMMC5 actualinjuryowner/phase, adaptordinarycontrols without treatingM3fixedstream assourceoracle.',
                    'Transfer/recover remaining14identity routes; resolve Scrooge1-2 lift timing and remaining all-arsenal/upgrade/lag/fidelity gaps.',
                    'Produce and inspect retainedlossless finalplaythroughs after final runtime integration; reconcile earliershortcut/nonshortcut requests.',
                    'Keep all73 retained legacy failures open until their source/entry evidence is independently resolved.'
                ],
                QA=dict(path='docs/qa/easy-hard-legacy-v49.md',sha256=sha(R/'docs/qa/easy-hard-legacy-v49.md')),
                goal_status='active',accepted_release=False,goal_complete=False)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],sha256=sha(out),workspace_bytes=size,root_live_handles=[])))


if __name__=='__main__':main()
