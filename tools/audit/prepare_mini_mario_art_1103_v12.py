"""Convert pinned original Mini Mario indexed art/animation to compact NES inputs."""
import base64,hashlib,io,itertools,json,subprocess,zipfile
from pathlib import Path
from PIL import Image,ImageDraw

R=Path(__file__).resolve().parents[2]
O=R/'build/mini-mario-art-1103-v12'
REF=R/'docs/qa/checkpoints/2026-11-02/mini-mario-reference-v1'
VERT=R/'docs/qa/checkpoints/2026-11-03/mini-mario-vertical-v8'
GB=Path('C:/Users/kando/Downloads/SuperMarioBrosMini.gb')
GBPIN='837d39a438f85c5b3ef32c4e41c6c4403147046a7e93bdeac039a09a4a202c81'
TREE='49563d9ab3e8d78e10b0fc7b0797f23676d3045f'
PATHS=['src/shared/lib/sprites/spriteData.ts','src/shared/lib/sprites/helpers.ts',
       'src/lib/compiler/compileSprites.ts','src/lib/compiler/compileData.ts']


def sha(data):return hashlib.sha256(data).hexdigest()


def index(rgb):
    # Literal GB Studio4.2 spriteDataIndexFn for opaque originalRGB PNGs.
    r,g,b=rgb
    return 0 if(g>249 and r<180 and b<20)or(b>=200 and g<20)else 1 if g>=205 else 2 if g>=130 else 3


def encode(pixels,interleaved=False):
    out=bytearray()
    for by in[0,8]:
        planes=[[sum(((pixels[(by+y)*8+x]>>bit)&1)<<(7-x)for x in range(8))for y in range(8)]for bit in[0,1]]
        out.extend(v for y in range(8)for v in[planes[0][y],planes[1][y]])if interleaved else out.extend(planes[0]+planes[1])
    return bytes(out)


