"""Freeze the first cold-cache native negative without another emulator run."""
from pathlib import Path
import argparse
import collections
import csv
import hashlib
import json
from PIL import Image, ImageDraw

D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
C = D/'robot-cold-palette-candidate-v2'
B = C/'ready-v2'
OLD = D/'proto-startup-budget-ready-v2/native'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
put = lambda p, z: Path(p).write_text(json.dumps(z, indent=2)+'\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args();a.output.mkdir(parents=True, exist_ok=False)
    for name, h in json.loads((B/'bindings.json').read_text()).items():
        assert sha(name) == h, name
    n = B/'native'
    launch = json.loads((B/'launch-outcome-v1.json').read_text())
    assert launch['returncode'] == 1 and not launch['passed'] and launch['no_retry']
    assert launch['native_worker_released']
    epochs = [json.loads(x) for x in (n/'ability-dma-epochs.jsonl').read_text().splitlines()]
    diag = [json.loads(x) for x in (n/'bass-diagnostic.jsonl').read_text().splitlines()]
    events = [json.loads(x) for x in (n/'events.jsonl').read_text().splitlines()]
    completed = [x for x in epochs if x['kind'] == 'completed-DMA-before-render-enable']
    for q in completed:
        assert q['source'] == q['hardware'] and len(q['source']) == len(q['writes']) == 256
        assert not q['differences'] and q['page'] == 2
        assert q['start']['oamaddr'] == q['complete']['oamaddr'] == 0
        assert q['start']['mask'] & 24 == q['complete']['mask'] & 24 == 0
        for i, w in enumerate(q['writes']):
            assert w['value'] == q['source'][i] and w['stamp']['oamaddr'] == i
            assert w['stamp']['mask'] & 24 == 0
    assert len(completed) == 353
    enables = [x for x in epochs if x['kind'] == 'actual-PPUMASK-write' and x['scoped'] and x['enabling']]
    bad = [x for x in enables if not x['safe']]
    assert len(bad) == 1 and bad[0]['stamp']['frame'] == 378
    assert (bad[0]['stamp']['scanline'], bad[0]['stamp']['cycle']) == (1, 38)
    assert bad[0]['stamp']['cpu'] == 11227390
    start = next(x for x in enables if x['stamp']['frame'] == 376)
    assert start['safe'] and (start['stamp']['scanline'], start['stamp']['cycle']) == (259, 265)
    old_diag = [json.loads(x) for x in (OLD/'bass-diagnostic.jsonl').read_text().splitlines()]
    old_nmi = next(x for x in old_diag if x['kind'] == 'NMI-entry' and x['stamp']['frame'] == 376)
    nmi = next(x for x in diag if x['kind'] == 'NMI-entry' and x['stamp']['frame'] == 376)
    assert nmi['state']['CrossoverBehaviorVersion'] == nmi['state']['ProtoVariant'] == 1
    assert nmi['state']['SelectedCharacter'] == 1 and nmi['state']['SsLastPalette'] == 1
    assert old_nmi['queues']['buffer1_offset'] == 56 and nmi['queues']['buffer1_offset'] == 38
    old_packet = old_nmi['queues']['buffer1']
    packet = nmi['queues']['buffer1']
    assert old_packet[:25] == old_packet[25:50] == packet[:25]
    assert packet[25:31] == old_packet[50:56]
    assert packet[31:39] == [63, 12, 4, 15, 39, 23, 15, 0]
    parser = [x for x in diag if x['kind'] == 'actual-parser-head' and x['stamp']['frame'] == 376]
    ret = {x['data']['name']:x for x in diag if x['kind'] == 'actual-owner-return' and x['stamp']['frame'] == 376}
    assert ret['SamusFreezeUpdateScreen']['data']['inclusive_cycles'] == 1022
    assert ret['BankSwitchCHR']['data']['inclusive_cycles'] == 435
    assert not any(x['stamp']['frame'] >= 378 for x in diag)
    assert not any(x['kind'] == 'mm-weapon-component-complete' for x in events)
    assert not (n/'native-mm-weapon-profile.json').exists()
    reset = next(x for x in events if x['kind'] == 'declared-component-reset')
    frames = list(csv.DictReader((n/'actual-ppu-index.csv').open()))
    pixels = (n/'actual-ppu.argb').read_bytes();size = 256*240*4
    assert len(frames) == 377 and len(pixels) == len(frames)*size
    assert frames[-1]['updates'] == '2' and frames[-1]['phase'] == 'use'
    selected = [nmi, *parser, *[x for x in diag if x['kind'] == 'actual-owner-return' and x['stamp']['frame'] == 376],
                *enables, reset]
    put(a.output/'actual-source-evidence.json', selected)
    old_index = list(csv.DictReader((OLD/'actual-ppu-index.csv').open()))
    old_pixels = (OLD/'actual-ppu.argb').read_bytes()
    samples = []
    sheet = Image.new('RGB', (4*256, 2*264), '#151923');draw = ImageDraw.Draw(sheet)
    wanted = [('installed3b', OLD, old_index, old_pixels, f) for f in [372, 373, 374, 375]]
    wanted += [('cold-cache', n, frames, pixels, f) for f in [374, 375, 376, 377]]
    for j, (name, source, index, raw, f) in enumerate(wanted):
        i = next(i for i,z in enumerate(index) if int(z['ppu_frame']) == f)
        image_raw = raw[i*size:(i+1)*size]
        image = Image.frombytes('RGBA', (256, 240), image_raw, 'raw', 'BGRA').convert('RGB')
        x, y = j%4*256, j//4*264
        sheet.paste(image, (x, y+24));draw.text((x+2, y+4), name+' actual PPU '+str(f), fill='white')
        samples.append(dict(profile=name, source=str(source/'actual-ppu.argb'), frame=f,
                            row=index[i], raw_frame_sha256=hashlib.sha256(image_raw).hexdigest()))
    sheet.save(a.output/'actual-startup-whole-images.png', optimize=True)
    fail_raw = (n/'first-failure.argb').read_bytes();assert len(fail_raw) == size
    Image.frombytes('RGBA', (256,240), fail_raw, 'raw','BGRA').convert('RGB').save(a.output/'incomplete-failure-snapshot.png')
    put(a.output/'samples.json', samples)
    files = [x for x in n.iterdir() if x.is_file()]
    files += [B/x for x in ['ROOT-grant.json','readiness.json','bindings.json','command.json',
                            'launch-binding-v1.json','launch-outcome-v1.json','launch-host-v1.log']]
    files += [C/x for x in ['candidate.nes','candidate.dbg','candidate.lbl','candidate.map','source.patch','source-manifest.json','proof.json',
                            'cpu-v1/proof.json','lifecycle-v2/proof.json','build-controls-v1/proof.json']]
    files += [OLD/'bass-diagnostic.jsonl', OLD/'ability-dma-epochs.jsonl', OLD/'actual-ppu.argb', OLD/'actual-ppu-index.csv', Path(__file__)]
    put(a.output/'external-raw-manifest.json', {str(x):sha(x) for x in files})
    put(a.output/'proof.json', dict(review_completed=True, native_pass=False, native_launches=1, retries=0,
        candidate_ROM_sha256=sha(C/'candidate.nes'), source_manifest_sha256=sha(C/'source-manifest.json'),
        startup_duplicate_removed=True, actual_mode_readback=1, actual_variant_readback=1,
        startup_376_old_queue_offset=56, startup_376_new_queue_offset=38,
        startup_old_duplicate_25_byte_group=True, startup_new_single_25_byte_group=True,
        actual_new_additional_3F0C_command_bytes=7, actual_376_palette_gateway_cycles=1022,
        old_376_palette_gateway_cycles=1478, actual_376_CHR_cycles=435,
        actual_startup_376_enable=start, first_bad_enable=bad[0],
        first_failure=json.loads((n/'first-failure.json').read_text()),
        completed_DMA_pages=len(completed), full_DMA_writes_checked=256*len(completed),
        all_completed_DMA_sources_physical_bytes_order_masks_and_addresses_exact=True,
        scoped_safe_enables=sum(x['safe'] for x in enables), scoped_bad_enables=len(bad),
        completed_mechanics_cases=0, source_updates_before_failure=2,
        phase_reset_event=reset, completed_PPU_frames=len(frames), completed_PPU_bytes=len(pixels),
        actual_378_queue_or_parser_recorded=False, diagnostic_frame_range=[374,377],
        source_CHR_or_NMI_final_aggregate_summary_available=False, native_worker_released=True,
        external_manifest_sha256=sha(a.output/'external-raw-manifest.json'),
        evidence_sha256=sha(a.output/'actual-source-evidence.json'), samples_sha256=sha(a.output/'samples.json'),
        sheet_sha256=sha(a.output/'actual-startup-whole-images.png'), tool_sha256=sha(__file__),
        limits='Strict profile FALSE retained. First startup fixed; later378 too-late enable not qualified. No mechanics completed, no acquisition or all-graphics claim. Original six-case guards stopped after actual setup/use atupdate2. No final source/CHR/NMI aggregate emitted.353 fullDMA pages independently reparsed exactly, including failed-enable page. Actual378 preDMA VRAM/CHR packet unlogged because original diagnostic ends377. First-failure screenshot is incomplete scanline1, not a completed378 image. Additional3F0C packet differs from old stopped baseline; do not present measured gateway saving456 as pure624 model or matched whole-workload gain.'))
    print(json.dumps(dict(proof=str(a.output/'proof.json'), sha256=sha(a.output/'proof.json'), native_pass=False), indent=2))


if __name__ == '__main__':main()
