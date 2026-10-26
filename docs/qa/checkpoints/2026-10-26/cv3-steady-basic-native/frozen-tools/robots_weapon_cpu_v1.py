"""Bounded robot inventory/transition audit of the explicitly supplied MMC5 ROM.

Actual assembled code, legal isolated RAM arenas. No emulator, interrupt, PPU,
audio-fidelity, untouched physical pickup, or campaign assertions.
"""
from pathlib import Path
import argparse, hashlib, itertools, json, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/audit'))
from check_tmnt_render_oa import load, Memory, address, location
from verify_native_relocation import NesMPU


def digest(data):
    return hashlib.sha256(data).hexdigest()


class Arena:
    def __init__(self, bundle, char=1, proto=0, roll=0):
        self.b = bundle
        self.m = Memory(bundle)
        self.put(SelectedCharacter=char, ProtoVariant=proto, RlVariant=roll,
                 CrossoverBehaviorVersion=1, PlayerStatus=1, OperMode=1,
                 GameEngineSubroutine=8, Player_Y_HighPos=1,
                 Player_X_Position=96, Player_PageLoc=1,
                 Player_Y_Position=160, PlayerFacingDir=1,
                 ScreenLeft_PageLoc=1, DisableScreenFlag=1)

    def get(self, name, i=0):
        return self.m[address(self.b, name)+i]

    def set(self, name, value, i=0):
        self.m[address(self.b, name)+i] = value

    def put(self, **values):
        for name, value in values.items():
            self.set(name, value)

    def array(self, name, values):
        for i, value in enumerate(values):
            self.set(name, value, i)

    def invoke(self, name, a=0, x=0, y=0, traps=()):
        sym = self.b['syms'][name]
        seg = self.b['segs'][sym['seg']]
        bank = (int(seg['ooffs'], 0)-16)//8192
        pc = address(self.b, name)
        window = (pc-0x8000)//8192
        self.m.page(window, bank)
        if window in (1, 2):
            self.set('CurrentBank' if window == 1 else 'CurrentBankC', bank | 128)
        self.m.writes = []
        c = NesMPU(memory=self.m, pc=pc)
        c.a, c.x, c.y, c.p, c.sp = a, x, y, 0x30, 0xfd
        c.stPushWord(0x5aff)
        trapped = {address(self.b, n): n for n in traps}
        seen = []
        for _ in range(100000):
            if c.pc == 0x5b00:
                assert c.sp == 0xfd
                return c, seen
            if c.pc in trapped:
                seen.append(trapped[c.pc])
                c.pc = (c.stPopWord()+1) & 65535
                continue
            c.step()
        raise AssertionError(('CPU timeout', name, hex(c.pc), self.m.banks))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--source-root', type=Path, default=ROOT)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    b = load(a.rom)
    source = ROOT/'reference/crossover2/extracted/scripts/com/smbc'
    manifest = {'ROM_sha256': digest(b['raw']), 'script_sha256': digest(Path(__file__).read_bytes()),
                'source_swf_sha256': digest((ROOT/'reference/crossover2/source.swf').read_bytes()),
                'source_files': {str(q.relative_to(ROOT)): digest(q.read_bytes()) for q in [
                    source/'characters/MegaMan.as', source/'characters/Bass.as',
                    source/'characters/base/MegaManBase.as', source/'characters/Character.as',
                    source/'managers/StatManager.as', source/'projectiles/MegaManProjectile.as']},
                'assembled_source_root': str(a.source_root),
                'cases': {}, 'passed': False,
                'scope': 'Assembled CPU components and static mapped CHR identity. Explicit isolated legal arenas. No interrupts, actual PPU visibility, audio parity, timed physical emergence, controller-only traversal, campaign, or hardware proof.'}
    assert manifest['source_swf_sha256'] == '6374c72426556bfc3cc16f7594ce4443a5867fe2d367514136c99cc8458b70af'
    manifest['implementation_files'] = {name: digest((a.source_root/name).read_bytes()) for name in [
        'src/inventory.s', 'src/inventory_drops.s', 'src/roll_weapons.s',
        'src/roll_core.s', 'src/roll_dispatch.s']}
    value = lambda name, i: b['raw'][location(b, name)+i]
    for char, limit, count in [(1, 8, 10), (9, 7, 8)]:
        assert value('InvItemCount', char) == count
        for item, cost in enumerate([8,4,8,4,4,4,16,12][:limit], 1):
            assert value('InvCosts', char*16+item) == cost
            assert value('InvInitialAmmo', char*16+item) == 112
            assert value('InvMaxAmmo', char*16+item) == 112
            assert value('InvSelectable', char*16+item) == 1
        assert value('InvSelectable', char*16+limit+1) == 0
    assert value('InvMushroomHi', 1) == 4 and value('InvMushroomLo', 9) == value('InvMushroomHi', 9) == 0
    manifest['cases']['source_inventory_cost_maximum_passive_tables'] = 18
    rows = []
    for char, proto in [(1, 0), (1, 1), (9, 0)]:
        limit = 8 if char == 1 else 7
        # Full, sparse, and buster-only ownership; passive items never cycle.
        for owned in [1, 1 | (1 << limit), (1 << (limit+2))-1, 1 | 4 | 32]:
            selections = [0] + [i for i in range(1, limit+1) if owned & (1 << i)]
            for selected, backward in itertools.product(selections, [False, True]):
                q = Arena(b, char, proto)
                q.set('InvOwnedLo', owned & 255, char)
                q.set('InvOwnedHi', owned >> 8, char)
                q.set('InvSelected', selected, char)
                q.put(GamePauseStatus=int(backward), InvFresh=2 if backward else 0)
                q.invoke('InventoryCycle')
                expected = selections[(selections.index(selected)+(-1 if backward else 1)) % len(selections)]
                assert q.get('InvSelected', char) == expected
                rows.append(dict(character=char, proto=proto, owned=owned, start=selected,
                                 backward=backward, selected=expected))
    manifest['cases']['cycle'] = len(rows)
    (a.output/'cycle.json').write_text(json.dumps(rows, indent=2)+'\n')

    count = 0
    for char, proto in [(1, 0), (1, 1), (9, 0)]:
        limit = 8 if char == 1 else 7
        offered = set()
        for draw in range(limit):
            q = Arena(b, char, proto)
            q.set('InvOwnedLo', 1, char)
            q.set('PseudoRandomBitReg', draw, 1)
            q.set('PowerUpType', 1, 5)
            q.invoke('InventoryPreparePickup', x=5)
            item = q.get('InvPickup', 5)
            assert 1 <= item <= limit and q.get('InvPickupOwner', 5) == char
            offered.add(item)
            count += 1
        assert offered == set(range(1, limit+1))
        for owned_item in range(1, limit+1):
            for draw in range(limit+2):
                q = Arena(b, char, proto)
                owned = 1 | (1 << owned_item)
                q.set('InvOwnedLo', owned & 255, char)
                q.set('InvOwnedHi', owned >> 8, char)
                q.set('PseudoRandomBitReg', draw, 1)
                q.set('PowerUpType', 1, 5)
                q.invoke('InventoryPreparePickup', x=5)
                assert q.get('InvPickup', 5) != owned_item
                count += 1
        q = Arena(b, char, proto)
        owned = (1 << (limit+2))-1
        if char == 1:
            owned |= 1 << 10
        q.set('InvOwnedLo', owned & 255, char)
        q.set('InvOwnedHi', owned >> 8, char)
        q.invoke('InventoryPreparePickup', x=5)
        assert q.get('InvPickup', 5) == 254
        count += 1
    manifest['cases']['native_block_offer_eligibility'] = count

    count = 0
    for char, proto in [(1, 0), (1, 1), (9, 0)]:
        for amount in [8, 40]:
            for selected, balance, expected_item in [(2, False, 2), (0, True, 3), (2, True, 3), (0, False, 0)]:
                q = Arena(b, char, proto)
                bal = 9 if char == 1 else 8
                owned = 1 | 4 | 8 | ((1 << bal) if balance else 0)
                q.set('InvOwnedLo', owned & 255, char)
                q.set('InvOwnedHi', owned >> 8, char)
                q.set('InvSelected', selected, char)
                q.array('InvAmmo', [112]*192)
                q.set('InvAmmo', 0, char*16+3)
                # Selected non-full has priority over a lower pool.
                if selected == 2 and not balance:
                    q.set('InvAmmo', 100, char*16+2)
                q.invoke('InventoryRefillAmount', a=amount)
                assert q.get('InvRefill') == (char*16+expected_item if expected_item else 0)
                if expected_item:
                    before = q.get('InvAmmo', char*16+expected_item)
                    for _ in range(3*(min(amount, 112-before)//4)):
                        q.invoke('InventoryUiTick')
                    assert q.get('InvAmmo', char*16+expected_item) == min(112, before+amount)
                    assert q.get('InvRefill') == 0 and q.get('TimerControl') == 0
                count += 1
    manifest['cases']['refill_route_and_completion'] = count

    count = 0
    for char, proto in [(1, 0), (1, 1), (9, 0)]:
        for chance, size, defeated, full in itertools.product([0, 1, 2, 3], [191, 192], [0, 0x20], [False, True]):
            q = Arena(b, char, proto)
            q.set('PseudoRandomBitReg', chance, 1)
            q.set('PseudoRandomBitReg', size, 2)
            q.set('Enemy_State', defeated, 0)
            q.set('Enemy_ID', 6, 0) # Native Goomba.
            q.set('Enemy_X_Position', 248, 0)
            q.set('Enemy_PageLoc', 1, 0)
            q.set('Enemy_Y_Position', 100, 0)
            q.array('InvDropKind', [1 if full else 0]*4)
            before = [q.get('InvDropKind', i) for i in range(4)]
            q.invoke('InventoryEnemyDrop', x=0)
            expected = chance == 0 and not defeated and not full
            if expected:
                assert q.get('InvDropKind', 3) == (1 if size < 192 else 2)
                assert q.get('InvDropX', 3) == 0 and q.get('InvDropPage', 3) == 2
                assert q.get('InvDropY', 3) == 108
            else:
                assert [q.get('InvDropKind', i) for i in range(4)] == before
            count += 1
    manifest['cases']['drop_chance_size_pool_page_carry'] = count

    # Actual clear helper must release both projectile pools and persistent locks.
    q = Arena(b)
    q.array('MmBulletType', [1, 2, 3, 6])
    q.array('RgShotType', list(range(9, 19)))
    q.put(SsHeld=1, SsKick=1, SsFreeze=10, SsBodyStop=12,
          MmChargeFrames=87, MmCharging=1)
    q.invoke('InventoryClearActive')
    assert all(q.get('MmBulletType', i) == 0 for i in range(4))
    assert all(q.get('RgShotType', i) == 0 for i in range(10))
    assert all(q.get(n) == 0 for n in ['SsHeld','SsKick','SsFreeze','SsBodyStop','MmChargeFrames','MmCharging'])
    manifest['cases']['clear_active'] = 1

    # Render data identity only: hardware visibility/palette remains native work.
    prg_bytes = b['raw'][4]*16384
    icons = []
    for item in range(1, 9):
        page = value('InvHudPhysicalBanks', item-1)
        icon = b['raw'][16+prg_bytes+page*1024+0x2a*16:16+prg_bytes+page*1024+0x2e*16]
        assert len(icon) == 64 and any(icon)
        icons.append(dict(item=item, physical_page=page, sha256=digest(icon)))
    assert len({r['sha256'] for r in icons}) == 8
    manifest['hud_icons'] = icons
    manifest['cases']['unique_hud_icons'] = 8

    count = 0
    for health, energy, kind, amount in itertools.product([1, 20, 28], [0, 20, 28], [0, 128], [8, 40]):
        q = Arena(b, 9, roll=1)
        q.put(RlHealth=health, RlEnergy=energy, InvDropSlot=3)
        q.set('AvDropItem', kind, 3)
        q.invoke('RlRefillDispatch', a=amount)
        assert q.get('RlHealth') == (min(28, health+amount//4) if kind else health)
        assert q.get('RlEnergy') == (energy if kind else min(28, energy+amount//4))
        assert q.get('InvRefill') == 0
        count += 1
    manifest['cases']['roll_independent_health_energy_capsules'] = count
    for entry, expected in [('InventorySupported', False), ('InventoryLegacyClassic', False)]:
        q = Arena(b, 9, roll=1)
        c, _ = q.invoke(entry)
        assert bool(c.p & 1) == expected
    manifest['cases']['roll_no_bass_inventory_dispatch'] = 2

    count = 0
    for facing, energy, charge, full in itertools.product([1, 2], [3, 4, 28], [59, 60], [False, True]):
        q = Arena(b, 9, roll=1)
        q.put(RlReady=82, RlLife=2, NumberofLives=2, RlArea=0, AreaPointer=0,
              RlWorld=0, WorldNumber=0, RlHealth=28, RlEnergy=energy,
              RlCharge=charge, SavedJoypadBits=64, PlayerFacingDir=facing)
        if full:
            q.array('MmBulletType', [1,1,1,3])
            q.array('MmBulletX', [100]*4)
            q.array('MmBulletPage', [1]*4)
            q.array('MmBulletY', [100]*4)
            q.array('MmBulletDir', [facing]*4)
        q.invoke('RlWeapons')
        fired = energy >= 4 and charge == 60 and not full
        assert q.get('RlChargeFired') == int(fired)
        assert q.get('RlEnergy') == energy-(4 if fired else 0)
        assert sum(q.get('MmBulletType', i) == 3 for i in range(4)) == int(full)+int(fired)
        if full and energy >= 4 and charge == 60:
            assert q.get('RlCharge') == 60
        count += 1
    manifest['cases']['roll_actual_charge_fire_payment_full_pool'] = count

    count = 0
    for facing in [1, 2]:
        q = Arena(b, 9, roll=1)
        q.put(RlReady=82, RlLife=2, NumberofLives=2, RlArea=0, AreaPointer=0,
              RlWorld=0, WorldNumber=0, RlHealth=28, RlEnergy=3,
              SavedJoypadBits=64, RlFresh=64, PlayerFacingDir=facing)
        q.array('MmBulletType', [1,1,0,1])
        q.array('MmBulletX', [100]*4)
        q.array('MmBulletPage', [1]*4)
        q.array('MmBulletY', [100]*4)
        q.array('MmBulletDir', [facing]*4)
        q.invoke('RlWeapons')
        assert sum(bool(q.get('MmBulletType', i)) for i in range(4)) == 3
        count += 1
    manifest['cases']['roll_actual_three_pellet_cap'] = count

    # Preserve the precise source mismatch as evidence without calling it a native
    # user reproduction. Source destroys only when old and new weapons differ.
    observations = []
    for char, proto in [(1, 0), (1, 1), (9, 0)]:
        q = Arena(b, char, proto)
        q.set('InvOwnedLo', 1, char)
        q.set('MmBulletType', 1, 3)
        q.put(SavedJoypad1Bits=32, InvPrevious=0)
        q.invoke('InventoryUiTick')
        observations.append(dict(character=char, proto=proto,
                                 selection=q.get('InvSelected', char),
                                 shot_before=1, shot_after=q.get('MmBulletType', 3)))
    manifest['noop_selection_observations'] = observations
    manifest['passed'] = True
    (a.output/'proof.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k not in ['source_files','hud_icons']}, indent=2))


if __name__ == '__main__':
    main()
