"""Pack all original wrestler poses; prove raster parity and measure current fit."""
from pathlib import Path
import hashlib,json,struct,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import wwf_roster_source_review_v1 as V
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
O=R/'build/wwf-roster-package-1101-v1';J=R/'build/ready76-menu-fixed-v5'
S=R/'build/wwf-roster-source-review-v1'
EXPECTED='28693c0bf61926f5bef62511b5da0b71f97543170d27d0e03e59bb5e70edf0ca'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')


def raster(cells,pages):
    out={}
    for tile,role,x,y,page in cells:
        pattern=pages[page*1024+tile*16:page*1024+tile*16+32]
        assert len(pattern)==32
        for half in range(2):
            for yy,row in enumerate(V.pixels(pattern[half*16:half*16+16])):
                for xx,value in enumerate(row):
                    if value:out[x+xx,y+half*8+yy]=(value,role)
    return out


def decode(meta,group,frame):
    start,width=meta[2+2*group:4+2*group]
    end=meta[2+2*(group+1)]if group+1<meta[0]else meta[1]
    count=end-start;assert frame<count
    at=2+meta[0]*2+2*(start+frame)
    lo,hi=meta[at:at+2];length=hi>>3;at=lo+256*(hi&7)
    page=meta[at];cells=[]
    for i in range(length):
        tile_role,x,y=meta[at+1+3*i:at+4+3*i]
        cells.append((tile_role&254,tile_role&1,x if x<128 else x-256,y if y<128 else y-256,page))
    return width,cells


