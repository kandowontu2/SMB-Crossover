"""Independent full panel glyph masks versus authenticated physical font395."""
from pathlib import Path
import argparse,hashlib,json
from PIL import Image

R=Path(__file__).resolve().parents[2];B=R/'build'
ROM=B/'zelda2_easy_glove.nes';EXPECTED='32694243361bb1366f6fd64c054ea2451f86b2517fc020d9c2b5d66bbf07bfa0'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bind=lambda p:dict(path=str(Path(p).resolve()),bytes=Path(p).stat().st_size,sha256=sha(p))

def pattern(tiles,font):
    assert len(tiles)==196 and len(font)==1024
    out=[]
    for y in range(112):
        row=[]
        for x in range(112):
            tile=tiles[(y//8)*14+x//8];assert 192<=tile<=255
            at=(tile-192)*16+y%8;bit=7-x%8;value=(font[at]>>bit&1)|(font[at+8]>>bit&1)<<1
            assert value in [1,3];row.append(value)
        out.append(row)
    return out

def pixels(image,tiles,font):
    assert image.size==(256,240),'Whole native PPU PNG, not a crop'
    want=pattern(tiles,font);groups={1:set(),3:set()};im=image.convert('RGB')
    for y in range(112):
        for x in range(112):groups[want[y][x]].add(im.getpixel((72+x,64+y)))
    assert len(groups[1])==len(groups[3])==1,'Every actual glyph/background pixel matches its source pattern class'
    white=next(iter(groups[1]));black=next(iter(groups[3]));assert sum(white)>sum(black),'Source palette1 white and palette3 black remain distinct'
    return dict(source_pattern_pixels=12544,source_class1_RGB=list(white),source_class3_RGB=list(black),scope='Exact whole112x112 source glyph/background classification; actual RGB colors reported, no assumed emulator palette lookup.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,default=B/'current-z2glove-zelda2-panel-supplement-v1');p.add_argument('--native',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--self-test',action='store_true');a=p.parse_args()
    assert sha(ROM)==EXPECTED;raw=ROM.read_bytes();font=raw[16+128*8192+395*1024:16+128*8192+396*1024];assert font==(R/'chr/characters/zelda2-pause-font.chr').read_bytes()
    cfg=json.loads((a.ready/'config.json').read_text());assert cfg['ROM_sha256']==EXPECTED
    if a.self_test:
        cases=[]
        for page in ['0','1']:
            tiles=cfg['panel_expected'][page];want=pattern(tiles,font);im=Image.new('RGB',(256,240),(100,100,220))
            for y in range(112):
                for x in range(112):im.putpixel((72+x,64+y),(255,255,255)if want[y][x]==1 else(0,0,0))
            assert pixels(im,tiles,font)['source_pattern_pixels']==12544
            for n,bad in [('blank',Image.new('RGB',(256,240),(143,143,255))),('one-pixel',im.copy()),('shift',im.copy())]:
                if n=='one-pixel':bad.putpixel((80,70),(12,34,56))
                if n=='shift':bad.paste(im.crop((72,64,183,176)),(73,64))
                try:pixels(bad,tiles,font)
                except AssertionError:pass
                else:raise AssertionError('Reject actual wrong image '+n)
                cases.append(dict(page=int(page),negative=n,rejected=True))
        actual=B/'current-z2glove-zelda2-easy-earned-v1/native/pause-spells.png'
        try:pixels(Image.open(actual),cfg['panel_expected']['0'],font)
        except AssertionError:pass
        else:raise AssertionError('Old real blank PNG must not qualify')
        out=dict(passed=True,native_run=False,Lua_VM_executed=False,self_test=True,positive_source_tile_pages=2,negative_controls=cases,real_blank_native_PNG_rejected=bind(actual),font_sha256=hashlib.sha256(font).hexdigest(),bindings=[bind(p)for p in [Path(__file__),a.ready/'config.json',ROM,R/'chr/characters/zelda2-pause-font.chr']])
    else:
        assert a.native;z=json.loads((a.native/'result.json').read_text());assert z['passed']and z['ROM_sha256']==EXPECTED
        pictures=[]
        for page,name in [('0','01-earned-spells-visible.png'),('1','02-earned-level-visible.png')]:
            d=z['screenshots'][name];assert d['page']==int(page)and d['actual_tiles']==cfg['panel_expected'][page]and d['CHR'][11]==395 and d['palette'][5]==48 and d['palette'][7]==15
            epochs=d['epochs'];assert len(epochs)>=3 and epochs[-1]['finish']['frame']>epochs[0]['finish']['frame']+1
            for e in epochs:
                assert e['start']['cpu']<=e['finish']['cpu']
                for h in [e['start'],e['finish'],e['enable']]:assert h['physical11']==395 and h['pending']==0 and h['active']==1 and h['page']==int(page)and h['mask']&24
                h=e['enable'];assert h['NMI']and(241<=h['line']<=260 or h['line']==-1 and h['dot']<=274)
            result=pixels(Image.open(a.native/name),cfg['panel_expected'][page],font);pictures.append(dict(page=int(page),file=bind(a.native/name),actual_epochs=epochs,**result))
        out=dict(passed=True,native_run=True,ROM_sha256=EXPECTED,agent_visual_review=False,automatic_exact_panel_mask_check=True,pictures=pictures,source_pixels_checked=25088,limitations='Only both112x112 panel regions and declared completed epochs. Wholeframe/HUD/other areas require agent review. No all-game visual or native acquisition claim beyond this actual result.',bindings=[bind(p)for p in [Path(__file__),a.ready/'prepared-not-run.json',a.ready/'config.json',a.native/'result.json',a.native/'panel-display-events.jsonl',ROM]])
    assert not a.output.exists();a.output.write_text(json.dumps(out,indent=2)+'\n',newline='\n');print(json.dumps(dict(passed=True,output=str(a.output),sha256=sha(a.output))))

if __name__=='__main__':main()
