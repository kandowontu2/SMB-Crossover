"""Check existing endpoint sheets against native1-2 source; extract no new epoch."""
from pathlib import Path
import gzip
import json
from PIL import Image
from current_roster_compact_11_v1 import ROOT, sha, linked
from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load
from check_tmnt_render_oa import address, location

ROM=ROOT/'build/zelda2_easy_glove.nes'
OUTPUT=ROOT/'build/current326-endpoint-question-row-v1.json'
PROFILES={
 'zelda2_current326':ROOT/'build/verification/compact-326942-zelda2-easy-v4',
 'bill_current326':ROOT/'build/verification/bill-inert-pool326-baseline-hard-ready-v1',
 'bill_private_candidate':ROOT/'build/verification/bill-landing-candidate326-hard-ready-v1',
}


def main():
    assert not OUTPUT.exists()
    assert sha(ROM)=='32694243361bb1366f6fd64c054ea2451f86b2517fc020d9c2b5d66bbf07bfa0'
    b=scoped_load(ROM);raw=b['raw'];at=lambda n:location(b,n);addr=lambda n:address(b,n)
    q=Arena(b,4);q.put(Z2Variant=1,CrossoverBehaviorVersion=0,AreaPointer=0xc0,AreaType=3,WorldNumber=0,LevelNumber=1)
    q.invoke('GetAreaDataAddrs')
    assert q.get('AreaDataLow')+256*q.get('AreaDataHigh')==addr('L_UndergroundArea1')+2
    q.array('AreaObjectLength',[255]*3);columns={}
    for col in range(18):
        q.put(CurrentPageLoc=col//16,CurrentColumnPos=col%16,BlockBufferColumnPos=col%32)
        q.invoke('AreaParserCore');columns[col]=[q.get('MetatileBuffer',r) for r in range(13)]
    assert [columns[c][7] for c in range(10,15)]==[0xc1,0xc0,0xc0,0xc0,0xc0]
    q.invoke('HpConfigure');assert q.get('HpCount')==0
    # True native helper record is a different sprite owner/tile. Do not
    # conflate visible question blocks with these native GIRDER descriptors.
    small=raw[at('MetaspritePlatformGirderSmall'):at('MetaspritePlatformGirderSmall')+17]
    assert small==bytes([16])+b''.join(bytes([0x5a,2,0,x]) for x in range(0,32,8))
    descriptor=raw[at('HpNativeInitSmallDescriptor::Descriptor'):at('HpNativeInitSmallDescriptor::Descriptor')+9]
    assert descriptor==bytes.fromhex('085a0200005a020008')
    chr_start=16+raw[4]*16384
    physical=[raw[at('ChrPhysicalMap')+addr('CHR_BG_UNDERGROUND')+i] for i in range(4)]
    background=b''.join(raw[chr_start+p*1024:chr_start+(p+1)*1024] for p in physical)
    tables=['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight']
    ids=[raw[at(n)+0xc0] for n in tables]
    assert ids==[0xa8,0xa9,0xb8,0xb9]
    assert ids==[raw[at(n)+0xc1] for n in tables]
    checked={};inputs={}
    for name,folder in PROFILES.items():
        review=json.loads((folder/'review.json').read_text());ready=json.loads((folder/'ready.json').read_text())
        placements=review['selected_whole_frames']['placements'];end=next(p for p in placements if p['name']=='endpoint')
        result=json.loads((folder/'result.json').read_text())
        assert result['passed'] and result['ROM_sha256']==ready['ROM_sha256']
        candidate=Path(next(p for p in ready['bindings']if p.endswith('.nes')))
        cr,cs,ca,cl,ch=linked(candidate);assert sha(candidate)==ready['ROM_sha256']
        cc=16+cr[4]*16384
        assert all(cr[cc+p*1024:cc+(p+1)*1024]==raw[chr_start+p*1024:chr_start+(p+1)*1024] for p in physical)
        assert all(cr[cl(n)+0xc0:cl(n)+0xc2]==raw[at(n)+0xc0:at(n)+0xc2] for n in tables)
        image=Image.open(folder/'selected-whole-frames.png').convert('RGB')
        colors={};conflicts=0;ox,oy=end['column']*256,end['row']*240
        for cell in range(5):
            for y in range(16):
                for x in range(16):
                    tile=ids[(y//8)*2+x//8];p=tile*16+y%8
                    value=((background[p]>>(7-x%8))&1)|(((background[p+8]>>(7-x%8))&1)<<1)
                    rgb=image.getpixel((ox+160+cell*16+x,oy+144+y))
                    if value in colors and colors[value]!=rgb:conflicts+=1
                    else:colors[value]=rgb
        assert conflicts==0
        checked[name]=dict(ROM_sha256=ready['ROM_sha256'],endpoint=end['source'],
            existing_sheet=str(folder/'selected-whole-frames.png'),sheet_row=end['row'],sheet_column=end['column'],
            region=[160,144,240,160],pixels_checked=1280,index_to_observed_RGB=colors,conflicts=conflicts,
            classification='Native source1-2 question-block background row; no GIRDER substitution is needed to explain these exact pixels.')
        for p in [folder/'ready.json',folder/'review.json',folder/'result.json',folder/'selected-whole-frames.png',candidate]:inputs[str(p)]=sha(p)
    for p in [ROM,ROM.with_suffix('.dbg'),ROM.with_suffix('.lbl'),Path(__file__).resolve(),
              ROOT/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',ROOT/'tools/audit/check_tmnt_render_oa.py',
              ROOT/'tools/audit/verify_native_relocation.py',ROOT/'src/metasprite.s',ROOT/'src/native_platform16.s',
              ROOT/'src/native_platform16_v2.s',ROOT/'src/crossover_helpers.s',ROOT/'src/level_tiles.s',ROOT/'src/screen_render.s']:
        inputs[str(p)]=sha(p)
    proof=dict(passed=True,scope='Narrow source/pixel explanation of existing selected endpoint row, not a whole1-2 visual or hardware-fetch qualification.',
        compiled_area=0xc0,source_area='L_UndergroundArea1',source_cells=[0xc1,0xc0,0xc0,0xc0,0xc0],
        source_cell_world_columns=[10,11,12,13,14],source_row=7,source_BG_tile_ids=ids,source_BG_physical_pages=physical,
        native_helper_count_area_C0=0,girder_record=small.hex(),native16_descriptor=descriptor.hex(),
        profiles=checked,new_extracted_epochs=0,new_images=0,bindings=inputs,
        limits=['Observed RGB is fitted to actual source pattern indices, not read from hardware palette RAM.',
                'No endpoint physical OAM/nametable/fetch trace survives in these route captures; no global platform/CHR certification.',
                'The orange five-block row is source-correct question-block artwork. Independent GIRDER art/collision behavior remains outside this check.'])
    OUTPUT.write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(proof=str(OUTPUT),sha256=sha(OUTPUT),bindings=len(inputs),existing_pixels_checked=len(checked)*1280,new_images=0),indent=2))


if __name__=='__main__':main()
