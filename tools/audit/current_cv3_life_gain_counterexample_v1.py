"""Finite CPU counterexample: earned CV3 subweapon/hearts lost after real 1-Up.

No native execution or game edits. Typed mature actors/map only; no life,
subweapon, heart, health, star timer, RNG or defeat-result setup writes.
"""
from pathlib import Path
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R/'tools/audit'))
from current_shared_star_life_prepare_v1 import Arena, NesMPU, hooks_for, actor, EXPECTED
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run(b, variant):
    q = Arena(b, 5)
    q.put(CrossoverBehaviorVersion=1, Cv3Variant=variant, OperMode_Task=3,
          AreaType=1, PlayerStatus=0, Player_X_Position=112, Player_PageLoc=0,
          Player_Y_Position=176, Player_State=0, ScreenLeft_PageLoc=0,
          ScreenLeft_X_Pos=0, ScreenRight_PageLoc=0, ScreenRight_X_Pos=255,
          ScrollLock=1, Player_CollisionBits=255, Player_MovingDir=1)
    q.array('GameTimerDisplay', [3, 9, 9])
    q.invoke('InventoryInit'); q.invoke('CrossoverGraphicsBank')
    for n in ['Block_Buffer_1', 'MmSolidTerrain', 'MmBrickHealth']:
        q.array(n, [0]*416)
    for page in range(2):
        for row in [11, 12]:
            for col in range(16): q.set('Block_Buffer_1', 84, page*208+row*16+col)
    for i in range(6): q.set('Enemy_Flag', 0, i); q.set('Enemy_CollisionBits', 0, i)
    names = ['Cv3Health', 'Cv3Hearts', 'Cv3Subweapon', 'Cv3Power']
    watched = {address(b, n)+variant-1: n for n in names}
    watched.update({address(b, n): n for n in ['NumberofLives', 'Cv3LastLife']})
    fields = lambda: {n: q.get(n, variant-1) for n in names} | {
        n: q.get(n) for n in ['NumberofLives', 'Cv3LastLife', 'StarInvincibleTimer']}
    hooks, _ = hooks_for(b)
    call = 0; phase = 'settle'; events = []; writers = []; physical = []; gain_snapshots = []
    oldstep = NesMPU.step
    span = lambda n: (address(b, n), address(b, n)+int(b['syms'][n]['size'], 0),
                      (location(b, n)-16)//8192)
    spans = {n: span(n) for n in ['Cv3Ensure', 'Cv3CollectPickupGate',
                                'Cv3UpdateDrops', 'FloateyNumbersCore']}

    def step(c):
        pc = c.pc; bank = q.m.banks[(pc-0x8000)//8192] if pc >= 0x8000 else -1
        old = {at: q.m[at] for at in watched}
        for name in ['PhysicalPickup', 'StarContact', 'LifeIncrement']:
            h = hooks[name]
            if pc == h['pc'] and bank in h['banks']:
                physical.append(dict(event=name, phase=phase, call=call, pc=pc,
                    bank=bank, x=c.x, pickup=q.get('PowerUpType', 5), before=fields()))
        start = len(q.m.writes); oldstep(c)
        for at, value in q.m.writes[start:]:
            if at not in watched: continue
            owners = [n for n, (a, z, owner) in spans.items() if owner == bank and a <= pc < z]
            writers.append(dict(phase=phase, call=call, writer_pc=pc,
                physical_bank=bank, opcode=list(b['raw'][16+bank*8192+(pc&8191):
                16+bank*8192+(pc&8191)+3]), source_owners=owners,
                field=watched[at], address=at, old=old[at], new=value))
            if watched[at] == 'NumberofLives' and value != old[at]:
                gain_snapshots.append(dict(call=call, fields=fields()))

    def main():
        nonlocal call
        q.set('SavedJoypadBits', 0); call += 1
        q.invoke('GameLoop')
        assert q.get('GameEngineSubroutine') == 8 and q.get('InjuryTimer') == 0
        assert q.get('MmDeathFlag') == 0

    NesMPU.step = step
    try:
        for _ in range(30): main()
        initial = fields()
        assert initial['Cv3Hearts'] == 10 and initial['Cv3Subweapon'] == 0
        phase = 'star'; actor(q, 46, 5, 2, 5)
        for _ in range(20):
            main()
            if q.get('StarInvincibleTimer'): break
        else: raise AssertionError('Real Star pickup missing')
        assert q.get('StarInvincibleTimer') == 35
        phase = 'star-contact'; actor(q, 6, 0, None, 5)
        for _ in range(20):
            main()
            if q.get('Enemy_State', 0) & 32: break
        else: raise AssertionError('Real Star contact defeat missing')
        phase = 'expiry'
        for _ in range(900):
            main()
            if q.get('StarInvincibleTimer') == 0: break
        else: raise AssertionError('Natural expiry missing')
        after_star = fields()
        credits = [w for w in writers if w['field'] == 'Cv3Hearts' and
                   w['new'] != w['old'] and w['source_owners'] == ['Cv3UpdateDrops']]
        assert len(credits) == 1 and credits[0]['old'] == 10 and credits[0]['new'] == 11
        assert after_star['Cv3Hearts'] == 11
        # Source prepares a genuine flower's owner/stamp; full GameLoop does
        # actual collision and grant. No equipment/heart fields are seeded.
        phase = 'equipment-prepare'; actor(q, 46, 5, 1, 5)
        q.invoke('Cv3PreparePickupGate', x=5)
        stamp = {n: q.get(n, 5) for n in ['InvPickup', 'InvPickupOwner',
                                          'Cv3PickupVariant', 'PowerUpType']}
        assert stamp == dict(InvPickup=0xd1, InvPickupOwner=5,
                             Cv3PickupVariant=variant, PowerUpType=1)
        phase = 'equipment-physical-collect'
        for _ in range(20):
            main()
            if q.get('Enemy_Flag', 5) == 0: break
        else: raise AssertionError('Real non-default subweapon pickup missing')
        earned = fields()
        assert earned['Cv3Subweapon'] == 1 and earned['Cv3Hearts'] == 16
        grants = [w for w in writers if w['phase'] == phase and
                  w['source_owners'] == ['Cv3CollectPickupGate']]
        assert any(w['field'] == 'Cv3Subweapon' and w['old'] == 0 and w['new'] == 1 for w in grants)
        assert any(w['field'] == 'Cv3Hearts' and w['old'] == 11 and w['new'] == 16 for w in grants)
        events.append(dict(event='genuinely-earned-before-1Up', call=call,
                           fields=earned, pickup_stamp=stamp, writers=grants))
        phase = 'life'; actor(q, 46, 5, 3, 5); before_life = earned['NumberofLives']
        for _ in range(70):
            main()
            if q.get('NumberofLives') == before_life+1: break
        else: raise AssertionError('Actual 1-Up popup INC missing')
        gain_call = call; assert len(gain_snapshots) == 1
        immediately_after_gain = gain_snapshots[0]['fields']
        assert immediately_after_gain['Cv3Hearts'] == 16 and immediately_after_gain['Cv3Subweapon'] == 1
        if q.get('Cv3Subweapon', variant-1) == 1:
            phase = 'first-update-after-life-gain'; main()
        after = fields()
        resets = [w for w in writers if w['call'] >= gain_call and w['source_owners'] == ['Cv3Ensure'] and w['old'] != w['new']]
        assert after['NumberofLives'] == before_life+1 and after['Cv3LastLife'] == after['NumberofLives']
        assert after['Cv3Hearts'] == 10 and after['Cv3Subweapon'] == 0
        assert [(w['field'], w['old'], w['new']) for w in resets] == [
            ('Cv3Hearts', 16, 10), ('Cv3Subweapon', 1, 0)]
        increments = [w for w in writers if w['field'] == 'NumberofLives' and w['old'] != w['new']]
        assert len(increments) == 1 and increments[0]['source_owners'] == ['FloateyNumbersCore']
        assert len([p for p in physical if p['event'] == 'LifeIncrement']) == 1
        events.append(dict(event='real-1Up-followed-by-unintended-reset', gain_call=gain_call,
            first_reset_call=resets[0]['call'], before=earned, immediately_after_gain=immediately_after_gain,
            after=after, first_wrong_write=resets[0], reset_writers=resets,
            actual_native_popup_increment=increments[0]))
        return dict(counterexample_confirmed=True, product_invariant_passed=False,
            variant=variant, identity={1:'grant', 2:'sypha'}[variant], full_GameLoop_calls=call,
            native_run=False, initial=initial, star_earned_collection=credits,
            events=events, actual_physical_hooks=physical, tracked_writers=writers,
            setup_scope='Zero-RAM standalone source cold initialization, flat typed map/mature actors and neutral input. No seeded life, health, subweapon, hearts, Star timer, RNG or defeat outcome; flower metadata prepared by actual Cv3PreparePickupGate. Life0 is zero-RAM cold baseline, not actual menu life count.')
    finally: NesMPU.step = oldstep


def main():
    rom = R/'build/mega_proto_body_palette_9ea.nes'
    assert sha(rom) == EXPECTED
    out = R/'build/current_cv3_life_gain_counterexample_v1.json'
    assert not out.exists(), 'Do not overwrite a preserved counterexample'
    b = scoped_load(rom)
    z = dict(ROM_sha256=EXPECTED, native_run=False,
        tool=dict(path=str(Path(__file__)), sha256=sha(__file__)),
        inputs=[dict(path=str(p), sha256=sha(p)) for p in
                [rom, rom.with_suffix('.dbg'), rom.with_suffix('.lbl'),
                 R/'src/cv3_core.s', R/'src/cv3_pickups.s', R/'src/cv3_drops.s']],
        cases=[run(b, v) for v in [1, 2]])
    out.write_text(json.dumps(z, indent=2)+'\n', newline='\n')
    print(json.dumps(dict(proof=str(out), sha256=sha(out), cases=len(z['cases']),
                         actual_product_counterexample=True, native_run=False)))


if __name__ == '__main__': main()
