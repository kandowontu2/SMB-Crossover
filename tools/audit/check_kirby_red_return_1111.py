"""Direct CPU evidence for the installed red shell turn and ledge contact."""
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

import prepare_kirby_contacts_current_1108_v1 as Authority


N = Authority.N
R = Authority.R
PIN = '8c1ebb1bfbe21499461c5fd65ea75b784460ac2cb81a712a9db9941aa7cec711'
JAY_SUCCESSOR = '6cb828b3c97bd287f5fb3421e01a478319bf3615e5f2eeed8a6b7888b15c9657'
NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
RED_RECEIPT = R / 'build/kirby-red-shell-1110-v3/capture/result.json'
RED_PIN = 'aed82618f6fc0bbd7ed0a6073c1a81efe68e36f25ed4bba270f587ed34af94a7'
RED_ROM = R / 'build/mini-contact-platform-combo-native-1110/candidate.nes'
RED_ROM_PIN = 'c8bd2e2c75015b84fe7bc3c4dba5b24b87e517620ef914ff229b5d4249acbe48'
SLOT = 3


def put_slot(m, slot, **fields):
    for name, value in fields.items():
        m[Authority.address(m.bundle, name)+slot] = value


def world(m, low, high, slot=0):
    return N.get(m, low, slot)+256*N.get(m, high, slot)


def shot(m):
    return dict(x=world(m, 'KbShotX', 'KbShotPage'), y=N.get(m,'KbShotY'), age=N.get(m,'KbShotAge'),
                kind=N.get(m,'KbShotKind'), type=N.get(m,'KbShotType'), direction=N.get(m,'KbShotDir'),
                vx=(N.get(m,'KbShotVXHi')+128)%256-128, fraction=N.get(m,'KbShotVXLo'))


def enemy(m):
    return dict(x=world(m,'Enemy_X_Position','Enemy_PageLoc',SLOT), y=N.get(m,'Enemy_Y_Position',SLOT),
                state=N.get(m,'Enemy_State',SLOT), kind=N.get(m,'Enemy_ID',SLOT),
                flags=N.get(m,'Enemy_Flag',SLOT), box=N.get(m,'Enemy_BoundBoxCtrl',SLOT))


def call(m, label, *, x=0, y=0, observe=None):
    b = m.bundle
    pc = Authority.address(b, label)
    bank = (Authority.location(b, label)-16)//8192 | 128
    if 0xa000 <= pc < 0xc000:
        m.raw_page(1, bank)
        N.put(m, CurrentBank=bank)
    c = N.NesMPU(memory=m, pc=pc)
    c.x, c.y, c.p, c.sp = x,y,0x31,224
    c.stPushWord(0x5aff)
    events = Counter()
    defeat = Authority.address(b,'ShellOrBlockDefeat')
    box = Authority.address(b,'KbShellEnemyContact')
    for _ in range(12000):
        if (c.pc,c.sp)==(0x5b00,224):
            assert not m.blocked, m.blocked
            return c, events
        if c.pc == defeat:
            assert c.x == SLOT and N.get(m,'ObjectOffset') == SLOT
            events['native_defeat'] += 1
        if c.pc == box and m.rawtags[1] == 202:
            events['linked_shell_box'] += 1
        if observe:
            observe(m,c)
        assert m[c.pc], (label,hex(c.pc),m.rawtags)
        c.step()
    raise AssertionError((label,hex(c.pc),c.sp))


def prepare(current=None):
    if current is None:
        current = NIGHTLY.read_bytes()
    assert sha256(current).hexdigest() in (PIN,JAY_SUCCESSOR)
    assert Authority.sha(Authority.AUTHORITY)==Authority.AUTHORITY_ROM
    assert Authority.sha(Authority.AUTHORITY.with_suffix('.dbg'))==Authority.AUTHORITY_DBG
    source = Authority.scoped_load(Authority.AUTHORITY)
    red_parent = RED_ROM.read_bytes()
    assert sha256(red_parent).hexdigest()==RED_ROM_PIN
    for name in ('KIRBY_ABILITIES','KIRBY_GFX'):
        region, = (s for s in source['segs'].values() if s['name']==f'"{name}"')
        at,size = (int(region[key],0) for key in ('ooffs','size'))
        assert current[at:at+size]==red_parent[at:at+size]
    for name in ('KbWeapons','KbShellEnemyContact'):
        at = Authority.location(source,name)
        size = int(source['syms'][name]['size'],0)
        assert current[at:at+size]==source['raw'][at:at+size]
    start = Authority.location(source,'KbWeapons::NotArc')
    end = Authority.location(source,'KbWeapons::NotReturn')
    assert current[start:end] == bytes.fromhex('bd675cc903f0034cfba5bd5e5cc920b0034cfba5bd435cc575bd465ce55ca903b0034cf8a5a9fd9d4f5c')
    boxes_at = Authority.location(source,'BoundBoxCtrlData')
    box = tuple(current[boxes_at+12:boxes_at+16])
    assert box == (2,9,14,21)
    receipt = RED_RECEIPT.read_bytes()
    assert sha256(receipt).hexdigest()==RED_PIN
    receipt = json.loads(receipt)
    assert receipt['passed'] and receipt['shell_contact']['shell']['age']==3
    assert receipt['native_defeat_return']['target']['state']==34
    source['raw'] = current
    seed = N.fresh(source)
    N.put(seed, SelectedCharacter=13, KbVariant=0, OperMode=1, OperMode_Task=3, GameEngineSubroutine=8,
          AreaType=1, KbHealth=6, NumberofLives=2, Player_Y_HighPos=1, Player_Y_Position=160,
          ScreenLeft_PageLoc=2, ScreenLeft_X_Pos=0, NmiDisable=255, ObjectOffset=0)
    seed[0x300:0x4a0] = bytes(0x1a0)
    return seed, box


