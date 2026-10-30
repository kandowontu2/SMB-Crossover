"""Compare every native Parodius frame and exact timing on the resource base."""
from pathlib import Path
import json
import sys

R = Path(__file__).resolve().parents[2]
O = R/'build/character-host-union-resources-v1'
sys.path.insert(0, str(R/'tools/audit'))
from checkpoint_roster_progress_1030_v2 import save, sha
from verify_parodius_chr_compact_native_v1 import frames


def main():
    prepared = json.loads((O/'native-prepared.json').read_text())
    inputs = dict(prepared['source_bindings'])
    for path, digest in inputs.items():
        assert sha(path) == digest, path
    rows = []
    for variant, name in [(1, 'Octopus'), (2, 'TwinBee'), (3, 'Pentarou')]:
        paths = [O/'native'/('parent-v'+str(variant)), O/'native'/('dense-v'+str(variant))]
        results = []
        for path, expected in zip(paths, [prepared['parent_ROM_sha256'], prepared['candidate_ROM_sha256']]):
            result = json.loads((path/'result.json').read_text())
            binding = json.loads((path/'binding.json').read_text())
            budget = json.loads((path/'capture-budget.json').read_text())
            assert result['passed'] and result['ROM_sha256'] == binding['ROM_sha256'] == expected
            assert binding['exit_code'] == budget['returncode'] == 0 and not budget['violations']
            assert '--nes.removeSpriteLimit=false' in budget['command'] and '--doNotSaveSettings' in budget['command']
            assert binding['driver_sha256'] == sha(O/'native-adapter.py')
            assert binding['template_sha256'] == sha(R/'build/character-host-union-v13/native_cold.lua')
            assert binding['controller_sha256'] == sha(path/'controller.lua')
            results.append({key: value for key, value in result.items() if key != 'ROM_sha256'})
            for current in path.iterdir():
                if current.is_file():
                    inputs[str(current)] = sha(current)
        assert results[0] == results[1], (name, 'All native metrics except ROMhash must match')
        for filename in ['trace.csv', 'main-cycles.csv', 'screens.bin']:
            assert (paths[0]/filename).read_bytes() == (paths[1]/filename).read_bytes(), (name, filename)
        sequence = frames((paths[1]/'screens.bin').read_bytes())
        assert len(sequence) == results[1]['captured_screens']
        rows.append(dict(character=name, physical_frames=results[1]['frames'],
                         exact_screen_pairs=len(sequence), identical_trace_and_Main_timing=True,
                         timing=results[1]['timing'], screens_SHA256=sha(paths[1]/'screens.bin'),
                         full_screen_frames=sequence))
    for path in [Path(__file__).resolve(), O/'native-prepared.json',
                 R/'tools/audit/prepare_union13_resources_native_v1.py',
                 R/'tools/audit/verify_parodius_chr_compact_native_v1.py']:
        inputs[str(path)] = sha(path)
    total = sum(row['exact_screen_pairs'] for row in rows)
    save('union-v13-resources-native', dict(
        status='ALL_NATIVE_PARODIUS_FRAME_AND_TIMING_PAIRS_EXACT',
        ROM_sha256=prepared['candidate_ROM_sha256'], parent_ROM_sha256=prepared['parent_ROM_sha256'],
        serial_native_runs=6, exact_native_screen_pairs=total, rows=rows,
        ordinary_sprite_limit=True, controller_only=True, lossless_streams_retained=True,
        root_visual_review_pending=True,
        limits=['Cold menu/lives/up/down/shoot comparisons; no full1-1/new-upgrade qualification.',
                'The V13 Bill extra missed frame remains; resource compaction does not fix it.',
                'No shared download or admission flags changed.']), inputs)


if __name__ == '__main__':
    main()
