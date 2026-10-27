"""Reparse the one ce635 six-case success, physical pages and actual busy packet."""
from pathlib import Path
import argparse
import collections
import csv
import hashlib
import json
from PIL import Image, ImageDraw

D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
B = D / 'robot-color-rotation-combined-ready-v1'
ROM_SHA = 'ce635f6e8793d096ba50adec9cdf1fc2dd41fd487e4acd4d0972af03af9ea111'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
put = lambda p, z: Path(p).write_text(json.dumps(z, indent=2) + '\n')
rows = lambda p: [json.loads(x) for x in Path(p).read_text().splitlines()]


def sheet(path, items):
    image = Image.new('RGB', (1024, ((len(items) + 3) // 4) * 264), '#151923')
    draw = ImageDraw.Draw(image)
    for j, (caption, frame) in enumerate(items):
        x, y = j % 4 * 256, j // 4 * 264
        image.paste(frame, (x, y + 24))
        draw.text((x+2, y+3), caption, fill='white')
    image.save(path, optimize=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    ready = json.loads((B / 'readiness.json').read_text())
    assert ready['candidate_ROM_sha256'] == ROM_SHA
    for f, h in json.loads((B / 'bindings.json').read_text()).items():
        assert sha(f) == h, f
    launch = json.loads((B / 'launch-outcome-v1.json').read_text())
    assert launch['returncode'] == 0 and launch['attempt'] == 1 and launch['no_retry']
    assert launch['native_worker_released'] and launch['strict_profile_pass']
    n = B / 'native'
    assert not (n / 'first-failure.json').exists()
    result = json.loads((n / 'native-mm-weapon-profile.json').read_text())
    assert result['passed'] and result['actual_mode_readback'] == 1 and result['hard']
    assert not result['acquisition'] and not result['goal_complete']
    assert result['updates'] == 656 and len(result['cases']) == 6
    cases = result['cases']
    for case, types, charges in zip(cases[:3], [[1], [1,2], [1,3]], [[0], [0,56], [0,87]]):
        assert [x['type'] for x in case['primarySpawns']] == types
        assert [x['charge'] for x in case['primarySpawns']] == charges
        assert case['beforeAmmo'] == case['finalAmmo'] == [0]*7 + [20]
    rush, gate, balance = cases[3:]
    assert rush['summoned'] and rush['existingAttack'] and rush['rushDraws'] == 124
    assert rush['landed'] == 479 and rush['launch'] == rush['bounced'] == 499
    assert rush['beforeAmmo'] == [0]*7 + [20] and rush['finalAmmo'] == [0]*7 + [8]
    assert rush['completed'] == 570
    assert gate['refused'] and gate['beforeAmmo'] == gate['finalAmmo'] == [0]*7 + [3]
    assert balance['balanceChoice'] and balance['refillCredits'] == 8
    assert balance['beforeAmmo'] == [60,4,0,0,0,0,0,8]
    assert balance['finalAmmo'] == [60,12,0,0,0,0,0,8] and balance['completed'] == 656
    assert result['minSP'] == 223 and result['nmis'] == result['irq_scroll_stores'] == 655
    assert result['hardware_chr_checks'] == 7860 and result['complete_dma_checks'] == 649
    events = rows(n / 'events.jsonl')
    counts = collections.Counter(x['kind'] for x in events)
    assert counts['mm-weapon-component-complete'] == 6
    assert counts['actual-rush-direct-debit'] == 1 and counts['actual-mm-balancer-credit'] == 2
    credit = [x for x in events if x['kind'] == 'actual-mm-balancer-credit']
    assert [x['data'] for x in credit] == [dict(before=4,after=8,credits=4,index=18), dict(before=8,after=12,credits=8,index=18)]
    epochs = rows(n / 'ability-dma-epochs.jsonl')
    complete = [x for x in epochs if x['kind'] == 'completed-DMA-before-render-enable']
    assert len(complete) == 1001
    for x in complete:
        assert x['source'] == x['hardware'] and len(x['source']) == len(x['writes']) == 256
        assert not x['differences'] and x['page'] == 2
        assert x['start']['oamaddr'] == x['complete']['oamaddr'] == 0
        assert x['start']['mask'] & 24 == x['complete']['mask'] & 24 == 0
        for i, write in enumerate(x['writes']):
            assert write['value'] == x['source'][i] and write['stamp']['oamaddr'] == i
            assert write['stamp']['mask'] & 24 == 0
    enables = [x for x in epochs if x['kind'] == 'actual-PPUMASK-write' and x['scoped'] and x['enabling']]
    assert enables and all(x['safe'] for x in enables)
    selected = {x['stamp']['frame']:x for x in enables if x['stamp']['frame'] in [376,377,378,992,993]}
    assert [(selected[f]['stamp']['scanline'], selected[f]['stamp']['cycle']) for f in [376,377,378,992,993]] == [(258,150),(257,213),(-1,264),(-1,243),(251,129)]
    diag = rows(n / 'bass-diagnostic.jsonl')
    entries = [x for x in diag if x['kind'] == 'NMI-entry']
    assert len(entries) == 7 and all(x['data']['incoming_NmiDisable'] == 0 for x in entries)
    color = [x for x in diag if x['kind'] in ['actual-owner-entry','actual-owner-return'] and x['data']['name'] == 'ColorRotation']
    busy = [x for x in color if x['stamp']['frame'] == 991]
    assert len(busy) == 2
    assert all(x['stamp']['updates'] == 616 and x['state']['FrameCounter'] == 0 and x['queues']['buffer1_offset'] == 47 for x in busy)
    assert busy[1]['data']['inclusive_cycles'] == 23
    assert busy[0]['queues']['buffer1'] == busy[1]['queues']['buffer1']
    during = [x for x in diag if x['kind'] == 'actual-buffer-or-lease-write' and busy[0]['stamp']['cpu'] <= x['stamp']['cpu'] <= busy[1]['stamp']['cpu']]
    assert not during
    consumed = next(x for x in entries if x['stamp']['frame'] == 992)
    assert consumed['queues']['buffer1_offset'] == 47 and consumed['queues']['buffer1'][47] == 0
    assert consumed['queues']['buffer1'][:47] == busy[0]['queues']['buffer1'][:47]
    old = rows(D / 'robot-balancer-budget-ready-v1/native/bass-diagnostic.jsonl')
    old_entry = next(x for x in old if x['kind'] == 'NMI-entry' and x['stamp']['frame'] == 993)
    assert old_entry['queues']['buffer1'][:47] == consumed['queues']['buffer1'][:47]
    assert old_entry['queues']['buffer1'][47:55] == [63,12,4,15,23,23,15,0]
    owner = [x for x in diag if x['kind'] == 'actual-owner-return' and x['stamp']['frame'] == 992]
    times = {x['data']['name']: x['data']['inclusive_cycles'] for x in owner}
    assert times['SamusFreezeUpdateScreen'] == 1249 and times['BankSwitchCHR'] == 426
    assert 'ColorRotateOffset' not in consumed['state']
    assert max(x['stamp']['frame'] for x in diag) == 996
    evidence = dict(actual_cases=cases, actual_enable_boundaries=selected,
        actual_busy_ColorRotation_entry_and_return=busy, actual_pending_packet_consumer=consumed,
        actual992_owner_returns=owner, actual_Balancer_credit=credit,
        native_counter_and_next_retry_limit='ColorRotateOffset not bound in frozen state. Focus ends996 atFrameCounter5, before nexteligible999; no native counter/retry reconstruction. Separate source seven-retry proof remains exactca9a scope.',
        original_df_false_entry=old_entry,
        combined_timing_limit='New busy packet consumes on992, old on993 acrosslag992. Combined renderer+mixer/palette/HUD source differs; do not call this a matched component-only timing/FPS trial.')
    put(a.output / 'native-evidence.json', evidence)
    frames = list(csv.DictReader((n / 'actual-ppu-index.csv').open(newline='')))
    pixels = (n / 'actual-ppu.argb').read_bytes()
    capture = json.loads((n / 'ppu-capture-native-result.json').read_text())
    size = 256*240*4
    assert len(frames) == capture['frames'] == 1031 and len(pixels) == capture['bytes'] == size*1031
    assert capture['original_done_seen']
    byframe = {int(x['ppu_frame']): i for i, x in enumerate(frames)}
    def frame(f):
        i = byframe[f]
        raw = pixels[size*i:size*(i+1)]
        return Image.frombytes('RGBA',(256,240),raw,'raw','BGRA').convert('RGB'), raw
    samples = []
    groups = collections.defaultdict(list)
    raw_manifest = {str(f):sha(f) for f in n.iterdir() if f.is_file()}
    for event in events:
        if event['kind'] != 'ppu-frame-captured':
            continue
        name = event['data']['name']
        path = n / (name + '.argb')
        image, raw = frame(event['wall'])
        assert path.read_bytes() == raw and len(raw) == size
        raw_manifest[str(path)] = sha(path)
        samples.append(dict(name=name, event=event, actual_PPU_row=frames[byframe[event['wall']]], raw_sha256=sha(path)))
        groups['primary' if name.startswith(('basic-','weak-','full-')) else 'support'].append((name+' PPU'+str(event['wall']), image))
    assert len(samples) == 34
    for group, items in groups.items():
        sheet(a.output / (group + '-actual-whole-images.png'), items)
    windows = {}
    landed = next(x['event']['wall'] for x in samples if x['name'] == 'rush-lifecycle-landed')
    for name, wanted in [('startup',range(374,382)),('busy-packet',range(990,998)),('rush-consecutive',range(landed-3,landed+33))]:
        data, items = [], []
        for f in wanted:
            image, raw = frame(f)
            data.append(dict(frame=f, actual_PPU_row=frames[byframe[f]], raw_sha256=hashlib.sha256(raw).hexdigest()))
            items.append(('Proto actual PPU'+str(f),image))
        sheet(a.output / (name + '-actual-whole-images.png'), items)
        windows[name] = data
    put(a.output / 'samples.json', dict(stages=samples, consecutive_windows=windows))
    for f in [B / x for x in ['readiness.json','bindings.json','ROOT-grant.json','command.json','launch-binding-v1.json','launch-outcome-v1.json','launch-host-v1.log']] + [Path(__file__)]:
        raw_manifest[str(f)] = sha(f)
    put(a.output / 'external-raw-manifest.json', raw_manifest)
    put(a.output / 'proof.json', dict(review_completed=True, native_profile_pass=True,
        ROM_sha256=ROM_SHA, actual_mode=1, actual_Proto_variant=1, native_launches=1, retries=0,
        native_worker_released=True, source_updates=656, six_components=6,
        all_mode_complete256DMA_pages=1001, independently_verified_source_destination_writes=1001*256,
        scoped_complete_DMA_checks=result['complete_dma_checks'], scoped_NMI_returns=result['nmis'],
        scoped_safe_enables=len(enables), scoped_bad_enables=0, hardware_CHR_checks=7860, physical_IRQ31_stores=655, min_SP=223,
        all_source_hardware_pages_order_OAMADDR_disabledmask_exact=True,
        actual_992_palette_gateway=1249, original_df993_gateway=1417, parser_work_reduction=168,
        actual_992_CHR=426, actual_busy47B_return_cycles=23, actual_next_native_counter_retry_unobserved=True,
        actual_enable_boundaries=selected, actual_complete_PPU_frames=1031, actual_PPU_bytes=len(pixels),
        stage_placements=34, startup_placements=8, busy_placements=8, Rush_placements=36,
        source_primary_art_callback_checks=counts['actual-mm-primary-art'], source_event_counts=dict(counts),
        agent_visual_review_pending=True,
        evidence_sha256=sha(a.output / 'native-evidence.json'), samples_sha256=sha(a.output / 'samples.json'),
        external_manifest_sha256=sha(a.output / 'external-raw-manifest.json'), tool_sha256=sha(__file__),
        limits='One combinedce635 stagedProtoHard sixcase native. ca9a standalone remainsunrun; earlierFALSEs immutable. No naturalacquisition/fullroster/allweapon/per-shotfairness/matchedFPS claim. Actualcounter/retry outsidefocus unlogged. Selected wholeimage review is separate; hardware/art pointer passes do not establish clean pixels or absence of8sprite omissions. No installation.'))
    print(json.dumps(dict(proof=str(a.output / 'proof.json'), sha256=sha(a.output / 'proof.json'),
        native_profile_pass=True, cases=6, full256DMA=1001, safe_enables=len(enables)), indent=2))


if __name__ == '__main__':
    main()
