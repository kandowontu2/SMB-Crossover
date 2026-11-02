"""Check genuine public callbacks, full-header rejection and interruption safety."""
import itertools
import json
import re
from pathlib import Path
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from prepare_selected_native_packet_v1 import R, sha

O = R / 'build/metal-reservation-1102-v42'
S = R / 'build/metal-storm-idle-shots-1101-v41'
BASE = R / 'build/excitebike-pose-1101-v3/current4.nes'


def seed(rom, component):
    m = M.fresh(scoped_load(rom))
    for bank, off, name in [(3, 0, 'native-actor.bin'), (2, 0xd00, 'native-render.bin'),
                            (2, 0x1ba0, 'native-extra.bin')]:
        data = (component / name).read_bytes()
        m.ram[bank][off:off + len(data)] = data
    for bank in [2, 3]:
        m.ram[bank][0x1fe0:0x1ff0] = (component / 'native-cookie.bin').read_bytes()
    M.put(m, SelectedCharacter=35, OperMode=1, GameEngineSubroutine=8, CurrentPlayer=0,
          NumberofLives=2, Player_X_Position=40, Player_PageLoc=0, Player_Y_Position=176,
          Player_Y_HighPos=1, FrameCounter=1, GamePauseStatus=0, SavedJoypadBits=0)
    return m


def main():
    seeds = [seed(BASE, S), seed(O / 'candidate.nes', O)]
    cases = 0
    for bits, flags, px in itertools.product([0, 1, 2, 128], [0x30, 0xf1], [40, 120]):
        pair = []
        for seed_m in seeds:
            m = M.fork(seed_m)
            M.put(m, SavedJoypadBits=bits, Player_X_Position=px)
            out = M.invoke(m, 'HuMovement', p=flags)
            pair.append((m, out))
        (a, z), (b, w) = pair
        assert all(z[k] == w[k] for k in ['A', 'X', 'Y', 'P'])
        assert a.rawtags == b.rawtags
        assert bytes(a.ram[2][:0x81a]) == bytes(b.ram[2][:0x81a]), (bits, flags, px)
        for lo, hi in [(0x83d, 0x880), (0x900, 0xd00)]:
            assert a.ram[2][lo:hi] == b.ram[2][lo:hi]
        for field in ['Player_X_Position', 'Player_PageLoc', 'Player_Y_Position', 'Player_Y_HighPos',
                      'Player_X_Speed', 'Player_XSpeedAbsolute', 'Player_Y_Speed', 'Player_State',
                      'Player_Pos_ForScroll', 'Player_X_Scroll', 'PlayerFacingDir', 'PlayerSize', 'CrouchingFlag']:
            assert M.get(a, field) == M.get(b, field), field
        assert M.get(b, 'ObjectMetasprite') == 0
        assert M.get(b, 'SmPosePtr') + 256 * M.get(b, 'SmPosePtr', 1) == address(b.bundle, 'ObjectMetasprite')
        cases += 1
    rejects = 0
    for byte in range(32):
        pair = []
        for seed_m in seeds:
            m = M.fork(seed_m)
            m.ram[2 + byte // 16][0x1fe0 + byte % 16] ^= 1
            before = [bytes(q) for q in m.ram]
            out = M.invoke(m, 'HuMovement')
            assert before == [bytes(q) for q in m.ram]
            assert not out['P'] & 1
            pair.append(out)
        assert all(pair[0][k] == pair[1][k] for k in ['A', 'X', 'Y', 'P'])
        rejects += 1

    labels = {n: int(a, 16) for a, n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',
                                                 (O / 'component.lbl').read_text(), re.M)}
    ranges = [(labels['MsRSave'], labels['MsRPosition']),
              (labels['MsRenderDraw'], labels['MsRBody']),
              (labels['Ms12Movement'], labels['Ms12NeedConstructor'])]
    native = M.NesMPU
    seen, counts = set(), {'IRQ': 0, 'lagNMI': 0}

    class Probe(native):
        def step(self):
            mem, pc = self.memory, self.pc
            key = (pc, self.sp)
            if mem.rawtags[2] == 2 and any(lo <= pc < hi for lo, hi in ranges) and key not in seen:
                seen.add(key)
                for kind in counts:
                    if kind == 'IRQ' and self.p & 4:
                        continue
                    n = M.fork(mem)
                    c = native(memory=n, pc=pc)
                    for attr in ['a', 'x', 'y', 'p', 'sp', 'pc']:
                        setattr(c, attr, getattr(self, attr))
                    regs = (c.a, c.x, c.y, c.p, c.sp, c.pc)
                    scratch, smc = bytes(n[3:11]), bytes(n[0x15a:0x17b])
                    ram, maps = [bytes(q) for q in n.ram], list(n.rawtags)
                    maps[2] = M.get(n, 'CurrentBankC')
                    c.irq() if kind == 'IRQ' else c.nmi()
                    for _ in range(200000):
                        if (c.a, c.x, c.y, c.p, c.sp, c.pc) == regs:
                            break
                        assert n[c.pc] != 0, ('ISR BRK', kind, hex(pc), hex(c.pc))
                        c.step()
                    else:
                        raise AssertionError(('ISR return', kind, hex(pc)))
                    assert scratch == bytes(n[3:11]) and smc == bytes(n[0x15a:0x17b])
                    assert ram == [bytes(q) for q in n.ram] and maps == n.rawtags
                    counts[kind] += 1
            return native.step(self)

    M.NesMPU = Probe
    try:
        m = M.fork(seeds[1])
        M.put(m, DisableScreenFlag=1, NmiDisable=255)
        M.invoke(m, 'HuMovement', p=0x31)
        M.invoke(m, 'HuDrawAll', p=0x31)
    finally:
        M.NesMPU = native
    assert counts['IRQ'] and counts['lagNMI']
    q = dict(passed=True, ROM_SHA256=sha(O / 'candidate.nes'), movement_equivalence_cases=cases,
             complete_header_rejections=rejects, actual_ISR_cuts=counts,
             manual_cache_fixture=True, native=False,
             scope='Real public callbacks; original source physics/native movement outputs retained. '
                   'Both full headers reject every one-byte corruption. Actual busy-IRQ/NMI returns '
                   'preserve registers, scratch, SMC, maps and source banks around changed renderer calls.',
             bindings={str(p.relative_to(R)): sha(p) for p in [Path(__file__), O / 'candidate.nes',
                 O / 'component.s', O / 'assembly.json']})
    (O / 'CPU.json').write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(q))


if __name__ == '__main__':
    main()
