"""Verify the original Sonic ring hit through exact current raw43 CPU entry."""
import argparse
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from py65.devices.mpu6502 import MPU

import check_dkjr_second_pipe_lifts_1110 as DK
import check_sonic_sms_ring_live_1110 as Live
import check_sonic_sms_ring_hurt_donor_1110 as Donor
import sonic_sms_ring_contact_1110 as Contact

PIN = 'a20d254d4730583ee1f039b10abcf873559987e4f989968037a38e17427faac1'
R, N, W, Native = Live.R, Live.N, Live.W, Live.Native
digest = lambda blob: sha256(blob).hexdigest()


def differences(before, after):
    return {i for i, (a, b) in enumerate(zip(before, after, strict=True)) if a != b}


def proposal():
    original = Live.Prior.reconstruct()
    parent, _ = Live.Menu.proposal(original[0])
    assert digest(parent) == Live.PIN
    installed, dk_cookie, _ = DK.proposal(parent)
    assert digest(installed) == PIN and DK.NIGHTLY.read_bytes() == installed
    with patch.object(Live.Prior, 'reconstruct', return_value=original), \
            patch.object(Live.Menu, 'NIGHTLY', SimpleNamespace(read_bytes=lambda: parent)):
        _, ring_image, common, base, storage = Live.proposal()
    assert storage['image_SHA256'] == '1d090bb1f636db2703f97cb0ef771d6088da432d6a1c0f61292623e2fa578626'
    bundle = Live.C.Current.W.bundle(installed)
    p = Contact.build(base, bundle)
    old, q = (one['packet'] for one in (base, p))
    derivative = bytearray(ring_image)
    for row, page in enumerate(q['code_pages']):
        at = Live.CHR + 1024 * page
        part = slice(1024 * row, 1024 * (row + 1))
        assert derivative[at:at + 1024] == old['kernel'][part]
        derivative[at:at + 1024] = q['kernel'][part]
    for at, field in ((Live.META, 'metadata'), (Live.COOKIE, 'cookie'),
                      (Live.CHR + 1024 * Live.Ring.PAGE, 'ring_extension')):
        size = len(q[field])
        assert derivative[at:at + size] == old[field]
        derivative[at:at + size] = q[field]
    dk_delta = differences(parent, installed)
    sonic_delta = differences(parent, derivative)
    assert not dk_delta & sonic_delta
    image = bytearray(installed)
    for i in sonic_delta:
        image[i] = derivative[i]
    assert differences(installed, image) == sonic_delta
    assert differences(derivative, image) == dk_delta
    assert image[DK.COOKIE_AT:DK.COOKIE_AT+16] == dk_cookie
    assert all(Live.Alias.page_bytes(image, page) == Live.Alias.page_bytes(installed, page)
               for page in (319, 320, 329, 331, 332, 334, 335))
    return installed, bytes(image), common, p, dict(
        parent_SHA256=PIN, image_SHA256=digest(image), retained_DK_changes=len(dk_delta),
        disjoint_Sonic_changes=len(sonic_delta), cookie=q['cookie'].hex(),
        extension_SHA256=digest(q['ring_extension']), sites=p['ring_contact_sites'],
        new_code_bytes=p['ring_contact_program']['used']['RING_CONTACT'])


