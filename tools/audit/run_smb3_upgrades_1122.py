"""Source-only validation by default; explicit Root native Mushroom/suit runs."""

import argparse
import json
from pathlib import Path
from unittest.mock import patch

import build_storage_guard_v1 as Storage
from capture_budget import preflight
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
import replay_smb3_upgrades_1122 as Replay
from run_stdout_mesen_1110 import run

Current = Replay.Current
R, ROM, H, PIN = Replay.R, Replay.ROM, Replay.H, Replay.PIN
OUT = R / 'build/smb2-flag-native-1113'


def prediction_checks(raw):
    """Bounded typed CPU/Lua components; these do not prove a natural route."""
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    from replay_sonic_hidden_life_f7c9_1116 import value

    policy = Replay.POLICY.read_text(encoding='utf-8')
    runtime = LuaRuntime()
    runtime.execute("SMB3_UPGRADE_BASE=function()return{}end;SMB3_UPGRADE_PROGRESS={};SMB3_UPGRADE_MODE='mushroom-suit'")
    helpers = runtime.execute(policy[:policy.index('return function(c)')] +
                              '\nreturn {advance=advanceRandom,jump=jumpDrawSteps}')
    _, old_bundle, _ = Current.Stock.Shared._metadata(Current.Stock.Beans.inverse(raw))
    bundle = dict(old_bundle, raw=raw)
    cpu = Current.N
    base = cpu.fresh(bundle)
    cpu.put(base, SelectedCharacter=17, M3Variant=2, M3Marker=0xb3, M3Form=1,
            NumberofLives=2, AreaType=1, LevelNumber=0, AreaNumber=0, PlayerFacingDir=1)
    cpu.invoke(base, 'M3Reset')
    cpu.put(base, Player_X_Position=220, Player_PageLoc=4, Player_Y_Position=176,
            Player_Y_HighPos=1, Player_State=0, PlayerSize=0, Player_X_Speed=0,
            Player_Y_Speed=0, SavedJoypadBits=0, M3Previous=0)
    fractions = (*range(0, 256, 16), 255)
    jump_cases = []
    for variant in (2, 3):
        for fraction in fractions:
            m = cpu.fork(base)
            cpu.put(m, M3Variant=variant, **{'M3Native::Player_YVelFrac': fraction})
            predicted = helpers.jump(176, fraction)
            trace = []
            for tick in range(1, 17):
                cpu.put(m, SavedJoypadBits=128, FrameCounter=tick)
                cpu.invoke(m, 'M3Movement')
                y = cpu.get(m, 'Player_Y_Position')
                trace.append(y)
                if 144 <= y + 6 <= 159:
                    assert tick == predicted, ('Native jump prediction', variant, fraction, tick, predicted, trace)
                    break
            else:
                raise AssertionError(('Native head-probe crossing bound', variant, fraction, trace))
            jump_cases.append(dict(variant=variant, fraction=fraction, steps=tick))

    random_cases = []
    seeds = ([165, 0, 0, 0, 0, 0, 0], [255]*7, list(range(1, 8)), [165, 53, 211, 48, 29, 3, 7])
    for seed in seeds:
        m = cpu.fork(base)
        cpu.put(m, OperMode=1, OperMode_Task=3, GameEngineSubroutine=8,
                GamePauseStatus=1, GamePauseTimer=1, SavedJoypad1Bits=0)
        address = Current.W.address(bundle, 'PseudoRandomBitReg')
        m[address:address+7] = seed
        before = cpu.get(m, 'FrameCounter')
        cpu.invoke(m, 'GameLoop')
        actual = list(m[address:address+7])
        expected = list(helpers.advance(runtime.table_from(seed), 1).values())
        assert actual == expected and cpu.get(m, 'FrameCounter') == before
        random_cases.append(dict(before=seed, after=actual))

    pause_cases = []
    for suit, target in Current.TARGET_SUITS.items():
        lua = LuaRuntime()
        lua.execute("SMB3_UPGRADE_BASE=function()return{}end;SMB3_UPGRADE_PROGRESS={mushroom=true};SMB3_UPGRADE_MODE='mushroom-suit';SMB3_UPGRADE_TARGET="+str(target))
        choose = lua.execute(policy)
        memory = dict(M3Form=1, FrameCounter=70)
        random = [165, 53, 211, 48, 29, 3, 7]
        def read(name, index=0):
            if name == 'PseudoRandomBitReg':
                return random[index or 0]
            return memory.get(name, 0)
        c = lua.table_from(dict(char=17, world=0, level=0, x=1244, y=176, vx=0,
                                grounded=True, lastA=False, update=100, r=read,
                                enemy=lambda: None, block=lambda x, y: 0))
        assert choose(c)['start']
        # Independent56-bit description of the authentic native seven RORs.
        def rotate(state):
            feedback=((state[0] ^ state[1]) & 2) >> 1
            return list(((int.from_bytes(bytes(state), 'big') >> 1) | (feedback << 55)).to_bytes(7, 'big'))
        # Two catch-up loops consume the old Left input before Start is polled.
        # Neither scheduling Start nor counting a GameLoop is acknowledgement.
        for skipped in (1, 2):
            c.x=1244-skipped;c.vx=256-skipped
            memory.update(FrameCounter=70+skipped, M3Previous=2,
                          **{'M3Native::Player_YVelFrac': 192})
            random=rotate(random);c.update+=1
            assert choose(c)['start'] and lua.globals().SMB3_UPGRADE_STATE.rng.jump_steps is None
        memory.update(GamePauseStatus=129, GamePauseTimer=43)
        random=rotate(random);c.update+=1
        assert not choose(c)['start']
        q=lua.globals().SMB3_UPGRADE_STATE.rng
        assert q.entry_waited==2 and q.frozen.x==1242 and q.frozen.yfrac==192 and q.jump_steps==9
        delayed_candidate=False
        for _ in range(512):
            if memory['GamePauseTimer']:
                memory['GamePauseTimer']-=1
            else:
                memory['GamePauseStatus'] &= 127
            random=rotate(random);c.update+=1
            pad=choose(c)
            if pad['start']:
                assert pad['a'] and memory['GamePauseTimer']==0 and memory['GamePauseStatus']==1
                if not delayed_candidate:
                    delayed_candidate=True
                    continue  # No new peripheral poll: cached neutral remains.
                if not q.canceled:
                    continue  # Refresh until a later LFSR draw cancels it.
                poll_pad=lua.globals().SMB3_UPGRADE_POLL(c)
                assert poll_pad['start'] and poll_pad['a'] and q.poll_refreshes>=1
                future=random[:]
                for _ in range(q.jump_steps):
                    future=rotate(future)
                assert future[2]==q.prediction.draw and future[2]%5+2==target
                # Exercise the actual observer's native consumer witness. Its
                # clock must be fixed at consumption, including a poll made in
                # the return window before the completed-loop count advanced.
                observer=Replay.body(targeted=True)
                consumer=observer[observer.index(" if name=='TargetPauseInput'then"):
                                  observer.index(" if name=='M3RNGRead'then")]
                q.prediction.read_before_update-=1
                memory['SavedJoypad1Bits']=144
                lua.globals().SMB3_TEST_READ=read
                accept=lua.execute('local r=SMB3_TEST_READ;local updates='+str(c.update)+
                                   ';local function state()return{}end;return function(name)\n'+consumer+'\nend')
                accept('TargetPauseInput')
                assert q.accepted.before_update==c.update and q.prediction.read_before_update==c.update+q.jump_steps-1
                memory.update(GamePauseStatus=128, GamePauseTimer=43, M3Fresh=128,
                              M3Previous=144, Player_State=1, FrameCounter=memory['FrameCounter']+1)
                random=rotate(random);c.update+=1;c.grounded=False;c.lastA=True
                assert choose(c)['a'] and q.unpaused.update==c.update
                pause_cases.append(dict(suit=suit, waited=q.waited, jump_steps=q.jump_steps,
                                        draw=future[2], stamp=0xd0+target, ignored_entry_updates=2,
                                        canceled_unpolled_choices=q.canceled,
                                        poll_refreshes=q.poll_refreshes, actual_native_consumption=True))
                break
        else:
            raise AssertionError(('Finite real-input pause selection', suit))
    return dict(scope='Typed native jump/LFSR and read-only Lua pause controls; no natural gameplay qualification',
                jump_cases=jump_cases, native_LFSR=random_cases, pause_cases=pause_cases,
                files=0, Mesen=False)


