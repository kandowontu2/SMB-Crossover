"""Authenticate and extract the UNUSED four-class2.02 prototype, not a reskin.

No network/TCRF bypass, native emulator, full source copy or assembly edits.
Raw original SWF bitmap39 must exactly match the surviving exported PNG.
"""
from pathlib import Path
from collections import Counter
import hashlib,json,re,struct,sys,zlib,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'reference/crossover2'
SCRIPTS=REF/'extracted/scripts'
sys.path.insert(0,str(ROOT/'tools/reference'))
from prepare_crossover import frames
SHA='6374c72426556bfc3cc16f7594ce4443a5867fe2d367514136c99cc8458b70af'
CLASSES=[('Fighter',0),('WhiteMage',282),('BlackMage',188),('Thief',94)]
FILES=['com/smbc/characters/'+s+'.as'for s in ['WarriorOfLight','Fighter','Thief','BlackMage','WhiteMage','Character']]+[
 'com/smbc/projectiles/BlackMageSpell.as','com/smbc/projectiles/Projectile.as',
 'com/smbc/displayInterface/FinalFantasyPointer.as','com/smbc/data/Spell.as',
 'com/smbc/data/DamageValue.as','com/smbc/data/AnimationTimers.as','com/smbc/data/CharacterInfo.as',
 'com/smbc/data/MovieClipInfo_WarriorOfLightMc.as','com/smbc/data/MovieClipInfo_BlackMageSpellMc.as',
 'com/smbc/utils/GameLoopTimer.as','com/explodingRabbit/display/CustomMovieClip.as',
 'com/smbc/main/AnimatedObject.as','com/smbc/managers/StatManager.as']

def digest(b):return hashlib.sha256(b).hexdigest()
def binding(p):p=Path(p);b=p.read_bytes();return dict(path=str(p.resolve()),bytes=len(b),sha256=digest(b))

def tags(data,start):
    while start+2<=len(data):
        at=start;header=int.from_bytes(data[start:start+2],'little');start+=2
        kind,n=header>>6,header&63
        if n==63:n=int.from_bytes(data[start:start+4],'little');start+=4
        assert start+n<=len(data)
        yield kind,data[start:start+n],at
        start+=n
        if kind==0:break

def swf_assets(raw):
    assert digest(raw)==SHA
    assert raw[:3]in [b'CWS',b'FWS']
    data=raw[:8]+zlib.decompress(raw[8:])if raw[:3]==b'CWS'else raw
    assert len(data)==int.from_bytes(raw[4:8],'little')
    rectbits=data[8]>>3;start=8+(5+4*rectbits+7)//8+4
    selected={}
    for tag,q,at in tags(data,start):
        if tag in[2,22,32,83,36,39]and int.from_bytes(q[:2],'little')in [13,14,17,18,21,22,39,40,41,174]:
            i=int.from_bytes(q[:2],'little');selected[i]=(tag,q,at)
    assert set(selected)=={13,14,17,18,21,22,39,40,41,174}
    tag,b,at=selected[39];assert tag==36 and b[2]==3
    w,h=struct.unpack_from('<HH',b,3);n=b[7]+1;expanded=zlib.decompress(b[8:])
    palette=[tuple(expanded[4*i:4*i+4])for i in range(n)]
    stride=(w+3)&~3;assert len(expanded)==n*4+stride*h
    pixels=expanded[n*4:];out=Image.new('RGBA',(w,h))
    out.putdata([palette[pixels[y*stride+x]]for y in range(h)for x in range(w)])
    exported=Image.open(REF/'images/39.png').convert('RGBA')
    assert exported.size==out.size and exported.tobytes()==out.tobytes(),'Original SWF bitmap39 vs exported PNG bytes'
    proof={str(i):dict(tag=t,uncompressed_SWF_offset=p,bytes=len(q),sha256=digest(q))for i,(t,q,p)in selected.items()}
    return out,palette,selected,proof

def actual_labels(payload):
    frame=1;labels=[]
    for kind,q,_ in tags(payload,4):
        if kind==43:labels.append([frame,q.split(b'\0',1)[0].decode('utf-8')])
        elif kind==1:frame+=1
    assert frame-1==int.from_bytes(payload[2:4],'little')
    return labels