def original_drop(p, rom):
    """Compare the updated 26-byte slot and immunity with actual SMS dispatch."""
    ring = p['ring_program']['symbols']
    contact = p['ring_contact_program']['symbols']
    at, flag, scroll, tick = (contact[name] for name in ('DropRecord', 'DropFlags', 'ScrollY', 'SourceTick'))
    image = p['packet']['ring_extension']
    stop = 0x3000
    cases = []
    for sy, y in ((0, 176), (0, 8), (128, 160), (128, 360), (0, 256)):
        z = Donor.Z80(rom)
        z.position(120, y)
        z.putword(Donor.SCROLL_Y, sy)
        z.m[Donor.RINGS] = 1
        z.m[Donor.POOL] = 255
        z.call(0x35fd)
        assert z.m[Donor.POOL] == 0x55
        m = bytearray(65536)
        m[Live.Ring.CODE:Live.Ring.CODE + 1024] = image
        m[scroll:scroll+2] = sy.to_bytes(2, 'little')
        m[at:at+26] = z.m[Donor.POOL:Donor.POOL+26]
        for frame in range(1, 141):
            z.m[0xd223] = m[tick] = frame
            z.setpair('de', Donor.POOL)
            z.call(0x32c8)
            cpu = MPU(memory=m, pc=contact['DropStep'])
            cpu.stPushWord(stop-1)
            for _ in range(120):
                if cpu.pc == stop:
                    break
                cpu.step()
            else:
                raise AssertionError((hex(cpu.pc), frame))
            assert m[at:at+26] == z.m[Donor.POOL:Donor.POOL+26], (sy, y, frame,
                m[at:at+26].hex(), z.m[Donor.POOL:Donor.POOL+26].hex())
            assert m[flag] == z.m[Donor.FLAG_DROP]
            if m[at] == 255:
                break
        else:
            raise AssertionError(('Missing despawn', sy, y))
        cases.append(frame)
    assert cases == [81, 4, 101, 70, 65] and ring['ContextEnd'] - ring['RingContext'] == 56
    return dict(type55_complete_record_frames=sum(cases), despawn_updates=cases)


def typed(image, common, p):
    t = Live.Public.A.T
    seed = t.install(Live.C.Current.W.bundle(image), p, common)
    t.S.scene(seed, 64, 176)
    t.S.set_native(seed, OperMode=1, OperMode_Task=3, WorldNumber=0, LevelNumber=0, AreaAddrsLOffset=5)
    assert Live.Public.public(seed, 0).p & 1
    s = p['ring_program']['symbols']
    lo, hi = (s[name] - 0xc000 for name in ('RingContext', 'SceneEnd'))
    counts = Counter()
    for tier in (0, 1, 2):
        for field, value in (('RingBCD', 0), ('RingBCD', 5), ('HurtFlags', 0x20), ('HurtFlags', 0x40),
                             ('StarFlags', 1), ('DropFlags', 1)):
            m = t.clone(seed, p)
            t.S.set_native(m, PlayerStatus=tier)
            m.ram[2][s[field] - 0xc000] = value
            before = bytes(m.ram[2][lo:hi])
            status = Live.Public.public(m, 6)
            assert status.p & 1 and bool(status.a) == bool(value) and (status.p & 2 != 0) == (value == 0)
            assert bytes(m.ram[2][lo:hi]) == before and N.get(m, 'PlayerStatus') == tier
            counts['eligibility_independent_of_native_tier'] += 1
            if value:
                c = Live.Public.public(m, 5, x=73)
                assert c.p & 1 and c.x == 73 and N.get(m, 'PlayerStatus') == tier
                if (field, value) in (('RingBCD', 5), ('HurtFlags', 0x20)):
                    assert m.ram[2][s['RingBCD']-0xc000] == 0
                    assert m.ram[2][s['HurtFlags']-0xc000] == 0x40
                    assert m.ram[2][s['DropRecord']-0xc000] == (0x55 if field == 'RingBCD' else 0)
                    assert int.from_bytes(m.ram[2][0x20:0x23], 'little', signed=True) == -512
                    assert int.from_bytes(m.ram[2][0x60:0x63], 'little', signed=True) == -1024
                    counts['actual_public_ring_or_shield_hit'] += 1
                else:
                    assert bytes(m.ram[2][lo:hi]) == before
                    counts['actual_public_protected_repeat_no_writes'] += 1
    for field, value in (('GameEngineSubroutine', 7), ('WorldNumber', 1), ('LevelNumber', 1), ('AreaAddrsLOffset', 6)):
        m = t.clone(seed, p)
        t.S.set_native(m, **{field: value}, PlayerStatus=2)
        m.ram[2][lo] = 5
        assert Live.Public.public(m, 6).a == 2
        assert not Live.Public.public(m, 5).p & 1 and m.ram[2][lo] == 5
        counts['actual_outside_scene_native_fallback'] += 1
    for bank in (2, 3):
        for row in (5, 6):
            m = t.clone(seed, p)
            m.ram[2][lo] = 5
            m.ram[bank][0x1fe0+15] ^= 1
            before = [bytes(q) for q in m.ram]
            assert not Live.Public.public(m, row).p & 1 and [bytes(q) for q in m.ram] == before
            counts['corrupt_header_rejects'] += 1
    return dict(counts)


