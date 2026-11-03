"""Pack exact original DK body/fruit/hit/point pixels into the granted rows.

Art files only, never a cartridge. Executable holes stay FF until typed cold
packing, and no native OAM reader is qualified by this art receipt alone.
"""
import json,zipfile
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
R=A.R;O=A.O;D=A.W.P.D


def main():
    donor=D.donor();pixels=donor[16400:];assert len(pixels)==8192
    packet=R/'docs/qa/checkpoints/2026-11-02/dkjr-source-core-v1'
    frozen=json.loads((packet/'manifest.json').read_text());assert A.sha((packet/'inputs.zip').read_bytes())==frozen['archive_SHA256']
    with zipfile.ZipFile(packet/'inputs.zip')as z:
        old=z.read('generated/body.chr');oldmeta=json.loads(z.read('generated/body-poses.json'))
    assert len(old)==1728 and old[:1408]==pixels[:1408]
    rows={n:bytearray([255])*1024 for n in [959,960,961]}
    rows[959][:]=pixels[:1024];rows[960][:384]=pixels[1024:1408]
    rows[960][384:576]=pixels[0x150*16:0x15c*16]
    # Source points EC3B..EC83 use actual C614..C61A first characters
    # F1,F2,5E,F3,F4,F5,F6 and the common second character F7.
    source=D.Bus();point_tiles=list(source[0xc614:0xc61b])+[0xf7];assert point_tiles==[0xf1,0xf2,0x5e,0xf3,0xf4,0xf5,0xf6,0xf7]
    for i,tile in enumerate(point_tiles):rows[960][768+32*i:800+32*i]=pixels[tile*16:(tile+1)*16]+bytes(16)
    for kind,base in enumerate([0xa4,0xa8,0xac]):rows[961][kind*64:(kind+1)*64]=pixels[base*16:(base+4)*16]
    for i,tile in enumerate(range(0x90,0x94)):rows[961][192+i*32:224+i*32]=pixels[tile*16:(tile+1)*16]+bytes(16)
    assert bytes(rows[961][:192])==old[1408:1600]and bytes(rows[961][192:320])==old[1600:]
    # Source active scene provides all3fruit kinds and their real BG palettes.
    active,_=D.active();m=active.memory;p=m[0x91]+256*m[0x92];seen={};samples=[]
    for i in range(m[p]//7):
        x,y,base=m[p+1+7*i:p+4+7*i];kind=(base-0xa4)//4;tx,ty=x//8,y//8
        attr=m.ppu[0x23c0+(ty//4)*8+tx//4];pal=(attr>>((ty&2)*2+(tx&2)))&3
        rgb=list(m.ppu[0x3f01+4*pal:0x3f04+4*pal]);tile=m.ppu[0x2000+ty*32+tx]
        assert tile==0x50+4*kind and rgb==([48,42,22]if kind==0 else[42,23,55])
        seen[kind]=rgb;samples.append(dict(kind=kind,source_record_PC=p+1+7*i,x=x,y=y,actual_original_BG_top_left_tile=tile,actual_original_BG_palette=pal,opaque_RGB=rgb))
    assert set(seen)=={0,1,2}
    domains=dict(body=dict(row959=[0,1024],row960=[0,384],native_even_tiles=list(range(0,88,2))),hanging=dict(row960=[384,576],native_even_tiles=list(range(88,100,2)),original_BG_tiles=[0x150,0x15c]),points=dict(row960=[768,1024],native_even_tiles=list(range(112,128,2)),original_tiles=point_tiles),falling=dict(row961=[0,192],native_even_tiles=list(range(128,140,2))),hit=dict(row961=[192,320],native_even_tiles=list(range(140,148,2))))
    # Every legal 8x16 selection maps completely inside typed art ranges.
    selections=[]
    for role,domain in domains.items():
        for tile in domain['native_even_tiles']:
            page=[959,960,961,961][tile//64];offset=(tile&63)*16
            key='row'+str(page);assert domain[key][0]<=offset and offset+32<=domain[key][1]
            selections.append(dict(role=role,native_tile=tile|1,physical_page=page,physical_byte_half_open=[offset,offset+32]))
    for page,data in rows.items():(O/f'native-art-{page}-v38.chr').write_bytes(data)
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,donor_SHA256=D.SHA,original_credits='Nintendo: original NES Donkey Kong Jr. World Rev1 instructions and pixels.',
        art_bytes=2176,body_bytes=1408,hanging_bytes=192,point_bytes=256,falling_bytes=192,hit_bytes=128,
        original_hanging_BG_to_native_sprite_adaptation=True,original_scene_hanging_samples=samples,typed_art_domains=domains,all_legal_8x16_selections=selections,
        executable_holes=dict(row960_cold=[606,725],row961_helpers=[320,1024]),
        scope='Original pixel packing and finite proposed reader domains only. Whole legal art pairs exclude exact code/helper holes. Native hanging-fruit representation is a BG-to-sprite adaptation using original fruit glyphs and actual original palettes; no worldfruit/native draw/controller placement has been admitted.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),packet/'manifest.json',R/'docs/qa/allocations/dkjr-private-resources-1102-v20.json']},rows={str(page):dict(bytes=len(data),SHA256=A.sha(data),path=(O/f'native-art-{page}-v38.chr').relative_to(R).as_posix())for page,data in rows.items()})
    (O/'native-atlas-v38.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','art_bytes','body_bytes','hanging_bytes','point_bytes','falling_bytes','hit_bytes']}))


if __name__=='__main__':main()