def window(f):
    bm=next(v for v in f['display'].values()if v.get('characterId')=='40')
    mask=next(v for v in f['display'].values()if v.get('characterId')=='18')
    b,m=bm['matrix'],mask['matrix']
    assert float(b.get('scaleX',1))==1 and float(b.get('scaleY',1))==1
    x=float(m['translateX'])/40-float(b['translateX'])/40
    y=float(m['translateY'])/40-float(b['translateY'])/40
    w=float(m['scaleX'])/2;h=float(m['scaleY'])/2
    assert abs(x-round(x))<0.01 and abs(y-round(y))<0.01,(f['frame'],x,y)
    return [round(x),round(y),round(w),round(h)],dict(mask=m,bitmap=b)

def functions(text):
    out=[]
    for match in re.finditer(r'(?:override\s+)?(?:public|protected|private)\s+function\s+(\w+)\([^)]*\)[^{]*\{',text):
        start=match.start();p=match.end();depth=1
        while depth:
            if text[p]=='{':depth+=1
            elif text[p]=='}':depth-=1
            p+=1
        body=text[start:p]
        out.append(dict(name=match[1],line=text[:start].count('\n')+1,end_line=text[:p].count('\n')+1,
                        bytes=len(body.encode()),sha256=digest(body.encode())))
    return out

