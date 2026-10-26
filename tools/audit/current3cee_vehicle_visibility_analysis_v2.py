"""Offline opaque-body/first-eight attribution, without inventing background pixels.

The frozen v1 physical/source checks are reused unchanged.  Its failed sky-only
background model is retained as negative evidence; this model makes no background
tile claim.  Actual RGB is compared exactly wherever an admitted front sprite owns
the coordinate, and body-color absence is measured separately elsewhere.
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse, hashlib, json, traceback
from PIL import Image, ImageDraw
import current3cee_vehicle_visibility_analysis_v1 as old


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--packet', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    try:
        assert sha(old.__file__) == '182cac6e7d0f55aeb493ffd542d90e48ea1316a218e8e24d4bd1b3eaa28ddaed'
        ready = old.get(a.packet / 'readiness.json')
        execution = old.get(a.packet / 'execution.json')
        assert execution['passed'] and execution['worker_released']
        assert all(sha(path) == digest for path, digest in ready['bindings'].items())
        raw = Path(ready['rom']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == old.SHA
        failure = a.packet / 'analysis-v1/failure.json'
        assert old.get(failure)['passed'] is False
        bindings = {str(Path(__file__).resolve()): sha(__file__),
                    str(Path(old.__file__).resolve()): sha(old.__file__),
                    str(failure): sha(failure),
                    str(a.packet / 'readiness.json'): sha(a.packet / 'readiness.json'),
                    str(a.packet / 'execution.json'): sha(a.packet / 'execution.json')}
        reports = []
        for case, frames in old.TARGETS.items():
            probe = old.Probe(a.packet, case, raw)
            samples = {f: probe.sample(f) for f in sorted(set(frames + old.CONTROLS[case]))}
            cal = defaultdict(Counter)
            for f in old.CONTROLS[case]:
                q = samples[f]
                limited, _ = probe.render(q, 8)
                for (x, y), v in limited.items():
                    if y >= 40 and not (v['attr'] & 32):
                        cal[(q['end']['mask'] & 225, v['NES_color'])][q['image'].getpixel((x, y))] += 1
            colors = {key: c.most_common(1)[0][0] for key, c in cal.items()
                      if sum(c.values()) >= 5 and c.most_common(1)[0][1] / sum(c.values()) >= .98}
            calibration = [dict(mask=key[0], NES_color=key[1], RGB=list(c.most_common(1)[0][0]),
                                samples=sum(c.values()), majority=c.most_common(1)[0][1], accepted=key in colors)
                           for key, c in sorted(cal.items())]
            rows = []
            sheet = Image.new('RGB', (1024, 260 * ((len(frames) + 3) // 4)), '#202020')
            draw = ImageDraw.Draw(sheet)
            for index, f in enumerate(frames):
                q = samples[f]
                eight, selection = probe.render(q, 8)
                full, _ = probe.render(q, 64)
                body8 = {xy: v for xy, v in eight.items() if v['body']}
                body64 = {xy: v for xy, v in full.items() if v['body']}
                admitted_checks = 0
                for xy, v in eight.items():
                    key = (q['end']['mask'] & 225, v['NES_color'])
                    if xy[1] >= 40 and not (v['attr'] & 32) and key in colors:
                        assert q['image'].getpixel(xy) == colors[key], dict(
                            case=case, frame=f, coordinate=xy, admitted_front_sprite=v,
                            actual=list(q['image'].getpixel(xy)), expected=list(colors[key]))
                        admitted_checks += 1
                exclusions = []
                counts = Counter()
                for xy, v in body64.items():
                    if xy in body8:
                        continue
                    allslots, first8 = selection[xy[1]]
                    if v['slot'] in first8:
                        continue
                    assert len(first8) == 8 and v['slot'] in allslots
                    key = (q['end']['mask'] & 225, v['NES_color'])
                    own = colors.get(key)
                    present = eight.get(xy)
                    actual = q['image'].getpixel(xy)
                    front = present is not None and not (present['attr'] & 32)
                    expected = colors.get((q['end']['mask'] & 225, present['NES_color'])) if front else None
                    # No assumption is made about background patterns, mirroring,
                    # scroll, or a behind-background sprite's final color.
                    if front and expected is not None:
                        assert actual == expected, dict(case=case, frame=f, xy=xy, present=present,
                                                       actual=actual, expected=expected)
                    if own is None or v['attr'] & 32:
                        status = 'body_color_uncalibrated_or_behind_background'
                    elif actual == own:
                        status = 'excluded_source_slot_same_RGB_ambiguous'
                    elif front and expected is not None:
                        status = 'body_color_absent_known_front_sprite'
                    else:
                        status = 'body_color_absent_background_not_modeled'
                    counts[status] += 1
                    exclusions.append(dict(
                        x=xy[0], y=xy[1], body_slot=v['slot'], tile=v['tile'], attr=v['attr'],
                        opaque_value=v['value'], source_pattern=v['pattern'],
                        source_NES_color=v['NES_color'], source_RGB=list(own) if own else None,
                        actual_RGB=list(actual), known_front_sprite_RGB=list(expected) if expected else None,
                        known_front_sprite=present if front else None, classification=status,
                        background_source_not_modeled=not front,
                        first_eight_slots=first8, all_row_slots=allslots,
                        first_eight_owners=['body' if i in q['body']['indices'] else
                                            'pre-body actor/projectile' if ((i * 4 - q['body']['rotation']) & 255) < q['body']['logical_start']
                                            else 'world/score/other' for i in first8]))
                b = q['body']
                absent = sum(n for k, n in counts.items() if k.startswith('body_color_absent_'))
                path = probe.native / 'frames' / f'{f:06d}.png'
                row = dict(actual_PPU_frame=f, publication=q['pub']['id'], DMA=q['end']['DMA'],
                           actual_start=q['start']['ppu'], actual_end=q['end']['ppu'],
                           DMA_started=q['start']['DMA_ppu'], DMA_completed=q['start']['DMA_complete'],
                           hardware_exact_source256=True, completed_DMA_writes=256,
                           no_OAM_change_between_start_and_end=True, actual_pattern_pages=q['banks'],
                           palette=q['end']['palette'], body_record_bank=b['record_bank'],
                           body_record_pointer=b['pointer'], body_record=b['record'],
                           body_tuple_projection_exact=True, body_part_count=b['length'] // 4,
                           body_physical_indices=b['indices'],
                           body_wraps=any(y < x for x, y in zip(b['indices'], b['indices'][1:])),
                           flags_at_body=b['ram'], flags_at_publication=q['pub']['ram'],
                           flags_at_DMA=probe.dmas[q['end']['DMA']]['ram'],
                           unlimited_sprite_body_candidate_pixels=len(body64),
                           first8_sprite_body_candidate_pixels=len(body8),
                           RGB_verified_admitted_front_sprite_pixels=admitted_checks,
                           opaque_body_pixels_excluded_by_first8=len(exclusions),
                           RGB_body_color_absent_at_excluded_pixels=absent,
                           exclusion_classifications=dict(counts), opaque_exclusions=exclusions,
                           actual_whole_PPU_path=str(path), actual_whole_PPU_sha256=sha(path))
                rows.append(row)
                x, y = index % 4 * 256, index // 4 * 260
                sheet.paste(q['image'], (x, y + 20))
                draw.text((x, y), f'{case} {f} body {len(body8)}/{len(body64)}', fill='white')
                bindings[str(path)] = sha(path)
            target = a.output / (case + '-attribution.json')
            old.put(target, dict(passed=True, case=case, calibration_frames=old.CONTROLS[case],
                                 calibration=calibration, findings=rows,
                                 limits='Physical/source first-eight exclusions and exact front-sprite RGB only. Background tile pixels are not reconstructed. Equal RGB is ambiguous, not a body-visibility proof. No repair or whole-frame simulation.'))
            sheet.save(a.output / (case + '-actual-PPU.png'))
            reports.append(dict(case=case, frames=len(rows),
                                opaque_first8_exclusions=sum(r['opaque_body_pixels_excluded_by_first8'] for r in rows),
                                RGB_body_color_absent=sum(r['RGB_body_color_absent_at_excluded_pixels'] for r in rows),
                                admitted_front_pixel_checks=sum(r['RGB_verified_admitted_front_sprite_pixels'] for r in rows),
                                path=str(target), sha256=sha(target)))
            for directory in [a.packet / case, probe.native]:
                bindings.update({str(f): sha(f) for f in directory.iterdir() if f.is_file() and
                                 (f.suffix in ['.json', '.jsonl', '.bin'] or f.name == 'direct-frame-index.csv')})
        old.put(a.output / 'bindings.json', bindings)
        old.put(a.output / 'proof.json', dict(
            passed=True, ROM_sha256=old.SHA, offline_only=True, native_workers_released=True,
            cases=reports, bindings_sha256=sha(a.output / 'bindings.json'),
            preserved_offline_v1_failure_sha256=sha(failure), no_game_changes=True,
            body_visibility_problem_remains_open=True,
            scope='Two exact read-only replays and 19 selected physical/source/RGB epochs. No reconstructed background, game fix, global visibility or performance verdict.'))
        print(json.dumps(dict(passed=True, cases=reports, proof_sha256=sha(a.output / 'proof.json')), indent=2))
    except BaseException as error:
        old.put(a.output / 'failure.json', dict(passed=False, offline_only=True, error=repr(error),
                                               traceback=traceback.format_exc(), tool_sha256=sha(__file__), native_untouched=True))
        (a.output / 'failed-tool.py').write_bytes(Path(__file__).read_bytes())
        raise


if __name__ == '__main__':
    main()
