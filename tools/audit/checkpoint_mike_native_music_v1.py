"""Keep small reviewed Mike adoption receipts and an explicit continuation record."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/mike-native-current5ec-v1')
FINAL = '9e0e5ed5d4957aac9baa040ea76616ee4a88233312700b78a8c55250c19f42d3'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def append_raw(path, text, prepend=False):
    old = path.read_bytes()
    nl = b'\r\n' if b'\r\n' in old else b'\n'
    extra = text.replace('\n', nl.decode()).encode('ascii')
    path.write_bytes(extra + old if prepend else old + extra)


def main():
    adopted = json.loads((D / 'adoption-v1/proof.json').read_text())
    assert adopted['adopted'] and adopted['ROM_sha256'] == FINAL
    assert sha(ROOT / 'build/smb-crossover-mmc5-expanded.nes') == FINAL
    out = ROOT / 'docs/qa/checkpoints/2026-10-25/mike-native-9e0e'
    out.mkdir(parents=True, exist_ok=False)
    sources = {
        'adoption.json': 'adoption-v1/proof.json',
        'raw-native-bindings.json': 'adoption-v1/raw-native-bindings.json',
        'qualification.json': 'ready-v1/qualification.json',
        'source-bindings.json': 'ready-v1/source-bindings.json',
        'changed-source-files.json': 'ready-v1/changed-source-files.json',
        'implementation.patch': 'ready-v1/review.patch',
        'pre-adoption-agent-report.txt': 'ready-v1/qa.txt',
        'frozen-inputs.json': 'frozen-inputs.json',
        'ROOT-original-CPU.json': 'root-full-cpu-v1/proof.json',
        'ROOT-dispatch-IRQ-CPU.json': 'root-dispatch-cpu-v1/proof.json',
        'ROOT-native-hard-pilot.json': 'root-native-pilot-hard-v1/native-result.json',
        'ROOT-strict-performance-easy.json': 'root-strict-performance-easy-v1.json',
        'ROOT-strict-performance-hard.json': 'root-strict-performance-hard-v1.json',
        'Mike-full-outer-ABI.json': 'qualification-v1/cpu-Mike-outer/proof.json',
        'full-audio-cost.json': 'qualification-v1/cpu-cost/proof.json',
    }
    for mode in ['easy', 'hard']:
        sources['native-music-' + mode + '.json'] = 'qualification-v1/native-candidate-music-' + mode + '/native-result.json'
    for name, source in sources.items():
        shutil.copy2(D / source, out / name)
    note = '''

2026-10-25 Mike original music accepted on the current combined build
Current MMC5:9e0e5ed5d4957aac9baa040ea76616ee4a88233312700b78a8c55250c19f42d3.
Fresh canonical ROOT compile, Downloads and default ROM/debugger metadata match.
Commit contains four production files: new mike_native_music.s, entrypoint.s,
expanded_audio.s and expanded linker configuration. Only29/7446/3PRG bytes in
banks38/115/126 change versus5ec. Existing Roll119, SMB3Pbar86, Mac123, CV3DMC,
resident127/mirror125 and all CHR remain byte-exact. No new RAM or CHR.
Eleven authentic StarTropics tracks map to14 explicit SMB area/event contexts;
source cadence/channels/stores retained. Native both-mode music matrix passes
7205 source calls/53361 ordered stores/107412 hardware checks per mode, real
CHR/OAM/IRQ and fiveSMC/bank/stack guards, actual NMI maxdepth1.
ROOT independently reran198011 original calls/961696 stores,78338 adapter
calls/590312 stores,9216 other-identity full calls and18 compiled IRQ cases,
then a cold-menu native Hard pilot. Six artificial nested-NMI injections stay
explicit non-reentrant-domain negatives; they are not relabeled as passes.
ROOT independently reaggregated raw600-completed-update performance fixtures
in both actual menu modes: exact gameplay work, equal totalframes886/1021;
primary draws119->120 and lagNMIs1->0, all other measured phase counts match.
Original audio averages3447..3881 CPUcycles/peak6056 versus wrong Pit2263/5144;
this bounded cadence result is not a universal60Hz or whole-level guarantee.
Rollback/source/native raw bindings remain external in
C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/mike-native-current5ec-v1/adoption-v1.
Do not rerun adopt_mike_native_music_once_v1.py. A first preflight glob also
matched native log files; it stopped before any mutation. Directory filtering
was corrected and all checks rerun before the one actual adoption.
Checkpoint:docs/qa/checkpoints/2026-10-25/mike-native-9e0e.
Roll fade and remaining CV3 effects are privately composing onto9e0e, not yet
installed. Parodius native music and crowded body visibility remain open;
the unchanged-art repacking trial found zero reduction across131 body poses.
Earlier8ff38route/37identity clears remain explicitly earlier-hash evidence.
Every-current-character/every-powerup acceptance is still incomplete. No new
characters/menu row, video completion, expandedMMC3 or real-hardware claim.
'''
    report = ROOT / 'docs/qa/mike-native-music-2026-10-25.txt'
    append_raw(report, 'ROOT ADOPTED STATUS (later worker report preserved below)\n' + note + '\n', prepend=True)
    for name in ['docs/qa/CLAUDE-HANDOFF-2026-10-24.txt',
                 'docs/qa/current-work-pr-2026-10-24.md',
                 'docs/qa/ten-agent-work-2026-10-25.txt']:
        append_raw(ROOT / name, note)
    tools = sorted((ROOT / 'tools/audit').glob('mike_native_music_*'))
    tools += [ROOT / 'tools/audit' / name for name in
              ['mike_parodius_music_probe.py', 'mike_parodius_rom_probe.py',
               'adopt_mike_native_music_once_v1.py', 'checkpoint_mike_native_music_v1.py']]
    manifest = dict(ROM_sha256=FINAL, goal_complete=False,
                    files={p.name: sha(p) for p in out.iterdir() if p.is_file()},
                    tools={p.relative_to(ROOT).as_posix(): sha(p) for p in tools},
                    source_files={n: sha(ROOT / n) for n in adopted['changed_source_files']},
                    adopted_report_sha256=sha(report), external_archive=str(D),
                    limitations=adopted['scope'])
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(dict(checkpoint=str(out), manifest_sha256=sha(out / 'manifest.json'))))


if __name__ == '__main__':
    main()
