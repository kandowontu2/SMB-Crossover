"""Private full Steve armor composition under explicit carrier bindings."""

import json
from functools import lru_cache

import check_steve_armor_lifecycle_1112 as Lifecycle
import steve_armor_art_1112 as Art
import steve_armor_packet_1113 as Packet
import steve_armor_transport_1112 as Entry
import steve_armor_wave_1113 as Wave
import audit_steve_wave_carrier_1113 as Carrier


SOURCE = Entry.ROOT/'tools/reference/steve_armor_live_1113.s'
NATIVE = Entry.ROOT/'tools/reference/steve_armor_native_1113.s'
MARKER = 0xaa
OLD_INJURY = bytes.fromhex(
    'ad045cf0034c74a18e125cad305f38e902b0034c76a1d0034c76a18d305fa93c8d045ca9018d0e5c'
    'a9048d9b07a9008d4a078d0d078d1d6f8d1c6fa9088d0501ae125c3860a9008d305fae125c4cd697')
OLD_STATUS = bytes.fromhex('ad045cf0034c99a1ad305fc90390034c99a1a9008d305f60a90160')
OLD_POSE_GUARD = bytes.fromhex('a0039820c280ade0dfc9a8d00f88c001d0f0adcfcec98ad0034ccfcea9e120c280a9dca00060')


@lru_cache(maxsize=4)
def order_blocks(rows):
    """Place complete scatter blocks within the codec's 4095-byte history."""
    def packed_size(order):
        return len(Packet.Codec.encode(b''.join(data for _, _, data in order)))

    best = list(rows)
    best_size = packed_size(best)
    for _ in range(3):
        previous_size = best_size
        origin = best
        for source in range(len(origin)):
            rest = origin[:source]+origin[source+1:]
            for destination in range(len(origin)):
                trial = rest[:destination]+[origin[source]]+rest[destination:]
                size = packed_size(trial)
                if size < best_size:
                    best, best_size = trial, size
        if best_size == previous_size:
            break
    return tuple(best)


