"""Source-only cartridge composition and real CPU/OAM feedback checks."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import check_sonic_sms_ring_contact_1110 as Contact
import check_sonic_static_portrait_1110 as Portrait
import check_sonic_native_effects_vectors_1110 as Vectors
import prepare_sonic_sms_skin_1110 as Body
import sonic_sms_ring_feedback_1110 as Feedback

Live = Contact.Live
R, N, W = Live.R, Live.N, Live.W
digest = lambda data: sha256(data).hexdigest()


def proposal():
    installed, base, common, before, receipt = Contact.proposal()
    assert receipt['image_SHA256'] == 'dcd1640b95bce9e35a44e3e29f5fd945a52b9a6fcb07e1417b0d185326f08fc6'
    bundle = Live.C.Current.W.bundle(base)
    art_preimage = Live.Alias.page_bytes(base, Feedback.ART_PAGE)
    extra_preimage = Live.Alias.page_bytes(base, Feedback.CODE_PAGE)
    rom = Contact.Donor.DONOR.read_bytes()
    assert Feedback.DONOR_PIN == Contact.Donor.PIN == Body.SMS_PIN == digest(rom)
    old_atlas, _ = Body.atlas(rom)
    assert art_preimage == old_atlas[:1024]
    assert extra_preimage == Live.Alias.page_bytes(base, 320)
    alias = json.loads(Live.RESERVATION.read_text())['mandatory_atomic_source_change']
    assert base[574138:574165] == bytes.fromhex(alias['new_hex'])
    p = Feedback.build(before, bundle, art_preimage, rom)
    old, q = (item['packet'] for item in (before, p))
    image = bytearray(base)
    allowed = set()
    for row, page in enumerate(old['code_pages']):
        at = Live.CHR + page * 1024
        data = slice(row*1024, (row+1)*1024)
        assert base[at:at+1024] == old['kernel'][data]
        image[at:at+1024] = q['kernel'][data]
        allowed.update(range(at, at+1024))
    for at, data, expected in (
            (Live.META, q['metadata'], old['metadata']), (Live.COOKIE, q['cookie'], old['cookie']),
            (Live.CHR+Feedback.ART_PAGE*1024, q['ring_art'], art_preimage),
            (Live.CHR+Feedback.CODE_PAGE*1024, q['ring_feedback'], extra_preimage)):
        assert base[at:at+len(expected)] == expected
        image[at:at+len(data)] = data
        allowed.update(range(at, at+len(data)))
    diff = Contact.differences(base, image)
    assert diff <= allowed
    assert all(Live.Alias.page_bytes(image, page) == Live.Alias.page_bytes(base, page)
               for page in (319, 320, 329, 331, 332, 333, 335))
    assert q['ring_extension'] == old['ring_extension'] and q['kernel'][:5526] == old['kernel'][:5526]
    assert all(image[i] == base[i] for i in range(Contact.DK.COOKIE_AT, Contact.DK.COOKIE_AT+16))
    return installed, base, bytes(image), common, p, dict(parent=Contact.PIN, image_SHA256=digest(image),
        contact_preimage=receipt['image_SHA256'], feedback_code_bytes=p['feedback_program']['used']['RING_FEEDBACK'],
        visual_art_SHA256=digest(q['ring_art']), code_page_preimage_SHA256=digest(extra_preimage),
        code_page_SHA256=digest(q['ring_feedback']), cookie=q['cookie'].hex(), changed_bytes=len(diff),
        art_page=Feedback.ART_PAGE, code_page=Feedback.CODE_PAGE, placement=p['feedback_atlas'])


def cold(raw, image, common, p):
    q = p['packet']
    bus = Live.O.blank(Live.C.Current.W.bundle(image))
    tail = bytes(bus.ram[2][0x1c00:0x1fe0])
    first = Live.C.cold(bus, 43, common['new'])
    assert first['PPU_reads'] == 22486
    Live.Eighth.owned(bus, q)
    assert bytes(bus.ram[2][0x1400:0x1800]) == q['ring_extension']
    assert bytes(bus.ram[2][0x1800:0x1c00]) == q['ring_feedback']
    assert bytes(bus.ram[2][0x1c00:0x1fe0]) == tail
    warm = Live.Eighth.S.slim_fork(bus)
    assert Live.C.cold(warm, 43, common['new'])['PPU_reads'] == 0 and warm.ram == bus.ram
    for i in (0, 511, 1023):
        m = Live.O.blank(Live.C.Current.W.bundle(image))
        m.corrupt_at = (2, 0x1800+i)
        Live.C.cold(m, 43, common['new'], expect_success=False)
        assert Live.O.headers(m) == (bytes(16),)*2
    for owner in range(37, 43):
        a, b = (Live.O.blank(Live.C.Current.W.bundle(source)) for source in (raw, image))
        left, right = (Live.C.cold(m, owner, common['new']) for m in (a,b))
        Live.C.parity(a, b, left, right)
    return dict(reads=first['PPU_reads'], minimum_SP=first['minimum_SP'], warm_reads=0,
                fault_rejects=3, foreign_cold_pairs=6)


def ownership(base, image):
    """Actual current portrait consumers and the newly re-used fairy alias."""
    menu = Portrait.Menu.Menu
    pair = []
    for source in (base, image):
        m = menu.I.UI.seed(menu.W.bundle(source), 25)
        for _ in range(3):
            menu.I.UI.key(m, 32)
        assert menu.menu_name(m)[0] == 'SONIC'
        sprites = [tuple(m[0x200+4*i:0x204+4*i]) for i in range(64) if m[0x200+4*i] < 240]
        assert sorted(sprite[1] for sprite in sprites) == sorted(Feedback.BODY)
        Live.Alias.regular_nmi(m)
        assert m.chr_latches[0] == 224
        pair.append((sprites, tuple(m.chr_latches)))
    assert pair[0] == pair[1]
    alias_at = 574138+26
    assert base[alias_at] == image[alias_at] == (320&255)
    broken = bytearray(image)
    broken[alias_at] = 334&255
    with patch.object(Live.Alias.N, 'Bus', Live.Alias.FundingBus):
        seeds = [Live.Alias.N.fresh(menu.W.bundle(source)) for source in (base, image, bytes(broken))]
    for face in (1, 2):
        outcomes = []
        for m in [Live.Alias.slim_fork(seed) for seed in seeds]:
            Live.Alias.N.put(m, SelectedCharacter=5, Z2Variant=1, PlayerFacingDir=face,
                             NmiDisable=255, FamilyMainCommit=1)
            Live.Alias.invoke(m, 'Z2SetPose', x=26)
            Live.Alias.invoke(m, 'Z2PublishBody')
            Live.Alias.regular_nmi(m)
            assert m.table_reads == [26]
            outcomes.append((Live.Alias.normalize_state(m), tuple(m.pattern_events)))
        assert outcomes[0] == outcomes[1]
        assert any(page == 334 for _,page,_ in outcomes[2][1])
        assert all(page != 334 for _,page,_ in outcomes[1][1])
    return dict(actual_sonic_menu_sprite_pairs=4, actual_fairy_face_pairs=2, stale_334_negatives=2)


def cells(m, rotation, start, stop):
    return [tuple(m[0x200+((at+rotation)&255):0x204+((at+rotation)&255)]) for at in range(start, stop, 4)]


def hud(p, bcd):
    a = p['feedback_atlas']
    tiles = (*a['glyphs'], a['digits'][bcd>>4], a['digits'][bcd&15])
    return [(34,tile,2,208+8*i) for i, tile in enumerate(tiles)]


def draw_tests(image, common, p):
    t = Live.Public.A.T
    seed = t.install(Live.C.Current.W.bundle(image), p, common)
    t.S.scene(seed, 40, 176)
    t.S.set_native(seed, OperMode=1, OperMode_Task=3, WorldNumber=0, LevelNumber=0, AreaAddrsLOffset=5)
    assert Live.Public.public(seed, 0).p & 1
    ring = p['ring_program']['symbols']
    draws = Counter()
    for count in range(100):
        m = t.clone(seed, p)
        bcd = (count//10)*16 + count%10
        m.ram[2][ring['RingBCD']-0xc000] = bcd
        rotation = (count & 3)*16
        t.S.set_native(m, CurrentOAMOffset=0, GuestOamRotationActive=int(bool(rotation)), RgOamRotation=rotation,
                       Player_Rel_XPos=80, Player_Rel_YPos=176, PlayerFacingDir=1, Player_SprAttrib=32,
                       ScreenLeft_PageLoc=0, ScreenLeft_X_Pos=100, FrameCounter=count)
        assert Live.Public.public(m, 2).p & 1
        end = N.get(m, 'CurrentOAMOffset')
        sprites = cells(m, rotation, 0, end)
        assert sprites[:4] == [(176,0,32,84), (176,2,32,92), (192,32,32,84), (192,34,32,92)]
        assert sprites[4:8] == hud(p, bcd)
        expect = []
        for i, x in enumerate((208,224,240,256,272)):
            if (i^count)&1 == 0:
                expect.extend((167,tile,2,x-100+8*n) for n,tile in enumerate(p['feedback_atlas']['world']))
        assert sprites[8:] == expect, (count,sprites)
        draws['all_BCD_and_rotated_world_parity'] += 1
    for start in (232,236,240,244,248,252):
        m = t.clone(seed, p)
        t.S.set_native(m, CurrentOAMOffset=start, GuestOamRotationActive=1, RgOamRotation=16,
                       Player_Rel_XPos=80, Player_Rel_YPos=176, ScreenLeft_PageLoc=0, ScreenLeft_X_Pos=100)
        before = bytes(m[0x200:0x300])
        assert Live.Public.public(m, 2).p & 1
        end = N.get(m, 'CurrentOAMOffset')
        own = {((i+16)&255) for i in range(start,end)}
        assert start <= end <= 252 and all(m[0x200+i]==before[i] for i in range(256) if i not in own)
        draws['exact_OAM_capacity_and_no_wrap'] += 1
    return dict(draws)


def natural(image, p):
    s = p['feedback_program']['symbols']
    ring = p['ring_program']['symbols']
    original_frame = Live.Native.Main.frame
    counts, seen_bcd = Counter(), set()
    palettes = set()

    def frame(m, old):
        start = None
        def observe(mem, cpu):
            nonlocal start
            old(mem, cpu)
            if cpu.pc not in (s['DrawFeedback'], s['DrawDone']) or mem.rawtags[2] != 2:
                return
            rotation = N.get(mem, 'RgOamRotation') if N.get(mem, 'GuestOamRotationActive') else 0
            offset = N.get(mem, 'CurrentOAMOffset')
            if cpu.pc == s['DrawFeedback']:
                start = offset
                return
            assert start is not None and offset >= start
            sprites = cells(mem, rotation, start, offset)
            bcd = mem.ram[2][ring['RingBCD']-0xc000]
            needle = hud(p, bcd)
            if any(sprites[i:i+4] == needle for i in range(len(sprites)-3)):
                seen_bcd.add(bcd)
                counts['actual_HUD'] += 1
            if any(y==167 and attr==2 and tile in p['feedback_atlas']['world'] for y,tile,attr,x in sprites):
                counts['actual_world_ring'] += 1
            if any(tile in p['feedback_atlas']['spark'] and attr==2 for y,tile,attr,x in sprites):
                counts['actual_spark'] += 1
            if any(tile in p['feedback_atlas']['drops'] and attr==2 for y,tile,attr,x in sprites):
                counts['actual_drop'] += 1
            start = None
        original_frame(m, observe)
        if m.chr_latches[0] == Feedback.ART_PAGE:
            counts['actual_NMI_body_page'] += 1
            palettes.add(tuple(m.vram[0x3f19:0x3f1c]))

    with patch.object(Live.Native.Main, 'frame', frame):
        result = Contact.natural(image, p)
    assert all(counts[name] for name in ('actual_HUD','actual_world_ring','actual_spark','actual_drop','actual_NMI_body_page'))
    assert {0,1,2,3,4,5} <= seen_bcd and (0x16,0x30,0x27) in palettes, (seen_bcd,palettes,counts)
    return dict(counts=dict(counts), seen_BCD=sorted(seen_bcd), sprite_palettes=sorted(palettes), mechanics=result)


def vectors(image, common, p):
    """Interrupt reached raw43 render instructions, then compare OAM continuation."""
    t = Live.Public.A.T
    irq = Live.Public.L
    seed = t.install(Live.C.Current.W.bundle(image), p, common)
    t.S.scene(seed, 40, 176)
    t.S.set_native(seed, OperMode=1, OperMode_Task=3, WorldNumber=0, LevelNumber=0, AreaAddrsLOffset=5)
    assert Live.Public.public(seed, 0).p & 1
    ring = p['ring_program']['symbols']
    end = Feedback.CODE + p['feedback_program']['used']['RING_FEEDBACK']
    stop = (0x5b00,224)
    stats = Counter()
    irq.DEEPEST = None
    irq.PATHS.clear()

    def foreground(m,c):
        return (irq.regs(c), bytes(m[3:11]), bytes(m[0x15a:0x17b]),
                bytes(m[0x101+c.sp:0x200]), bytes(m[0x200:0x300]),
                tuple(bytes(bank) for bank in m.ram), tuple(m.rawtags))

    def trace(mem,cpu):
        key = (cpu.pc,cpu.sp)
        if mem.rawtags[2] != 2 or not Feedback.CODE <= cpu.pc < end or key in reached:
            return
        reached.add(key)
        for kind in ('NMI','IRQ'):
            q,d = Vectors.clone(mem,cpu)
            expected = foreground(q,d)
            assert irq.isr(q,d,kind,stop) == 'returned'
            assert foreground(q,d) == expected, (kind,hex(cpu.pc),'render interrupt changed live state')
            original,c = Vectors.clone(mem,cpu)
            irq.finish(original,c,stop)
            irq.finish(q,d,stop)
            assert foreground(original,c) == foreground(q,d), (kind,hex(cpu.pc),'OAM continuation')
            stats[kind] += 1

    with patch.object(irq,'regs',side_effect=lambda c:(c.pc,c.a,c.x,c.y,c.p&0xef,c.sp)), \
            patch.object(irq,'clone',side_effect=Vectors.clone):
        for start, rotation in ((0,224),(244,16)):
            m = t.clone(seed,p)
            t.S.set_native(m, DisableScreenFlag=0, Mirror_PPUMASK=30, NmiDisable=255,
                           CurrentOAMOffset=start, GuestOamRotationActive=1, RgOamRotation=rotation,
                           Player_Rel_XPos=80, Player_Rel_YPos=176, ScreenLeft_X_Pos=100)
            at = lambda name: ring[name]-0xc000
            m.ram[2][at('SparkX'):at('SparkX')+2] = b'\xd0\x00'
            m.ram[2][at('SparkY')] = 168
            m.ram[2][at('SparkTimer')] = 6
            drop = at('DropRecord')
            for i,value in ((0,0x55),(2,200),(5,132),(15,0x39),(17,6),(18,3)):
                m.ram[2][drop+i] = value
            reached = set()
            assert Live.Public.public(m,2,observe=trace).p & 1
        assert irq.DEEPEST is not None
        mem,cpu,entry,stop = irq.DEEPEST
        q,d = Vectors.clone(mem,cpu)
        before = foreground(q,d)
        assert irq.isr(q,d,'IRQ') == 'returned' and foreground(q,d) == before
        original,c = Vectors.clone(mem,cpu)
        for target in ((entry[0],entry[-1]),stop):
            irq.finish(original,c,target)
            irq.finish(q,d,target)
            assert foreground(original,c) == foreground(q,d)
    assert stats['NMI'] == stats['IRQ'] >= 140
    return dict(cuts=dict(stats), actual_handler_paths=dict(irq.PATHS), nested_IRQ=1,
                deepest_parent_stack=cpu.sp)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    cli.add_argument('--part', choices=('all','build','draw','natural','vectors'), default='all')
    args = cli.parse_args()
    assert args.output.resolve().is_relative_to(R/'build') and not args.output.exists()
    raw, base, image, common, p, record = proposal()
    print(json.dumps(dict(event='proposal', **record), sort_keys=True), flush=True)
    if args.part in ('all','draw'):
        print(json.dumps(dict(event='draw', **draw_tests(image, common, p)), sort_keys=True), flush=True)
        print(json.dumps(dict(event='ownership', **ownership(base, image)), sort_keys=True), flush=True)
    if args.part == 'all':
        print(json.dumps(dict(event='cold', **cold(raw, image, common, p)), sort_keys=True), flush=True)
    if args.part in ('all','natural'):
        print(json.dumps(dict(event='natural', **natural(image, p)), sort_keys=True), flush=True)
    if args.part == 'vectors':
        print(json.dumps(dict(event='vectors', **vectors(image, common, p)), sort_keys=True), flush=True)
    assert not args.output.exists()
    print(json.dumps(dict(passed=True, output_files=0)), flush=True)


if __name__ == '__main__':
    main()
