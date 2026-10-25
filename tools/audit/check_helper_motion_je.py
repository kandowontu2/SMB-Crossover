"""Verify compiled helper motion in isolation and bind its unchanged HR layout."""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import random

R = Path(__file__).resolve().parents[2]
O = R / 'build/verification/crossover-helpers-jb/motion-check-je'
MODEL = R / 'build/verification/agent49-samus-bill-arsenal-a/palette_native_model_cu.py'
ROM = R / 'build/verification/crossover-helpers-jb/motion-build-jd-mmc3/smb-crossover-mmc3.nes'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
at = lambda a: a if a < 0x800 else a - 0x6000 + 0x800


def main():
    assert not O.exists()
    O.mkdir()
    spec = importlib.util.spec_from_file_location('helper_motion_cpu', MODEL)
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    im = model.q.Image(ROM)
    old = model.q.Image(R / 'build/checkpoints/ryu-overlap-hr/build/smb-crossover-mmc3.nes')
    assert all(im.ram[n] == address for n, address in old.ram.items())
    globals_at = lambda image: {(s['name'], s['val']) for s in image.data['sym'] if s.get('scope') == 1 and 'seg' in s and 'val' in s}
    assert globals_at(old) <= globals_at(im)
    a, b = old.raw, im.raw
    assert len(a) == len(b) and a[:16] == b[:16] and a[16 + 512 * 1024:] == b[16 + 512 * 1024:]
    changed = {(i - 16) // 8192 for i, (v, w) in enumerate(zip(a, b)) if v != w}
    assert changed == {24}, changed
    records = json.loads((ROM.parent.parent / 'source/src/crossover_helper_data.json').read_text())['records']
    allowed = {im.ram[n] + i for n, count in (
        ('HpSlot', 1), ('HpTemp', 1), ('HpTemp2', 1), ('HpOffset', 1), ('HpSineIndex', 1),
        ('HpPhaseLo', 3), ('HpPhaseMid', 3), ('HpPhaseHi', 3),
        ('HpXLo', 3), ('HpXHi', 3), ('HpY', 3), ('HpPreviousXLo', 3),
        ('HpPreviousXHi', 3), ('HpPreviousY', 3)) for i in range(count)}
    rng = random.Random(20261022)
    cases = []
    digest = hashlib.sha256()
    phases = [0, 1, 0x3fffff, 0x400000, 0x7fffff, 0x800000,
              0xbfffff, 0xc00000, 0xffffff] + [rng.randrange(1 << 24) for _ in range(7)]
    for record, data in enumerate(records):
        for slot in range(3):
            for visible in (0, 1):
                for phase in phases:
                    ram = bytearray(10240)
                    def put(n, value, i=0):
                        ram[at(im.ram[n] + i)] = value & 255
                    put('HpRecord', record, slot)
                    put('HpVisible', visible, slot)
                    for n, v in zip(('HpPhaseLo', 'HpPhaseMid', 'HpPhaseHi'), (phase, phase >> 8, phase >> 16)):
                        put(n, v, slot)
                    put('HpXLo', data['center_x'], slot)
                    put('HpXHi', data['center_x'] >> 8, slot)
                    put('HpY', data['top_y'], slot)
                    ram[0x1d1:0x1d3] = bytes((0xff, 0x5c))
                    result = model.execute(im, ram, [77, slot, 231, 0x45, 0xd0],
                        {0x8000: 62, 0xa000: 24, 0xc000: 34, 0xe000: 63},
                        im.hook('HpMotionTick')['address'], 0x5d00, 0xd2)
                    final = result['ram']
                    get = lambda n: final[at(im.ram[n] + slot)]
                    step = 44503 if data['axis'] else 66754
                    actual_phase = get('HpPhaseLo') + 256 * get('HpPhaseMid') + 65536 * get('HpPhaseHi')
                    assert actual_phase == ((phase + step * visible) & 0xffffff)
                    sample = phase >> 14
                    folded = sample % 512
                    if folded >= 256:
                        folded = 511 - folded
                    amplitude = 75 if data['axis'] else 30
                    displacement = math.floor(amplitude * math.sin(folded * math.pi / 512) + .5)
                    if sample >= 512:
                        displacement = -displacement
                    if not visible:
                        displacement = 0
                    x = get('HpXLo') + 256 * get('HpXHi')
                    y = get('HpY')
                    assert x == data['center_x'] + (0 if data['axis'] else displacement)
                    assert y == data['top_y'] + (displacement if data['axis'] else 0)
                    assert get('HpPreviousXLo') + 256 * get('HpPreviousXHi') == data['center_x']
                    assert get('HpPreviousY') == data['top_y']
                    actual_stack = {physical for pc, opcode, address, physical, value in result['trace'] if 0x100 <= physical < 0x200}
                    assert all(v == w or i in actual_stack or (i if i < 0x800 else i - 0x800 + 0x6000) in allowed
                               for i, (v, w) in enumerate(zip(ram, final)))
                    digest.update(final)
                    cases.append(result['cycles'])
    # Bound native integer sampling against the continuous source sine for
    # every16-bit angle, separately from the compiled table-folding oracle.
    errors = {}
    for amplitude in (30, 75):
        largest = 0
        for phase in range(65536):
            sample = phase >> 6
            folded = sample % 512
            if folded >= 256:
                folded = 511 - folded
            pixel = math.floor(amplitude * math.sin(folded * math.pi / 512) + .5)
            if sample >= 512:
                pixel = -pixel
            largest = max(largest, abs(pixel - amplitude * math.sin(phase * 2 * math.pi / 65536)))
        errors[str(amplitude)] = largest
        assert largest < 1
    report = dict(passed=True, compiled_cases=len(cases), result_digest=digest.hexdigest(),
        cycles=[min(cases), max(cases)], phase_sampling_errors_pixels=errors,
        ROM_sha256=sha(ROM), script_sha256=sha(__file__), all_old_PC_RAM_header_CHR_unchanged=True,
        changed_banks=sorted(changed), main_changed=False, integrated=False,
        scope='Compiled motion component and explicit pixel-quantization bound only; no native helper playthrough, collision, carry, artwork, pause or offscreen-admission certification.', goal_complete=False)
    (O / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
