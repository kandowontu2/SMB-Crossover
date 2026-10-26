"""Compare linked Rescue Rangers player to original per-call state/APU traces."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
from root_chip_native_layout_cpu_v1 import verify_layout
from collections import Counter
from check_tmnt_render_oa import load, address
from check_tmnt_audio_fallback_oc import qualified
from mike_native_music_cpu import MusicMemory
from verify_native_relocation import NesMPU

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--calls', type=int, default=512)
    a = ap.parse_args()
    assert not a.output.exists() and not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True)
    gold = D / 'root-chip-native-music-source-v1'
    original = json.loads((gold / 'proof.json').read_text())
    b = load(a.rom)
    base = ROOT / 'build/smb-crossover-mmc5-expanded.nes'
    assert sha(base) == '50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
    before, after = base.read_bytes(), a.rom.read_bytes()
    diff = {i: sum(x != y for x, y in zip(before[16+i*8192:16+(i+1)*8192], after[16+i*8192:16+(i+1)*8192])) for i in range(128)}
    diff = {k:v for k,v in diff.items() if v}
    assert set(diff) == {62,93,94}, diff
    layout=verify_layout(a.rom)
    assert before[:16] == after[:16] and before[1048592:] == after[1048592:]
    qb, qa = qualified(base), qualified(a.rom)
    moved = {str(k):[v,qa.get(k)] for k,v in qb.items() if qa.get(k) != v}
    assert len(moved)==len(layout['genuine_mac_label_moves']),moved
    assert before[16+62*8192:16+62*8192+0x2b7] == after[16+62*8192:16+62*8192+0x2b7]
    ram, zp = address(b,'ChNativeRam'), address(b,'ChNativeZp')
    read_pc = address(b,'ChNativeRead')
    source_read_entries = {address(b,f'ChNativeP{pc:04X}'):v-0xc0 for pc,op,mode,v in json.loads((a.rom.parent/'preparation.json').read_text())['intercepts'] if mode=='iny'}
    all_rows = []
    for song in original['tracks']:
        m = MusicMemory(b)
        m.page(1,62)
        m.page(2,94)
        c = NesMPU(memory=m)
        m[:256] = [(71+19*i)&255 for i in range(256)]
        foreground = bytes(m[:256])
        pointer = address(b,'ChNativePointer')
        mapped = address(b,'ChNativeMappedC5')
        private_zp = [address(b,n)+i for n in ['ChNativePointer','ChNativeMappedC5','ChNativeMappedC1'] for i in [0,1]] + list(range(zp,zp+25))
        owned = set(range(256,512)) | set(range(ram,ram+0xa4)) | set(private_zp) | {0x4015}
        for name in ['GuestNativeApu','GuestNativeDirty']:
            owned.update(range(address(b,name),address(b,name)+16))
        owned.update(address(b,name) for name in ['GuestNativeEnable','GuestCombinedEnable'])
        count, stores, minimum, costs, reads = 0,0,255,[],0
        read_counts = Counter()
        peak = None
        with gzip.open(gold/f'song-{song:02d}.jsonl.gz','rt') as stream:
            for tick, line in enumerate(stream):
                if tick > a.calls:
                    break
                want = json.loads(line)
                c.pc = address(b,'ChNativeSourceInit' if tick == 0 else 'ChNativeSourcePlay')
                c.a,c.x,c.y,c.p,c.sp = song-1 if tick == 0 else 0,0,0,0x24,253
                m[510],m[511] = 255,126
                m.events,m.lowwrites,m.writes = [],[],[]
                start = c.processorCycles
                frame_reads = Counter()
                original_before = dict(zp=list(m[zp:zp+25]), ram=list(m[ram:ram+128]))
                for _ in range(200000):
                    if c.pc == 0x7f00:
                        break
                    if c.pc in source_read_entries:
                        slot = source_read_entries[c.pc]
                        at = (m[zp+slot] + 256*m[zp+slot+1] + c.y)&65535
                        assert 0x8100 <= at < 0xafb0, ('Indirect data outside preserved data',song,tick,hex(at))
                        if slot in [1,5]:
                            pointer_cache=address(b,'ChNativeMappedC1' if slot==1 else 'ChNativeMappedC5')
                            mapped_at=m[pointer_cache]+256*m[pointer_cache+1]+c.y
                            assert mapped_at==at+0x2200,('Cached pointer divergence',song,tick,hex(c.pc),slot,hex(at),hex(mapped_at))
                        reads += 1
                        frame_reads[f'{slot:02x}:Y{c.y}'] += 1
                        read_counts[f'{slot:02x}:Y{c.y}'] += 1
                    assert m[c.pc] != 0, 'Unexpected source BRK'
                    minimum = min(minimum,c.sp)
                    m.pc = c.pc
                    c.step()
                else:
                    raise AssertionError(('Source timeout',song,tick,hex(c.pc)))
                m.pc = None
                assert c.sp == 255
                actual = [[at,m[zp+at-0xc0] if at < 256 else m[ram+at-0x700]] for at,_ in want['RAM']]
                assert actual == want['RAM'], ('Original state divergence',song,tick,[(x,y)for x,y in zip(actual,want['RAM'])if x!=y][:12])
                assert list(map(list,m.events)) == want['writes'], ('Ordered source APU divergence',song,tick,m.events,want['writes'])
                expect = want['final']
                assert (c.a,c.x,c.y,c.p&0xcf,c.sp) == (expect['a'],expect['x'],expect['y'],expect['p']&0xcf,expect['sp']), ('Actual CPU flags/register divergence',song,tick,(c.a,c.x,c.y,c.p,c.sp),expect)
                assert all(at in owned for pc,at,v in m.lowwrites), ('Unowned write',song,tick,next(x for x in m.lowwrites if x[1]not in owned))
                assert all(m[i] == foreground[i] for i in range(256) if i not in private_zp), ('Gameplay ZP changed',song,tick)
                costs.append(c.processorCycles-start)
                if tick and (peak is None or costs[-1] > peak['linked_cycles']):
                    peak = dict(tick=tick, linked_cycles=costs[-1], original_cycles=want['cycles'],
                                indirect_read_counts=dict(frame_reads), original_before=original_before)
                count += 1
                stores += len(m.events)
        row = dict(song=song,calls=count,ordered_original_APU_stores=stores,
                   original_numeric_state_exact=True,actual_CPU_flags_registers_exact=True,
                   indirect_reads_checked=reads,minimum_SP=minimum,init_cycles=costs[0],
                   mean_play_cycles=sum(costs[1:])/len(costs[1:]),peak_play_cycles=max(costs[1:]),
                   read_counts=dict(read_counts), peak=peak)
        all_rows.append(row)
        print(json.dumps({k:v for k,v in row.items() if k not in ['read_counts','peak']}),flush=True)
        (a.output/'progress.json').write_text(json.dumps(all_rows,indent=2)+'\n')
    result = dict(passed=True,accepted=False,native_run=False,gameplay_dispatch_added=False,
                  candidate_ROM_sha256=sha(a.rom),source_sha256=original['source_sha256'],
                  changed_PRG_bytes=diff,old_scoped_symbols_unchanged_except_genuine_Mac_records=len(qb)-len(moved),layout=layout,CHR_exact=True,
                  source_data_numeric_pointers_unchanged=True,tracks=all_rows,
                  flag_contract='All physical6502 flags compared; virtual B/unused stack-status bits excluded. All raw APU bytes/order retained.',
                  limitations='Original per-call music component only; DIRECT C0..D8 are owned source scratch in this component, not restored foreground bytes. A gameplay adapter must explicitly borrow/restore all25 before any native grant. No full outer/interrupt/native cadence qualification.',
                  checker_sha256=sha(__file__))
    (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,calls=sum(r['calls'] for r in all_rows),stores=sum(r['ordered_original_APU_stores'] for r in all_rows))))


if __name__ == '__main__':
    main()
