"""Execute the genuine WWF action interpreter for every wrestler/input.

The native donor snapshot supplies initialized game state. These explicit CPU
fixtures recover script timing and side effects; they do not qualify a host
port, substitute platform rules, or claim natural controller contact coverage.
"""
from pathlib import Path
import csv
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools/audit'), str(R/'tools')]
from py65.devices.mpu6502 import MPU
import wwf_roster_source_review_v1 as W

N = R/'build/wwf-action-donor-native-1031-v1/discovery'
O = R/'build/wwf-action-vm-recovery-1031-v1'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class Bus:
    def __init__(self, prg, ram):
        self.prg, self.bank = prg, 0
        self.ram = bytearray(2048)
        self.ram[:] = ram
        self.io, self.apu, self.writes, self.executed = {}, [], [], set()

    def __getitem__(self, a):
        if isinstance(a, slice):
            return [self[i] for i in range(a.start, a.stop, a.step or 1)]
        if a >= 0x8000:
            return self.prg[self.bank*32768+a-0x8000]
        if a < 0x2000:
            return self.ram[a & 2047]
        if a == 0x4015:
            return 0
        if a in self.io:
            return self.io[a]
        raise AssertionError(('Unmodeled source external read', hex(a), self.bank))

    def __setitem__(self, a, value):
        value &= 255
        self.writes.append((a, value))
        if a >= 0x8000:
            self.bank = value & 3
        elif a < 0x2000:
            self.ram[a & 2047] = value
        elif 0x4000 <= a <= 0x4017:
            self.apu.append((a, value)); self.io[a] = value
        else:
            raise AssertionError(('Unmodeled source external write', hex(a), value))


def call(b, pc, *, a=0, x=0, y=0, flags=0x30, limit=10000):
    c = MPU(memory=b, pc=pc)
    c.a, c.x, c.y, c.p, c.sp = a, x, y, flags, 253
    c.stPushWord(0x7eff)
    for _ in range(limit):
        if c.pc == 0x7f00:
            return c
        b.executed.add((b.bank, c.pc))
        assert b[c.pc] != 0, ('Unexpected sourceBRK', b.bank, hex(c.pc))
        c.step()
    raise AssertionError(('Source CPU bound', hex(pc), b.bank, hex(c.pc)))


def main():
    assert not O.exists()
    binding = json.loads((N/'capture/binding.json').read_text())
    result = json.loads((N/'capture/result.json').read_text())
    assert binding['exit_code'] == 0 and result['passed'] and result['dispatches'] == 1076
    for p, digest in binding['bindings'].items():
        assert sha(p) == digest, p
    raw = W.ROM.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == W.SHA
    prg, snapshot = raw[16:], (N/'capture/ram-match-entry.bin').read_bytes()
    assert len(snapshot) == 2048
    chars = W.tables(prg)
    source = list(csv.DictReader((N/'capture/script-dispatch.csv').open(newline='')))
    for line in source:
        address, opcode = int(line['pointer'])+int(line['cursor']), int(line['opcode'])
        assert prg[address-0x8000] == opcode
    O.mkdir()
    report = dict(passed=False, source_CPU_only=True, native_host=False, installed=False,
        original_donor_native_trace_verified=len(source), cases=[],
        native_identity_layout='E2E8 chooses script descriptor25 from2A+(actorX xor1). Thus state actor0 uses character2B, actor1 uses2A. The v1 trace column labels actor0_identity/actor1_identity record raw2A/2B selection fields and must not be read as actor-indexed identities.',
        timing_contract='E2E8 updates one actor selected by71&1 per video frame. Fixtures call actor0 at source phases0/2/4, advancing original8D frame counter by2 between its64 updates.',
        limitations=['CPU fixtures only; no host platform movement or combat contract is implemented here.',
                     'Native source ring bounds/contact remain active. Distinct input selectors are not proof every grapple/pin/rope action is eligible in SMB.',
                     'No full donor disassembly/rebuild, audible/native-host audio or unlock claim.'])
    all_pc = set()
    try:
        for character in chars:
            for inp, held, fresh in [('A',128,128), ('B',64,64), ('Up',8,0), ('Down',4,0),
                ('A+B',192,192), ('Up+A',136,128), ('Down+A',132,128),
                ('Up+B',72,64), ('Down+B',68,64), ('Up+A+B',200,192), ('Down+A+B',196,192)]:
                b = Bus(prg, snapshot)
                # Actual descriptor producer initializes native stats/palettes.
                b.ram[0x2a], b.ram[0x2b] = (character['id']+1)%6, character['id']
                call(b, 0xd1a5)
                for at in [0x3c,0x3d,0x3e,0x3f,0x40,0x41,0x8b,0x8c,0xa2,0xa3,0xa4,0xa5,0xcb,0xcc,0xc0,0xc1]:
                    b.ram[at] = 0
                b.ram[0x0d], b.ram[0x0e] = held, fresh
                call(b, 0xaf4d, x=0, y=0)
                action = b.ram[0x3e]
                expected = next(q['side_action'] for q in character['original_input_action_selectors'] if q['input'] == inp)
                assert action == expected, (character['name'], inp, action, expected)
                # Genuine producer continuation adopts requested3E into3C;
                # start after its two already-executed controller polls.
                call(b, 0xaed4)
                assert b.ram[0x3c] == action
                b.ram[0x0d] = b.ram[0x0e] = 0
                sequence = []
                for tick in range(64):
                    b.ram[0x71] = (tick*2)%6
                    b.ram[0x8d] = (snapshot[0x8d]+tick*2)&255
                    start = len(b.writes)
                    c = call(b, 0xe2e8)
                    sequence.append(dict(tick=tick, action=b.ram[0x3c], cursor=b.ram[0x40],
                        group=b.ram[0x32], pose=b.ram[0x34], x=b.ram[0x2c], y=b.ram[0x2e],
                        direction=b.ram[0x3a], CPU_cycles=c.processorCycles,
                        writes=b.writes[start:]))
                all_pc.update(b.executed)
                report['cases'].append(dict(character=character['id'], name=character['name'],
                    input=inp, native_action=action, source_updates=64, sequence=sequence,
                    original_audio_writes=b.apu, final_bank=b.bank))
        assert len(report['cases']) == 66
        report.update(passed=True, genuine_script_updates=4224,
            executed_native_PC_count=len(all_pc), executed_native_banks=sorted({bank for bank, pc in all_pc}))
    except Exception as e:
        report['error'] = repr(e)
        raise
    finally:
        report['bindings'] = {str(p.resolve()): sha(p) for p in [Path(__file__), Path(W.__file__), W.ROM,
            N/'ready.json', N/'capture/binding.json', N/'capture/result.json', N/'capture/ram-match-entry.bin',
            N/'capture/script-dispatch.csv']}
        (O/'controls.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
        (O/'executed-PCs.json').write_text(json.dumps(sorted(all_pc), indent=2)+'\n', encoding='utf-8', newline='\n')
        print(json.dumps(dict(passed=report['passed'], cases=len(report['cases']),
                             source_updates=report.get('genuine_script_updates'), error=report.get('error'))))


if __name__ == '__main__':
    main()
