"""Execute compiled Sophia geometry against exact rational source endpoints."""
from pathlib import Path
from fractions import Fraction
import collections
import hashlib
import importlib.util
import json
import sys

R = Path(__file__).resolve().parents[2]
D = R / 'build/verification/root49-sophia-source-body-hl'
G = R / 'build/verification/ryu49-head-status-bridge-g'
sys.path.insert(0, str(G))
spec = importlib.util.spec_from_file_location('sophia_compiled_bus', G / 'check.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
CPU = g.loadcpu().NesMPU
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = D / 'compiled-geometry-ho.json'
    assert not out.exists()
    base = R / 'build/roster-through-2-2/root49hi-sophia-body-11-v0-mmc3/actual-firebar-body.bin'
    assert sha(base) == 'feafef2b5de720a41dbd4147142198e87a9a029f71af8c09a25cd49853033973'
    captured = g.Image(D / 'source/build/smb-crossover-mmc3.nes')
    report = dict(status='RUNNING', snapshot_sha256=sha(base), script_sha256=sha(__file__), maps=[],
        retained_fixture_correction='HN copied mapper3 SRAM bytes into mapper5 SelectedCharacter at a different address, making that gate fixture Mario. Explicit named source values are copied below. These are component seeds, never a mapper5 ordinary snapshot or route.',
        scope='Direct compiled leaf ABI and exact source integer projection from actual captured Sophia RAM. Explicitly seeded component controls, no ordinary route or native emulator proof inferred.')
    try:
        for mapper in ['mmc3', 'mmc5']:
            im = g.Image(D / 'source/build' / f'smb-crossover-{mapper}.nes')
            L = im.ram
            initial = bytearray(base.read_bytes())
            for name, length in [('SelectedCharacter',1),('MmDeathFlag',1),('MmXFraction',2),('MmYFraction',2)]:
                for i in range(length):
                    initial[g.at(L[name]+i)] = base.read_bytes()[g.at(captured.ram[name]+i)]
            for seg in im.segs.values():
                if seg['name'] == 'SMCCODE':
                    initial[seg['start']:seg['start']+seg['size']] = im.raw[seg['ooffs']:seg['ooffs']+seg['size']]
            def put(ram, n, v):
                label, _, offset = n.partition('+')
                ram[g.at(L[label] + int(offset or 0))] = v & 255
            def run(name, changes, entry, flags=0x81, stack=0xe9):
                ram = bytearray(initial)
                for n, v in dict(CurrentBank=58 | (128 if im.mapper == 5 else 0), **changes).items():
                    put(ram, n, v)
                if im.mapper == 4:
                    put(ram, 'BankShadow', 0x47)
                ram[0x101+stack] = (g.RET-1)&255
                ram[0x102+stack] = (g.RET-1)>>8
                registers = [0x6b, 0xa3, 0x57, flags, stack]
                banks = {0x8000:62, 0xa000:58, 0xc000:36, 0xe000:63}
                got = g.execute(im, CPU, ram, registers, banks, im.hook(entry)['address'], g.RET, native_status=True)
                # The synthetic caller return is consumed by the actual RTS.
                assert got['regs'][1:3] == registers[1:3] and got['regs'][4:] == [stack+2, g.RET], (name,got['regs'])
                if entry == 'SophiaSourceBodyBox':
                    assert got['regs'][:4] == registers[:4], (name, got['regs'], registers)
                written = {t[3]: t[4] for t in got['trace']}
                box = {L['BoundingBox_UL_Corner']+i for i in range(4)} if entry == 'SophiaSourceBodyBox' else set()
                expected = bytearray(ram)
                for address, value in written.items():
                    assert address in box or 0x100 <= address <= 0x100+stack, ('Only box or individual callee push', name, address)
                    expected[g.at(address)] = value
                assert bytes(expected) == got['ram'], ('Every10240RAMbyte', name)
                assert got['ram'][0x101+stack:0x200] == bytes(ram[0x101+stack:0x200]), ('Live caller stack', name)
                return ram, got
            forms = []
            fractions = [0,1,255,256,32767,32768,32769,65280,65534,65535]
            costs = collections.Counter()
            count = 0
            for mode in [0, 1]:
                for state in [0,1,2]:
                    for f in fractions:
                        # A permutation independently covers both half-pixel boundaries.
                        for yf in [f, fractions[(fractions.index(f)+3)%len(fractions)]]:
                            changes = {'SelectedCharacter':11, 'CrossoverBehaviorVersion':mode, 'Player_State':state,
                                'MmXFraction':f&255, 'MmXFraction+1':f>>8, 'MmYFraction':yf&255, 'MmYFraction+1':yf>>8}
                            before, got = run('flat-'+str(count), changes, 'SophiaSourceBodyBox')
                            x = before[g.at(L['Player_X_Position'])]-before[g.at(L['ScreenLeft_X_Pos'])]
                            x %= 256
                            y = before[g.at(L['Player_Y_Position'])]
                            left = Fraction(x*65536+f,65536)-Fraction(3,2)
                            right = Fraction(x*65536+f,65536)+Fraction(35,2)
                            top = Fraction(y*65536+yf,65536)+Fraction(33,2)
                            bottom = Fraction(y*65536+yf,65536)+32
                            ceil = lambda v: -((-v.numerator)//v.denominator)
                            wanted = [ceil(left),ceil(top),right.numerator//right.denominator,bottom.numerator//bottom.denominator]
                            actual = [got['ram'][g.at(L['BoundingBox_UL_Corner']+i)] for i in range(4)]
                            assert wanted == actual, ('Rational source endpoints', mode, state, f, yf, wanted, actual)
                            costs[got['cycles']] += 1
                            if count < 4 or f in [32768,32769]:
                                forms.append(dict(mode=mode, state=state, xf=f, yf=yf, source_projection=actual))
                            count += 1
            unsupported = [ {'SelectedCharacter':n} for n in range(14) if n!=11 ] + [
                {'OperMode':0}, {'OperMode':2}, {'GameEngineSubroutine':7}, {'GameEngineSubroutine':4},
                {'Player_State':3}, {'Player_State':255}, {'XgWall':1}, {'XgWall':2}, {'XgCeiling':1},
                {'MmDeathFlag':1}, {'Player_Y_HighPos':0}, {'Player_Y_HighPos':2}, {'Player_Y_Position':224},
                {'Player_PageLoc':0}, {'Player_PageLoc':4}, {'Player_X_Position':0},
                {'Player_X_Position':255, 'ScreenLeft_X_Pos':0, 'ScreenLeft_PageLoc':2}]
            fallback_count = 0
            for idx, changes in enumerate(unsupported):
                for flags in [0,1,2,0x45,0x8b,0xcf]:
                    before, got = run('fallback-'+str(idx), changes, 'SophiaSourceBodyBox', flags, 0x89)
                    bb = L['BoundingBox_UL_Corner']
                    assert got['ram'][g.at(bb):g.at(bb)+4] == bytes(before[g.at(bb):g.at(bb)+4]), changes
                    fallback_count += 1
            gates = []
            for yf in fractions:
                # All actual vertical integral native containers around the source body.
                for piece_y in range(96,158):
                    changes = {'MmYFraction':yf&255, 'MmYFraction+1':yf>>8, 'R7':piece_y}
                    before, projected = run('project-gate', changes, 'SophiaSourceBodyBox')
                    # Feed exact compiled published bbox into the actual consumer leaf.
                    for i in range(4):changes['BoundingBox_UL_Corner+'+str(i)] = projected['ram'][g.at(L['BoundingBox_UL_Corner']+i)]
                    before, got = run('gate-'+str(yf)+'-'+str(piece_y), changes, 'SophiaSourceFirebarDisjoint')
                    top = 112 + Fraction(33,2) + Fraction(yf,65536)
                    bottom = 144 + Fraction(yf,65536)
                    rejected = piece_y+13 < top or piece_y-3 > bottom
                    assert bool(got['regs'][3]&1) == rejected, ('Actual consumer rational edge', yf, piece_y, rejected, got['regs'])
                    gates.append(dict(yf=yf,pieceY=piece_y,rejected=rejected))
            report['maps'].append(dict(mapper=mapper, ROM=im.metadata(), projected_cases=count,
                unsupported_complete_ABI=fallback_count, firebar_rational_edges=len(gates), representative_boxes=forms,
                direct_body_cycles=dict(costs), rejected_firebar_cases=sum(x['rejected']for x in gates),
                all10240_RAM_and_individual_pushes=True, every_live_caller_stack_byte=True))
            out.write_text(json.dumps(report,indent=2)+'\n')
        report['status'] = 'PASS_COMPILED_RATIONAL_BODY_AND_FIREBAR_EDGES'
    except Exception as exc:
        report.update(status='FAIL_RETAINED', error=str(exc))
        raise
    finally:
        out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'], maps=[{k:v for k,v in row.items()if k in ['mapper','projected_cases','unsupported_complete_ABI','firebar_rational_edges']}for row in report['maps']])))


if __name__ == '__main__':
    main()
