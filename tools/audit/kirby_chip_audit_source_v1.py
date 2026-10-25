"""Authenticate and execute the relocated Rescue Rangers arithmetic kernels.

This is not a whole-player controller/physics comparison. Full input, terrain,
rendering, swimming and source audio still require native verification.
"""
from pathlib import Path
import argparse, gzip, hashlib, json, random, re
from check_tmnt_render_oa import load, Memory, address, location
from verify_native_relocation import NesMPU


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--source', type=Path, default=Path("C:/NES/Chip 'n Dale - Rescue Rangers (USA).nes"))
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    original = a.source.read_bytes()
    source_sha = hashlib.sha256(original).hexdigest()
    assert source_sha == '8d5e3d9ce20fa0a61b23e93dbc975606803f2d5e7a264514b02b96f832a63181'
    b = load(a.rom)
    dp = a.rom.with_suffix('.dbg')
    debug = dp.read_text() if dp.exists() else gzip.decompress(a.rom.with_suffix('.dbg.gz').read_bytes()).decode()
    owners, syms = [], []
    for line in debug.splitlines():
        if line.startswith(('scope\t','sym\t')):
            q = dict(t.split('=',1) for t in line.split('\t',1)[1].split(',') if '=' in t)
            (owners if line.startswith('scope\t') else syms).append(q)
    owner = next(q['id'] for q in owners if q.get('name') == '"CdNative"')
    linked = {int(q['name'].strip('"')[1:],16):int(q['val'],0) for q in syms
              if q.get('scope') == owner and re.fullmatch('"NF[0-9A-F]{3}"', q.get('name','')) and 'val' in q}
    assert len(linked) > 60, len(linked)
    native = [0]*65536
    native[0xc000:] = original[16+7*16384:16+8*16384]
    bank = (location(b,'CdMovement')-16)//8192
    port = Memory(b)
    port.page(1,bank)
    opcodes = NesMPU().disassemble
    ram_map, decoded = {}, []
    for oldpc,newpc in sorted(linked.items()):
        oldop,newop = native[oldpc],port[newpc]
        oldname,oldmode = opcodes[oldop]
        newname,newmode = opcodes[newop]
        assert oldname == newname and (oldmode == newmode or (oldmode,newmode) == ('zpg','abs')), (hex(oldpc),oldname,oldmode,newname,newmode)
        if oldmode == 'rel':
            s = lambda n:n if n < 128 else n-256
            target = oldpc+2+s(native[oldpc+1])
            assert newpc+2+s(port[newpc+1]) == linked[target]
        elif oldmode == 'imm':
            assert native[oldpc+1] == port[newpc+1]
        elif oldmode in ['abx','abs','zpg']:
            left = native[oldpc+1]+(256*native[oldpc+2] if oldmode != 'zpg' else 0)
            right = port[newpc+1]+256*port[newpc+2]
            assert left < 0x800 and 0x5c00 <= right < 0x5d00, (hex(oldpc),hex(left),hex(right))
            assert ram_map.setdefault(left,right) == right
        else:
            assert oldmode == 'imp', (hex(oldpc),oldmode)
        decoded.append(dict(source_pc=oldpc, linked_pc=newpc, mnemonic=oldname, source_mode=oldmode, linked_mode=newmode))
    rng = random.Random(20261025)
    counts, cycle_deltas = {}, {}
    for start in [0xf21e,0xf23c,0xf2a2,0xf2c5,0xf2fb,0xf31d]:
        deltas = set()
        for case in range(128):
            left = native.copy()
            right = Memory(b)
            right.page(1,bank)
            values = {at:(0 if case == 0 else 255 if case == 1 else rng.randrange(256)) for at in ram_map}
            for oldat,newat in ram_map.items():
                left[oldat] = right[newat] = values[oldat]
            results = []
            for memory,entry in [(left,start),(right,linked[start])]:
                c = NesMPU(memory=memory,pc=entry)
                c.a,c.x,c.y,c.p,c.sp = 0x57,0,0x93,(0x30 if case&1 else 0x71),0xfd
                c.stPushWord(0x5aff)
                for _ in range(100):
                    if c.pc == 0x5b00:
                        break
                    c.step()
                else:
                    raise AssertionError(('Kernel did not return',hex(start)))
                assert c.sp == 0xfd
                results.append((c.a,c.x,c.y,c.p,c.sp,c.processorCycles))
            assert results[0][:5] == results[1][:5]
            assert all(left[oldat] == right[newat] for oldat,newat in ram_map.items())
            deltas.add(results[1][5]-results[0][5])
        counts[hex(start)] = 128
        cycle_deltas[hex(start)] = sorted(deltas)
    proof = dict(passed=True,accepted=False,source_ROM_sha256=source_sha,
        ROM_sha256=hashlib.sha256(b['raw']).hexdigest(),driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        decoded_instructions=len(decoded),decoded=decoded,RAM_retargeting={hex(k):hex(v) for k,v in ram_map.items()},
        actual_CPU_cases=sum(counts.values()),cases_by_native_entry=counts,extra_cycles_by_native_entry=cycle_deltas,
        scope='Six actual original-ROM arithmetic kernels versus linked retargeted instructions. Exact A/X/Y/P/SP and retargeted RAM, including native F0-page wrap and zero/FF cases. Wrapper controls, full motion, terrain, graphics, interrupt timing, audio and campaign remain outside this proof.')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:v for k,v in proof.items() if k not in ['decoded','RAM_retargeting']},indent=2))


if __name__ == '__main__':
    main()