def main():
    target=ROOT/'chr/characters';target.mkdir(parents=True,exist_ok=True)
    source,palette,selected,rawtags=swf_assets((REF/'source.swf').read_bytes())
    tree=ET.parse(REF/'main.xml').getroot();sprites={i.get('spriteId'):i for i in tree.iter('item')if i.get('type')=='DefineSpriteTag'}
    body=frames(sprites['41']);spells=frames(sprites['174'])
    assert len(body)==18 and len(spells)==15
    for k,timeline in [('41',body),('174',spells)]:
        assert [[f['frame'],label]for f in timeline for label in f['labels']]==actual_labels(selected[int(k)][1])
    collision=[]
    for f in body:
        boxes={}
        for ident,role in [('14','body'),('22','attack')]:
            p=next(v for v in f['display'].values()if v.get('characterId')==ident);m=p['matrix']
            # Actual shapes13/21 are [0,160]twips=8Flash pixels each axis.
            boxes[role]=dict(source_matrix=m,NES_unrounded_rect=[float(m['translateX'])/40,float(m['translateY'])/40,
                              float(m.get('scaleX',1))*4,float(m.get('scaleY',1))*4])
        collision.append(dict(frame=f['frame'],labels=f['labels'],boxes=boxes))
    atlas=Image.new('RGBA',(18*48,8*48));facts=[];previews={}
    for variant,(name,ofs)in enumerate(CLASSES):
        for tier in[0,1]:
            union=Counter()
            for i,f in enumerate(body):
                rect,transforms=window(f);x,y,w,h=rect;x+=423*tier;y+=ofs
                assert 0<=x<x+w<=source.width and 0<=y<y+h<=source.height
                crop=source.crop((x,y,x+w,y+h));colors=Counter(crop.getdata());colors.pop((0,0,0,0),None)
                opaque=sum(n for rgba,n in colors.items()if rgba[3]);assert opaque
                # No chroma-key assumptions: all original alpha/RGB bytes survive.
                assert not colors.get((111,49,152,255)),('atlas boundary entered clip',name,tier,i)
                union.update(colors)
                tile=Image.new('RGBA',(48,48));tile.paste(crop,(1,0))
                atlas.paste(tile,(i*48,(variant*2+tier)*48))
                cropbytes=crop.tobytes();rec=dict(variant=variant,class_name=name,tier=tier,source_frame=f['frame'],labels=f['labels'],
                        source_rect=[x,y,w,h],atlas_rect=[i*48,(variant*2+tier)*48,48,48],
                        source_matrix=transforms,foreground_bounds=crop.getbbox(),RGBA_sha256=digest(cropbytes),
                        opaque_pixels=opaque,colors=[dict(RGBA=list(c),pixels=n)for c,n in sorted(colors.items())],
                        float_truncation_margin_opaque=sum(1 for xx in range(w)if crop.getpixel((xx,h-1))[3])+sum(1 for yy in range(h)if crop.getpixel((w-1,yy))[3]))
                facts.append(rec);previews[variant,tier,f['frame']]=tile
            # Exact source RGB only; no NES nearest-color palette invented.
    atlaspath=target/'final-fantasy-prototype-poses.png';atlas.save(atlaspath)
    reopened=Image.open(atlaspath).convert('RGBA');assert reopened.tobytes()==atlas.tobytes()
    spellfacts=[]
    for f in spells:
        rect,transforms=window(f);x,y,w,h=rect;crop=source.crop((x,y,x+w,y+h))
        inbounds=max(0,min(source.width,x+w)-max(0,x))*max(0,min(source.height,y+h)-max(0,y))
        spellfacts.append(dict(frame=f['frame'],labels=f['labels'],source_rect=rect,source_matrix=transforms,
                               out_of_bounds_pixels=w*h-inbounds,opaque_pixels=sum(1 for p in crop.getdata()if p[3]),
                               RGBA_sha256=digest(crop.tobytes())))
    spellpath=target/'final-fantasy-authored-spell-region.png'
    source.crop((893,6,1307,359)).save(spellpath)
    iconpath=target/'final-fantasy-unbound-sword-glyphs.png'
    icons=Image.new('RGBA',(96,48))
    for i,y in enumerate([54,148]):icons.paste(source.crop((1,y,47,y+46)),(i*48+1,0))
    icons.save(iconpath)
    # One preview, narrow contrasting gutters; raw/authored artifacts stay RGBA.
    preview=Image.new('RGB',(760,8*112),(27,34,43));draw=ImageDraw.Draw(preview)
    for variant,(name,ofs)in enumerate(CLASSES):
        for tier in[0,1]:
            row=variant*2+tier;draw.text((5,row*112+4),name+(' upgrade'if tier else' base'),fill='white')
            for col,frame in enumerate([1,6,10,13,14]):
                pane=Image.new('RGBA',(48,48),(55,62,70));pane.alpha_composite(previews[variant,tier,frame])
                x=145+col*120;y=row*112+8
                preview.paste(pane.convert('RGB').resize((96,96),Image.Resampling.NEAREST),(x,y))
                draw.rectangle((x-1,y-1,x+96,y+96),outline=(240,210,40))
                draw.text((x,y+97),next(f['labels'][0]for f in body if f['frame']==frame),fill='white')
    previewpath=target/'final-fantasy-preview.png';preview.save(previewpath)
    scriptmap={}
    for f in FILES:
        p=SCRIPTS/f;scriptmap[f]=dict(binding=binding(p),functions=functions(p.read_text()))
    spellbase=next(f for f in spellfacts if f['frame']==1)
    assert spellbase['opaque_pixels']==0 and spellbase['out_of_bounds_pixels']>0
    report=dict(status='SOURCE/ASSET AUTHENTICATION ONLY; unused unfinished2.02 prototype, not playable/native',
                source_SWF=binding(REF/'source.swf'),source_provenance=binding(REF/'source.json'),
                main_XML=binding(REF/'main.xml'),original_bitmap=binding(REF/'images/39.png'),
                original_SWF_tags=rawtags,bitmap_palette_RGBA=[list(p)for p in palette],bitmap_size=list(source.size),
                raw_SWF_bitmap_export_exact=True,actual_SWF_frame_labels_match_XML=True,source_map=scriptmap,
                class_order=[x[0]for x in CLASSES],class_copyY=dict(CLASSES),upgrade_copyX=423,
                body_timeline_labels=actual_labels(selected[41][1]),body_frames=18,body_class_tier_cells=len(facts),
                original_collision_rects=collision,
                body_cells=facts,spell_timeline_labels=actual_labels(selected[174][1]),spell_timeline=spellfacts,
                authored_spell_region=dict(rect=[893,6,414,353],role='Unaltered authored atlas spell pixels; not a repaired timeline or invented frame map'),
                no_NES_palette_quantization=True,CHR_first_page='UNALLOCATED/configurable; no CHR/PRG segment written',
                unbound_sword_glyphs=dict(rects=[[1,54,46,46],[1,148,46,46]],
                    role='Authored first-column sword glyphs; no proved pickup registration or reward semantics'),
                extraction_contract='Full authored46px cell, exact RGBA. Float mask45.998px may truncate to45 in prototype BitmapData; margin evidence retained, no runtime rendering equality claim.',
                outputs=[binding(p)for p in[atlaspath,spellpath,iconpath,previewpath]],
                gaps=['WhiteMage has no side/up/down attack or healing override',
                      'Prototype omitted from CharacterInfo and ordinary skin/upgrade registration',
                      'Spell timeline Fire/Ice point below actual bitmap39 bottom; must author repair openly',
                      'Pointer appearance timer has no start call in WarriorOfLight; spellPnt stored but never used by projectile',
                      'No class-specific FF powerup or MP tables found; inherited shared pickup integration requires registration',
                      'No host movement/world/damage/render integration or runtime/native qualification'])
    out=target/'final-fantasy-source-v1.json';out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(metadata=binding(out),cells=len(facts),spell_blank_frames=[f['frame']for f in spellfacts if f['opaque_pixels']==0],
                          PNGs=report['outputs'])))

if __name__=='__main__':main()