def validate(raw):
    def deny(*args, **kwargs):
        raise AssertionError('Source-only upgrades attempted files, process launch or gameplay')
    cases = []
    with patch.object(Path, 'write_bytes', deny), patch.object(Path, 'write_text', deny), \
         patch('subprocess.Popen', deny), patch.object(Current.Frames, 'frame', deny), \
         patch.object(Current.N, 'invoke', deny):
        for form in Current.FORMS:
            for route in Current.ROUTES:
                text = Replay.controller(raw, form, route)
                q = Current.bindings(raw, form, route)
                assert q['sha'] == PIN and q['character'] == 17 and q['slot'] == 16
                cases.append(dict(form=form, route=route, controller_SHA256=H(text.encode()),
                                  hooks=len(q['hooks']), ram_fields=len(q['ram'])))
            for suit in Current.TARGET_SUITS:
                text = Replay.controller(raw, form, suit=suit)
                q = Current.bindings(raw, form, suit=suit)
                assert q['target_suit'] == Current.TARGET_SUITS[suit] and q['target_stamp'] == 0xd0+q['target_suit']
                cases.append(dict(form=form, route='mushroom-suit', suit=suit,
                                  controller_SHA256=H(text.encode()), hooks=len(q['hooks']),
                                  ram_fields=len(q['ram'])))
        rejected = 0
        for wrong in (raw[:-1], raw[:100] + bytes((raw[100] ^ 1,)) + raw[101:], Current.Stock.Beans.inverse(raw)):
            try:
                Current.bindings(wrong)
            except AssertionError:
                rejected += 1
            else:
                raise AssertionError('Wrong ROM accepted by strict32 upgrade adapter')
    return dict(passed=True, ROM_SHA256=PIN, cases=cases, strict_rejections=rejected,
                prediction_components=prediction_checks(raw),
                files=0, emulator=False, actual_natural_upgrades_verified=False)


