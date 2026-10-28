"""Finite cold caller/entrance/IRQ controls and original displayed-epoch facts."""
from pathlib import Path
import csv
import hashlib
import itertools
import json

from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load
from check_tmnt_render_oa import address, location
from cv3_life_gain_controls_v1 import run, regs, clone, BASE, bus
from chip_hud_queue_controls_v1 import irq_live, queue
from final_inventory_compact_capture_v1 import records
import current_chip_dale_earned_cpu_v1 as earned

R = Path(__file__).resolve().parents[2]
B = R / 'build'
P = B / 'chip_hud_queue_complete.nes'
N = B / 'chip_cold_health_init.nes'
OLD = '129dabe88489c78e1ead49b17e898979bd01ee0806d44eba2efc1871d4dd227f'
NEW = 'cd70d5647999e9167af94842ec4a6d09a94c2f5802f49d7b944772ca11451a83'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def cold(b, identity='chip', mode=0):
    _, char, variant, value = BASE[identity]
    q = Arena(b, char)
    q.put(OperMode=1, OperMode_Task=3, AreaType=1,
          CrossoverBehaviorVersion=mode, NumberofLives=2, AreaPointer=194,
          WorldNumber=0, LevelNumber=0, PlayerStatus=0, Player_X_Position=40,
          Player_PageLoc=0, Player_Y_Position=176, Player_Y_HighPos=1,
          PlayerEntranceCtrl=0, AltEntranceControl=0, GameEngineSubroutine=7,
          DisableScreenFlag=0, NmiDisable=255, CdHealth=2, CdMagic=165)
    q.array('X5MenuVariants', list(range(16)))
    if variant:
        q.set(variant, value)
    q.array('GameTimerDisplay', [4, 0, 0])
    return q


def state(q):
    return {n: q.get(n) for n in ['CdHealth', 'CdMagic', 'GameEngineSubroutine']}


def stable(q, omit=()):
    dead = set(range(256, 512))
    for g in q.b['segs'].values():
        if g['name'] == '"SMCCODE"':
            dead.difference_update(range(int(g['start'], 0), int(g['start'], 0) + int(g['size'], 0)))
    return bytes(v for i, v in enumerate(q.m[:0x8000]) if i not in dead and i not in omit), q.m.banks


