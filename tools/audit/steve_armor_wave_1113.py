"""Source-derived armored wave art, coordinates and incumbent call bindings."""

import json

import steve_armor_art_1112 as Art
import steve_armor_packet_1113 as Packet


POSES = (0x1d6,0x1d8,0x1da)
SOURCE = Packet.Entry.ROOT/'tools/reference/steve_armor_wave_1113.s'


def art(donor):
    assert Packet.Entry.digest(donor) == Art.D.PIN
    source_start = 16+0x20000+82*1024+0x200
    cells = donor[source_start:source_start+192]
    assert len({cells[index:index+32] for index in range(0,192,32)}) == 6
    records = {}
    for pose in POSES:
        page, parts = Art.Art.Geometry.parts(donor,pose)
        assert page == 0
        shaped = []
        for facing in (0,1):
            source_page, source = Art.Art.Geometry.parts(donor,pose+facing)
            assert source_page == 0
            mapped = []
            for dy,dx,tile,attr in source:
                assert tile&1 and 0x21 <= tile <= 0x2b
                index = ((tile&254)-0x20)//2
                mapped.append((dy,dx,index*2+1,attr))
            shaped.append(Art.Art.packet(mapped))
        records[pose] = tuple(shaped)
    return cells,records


def incumbent(raw):
    bundle = Packet.Host.C.Start.W.bundle(raw)
    resident = Packet.original_resident(raw)[3]
    matches = [index for index in range(len(resident)-6)
               if resident[index:index+2] == bytes.fromhex('aa0d') and
               resident[index+4:index+6] == bytes.fromhex('2903')]
    index, = matches
    oam = int.from_bytes(resident[index+2:index+4],'little')
    assert (index+0xa000,oam) == (0xb5d2,0x06de)
    bundle = dict(bundle, syms=dict(bundle['syms']))
    bundle['syms']['CurrentOAMOffset'] = dict(val=hex(oam))
    base = Packet.Entry.U.Steve.S
    linked = base.link(bundle)
    at = linked['symbols']['OtherSteveCaller']-0xa000
    assert resident[at] == 0x4c
    movement = int.from_bytes(resident[at+1:at+3],'little')
    linked = base.link(bundle,movement_entry=movement)
    syms = linked['symbols']
    for name,count in (('StevePunchBirth',6),('SteveDraw',4),('SteveHitEnemy',12),('SteveDrawInvoke',7)):
        address = syms[name]
        segment, = (key for key,(origin,size) in base.LAYOUT.items() if origin <= address < origin+size)
        offset = address-base.LAYOUT[segment][0]
        assert resident[address-0xa000:address-0xa000+count] == linked['images'][segment][offset:offset+count], name
    at = syms['SteveNoCue']-0xa000
    assert resident[at:at+6] == bytes.fromhex('ad875cf00620')
    assert resident[at+8:at+11] == bytes.fromhex('ce875c')
    ordinary_hit = int.from_bytes(resident[at+6:at+8],'little')
    c2 = Packet.original_resident(raw)[2]
    assert ordinary_hit == 0xc2df and c2[ordinary_hit-0xc000:ordinary_hit-0xc000+3] == bytes.fromhex('a20520')
    token_owned = int.from_bytes(c2[ordinary_hit-0xc000+3:ordinary_hit-0xc000+5],'little')
    point = Packet.Cold.W.location(bundle,'Cv3BlockPoint')
    code = raw[point:point+183]
    assert code[:3] == bytes.fromhex('ad8668')
    assert code[0x12:0x15] == bytes.fromhex('ad8568')
    assert code[0x1d:0x20] == bytes.fromhex('ad8468')
    assert code[-4:] == bytes.fromhex('68aa3860')
    assert Packet.Entry.digest(code) == 'adee5ff769a0ea4fe7a1463d0ffcfc60264acb8760cd6829778b0b07e78ec196'
    special = Packet.Cold.W.location(bundle,'X5SetSpecialChr')
    assert (special-16)//8192 == 62
    syms = dict(syms, CurrentOAMOffset=oam,
                NativeWaveOrdinaryHit=ordinary_hit, NativeWaveTokenOwned=token_owned,
                NativeWaveBlockPoint=Packet.Cold.W.address(bundle,'Cv3BlockPoint'),
                NativeWaveBlockBank=((point-16)//8192)|128,
                WaveProbeX=0x6884,WaveProbePage=0x6885,WaveProbeY=0x6886)
    return linked,syms,code


if __name__ == '__main__':
    raw = Art.D.HOST.read_bytes()
    linked, symbols, block = incumbent(raw)
    cells,records = art(Art.D.DONOR.read_bytes())
    print(json.dumps(dict(parent=Packet.Entry.digest(raw),wave_art_bytes=len(cells),
                          wave_records={hex(p):[r.hex() for r in pair] for p,pair in records.items()},
                          incumbent={name:hex(symbols[name]) for name in
                                     ('StevePunchBirth','SteveDraw','SteveHitEnemy','SteveNoCue','SteveDrawInvoke',
                                      'NativeWaveBlockPoint','NativeWaveBlockBank')},
                          native_block_source_sha256=Packet.Entry.digest(block),output_files=0),sort_keys=True),flush=True)
