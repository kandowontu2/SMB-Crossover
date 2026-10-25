"""Install the independently reviewed20-file CV3 proposal once, retaining rollback."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/cv3-dmc-complete-v1')
BASE='8ff245ae662059abbc77c5de517260032775b7ba881a5201b8b54686ccf08277'
FINAL='4c70fe485f73fb8d437fae2e79ae8ddad83908dc26d4008f21e0a2abeccee2da'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out=D/'adoption-optimized-v2'
    assert not out.exists(),'One-shot adoption already started; inspect retained state.'
    default=ROOT/'build/smb-crossover-mmc5-expanded.nes'
    installed=Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes')
    assert sha(default)==sha(installed)==BASE
    receipt=ROOT/'tools/audit/cv3_dmc_complete_qualified_v2.json'
    assert sha(receipt)=='ee66bfe6fb906069d8fabcd5987d222add8727a1577175a5827406f676022683'
    packet=json.loads(receipt.read_text(encoding='utf-8'))
    assert packet['ROM_sha256']==FINAL and len(packet['source_files'])==20
    assert packet['behavior_checks_passed']and packet['per_case_performance_nonregression_pass']
    for n,v in packet['receipts'].items():assert sha(D/n)==v,n
    for n,v in packet['tools'].items():assert sha(ROOT/'tools/audit'/n)==v,n
    assert sha(ROOT/'docs/qa/cv3-dmc-complete-native-v2-2026-10-25.txt')==packet['report_sha256']
    evidence=D/'native-qualification-optimized-current8ff-v2-r2/evidence-manifest.json'
    for name,files in json.loads(evidence.read_text()).items():
        for n,v in files.items():assert sha(D/'native-optimized-current8ff-v2'/name/n)==v,(name,n)
    root_receipts=[D/'root-optimized-v1'/n/'proof.json'for n in['cpu','save-cpu','irq','layout']]
    root_receipts += [D/'root-optimized-cadence-v2/proof.json',D/'root-optimized-roster-audio-v2/proof.json']
    for p in root_receipts:
        q=json.loads(p.read_text());assert q['passed'],p
        assert q.get('ROM_sha256',q.get('candidate_sha256'))==FINAL,p
    native=json.loads(root_receipts[-2].read_text())
    assert native['native_guards_passed']and len(native['comparisons'])==6
    assert native['qualifier_sha256']==sha(ROOT/'tools/audit/qualify_cv3_dmc_optimized_cadence_v2.py')
    for n,v in(native['tools']|native['receipts']).items():assert sha(Path(n))==v,n
    roster=json.loads(root_receipts[-1].read_text());assert roster['identities']==37 and roster['full_AudioUpdate_calls']==9472
    assert roster['tool_sha256']==sha(ROOT/'tools/audit/check_cv3_audio_roster_v2.py')
    for stem,digest in [('expanded',FINAL),('mmc3','d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),('mmc5','f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
        assert sha(D/'root-optimized-v1/fresh-build'/(stem+'.nes'))==digest
    source=D/'final-optimized-current8ff-v2/source-final'
    for row in packet['source_files']:
        path=(ROOT/row['path']).resolve();assert path.is_relative_to(ROOT)
        assert(sha(path)if path.exists()else None)==row['baseline_sha256'],row['path']
        assert sha(source/row['path'])==row['sha256'],row['path']
    out.mkdir();shutil.copy2(installed,out/'previous-MMC5.nes')
    suffixes=['.nes','.dbg','.lbl','.map','.build.json','.build.log','.cv3-mirror.json']
    previous=out/'previous-source'
    for row in packet['source_files']:
        p=ROOT/row['path']
        if p.exists():
            saved=previous/row['path'];saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,saved)
    for ext in suffixes:
        p=default.with_suffix(ext)
        if p.exists():
            saved=out/'previous-default'/p.name;saved.parent.mkdir(exist_ok=True);shutil.copy2(p,saved)
    try:
        for row in packet['source_files']:
            p=ROOT/row['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((source/row['path']).read_bytes())
        with(out/'fresh-ROOT-build.log').open('w',encoding='utf-8')as log:
            subprocess.run([sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),
                '--output',str(out/'candidate.nes')],cwd=ROOT,check=True,stdout=log,stderr=subprocess.STDOUT)
        assert sha(out/'candidate.nes')==FINAL,'Canonical ROOT compile differs from exact qualified candidate'
    except BaseException:
        for row in packet['source_files']:
            p=ROOT/row['path']
            if row['baseline_sha256']is None:p.unlink(missing_ok=True)
            else:shutil.copy2(previous/row['path'],p)
        raise
    staging=installed.with_name(installed.stem+'.staging-'+FINAL[:8]+'.nes');assert not staging.exists()
    shutil.copy2(out/'candidate.nes',staging);assert sha(staging)==FINAL;staging.replace(installed)
    for ext in suffixes:shutil.copy2((out/'candidate.nes').with_suffix(ext),default.with_suffix(ext))
    assert sha(default)==sha(installed)==FINAL
    result=dict(adopted=True,goal_complete=False,ROM_sha256=FINAL,baseline_ROM_sha256=BASE,
        fresh_canonical_ROOT_compile_exact=True,installed=str(installed),Downloads_and_default_build_current=True,
        source_files=packet['source_files'],source_file_count=20,agent_packet_sha256=sha(receipt),
        root_receipts={str(p):sha(p)for p in root_receipts},ordinary_roster_AudioUpdate_cases=9472,
        native_candidate_cases=32,native_baseline_cases=24,root_independent_candidate_cases=6,
        copy_loop_cycles_saved=314,CV1_CV3_idle_AudioUpdate_delta=-301,
        held_source_active_AudioUpdate_delta=-273,
        temporary_prefix_phase_difference_explicitly_reviewed=packet['temporary_prefix_deficit_cases'],
        phase_decision='Accepted bounded scheduling improvement: lone one-frame draw prefix deficit recovers next frame; '
            'Hard pressure finishes2frames sooner, no fewer draws/updates, fewer idle frames and no longer maximum stall. '
            'Old e6b lost-draw result remains rejected. No claim of exact per-frame phase or universal lag removal.',
        non_CV3_ordinary_audio_costs=roster['rows'],
        raw_existing_Git_EOL_preserved=True,new_RAM_bytes=0,new_CHR_bytes=0,
        Mac_bank123_gate18_and_original127_samples_exact=True,backup=str(out),
        scope='Authentic CV3 primary72/Sypha75 and natural held-DAC completion with exact source-owned priority/lifecycle; '
              'original24-cell Save image copied in the same order with preserved CPU state. '
              'All37 ordinary CPU audio/state outcomes exact; rare ordinary DMC controls add up to72CPU cycles, '
              'CV1/CV3 paths save at least229 in that ordinary matrix. '
              'No full37-identity native4c70 campaign/every-item/waveform/hardware or MMC3 parity certification.')
    (out/'proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    verification=ROOT/'build/verification/cv3-dmc-optimized';verification.mkdir(exist_ok=True)
    shutil.copy2(out/'proof.json',verification/'proof.json')
    print(json.dumps({k:result[k]for k in['adopted','goal_complete','ROM_sha256','source_file_count','installed','fresh_canonical_ROOT_compile_exact']},indent=2))


if __name__=='__main__':main()
