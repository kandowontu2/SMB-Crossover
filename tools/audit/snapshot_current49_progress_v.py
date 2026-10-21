"""Freeze current user baseline and executed legacy-mode progress honestly."""
from pathlib import Path
import datetime,hashlib,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=V/'root-current49-progress-v.json';assert not out.exists()
    baseline=V/'root49-easy-hard-user-baseline-a/baseline.json';b=json.loads(baseline.read_text())
    assert sha(baseline)=='1b7fef1ea3279fc21dcb8ffca4db551b4285cfb7ad9566711db978dffa2861f1'
    assert all(sha(R/n)==h for n,h in b['current_source_hashes'].items())
    roms={m:sha(R/('build/smb-crossover-'+m+'.nes'))for m in ['mmc3','mmc5']}
    assert roms=={'mmc3':'ef8743c306818d301d101eaa6bfb39dac8d7ec12d017c3817042310d7d2a3c00','mmc5':'4a2ee25aa2ec4d88ea7e7cf0ca4285629ac70b0ead1cbffca7cfe5a176c4e9c4'}
    refs=['root-current49-progress-u.json','root49-easy-hard-user-baseline-a/baseline.json',
      'root49-easy-inventory-base-a/build-review-b.json','root49-easy-inventory-base-a/query-cpu-b.json',
      'root49-easy-injury-private-a/build-review-c.json','root49-easy-injury-private-a/spend-cpu-c.json',
      'root49-easy-injury-private-a/hard-regressions-b/report.json',
      'root49-easy-contact-private-d/build-review-f.json','root49-easy-union-a/report.json',
      'agent49-megaman-easy-hard-implementation-a/freeze.json',
      'agent49easy-bill-fan-a/freeze.json','agent49easy-samus-bill-runtime-a/tier-freeze.json',
      'agent-lsr-easy-hard-implementation-a/numeric-primary-freeze-h.json',
      'specialist-mario-easy-hard-source-a/source-freeze.json',
      'specialist-scrooge-s2/handoff-m5-final.json','agent49s2-pit-record-an/freeze.json',
      'agent-lsr-t-blooper-geometry-a/freeze.json','root49-bill-native-h/positive-m3-a-review.json']
    for tag in ['full-m3-c','full-m5-d','pickup-m3-e','pickup-m5-f']:
        n='root49-easy-injury-private-a/native/'+tag+'/host-report.json';d=json.loads((V/n).read_text());assert d['exit']==0;refs.append(n)
    for tag in ['eligibility-m3-g','eligibility-m5-h']:
        n='root49-easy-contact-private-d/native/'+tag+'/host-report.json';d=json.loads((V/n).read_text());assert d['exit']==0 and d['result']['cases']==144;refs.append(n)
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(R);assert used<50_000_000_000
    report=dict(status='ACTIVE_PROGRESS_USER_LABELS_PRESERVED_EASY_RUNTIME_PRIVATE_INCOMPLETE',
      utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),
      main_source412_exact_user_baseline=True,working_ROM_sha256=roms,main_runtime_changed_this_phase=False,
      references=[dict(path=str((V/n).relative_to(R)),sha256=sha(V/n),bytes=(V/n).stat().st_size)for n in refs],
      private_executed=['109056 compiled inventory ownership/support executions on bothmaps.',
       '107520 compiled ammo commit cases per mapper, allphysicalRAM and unaffectedABI.',
       '48 native contact/injury arenas per mapper, source60-update freeze and150-update protection, Hard one-hit Bill preserved.',
       '36 native Easy Mushroom/Flower contact cases per mapper, one-tier progression and cap/no inventory changes.',
       '16 existing Hard injury regression groups pass bothmaps.',
       '144 real native source/native water eligibility contacts per mapper.',
       'MM final4file layer:11632CPU +124movement scenarios and144nativeBuster componentcases.',
       'Bill fanorder1320nativecases per mapper, distinguishing originalcontrols.',
       'Samus/Billtier6384components, MMC5coverage split into two1320case Billruns after separate continuous-death negatives.',
       'LSRnumeric/primary780movement+84weaponcomponents frozen.'],
      current_integration='root49-easy-union-a three shared-file merges clean; actuallinkfails GUEST13B/SPECIAL_ROSTER16B. No working publication.',
      live_root_native_or_CPU_handles=[],
      active_specialists=['Mario original/202 movement and injury privateimplementation.',
       'Link pre-bodypriority/300ms thrust/wholeclip boomerang and coldclosure relocations.',
       'Samus400ms EasySTOP frozen next; demonstrated Hard150ms aggregate invulnerability tofix.'],
      completed_S2_recorded_routes=['MarioM3/M5','LuigiM3/M5','ScroogeM3/M5','PitM3'],
      record_qualification='Each tied to immutableS2, not Easyupdate. Pit andScroogeM5 final media reviews nowfrozen; no human listening/sourcewaveform perfection claim.',
      workspace_bytes=used,cap_bytes=50_000_000_000,retain_lossless_captures=True,
      remaining=['Finish allsource-backed Easy differences including Mario and characteranimation/effect gaps.',
       'Integrate private layers, meaningful full regressions/nativeordinaryplayback, publish exacttestedROMs.',
       'Actualblockemergence/dropeligibility traces and allweapon/upgradevalidation.',
       'Ryu waterbody/cache repair and Bill bodyproposal lifecycle/layout.',
       'Fullroster ordinarypower-on end2-2 clears/alternates, lagoptimization and finalsamecheckpointrecordings.'],
      accepted_release=False,goal_complete=False)
    out.write_text(json.dumps(report,indent=2)+'\n');print(out.name,sha(out),used,flush=True)
if __name__=='__main__':main()