def launch(m, x, facing, copy=3):
    N.put(m,KbCopy=copy,PlayerFacingDir=facing,Player_X_Position=x&255,Player_PageLoc=x>>8)
    call(m,'KbWeapons::CopyAttack')
    p = shot(m)
    assert (p['x'],p['y'],p['age'],p['kind'],p['type'],p['vx'],p['fraction']) == (
        x+(16 if facing==1 else 0),180,0,copy,3,3 if facing==1 else -3,0)
    return p


def turns(seed):
    proof = []
    for x, facing in product((490,516),(1,2)):
        m = N.fork(seed)
        N.put(m,ScreenLeft_PageLoc=1,ScreenLeft_X_Pos=128)
        p = launch(m,x,facing)
        positions = [p['x']]
        old_vx = p['vx']
        for age in range(1,39):
            _, events = call(m,'KbWeapons::Shots')
            q = shot(m)
            wanted = old_vx if age < 32 else -old_vx
            assert (q['type'],q['age'],q['vx'],q['direction'],q['fraction'],q['x']-positions[-1]) == (
                3,age,wanted,facing,0,wanted), (x,facing,age,q,positions[-1])
            assert q['y']==180 and not events
            positions.append(q['x'])
        proof.append(dict(player=x,facing=facing,turn_age=32,age31_x=positions[31],
            age32_x=positions[32],returned_vx=-old_vx,world_page_crossing=len({p>>8 for p in positions})>1))
    assert sum(p['world_page_crossing'] for p in proof)==2
    return proof


def point(box, e, sx, sy):
    l,t,r,b = box
    return e['x']+l <= sx+7 and sx-8 <= e['x']+r and e['y']+t <= sy+7 and sy-8 <= e['y']+b


def place_enemy(m, ex, ey):
    put_slot(m,SLOT,Enemy_Flag=1,Enemy_ID=3,Enemy_State=0,Enemy_X_Position=ex&255,
        Enemy_PageLoc=ex>>8,Enemy_Y_Position=ey,Enemy_Y_HighPos=1,Enemy_BoundBoxCtrl=3,
        Enemy_Y_Speed=1,Enemy_Y_MoveForce=0)


def place_shot(m, start, vx, *, facing=None, age=5):
    facing = facing or (1 if vx>0 else 2)
    put_slot(m,0,KbShotType=3,KbShotKind=3,KbShotVXHi=vx&255,KbShotVXLo=0,KbShotFX=0,
        KbShotVYHi=0,KbShotVYLo=0,KbShotFY=0,KbShotX=start&255,KbShotPage=start>>8,KbShotY=180,
        KbShotDir=facing,KbShotAge=age)


def corners(seed,box,*,swept=False):
    proof = []
    for vx in (3,-3):
        m = N.fork(seed)
        last = 648 if vx>0 else 621
        place_enemy(m,626,150)
        place_shot(m,last-vx,vx)
        _, first = call(m,'KbWeapons::Shots')
        assert first=={'linked_shell_box':1} and shot(m)['x']==last and shot(m)['type']==3
        assert not point(box,enemy(m),last,180)
        N.put(m,ObjectOffset=SLOT)
        call(m,'MoveD_EnemyVertically',x=SLOT)
        N.put(m,ObjectOffset=0)
        assert (enemy(m)['x'],enemy(m)['y'])==(626,151)
        assert point(box,enemy(m),last,180) and not point(box,enemy(m),last+vx,180)
        before = enemy(m)
        _, second = call(m,'KbWeapons::Shots')
        assert second['linked_shell_box']==1 and second['native_defeat']==int(swept)
        assert (shot(m)['type'],enemy(m)['state']) == ((0,34) if swept else (3,0))
        proof.append(dict(vx=vx,last_shell_center=[last,180],midstep_target=before,next_shell_center=[last+vx,180],
                          sampled_defeats=second['native_defeat']))
    return proof


def endpoint_edges(seed,box):
    counts = Counter()
    for vx, sy, dx in product((3,-3),(169,170,197,198),(-6,-5,22,23)):
        m = N.fork(seed)
        # Shell Y is fixed here; move target by the equivalent relative Y.
        place_enemy(m,626,168+180-sy)
        center = 626+dx
        place_shot(m,center-vx,vx)
        before = enemy(m)
        want = point(box,before,center,180)
        _, events = call(m,'KbWeapons::Shots')
        assert events['linked_shell_box']==1 and bool(events['native_defeat'])==want, (vx,sy,dx,events)
        assert shot(m)['type']==(0 if want else 3)
        assert bool(enemy(m)['state'] & 32)==want
        counts['hit' if want else 'miss'] += 1
    assert counts['hit'] and counts['miss']
    return dict(counts)


def main():
    seed, box = prepare()
    print(json.dumps(dict(passed=True,ROM_SHA256=sha256(seed.bundle['raw']).hexdigest(),red_return=turns(seed),
        endpoint_edges=endpoint_edges(seed,box),directed_corner_misses=corners(seed,box),
        original_natural_scope='c8bd native 4-3 Start Level replay earned red copy and made an outbound age-3 hit',
        scope='Actual linked CPU with directed shot and actor starting state. No natural ledge miss or Mesen claim.',
        output_files=0),sort_keys=True),flush=True)


if __name__ == '__main__':
    main()
