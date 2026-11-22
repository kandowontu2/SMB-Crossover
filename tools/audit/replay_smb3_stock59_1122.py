"""Direct59 natural stock pickups for the four SMB3 roster variants.

Reuses the unchanged native acquisition and stock observers/controllers.
No-option execution is source-only; --run belongs to root's sequential slot.
"""

import argparse
import json

import replay_smb3_actions_1122 as Current
from check_ff_stdout_controller_source_1110 import LuaRuntime
from replay_sonic_hidden_life_f7c9_1116 import value

Acquire = Current.Acquire
Stock = Acquire.Stock
R, ROM, PIN, H, W = Current.R, Current.ROM, Current.PIN, Current.H, Current.W
ITEMS = {'mushroom': 0, 'flower': 1, '1up': 3, 'star': 2}
GROUPS = {'mario-luigi': ('mario3', 'luigi3'), 'toad-peach': ('toad3', 'peach3')}


def bindings(raw, form, item):
    assert item in ITEMS
    q = Current.bindings(raw, form, 'Fire')
    if item in ('mushroom', 'flower'):
        keep = ('GameLoop', 'M3Movement', 'M3Step', 'M3PreparePickup', 'M3CollectPickup',
                'HandlePowerUpCollision', 'PlayerHeadCollision', 'M3RisePickup',
                'M3Graphics', 'M3DrawWorld', 'M3RNGRead', 'TargetPauseInput')
        q['hooks'] = {name: q['hooks'][name] for name in keep}
        q.update(route='mushroom' if item == 'mushroom' else 'mushroom-suit', item=item,
                 stockKind=ITEMS[item], blockX=336 if item == 'mushroom' else 1248)
        return q
    b = Current.authority()
    keep = ('GameLoop', 'M3Movement', 'M3Step', 'M3PreparePickup', 'M3CollectPickup',
            'HandlePowerUpCollision', 'PlayerHeadCollision')
    q['hooks'] = {name: q['hooks'][name] for name in keep}
    def hook(owner, delta=0, size=12):
        pc, at = W.address(b, owner)+delta, W.location(b, owner)+delta
        bank = (at-16)//8192
        assert at-16 == bank*8192+(pc&8191)
        code = raw[at:at+size]
        return dict(pc=pc, tag=bank|128, offset=at-16, hex=code.hex(), bytes=list(code))
    def find(owner, pattern, limit=256):
        at = W.location(b, owner)
        hits = [i for i in range(limit-len(pattern)+1) if raw[at+i:at+i+len(pattern)] == pattern]
        assert len(hits) == 1, (owner, pattern.hex(), hits)
        return hook(owner, hits[0], len(pattern))
    lives = q['ram']['NumberofLives'].to_bytes(2, 'little')
    q['hooks']['LifeCredit'] = find('DecNumTimer', b'\xee'+lives, 48)
    q['hooks']['LifeCreditAfter'] = hook('DecNumTimer',
        q['hooks']['LifeCredit']['pc']-W.address(b, 'DecNumTimer')+3)
    star = q['ram']['StarInvincibleTimer'].to_bytes(2, 'little')
    music = q['ram']['AreaMusicQueue'].to_bytes(2, 'little')
    q['hooks']['StockStarGrant'] = find('MarioSourcePowerupCollision', b'\xa9\x23\x8d'+star+b'\xa9\x40\x8d'+music,96)
    popup = q['ram']['FloateyNum_Control'].to_bytes(2, 'little')
    q['hooks']['StockOneUpGrant'] = find('MarioSourcePowerupCollision', b'\xa9\x0b\x9d'+popup+b'\x60')
    q.update(route=item, item=item, stockKind=ITEMS[item],
             blockX=1024 if item == '1up' else 1616, blockY=128 if item == '1up' else 144)
    return q


def controller(raw, form, item):
    q = bindings(raw, form, item)
    navigation = Stock.Navigation.policy()
    if item in ('mushroom', 'flower'):
        observer = Acquire.body(targeted=item == 'flower')
        policy = Acquire.POLICY.read_text(encoding='utf-8')
        parts = ('local SMB3_UPGRADE_PROGRESS={}', 'local SMB3_UPGRADE_MODE=C.route',
                 'local SMB3_UPGRADE_TARGET='+('C.target_suit' if item == 'flower' else 'nil'),
                 'local SMB3_UPGRADE_BASE=(function()\n'+navigation+'\nend)()')
    else:
        observer = Stock.body()
        policy = Stock.POLICY.read_text(encoding='utf-8')
        parts = ('local SMB3_PICKUP_KIND=C.stockKind',
                 'local SMB3_PICKUP_BASE=(function()\n'+navigation+'\nend)()')
    text = '\n'.join(('local C='+value(q), "local ROSTER_CONFIG={name='smb3'}", *parts,
                      'local choose=(function()\n'+policy+'\nend)()', observer))
    LuaRuntime().compile(text)
    assert not any(word in text for word in ('emu.write','emu.setState','io.open','takeScreenshot','saveState','loadState','dofile'))
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true', help='Root only: existing shared sequential Mesen slot')
    parser.add_argument('--form', choices=(*Current.FORMS, *GROUPS), default='mario-luigi')
    parser.add_argument('--item', choices=tuple(ITEMS), action='append')
    args = parser.parse_args()
    forms = GROUPS.get(args.form, (args.form,))
    items = args.item or tuple(ITEMS)
    raw = ROM.read_bytes();assert H(raw) == PIN
    if not args.run:
        cases = [dict(form=form,item=item,script_SHA256=H(controller(raw,form,item).encode()))
                 for form in forms for item in items]
        print('SMB3 STOCK59 SOURCE '+json.dumps(dict(passed=True,ROM_SHA256=PIN,cases=cases,files=0,Mesen=False)),flush=True)
        return
    from capture_budget import preflight
    from mesen_session_guard_v1 import require_free_workspace
    from nightly_patch_guard_v1 import check
    from run_stdout_mesen_1110 import run
    output = Current.OUT
    before = check(ROM);assert before['ROM_sha256'] == PIN and not before['matching_patch_files']
    assert {p.name for p in output.iterdir()} == {'candidate.nes','controller.lua'}
    assert (output/'candidate.nes').read_bytes() == raw
    preflight(output/'capture',reserved_files=0);require_free_workspace(R,ROM,allow_interactive=True)
    script=output/'controller.lua';previous=script.read_bytes()
    try:
        for form in forms:
            for item in items:
                script.write_bytes(controller(raw,form,item).encode())
                result=run(script,ROM,output/'capture',PIN,180)
                assert not result['images'] and result['outputs_written']==0
                print('SMB3 STOCK59 '+json.dumps(dict(form=form,item=item,**result),separators=(',',':')),flush=True)
                assert ROM.read_bytes()==raw and check(ROM)==before
                if not result['passed']:return 1
    finally:
        script.write_bytes(previous);assert ROM.read_bytes()==raw and check(ROM)==before
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
