"""Retain Pit v2 FALSE; prove full-caller collision/recharge ordering read-only."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load
from check_tmnt_render_oa import address, location
from verify_native_relocation import NesMPU

ROM_SHA = '6be48337ffee66a22b22de9ce134d5db323649fb4de620c43bad4ca98b80f193'
READY_SHA = '7550b280010b18f7e710cbd94540a907fafd7b7a1dd8fd46a79b92394d5ab114'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def cpu_case(b, mode, partial, immediate, native):
    q = Arena(b, 6)
    q.put(PlayerStatus=0, ObjectOffset=5, CrossoverBehaviorVersion=mode)
    for pickup, tier in [(0, 1), (1, 2)]:
        for n, v in [('PowerUpType', pickup), ('InvPickupOwner', 6),
                     ('InvPickup', 0xfc), ('Enemy_Flag', 1), ('Enemy_State', 128)]:
            q.set(n, v, 5)
        q.invoke('MarioSourcePowerupCollision', x=5)
        for _ in range(60):
            q.invoke('GuestPowerupUpdate')
        assert q.get('PlayerStatus') == tier
    q.put(Player_X_Position=112, Player_PageLoc=0, Player_Y_Position=176,
          Player_Y_HighPos=1, Player_State=0, PlayerFacingDir=1,
          Player_MovingDir=1, Player_CollisionBits=255, MmOldX=112,
          ScreenLeft_PageLoc=0, ScreenLeft_X_Pos=0, ScreenRight_PageLoc=0,
          ScreenRight_X_Pos=255, GameEngineSubroutine=8, TimerControl=0,
          AreaType=1, OperMode_Task=3, ScrollLock=1, AreaParserTaskNum=0)
    q.array('GameTimerDisplay', [3, 9, 9])
    for page in (0, 1):
        for row in (11, 12):
            for col in range(16):
                q.set('Block_Buffer_1', 0x54, page*208+row*16+col)
    for slot in range(6):
        q.set('Enemy_Flag', 0, slot)
    names = ['GameLoop', 'ExpandedMovement', 'PitFlightUpdate',
             'PitFlightUpdate::Stop', 'PitFlightUpdate::Done',
             'PlayerBGCollision', 'MegaMan202AfterBG']
    owners = {(address(b, n), (location(b, n)-16)//8192): n for n in names}
    trace, endpoints, burns, fuel_writes = [], [], [], []
    landed, recharge, relaunched, eligible, age = None, None, None, None, 0
    original = NesMPU.step

    def step(c):
        nonlocal eligible
        bank = q.m.banks[(c.pc-0x8000)//8192] if c.pc >= 0x8000 else -1
        n = owners.get((c.pc, bank))
        row = dict(age=age, owner=n, PC=c.pc, bank=bank,
                   state=q.get('Player_State'), y=q.get('Player_Y_Position'),
                   fuel=q.get('XgPitFuel'), flight=q.get('XgPitFlight'))
        if n:
            trace.append(row)
        if n == 'PitFlightUpdate':
            eligible = row.copy()
            eligible['sp'] = c.sp
            eligible['return_word'] = q.m[256+(c.sp+1)%256]+256*q.m[256+(c.sp+2)%256]
        if n in ['PitFlightUpdate::Done', 'PitFlightUpdate::Stop']:
            # Stop names its first instruction; its genuine RTS is +8.
            pass
        exit_pcs = [address(b, 'PitFlightUpdate::Done'), address(b, 'PitFlightUpdate::Stop')+8]
        if bank == (location(b, 'PitFlightUpdate')-16)//8192 and c.pc in exit_pcs:
            assert eligible and c.sp == eligible['sp']
            ret = q.m[256+(c.sp+1)%256]+256*q.m[256+(c.sp+2)%256]
            assert ret == eligible['return_word'] and ret+1 == 0x016e
            now = q.get('XgPitFuel')
            if eligible['fuel'] == now+1:
                burns.append(age)
            if eligible['state'] == 0:
                assert now == 60 and q.get('XgPitFlight') == 0
            endpoints.append(dict(age=age, PC=c.pc, bank=bank, sp=c.sp,
                                  return_word=ret, entry=eligible.copy(),
                                  fuel=now, state=q.get('Player_State'),
                                  flight=q.get('XgPitFlight')))
        original(c)

    NesMPU.step = step
    matched = 0
    last_fuel = None
    try:
        for age in range(241 if partial else 351):
            a = 5 <= age < 11 or 17 <= age < (36 if partial else 111)
            if landed is not None and not partial:
                start = landed+(1 if immediate else 3)
                a = a or start <= age < start+6
            q.put(SavedJoypadBits=(128 if a else 0) |
                  (64 if not partial and 41 <= age < 44 else 0))
            _, writes = q.invoke('GameLoop')
            now = dict(x=q.get('Player_X_Position'), y=q.get('Player_Y_Position'),
                       state=q.get('Player_State'), fuel=q.get('XgPitFuel'),
                       flight=q.get('XgPitFlight'))
            assert now['x'] == 112 and q.get('PlayerStatus') == 2
            assert q.get('GameEngineSubroutine') == 8
            assert q.get('InjuryTimer') == q.get('GuestHurtTicks') == q.get('MmDeathFlag') == 0
            if not partial and not immediate and mode == 0 and age in native:
                assert now == {n: int(native[age][n]) for n in now}
                matched += 1
            fuel_writes += [dict(age=age, **w) for w in writes if w['address'] == address(b, 'XgPitFuel')]
            if burns and now['state'] == 0 and landed is None:
                landed = age
                assert now['fuel'] == (41 if partial else 0), now
            if landed is not None and age == landed+1:
                assert now['fuel'] == 60 and now['flight'] == 0
                recharge = age
            if landed is not None and age > landed and now['state'] != 0 and relaunched is None:
                assert not partial and now['fuel'] == 60 and now['flight'] == 0
                relaunched = age
            last_fuel = now['fuel']
    finally:
        NesMPU.step = original
    assert len(burns) == (19 if partial else 60)
    assert landed is not None and recharge == landed+1
    assert partial or relaunched == landed+(1 if immediate else 3)
    assert last_fuel == 60 and q.get('Player_State') == 0
    window = [r for r in trace if landed-1 <= r['age'] <= landed+3]
    ground = next(r for r in endpoints if r['age'] == recharge)
    assert ground['fuel'] == 60
    assert ground['entry']['state'] == (1 if immediate else 0)
    return dict(mode=mode, partial_release=partial, immediate_next_grounded_A=immediate,
                GameLoop_calls=age+1, saved_native_rows_matched=matched,
                burn_count=len(burns), burn_ages=[burns[0], burns[-1]],
                landing_age=landed, collision_update_fuel=41 if partial else 0,
                recharge_age=recharge, recharge_fuel=60, relaunch_age=relaunched,
                real_ground_return=ground, owner_window=window,
                fuel_writes=[w for w in fuel_writes if landed-1 <= w['age'] <= landed+3],
                final_cleanup=True, source_owned_tier_and_fuel=True)


def model(rec, now, age):
    assert rec['recharged'] and rec['groundRechargeAt'] == age
    assert age == rec['landedAt']+1 and now['fuel'] == 60 and now['flight'] == 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=ROOT/'build/current-6be-pit-easy-items-v2/landing-negative.json')
    a = p.parse_args()
    assert not a.output.exists()
    folder = ROOT/'build/current-6be-pit-easy-items-v2'
    ready = folder/'prepared-not-run.json'
    assert sha(ready) == READY_SHA
    for z in json.loads(ready.read_text())['bindings']:
        f = Path(z['path'])
        assert f.stat().st_size == z['bytes'] and sha(f) == z['sha256']
    rom = ROOT/'build/samus_fixed_hud_current4a.nes'
    assert sha(rom) == ROM_SHA
    launch = json.loads((folder/'launch.json').read_text())
    assert launch['exit_code'] == 1 and not launch['changed_inputs']
    assert launch['settings_before'] == launch['settings_after']
    assert 'FAIL Real landing restored fuel' in (folder/'native/samus_fixed_hud_current4a-run.log').read_text()
    rows = list(csv.DictReader((folder/'native/pit-components.csv').open()))
    native = {int(r['age']): r for r in rows if r['event'] == 'update' and r['case'] == '8'}
    assert sorted(native) == list(range(137))
    assert len([r for r in rows if r['event'] == 'case-complete']) == 7
    b = scoped_load(rom)
    controls = [cpu_case(b, mode, partial, immediate, native)
                for mode in (0, 1) for partial, immediate in [(False, False), (True, False), (False, True)]]
    assert controls[0]['saved_native_rows_matched'] == 137
    rec = dict(recharged=True, landedAt=137, groundRechargeAt=138)
    now = dict(fuel=60, flight=0)
    model(rec, now, 138)
    rejects = 0
    for r, n, age in [({**rec, 'recharged': False}, now, 138),
                      ({**rec, 'groundRechargeAt': 137}, now, 138),
                      (rec, {**now, 'fuel': 59}, 138),
                      (rec, {**now, 'flight': 1}, 138),
                      (rec, now, 139)]:
        try:
            model(r, n, age)
        except AssertionError:
            rejects += 1
    assert rejects == 5
    files = [Path(__file__), ready, folder/'launch.json']
    files += sorted(f for f in (folder/'native').iterdir() if f.is_file())
    files += [rom, rom.with_suffix('.dbg'), ROOT/'tools/audit/current_pit_powerups_v2.lua',
              ROOT/'tools/audit/current_pit_powerups_prepare_v2.py']
    files += [ROOT/'src'/n for n in ['expanded.s', 'expanded_weapons.s', 'player.s', 'collision.s', 'roster.s']]
    proof = dict(passed=False, native_passed=False, source_diagnosis_passed=True,
                 ROM_sha256=ROM_SHA, original_ready_sha256=READY_SHA,
                 original_failure='Real landing restored fuel', completed_native_cases=7,
                 last_saved_native_row=native[136], Hard='UNRUN',
                 native_terminal_snapshot=False,
                 diagnosis='Fixture checks at collision-established landing; source recharges at next grounded movement, not retroactively in the prior movement call.',
                 controls=controls, complete_GameLoop_calls=sum(c['GameLoop_calls'] for c in controls),
                 model_positive=1, model_negative_rejections=rejects,
                 agent_visual_review=True, selected_existing_images=6,
                 visual_scope='Six existing whole-frame PNGs: bow/hammer/transform/flutter body and arrow coherent in samples; wing poses use existing source art. No all-frame or pixel/audio fidelity claim.',
                 limits='No emulator launch. Complete CPU callers and saved137-row numeric match; not a saved full RAM replay, actual failed-frame pixels or PPU timing. No resource/outcome writes introduced in native fixture. Controls earn CPU tiers via actual collision/transform and fuel through actual ground source.',
                 bindings=[dict(path=str(f.resolve()), bytes=f.stat().st_size, sha256=sha(f)) for f in files])
    a.output.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(output=str(a.output),sha256=sha(a.output),bindings=len(files),
                          native_passed=False,complete_GameLoop_calls=proof['complete_GameLoop_calls'])))


if __name__ == '__main__':
    main()
