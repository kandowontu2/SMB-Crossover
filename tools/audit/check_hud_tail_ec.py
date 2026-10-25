"""Compare compiled immediate HUD output, including foreign last-writer order."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import itertools
import json
import traceback

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
O = V / 'hud-tail-ee'
spec = importlib.util.spec_from_file_location('hud_ec_model', V / 'agent49-samus-bill-arsenal-a/palette_native_model_cu.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def at(ad):
    return ad if ad < 2048 else ad - 0x6000 + 2048


def put(im, raw, name, value, i=0):
    raw[at(im.ram[name] + i)] = value & 255


def seed(im, selector=0x43):
    raw = bytearray(10240)
    for seg in im.segs.values():
        if seg['name'] == 'SMCCODE':
            raw[seg['start']:seg['start'] + seg['size']] = im.raw[seg['ooffs']:seg['ooffs'] + seg['size']]
    for name, value in dict(CurrentBank=3 | (128 if im.mapper == 5 else 0), VRAM_Buffer1_Offset=0, ObjectOffset=3,
                            SelectedCharacter=7, NmiDisable=255, R1=0x73, R2=0x4d, R3=0x2e, R4=0x49, R5=0x32, R6=0x18, R7=0x50).items():
        put(im, raw, name, value)
    if im.mapper == 4:
        put(im, raw, 'BankShadow', selector)
    for name, digits in [('Player1ScoreDisplay', [0, 0, 1, 2, 5, 0]), ('Player2ScoreDisplay', [0, 9, 4, 2, 0, 0]),
                         ('Player1CoinDisplay', [1, 4]), ('Player2CoinDisplay', [2, 3]), ('TopScoreDisplay', [0, 0, 9, 9, 9, 9]), ('GameTimerDisplay', [3, 8, 6])]:
        for i, value in enumerate(digits):
            put(im, raw, name, value, i)
    return raw


def call(im, raw, a, p=1, selector=0x43):
    raw = bytearray(raw)
    raw[0x1ef] = 0xff
    raw[0x1f0] = 0x5c
    hook = im.hook('UpdateNumber')
    banks = {0x8000: 62, 0xa000: 3, 0xc000: 12, 0xe000: 63}
    q = m.execute(im, raw, [a, 17, 99, p, 238], banks, hook['address'], 0x5d00, 240)
    assert q['banks'] == banks
    assert q['selector'] == (selector if im.mapper == 4 else 0x47)
    return q


def append(im, raw, data):
    raw = bytearray(raw)
    off = raw[at(im.ram['VRAM_Buffer1_Offset'])]
    for i, value in enumerate(data + [0]):
        put(im, raw, 'VRAM_Buffer1', value, off + i)
    put(im, raw, 'VRAM_Buffer1_Offset', off + len(data))
    return raw


def queue(im, raw):
    off = raw[at(im.ram['VRAM_Buffer1_Offset'])]
    return list(raw[at(im.ram['VRAM_Buffer1']):at(im.ram['VRAM_Buffer1']) + off + 1])


def output(data):
    image = {}
    i = 0
    while data[i]:
        address = (data[i] << 8 | data[i + 1]) & 0x3fff
        flags = data[i + 2]
        count = flags & 63
        assert count
        i += 3
        for j in range(count):
            ad = (address + j * (32 if flags & 128 else 1)) & 0x3fff
            if 0x2000 <= ad < 0x3f00:
                ad = 0x2000 + ((ad - 0x2000) & 0x7ff)
            image[ad] = data[i if flags & 64 else i + j]
        i += 1 if flags & 64 else count
    assert i == len(data) - 1
    return image


def main():
    global O
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,default=V/'hud-tail-dz/source')
    parser.add_argument('--tag',default='hud-tail-ee')
    args=parser.parse_args()
    O=V/args.tag
    assert not O.exists()
    O.mkdir()
    report = dict(status='RUNNING', groups=[], goal_complete=False,
                  scope='Compiled no-ISR public numeric/queue semantics. Native callers and attained interrupts still require separate verification; no current ROM admission.')
    context = None
    try:
        for mapper in ('mmc3', 'mmc5'):
            ims = [m.q.Image(R / f'build/checkpoints/water-visible-cw/build/smb-crossover-{mapper}.nes'), m.q.Image(args.candidate / f'build/smb-crossover-{mapper}.nes')]
            group = dict(mapper=mapper, ROMs=[sha(im.path) for im in ims], raw_request_cases=0, ordering_cases=[], coalesced_cases=[], cycle_deltas=[])
            report['groups'].append(group)
            for a, p in itertools.product(range(256), (0, 1, 0x49, 0xc1)):
                selector = 0x40 | ((a + p) & 7)
                context = dict(mapper=mapper, a=a, p=p, selector=selector)
                qs = [call(im, seed(im, selector), a, p, selector) for im in ims]
                old, new = qs
                assert old['regs'] == new['regs'], ('registers', context, old['regs'], new['regs'])
                assert queue(ims[0], old['ram']) == queue(ims[1], new['ram'])
                assert old['banks'] == new['banks'] and old['selector'] == new['selector']
                L = ims[0].ram
                allowed = {L[n] for n in ('BillNativeReturnP', 'BillNativeReturnA', 'BillNativeReturnSelector')}
                allowed |= {L[n] + d for n, d in [('SafecallA_SMC', 1), ('FarcallJmpTarget_SMC', 1), ('FarcallJmpTarget_SMC', 2), ('NextBank_SMC', 1), ('SafereturnA_SMC', 1)]}
                dead = {ad for z in qs for pc, op, ad0, ad, value in z['trace'] if 0x100 <= ad <= 0x1ee and op in (0x08, 0x48, 0x20)}
                for i, (v, w) in enumerate(zip(old['ram'], new['ram'])):
                    if v != w:
                        ad = m.q.g.RAMS[i]
                        assert ad in allowed | dead, ('RAM', context, hex(ad), v, w)
                group['raw_request_cases'] += 1
                group['cycle_deltas'].append(new['cycles'] - old['cycles'])
            fixtures = {
                'partial-score': [0x20, 0x63, 1, 9], 'exact-score': [0x20, 0x62, 6, 9, 9, 9, 9, 9, 9],
                'vertical-score': [0x20, 0x43, 0x82, 9, 9], 'mirrored-score': [0x28, 0x63, 1, 9],
                'partial-coins': [0x20, 0x6e, 1, 9], 'nonoverlap': [0x20, 0x90, 3, 9, 8, 7],
                'palette': [0x3f, 0x11, 3, 0x16, 0x30, 0x27], 'RLE': [0x20, 0x90, 0x7f, 9],
                'vertical-RLE': [0x20, 0x90, 0xff, 9],
                'forged-tail-in-payload': [0x20, 0x80, 16, 7, 7, 0x20, 0x6d, 2, 1, 4, 0x20, 0x62, 6, 0, 0, 1, 2, 5, 0],
            }
            for name, foreign in fixtures.items():
                for order in ('before', 'after', 'between', 'before-repeated'):
                    context = dict(mapper=mapper, foreign=name, order=order)
                    observations = []
                    for im in ims:
                        raw = seed(im)
                        if order.startswith('before'):
                            raw = append(im, raw, foreign)
                        raw = bytearray(call(im, raw, 0x02)['ram'])
                        if order in ('after', 'between'):
                            raw = append(im, raw, foreign)
                        if order in ('between', 'before-repeated'):
                            put(im, raw, 'Player1ScoreDisplay', 3, 2)
                            put(im, raw, 'Player1CoinDisplay', 5, 1)
                            raw = call(im, raw, 0x02)['ram']
                        observations.append(queue(im, raw))
                    assert output(observations[0]) == output(observations[1]), context
                    group['ordering_cases'].append(dict(**context, old_length=len(observations[0])-1, new_length=len(observations[1])-1,
                                                        old_queue=observations[0], new_queue=observations[1], PPU_image_equal=True))
            for pattern in ((0x02, 0x02), (0x02, 0x13), (0x13, 0x02), (0x13, 0x13), (0x02,) * 5, (0x13,) * 5):
                observations = []
                for im in ims:
                    raw = seed(im)
                    for j, a in enumerate(pattern):
                        put(im, raw, 'Player1ScoreDisplay', j + 1, 4)
                        put(im, raw, 'Player2ScoreDisplay', j + 2, 4)
                        raw = bytearray(call(im, raw, a)['ram'])
                    observations.append(queue(im, raw))
                assert output(observations[0]) == output(observations[1])
                assert len(observations[1]) == 15
                group['coalesced_cases'].append(dict(requests=list(pattern), old_bytes=len(observations[0])-1, new_bytes=14, PPU_image_equal=True))
            group['cycle_delta_min'] = min(group['cycle_deltas'])
            group['cycle_delta_max'] = max(group['cycle_deltas'])
            print(mapper, group['raw_request_cases'], 'raw requests;', len(group['ordering_cases']), 'ordering cases', flush=True)
        report['status'] = 'PASS_COMPILED_RAW_REQUESTS_AND_FOREIGN_ORDER_PRIVATE_CANDIDATE'
    except Exception as error:
        report.update(status='FAILURE_RETAINED', context=context, error=repr(error), traceback=traceback.format_exc())
        raise
    finally:
        (O / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