def main():
    assert sha(P) == OLD and sha(N) == NEW
    out = B / 'chip_cold_health_init_controls.json'
    assert not out.exists()
    old, new = scoped_load(P), scoped_load(N)
    whole, trajectories, irqs = [], [], []
    health = address(new, 'CdHealth')
    magic = address(new, 'CdMagic')
    for identity, mode, flags in itertools.product(BASE, [0, 1], [0x20, 0x21, 0x60, 0xa2]):
        qs = [cold(b, identity, mode) for b in [old, new]]
        variants = [bytes(q.get('X5MenuVariants', i) for i in range(16)) for q in qs]
        cs = [run(q, 'KbFreshGameInit', flags=flags)[0] for q in qs]
        own = identity in ['chip', 'dale']
        assert regs(cs[0]) == regs(cs[1])
        omit = {health, magic} if own else set()
        assert stable(qs[0], omit) == stable(qs[1], omit)
        assert bus(qs[0], omit) == bus(qs[1], omit)
        assert all(bytes(q.get('X5MenuVariants', i) for i in range(16)) == v for q, v in zip(qs, variants))
        assert [q.get('CdHealth') for q in qs] == ([0, 3] if own else [0, 0])
        assert [q.get('CdMagic') for q in qs] == ([0, 165] if own else [0, 0])
        if own:
            assert [(at, v) for at, v in qs[1].m.writes if at in omit] == [(health, 0), (magic, 0), (health, 3), (magic, 165)]
        whole.append(dict(identity=identity, mode=mode, flags=flags,
                          delta=cs[1].processorCycles-cs[0].processorCycles,
                          only_cold_constructor_HP_and_magic_changed=own))

    for identity, mode in itertools.product(['chip', 'dale'], [0, 1]):
        qs = [cold(b, identity, mode) for b in [old, new]]
        for q in qs:
            run(q, 'KbFreshGameInit')
        steps = []
        old_queued_digit = set()
        for tick in range(3):
            samples = []
            cs = []
            for q in qs:
                q.put(VRAM_Buffer1=0, VRAM_Buffer1_Offset=0,
                      VRAM_Buffer_AddrCtrl=0, SavedJoypadBits=0)
                before = state(q)
                c, trace = run(q, 'GameLoop', record=True)
                cs.append(c)
                names = [n for n in ['PlayerCtrlRoutine', 'CdMovement', 'CdEnsureInit', 'CdHud']
                         if (address(q.b, n), (location(q.b, n)-16)//8192) in trace]
                samples.append(dict(before=before, after=state(q), owners=names, queue=queue(q).hex()))
            assert regs(cs[0]) == regs(cs[1])
            if tick == 0:
                assert samples[0]['after'] == dict(CdHealth=0, CdMagic=0, GameEngineSubroutine=8)
                assert samples[1]['after'] == dict(CdHealth=3, CdMagic=165, GameEngineSubroutine=8)
                assert samples[0]['owners'] == samples[1]['owners'] == ['CdHud']
                assert samples[0]['queue'].endswith('204b042411190000')
                assert samples[1]['queue'].endswith('204b042411190300')
                before_packet = bytes.fromhex(samples[0]['queue'])
                after_packet = bytes.fromhex(samples[1]['queue'])
                assert len(before_packet) == len(after_packet)
                changed = [i for i, (a, b) in enumerate(zip(before_packet, after_packet)) if a != b]
                assert changed == [len(before_packet)-2] and before_packet[changed[0]] == 0 and after_packet[changed[0]] == 3
                old_queued_digit = {address(new, 'VRAM_Buffer1')+changed[0]}
            else:
                # The deliberately corrected first HP payload remains as dead
                # bytes beyond the next terminated queue. No other RAM/SMC
                # may differ, and the current complete live queue is exact.
                assert stable(qs[0], old_queued_digit) == stable(qs[1], old_queued_digit)
                assert samples[0]['queue'] == samples[1]['queue']
                assert samples[1]['after']['CdHealth'] == 3
                active_end = address(new, 'VRAM_Buffer1')+qs[1].get('VRAM_Buffer1_Offset')
                assert all(at > active_end for at in old_queued_digit)
                assert all(qs[0].m[at] == 0 and qs[1].m[at] == 3 for at in old_queued_digit)
            steps.append(dict(tick=tick, samples=samples, CPU_delta=cs[1].processorCycles-cs[0].processorCycles))
        trajectories.append(dict(identity=identity, mode=mode, steps=steps,
            preserved_prior_corrected_queue_digit_addresses=sorted(old_queued_digit),
            scope='Actual assembled new-game caller then full entrance/Main sequence; staged CPU context, not an actual native RAM snapshot.'))

    for identity in ['chip', 'dale', 'mario']:
        q = cold(new, identity)
        image, banks = list(q.m), q.m.banks[:]
        reference = clone(new, image, banks)
        cpu, trace = run(reference, 'KbFreshGameInit', record=True)
        names = ['CdNewGameProfiles', 'X5InventoryInit', 'X5ProfilesNewGame']
        spans = [(address(new, n), address(new, n)+int(new['syms'][n]['size'], 0),
                  (location(new, n)-16)//8192) for n in names]
        keys = sorted({k for k in trace if any(k[1] == bank and lo <= k[0] < hi for lo, hi, bank in spans)})
        for key in keys:
            t = clone(new, image, banks)
            c, _ = run(t, 'KbFreshGameInit', inject=key)
            assert regs(c) == regs(cpu) and irq_live(t) == irq_live(reference)
            assert bus(t) == bus(reference)
            hardware = [(at, v) for i, (at, v) in enumerate(t.m.writes) if i in t.m.irq_indices and at >= 0x2000]
            scroll, control = t.get('IrqNewScroll'), t.get('IrqPPUCTRL')
            assert hardware == [(0x2006, (control&1)<<2), (0x5128, 0), (0x2005, 32),
                                (0x2005, scroll), (0x2006, 128|(scroll>>3))]
        irqs.append(dict(identity=identity, actual_instruction_boundaries=len(keys),
                         final_AXYP_RAM_banks_fiveSMC_exact=True, ordered_five_IRQ_stores_checked=True))

    # Reuse the real earned campaign, changing only its initial legacy init
    # invocation to the actual cold-menu new-game constructor under test.
    campaigns = []
    original = Arena.invoke
    init_calls = []
    def invoke(q, name, *a, **kw):
        if name == 'InventoryInit':
            name = 'KbFreshGameInit'
            init_calls.append(q.get('CdVariant'))
        return original(q, name, *a, **kw)
    Arena.invoke = invoke
    try:
        for variant, mode in itertools.product([0, 1], [0, 1]):
            proof = earned.campaign(new, variant, mode)
            assert proof['passed']
            campaigns.append(dict(variant=variant, mode=mode, actual_ROM_sha256=NEW,
                                  Main_calls=proof['GameLoop_calls'],
                                  actual_cold_caller='KbFreshGameInit',
                                  stages=[dict(name=z['name'], before=z['before'], after=z['after']) for z in proof['cases']]))
    finally:
        Arena.invoke = original
    assert init_calls == [0, 0, 1, 1]

    native = B / 'verification/chip-129d-easy-v1'
    crop = lambda raw, x, y: b''.join(raw[((y+d)*256+x)*4:((y+d)*256+x+8)*4] for d in range(8))
    epochs = []
    three = None
    for record, raw in records(native / 'captures.nesppuv1'):
        frame = record['stamp']['ppu_frame']
        if record['record'] <= 3:
            digit = crop(raw, 112, 16)
            if record['record'] <= 2:
                assert digit == crop(raw, 24, 24)  # Actual displayed score0 glyph.
            else:
                three = digit
            epochs.append(dict(record=record['record'], frame=frame, stamp=record['stamp'],
                               digit=0 if record['record'] < 3 else 3,
                               glyph_sha256=hashlib.sha256(digit).hexdigest()))
        if frame == 408:
            assert three == crop(raw, 208, 24)  # Actual displayed timer394's first3.
            break
    rows = list(csv.DictReader((native / 'trace.csv').open()))
    paths = [Path(__file__), P, P.with_suffix('.dbg'), N, N.with_suffix('.dbg'),
             B / 'chip_cold_health_init_build.json', B / 'chip_cold_health_init_setup_negative.json',
             B / 'chip_cold_health_init_first_caller_mismatch.json',
             native / 'result.json', native / 'trace.csv', native / 'captures.nesppuv1',
             native / 'captures-index.jsonl', R / 'tools/audit/current_chip_dale_earned_cpu_v1.py']
    result = dict(passed=True, source_CPU_only=True, native_run=False,
        parent_sha256=OLD, candidate_sha256=NEW, whole_cold_callers=whole,
        entrance_sequences=trajectories, IRQ=irqs, earned_campaigns=campaigns,
        actual_old_native_epochs=epochs,
        old_native_trace=[z for z in rows if 243 <= int(z['frame']) <= 247],
        cause='Visible first entrance draws before first PlayerCtrl/CdMovement/CdEnsureInit. Original HUD reads cold0; initialized3 appears in PPU247 after the first movement update.',
        limitations='Native raw health/initialization stores and exact PPUMASK stamps were not logged at245. Actual full rendered pixels establish visible0 in245/246 and3 in247; detailed init ordering is a complete source-CPU reproduction. No candidate native or actual vblank/NMI scheduling claim.',
        hot_gameplay_CPU_delta=0, new_RAM=0, bank79_queue_repair_unchanged=True,
        retained_control_negative='Initial whole-RAM continuation assertion rejected the deliberately corrected prior HP payload byte after it was beyond the next queue terminator. Successor checks only that exact source-written0/3 payload address, proves it is outside every current live queue, and compares all other RAM/SMC/active queue exactly. No hardware/APU mask.',
        bindings={str(p): sha(p) for p in paths})
    out.write_text(json.dumps(result, indent=2)+'\n', newline='\n')
    print(json.dumps(dict(passed=True, receipt=str(out), sha256=sha(out),
        cold_callers=len(whole), IRQ=sum(z['actual_instruction_boundaries'] for z in irqs),
        earned_Main=sum(z['Main_calls'] for z in campaigns),
        cold_cycle_deltas=sorted({z['delta'] for z in whole})), indent=2))


if __name__ == '__main__':
    main()
