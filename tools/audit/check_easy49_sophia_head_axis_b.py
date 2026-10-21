"""Run the compiled normal-flat corner selector against independent Q16 math."""
from pathlib import Path
import hashlib
import importlib.util
import json
import random
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
D = V / 'root49-sophia-head-axis-b'
G = V / 'ryu49-head-status-bridge-g'
sys.path.insert(0, str(G))
spec = importlib.util.spec_from_file_location('head_axis_bus', G / 'check.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
CPU = g.loadcpu().NesMPU
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
Q = 65536


def main():
    out = D / 'compiled-axis-b.json'
    assert not out.exists()
    report = dict(status='RUNNING', script_sha256=sha(__file__), maps=[],
                  scope='Actual compiled selector, rational Q16 independent oracle; not full native caller/interrupt or Flash deferred scheduling.')
    try:
        for mapper in ('mmc3', 'mmc5'):
            im = g.Image(D / f'source/build/smb-crossover-{mapper}.nes')
            old = g.Image(V / f'root49-combined-working-c/source/build/smb-crossover-{mapper}.nes')
            L = im.ram
            assert im.ram == old.ram
            oldsegs = {z['name']: z for z in old.segs.values()}
            for z in im.segs.values():
                if z['name'] in oldsegs:
                    a = oldsegs[z['name']]
                    assert z['start'] == a['start'], z['name']
                    if z['name'] != 'SOPHIA_TERRAIN_COLD':
                        assert z['size'] == a['size'], z['name']
            h = im.hook('SophiaHeadSourceAxis')
            count = 0
            digest = hashlib.sha256()
            cycles = []
            branches = {}

            def execute(prior_x, current_x, current_top, cell_left, cell_bottom, vx, vy, p):
                nonlocal count
                prior_right, prior_left = prior_x + 17 * Q + Q // 2, prior_x - Q - Q // 2
                corner = 'right' if prior_right <= cell_left * Q else 'left' if prior_left >= (cell_left + 16) * Q else 'direct'
                vpen = cell_bottom * Q - current_top
                hpen = current_x + 17 * Q + Q // 2 - cell_left * Q if corner == 'right' else (cell_left + 16) * Q - (current_x - Q - Q // 2)
                expected = corner == 'direct' or bool(vx and (not vy or vpen <= hpen))
                ram = bytearray(10240)
                def put(n, value):
                    n, _, off = n.partition('+')
                    ram[g.at(L[n] + int(off or 0))] = value & 255
                def fixed(n, value, length):
                    for j in range(length):
                        put(f'{n}+{j}', value >> (8*j))
                fixed('MmVX', vx, 3)
                fixed('MmVY', vy, 3)
                px, xf = divmod(current_x, Q)
                py, yf = divmod(current_top - 16 * Q - Q // 2, Q)
                ox, of = divmod(prior_x, Q)
                for n, value in dict(Player_X_Position=px, Player_PageLoc=px>>8, Player_Y_Position=py,
                                     RyWallOldX=ox, RyWallOldPage=ox>>8, RyWallOldXFine=of&255, RyWallOldXFrac=of>>8,
                                     RgTempX=cell_left, RgTempPage=cell_left>>8, RgTemp2=cell_bottom,
                                     R2=0x50, R3=0x54, R4=7, R6=0x13, R7=3, SmTemp=30).items():
                    put(n, value)
                fixed('MmXFraction', xf, 2)
                fixed('MmYFraction', yf, 2)
                sp = 0xE9
                ram[0x101+sp] = (g.RET-1)&255
                ram[0x102+sp] = (g.RET-1)>>8
                got = g.execute(im, CPU, ram, [73, 13, 30, p, sp], {0x8000:62, 0xA000:h['physical_bank'], 0xC000:36, 0xE000:63}, h['address'], g.RET, native_status=True)
                assert bool(got['regs'][3]&1) == expected, (mapper, corner, prior_x, current_x, current_top, cell_left, vx, vy, vpen, hpen, got['regs'])
                assert got['regs'][4:] == [sp+2, g.RET]
                for n in ['R2','R3','R4','R6','R7','SmTemp','RgTempX','RgTempPage','RgTemp2']:
                    assert got['ram'][g.at(L[n])] == ram[g.at(L[n])], n
                assert got['ram'][0x101+sp:0x200] == ram[0x101+sp:0x200]
                count += 1
                branches[corner] = branches.get(corner, 0) + 1
                cycles.append(got['cycles'])
                digest.update(bytes([expected, got['regs'][3]&1]))
                digest.update(got['ram'])

            # Equality and one-Q16-unit neighbors on both mirror corners and
            # across native page boundaries; includes zero/full fractional vx.
            for cell in [256, 496, 512, 608, 752, 768, 1024]:
                for side in ['left','right','direct']:
                    boundary = (cell-17)*Q-Q//2 if side=='right' else (cell+17)*Q+Q//2 if side=='left' else cell*Q
                    for prior_delta in [-Q, -1, 0, 1, Q]:
                        for penetration in [0, 1, 0x7fff, 0x8000, 0x8001, Q, 3*Q]:
                            current_x = (cell-17)*Q-Q//2+penetration if side!='left' else (cell+17)*Q+Q//2-penetration
                            for delta in [-1, 0, 1]:
                                vpen = max(0, penetration+delta)
                                for vx, vy in [(0,-Q),(1,-Q),(-1,-Q),(Q,0)]:
                                    execute(boundary+prior_delta, current_x, 192*Q-vpen, cell, 192, vx, vy, 0x81)
            rng = random.Random(0x49C0)
            for i in range(4000):
                cell = rng.choice([256,496,512,608,752,768,1024])
                side = i&1
                hp, vp = rng.randrange(5*Q), rng.randrange(5*Q)
                if side:
                    ox = (cell-17)*Q-Q//2-rng.randrange(3*Q)
                    cx = (cell-17)*Q-Q//2+hp
                else:
                    ox = (cell+17)*Q+Q//2+rng.randrange(3*Q)
                    cx = (cell+17)*Q+Q//2-hp
                execute(ox, cx, 192*Q-vp, cell, 192, rng.choice([0,1,-1,Q,-Q]), rng.choice([0,-1,-Q,-3*Q]), rng.randrange(256)&0xCF)
            delta = [i for i,(a,b) in enumerate(zip(old.raw,im.raw)) if a!=b]
            jsr = old.hook('Separate','SophiaSourceHeadProbe')['rom_offset']
            append = h['rom_offset']
            assert all(jsr <= i < jsr+3 or append <= i < append+im.sym('SophiaHeadSourceAxis')['size'] for i in delta)
            assert old.raw[:16] == im.raw[:16] and old.raw[16+512*1024:] == im.raw[16+512*1024:]
            report['maps'].append(dict(mapper=mapper, cases=count, branches=branches, digest=digest.hexdigest(),
                                       cycle_range=[min(cycles),max(cycles)], ROM=im.metadata(),
                                       changed_ROM_bytes=len(delta), new_helper_size=im.sym('SophiaHeadSourceAxis')['size'],
                                       all_old_RAM_and_segment_starts_literal=True))
        report['status'] = 'PASS_COMPILED_SOURCE_NORMAL_FLAT_CORNER_AXES_BOTH_MAPPERS'
    except Exception as e:
        report.update(status='FAIL_RETAINED', error=str(e))
        raise
    finally:
        out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status=report['status'], cases=sum(z['cases'] for z in report['maps']))))


if __name__ == '__main__':
    main()
