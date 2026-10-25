"""Bounded assembled Kirby/Meta/Chip/Dale contact and health audit.

No emulator, visual-frame, audio fidelity or campaign claims. External defeat
leaves are intercepted only to identify contact admission, not to simulate HP.
"""
from pathlib import Path
import argparse, gzip, hashlib, itertools, json
from check_tmnt_render_oa import load, Memory, address, location
from verify_native_relocation import NesMPU


def scoped(path, scope, name):
    p = path.with_suffix('.dbg')
    text = p.read_text() if p.exists() else gzip.decompress(path.with_suffix('.dbg.gz').read_bytes()).decode()
    owners = set()
    rows = []
    for line in text.splitlines():
        if not line.startswith(('scope\t', 'sym\t')):
            continue
        q = dict(v.split('=', 1) for v in line.split('\t', 1)[1].split(',') if '=' in v)
        if line.startswith('scope\t') and q.get('name') == '"'+scope+'"':
            owners.add(q['id'])
        elif line.startswith('sym\t'):
            rows.append(q)
    found = [int(q['val'], 0) for q in rows if q.get('scope') in owners and q.get('name') == '"'+name+'"' and 'val' in q]
    assert len(found) == 1, (scope, name, found)
    return found[0]


class Arena:
    def __init__(self, b, entry, values):
        self.b, self.m = b, Memory(b)
        at = address(b, entry)
        self.m.page((at-0x8000)//8192, (location(b, entry)-16)//8192)
        self.m[address(b, 'CurrentBank')] = self.m.banks[1] | 128
        self.m[address(b, 'CurrentBankC')] = self.m.banks[2] | 128
        self.put(**values)

    def get(self, name, i=0):
        return self.m[address(self.b, name)+i]

    def put(self, **values):
        for name, value in values.items():
            for i, v in enumerate(value if isinstance(value, (list, tuple)) else [value]):
                self.m[address(self.b, name)+i] = v & 255

    def run(self, entry, a=0, x=0, pc=None, traps=()):
        c = NesMPU(memory=self.m, pc=pc or address(self.b, entry))
        c.a, c.x, c.y, c.p, c.sp = a, x, 0, 0x30, 0xfd
        c.stPushWord(0x5aff)
        stops = {address(self.b, n): n for n in traps}
        self.m.writes = []
        seen, trace = [], []
        for _ in range(30000):
            if c.pc == 0x5b00:
                assert c.sp == 0xfd
                return c, seen, trace
            if c.pc in stops:
                seen.append(stops[c.pc])
                c.pc = c.stPopWord()+1
                continue
            before = len(self.m.writes)
            oldpc = c.pc
            bank = self.m.banks[(oldpc-0x8000)//8192] if oldpc >= 0x8000 else None
            c.step()
            trace.extend(dict(pc=oldpc, bank=bank, at=at, value=v) for at, v in self.m.writes[before:])
        raise AssertionError(('CPU timeout', entry, hex(c.pc), self.m.banks))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--require-page-fix', action='store_true')
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    b = load(a.rom)
    counts = dict(families=0, inhale_contacts=0, grounded_suction=0, heals=0,
                  meta_grounding=0, chip_food=0, contact_page_negatives=0)
    family_names = [('Goomba',1), ('GreenKoopa',2), ('RedKoopa',3), ('BuzzyBeetle',4),
        ('HammerBro',5), ('Bloober',6), ('GreyCheepCheep',7), ('RedCheepCheep',8),
        ('FlyingCheepCheep',8), ('GreenParatroopaJump',9), ('RedParatroopa',9),
        ('GreenParatroopaFly',9), ('Lakitu',10), ('Spiny',11), ('PiranhaPlant',12),
        ('Podoboo',13), ('BulletBill_FrenzyVar',14), ('BulletBill_CannonVar',14)]
    allowed = {address(b,n):v for n,v in family_names}
    for enemy_id, flag, state, high in itertools.product(range(256), [0, 1, 128], [0, 2, 32], [1]):
        q = Arena(b, 'KbFamilyForEnemy', dict(Enemy_Flag=[flag], Enemy_State=[state], Enemy_ID=[enemy_id], Enemy_Y_HighPos=[high]))
        c, _, _ = q.run('KbFamilyForEnemy')
        expected = allowed.get(enemy_id, 0) if flag == 1 and not state & 32 and not(enemy_id == 6 and state >= 2) else 0
        assert c.a == expected, ('family', enemy_id, flag, state, c.a, expected)
        counts['families'] += 1
    for face, dx, dy, age, held, variant in itertools.product([1, 2], [-58,-20,-8,0,8,20,58], [-13,0,13], [0,8], [0,64], [0,1]):
        enemy = 640+dx
        q = Arena(b, 'KbBodyContact', dict(KbVariant=variant, KbHurt=0, KbCopy=0, KbAction=1, KbActionAge=age,
            SavedJoypadBits=held, PlayerFacingDir=face, Player_X_Position=128, Player_PageLoc=2, Player_Y_Position=176,
            Enemy_Flag=[1], Enemy_State=[0], Enemy_ID=[6], Enemy_X_Position=[enemy&255], Enemy_PageLoc=[enemy>>8],
            Enemy_Y_Position=[184+dy], Enemy_Y_HighPos=[1]))
        c, _, _ = q.run('KbBodyContact')
        expected = variant == 0 and age == 0 and held == 64 and abs(dy) <= 12 and (0 <= (dx if face == 1 else -dx) < 57)
        assert bool(c.p&1) == expected
        counts['inhale_contacts'] += 1
    suction_pc = scoped(a.rom, 'KbWeapons', 'Suction')
    for face, dx, enemy_id in itertools.product([1,2], [16,24,40], sorted(allowed)):
        enemy = 640+(dx if face == 1 else -dx)
        q = Arena(b, 'KbWeapons', dict(PlayerFacingDir=face, Player_X_Position=128, Player_PageLoc=2,
            Player_Y_Position=176, Enemy_Flag=[1], Enemy_State=[0], Enemy_ID=[enemy_id],
            Enemy_X_Position=[enemy&255], Enemy_PageLoc=[enemy>>8], Enemy_Y_Position=[184],
            Enemy_Y_HighPos=[1], Enemy_Y_Speed=[2], Enemy_Y_MoveForce=[200], ObjectOffset=4))
        q.run('KbWeapons', pc=suction_pc)
        assert q.get('Enemy_Y_Position') == 184 and q.get('ObjectOffset') == 4
        assert q.get('Enemy_Y_Speed') == q.get('Enemy_Y_MoveForce') == 0
        counts['grounded_suction'] += 1
    for hp, kind in itertools.product(range(1,7), range(4)):
        q = Arena(b, 'KbHealPickup', dict(KbHealth=hp, KbFoodKind=0))
        c, _, _ = q.run('KbHealPickup', a=kind)
        assert q.get('KbHealth') == (min(6,hp+2) if kind < 2 else hp)
        assert bool(c.p&1) == (kind < 2)
        if kind < 2:
            assert q.get('Square2SoundQueue') != 0
        counts['heals'] += 1
    for variant, floating, mouth, copy in itertools.product([1], [0,1], [0,7], [0,14]):
        q = Arena(b, 'MkMovementInput', dict(KbVariant=variant, KbFloat=floating, KbMouth=mouth, KbCopy=copy))
        q.run('MkMovementInput')
        assert q.get('KbFloat') == q.get('KbMouth') == q.get('KbCopy') == 0
        counts['meta_grounding'] += 1
    for hp, kind, variant in itertools.product(range(1,4), range(4), [0,1]):
        q = Arena(b, 'CdCollectPickup', dict(SelectedCharacter=14, CdVariant=variant, CdHealth=hp, PowerUpType=[kind]))
        c, _, _ = q.run('CdCollectPickup')
        assert q.get('CdHealth') == ((min(3,hp+1) if kind == 0 else 3) if kind < 2 else hp)
        assert bool(c.p&1) == (kind < 2)
        counts['chip_food'] += 1
    failures = []
    contacts_pc = scoped(a.rom, 'KbWeapons', 'EnemyContacts')
    for family in ['kirby', 'chip']:
        for high in [0,1,2]:
            common = dict(SelectedCharacter=13 if family == 'kirby' else 14, ObjectOffset=4,
                Enemy_Flag=[1], Enemy_State=[0], Enemy_ID=[6], Enemy_X_Position=[100], Enemy_PageLoc=[2],
                Enemy_Y_Position=[184], Enemy_Y_HighPos=[high])
            if family == 'kirby':
                common.update(KbSavedSlot=0, KbShotType=[1], KbShotX=[100], KbShotPage=[2], KbShotY=[184])
                q = Arena(b, 'KbWeapons', common)
                _, seen, trace = q.run('KbWeapons', pc=contacts_pc, traps=['ShellOrBlockDefeat'])
            else:
                common.update(CdSlot=0, CdBoxKind=[1], CdBoxX=[100], CdBoxPage=[2], CdBoxY=[184])
                q = Arena(b, 'CdBoxEnemies', common)
                _, seen, trace = q.run('CdBoxEnemies', traps=['CdDefeatEnemy'])
            if high != 1 and seen:
                at = address(b, 'ObjectOffset')
                first = next(w for w in trace if w['at'] == at and w['value'] == 0)
                failures.append(dict(family=family, enemy_Y_HighPos=high, rejected_native_defeat=False,
                                     first_wrong_contact_owner_write=first, wrong_defeat_admission=seen))
            assert bool(seen) == (high == 1 or not a.require_page_fix), (family, high, seen)
            counts['contact_page_negatives'] += high != 1
    proof = dict(passed=not failures, bounded_components_passed=True,
        accepted=False, ROM_sha256=hashlib.sha256(b['raw']).hexdigest(),
        driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), counts=counts,
        failures=failures, scope='Assembled CPU component audit. Contact defeat leaves are intercepted at actual entries; this certifies admission, not native defeat/drop internals. No interrupt, frame, PPU, audio waveform or campaign certification.')
    (a.output/'proof.json').write_text(json.dumps(proof, indent=2)+'\n')
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
