"""Read-only current Mini fireball donor/provenance; no proposed art or CPU."""
from pathlib import Path
from unittest.mock import patch
import json
import compose_mini_weapon_owner_a2_1116 as C

R,ROM,H=C.R,C.ROM,C.H
GB=Path('C:/Users/kando/Downloads/SuperMarioBrosMini.gb')
GBPIN='837d39a438f85c5b3ef32c4e41c6c4403147046a7e93bdeac039a09a4a202c81'
PINS={
 'tools/audit/prepare_mini_fireball_contract_1103.py':'e0ec815ec9fe7a6debc8582e9985dfb9de9ca06cc1eab8bdabbf6613d4d0d2f7',
 'tools/audit/prepare_mini_fireball_art_1108.py':'ff4f95fe0c779c745f249b516e27254d0f965b6d07dd02a9f9efcc994796fa34',
 'tools/audit/extract_mini_fireball_art_1108_v1.py':'58ddf5d160bf31fa1f48854026aa266ed4b016e03319037e2fe2565bdf533bc7',
 'tools/reference/mini_fireball_art_1108.s':'4c852862cb848823b28d47fb39c7dac2ff94489e0e0a8cca79aaab18f99f1822',
 'tools/reference/mini_mario_fireball_1103.s':'fece86b43bcffa05508d3ec2d25a684d3e03a88746805b29f1a7a5d75f7437d8'}
ROWS=(('A',0x10ff30,0x2e0,0x6f,'0038367e5e4c20000000380c0c000000'),
      ('B',0x10ff50,0x3e0,0x7f,'00384e1e3a3c1c00000004041c180000'),
      ('C',0x10ff70,0x3a0,0x7b,'00002418182400000000000000000000'),
      ('D',0x10ff90,0x3c0,0x7d,'24bd7ee7e77ebd240000183c3c180000'))

def decode(data):
    assert len(data)==32
    return[[((data[y//8*16+y%8]>>(7-x))&1)|(((data[y//8*16+8+y%8]>>(7-x))&1)<<1)for x in range(8)]for y in range(16)]

def bounds(data):
    points=[(x,y)for y,row in enumerate(decode(data))for x,color in enumerate(row)if color]
    return dict(opaque_pixels=len(points),half_open_XYXY=[min(x for x,y in points),min(y for x,y in points),max(x for x,y in points)+1,max(y for x,y in points)+1])

def run(owning):
    assert H(owning)==C.CANDIDATE
    for path,pin in PINS.items():assert H((R/path).read_bytes())==pin
    gbc=GB.read_bytes();assert len(gbc)==2097152 and H(gbc)==GBPIN
    code_at=1048592+962*1024;meta_at=1048592+967*1024;meta=owning[meta_at:meta_at+1024]
    payload=owning[code_at:code_at+7168];cookie=bytes.fromhex('a72901')+bytes.fromhex(H(payload))[:13]
    assert owning[536595:536611]==cookie
    rows=[]
    for name,offset,art,tile,expected in ROWS:
        source=gbc[offset:offset+16];assert gbc.find(source)==gbc.rfind(source)==offset
        assert gbc[offset-16:offset]==bytes(16)
        pixels=[[ (0,2,3,1)[((source[2*y]>>(7-x))&1)|(((source[2*y+1]>>(7-x))&1)<<1)]for x in range(8)]for y in range(8)]
        nes=bytes(sum(((pixels[y][x]>>plane)&1)<<(7-x)for x in range(8))for plane in(0,1)for y in range(8))+bytes(16)
        assert nes[:16].hex()==expected and meta[art:art+32]==nes
        row=dict(frame=name,role='moving'if name in'AB'else'impact',GBC_pair_file=offset-16,GBC_active_tile_file=offset,GBC_active_interleaved_hex=source.hex(),
            GBC_pair_SHA256=H(gbc[offset-16:offset+16]),NES_pair_SHA256=H(nes),NES_pair_hex=nes.hex(),CHR_bank=967,CHR_offset=art,
            physical_file=meta_at+art,OAM_tile=tile,blank_second_NES_tile=True,donor_palette_map=[0,2,3,1],**bounds(nes))
        rows.append(row)
    assert[rows[i]['opaque_pixels']for i in range(4)]==[23,23,8,44]
    assert all(r['half_open_XYXY']==[1,1,7,7]for r in rows[:2])
    warm=bytes.fromhex('f09090f0000000000060600000000000')+bytes(16)
    assert bounds(warm)==dict(opaque_pixels=16,half_open_XYXY=[0,0,4,4])
    old_source=(R/'tools/reference/mini_mario_fireball_1103.s').read_text()
    assert '; User-requested4x4 opaque extent, centered warm core, no resampling claim.'in old_source
    phase=(R/'tools/reference/mini_fireball_art_1108.s').read_text()
    for line in(' lda #$6f',' lda #$7f',' lda #$c2',' sbc #7',' adc #1',' sta $0201,x',' sta $0202,x',' sta $0200,x'):assert line in phase
    q=dict(passed=True,read_only=True,owning_functional_ROM_SHA256=C.CANDIDATE,GBC_path=str(GB),GBC_SHA256=GBPIN,GBC_bytes=len(gbc),
        donor_frames=rows,source_pins=PINS,old1103_adapted_warm_core=dict(pair_hex=warm.hex(),**bounds(warm),not_current_art=True),
        provenance='The1103 contract measured its deliberately adapted4x4 warmcore. The1108 builder explicitly replaced moving+impact frames with exact pinnedGBC art, documented live6x6 versus native4x4 collision, and retained animation and palette mapping. Current9826 is exact1108 donor art, not proof of current4x4 visuals.',
        metadata967=dict(file=meta_at,SHA256=H(meta),payload7168_SHA256=H(payload),code5120_SHA256=H(payload[:5120]),
            cookie_file=536595,cookie_hex=cookie.hex(),cookie_occurrences=owning.count(cookie),
            ownership='A D2E0..D300 is declared projectile art; B D3E0..D400 is physical sprite art in immutable metadata row. Cold source copies pose/restore workers from D300 then reconstructs runtime attributes over D300..D400; the physical CHR art is retained. No claim that these physical art bytes are executable slack.'),
        renderer=dict(PPUCTRL_native_observed=168,sprite_height=16,slot5=967,moving_OAM_tiles=[111,127],normal_attributes=2,flipped_attributes=194,
            source_normal_OAM_Y_offset=1,source_flipped_OAM_Y_offset=-7,source_OAM_X_offset=4,
            source_moving_opaque_world_half_open_relative_to_native=[5,3,11,9],unchanged_native_control8_edge_offsets=[6,4,10,8],
            scope='Offsets/phase rule bind retained source plus root79115 actualOAM/banks. This inspector runs no renderer or CPU.'),
        cookie_change_required_if_future_art_changes='Existing physical16B Mini cookie atPRG65:B003 derives from all7168bytes; both loaded16B headers and native observers would need the new cookie. No cookie or art replacement is proposed here.',
        preference_pending=True,proposed_art_spans=[],new_art_candidate=False,game_CPU_run=False,files=0,Mesen=False)
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**kw):raise AssertionError('Readonly donor inspection attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(C.current(ROM.read_bytes()))
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
