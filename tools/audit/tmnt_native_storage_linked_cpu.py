"""Actual linked TMNT writers/state/ABI against complete original source calls."""
from pathlib import Path
import argparse
import gzip
import json
from check_tmnt_render_oa import load, Memory, address
from verify_native_relocation import NesMPU
from tmnt_native_storage_driver import OB, ROOT, ORIGINAL, sha
from tmnt_native_storage_cpu import Probe


class Linked:
    def __init__(self, rom, swap):
        self.b = load(rom)
        self.m = Memory(self.b)
        self.c = NesMPU(memory=self.m)
        self.swap = swap
        self.m.page(1, 63)
        self.m.page(2, 99 if swap else 124)
        self.m[address(self.b, 'CurrentBank')] = 191
        self.m[address(self.b, 'CurrentBankC')] = 227 if swap else 252
        self.m[address(self.b, 'SelectedCharacter')] = 19
        self.m[address(self.b, 'OperMode')] = 1
        self.zp, self.ram = address(self.b, 'TnAudioZp'), address(self.b, 'TnAudioRam')
        self.saved_zp = bytes(self.m[:256])
        prep = json.loads(rom.parent.joinpath('preparation.json').read_text())
        normal = lambda at: at + 8192 if at < 49152 else at - 8192
        self.sites = {normal(row['pc']): row for row in prep['standalone_source']['APU_stores']}
        self.allowed = set(range(0x1d0, 512)) | set(range(self.zp, self.zp + 14)) | set(range(self.ram, self.ram + 216))
        for name in ['GuestNativeApu', 'GuestNativeDirty']:
            self.allowed.update(range(address(self.b, name), address(self.b, name) + 16))
        self.allowed.update(address(self.b, name) for name in ['GuestNativeEnable', 'GuestCombinedEnable', 'BassDmcActive', 'TnDmcDrain'])
        self.writers = self.depth = 0
        self.HW = []

    def call(self, row, song):
        c, m = self.c, self.m
        c.sp = 253
        m[510], m[511] = 255, 1
        if row['call'] == -1:
            c.a, c.x, c.y, c.pc = song - 1, 0, 0, address(self.b, 'TnNativeInit')
        else:
            c.pc = address(self.b, 'TnNativePlay')
        m.writes = []
        start, source, pending = c.processorCycles, [], []
        minimum = 255
        for _ in range(50000):
            if c.pc == 512: break
            minimum = min(minimum, c.sp)
            if pending and c.pc == pending[-1][0]:
                ret, before = pending.pop()
                after = c.a, c.x, c.y, c.p & 207, c.sp
                assert after == before, ('Source STA writer ABI', song, row['call'], hex(ret), before, after)
                self.writers += 1
            if c.pc in self.sites and m.banks[(c.pc - 0x8000) // 8192] == 63:
                site = self.sites[c.pc]
                index = c.x if site['mode'] == 'abx' else c.y if site['mode'] == 'aby' else 0
                source.append([site['address'] + index, c.a])
                pending.append((c.pc + 3, (c.a, c.x, c.y, c.p & 207, c.sp)))
            c.step()
        else:
            raise AssertionError(('Linked source timeout', song, row['call'], hex(c.pc), m.banks))
        assert not pending and c.sp == 255
        assert source == row['writes'], ('Linked original ordered requests', song, row['call'], source, row['writes'])
        assert all(at in self.allowed for at, value in m.writes if at < 0x8000 and not 0x4000 <= at <= 0x4017), ('Unowned foreground write', song, row['call'], [(hex(at), v) for at, v in m.writes if at < 0x8000 and at not in self.allowed and not 0x4000 <= at <= 0x4017][:5])
        assert all(m[i] == self.saved_zp[i] for i in range(256) if not self.zp <= i < self.zp + 14)
        assert not [(at, value) for at, value in m.writes if 0x2000 <= at < 0x4000 or 0x5000 <= at < 0x6000], ('Unexpected PPU/CHR/mapper write', song, row['call'])
        assert m.banks == [126, 63, 99 if self.swap else 124, 127]
        self.depth = min(self.depth or 255, minimum)
        self.HW.extend((at, value) for at, value in m.writes if 0x4000 <= at <= 0x4017)
        return c.processorCycles - start

    def state(self):
        return bytes(self.m[self.zp:self.zp + 14] + self.m[self.ram:self.ram + 174])

    def registers(self):
        return self.c.a, self.c.x, self.c.y, self.c.p & 207, self.c.sp


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['raw-original', 'duration', 'swap', 'output']:
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--plays', type=int, default=12000)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT) and 1 <= a.plays <= 12000
    a.output.mkdir(parents=True, exist_ok=False)
    coverage = json.loads((OB / 'probe-v2/coverage.json').read_text())
    rows, count, stores, writers = [], 0, 0, 0
    for song, record in coverage['songs'].items():
        capture = OB / f'probe-v2/song-{int(song):02d}.json.gz'
        assert sha(capture) == record['capture_sha256']
        gold = json.loads(gzip.decompress(capture.read_bytes()))[:a.plays + 1]
        original, duration, swap = Probe(a.raw_original, True), Linked(a.duration, False), Linked(a.swap, True)
        costs = [[], [], []]
        for want in gold:
            for i, runner in enumerate([original, duration, swap]):
                costs[i].append(runner.call(want, int(song)))
            assert original.registers() == duration.registers() == swap.registers(), ('Linked literal public ABI', song, want['call'], original.registers(), duration.registers(), swap.registers())
            assert original.state() == duration.state(), ('Linked duration exact source RAM', song, want['call'])
            addresses = list(range(0xe0, 0xee)) + list(range(0x7000, 0x70ae))
            expected = [(original.m[at] - (27 if original.origin.get(at) in original.changed_high else 0)) & 255 for at in addresses]
            assert bytes(expected) == swap.state(), ('Linked storage exact pointer-provenance source RAM', song, want['call'], [(hex(at), expected[i], swap.state()[i], original.origin.get(at)) for i, at in enumerate(addresses) if expected[i] != swap.state()[i]][:8])
            assert costs[1][-1] == costs[2][-1], ('Storage changed linked cycles', song, want['call'], costs[1][-1], costs[2][-1])
            count += 1
            stores += len(want['writes'])
        writers += duration.writers + swap.writers
        row = dict(song=int(song), calls=len(gold), ordered_source_requests=sum(len(v['writes']) for v in gold),
                   raw_original_cycles=sum(costs[0]), duration_linked_cycles=sum(costs[1]), swapped_linked_cycles=sum(costs[2]),
                   duration_mean_play_cycles=sum(costs[1][1:]) / a.plays, duration_peak_play_cycles=max(costs[1][1:]),
                   original_peak_play_cycles=max(costs[0][1:]), maximum_stack_depth=255 - min(duration.depth, swap.depth))
        rows.append(row)
        print('LINKED', row, flush=True)
        (a.output / 'progress.json').write_text(json.dumps(rows, indent=2) + '\n')
    result = dict(passed=True, native_run=False, production_changes=False, original_NSF_sha256=ORIGINAL,
                  duration_ROM_sha256=sha(a.duration), swapped_ROM_sha256=sha(a.swap),
                  original_calls=count, ordered_original_source_APU_requests=stores,
                  literal_public_AXYP_SP_exact=True, every_writer_AXYP_SP_exact=True,
                  checked_writer_returns=writers, source_RAM_and_ZP_provenance_exact=True,
                  foreground_RAM_ZP_PPU_CHR_SMC_banks_owned=True, storage_cycles_exactly_duration=True,
                  songs=rows, tool_sha256=sha(Path(__file__)),
                  limits='Actual linked native drivers and writers, with seeded isolated music state. No adapter/whole outer call or real IRQ/NMI/DMA/sample clock/cadence qualification.')
    (a.output / 'proof.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['passed', 'original_calls', 'ordered_original_source_APU_requests', 'checked_writer_returns']}))


if __name__ == '__main__':
    main()