def link(raw, *, wave=True):
    donor = Art.D.DONOR.read_bytes()
    pages, records, art_proof = Art.atlas(donor)
    bundle = Packet.Host.C.Start.W.bundle(raw)
    names = ('FrameCounter', 'Player_State', 'Player_X_Position', 'Player_PageLoc',
             'Player_Y_Position', 'Player_Y_HighPos', 'PlayerFacingDir', 'JnHurt',
             'SmPosePtr', 'ObjectMetasprite', 'GameEngineSubroutine', 'CurrentBank')
    fields = Entry.FIELDS | {name: Packet.Cold.W.address(bundle, name) for name in names}
    fields |= dict(SteveArmorWarning=0xc97a, SteveArmorEffectActor=0xc97b,
                   SteveArmorExitCount=0xc97c, SteveArmorAngleStep=0xc97d,
                   ArmorHurtAge=0xc97e, ArmorBodyPose=0xc97f)
    source = SOURCE.read_text()
    if wave:
        _, incumbent, _ = Wave.incumbent(raw)
        fields |= {name:incumbent[name] for name in (
            'SteveHitLife','SteveHitX','SteveHitPage','SteveHitY','SteveHitHigh',
            'StevePunchLives','SteveHitEnemy','SteveDrawInvoke','SteveDraw','CurrentOAMOffset',
            'NativeWaveBlockPoint','NativeWaveBlockBank','WaveProbeX','WaveProbePage','WaveProbeY',
            'NativeWaveOrdinaryHit','NativeWaveTokenOwned')}
        fields |= {name:Packet.Cold.W.address(bundle,name) for name in (
            'MetaspriteRenderLoop','X5SetSpecialChr','SprDataOffset_Ctrl','ScreenLeft_X_Pos','ScreenLeft_PageLoc',
            'Enemy_State','Enemy_Y_HighPos','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','InvPickup')}
        fields |= dict(SteveArmorEffectActor=0x5c87, ArmorWaveAge=0xc97d,
                       ArmorWaveFacing=0xc97b, WavePhysicalPage=739)
        source = source.replace('    beq ArmorDamage\n',
            '    beq ArmorDamage\n    cmp #3\n    beq ArmorWaveTick\n    cmp #4\n    beq ArmorWaveDraw\n')
        source += '\n'+Wave.SOURCE.read_text()+'\n'
    lifecycle = Lifecycle.SOURCE.read_text().replace('"ARMOR_LIFECYCLE"', '"STEVE_ARMOR_RUNTIME"')
    lifecycle = lifecycle.replace('SteveArmorExitAnimation', 'ArmorAnimate')
    lifecycle = lifecycle.replace('SteveArmorResetRobot', 'ArmorResetRobot')
    source += '\n'+lifecycle+'\n.segment "STEVE_ARMOR_RUNTIME"\n'
    for label, data in (
        ('ArmorPoseIds', Art.POSES),
        ('ArmorPageLow', [records[pose][0]&255 for pose in Art.POSES]),
        ('ArmorPageHigh', [records[pose][0]>>8 for pose in Art.POSES])):
        source += label+': .byte '+','.join(map(str, data))+'\n'
    for label, operator in (('ArmorRecordLow', '<'), ('ArmorRecordHigh', '>')):
        source += label+': .byte '+','.join(operator+f'ArmorRecord{pose:02x}' for pose in Art.POSES)+'\n'
    for pose in Art.POSES:
        source += f'ArmorRecord{pose:02x}: .byte '+','.join(map(str, records[pose][1]))+'\n'
    if wave:
        _, wave_records = Wave.art(donor)
        for label, operator in (('WaveRecordLow','<'),('WaveRecordHigh','>')):
            source += label+': .byte '+','.join(operator+f'WaveRecord{index}' for index in range(3))+'\n'
        for index,pose in enumerate(Wave.POSES):
            source += f'WaveRecord{index}: .byte '+','.join(map(str,wave_records[pose][0]))+'\n'
    program = Packet.assemble(Entry.bindings(fields)+source,
                              {'STEVE_ARMOR_RUNTIME': (0xa000, 2048),
                               'STEVE_ARMOR_BRIDGE': (0xcd00, 136),
                               'STEVE_ARMOR_GATE': (0xc3bf, 60),
                               'STEVE_ARMOR_RECOVERY': (0xda4d, 37)})
    return program, pages, records, art_proof


def native_edits(raw, runtime):
    bundle = Packet.Host.C.Start.W.bundle(raw)
    names = ('JnSavedX', 'JnHealth', 'JnHurt', 'JnUiDirty', 'InjuryTimer',
             'TimerControl', 'PlayerChangeSizeFlag', 'GuestHurtTicks',
             'GuestHurtKind', 'Square1SoundQueue', 'KillPlayer', 'CurrentBankC')
    fields = {name: Packet.Cold.W.address(bundle, name) for name in names}
    fields |= dict(ArmorCookieMarker=MARKER,
                   ArmorDamageGateway=runtime['symbols']['ArmorDamageGateway'])
    native = Packet.assemble(Entry.bindings(fields)+NATIVE.read_text(),
                              {'STEVE_ARMOR_INJURY': (0xa131, 80),
                               'STEVE_ARMOR_STATUS': (0xa181, 27),
                               'STEVE_ARMOR_AUTH': (0xbfdf, 33),
                               'STEVE_ARMOR_MAP_CALL': (0xbfe6, 26)})
    assert native['used']['STEVE_ARMOR_INJURY'] == 80
    assert native['used']['STEVE_ARMOR_AUTH'] == 33
    assert native['used']['STEVE_ARMOR_MAP_CALL'] == 26
    prg8 = json.loads((Entry.ROOT/'docs/qa/allocations/steve-native-prg8-1113.json').read_bytes())
    assert Entry.digest(raw[16+8*8192:16+9*8192]) == prg8['bank_SHA256']
    endpoint = bytes.fromhex('2078bf90034c3ebbad02608d6a01a9908d6c01a9a28d6d01a98a4c5a01')
    at = Entry.prg(5, 0xbfc2)
    assert raw[at:at+29] == endpoint
    changes = []
    for bank, address, old, segment in (
        (96, 0xa131, OLD_INJURY, 'STEVE_ARMOR_INJURY'),
        (96, 0xa181, OLD_STATUS, 'STEVE_ARMOR_STATUS'),
        (5, 0xbfdf, bytes([255])*33, 'STEVE_ARMOR_AUTH'),
        (8, 0xbfe6, bytes([255])*26, 'STEVE_ARMOR_MAP_CALL')):
        at = Entry.prg(bank, address)
        assert raw[at:at+len(old)] == old, (bank, hex(address))
        changes.append((at, old, native['images'][segment].ljust(len(old), b'\xea')))
    at = Entry.prg(96, 0xa23f)
    assert raw[at:at+38] == OLD_POSE_GUARD
    guard = OLD_POSE_GUARD.replace(b'\xc9\xa8', b'\xc9'+bytes((MARKER,)))
    changes.append((at, OLD_POSE_GUARD, guard))
    return changes, native


