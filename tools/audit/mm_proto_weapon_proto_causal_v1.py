"""Compare the two retained strict ProtoHard startup failures, without reruns."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
from PIL import Image, ImageDraw

D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
B = D/'mm-proto-weapon-boundary0a-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
put = lambda p, z: Path(p).write_text(json.dumps(z, indent=2)+'\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args();a.output.mkdir(parents=True, exist_ok=False)
    cases, bindings, transfers = [], {}, []
    for folder in ['proto-hard-ready-v1', 'proto-installed3b-baseline-ready-v1']:
        root = B/folder;native = root/'native'
        outcome = json.loads((root/'launch-outcome-v1.json').read_text())
        assert outcome['returncode'] == 1 and not outcome['passed'] and outcome['no_retry']
        rows = [json.loads(z) for z in (native/'ability-dma-epochs.jsonl').read_text().splitlines()]
        complete = [z for z in rows if z['kind'] == 'completed-DMA-before-render-enable']
        for z in complete:
            assert z['source'] == z['hardware'] and len(z['source']) == len(z['writes']) == 256 and not z['differences']
            assert z['page'] == 2 and z['start']['oamaddr'] == z['complete']['oamaddr'] == 0
            assert z['start']['mask'] & 24 == z['complete']['mask'] & 24 == 0
            for i, w in enumerate(z['writes']):
                assert w['value'] == z['source'][i] and w['stamp']['oamaddr'] == i and w['stamp']['mask'] & 24 == 0
        bad = [z for z in rows if z['kind'] == 'actual-PPUMASK-write' and z['scoped'] and z['enabling'] and not z['safe']]
        assert len(bad) == 1 and len(complete) == 351
        disable = [z for z in rows if z['kind'] == 'actual-PPUMASK-write' and not z['enabling']][-1]
        index = list(csv.DictReader((native/'actual-ppu-index.csv').open()))
        assert len(index) == 375 and index[-1]['phase'] == 'menu' and index[-1]['updates'] == '0'
        assert (native/'events.jsonl').stat().st_size == 0
        last = complete[-1]
        cases.append(dict(profile=folder, first_failure=json.loads((native/'first-failure.json').read_text()),
                          first_bad_enable=bad[0], last_disable=disable,
                          last_DMA={k:v for k,v in last.items() if k not in ['source', 'hardware', 'writes']},
                          complete_DMA_pages=len(complete), full_writes_checked=256*len(complete),
                          inclusive_disable_to_DMA_start_cycles=last['start']['cpu']-disable['stamp']['cpu'],
                          DMA_start_to_completion_cycles=last['complete']['cpu']-last['start']['cpu'],
                          completion_to_enable_cycles=bad[0]['stamp']['cpu']-last['complete']['cpu'],
                          observed_component_events=0, last_completed_index=index[-1]))
        transfers.append(complete)
        for x in [*native.iterdir(), root/'readiness.json', root/'bindings.json', root/'command.json', root/'launch-binding-v1.json', root/'launch-outcome-v1.json']:
            if x.is_file():bindings[str(x)] = sha(x)
    assert [z['source'] for z in transfers[0]] == [z['source'] for z in transfers[1]]
    assert [z['hardware'] for z in transfers[0]] == [z['hardware'] for z in transfers[1]]
    left = B/'proto-hard-ready-v1/native';right = B/'proto-installed3b-baseline-ready-v1/native'
    assert (left/'actual-ppu.argb').read_bytes() == (right/'actual-ppu.argb').read_bytes()
    assert (left/'actual-ppu-index.csv').read_bytes() == (right/'actual-ppu-index.csv').read_bytes()
    raw = (left/'actual-ppu.argb').read_bytes()[-256*240*4:]
    image = Image.frombytes('RGBA', (256,240), raw, 'raw', 'BGRA').convert('RGB')
    sheet = Image.new('RGB', (512,264), '#151923');draw = ImageDraw.Draw(sheet)
    for i, label in enumerate(['0a candidate actual completed PPU375','3b baseline actual completed PPU375']):
        draw.text((256*i,4), label, fill='white');sheet.paste(image,(256*i,24))
    sheet.save(a.output/'proto-last-completed-375-pair.png')
    source = D/'root-current-roster-composition-v1/source'
    source_bindings = {str(source/x):sha(source/x) for x in ['src/reset.s','src/samus_freeze_render.s','src/parodius_hud_queue.s','src/parodius_bells.s','src/mmc5.s','src/mmc5_expanded.s']}
    put(a.output/'external-raw-manifest.json', dict(sorted(bindings.items())))
    put(a.output/'proof.json', dict(causal_comparison_completed=True, native_profiles_pass=False,
        candidate_regression_demonstrated=False, existing_installed3b_deadline_failure_demonstrated=True,
        candidate_ROM='0a7dd88e6732bc189e432a9d55b18dd8f7ecf68a22e3b20f0a13ab7276241c09',
        baseline_ROM='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287',
        both_observed_completed_cases=0, cases=cases, all351_source_pages_byte_exact_between_runs=True,
        all351_physical_pages_byte_exact_between_runs=True, all375_completed_PPU_and_index_bytes_exact=True,
        candidate_bad_enable_cpu_delta_vs_baseline=cases[0]['first_bad_enable']['stamp']['cpu']-cases[1]['first_bad_enable']['stamp']['cpu'],
        source_path='reset.s normal NMI PPUMASK-disable -> SamusFreezeUpdateScreen/PnHudPreUpdateScreen/PnPaletteScreenUpdate/native UpdateScreen and pending palette -> scroll/PPUCTRL -> BankSwitchCHR/X5PublishChr -> OAMandReadJoypad/E008 -> actual enabling STA2001 atE00B; AudioUpdate follows DMA/input and cannot be this same-NMI preDMA cost.',
        actual_observed_common_preDMA_span_cycles=1988,
        ownership_limit='No exact VRAM packet, ReloadCHRBank/X5WideChrActive or nested routine entry stamps were recorded by this fixture before entry.1988 is the inclusive observed disable-to-DMA span, not a measured parser/CHR split. Cannot assign exact subroutine/packet cause or first accept-PC timing from these logs.',
        raw_manifest_sha256=sha(a.output/'external-raw-manifest.json'), source_bindings=source_bindings,
        actual_last_completed_sheet_sha256=sha(a.output/'proto-last-completed-375-pair.png'),
        native_worker_released=True, new_native_launches=0, no_retry=True, no_game_patch=True,
        tool_sha256=sha(__file__)))
    print(json.dumps(dict(proof=str(a.output/'proof.json'), sha256=sha(a.output/'proof.json'),
                          common_preDMA=1988, candidate_enable_delta=-4), indent=2))


if __name__ == '__main__':
    main()
