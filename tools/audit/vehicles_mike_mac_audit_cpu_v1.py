"""Bounded assembled-CPU audit. No emulator, PPU, music or campaign claims."""
from pathlib import Path
import argparse, hashlib, itertools, json, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/audit'))
from check_tmnt_render_oa import load, Memory, address
from verify_native_relocation import NesMPU
from check_tmnt_audio_fallback_oc import qualified


class TraceMemory(Memory):
    def __init__(self, bundle):
        self.pc = None
        self.trace = []
        super().__init__(bundle)

    def __setitem__(self, at, value):
        if isinstance(at, int) and self.pc is not None:
            self.trace.append(dict(pc=self.pc, bank=self.banks[(self.pc-0x8000)//8192]
                                  if self.pc >= 0x8000 else None, address=at, value=value))
        super().__setitem__(at, value)


class Arena:
    def __init__(self, bundle):
        self.b = bundle
        self.m = TraceMemory(bundle)

    def set(self, name, value, index=0):
        self.m[address(self.b, name)+index] = value & 255

    def get(self, name, index=0):
        return self.m[address(self.b, name)+index]

    def put(self, **values):
        for name, value in values.items():
            self.set(name, value)

    def call(self, name, a=0, x=0, y=0, p=0x30):
        symbol = self.b['syms'][name]
        segment = self.b['segs'][symbol['seg']]
        bank = (int(segment['ooffs'], 0)-16)//8192
        pc = address(self.b, name)
        window = (pc-0x8000)//8192
        self.m.page(window, bank)
        if window in [1, 2]:
            self.set('CurrentBank' if window == 1 else 'CurrentBankC', bank | 128)
        cpu = NesMPU(memory=self.m, pc=pc)
        cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = a, x, y, p, 0xfd
        cpu.stPushWord(0x5aff)
        self.m.trace = []
        for _ in range(100000):
            if cpu.pc == 0x5b00:
                self.m.pc = None
                assert cpu.sp == 0xfd
                return cpu
            self.m.pc = cpu.pc
            cpu.step()
        raise AssertionError((name, hex(cpu.pc), self.m.banks))


def tmnt(bundle, turtle, slot, scroll, relative, state=128):
    q = Arena(bundle)
    world = 3*256+scroll+relative
    q.put(SelectedCharacter=19, TnVariant=turtle, GameEngineSubroutine=8,
          ScreenLeft_X_Pos=scroll, ScreenLeft_PageLoc=3, ObjectOffset=slot)
    for name, value in [('TnHealth', 128)]:
        q.set(name, value, turtle)
    for name, value in [('Enemy_Flag', 1), ('Enemy_ID', 0x2e),
                        ('PowerUpType', 1), ('Enemy_X_Position', world & 255),
                        ('Enemy_PageLoc', world >> 8), ('Enemy_Y_Position', 120),
                        ('Enemy_Y_HighPos', 1), ('Enemy_State', 1)]:
        q.set(name, value, slot)
    q.set('SprObj_BoundBoxCtrl', 9, slot+1)
    q.call('TnPreparePickupDispatch', x=slot)
    assert q.get('InvPickup', slot) == 0xb4 and q.get('TnPickupStamp', slot) == 4
    q.set('Enemy_State', state, slot)
    q.call('RelativeEnemyPosition', x=slot)
    q.call('GetEnemyOffscreenBits', x=slot)
    q.call('GetEnemyBoundBox', x=slot)
    q.call('TnPickupCollisionDispatch', x=slot)
    return q


def mac(bundle, old, current, health=37, stars=3, hearts=9, area=0x25, world=0):
    q = Arena(bundle)
    q.put(SelectedCharacter=15, LmReady=0x4d, LmLife=old, NumberofLives=current,
          AreaPointer=area, LmArea=area, WorldNumber=world, LmWorld=world,
          LmHealth=health, LmStars=stars, LmHearts=hearts, LmAttack=24,
          LmSuper=1, LmPrevious=0x40, LmWalk=17)
    q.call('LmEnsure')
    return q


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    old, new = load(a.baseline), load(a.candidate)
    old_q, new_q = qualified(a.baseline), qualified(a.candidate)
    assert all(new_q.get(n) == v for n, v in old_q.items()), 'An existing qualified symbol moved'
    proof = dict(base_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),
                 candidate_ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),
                 qualified_existing_symbols_checked=len(old_q),
                 tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 passed=False, cases={},
                 scope='Actual assembled CPU routines in legal isolated RAM states. '
                       'No interrupts, PPU, natural controller pickup, music or campaign verification.')
    failures = []
    # This is a legal fully emerged full-HP flower -> Kiai reward. All prior
    # owner/type/stamp decisions execute actual reveal code, not invented IDs.
    q = tmnt(old, 0, 5, 80, 120)
    expected = [124, 124, 132, 134]
    before = [q.get('EnemyBoundingBoxCoord', 20+i) for i in range(4)]
    writes = [r for r in q.m.trace if r['address'] in [address(old, 'EnemyBoundingBoxCoord')+20,
                                                     address(old, 'EnemyBoundingBoxCoord')+22]]
    assert before != expected
    failures.append(dict(case='TMNT_Kiai_scrolled_pickup', world_x=968, screen_x=120,
                         scroll_x=80, actual_box=before, expected_box=expected,
                         first_wrong_write=writes[0], writes=writes))
    rows = []
    for turtle, slot, scroll, relative in itertools.product(
            range(4), range(6), [0,1,15,16,31,64,80,127,128,192,224,239,240,255],
            [0,1,8,32,96,120,127,128,200,239,240]):
        q = tmnt(new, turtle, slot, scroll, relative)
        got = [q.get('EnemyBoundingBoxCoord', 4*slot+i) for i in range(4)]
        want = [relative+4,124,relative+12,134]
        assert got == want, (turtle,slot,scroll,relative,got,want)
        # Execute the real SMB rectangle core, testing contact at the visible
        # item and the false old world-coordinate location separately.
        for player_x, expected_overlap in [(relative+8, True), ((relative+80+8)&255, False)]:
            for i, value in enumerate([player_x-2,120,player_x+2,136]):
                q.set('BoundingBox_UL_Corner', value, i)
            c = q.call('PlayerCollisionCore', y=4*(slot+1))
            assert bool(c.p&1) == expected_overlap, (turtle,slot,scroll,relative,player_x,got,c.p)
        rows.append(dict(turtle=turtle,slot=slot,scroll=scroll,relative=relative,box=got))
    proof['cases']['TMNT_scrolled_pickup_boxes_and_real_collision_core'] = len(rows)
    # Edge clipping is the actual native policy, including right overflow and
    # signed left-edge clipping. Fully hidden actors are excluded by the
    # existing EnemyOffscrBitsMasked guard before player contact.
    edge_rows = []
    for scroll, relative, slot in itertools.product([0,1,80,128,240,255], [-8,-4,244,248,252], range(6)):
        q = tmnt(new, 1, slot, scroll, relative)
        got = [q.get('EnemyBoundingBoxCoord',4*slot+i) for i in range(4)]
        want = [max(0,min(255,relative+4)),124,max(0,min(255,relative+12)),134]
        assert got == want, (scroll,relative,slot,got,want)
        edge_rows.append(dict(scroll=scroll,relative=relative,slot=slot,box=got))
    proof['cases']['TMNT_native_edge_clipping'] = len(edge_rows)
    # Do not collect a still-rising icon; native 48-update rise is retained.
    rise = []
    for turtle,slot in itertools.product(range(4),range(6)):
        q = tmnt(new,turtle,slot,80,120,state=1)
        q.set('Enemy_Y_Position',136,slot)
        for tick in range(48):
            q.call('TnRisePickupDispatch',x=slot)
            c=q.call('TnPickupCollisionDispatch',x=slot)
            assert bool(c.p&1)==(tick==47)
            assert q.get('TnEquipment',turtle)==q.get('TnAmmo',turtle)==0
        assert q.get('Enemy_Y_Position',slot)==120 and q.get('Enemy_State',slot)==128
        c=q.call('TnCollectEquipment',x=slot)
        assert c.p&1 and q.get('TnEquipment',turtle)==4 and q.get('TnAmmo',turtle)==20
        rise.append(dict(turtle=turtle,slot=slot,updates=48,ammo=20))
    proof['cases']['TMNT_48_update_physical_emergence_and_collection'] = len(rise)
    q=mac(old,2,3)
    assert (q.get('LmHealth'),q.get('LmStars'),q.get('LmHearts'),q.get('LmAttack'))==(96,0,20,0)
    writes=[r for r in q.m.trace if r['address']==address(old,'LmHealth')]
    failures.append(dict(case='Mac_1Up_erases_boxing_power', old_lives=2,new_lives=3,
                         before=dict(health=37,stars=3,stamina=9,attack=24),
                         after=dict(health=q.get('LmHealth'),stars=q.get('LmStars'),
                                    stamina=q.get('LmHearts'),attack=q.get('LmAttack')),
                         first_wrong_write=writes[0]))
    life_rows=[]
    for old_lives,delta,health,stars in itertools.product(range(1,99),[0,1,-1],[1,37,96],range(4)):
        current=old_lives+delta
        if not 0<=current<=99:continue
        q=mac(new,old_lives,current,health,stars)
        names=['LmHealth','LmStars','LmHearts','LmAttack','LmSuper','LmPrevious','LmWalk']
        got=[q.get(n)for n in names]
        want=[96,0,20,0,0,0,0]if delta<0 else[health,stars,9,24,1,0x40,17]
        assert got==want,(old_lives,delta,health,stars,got,want)
        assert q.get('LmLife')==current
        if delta==1:
            q.set('NumberofLives',old_lives)
            q.call('LmEnsure')
            assert(q.get('LmHealth'),q.get('LmStars'),q.get('LmAttack'))==(96,0,0)
        life_rows.append(dict(lives=old_lives,delta=delta,health=health,stars=stars))
    proof['cases']['Mac_unchanged_gain_loss_then_gain_to_death'] = len(life_rows)
    # Same-life area transition must retain persistent boxing stats but reset
    # transient moves; uninitialized new game must still establish defaults.
    for initialized,area_change in [(True,True),(False,False)]:
        q=mac(new,2,2)
        q.put(LmReady=0x4d if initialized else 0,AreaPointer=0x26 if area_change else 0x25)
        q.call('LmEnsure')
        assert(q.get('LmHealth'),q.get('LmStars'),q.get('LmHearts'),q.get('LmAttack'))==(
            (37,3,9,0)if initialized else(96,0,20,0))
    proof['cases']['Mac_area_and_new_game_controls']=2
    (a.output/'preserved-failures.json').write_text(json.dumps(failures,indent=2)+'\n')
    (a.output/'tmnt-cases.json').write_text(json.dumps(rows+edge_rows+rise,separators=(',',':'))+'\n')
    (a.output/'mac-cases.json').write_text(json.dumps(life_rows,separators=(',',':'))+'\n')
    proof['passed']=True
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(proof,indent=2))


if __name__=='__main__':
    main()
