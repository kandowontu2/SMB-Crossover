"""Run the genuine actor-move JSR continuously through its real consumer.

No return-register exclusions: compare full final AXYP/SP after the immediate
JMP OffscreenBoundsCheck has completed. Retain/disclose intermediate dead A/P
differences. Bounded assembled CPU component only, not whole-RAM/NMI/native QA.
"""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from py65.disassembler import Disassembler
from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load
from check_tmnt_render_oa import address, location
from verify_native_relocation import NesMPU

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_OLD = '62dd860e9dd6d5414cd6251c5bd0557c5c14b6872aacf81d5e628eb4bab8caff'
EXPECTED_NEW = '7b42160095b0c817c13a3991773c240b3c93e15eaae9833aa7d3e8f4ef0a3d37'
FIELDS = ['Enemy_Flag', 'Enemy_ID', 'Enemy_State', 'Enemy_X_Position', 'Enemy_PageLoc',
          'Enemy_Y_Position', 'Enemy_Y_HighPos', 'Enemy_X_Speed', 'Enemy_Y_Speed',
          'Enemy_MovingDir', 'Enemy_Y_MoveForce', 'Enemy_YMoveForceFractional',
          'EnemyIntervalTimer', 'RgEnemyStun', 'RcEnemyStun', 'RcEnemyType', 'RcEnemyStamp']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def setup(bundle, char, slot, kind, stun, edge=0):
    q = Arena(bundle, char)
    q.put(ObjectOffset=slot, TimerControl=0, AreaType=1, FrameCounter=32,
          ScreenLeft_PageLoc=1, ScreenLeft_X_Pos=0,
          ScreenRight_PageLoc=1, ScreenRight_X_Pos=255)
    for name, value in [('Enemy_Flag', 1), ('Enemy_ID', kind), ('Enemy_State', 0),
        ('Enemy_X_Position', [96, 0, 255][edge]), ('Enemy_PageLoc', [1, 0, 2][edge]),
        ('Enemy_Y_Position', 160), ('Enemy_Y_HighPos', 1), ('Enemy_X_Speed', 0xf8),
        ('Enemy_Y_Speed', 0), ('Enemy_MovingDir', 2), ('RgEnemyStun', stun)]:
        q.set(name, value, slot)
    return q