def natural(image, p):
    with redirect_stdout(io.StringIO()):
        opening, m = Native.Opening.run(image, p, goal_x=190)
    assert opening['passed']
    ring = p['ring_program']['symbols']
    symbols = p['ring_contact_program']['symbols']
    cookie = p['packet']['cookie']
    hits, picks, drops, visits = [], [], [], Counter()
    landed = resume = expired = None
    callbacks = {(2, symbols[n]): n for n in ('DamageStatus', 'DamageContact', 'DropStep')}
    callbacks[2, ring['RingHurt']] = 'RingHurt'
    for name in ('ForceInjury', 'KillPlayer'):
        callbacks[((W.location(m.bundle, name)-16)//8192|128, W.address(m.bundle, name))] = name

    def field(name):
        return m.ram[2][ring[name]-0xc000]

    def state():
        s = Native.state(m)
        return dict(x=s['x'], y=s['y'], tick=s['source_tick'], vx=s['vx'], vy=s['vy'],
                    engine=s['engine'], lives=s['lives'], tier=s['status'], flags=s['flags'],
                    bcd=field('RingBCD'), stun=field('HurtFlags'), drop_flags=field('DropFlags'), drop=field('DropRecord'))

    def observe(mem, cpu):
        if cpu.pc < 0x8000:
            return
        bank = mem.rawtags[(cpu.pc-0x8000)//8192]
        name = callbacks.get((bank, cpu.pc))
        if not name:
            return
        visits[name] += 1
        assert name != 'KillPlayer', state()
        if bank == 2:
            assert tuple(bytes(mem.ram[i][0x1fe0:0x1ff0]) for i in (2,3)) == (cookie,)*2
        if name == 'ForceInjury' and not hits:
            enemy = Native.actors(m)[cpu.x]
            assert enemy['id'] == 6 and enemy['flag'] == 1
            hits.append(dict(before=state(), enemy=enemy))

    for step in range(500):
        before = state()
        m.controller_pad = 0x81 if before['stun'] & 0x40 else 1
        Native.Main.frame(m, observe)
        after = state()
        assert (after['engine'], after['lives'], after['tier']) == (8, 2, 0), after
        if after['bcd'] > before['bcd']:
            picks.append([after['x'], after['bcd']])
        if hits and 'after' not in hits[0]:
            hits[0]['after'] = after
            assert (hits[0]['before']['bcd'], after['bcd'], after['vx'], after['vy'], after['stun'], after['drop']) == (
                5, 0, -512, -1024, 0x40, 0x55)
        if before['stun'] & 0x40:
            assert m.ram[2][0xa8] == 0 and not after['flags'] & 5
            if not after['stun'] & 0x40:
                assert after['flags'] & 0x80 and after['vy'] >= 0 and after['vx'] == 0
                assert (m.ram[2][0x41], m.ram[2][0x31]) == (28, 16)
                landed = after
        if after['drop_flags'] & 1 and not before['drop_flags'] & 1:
            assert after['tick'] % 8 == 0
            drops.append(after)
        if after['drop'] == 255 and expired is None:
            assert not after['drop_flags'] & 1
            expired = after
        if landed and after['x'] >= landed['x'] + 16 and resume is None:
            resume = after
        if resume and expired:
            break
    else:
        raise AssertionError((state(), visits, landed, resume, expired, hits))
    assert [bcd for _, bcd in picks] == list(range(1, 6))
    assert visits['RingHurt'] == 1 and visits['DropStep'] == 81 and len(drops) == 1
    return dict(iterations=step + 1, pickups=picks, contact=hits[0], callbacks=dict(visits),
                first_type55_update=drops[0], grounded_stun_release=landed, resumed=resume, despawned=expired)


class PoweredContact(BaseException):
    """End the frozen route after its first completed injury frame."""

    def __init__(self, memory):
        self.memory = memory


def earned_powered(image, p):
    """Reuse every frozen controller decision through the actual earned hit."""
    s = p['ring_program']['symbols']
    original_frame = Native.Main.frame
    ages, contact, counts = [], [], Counter()
    cookie = p['packet']['cookie']

    def state(m):
        current = Native.state(m)
        current.update(bcd=m.ram[2][s['RingBCD']-0xc000],
                       stun=m.ram[2][s['HurtFlags']-0xc000],
                       drop=m.ram[2][s['DropRecord']-0xc000])
        return current

    def frame(mem, observer):
        points = {((W.location(mem.bundle, name)-16)//8192|128, W.address(mem.bundle, name)): name
                  for name in ('GuestPowerupUpdate', 'ForceInjury', 'KillPlayer')}
        def read(m, cpu):
            observer(m, cpu)
            if cpu.pc < 0x8000:
                return
            tag = m.rawtags[(cpu.pc-0x8000)//8192]
            name = points.get((tag, cpu.pc))
            if name is None:
                return
            counts[name] += 1
            assert name != 'KillPlayer'
            if name == 'GuestPowerupUpdate' and N.get(m, 'GuestPowerupActive'):
                ages.append(N.get(m, 'GuestPowerupAge'))
            if name == 'ForceInjury':
                assert not contact and ages == list(range(60))
                before = state(m)
                assert before['status'] == 1 and before['bcd'] == 5 and before['lives'] == 2
                contact.append(dict(before=before, enemy=Native.actors(m)[cpu.x]))

        original_frame(mem, read)
        if contact:
            after = state(mem)
            assert (after['bcd'], after['stun'], after['status'], after['engine'], after['lives']) == (0, 0x40, 1, 8, 2)
            assert (after['vx'], after['vy']) == (-512, -1024)
            assert tuple(bytes(mem.ram[i][0x1fe0:0x1ff0]) for i in (2,3)) == (cookie,)*2
            contact[0]['after'] = after
            raise PoweredContact(mem)

    with patch.object(Native.Main, 'frame', frame), redirect_stdout(io.StringIO()):
        try:
            Native.run(image, p)
        except PoweredContact as end:
            m = end.memory
        else:
            raise AssertionError('Frozen earned route missed the explicit completed-contact boundary')
    landed = None
    kill_key = ((W.location(m.bundle, 'KillPlayer')-16)//8192|128, W.address(m.bundle, 'KillPlayer'))

    def guard(m, cpu):
        if cpu.pc >= 0x8000:
            assert (m.rawtags[(cpu.pc-0x8000)//8192], cpu.pc) != kill_key

    for tick in range(180):
        m.controller_pad = 0x81 if state(m)['stun'] & 0x40 else 1
        original_frame(m, guard)
        after = state(m)
        assert (after['status'], after['engine'], after['lives']) == (1, 8, 2)
        if not after['stun'] & 0x40 and landed is None:
            assert after['flags'] & 0x80 and after['vy'] >= 0 and after['vx'] == 0
            landed = after
        if landed and after['x'] >= landed['x'] + 16:
            return dict(earned_growth_updates=len(ages), contact=contact[0], grounded_release=landed,
                        resumed=after, post_hit_iterations=tick + 1, prefix_callbacks=dict(counts))
    raise AssertionError(('Powered source recovery bound', state(m), landed))


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    cli.add_argument('--part', choices=('all', 'natural', 'powered', 'build'), default='all')
    args = cli.parse_args()
    assert args.output.resolve().is_relative_to(R/'build') and not args.output.exists()
    raw, image, common, p, record = proposal()
    print(json.dumps(dict(event='proposal', **record), sort_keys=True), flush=True)
    if args.part == 'all':
        rom = Donor.DONOR.read_bytes()
        assert digest(rom) == Donor.PIN
        print(json.dumps(dict(event='typed_and_donor', **original_drop(p, rom), typed=typed(image, common, p)),
                         sort_keys=True), flush=True)
        print(json.dumps(dict(event='cold', **Live.cold(raw, image, common, p)), sort_keys=True), flush=True)
    if args.part in ('all', 'natural'):
        print(json.dumps(dict(event='natural', **natural(image, p)), sort_keys=True), flush=True)
    if args.part in ('all', 'powered'):
        print(json.dumps(dict(event='earned_powered', **earned_powered(image, p)), sort_keys=True), flush=True)
    assert not args.output.exists()
    print(json.dumps(dict(passed=True, output_files=0)), flush=True)


if __name__ == '__main__':
    main()
