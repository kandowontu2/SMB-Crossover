"""Execute original Doki renderer, pack four CHR pages and prove source pixels."""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from verify_native_relocation import NesMPU
from link_pit_rygar_sophia_audit_cpu import scoped_load
from PIL import Image,ImageDraw
D=R/'build/doki-original-rebuild-1031-v1';O=R/'build/doki-original-art-1101-v1'
P=R/'build/wwf-roster-native-1101-v1/candidate.nes'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def pixels(pattern,attr):
    out={}
    for y in range(16):
        yy=15-y if attr&128 else y
        lo=pattern[(yy//8)*16+yy%8];hi=pattern[(yy//8)*16+yy%8+8]
        for x in range(8):
            bit=x if attr&64 else 7-x;value=((lo>>bit)&1)|(((hi>>bit)&1)<<1)
            if value:out[x,y]=value
    return out


def main():
    assert not(O/'source-stage.json').exists();O.mkdir(exist_ok=True)
    q=json.loads((D/'reproduction.json').read_text());files={r['name']:r for r in q['disk_files']};labels={}
    for line in(D/'assembled/original.dbg').read_text().splitlines():
        if line.startswith('sym\t'):
            row=dict(re.findall(r'(\w+)=("[^"\n]*"|[^,\n]+)',line))
            if 'val'in row:labels[row['name'].strip('"')]=int(row['val'],0)
    main=(D/'original-files/main_pro.bin').read_bytes();temp=(D/'original-files/temp_prg.bin').read_bytes()
    assert sha(D/'original-files/main_pro.bin')==files['MAIN-PRO']['sha256']
    # Original TITLE-C leaves this transparent pair in place. Later level
    # uploads stop below it, so native frameFB remains transparent.
    title=(D/'original-files/title_c.bin').read_bytes();assert title[0x1fa0:0x1fc0]==bytes(32)
    assert all(f['CPU']+f['bytes']<=0x1fa0 for f in files.values()if f['type']==1 and f['name'].startswith('BG-CHR'))
    cart=scoped_load(P);raw=cart['raw'];old_objects=raw[1048592+804*1024:1048592+805*1024]
    # Existing S2 capacity, not an un-emitted allocation.
    own=next(s for s in cart['segs'].values()if s['name']=='"SMB2_ROSTER_CHR"')
    assert int(own['start'],0)==0xc7000 and int(own['size'],0)==0x3000
    assert raw[1048592+805*1024:1048592+808*1024]==bytes(3072)
    assert not any(old_objects[96:]),'Only three original vegetable pairs are owned here'
    chars=['Imajin','Lina','Papa','Mama'];payload=bytearray();rows=[];common=None;raster_cases=0
    palptr=labels['palettes_players']-0x6000;nativeids=[0,1,3,2];palettes=[]
    for ci,name in enumerate(chars):
        f=files[name.upper()+'-C'];art=Path(f['extracted']).read_bytes();assert len(art)==832 and sha(f['extracted'])==f['sha256']
        page=bytearray(1024)
        if ci==0:page[:96]=old_objects[:96]
        page[96:928]=art;payload.extend(page);pal=list(temp[palptr+4*nativeids[ci]:palptr+4*nativeids[ci]+4]);palettes+=pal
        chrview=bytearray(title);chrview[:832]=art
        records=[]
        for action in [0,2,4,6,7,8,9,10]:
            for carry in [0,1]:
                for face in [0,1]:
                    m=bytearray(65536);m[0x6000:0xe000]=main;m[0x6000:0x65ff]=temp
                    for field,value in dict(player_screen_x=64,player_screen_y_lo=64,player_screen_y_hi=0,player_ani_frame=action,player_item_held=carry,player_dir=face,attr_player=0).items():m[labels[field]]=value
                    cpu=NesMPU(memory=m,pc=labels['player_render_gen']);cpu.sp=224;cpu.p=0x24;cpu.stPushWord(0x7ffe)
                    for _ in range(5000):
                        if cpu.pc==0x7fff:break
                        assert m[cpu.pc]!=0,('Original render BRK',hex(cpu.pc));cpu.step()
                    else:raise AssertionError('Original renderer bound')
                    packet=[16];before={};after={}
                    for part in range(4):
                        y,t,attr,x=m[labels['oam_buffer']+32+4*part:labels['oam_buffer']+36+4*part]
                        xx=x-64;yy=y-64;tile=58 if t==251 else t+6
                        assert t==251 or(t&1==0 and 0<=t<=50)
                        packet.extend([tile,attr,yy&255,xx&255])
                        offset=(t&1)*4096+(t&254)*16
                        for (px,py),value in pixels(chrview[offset:offset+32],attr).items():before[xx+px,yy+py]=value
                        for (px,py),value in pixels(page[tile*16:tile*16+32],attr).items():after[xx+px,yy+py]=value
                    assert before==after,(name,action,carry,face)
                    records.append(dict(action=action,holding=carry,facing=face,packet=packet,pixels=len(before),pixel_sha256=hashlib.sha256(json.dumps(sorted((x,y,c)for(x,y),c in before.items())).encode()).hexdigest()));raster_cases+=1
        if common is None:common=[r['packet']for r in records]
        else:assert common==[r['packet']for r in records],'Doki quartet really shares one original frame table'
        rows.append(dict(name=name,physical_page=804+ci,palette=pal,donor=f,poses=records))
    assert len(payload)==4096
    assert payload[:96]==old_objects[:96] and all(129+2*i in [129,131,133]for i in range(3))
    (O/'doki-shared-pages.chr').write_bytes(payload)
    off=labels['player_frames']-0x6000;(O/'frames.bin').write_bytes(main[off:off+44]);(O/'palettes.bin').write_bytes(bytes(palettes))
    # Small visual diagnostic, one image rather than a frame sequence.
    colors={1:'#001e74',6:'#541d07',0x30:'#eceeec',0x27:'#eca866',0x25:'#ec58b4',0x36:'#ecd0b4',0x11:'#4c9aec',0x37:'#ecd0b4'}
    img=Image.new('RGB',(8*48,4*84),'#131c29');draw=ImageDraw.Draw(img)
    for i,row in enumerate(rows):
        draw.text((3,i*84+1),row['name'],fill='white')
        for j,a in enumerate([0,2,4,6,7,8,9,10]):
            packet=next(r['packet']for r in row['poses']if r['action']==a and r['holding']==0 and r['facing']==1);page=payload[i*1024:(i+1)*1024]
            for k in range(1,len(packet),4):
                tile,attr,y,x=packet[k:k+4];y=y-256 if y>=128 else y;x=x-256 if x>=128 else x
                for (px,py),v in pixels(page[tile*16:tile*16+32],attr).items():
                    color=colors.get(row['palette'][v],'#e7b36c');draw.rectangle((j*48+6+(x+px)*2,i*84+15+(y+py)*2,j*48+7+(x+px)*2,i*84+16+(y+py)*2),fill=color)
    img.save(O/'original-poses.png')
    report=dict(passed=True,source_CPU=True,native=False,installed=False,original_renderer_cases=raster_cases,CHR_pages=[804,805,806,807],shared_existing_object_bytes=96,previously_zero_pages_in_existing_S2_segment=3,additional_allocated_CHR_pages=0,body_tile_base=6,transparent_tile=58,profiles=rows,
        scope='Actual original FDS renderer at all8 actions, holding and facing states for all4 original CHR files. Exact visible pattern-value/position/flip parity after reindexing. Existing three vegetable pairs remain exact. Not yet linked, menu-admitted or native-qualified.',
        bindings={str(p.resolve()):sha(p)for p in[Path(__file__),P,D/'reproduction.json',D/'assembled/original.dbg',D/'original-files/main_pro.bin',D/'original-files/temp_prg.bin',*[Path(files[n.upper()+'-C']['extracted'])for n in chars]]})
    (O/'asset-controls.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items()if k not in ['bindings','profiles']}))


if __name__=='__main__':main()
