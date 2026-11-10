"""Directed actual-native head effects; no ROM or test artifacts are written.

This is an explicit isolated CPU terrain fixture, NOT a controller route.
Both versions are loaded through the actual FF forcedblank copy/verify.
The default characterizes the frozen db20 coin regression; --require-coins
qualifies a new module's derivative against the actual native coin consumer.
"""
import argparse
from hashlib import sha256
import importlib
import json
from pathlib import Path

import check_ff_white_mushroom_current_1110 as W

N = W.N


def cold(raw):
    b = W.Symbols.bundle()
    b['raw'] = raw
    m = N.fresh(b)
    N.put(m, SelectedCharacter=22, OperMode=1, Mirror_PPUMASK=0,
          DisableScreenFlag=1, NmiDisable=255)
    before = m.ppu_reads
    result = N.invoke(m, 'FwLoad')
    assert result['P'] & 1 and m.ppu_reads-before == 16400
    N.invoke(m, 'FwEnsure')
    return m


def native(seed, tile, y):
    m = N.fork(seed)
    for at in range(0x300, 0x4a0):
        m[at] = 0
    N.put(m, SelectedCharacter=22, DisableScreenFlag=0, Mirror_PPUMASK=24,
          GameEngineSubroutine=8, GamePauseStatus=0, TimerControl=0,
          DisableCollisionDet=0, Player_X_Position=0xb2, Player_PageLoc=8,
          Player_Y_Position=y, Player_Y_HighPos=1, Player_Y_Speed=255,
          Player_State=1, PlayerSize=0, CrouchingFlag=0, RgCrouch=0,
          SwimmingFlag=0, AreaType=1, PlayerFacingDir=1, BlockBounceTimer=0,
          GuestHurtTicks=0, CoinTallyFor1Ups=0, Square2SoundQueue=0)
    frame = W.address(m.bundle, 'FfRenderBuffer')
    m[frame+2], m[frame+8], m[frame+9] = 160, 0xb1, 8
    cell = 0x300+7*16+12
    m[cell] = tile
    result = N.invoke(m, 'PlayerBGCollision', a=83, x=71, y=0, p=0x31)
    return dict(y=N.get(m, 'Player_Y_Position'), vy=N.get(m, 'Player_Y_Speed'),
                x=N.get(m, 'Player_X_Position')+256*N.get(m, 'Player_PageLoc'),
                coins=N.get(m, 'CoinTallyFor1Ups'), cell=m[cell],
                sound=N.get(m, 'Square2SoundQueue'), state=N.get(m, 'Player_State'),
                head_flags=m[frame], AXYP=[result[k] for k in ('A','X','Y','P')])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--module', default='check_ff_head_corner_1110')
    p.add_argument('--require-coins', action='store_true')
    args = p.parse_args()
    fix = importlib.import_module(args.module)
    original = W.ROM.read_bytes()
    assert sha256(original).hexdigest() == W.PIN
    trial, _, cookie, _, _, _ = fix.proposal(original)
    old, new = cold(original), cold(trial)
    rows, missing = [], []
    for tile in (0xc2, 0xc3, 0x23, 0x61):
        for y in (150,151,152,153):
            a, b = native(old, tile, y), native(new, tile, y)
            assert a['y'] == 154
            if tile in (0xc2,0xc3):
                assert (a['coins'],a['cell'],a['sound']) == (1,0,1)
                if args.require_coins:
                    assert (b['coins'],b['cell'],b['sound']) == (1,0,1), (tile,y,a,b)
                    assert b == a, ('coin callback behavior changed',tile,y,a,b)
                elif b['coins'] != 1:
                    missing.append(dict(tile=tile, y=y, before=a, after=b))
            else:
                assert (a['coins'],b['coins'],a['cell'],b['cell']) == (0,0,tile,tile)
                assert a['vy'] == 1 and b['vy'] == 255 and b['y'] == y
            rows.append(dict(tile=tile, initial_y=y, old=a, new=b))
    if not args.require_coins:
        assert sha256(trial).hexdigest() == 'db20d5a53259b90b0c0892b416e8da78aab1815a1c68fb99c4a1974ad5326069'
        assert [(r['tile'],r['y']) for r in missing] == [(194,152),(194,153),(195,152),(195,153)]
    print(json.dumps(dict(passed=True, derivative_accepted=args.require_coins,
        actual_native_callback='PlayerBGCollision, including CheckForCoinMTiles/side consumer',
        explicit_CPU_fixture_only=True, Mesen_run=False, outputs_written=0,
        candidate_SHA256=sha256(trial).hexdigest(), cookie=cookie.hex(),
        module_SHA256=sha256(Path(fix.__file__).read_bytes()).hexdigest(),
        directed_cases=len(rows), missing_coins=missing, rows=rows,
        scope='Directed native consumer regression. No natural terrain placement, gameplay route, physical rendering or other lifecycle/IRQ claim.')), flush=True)


if __name__ == '__main__':
    main()