def decode(data):
    return [((data[(y//8)*16+y%8]>>(7-x))&1)|(((data[(y//8)*16+8+y%8]>>(7-x))&1)<<1)for y in range(16)for x in range(8)]


def flip(pixels,h=False,v=False):
    return [pixels[(15-y if v else y)*8+(7-x if h else x)]for y in range(16)for x in range(8)]


def main():
    O.mkdir(exist_ok=True);assert not(O/'receipt.json').exists()
    reference=json.loads((REF/'receipt.json').read_text());assert sha((REF/'reference.zip').read_bytes())==reference['archive_SHA256']
    vertical=json.loads((VERT/'receipt.json').read_text());assert sha((VERT/'inputs.zip').read_bytes())==vertical['archive_SHA256']
    z=zipfile.ZipFile(REF/'reference.zip');v=zipfile.ZipFile(VERT/'inputs.zip')
    direct=zipfile.ZipFile(io.BytesIO(v.read('build/mini-mario-defaults-1103-v6/direct-inputs.zip')))
    gb=GB.read_bytes();assert sha(gb)==GBPIN
    compiler=O/'compiler-inputs.zip';upstream={}
    if compiler.exists():
        with zipfile.ZipFile(compiler)as c:
            upstream={name:c.read(name)for name in PATHS};source_bindings=json.loads(c.read('bindings.json'))
    else:
        source_bindings={}
        for name in PATHS:
            q=json.loads(subprocess.check_output(['gh','api','repos/chrismaltby/gb-studio/contents/'+name+'?ref='+TREE]))
            data=base64.b64decode(q['content']);assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==q['sha']
            upstream[name]=data;source_bindings[name]=dict(git_blob=q['sha'],SHA256=sha(data),bytes=len(data))
        with zipfile.ZipFile(compiler,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as c:
            for name,data in upstream.items():c.writestr(name,data)
            c.writestr('bindings.json',json.dumps(source_bindings,indent=2))
    for name,data in upstream.items():assert sha(data)==source_bindings[name]['SHA256']
    assert 'colors: [p.colors[0], p.colors[0], p.colors[1], p.colors[3]]'in upstream[PATHS[3]].decode()
    nes_palette_path=R/'tools/Windows/NEXXT 3.0/defaults/nes.pal'
    palette_bytes=nes_palette_path.read_bytes();assert len(palette_bytes)==192
    rgb=[tuple(palette_bytes[i:i+3])for i in range(0,192,3)]
    palettes={};display={}
    for name in['mario','fire_mario']:
        data=json.loads(z.read('project/palettes/'+name+'.gbsres'));colors=data['colors']
        opaque=[tuple(bytes.fromhex(colors[i]))for i in[0,1,3]]
        choices=[min(range(64),key=lambda j:sum((rgb[j][k]-c[k])**2 for k in range(3)))for c in opaque]
        palettes[name]=dict(source_full_colors=colors,source_opaque_RGB=opaque,NES_opaque=choices,
            proposed_display_RGB=[rgb[i]for i in choices],RGB_exact=False,
            mapping='Official getSpritePalette uses[p0,p0,p1,p3]; transparent0 is ignored. NearestRGB NES colors are an explicit hardware adaptation, not an originalGB hardware palette claim.')
        display[name]=[(0,0,0)]+opaque;display[name+'_NES']=[(0,0,0)]+[rgb[i]for i in choices]
    pairs=[];pairpixels=[];forms={};allgbtiles=set();pixel_checks=0;pose_records=[];poses=bytearray();pose_index={};animation=bytearray();animation_rows=[]
    for name in['smolmario','supamario']:
        png=z.read('assets/sprites/'+name+'.png');assert sha(png)==reference['files']['assets/sprites/'+name+'.png']['SHA256']
        image=Image.open(io.BytesIO(png)).convert('RGB');assert image.size==(128,16)
        spec=json.loads(direct.read('Mico27/SuperMarioBrosMini/assets/sprites/'+name+'.png.gbsres'))
        mapping=[]
        for x in range(0,128,8):
            pixels=[index(c)for c in image.crop((x,0,x+8,16)).get_flattened_data()]
            packed=encode(pixels);assert decode(packed)==pixels;pixel_checks+=128
            if packed not in pairs:pairs.append(packed);pairpixels.append(pixels)
            mapping.append(pairs.index(packed))
            gbpair=encode(pixels,True)
            for at in[0,16]:
                tile=gbpair[at:at+16]
                if any(tile):allgbtiles.add(tile)
        states=[]
        for state_index,state in enumerate(spec['states']):
            rows=[]
            for ai,a in enumerate(state['animations']):
                ids=[];source_frames=[]
                for frame in a['frames']:
                    assert len(frame['tiles'])<=1
                    parts=[];expected=[0]*128
                    for t in frame['tiles']:
                        assert(t['x'],t['y'],t['sliceY'])==(0,0,0)and t['sliceX']%8==0
                        pair=mapping[t['sliceX']//8];h=t.get('flipX',False);vv=t.get('flipY',False)
                        assert t.get('paletteIndex',0)==0
                        parts.append((t['x'],t['y'],2*pair+1,(64 if h else 0)|(128 if vv else 0)|(32 if t.get('priority',False)else 0)))
                        expected=flip([index(c)for c in image.crop((t['sliceX'],0,t['sliceX']+8,16)).get_flattened_data()],h,vv)
                        assert flip(decode(pairs[pair]),h,vv)==expected;pixel_checks+=128
                    key=tuple(parts)
                    if key not in pose_index:
                        pose_index[key]=len(pose_records);offset=len(poses);poses.append(len(parts))
                        for part in parts:poses.extend(v&255 for v in part)
                        pose_records.append(dict(id=pose_index[key],offset=offset,parts=[dict(x=p[0],y=p[1],tile=p[2],attributes=p[3])for p in parts]))
                    ids.append(pose_index[key]);source_frames.append([dict(sliceX=t['sliceX'],sliceY=t['sliceY'],flipX=t.get('flipX',False),flipY=t.get('flipY',False))for t in frame['tiles']])
                offset=len(animation);animation.extend([len(ids)]+ids)
                rows.append(dict(source_animation_index=ai,engine_animation_index=[1,3,2,0,5,7,6,4][ai],
                    offset=offset,pose_ids=ids,source_frames=source_frames))
                animation_rows.append(dict(form=name,state=state.get('name',''),source_animation_index=ai,offset=offset,pose_ids=ids))
            states.append(dict(name=state.get('name',''),animationType=state.get('animationType'),flipLeft=state.get('flipLeft',False),animations=rows))
        forms[name]=dict(source_PNG_SHA256=sha(png),source_meta_SHA256=sha(direct.read('Mico27/SuperMarioBrosMini/assets/sprites/'+name+'.png.gbsres')),
            canvas=[spec['canvasWidth'],spec['canvasHeight']],collision_bounds={k:spec[k]for k in['boundsX','boundsY','boundsWidth','boundsHeight']},
            animSpeed=spec['animSpeed'],sheet_columns=mapping,states=states)
    # A unique index permutation recovers every nonblank originalGB tile.
    matches=[dict(GB_ROM_offset=gb.find(tile),SHA256=sha(tile))for tile in sorted(allgbtiles)]
    assert len(matches)==43 and all(m['GB_ROM_offset']>=0 for m in matches)
    atlas=b''.join(pairs);assert len(atlas)<=1024 and len(pairs)<=32
    (O/'body.chr').write_bytes(atlas);(O/'poses.bin').write_bytes(poses);(O/'animations.bin').write_bytes(animation)
    # Natural-sized idle portrait: original onepart8x16, no scaling/repainting.
    idle=forms['smolmario']['sheet_columns'][0]
    portrait=dict(canvas=[16,32],facing='right/source_idle_animation0',parts=[dict(x=4,y=16,tile=2*idle+1,attributes=0)],
        source_pair=idle,natural_pixels=True,anchor='Preview-only canvas placement; runtime/native anchor awaits compiler-origin proof.')
    (O/'menu-portrait.chr').write_bytes(pairs[idle])
    layout=dict(format=dict(tile_bank=1,pair_bytes=32,poses='count:u8 then[x:i8,y:i8,tile:u8,attributes:u8]; offsets are originalgbsres part coordinates',
        animation='framecount:u8 thenposeIDs:u8; eachstate retains all8 source animations, no runtime state dispatch invented',
        native_anchor='UNRESOLVED: preserve relativepart0,0; helper owns missingGBS origin defaults/migration. Do not bind nativeanchor from sourcebounds alone.'),
        forms=forms,pose_records=pose_records,animation_rows=animation_rows,palettes=palettes,portrait=portrait)
    (O/'layout.json').write_text(json.dumps(layout,indent=2)+'\n')
    panel=Image.new('RGB',(16*44+24,4*92+32),(28,31,38));draw=ImageDraw.Draw(panel)
    for row,(form,pal)in enumerate([('smolmario','mario'),('supamario','mario'),('smolmario','mario_NES'),('supamario','fire_mario_NES')]):
        draw.text((8,row*92+2),form+' / '+pal,fill='white')
        for col,pair in enumerate(forms[form]['sheet_columns']):
            ox=12+col*44;oy=row*92+20
            for y in range(16):
                for x in range(8):
                    c=pairpixels[pair][y*8+x]
                    if c:draw.rectangle((ox+x*4,oy+y*4,ox+x*4+3,oy+y*4+3),fill=display[pal][c])
            draw.text((ox,oy+65),str(col),fill='white')
    panel.save(O/'source-and-NES.png')
    menu=Image.new('RGB',(256,160),(45,87,167));draw=ImageDraw.Draw(menu)
    for side,h in enumerate([False,True]):
        pix=flip(pairpixels[idle],h)
        for y in range(16):
            for x in range(8):
                c=pix[y*8+x]
                if c:draw.rectangle((32+side*128+x*6,24+y*6,37+side*128+x*6,29+y*6),fill=display['mario_NES'][c])
        draw.text((28+side*128,128),'RIGHT'if not h else'LEFT',fill='white')
    menu.save(O/'facing-preview.png')
    receipt=dict(passed=True,source_only=True,ROM_written=False,NES_native_run=False,resources_allocated=False,
        original_GB_SHA256=GBPIN,GBS_compiler_tree=TREE,compiler_source_bindings=source_bindings,
        indexed_pixel_comparisons=pixel_checks,unique_originalGB_nonblank_tiles=43,original_GB_tile_matches=matches,
        body_CHR_bytes=len(atlas),body_pairs=len(pairs),pose_bytes=len(poses),pose_records=len(pose_records),animation_bytes=len(animation),animation_rows=len(animation_rows),
        maximum_sprites_per_pose=1,NES_palette_approximation_explicit=True,native_anchor_qualified=False,
        source_state_graphs_preserved=True,source_empty_frames_preserved=True,source_flipX_and_flipY_preserved=True,
        source_index_mapping={'65ff00':0,'e0f8cf':1,'86c06c':2,'071821':3},
        scope='OriginalPNG indexed shapes/explicit sourceparts/all animationframes and NES8x16 decode agree exactly; all43 unique nonblank8x8 tiles also occur verbatim in exactoriginalGB. Originalpalette roles are compiler-bound; nearestNESRGB is a deliberate approximation. This is compact art/metadata only: no originalGB renderer execution/animationtiming equivalence, nativebody/menu admission, RAM/page grant, nativeanchor/GBSmigration claim or ROM change.',
        bindings={str(p.relative_to(R))if p.is_relative_to(R)else str(p):sha(p.read_bytes())for p in[Path(__file__),REF/'reference.zip',REF/'receipt.json',VERT/'inputs.zip',VERT/'receipt.json',GB,compiler,nes_palette_path]},
        outputs={p.name:dict(bytes=p.stat().st_size,SHA256=sha(p.read_bytes()))for p in O.iterdir()if p.is_file()})
    (O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k]for k in['passed','body_CHR_bytes','body_pairs','pose_bytes','pose_records','animation_bytes','animation_rows','indexed_pixel_comparisons','native_anchor_qualified']}))


if __name__=='__main__':main()
