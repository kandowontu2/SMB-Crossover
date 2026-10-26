"""Finite source-only Parodius bar space/pixel audit; no ROM/native mutations."""
from pathlib import Path
import argparse, hashlib, json, re
from PIL import Image, ImageDraw

SHA='6c69e506b45c8420cf57a62b868f89c0fe86d308c0ee55655b48e8f44af9521a'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mask(raw):
    return [[((raw[y]>>(7-x))&1)|(((raw[y+8]>>(7-x))&1)<<1) for x in range(8)]for y in range(8)]
def cells(text): return [int(x,16)for x in re.findall(r'\$([0-9a-fA-F]{2})',text)]
def bar(font,ts):
    a=Image.new('RGB',(8*len(ts),8),'black');p=a.load()
    for i,t in enumerate(ts):
        for y,row in enumerate(mask(font[t*16:t*16+16])):
            for x,v in enumerate(row): p[i*8+x,y]=(255,255,255) if v else (0,0,0)
    return a
def encode(a):
    return bytes(sum((a[y][x]&1)<<(7-x)for x in range(8))for y in range(8))+bytes(sum(((a[y][x]>>1)&1)<<(7-x)for x in range(8))for y in range(8))
def make_proposal(font,ts,frame,keep):
    # Only existing source pixels: Parodius letter-hole masks become positive
    # foreground; the thin frame is copied from the current Gradius first cell.
    target=[];glyphs=0
    for cell in range(7):
        old=[sum((mask(font[t*16:t*16+16])[y]for t in ts[cell*4:cell*4+4]),[])for y in range(8)]
        new=[[0]*32 for _ in range(8)]
        for y in range(8):
            for x in range(32):
                if y in [0,1,7]:new[y][x]=frame[y][x]
                elif x==0:new[y][x]=frame[y][0]
                elif x==31:new[y][x]=frame[y][30] # retain30px letter interior; move source right edge1px
                elif 2<=y<=6:new[y][x]=1-old[y][x]
        assert all(old[y][0]==old[y][31]==1 for y in range(2,7))
        assert all(new[y][x]==1-old[y][x]for y in range(2,7)for x in range(1,31))
        glyphs+=sum(new[y][x]for y in range(2,7)for x in range(1,31))
        target += [encode([r[c*8:c*8+8]for r in new])for c in range(4)]
    out=bytearray(font);free=sorted(set(range(64))-keep);pool={bytes(font[t*16:t*16+16]):t for t in keep};mapped=[]
    for raw in target:
        if raw not in pool:
            t=free.pop(0);pool[raw]=t;out[t*16:t*16+16]=raw
        mapped.append(pool[raw])
    assert all(out[t*16:t*16+16]==font[t*16:t*16+16]for t in keep)
    assert [bytes(out[t*16:t*16+16])for t in mapped]==target
    return bytes(out),mapped,dict(glyph_foreground_pixels=glyphs,unique_bar_tiles=len(set(mapped)),spare_tiles=len(free),exact_all21_source_letter_masks=True)
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--rom',type=Path,required=True);p.add_argument('--run',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);assert sha(a.rom)==SHA
    rom=a.rom.read_bytes();base=16+rom[4]*16384
    pages=[rom[base+(395+v)*1024:base+(396+v)*1024]for v in range(1,4)]
    assert b''.join(pages)==(a.source/'chr/characters/parodius-hud.chr').read_bytes()
    ts=cells((a.source/'src/parodius_hud.inc').read_text());assert len(ts)==84
    vv=cells((a.source/'src/vic_hud.inc').read_text());assert len(vv)==28
    g=rom[base+394*1024:base+395*1024];bars=[bar(pages[v],ts[v*28:(v+1)*28])for v in range(3)]
    bars.append(bar(g,vv[:24]));sheet=Image.new('RGB',(1024,240),'#202020');d=ImageDraw.Draw(sheet)
    for i,(name,im)in enumerate(zip(['Octopus current','Twinbee current','Pentarou current','Vic/Gradius current'],bars)):
        d.text((0,i*60),name,fill='white');sheet.paste(im,(0,i*60+16));sheet.paste(im.resize((im.width*4,32),Image.Resampling.NEAREST),(0,i*60+27))
    sheet.save(a.output/'existing-bar-comparison.png')
    atlas=Image.new('RGB',(16*40,4*52),'#202020');d=ImageDraw.Draw(atlas)
    for t in range(64):
        x,y=(t%16)*40,(t//16)*52;d.text((x,y),f'{t:02x}',fill='white');atlas.paste(bar(pages[0],[t]).resize((32,32),Image.Resampling.NEAREST),(x,y+16))
    atlas.save(a.output/'octopus-existing-64tile-atlas.png')
    data={'ROM_sha256':SHA,'source':str(a.source),'CHR_start':base,'tables':ts,'bars':[]}
    keep=set(range(10))|{ord(c)-ord('A')+10 for c in set('OCTOPUSTWINBEEPENTAROUWORLDTIMESCOREHP')}|{0x24,0x28,0x29,0x2e}
    for v,font in enumerate(pages):
        used=set(ts[v*28:(v+1)*28]);data['bars'].append({'variant':v+1,'bar_unique_tiles':len(used),'kept_standard_tiles':len(keep),'bar_unique_nonkept':len(used-keep),'unassigned_tiles':sorted(set(range(64))-keep-used),'font_sha256':hashlib.sha256(font).hexdigest()})
    (a.output/'initial-measurements.json').write_text(json.dumps(data,indent=2)+'\n')
    frame=[sum((mask(g[t*16:t*16+16])[y]for t in vv[:4]),[])for y in range(8)]
    proposed=[make_proposal(font,ts[v*28:(v+1)*28],frame,keep)for v,font in enumerate(pages)]
    newchr=b''.join(z[0]for z in proposed);(a.output/'proposal-parodius-hud.chr').write_bytes(newchr)
    nt=[t for z in proposed for t in z[1]]
    (a.output/'proposal-parodius_hud.inc').write_text('; SOURCE-ONLY MOCK: current Parodius letter masks, current Gradius thin frame.\nPnHudCells:\n'+''.join(' .byte '+','.join(f'${t:02x}'for t in nt[i:i+28])+'\n'for i in range(0,84,28)))
    comparison=Image.new('RGB',(1024,3*110),'#202020');d=ImageDraw.Draw(comparison)
    for v in range(3):
        old=bars[v];new=bar(proposed[v][0],proposed[v][1]);y=v*110
        d.text((0,y),f'Variant{v+1}: actual current masks / proposed actual-mask composition',fill='white')
        comparison.paste(old.resize((896,32),Image.Resampling.NEAREST),(0,y+16));comparison.paste(new.resize((896,32),Image.Resampling.NEAREST),(0,y+52))
        comparison.paste(old,(0,y+88));comparison.paste(new,(240,y+88))
    comparison.save(a.output/'source-tile-proposal-comparison.png')
    capture=a.run/'frame-000548.argb';actual=Image.frombytes('RGBA',(256,240),capture.read_bytes(),'raw','BGRA').convert('RGB')
    states=[json.loads(s)for s in(a.run/'hud-frames.jsonl').read_text().splitlines()];state=next(z['start']for z in states if z['finished']['frame']==548)
    assert state['chr'][8]==396 and state['labels']==ts[:28]and state['attrs']==[170]*8
    colors={}
    for y in range(8):
        for x in range(224):
            t=ts[x//8];value=mask(pages[0][t*16:t*16+16])[y][x%8];color=actual.getpixel((x+16,y+8));colors.setdefault(value,set()).add(color)
    assert set(colors)=={0,1}and all(len(x)==1 for x in colors.values());colors={k:next(iter(v))for k,v in colors.items()}
    mock=actual.copy();p=mock.load();new=proposed[0]
    for y in range(8):
        for x in range(224):p[x+16,y+8]=colors[mask(new[0][new[1][x//8]*16:new[1][x//8]*16+16])[y][x%8]]
    changed=sum(actual.getpixel((x,y))!=mock.getpixel((x,y))for y in range(240)for x in range(256))
    assert all(actual.getpixel((x,y))==mock.getpixel((x,y))for y in range(240)for x in range(256)if not(16<=x<240 and 8<=y<16))
    preview=Image.new('RGB',(512,310),'#202020');d=ImageDraw.Draw(preview);d.text((0,0),'ACTUAL6c69 frame548',fill='white');d.text((256,0),'MOCK only bar pixels changed',fill='white');preview.paste(actual,(0,18));preview.paste(mock,(256,18))
    preview.paste(actual.crop((0,8,256,16)).resize((512,16),Image.Resampling.NEAREST),(0,270));preview.paste(mock.crop((0,8,256,16)).resize((512,16),Image.Resampling.NEAREST),(0,290));preview.save(a.output/'actual548-and-tile-mock.png')
    statuses=[]
    for meter in range(128):
        attrs=[]
        bit=1
        for _ in range(8):
            z=0xa6 if bit&meter else 0xaa
            if(bit>>1)&meter:z=(z&0xfc)|1
            attrs.append(z);bit=(bit<<1)&255
        for cell in range(7):
            palettes=[(attrs[(col+2)//4]>>((col+2)&2))&3 for col in range(cell*4,cell*4+4)]
            assert palettes==([1]*4 if meter&(1<<cell)else[2]*4)
        statuses.append(dict(meter=meter,attributes=attrs))
    (a.output/'all128-status-attributes.json').write_text(json.dumps(statuses,indent=2)+'\n')
    facts=dict(source_only=True,native_run=False,ROM_sha256=SHA,proposed_layout='Same seven32px cells x16..239/y8..15; source letter masks positive; actual Gradius thin frame',
      original_data=data,proposal_rows=[dict(variant=v+1,**z[2])for v,z in enumerate(proposed)],
      unchanged=dict(standard_HUD_tiles_each_page=len(keep),CHR_total_bytes=3072,font_pages=[396,397,398],cell_table_bytes=84,row_cells=28,attribute_bytes=8,first_queue_bytes=42,dirty_queue_bytes=11,live_status_bits=7,all_status_values_checked=128,runtime_instructions=True,added_CPU_cycles=0,added_PPU_writes=0,palette_writes=0,rows=1),
      metrics=dict(letter_pixel_height=5,letter_pixel_width=3,cell_width=32,row_height=8,framed7high_letter_minimum_rows=10,existing_Gradius_letter_pixel_height=5),
      mock=dict(actual_capture=str(capture),actual_capture_sha256=sha(capture),actual_state_frame=548,exact_palette_colors={str(k):list(v)for k,v in colors.items()},changed_pixels=changed,outside_bar_pixels_exact=True,not_an_emulator_output=True),
      limits='Finite source/data-only proposal; no build/native run or demonstrated player-readability improvement. Font stays3x5; larger framed text requires another row or wider layout. Current actual selection meter is0; 128status controls are source predicate enumeration, not physical acquisition. No palette color3/dark-plate assumption, no audio/body/roster/source-game art modification.')
    (a.output/'measurements.json').write_text(json.dumps(facts,indent=2)+'\n')
    inputs=[a.rom,a.source/'src/parodius_hud.inc',a.source/'src/parodius_hud_queue.s',a.source/'src/parodius_render.s',a.source/'src/vic_render.s',a.source/'src/vic_hud.inc',a.source/'tools/reference/prepare_parodius_hud.py',a.source/'tools/reference/build_vic_hud.py',a.source/'chr/characters/parodius-hud.chr',a.source/'src/reset.s',capture,a.run/'hud-frames.jsonl',Path(__file__)]
    files=inputs+[z for z in a.output.iterdir()if z.is_file()];manifest={str(z.resolve()):sha(z)for z in sorted(files,key=str)}
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    proof=dict(passed=True,classification='Source-only finite readability proposal and actual-tile mock, not native or global quality clearance',native_run=False,ROM_sha256=SHA,measurements_sha256=sha(a.output/'measurements.json'),manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),agent_visual_review=False)
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2));print('proof_sha256='+sha(a.output/'proof.json'))
if __name__=='__main__':main()
