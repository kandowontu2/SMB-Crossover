"""Pin current P ordinary proofs, private performance evidence and negatives."""
from pathlib import Path
import datetime,hashlib,json,sys,zipfile
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/verification/root-current49-progress-o.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not OUT.exists()
    cp=ROOT/'build/checkpoints/roster-audit-v49-provisional-pit-wings-p'
    assert sha(cp/'manifest.json')=='be6ef9fd6447de62e6cce5ea2574b369b63cf33106210047facf65596726d8b5'
    m=json.loads((cp/'manifest.json').read_text());cat=m['source_hashes']
    assert len(cat)==409 and all(sha(ROOT/n)==h for n,h in cat.items())
    with zipfile.ZipFile(cp/'source-v49-pit-wings-p.zip')as z:assert json.loads(z.read('archived-file-hashes.json'))==cat
    assert sha(cp/'source-v49-pit-wings-p.zip')==m['source_archive_sha256']
    for row in m['compiled']:
        for key in ('rom','debug','labels','map'):
            r=row['target'][key];p=Path(r['path']);assert sha(p)==r['sha256']==sha(ROOT/'build'/p.name)
    refs={
      'previous_N':'build/verification/root-current49-progress-n.json',
      'current_P':'build/checkpoints/roster-audit-v49-provisional-pit-wings-p/manifest.json',
      'user50GB_lossless_policy':'build/verification/root-workspace-storage-policy-50gb-a.json',
      'three_current_P_ordinary_fixed_clears':'build/verification/root49p-three-fixed-a/report.json',
      'U_native9CSV_and_compile':'build/verification/root-reference-runner-u-validation-a/report.json',
      'U_actual_retained_lossless_RGB_PCM_delivery':'build/verification/root-reference-runner-u-recording-b/report.json',
      'Sophia_deep_D':'build/verification/root49o2-sophia-deep-profile-d/report.json',
      'Sophia_ratio_B_build':'build/verification/root49o2-sophia-ratio-private-build-b/report.json',
      'Sophia_ratio_B_CPU_M3':'build/verification/root49o2-sophia-ratio-private-build-b/cpu-mmc3-a.json',
      'Sophia_ratio_B_CPU_M5':'build/verification/root49o2-sophia-ratio-private-build-b/cpu-mmc5-a.json',
      'Sophia_ratio_B_native_profile':'build/verification/root49o2-sophia-ratio-b-profile-e/report.json',
      'Sophia_ratio_B_38_native_and_host_controls':'build/verification/root49o2-sophia-ratio-b-native-f/report.json',
      'Sophia_C_assembly_negative':'build/verification/root49o2-sophia-friction-private-build-c-driver.log',
      'Sophia_C2_host_path_negative':'build/verification/root49o2-sophia-friction-private-build-c2-driver.log',
      'Sophia_C2b_compiled_template_build':'build/verification/root49o2-sophia-friction-private-build-c2b/report.json',
      'Bill_O_actual_contact_owner':'build/verification/root49n-bill-late-contact-o-admission-a/review.json',
      'Bill_P_partial_controller_negative':'build/roster-through-2-2/root49n-bill-red-paratroopa-wait-p-3-v0-mmc3/manifest.json',
      'Bill_Q_partial_controller_negative':'build/roster-through-2-2/root49n-bill-native-wait-q-3-v0-mmc3/manifest.json',
      'Bill_fractional_source_audit':'build/verification/agent49o2-bill-shapes-source-a/freeze.json',
      'Scrooge_V_original_host_negative':'build/verification/root49n-scrooge-castle-observe-v-review-a.json',
      'Scrooge_V_actual_indexed_firebar_review':'build/verification/root49n-scrooge-castle-v-host-review-b/report.json',
      'Ryu_E_private_build':'build/verification/root49o2-head-private-build-e/report.json',
      'Ryu_E_uncached_host_interruption':'build/verification/root49o2-head-e-foot-host-interruption-a.json',
      'Ryu_E_foot143360_M3':'build/verification/root49o2-head-e-foot-mmc3-b.json',
      'Ryu_E_foot143360_M5':'build/verification/root49o2-head-e-foot-mmc5-b.json',
      'Ryu_E_host_cache_M3':'build/verification/root49o2-head-e-foot-mmc3-b-cache.json',
      'Ryu_E_host_cache_M5':'build/verification/root49o2-head-e-foot-mmc5-b-cache.json',
      'Ryu_F_native_results_case61_setup_gap':'build/verification/root49o2-head-f-native-c/report.json',
      'Ryu_F_native_status_representation_negative':'build/verification/root49o2-head-f-e-mmc3-native-check-a.log',
      'Ryu_F_native_status_fullRAM_diagnostic':'build/verification/root49o2-head-f-case1-model-diagnostic-a.json',
      'Ryu_F_case61_host_review':'build/verification/ryu49o2-head-components-f/case61-host-review-a/report.json',
      'Ryu_end_of_head_effect_checker_UNRUN':'build/verification/ryu49o2-head-end-effects-f/freeze.json',
      'QA_as_of_this_snapshot':'docs/qa/roster-provisional-v49.md',
    }
    pins={k:{'path':n,'sha256':sha(ROOT/n),'bytes':(ROOT/n).stat().st_size}for k,n in refs.items()}
    fixed=json.loads((ROOT/refs['three_current_P_ordinary_fixed_clears']).read_text())
    assert all(c['pass']and c['result']['deaths']==0 for c in fixed['cases'])and len(fixed['cases'])==3
    for n in ('Ryu_E_foot143360_M3','Ryu_E_foot143360_M5'):
        f=json.loads((ROOT/refs[n]).read_text())['foot_exhaustive'];assert f['cases']==143360 and f['all256P']and f['all10240_exact_with_individual_extra_write_oracle']
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(ROOT);assert used<50_000_000_000
    report={'status':'progress-full-goal-incomplete','goal_complete':False,'accepted_release':False,
            'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'script_sha256':sha(Path(__file__)),
            'working_checkpoint':cp.name,'shared409_source_exact':True,'root_ROM_DBG_LBL_MAP_exact':True,
            'current_P_MMC3_fixed_ordinary_end2_2':['Mario','Luigi','Samus'],'current_P_MMC5_fixed_ordinary_end2_2':[],
            'workspace_bytes':used,'prospective_cap_bytes':50_000_000_000,'retain_lossless_captures':True,
            'root_active_native_CPU_compile_jobs':[],'references':pins,
            'unfinished':['Full current roster through2-2, every alternate attack/upgrade and final retained recordings.',
                          'Sophia homing stress still115/180 and106/180 missedframes; ratioB not promoted; frictionC2b CPU/interruption/performance unfinished.',
                          'Ryu E case61 setup never launches; physical status representation/native fullRAM proof and independent end-of-head effects remain open.',
                          'Bill Q pending native foot-callee token and exact source geometry/temporal water/terrain/body discrepancies remain open.',
                          'Scrooge actual castle firebar contact is identified; successful ordinary tactic remains unprepared.',
                          'Source48 isolated audio-owner full reset lineage and current49 transplant remain unaccepted.',
                          'No source-perfect/allweapon/hardware/finalrelease claim.']}
    OUT.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'path':str(OUT),'sha256':sha(OUT),'workspace_bytes':used}))

if __name__=='__main__':main()