def main():
    assert not(O/'source-package.json').exists();O.mkdir(exist_ok=True)
    assert sha(J/'candidate.nes')==EXPECTED
    stage=json.loads((J/'source-stage.json').read_text())
    for p,h in stage['bindings'].items():assert sha(p)==h,p
    original=V.raw();source=json.loads((S/'wrestlers.json').read_text());pages=(S/'wrestlers-pages.chr').read_bytes()
    assert len(pages)==84*1024 and source['original_ROM']==V.SHA
    chars=V.tables(original)
    for actual,saved in zip(chars,source['characters']):
        for key,value in actual.items():assert saved[key]==value,(actual['id'],key)
    package=bytearray();rows=[];pose_checks=face_checks=0
    for char in chars:
        poses=sorted((p for p in source['poses']if p['character']==char['id']),key=lambda p:(p['group'],p['frame']))
        groups=len(char['groups']);head=2+2*groups+2*len(poses)
        meta=bytearray([groups,len(poses)]);start=0
        for group in range(groups):
            members=[p for p in poses if p['group']==group]
            assert 1<=len(members)<=16 and start<256
            widths={p['width']for p in members};assert len(widths)==1
            meta.extend([start,widths.pop()]);start+=len(members)
        records=bytearray();directory=bytearray()
        for p in poses:
            cells=p['packed_8x16_cells'];offset=head+len(records)
            assert offset<2048 and 0<len(cells)<32
            directory.extend([offset&255,(offset>>8)|(len(cells)<<3)])
            records.append(p['packed_page'])
            for c in cells:
                assert c['page_tile']&1==0 and c['role']in[0,1]
                records.extend([c['page_tile']|c['role'],c['x']&255,c['y']&255])
        meta.extend(directory);meta.extend(records);assert len(meta)<=1687
        bank=original[char['bank']*32768:(char['bank']+1)*32768]
        for p in poses:
            # Execute the actual donor renderer for every legal group/frame.
            bus=V.Bus(bank);bus.m[0x6d]=p['group'];bus.m[0x6e]=p['frame'];V.call(bus,0x8003,char['selector'])
            expected={}
            for i,part in reversed(list(enumerate(p['parts']))):
                at=part['source_address']-0x8000;pattern=bank[at:at+16]
                assert bytes(bus.m[0x200+i*16:0x210+i*16])==pattern
                assert bus.m[0x340+i*3:0x343+i*3]==[(-part['y'])&255,part['x']&255,part['attribute_low_bit']]
                for yy,row in enumerate(V.pixels(pattern)):
                    for xx,value in enumerate(row):
                        if value:expected[part['x']+xx,part['y']+yy]=(value,part['attribute_low_bit'])
            width,cells=decode(meta,p['group'],p['frame'])
            actual=raster(cells,pages);assert actual==expected and width==p['width']
            # The existing host's facing transform must retain every pixel/role.
            flipped={(width-1-x,y):v for(x,y),v in actual.items()}
            assert flipped=={(width-1-x,y):v for(x,y),v in expected.items()}
            pose_checks+=1;face_checks+=2
        offset=len(package);package.extend(meta);package.extend(bytes(16))
        rows.append(dict(id=char['id'],name=char['name'],theme=char['theme'],groups=groups,poses=len(poses),metadata_bytes=len(meta),package_offset=offset,cookie_offset=offset+len(meta),cookie_bytes_reserved=16,
                         palette=char['palette'],alternate_palette=char['alternate_palette']))
    assert pose_checks==195 and len(package)==8182
    (O/'body-pages.chr').write_bytes(pages)
    (O/'metadata-and-cookie-slots.bin').write_bytes(package)
    # Source spans are not yet relocated audio code and are never executable
    # host templates. Execute the original entry points to establish the oracle.
    spans=[(0x8018,0x88d7),(0xe222,0xe960),(0xe960,0xf83c)]
    bank=original[2*32768:3*32768];audio=b''.join(bank[a-0x8000:z-0x8000]for a,z in spans)
    assert len(audio)==7897;(O/'audio-original-spans.bin').write_bytes(audio)
    music=[]
    for char in chars:
        bus=V.Bus(bank);V.call(bus,0xe22e);bus.m[1]=char['theme'];init=V.call(bus,0xe249)
        digest=hashlib.sha256();costs=[];writes=0
        for frame in range(1200):
            bus.apu=[];costs.append(V.call(bus,0xe4de));writes+=len(bus.apu)
            for a,v in bus.apu:digest.update(struct.pack('<IHB',frame,a,v))
        reads={a for a in bus.reads if a>=0x8000}
        assert all(any(a<=pc<z for a,z in spans)for pc in reads)
        assert all(0<=a<=8 or 0x500<=a<=0x5bf or 0x100<=a<0x200 for a in bus.writes if a<0x800)
        assert writes>100
        music.append(dict(id=char['id'],theme=char['theme'],ticks=1200,init_cycles=init,tick_cycles=[min(costs),max(costs)],APU_writes=writes,APU_trace_sha256=digest.hexdigest()))
    b=scoped_load(J/'candidate.nes');raw=b['raw']
    def selected(suffix):
        return next(p for p in(J/'sideoutputs').iterdir()if p.name.endswith(suffix)).read_bytes()
    c2=bytearray(selected('final-c2.bin'));meta_at=address(b,'WfHoganMetadata')-0xc000
    assert address(b,'WfHoganMetadataEnd')-address(b,'WfHoganMetadata')==1687
    c2[meta_at:meta_at+1687]=bytes(1687)
    c2[0x1fe0:0x1ff0]=bytes(16)
    zero_pages=[i for i in range(8)if not any(c2[i*1024:(i+1)*1024])]
    assert zero_pages==[0,1,3]
    available=[(442,460),(546,604),(629,668)]
    assert all(not any(raw[1048592+lo*1024:1048592+hi*1024])for lo,hi in[(442,460),(563,604),(655,668)])
    required=dict(body=84,metadata_and_cookie_slots=8,generic_C2_nonzero=5,generic_A3=8,audio_budget=8)
    assert sum(required.values())==113 and sum(hi-lo for lo,hi in available)==115
    footprint=dict(storage_only_fit=True,available_CHR_pages=available,available_pages=115,required_pages=required,total_required_pages=113,spare_pages=2,
                   generic_C2_zero_fill_pages=zero_pages,metadata_slot_bytes=1687,max_metadata_bytes=max(r['metadata_bytes']for r in rows),
                   resident_A_free_bytes=0xbd00-max(int(s['start'],0)+int(s['size'],0)for s in b['segs'].values()if s.get('name')in['"WF_ROM_A"','"WF_RESIDENT_PROXY"','"WF_RUNTIME_A"']),resident_C_free_bytes=0xe000-address(b,'WfResidentCEnd'),
                   qualifications=['Storage fit only; actual relocated audio and full loader/runtime still need compilation','No new host bank/RAM allocation or native playable admission','Use the current forced-blank retire/load protocol; preserve Thomas and foreign CHR exactly','Per-wrestler cookie slots are reserved zeros, not valid cache authentication'])
    save(O/'roster.json',dict(original_ROM=V.SHA,current_nightly=EXPECTED,variants=rows,pose_checks=pose_checks,facing_raster_checks=face_checks,source_theme_checks=music,
                             format='Groups: poseStart,width; count is next poseStart minus current, with total pose count ending the last group. Pose directory: offsetLow,offsetHigh3bits/cellCount5bits. Records: page, then tileEven|paletteRole,x,y per cell. Slot padding restored on cold load.',footprint=footprint))
    refs={Path(__file__),Path(V.__file__),V.ROM,S/'wrestlers.json',S/'wrestlers-pages.chr',J/'candidate.nes',J/'candidate.dbg',J/'source-stage.json'}
    refs|={p for p in O.iterdir()if p.is_file()}
    save(O/'source-package.json',dict(passed=True,source=True,native=False,installed=False,current_nightly=EXPECTED,poses=195,metadata_bytes=8182,source_audio_bytes=7897,storage_pages=113,
                                     bindings={str(p.resolve()):sha(p)for p in refs}))
    print(json.dumps(dict(passed=True,poses=pose_checks,facing_rasters=face_checks,metadata_bytes=len(package),audio_bytes=len(audio),pages_required=113,pages_available=115,playable_admission=False)))


if __name__=='__main__':main()
