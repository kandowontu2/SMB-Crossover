"""Current Bub/Bob genuine cold/Main cost attribution; stdout and zero outputs.

The menu arena is the established native cold fixture. After Select/Start only
controller input and ordinary Main/NMI scheduling change. Model CPU cycles do
not establish hardware cadence. No synthetic terrain, actors or ability state.
"""
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re

import check_ff_white_mushroom_current_1110 as W

R = Path(__file__).resolve().parents[2]
N = W.N
PIN = '7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc'
PAGES = (301, 305, 337, 362, 363, 440, 819, 666)
ROM = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')


def labels(path):
    return {n: int(a, 16) for a, n in re.findall(
        r'^al ([0-9A-Fa-f]+) \.(\S+)$', path.read_text(), re.M)}


def state(m):
    q = {n: N.get(m, n) for n in ('SelectedCharacter', 'Player_Y_Position',
        'NumberofLives', 'GameEngineSubroutine', 'OperMode', 'OperMode_Task',
        'PlayerStatus', 'FrameCounter')}
    q['x'] = N.get(m, 'Player_X_Position') + 256 * N.get(m, 'Player_PageLoc')
    q['actors'] = [dict(slot=i, flag=N.get(m, 'Enemy_Flag', i),
        id=N.get(m, 'Enemy_ID', i), x=N.get(m, 'Enemy_X_Position', i)
        + 256 * N.get(m, 'Enemy_PageLoc', i), y=N.get(m, 'Enemy_Y_Position', i))
        for i in range(6) if N.get(m, 'Enemy_Flag', i)]
    return q


def frame(m, observe=None, *, cold=False, whole_pass=False):
    idle = W.address(m.bundle, 'IdleLoop')
    W.clear_logs(m)
    N.consume(m)
    c = N.NesMPU(memory=m, pc=idle)
    c.sp, c.p = 255, 0x31
    c.stPushWord(0xe33b)
    for _ in range(4_000_000 if cold else 500_000):
        stop=(idle,253) if whole_pass else (idle+12,252)
        if c.processorCycles and (c.pc,c.sp)==stop:
            assert not m.blocked
            return c.processorCycles
        if observe:
            observe(m, c)
        assert m[c.pc], ('BRK', hex(c.pc), m.rawtags)
        c.step()
    raise AssertionError(('Main bound', hex(c.pc), c.sp))


def cold(raw, identity):
    b = W.Symbols.bundle()
    b['raw'] = raw
    old = N.Bus
    N.Bus = W.ControllerBus
    try:
        m = W.UI.seed(b, 0)
    finally:
        N.Bus = old
    for bits in (4, 4, 4, 1):
        W.UI.key(m, bits)
    assert N.get(m, 'CrossoverMenuIndex') == 25
    for _ in range(identity + 1):
        W.UI.key(m, 32)
    assert W.UI.menu_name(m)[0] == ('BUB', 'BOB')[identity]
    start = W.UI.key(m, 16)
    N.invoke(m, 'NativeRareGameMenuRoutineCore::ChkContinue',
        a=start['A'], x=start['X'], y=start['Y'], p=start['P'])
    N.invoke(m, 'PauseRoutine', a=0)
    for epoch in range(700):
        q = state(m)
        assert q['SelectedCharacter'] == 39 and q['NumberofLives'] == 2
        if (q['OperMode'], q['OperMode_Task'], q['GameEngineSubroutine']) == (1, 3, 8):
            return m, dict(epochs=epoch, state=q)
        m.controller_pad = 0
        frame(m, cold=True)
    raise AssertionError('cold active bound')


def bindings(raw):
    image = b''.join(raw[1048592+p*1024:1048592+(p+1)*1024] for p in PAGES)
    retained = R/'build/bub-initial-tier-1103-v87/private-image.bin'
    assert image == retained.read_bytes(), 'Bub carrier changed since cf7'
    q = json.loads((R/'build/bub-upgrades-root-1102-v48/proposal.json').read_text())
    tracked = ('BbNativeUpdate', 'BbNativeInput', 'BbNativeDraw', 'BbNativeBoxes',
        'BbNativeIn', 'BbNativeOut', 'BbNativeProxiesIn', 'BbNativeProxiesOut',
        'BbPlayerStep', 'BbSourceClock', 'BbBubbleStep', 'BbTrappedEnemyStep')
    points = {(3, at): name for name, at in q['labels'].items() if name in tracked}
    head = json.loads((R/'build/bub-menu-candidate-1102-v2/head-projection-v55.json').read_text())
    points.update({(3, at): n for n, at in head['labels'].items()})
    # Source-owned current manager labels are deliberately recorded separately;
    # no old manager address is silently assumed current.
    start = 16+65*8192+0xe00
    manager = raw[start:start+531]
    checks = {'CoCheckCode': 'ad026038e925c907b039aaa50848a509482019af2027af68850968850860',
              'CoCheckHeaders': 'ada17d48a2038ea17d8e1651a00fb9e0dfd108d00a8810f6cae001d0e9b00118688da17d8d165160'}
    for name, code in checks.items():
        data = bytes.fromhex(code)
        assert manager.count(data) == 1, (name, 'current compiled auth binding')
        points[(193, 0xae00+manager.index(data))] = name
    return q, points, dict(private_image_SHA256=sha256(image).hexdigest(),
        current_manager_531_SHA256=sha256(raw[16+65*8192+0xe00:16+65*8192+0x1013]).hexdigest(),
        manager_label_points={n: a for (b,a),n in points.items() if b==193})