def native(raw, forms, route, mode, suits=None):
    before = check(ROM)
    assert H(raw) == PIN == before['ROM_sha256'] and not before['matching_patch_files']
    candidate, script = OUT / 'candidate.nes', OUT / 'controller.lua'
    assert {p.name for p in OUT.iterdir()} == {'candidate.nes', 'controller.lua'}
    assert candidate.read_bytes() == raw
    Storage.preflight(private_root=OUT, reserved_bytes=0, reserved_files=0, fresh=True)
    preflight(OUT / 'capture', reserved_files=0)
    require_free_workspace(R, ROM, allow_interactive=True)
    previous = script.read_bytes()
    try:
        for form, suit in ((form, suit) for form in forms for suit in (suits or (None,))):
            script.write_bytes(Replay.controller(raw, form, route, mode=mode, suit=suit).encode())
            result = run(script, ROM, OUT / 'capture', PIN, 180)
            assert not result['images'] and result['outputs_written'] == 0
            receipt = result['receipt']
            summary = {key: receipt.get(key) for key in (
                'passed', 'reason', 'form', 'route', 'difficulty', 'physical_frames',
                'updates', 'movement_updates', 'items', 'head', 'phase', 'counts',
                'pending_returns', 'terminal', 'tail', 'logical_item_policy',
                'requested_suit', 'requested_stamp',
            )}
            summary['completed_checkpoints'] = [key for key, q in receipt.get('items', {}).items() if q.get('after')]
            summary.update(receipt_SHA256=result['receipt_SHA256'], script_SHA256=result['script_SHA256'])
            print('SMB3 UPGRADES ' + json.dumps(summary, separators=(',', ':')), flush=True)
            assert ROM.read_bytes() == raw and check(ROM) == before
            if not result['passed']:
                return 1
    finally:
        script.write_bytes(previous)
        assert candidate.read_bytes() == raw and ROM.read_bytes() == raw and check(ROM) == before
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--validate', action='store_true')
    action.add_argument('--run', action='store_true', help='Root-only explicit shared Mesen queue')
    parser.add_argument('--form', choices=(*Current.FORMS, 'both'), default='both')
    parser.add_argument('--route', choices=Current.ROUTES, default='mushroom-suit')
    parser.add_argument('--mode', choices=('easy', 'hard'), default='easy')
    parser.add_argument('--suit', choices=tuple(Current.TARGET_SUITS), action='append',
                        help='Naturally target this suit; repeat to run several suits sequentially per form')
    args = parser.parse_args()
    raw = ROM.read_bytes()
    if args.suit and args.route != 'mushroom-suit':
        parser.error('--suit requires --route mushroom-suit')
    if not args.run:
        print('SMB3 UPGRADE SOURCE ' + json.dumps(validate(raw), separators=(',', ':')), flush=True)
        assert ROM.read_bytes() == raw
        return 0
    forms = tuple(Current.FORMS) if args.form == 'both' else (args.form,)
    return native(raw, forms, args.route, args.mode, args.suit)


if __name__ == '__main__':
    raise SystemExit(main())