def contract(bundle):
    """Disassemble the actual caller span, bind sole JSR and literal next JMP."""
    q = Arena(bundle, 0)
    symbol = bundle['syms']['RunNormalEnemies']
    seg = bundle['segs'][symbol['seg']]
    bank = (int(seg['ooffs'], 0)-16)//8192
    start, end = address(bundle, 'RunNormalEnemies'), address(bundle, 'EnemyMovementSubs')
    q.m.page((start-0x8000)//8192, bank)
    dis = Disassembler(NesMPU(memory=q.m))
    pc = start
    instructions = []
    while pc < end:
        length, text = dis.instruction_at(pc)
        instructions.append((pc, bytes(q.m[pc:pc+length]), text))
        pc += length
    assert pc == end
    target = address(bundle, 'EnemyMovementSubs')
    needle = bytes([0x20, target & 255, target >> 8])
    hits = [pc for pc, raw, _ in instructions if raw == needle]
    assert len(hits) == 1, hits
    call = hits[0]
    consumer = address(bundle, 'OffscreenBoundsCheck')
    code = bytes(q.m[call-5:call+6])
    timer = address(bundle, 'TimerControl')
    assert code == bytes([0xac, timer & 255, timer >> 8, 0xd0, 3,
                          0x20, target & 255, target >> 8,
                          0x4c, consumer & 255, consumer >> 8]), code.hex()
    assert bytes(q.m[consumer:consumer+4]) == bytes([
        0xb5, address(bundle, 'Enemy_ID'), 0xc9, 0x14])
    # Count the exact JSR bytes across PRG too; the source and instruction
    # stream distinguish this genuine callsite from accidental data patterns.
    raw_hits = []
    raw = bundle['raw'][16:16+128*8192]
    at = raw.find(needle)
    while at >= 0:
        raw_hits.append(dict(bank=at//8192, offset=at % 8192))
        at = raw.find(needle, at+1)
    assert [h for h in raw_hits if h['bank'] == bank] == [
        dict(bank=bank, offset=(call-0x8000) % 8192)], raw_hits
    aliases = []
    for hit in raw_hits:
        if hit['bank'] == bank:
            continue
        offset = 16+hit['bank']*8192+hit['offset']
        owners = [g for g in bundle['segs'].values() if 'ooffs' in g and
                  int(g['ooffs'],0) <= offset < int(g['ooffs'],0)+int(g['size'],0)]
        assert len(owners) == 1
        owner = owners[0]
        pc_alias = int(owner['start'],0)+offset-int(owner['ooffs'],0)
        assert owner['name'] == '"MAC_NATIVE_AUDIO"' and hit == dict(bank=123,offset=11)
        assert 0xa000 <= pc_alias < 0xc000 and 0xa000 <= target < 0xc000
        # A literal JSR changes no PRG mapping. This is a real Mac-driver call
        # to its own physical123:A4BA, never OBJECT physical0:A4BA.
        aliases.append(dict(**hit,PC=pc_alias,segment=owner['name'],
                            same_window_target_bank=hit['bank'],EnemyMovementSubs_owner=False))
    return dict(bank=bank, start=call-5, JSR=call, after_JSR=call+3,
                consumer=consumer, bytes=code.hex(), all_PRG_numeric_JSR_hits=raw_hits,
                unrelated_same_numeric_address_calls=aliases)


def state(q, c):
    return dict(cpu=[c.a, c.x, c.y, c.p, c.sp],
                actors={name: [q.get(name, i) for i in range(6)] for name in FIELDS},
                ObjectOffset=q.get('ObjectOffset'),
                bank_state=[q.m.banks, q.get('CurrentBank'), q.get('CurrentBankC')])


def run(q, bound, slot, flags=0x30):
    q.m.page((bound['start']-0x8000)//8192, bound['bank'])
    q.set('CurrentBank', bound['bank'] | 128)
    q.m.writes = []
    c = NesMPU(memory=q.m, pc=bound['start'])
    c.a, c.x, c.y, c.p, c.sp = 0x69, slot, 7, flags, 0xfd
    c.stPushWord(0x5aff)
    observed = {}
    counts = dict(movement=0, consumer=0, city=0)
    city_pc = address(q.b, 'RcEnemyControl')
    move_pc = address(q.b, 'EnemyMovementSubs')
    for _ in range(100000):
        if c.pc == 0x5b00:
            assert c.sp == 0xfd and counts['consumer'] == 1
            return state(q, c), c.processorCycles, observed, counts
        current_bank = q.m.banks[(c.pc-0x8000)//8192] if c.pc >= 0x8000 else -1
        if c.pc == move_pc and current_bank == bound['bank']:
            counts['movement'] += 1
        if c.pc == bound['consumer'] and current_bank == bound['bank']:
            counts['consumer'] += 1
        if c.pc == city_pc:
            sym = q.b['syms']['RcEnemyControl']
            seg = q.b['segs'][sym['seg']]
            if current_bank == (int(seg['ooffs'], 0)-16)//8192:
                counts['city'] += 1
        if current_bank == bound['bank'] and c.pc in (
                bound['after_JSR'], bound['consumer']+2, bound['consumer']+4):
            observed[c.pc-bound['consumer']] = [c.a, c.x, c.y, c.p, c.sp]
        c.step()
    raise AssertionError(('actual caller timeout', hex(c.pc), q.m.banks))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), 'Preserve the previous receipt'
    assert sha(args.baseline) == EXPECTED_OLD and sha(args.rom) == EXPECTED_NEW
    inputs = [args.baseline, args.rom, Path(__file__),
              ROOT/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',
              ROOT/'tools/audit/check_tmnt_render_oa.py',
              ROOT/'tools/audit/verify_native_relocation.py']
    inputs += [p.with_suffix(ext) for p in (args.baseline, args.rom) for ext in ('.dbg', '.lbl')]
    negatives = [ROOT/f'build/roster-expansion-river-enemy-gate-controls-v{i}.json' for i in (1, 2)]
    inputs += negatives
    before = {str(p): sha(p) for p in inputs}
    proof = dict(passed=False, source_only=True, native_run=False, scope=__doc__, bindings=before,
                 retained_negatives={str(p): json.loads(p.read_text())['passed'] for p in negatives})
    try:
        old, new = scoped_load(args.baseline), scoped_load(args.rom)
        contracts = [contract(b) for b in (old, new)]
        assert contracts[0]['start'] == contracts[1]['start']
        source = (ROOT/'src/object.s').read_text()
        assert source.count('jsr EnemyMovementSubs') == 1
        proof['actual_caller_contracts'] = contracts
        rows, intermediate = [], []
        specs = list(itertools.product([*range(21), 22, 23], range(6), [0,6,8,9,19], [0,3], [0]))
        # All21 dispatch entries at real return/consumer; both erase edges.
        specs += list(itertools.product([0,1,20,22,23], range(6), range(21), [0], [1,2]))
        # Earlier v1/v2 failing cells under all64 meaningful input flags.
        detailed = [(0,0,kind,stun,0,flags|0x30) for kind,stun in [(9,0),(19,0),(8,3)]
                    for flags in range(256) if flags & 0x30 == 0]
        detailed += [(*spec,0x30) for spec in specs]
        for char,slot,kind,stun,edge,flags in detailed:
            pair = [setup(b,char,slot,kind,stun,edge) for b in (old,new)]
            results = [run(q,bound,slot,flags) for q,bound in zip(pair,contracts)]
            assert results[0][0] == results[1][0], dict(case=[char,slot,kind,stun,edge,flags],
                                                       old=results[0][0],new=results[1][0])
            for r in results:
                assert r[3]['movement'] == 1 and r[3]['consumer'] == 1
            for boundary in (2,4):
                # Compare only A/P at this *internal* boundary. Y is still a
                # dead JumpEngine table index until real Offscreen LDY.
                assert [results[0][2][boundary][i] for i in (0,3)] == [results[1][2][boundary][i] for i in (0,3)]
            if results[0][2] != results[1][2] and len(intermediate) < 12:
                intermediate.append(dict(case=[char,slot,kind,stun,edge,flags],
                    baseline=results[0][2], candidate=results[1][2],
                    final_full_CPU_exact=True))
            rows.append(results[1][1]-results[0][1])
        proof['foreign_and_native_fallback_cases'] = len(rows)
        proof['complete_caller_cycle_delta'] = [min(rows),max(rows)]
        proof['unmasked_intermediate_examples'] = intermediate
        # Pause's genuine LDY/BNE skips the gate and still consumes offscreen.
        paused = 0
        for char,slot in itertools.product([0,20,21,22,23], range(6)):
            pair = [setup(b,char,slot,9,3) for b in (old,new)]
            for q in pair: q.put(TimerControl=1)
            result = [run(q,bound,slot) for q,bound in zip(pair,contracts)]
            assert result[0][0] == result[1][0] and result[0][1] == result[1][1]
            assert all(v[3]['movement'] == 0 for v in result)
            paused += 1
        proof['actual_timer_skip_cases'] = paused
        city = []
        for variant,slot in itertools.product([0,1],range(6)):
            q=setup(new,21,slot,6,0)
            q.put(RcVariant=variant,RcCarrySlot=255,RcThrowSlot=255)
            for name,value in [('RcEnemyStun',12),('RcEnemyType',7),('RcEnemyStamp',1)]:q.set(name,value,slot)
            native_fields=['Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_X_Speed','Enemy_Y_Speed']
            initial=[q.get(n,slot) for n in native_fields]
            costs=[]
            for _ in range(4):
                value,cycles,_,hits=run(q,contracts[1],slot)
                assert hits['city']==1 and hits['movement']==1
                assert value['cpu'][1]==slot and value['cpu'][4]==253
                assert q.get('RcEnemyStun',slot)==12
                assert [q.get(n,slot) for n in native_fields]==initial
                costs.append(cycles)
            q.put(RcCarrySlot=slot,RcCarryType=6,RcHurt=0,Player_X_Position=120,
                  Player_PageLoc=2,Player_Y_Position=140,ScreenLeft_PageLoc=2,ScreenRight_PageLoc=2)
            value,cycles,_,hits=run(q,contracts[1],slot)
            assert hits['city']==1 and value['cpu'][1]==slot and value['cpu'][4]==253
            assert q.get('ObjectOffset')==slot and q.get('RcCarrySlot')==slot
            assert [q.get(n,slot) for n in native_fields]==[120,2,124,0,0]
            assert [q.get(n,slot) for n in ('Enemy_Flag','Enemy_ID','Enemy_State','Enemy_Y_HighPos')]==[1,6,0,1]
            city.append(dict(variant=variant,slot=slot,stun_calls=4,stun_caller_cycles=costs,
                             carried_origin=[2,120,124],carry_caller_cycles=cycles,
                             genuine_gate_and_consumer_hits=hits))
        proof['shared_city_12_cells'] = city
        proof['final_contract'] = 'Exact final A/X/Y/P(all bits)/SP, all named six-slot native/private actor fields, ObjectOffset and restored PRG bank state. No CPU flag exclusions.'
        proof['limits'] = 'Isolated movement/Offscreen caller: no collision/graphics/full RunNormalEnemies, whole application RAM/dead stack/SMC equality, IRQ/NMI/native route timing or River City damage/throw progression claim.'
        assert all(sha(p)==d for p,d in before.items()), 'Bound input changed'
        proof['passed']=True
    except Exception as error:
        proof['error']=repr(error)
        raise
    finally:
        args.output.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=True,cases=proof['foreign_and_native_fallback_cases'],
                         paused=paused,city_cells=len(city),proof_sha256=sha(args.output))))


if __name__=='__main__':
    main()