def profile(raw, identity, count=24):
    q, points, bound = bindings(raw)
    m, opening = cold(raw, identity)
    for name in ('HuMovement', 'HuDraw', 'HuVisible', 'HuSide', 'HuWeaponTail',
                 'HuFullBox', 'HuHead', 'HuColors', 'HuScroll', 'HuUi',
                 'X5BounceUiDispatch', 'X5OwnInventoryUi', 'X5NativeInventoryUiLeaf',
                 'RlUiDispatch', 'LmUiGate', 'VvUiDispatch', 'NrUi'):
        if name in m.bundle['syms']:
            points[(((W.location(m.bundle, name)-16)//8192)|128,
                    W.address(m.bundle, name))] = name
    assert bytes(m.ram[3][:0x1fe0]) == b''.join(
        raw[1048592+p*1024:1048592+(p+1)*1024] for p in PAGES)[:0x1fe0]
    source_end = q['labels']['BbCodeEnd']
    cases = []
    for phase, pad in (('idle', 0), ('walk', 1)):
        buckets = Counter(); calls = Counter(); pc_cost = Counter(); totals = []; rows = Counter()
        other_banks=Counter();other_pcs=Counter()
        stack = []; inclusive = defaultdict(list)
        before = state(m); last = None
        def observe(mm, c):
            nonlocal last
            if last:
                bucket, bank, pc, cycles = last
                cost = c.processorCycles - cycles
                buckets[bucket] += cost
                pc_cost[bank, pc] += cost
                if bucket=='other_native':
                    other_banks[bank]+=cost;other_pcs[bank,pc]+=cost
            pc = c.pc
            bank = mm.rawtags[(pc-0x8000)//8192] if pc >= 0x8000 else -1
            while stack and (pc, c.sp, bank) == stack[-1]['return']:
                item=stack.pop()
                inclusive[item['name']].append(c.processorCycles-item['cycles'])
            name = points.get((bank, pc))
            if name:
                calls[name] += 1
                if name.startswith(('Hu','X5','Rl','Lm','Vv','Nr')) or name in ('CoCheckCode', 'CoCheckHeaders'):
                    ret=(mm[0x100+((c.sp+1)&255)]+256*mm[0x100+((c.sp+2)&255)]+1)&65535
                    tag=mm.rawtags[(ret-0x8000)//8192] if ret>=0x8000 else -1
                    stack.append(dict(name=name,return_=(ret,(c.sp+2)&255,tag),cycles=c.processorCycles))
                    stack[-1]['return']=stack[-1].pop('return_')
                if name == 'CoCheckCode':
                    smc = W.address(mm.bundle, 'FarcallJmpTarget_SMC')
                    target = mm[smc+1]+256*mm[smc+2]
                    rows[f'{target:04X}'] += 1
            if bank == 3:
                bucket = 'original_source' if 0xa100 <= pc < source_end else 'private_bridge'
            elif bank == 2 and 0xd320 <= pc < 0xd400:
                bucket = 'private_helper'
            elif bank == 193 and 0xae00 <= pc < 0xb013:
                bucket = 'shared_auth'
            elif bank == 193 and (0xa740 <= pc < 0xa800 or 0xb08c <= pc < 0xb0fe):
                bucket = 'shared_dispatch'
            elif bank == 207:
                bucket = 'shared_high_router'
            elif 0x15a <= pc < 0x17c:
                bucket = 'RAM_farcall'
            else:
                bucket = 'other_native'
            last = bucket, bank, pc, c.processorCycles
        for _ in range(count):
            m.controller_pad = pad
            last = None
            total = frame(m, observe)
            bucket, bank, pc, cycles = last
            buckets[bucket] += total-cycles
            pc_cost[bank, pc] += total-cycles
            if bucket=='other_native':
                other_banks[bank]+=total-cycles;other_pcs[bank,pc]+=total-cycles
            totals.append(total)
            assert N.get(m, 'NumberofLives') == 2
        after = state(m)
        assert sum(buckets.values()) == sum(totals) and not stack, stack
        result = dict(identity=('BUB','BOB')[identity], phase=phase, updates=count,
            mean_CPU=sum(totals)/count, range_CPU=[min(totals),max(totals)],
            mean_exclusive={k:v/count for k,v in buckets.items()}, calls=dict(calls),
            authenticated_targets=dict(rows),
            inclusive_cycles_per_update={n:sum(v)/count for n,v in inclusive.items()},
            other_native_banks={k:v/count for k,v in other_banks.items()},
            other_native_hot_PC=[dict(bank=b,PC=f'{p:04X}',cycles_per_update=v/count)
                                 for (b,p),v in other_pcs.most_common(16)],
            hot_PC=[dict(bank=b, PC=f'{p:04X}', cycles_per_update=v/count)
                    for (b,p),v in pc_cost.most_common(12)], before=before, after=after)
        cases.append(result)
        print(json.dumps(dict(event='profile', **result)), flush=True)
    return dict(opening=opening, bindings=bound, cases=cases)


def main():
    p=argparse.ArgumentParser();p.add_argument('--identity',type=int,choices=(0,1))
    p.add_argument('--updates',type=int,default=24);a=p.parse_args()
    raw=ROM.read_bytes();assert sha256(raw).hexdigest()==PIN
    results=[profile(raw,i,a.updates) for i in ([a.identity] if a.identity is not None else range(2))]
    print(json.dumps(dict(passed=True, ROM_SHA256=PIN, bindings=results[0]['bindings'],
        output_files=0, Mesen_run=False, ROM_written=False,
        scope='Genuine cold/menu plus real Main/NMI; CPU model costs only. Actor list is observed, never cleared. No native cadence or full-route claim.')),flush=True)


if __name__=='__main__':main()