def proposal(raw):
    reservation = json.loads((Entry.ROOT/'docs/qa/allocations/steve-armor-pages-1113.json').read_bytes())
    assert reservation['physical_CHR_pages'] == [8, 10, 709]
    for page in (8, 10):
        assert Entry.digest(Art.page(raw, page)) == reservation['old_pages_8_and_10_SHA256']
    assert Entry.digest(Art.page(raw, 709)) == reservation['old_page_709_SHA256']
    wave_reservation = json.loads((Entry.ROOT/'docs/qa/allocations/steve-wave-page-1113.json').read_bytes())
    assert wave_reservation['physical_CHR_pages'] == [739]
    assert Entry.digest(Art.page(raw,739)) == wave_reservation['preimage_SHA256']
    alias_image, alias_info = Carrier.proposal(raw)
    program, pages, records, art_proof = link(raw)
    resident = {bank: bytearray(data) for bank, data in Packet.original_resident(raw).items()}
    resident[2][0x1f0:0x200] = bytes(16)
    resident[2][0x3fb:0x400] = bytes(5)
    resident[2][0x97e] = 255
    symbols = program['symbols']

    def edit(bank, address, before, after):
        offset = address-0xa000 if bank == 3 else address-0xc000
        assert len(before) == len(after)
        assert resident[bank][offset:offset+len(before)] == before, (bank, hex(address))
        resident[bank][offset:offset+len(after)] = after

    old, entry = Entry.link()
    edit(2, 0xc100, old['images']['UPGRADE'], entry['images']['ARMOR_TRANSPORT'])
    edit(3, 0xab7c, bytes.fromhex('2032c1'), b'\x20'+entry['symbols']['SteveArmorTransportTick'].to_bytes(2, 'little'))
    edit(2, 0xdb0b, bytes.fromhex('ad855c'), bytes.fromhex('adf2c1'))
    old_boot = Packet.Cold.T.page(raw, 375)[0x300:0x388]
    assert Entry.digest(old_boot) == '855f5fff08090ff2e0892560bd723fe40b7b3f41deb0c515135e909246ae311a'
    edit(2, 0xcd00, old_boot, program['images']['STEVE_ARMOR_BRIDGE'].ljust(136, b'\xea'))
    edit(2, 0xced0, bytes.fromhex('48a50f'), b'\x4c'+symbols['ArmorPoseEntry'].to_bytes(2, 'little'))
    edit(2, 0xcf21, bytes.fromhex('2072da'), b'\x20'+symbols['ArmorRecoveryPage'].to_bytes(2, 'little'))
    edit(2, 0xcf30, bytes.fromhex('a201'), b'\xea\xea')
    edit(2, 0xdeb1, bytes.fromhex('207cab'), b'\x20'+symbols['ArmorMainGateway'].to_bytes(2, 'little'))
    old_first = bytes(resident[2][0xab6:0xac1])
    assert old_first == bytes.fromhex('adf4c1d0faadf6c1c90160')
    edit(2, 0xcab6, old_first, (b'\x4c'+symbols['ArmorFirstBotActive'].to_bytes(2, 'little')).ljust(11, b'\xea'))
    old_bridge = bytes(resident[2][0x1a4d:0x1a72])
    assert old_bridge[:5] == bytes.fromhex('a27fbd00d1')
    edit(2, 0xda4d, old_bridge, program['images']['STEVE_ARMOR_RECOVERY'].ljust(37, b'\xea'))
    # The replaced cold transaction no longer calls either staged bootstrap.
    # These are the ordinary writable pose buffers and the spent copy tail.
    assert resident[2][0x8c0:0x8c6] == bytes.fromhex('a20884038405')
    resident[2][0x8c0:0x900] = bytes(64)
    assert resident[2][0x4f4:0x4fb] == bytes.fromhex('a930a2ab4c2ccd')
    resident[2][0x4f4:0x500] = bytes(12)
    # The two original recovery records move their eight source cells from
    # physical307 +200 to physical10 +300. Geometry and attributes stay exact.
    for pose, address in ((0xae, 0xcdc8), (0xb2, 0xcddd)):
        offset = address-0xc000
        size = resident[2][offset]+1
        before = bytes(resident[2][offset:offset+size])
        after = bytearray(before)
        assert size == (21 if pose == 0xae else 25)
        for at in range(1, size, 4):
            assert 0x20 <= after[at] <= 0x2e and not after[at]&1
            after[at] += 0x10
        edit(2, address, before, bytes(after))
    recovery = Art.page(raw, 307)[0x200:0x300]
    assert pages[10][0x300:] == bytes(256)
    pages[10] = pages[10][:0x300]+recovery
    image = Art.aliases(alias_image, Packet.Host.C.Start.W.bundle(alias_image))
    changes, native = native_edits(raw, program)
    image = bytearray(image)
    for at, before, after in changes:
        assert image[at:at+len(before)] == before
        image[at:at+len(after)] = after
    for page, data in pages.items():
        at = Entry.CHR+page*1024
        image[at:at+1024] = data
    rows = [(bank, address, bytes(resident[bank][address-0xc000:address-0xc000+size]))
            for bank, address, size in Packet.REGIONS]
    rows.append((2, 0xc3bf, program['images']['STEVE_ARMOR_GATE']))
    _, incumbent, _ = Wave.incumbent(raw)
    wave_hooks = []
    for address,before,after in (
        (incumbent['StevePunchBirth'],b'\xbd'+incumbent['StevePunchLives'].to_bytes(2,'little')+bytes.fromhex('8d875c'),
         (b'\x20'+symbols['ArmorWaveBirth'].to_bytes(2,'little')).ljust(6,b'\xea')),
        (incumbent['SteveDraw'],bytes.fromhex('aa0dde06'),
         (b'\x4c'+symbols['ArmorWaveDrawGateway'].to_bytes(2,'little')).ljust(4,b'\xea')),
        (incumbent['SteveNoCue']+5,b'\x20'+incumbent['NativeWaveOrdinaryHit'].to_bytes(2,'little')+bytes.fromhex('ce875c'),
         (b'\x20'+symbols['ArmorWaveGateway'].to_bytes(2,'little')).ljust(6,b'\xea'))):
        offset = address-0xa000
        assert Packet.original_resident(raw)[3][offset:offset+len(before)] == before, hex(address)
        rows.append((3,address+0x2000,after))
        wave_hooks.append((address,before,after))
    helper = (1, 0xc000, program['images']['STEVE_ARMOR_RUNTIME'])
    orders = [rows[:index]+[helper]+rows[index:] for index in range(len(rows)+1)]
    rows = min(orders, key=lambda order: len(Packet.Codec.encode(b''.join(data for _, _, data in order))))
    rows = list(order_blocks(tuple(rows)))
    binding = b''.join(at.to_bytes(4, 'little')+after for at, _, after in changes)
    binding += b''.join(pages[page] for page in sorted(pages))
    binding += b''.join(row['offset'].to_bytes(4,'little')+bytes.fromhex(row['after'])
                        for row in alias_info['edits'])
    wave_art, wave_records = Wave.art(Art.D.DONOR.read_bytes())
    candidate, info = Packet.proposal(bytes(image), rows, recovery_relocated=True,
                                       marker=MARKER, binding=binding,
                                       warm_verifier=program['symbols']['ArmorVerifyRaw1'],
                                       wave_page=739,wave_art=wave_art)
    info.update(runtime=program, native=native, art=art_proof, records=records,
                native_changes=changes, wave_hooks=wave_hooks,wave_records=wave_records,
                previous_owner_alias=alias_info, release_qualified=False)
    return candidate, info


