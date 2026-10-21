"""Bind the raised storage cap to real segmented capture and host guard checks."""
from pathlib import Path
import csv, difflib, hashlib, json, shutil

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-capture-raised-cap-ax'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    output = H / 'report-ba.json'
    assert not output.exists()
    before = json.loads((H / 'before.json').read_text())['files']
    before.append(json.loads((H / 'before-native.json').read_text()))
    changes = []
    for item in before:
        current = R / item['path']
        old = H / ('before-' + current.name)
        assert sha(old) == item['sha256']
        changes.append(dict(path=item['path'], before_sha256=sha(old), after_sha256=sha(current),
                            diff=''.join(difflib.unified_diff(old.read_text().splitlines(True), current.read_text().splitlines(True),
                                                          fromfile='before/' + current.name, tofile='after/' + current.name))))
    native = R / 'build/roster-through-2-2/root49ay-capture-cap50-0-v0-mmc3'
    negative = R / 'build/roster-through-2-2/root49ax-capture-cap50-0-v0-mmc3'
    manifest = json.loads((native / 'manifest.json').read_text())
    assert manifest['config']['workspaceCapBytes'] == 50_000_000_000 and manifest['config']['segmented']
    assert manifest['result']['failure'] == 'frame limit' and manifest['result']['frames'] == 650
    assert not manifest['verified_through_2_2'] and manifest['assemble_exit'] == 0 and manifest['native_parts_retained']
    assert sha(native / 'capture_segments.c') == sha(R / 'tools/playthroughs/capture_segments.c')
    proof = native / 'playthrough-lossless.verification/report.json'
    assert sha(proof) == 'eddcb74414ce43ff3088d7bf64bb13125166a20654b8716722cbf2b440deb4a7'
    media = json.loads(proof.read_text())
    assert media['result'] == 'passed-exact-rgb-and-pcm' and media['total_frames'] == 649
    assert media['video_rgb_identity'] and media['continuous_pcm_identity'] and media['timestamps_passed']
    unrecorded = R / 'build/roster-through-2-2/root49aw-mario-fixed-0-v0-mmc3'
    trace = list(csv.DictReader((native / 'trace.csv').open()))
    baseline = list(csv.DictReader((unrecorded / 'trace.csv').open()))
    assert len(trace) == 650 and trace == baseline[:650]
    host = H / 'native-controls-az/report.json'
    assert sha(host) == 'a6ff3815a9ceccfbea656bd756a915a776798a90dd2b5a1ccb0645c5ea1a94e3'
    controls = json.loads(host.read_text())
    assert controls['result'] == 'passed-host-budget-controls' and controls['case_count'] == 52
    assert controls['production_c_sha256'] == sha(R / 'tools/playthroughs/capture_segments.c')
    assert sha(H / 'native-controls-az/capture_segments.proposed.c') == controls['production_c_sha256']
    native_log = V / 'smb-crossover-mmc3-run-root49ay-capture-cap50-0-v0-mmc3.log'
    shutil.copyfile(native_log, H / 'ay-native.log')
    pub_path = R / 'build/checkpoints/roster-audit-v49-bill-laser-u/manifest.json'
    pub = json.loads(pub_path.read_text())
    assert all(sha(R / path) == digest for path, digest in pub['source_hashes'].items())
    report = dict(status='PASS_USER_RAISED_CAPTURE_CAP_HOST_AND_NATIVE', script_sha256=sha(__file__),
                  changes=changes, cap_bytes=50_000_000_000,
                  host_controls=dict(cases=52, report_sha256=sha(host),
                                     coverage='Actual Win32 retained-file/reserve/sharing/junction/error controls, valid30GB/50GB/uint64 cap and overflow rejection. Host stubs, not recorder proof.'),
                  native_calibration=dict(mapper='mmc3', image='AP', frames=650, video_frames=649,
                                          manifest_sha256=sha(native / 'manifest.json'),
                                          native_log_sha256=sha(H / 'ay-native.log'), lossless_proof_sha256=sha(proof),
                                          all_650_trace_rows_exact_unrecorded_AP=True, exact_RGB_and_PCM=True,
                                          parts_retained=True, WAV_retained=True, lossless_master_retained=True),
                  negative=dict(path=negative.relative_to(R).as_posix(),
                                reason='First AX run removed only Python30GB ceilings. Native C still rejected50GB configuration before gameplay; the early audit then read uninitialized preference. Original marker/logs/artifacts retained. All three production ceilings are now corrected.',
                                manifest_sha256=sha(negative / 'manifest.json')),
                  published_U_source_exact=True, game_ROM_changed=False, emulated_memory_or_register_changes=False,
                  limitations=['650-frame recording calibration, not full route completion or final media.',
                               'No available UNC native recording test share; existing path checks remain.',
                               'Positive cap parsing, byte/reserve guards and per-segment checks remain. Only obsolete30GB upper ceilings were removed.'],
                  files_deleted=False, accepted_release=False, goal_complete=False)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(output.name, sha(output), flush=True)


if __name__ == '__main__':
    main()