def reverse(image):
    """Restore the exact authenticated parent while retaining unrelated edits."""
    parent = bytearray(image)
    parent_cookie = image[Entry.CHR+371*1024+64:Entry.CHR+371*1024+80]
    assert parent_cookie[:3] == bytes.fromhex('a81020') and parent_cookie[3] in (10,11)
    for page, row in zip(Packet.PAGES, Packet.Preimage.original_rows(), strict=True):
        at = Entry.CHR+page*1024
        parent[at:at+1024] = row
    at = Entry.CHR+739*1024
    parent[at:at+1024] = bytes(1024)
    for page, source in ((8,2), (10,2), (709,13)):
        at = Entry.CHR+page*1024
        parent[at:at+1024] = Art.page(image, source)
    for bank in Art.Census.MAP_BANKS:
        at = Art.Census.prg_at(bank, 0xe36)
        for logical, physical in ((0x70,8), (0x78,10)):
            assert parent[at+logical] == 2
            parent[at+logical] = physical
    for bank, address, old in ((96,0xa131,OLD_INJURY), (96,0xa181,OLD_STATUS),
                               (96,0xa23f,OLD_POSE_GUARD), (5,0xbfdf,bytes([255])*33),
                               (8,0xbfe6,bytes([255])*26), (94,0xb2ef,parent_cookie)):
        at = Entry.prg(bank, address)
        parent[at:at+len(old)] = old
    old_cold = Packet.Cold.compact_cold(parent_cookie, extended=True,
                                        upgrade=Entry.U.descriptor(371))
    at = Entry.prg(65, Packet.Cold.T.COLD)
    parent[at:at+Packet.Cold.T.COLD_SIZE] = old_cold['images']['COLD65'].ljust(Packet.Cold.T.COLD_SIZE,b'\xea')
    at = Entry.prg(65, 0xaf01)
    parent[at:at+2] = old_cold['symbols']['JaySelect'].to_bytes(2,'little')
    parent = Carrier.reverse(bytes(parent))
    assert proposal(parent)[0] == image
    return parent


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wave-link',action='store_true')
    args = parser.parse_args()
    raw = Art.D.HOST.read_bytes()
    if args.wave_link:
        program = link(raw,wave=True)[0]
        print(json.dumps(dict(parent=Entry.digest(raw),segments=program['used'],
                              wave_carrier_mounted=False,output_files=0),sort_keys=True),flush=True)
        return
    candidate, info = proposal(raw)
    print(json.dumps(dict(parent=Entry.digest(raw), candidate=Entry.digest(candidate),
                          runtime_bytes=len(info['runtime']['images']['STEVE_ARMOR_RUNTIME']),
                          cold_prefix_bytes=info['prefix_bytes'], packed_bytes=info['packed_bytes'],
                          spare=info['spare'], native_injury_hook_mounted=True,
                          release_qualified=False, output_files=0), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
