"""Pack the six added guests from pinned Crossover 2 sheets / native NES OAM.

Reference inputs are optional regeneration material. Normal ROM builds use the
committed CHR and pose tables and do not require any original ROM or SWF.
"""
from pathlib import Path
import argparse, hashlib, json
from PIL import Image
import build_megaman_assets as assets
import build_samus_assets as packing

ROOT=assets.ROOT
POSES='STAND WALK1 WALK2 WALK3 JUMP CROUCH ATTACK1 ATTACK2 ATTACK3 CLIMB1 CLIMB2 HURT DIE DASH UP DIAGUP DIAGDOWN THROW WALL CEILING HOVER CROUCHSHOOT JUMPSHOOT JUMPUP CROUCHATTACK1 CROUCHATTACK2 CROUCHATTACK3 JUMPATTACK1 JUMPATTACK2 JUMPATTACK3 JUMPDIAGUP JUMPDIAGDOWN HOVERSMALL DEATH1 DEATH2 DEATH3 DEATH4'.split()
POSES += [f'{stance}{kind}{i}' for kind in ('SLASH','THROW') for stance in ('RYU','DUCK','AIR') for i in range(1,6)]
POSES += [f'{stance}THROW{i}' for stance in ('WALL','BACK') for i in range(1,6)]
POSES += ['WALKSTEP','FLAP1','FLAP2','FLAPSHOT1','FLAPSHOT2','FLAPUP1','FLAPUP2']
assert len(POSES)*3<=256
ROLES=['PIT','RYGAR','LUIGI','BASS','RYU','SOPHIA']
PIT_FLIGHT_BASE={pose:base for poses,base in (
    (('FLAP1','FLAP2'),'JUMP'),
    (('FLAPSHOT1','FLAPSHOT2'),'JUMPSHOOT'),
    (('FLAPUP1','FLAPUP2'),'JUMPUP')) for pose in poses}
ROLE=''
ATLAS=json.loads((ROOT/'docs/reference/expanded-atlas.json').read_text())
COLORS=[]
BASS_PROJECTILE=False
RGB={0x20:(252,252,252),0x07:(82,33,0),0x0f:(0,0,0),0x00:(116,116,116),0x16:(216,40,0),0x26:(248,120,88),0x27:(252,152,56),0x36:(252,152,56),0x30:(252,252,252),0x17:(164,80,0),0x28:(248,184,0),0x37:(252,216,168),0x15:(228,0,88),0x21:(60,188,252)}

def layers(im,projectile=False):
    out={p:[[0]*im.width for _ in range(im.height)] for p in (0,2,3)}
    for y in range(im.height):
        for x in range(im.width):
            v=im.getpixel((x,y))
            if v[3]<128:continue
            _,(p,c)=min(COLORS,key=lambda item:sum((v[i]-item[0][i])**2 for i in range(3)))
            if ROLE=='BASS' and BASS_PROJECTILE:
                # Red/orange/white buster pixels fit one world-palette sprite.
                _,c=min(((RGB[0x16],1),(RGB[0x27],3),(RGB[0x30],2)),key=lambda item:sum((v[i]-item[0][i])**2 for i in range(3)))
                p=2
            out[p][y][x]=c
    return out

def targets(role):
    common=[((0,0,0),(3,1)),((255,255,255),(2,2)),((216,40,0),(2,1))]
    if role=='RYU':common += [(RGB[0x27],(2,3))]
    body={
      'PIT':[(RGB[0x07],(0,1)),(RGB[0x26],(0,2)),(RGB[0x30],(0,3))],
      'RYGAR':[(RGB[0x16],(0,1)),(RGB[0x30],(0,2)),(RGB[0x0f],(0,3))],
      'LUIGI':[((0,168,0),(0,1)),((252,152,56),(0,2)),((123,102,1),(0,3))],
      'BASS':[((5,5,5),(0,1)),((248,152,56),(0,2)),((112,112,112),(0,3)),((248,224,160),(3,2))],
      'RYU':[((146,144,255),(0,1)),((86,29,0),(0,2)),((255,196,234),(0,3))],
      'SOPHIA':[((228,0,88),(0,1)),((255,255,255),(0,2)),((0,0,0),(0,3))],
    }[role]
    return body+common

def sheet(role):
    p=next((ROOT/'reference/crossover2/images').glob('*_'+role.title().replace('Ryu','Ryu')+'000.png'))
    return Image.open(p).convert('RGBA')

def cell(im,box):
    im=im.crop(box)
    im.putdata([(0,0,0,0) if p[:3]==(111,49,152) else p for p in im.getdata()])
    return im

def atlas_pic(role,symbol,label,part=0):
    entry=ATLAS[symbol][label]['parts'][part]
    return cell(sheet(role),entry['crop']),entry['offset']

def native(role,frame,source='reference-native'):
    base=ROOT/f'build/{source}/{role.lower()}-{frame}'
    data=base.with_suffix('.chr').read_bytes();pal=base.with_suffix('.pal').read_bytes();oam=base.with_suffix('.oam').read_bytes()
    slots=range(8,14) if role=='PIT' else range(4,8)
    valid=[oam[i*4:i*4+4] for i in slots if oam[i*4]<240]
    if not valid:
        # Native injury blinking hides the entire player on alternate frames.
        # Use the closest captured visible pose, retaining native OAM data.
        for distance in range(5,31,5):
            for other in (frame-distance,frame+distance):
                p=ROOT/f'build/{source}/{role.lower()}-{other}.oam'
                if p.exists() and any(p.read_bytes()[i*4]<240 for i in slots):
                    return native(role,other,source)
        raise ValueError((role,frame,'no visible native player'))
    left=min(p[3] for p in valid);top=min(p[0]+1 for p in valid)
    pic=Image.new('RGBA',(24,40))
    for sy,t,a,sx in valid:
        height=8 if role=='PIT' else 16
        for y in range(height):
            yy=height-1-y if a&128 else y
            addr=t*16 if height==8 else (t&1)*4096+(t&254)*16+(yy//8)*16
            for x in range(8):
                xx=7-x if a&64 else x
                v=((data[addr+yy%8]>>(7-xx))&1)|(((data[addr+8+yy%8]>>(7-xx))&1)<<1)
                if not v:continue
                color=pal[16+(a&3)*4+v]&63
                rgb=RGB.get(color,RGB[0x27])
                px,py=sx-left+x,sy+1-top+y
                if 0<=px<24 and 0<=py<40:pic.putpixel((px,py),rgb+(255,))
    pic=pic.crop(pic.getbbox())
    # Rygar's later recorded frames face left; normalize source direction.
    if role=='RYGAR' and valid[0][2]&64:pic=pic.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    return pic

def body(role,pose,power):
    out=Image.new('RGBA',(96,80));foot=(40,64)
    if role=='PIT' and pose.startswith('FLAP'):
        # The original Kid Icarus body already contains Pit's wings. Keep
        # those exact native pixels while flying, including the bow poses.
        return body(role,PIT_FLIGHT_BASE[pose],power)
    if role in ('PIT','RYGAR'):
        # Fresh, injury-free captures distinguish standing, ducking and air
        # attacks. The older late captures include damage blinking and a
        # standing Rygar frame incorrectly labelled as crouching.
        pit={'STAND':300,'JUMP':457,'CROUCH':330,'UP':512,'DIAGUP':512,'THROW':405,'CROUCHSHOOT':330,'JUMPSHOOT':462,'JUMPUP':512,'HURT':457,'DIE':330}
        rygar={'STAND':300,'JUMP':457,'CROUCH':330,'ATTACK1':300,'ATTACK2':405,'ATTACK3':405,'THROW':405,'CROUCHSHOOT':345,'JUMPSHOOT':462,'HURT':457,'DIE':330}
        if pose.startswith('WALK'):
            if pose=='WALKSTEP':return body(role,'STAND',power)
            if role=='RYGAR':
                frame={'WALK1':302,'WALK2':309,'WALK3':316}[pose]
                return rygar_walk(frame,foot,out)
            frame={'WALK1':405,'WALK2':415,'WALK3':425}[pose]
            pic=native(role,frame)
        else:
            frame=(pit if role=='PIT' else rygar).get(pose,300)
            if role=='PIT' and 'ATTACK' in pose:frame=330 if pose.startswith('CROUCH') else 457 if pose.startswith('JUMP') else 300
            if role=='RYGAR' and pose in ('ATTACK2','ATTACK3','THROW'):
                # Original standing throw after windup: the old 405 capture
                # had already caught the disk and still held it at the body.
                pic=native(role,307,'rygar-audit/native')
            else:
                pic=native(role,frame,'reference-combat')
        center=pic.width//2
        if role=='PIT' and pose=='CROUCHSHOOT':
            # Kid Icarus has no crouching shot. Keep its complete crouching
            # head/body and add the native extended bow arm at crouch height.
            arm=native(role,405,'reference-combat').crop((9,9,16,17))
            extended=Image.new('RGBA',(pic.width+5,pic.height));extended.alpha_composite(pic,(0,0));extended.alpha_composite(arm,(pic.width-2,6));pic=extended
        if role=='PIT' and pose=='JUMPUP':
            legs=native(role,457,'reference-combat').crop((0,16,18,24))
            pic=pic.copy();pic.paste((0,0,0,0),(0,16,pic.width,pic.height));pic.alpha_composite(legs,(0,16))
        out.alpha_composite(pic,(foot[0]-center,foot[1]-pic.height))
        if role=='PIT' and 'ATTACK' in pose:
            phase=int(pose[-1])-1
            hammer=weapons(role)[8].rotate((90,0,-90)[phase],expand=True)
            out.alpha_composite(hammer,(foot[0]+(1,9,10)[phase],foot[1]-pic.height+(-7,3,11)[phase]))
    elif role=='BASS':
        pos={'STAND':(1,0),'WALK1':(2,0),'WALK2':(3,0),'WALK3':(4,0),'JUMP':(8,0),'CROUCH':(1,0),'DASH':(2,2),'ATTACK1':(1,1),'ATTACK2':(1,1),'ATTACK3':(1,1),'UP':(4,3),'DIAGUP':(3,3),'DIAGDOWN':(2,3),'JUMPSHOOT':(8,1),'JUMPUP':(8,3),'JUMPDIAGUP':(6,3),'JUMPDIAGDOWN':(5,3),'CLIMB1':(6,1),'CLIMB2':(7,1),'HURT':(6,2),'DIE':(6,2)}
        # Row zero contains idle/blink, slide and jump, NOT the walk cycle.
        # The default Bass skin supplies its three normal walk cells on row 2;
        # the source timeline uses 1,2,3,2 at 100ms per animation tick.
        pos.update({'WALKSTEP':(1,2),'WALK1':(2,2),'WALK2':(3,2),'WALK3':(4,2)})
        c,r=pos.get(pose,(1,0));pic=cell(sheet(role),(1+c*36,7+r*36,36+c*36,42+r*36))
        out.alpha_composite(pic,(foot[0]-17,foot[1]-33))
    elif role=='RYU':
        # These generic pose IDs are unused by Ryu's dedicated sword/throw
        # animator. Reuse them for his native four-phase flip and Jump Slash.
        flips={'UP':'flipStart','DIAGUP':'flip-2','DIAGDOWN':'flip-3','THROW':'flip-4',
               'ATTACK1':'jumpSlashStart','ATTACK2':'jumpSlash-2','ATTACK3':'jumpSlash-3','DASH':'jumpSlash-4'}
        if pose in flips:
            entry=ATLAS['Ryu'][flips[pose]]['parts'][0]
            pic=cell(sheet(role),entry['crop']);dx,dy=entry['offset']
            out.alpha_composite(pic,(foot[0]+dx,foot[1]+dy))
            return out
        if any(pose.startswith(s) for s in ('RYUSLASH','DUCKSLASH','AIRSLASH','RYUTHROW','DUCKTHROW','AIRTHROW','WALLTHROW','BACKTHROW')):
            phase=int(pose[-1])-1
            prefix=('crouch' if pose.startswith('DUCK') else 'fall' if pose.startswith('AIR') else 'climb' if pose.startswith(('WALL','BACK')) else '')
            action='Throw' if 'THROW' in pose else 'Attack'
            if pose.startswith('BACK'):action='ThrowBackwards'
            label=prefix+action if prefix else action.lower()
            label+= 'Start' if phase==0 else '-'+str(phase+1)
            entries=ATLAS['Ryu'][label]['parts']
            selected=[entries[0]]
            if 'SLASH' in pose:
                if phase<3:selected += [e for e in entries if e['name']==('swordWaveStg' if power else 'swordStg')]
                elif power:selected += [e for e in entries if e['name']=='swordStg']
            for entry in selected:
                pic=cell(sheet(role),entry['crop']);dx,dy=entry['offset']
                if entry['name']=='swordWaveStg':
                    # Its three source weapon tones share the existing
                    # red/white/tan world palette, keeping the wave on one
                    # sprite layer without recoloring mushrooms/enemies.
                    pic.putdata([RGB[0x27]+(p[3],) if p[3] and p[:3]==(255,196,234) else p for p in pic.getdata()])
                out.alpha_composite(pic,(foot[0]+dx,foot[1]+dy))
            return out
        labels={'STAND':'standStart','WALK1':'walkStart','WALK2':'walk-2','WALK3':'walk-3','JUMP':'fall','CROUCH':'crouch','THROW':'throw-3','CLIMB1':'climbStart','CLIMB2':'climbEnd','WALL':'climbStop','HURT':'takeDamage','DIE':'die'}
        if 'ATTACK' in pose:
            phase=int(pose[-1])-1
            prefix='crouchAttack' if pose.startswith('CROUCH') else 'fallAttack' if pose.startswith('JUMP') else 'attack'
            label=prefix+('Start','-3','End')[phase]
        else:label=labels.get(pose,'standStart')
        pic,offset=atlas_pic(role,'Ryu',label)
        out.alpha_composite(pic,(foot[0]+offset[0],foot[1]+offset[1]))
        if 'ATTACK' in pose:
            sword=cell(sheet(role),(44,243,86,264));sword=sword.crop(sword.getbbox())
            # Keep the complete arc in the shared red/white palette. Using
            # the body's skin tone for its pink outline adds another layer
            # across the blade and can exceed eight sprites on one scanline.
            sword.putdata([(255,255,255,p[3]) if min(p[:3])>=230 else (216,40,0,p[3]) for p in sword.getdata()])
            sword=sword.resize((24 if power else 16,sword.height),Image.Resampling.NEAREST)
            sy=foot[1]-(20 if pose.startswith('CROUCH') else 29 if pose.startswith('JUMP') else 27)
            out.alpha_composite(sword,(foot[0]+5,sy))
    elif role=='LUIGI':
        labels={'STAND':'stand','WALK1':'walk-1','WALK2':'walk-2','WALK3':'walk-3','JUMP':'jumpStart','ATTACK1':'shoot','ATTACK2':'shoot','ATTACK3':'shoot','CLIMB1':'climbStart','CLIMB2':'climbEnd','HOVER':'swimStillStart','CROUCH':'crouch','DASH':'skid'}
        suffix='_1' if power==0 else '_2'
        label=labels.get(pose,'stand')+suffix
        if pose.startswith('ATTACK') and power==0:label='stand_1'
        if pose=='CROUCH' and power==0:label='stand_1'
        if pose=='DIE':label='die_1'
        if pose=='HURT':label='takeDamageStart' if power else 'stand_1'
        pic,offset=atlas_pic(role,'Mario',label)
        out.alpha_composite(pic,(foot[0]+offset[0],foot[1]+offset[1]))
    else:
        if pose.startswith('DEATH'):
            frame=(16,17,19,20)[int(pose[-1])-1]
            pic,offset=atlas_pic(role,'SophiaExplosion','#'+str(frame))
            out.alpha_composite(pic,(foot[0]+offset[0],foot[1]+offset[1]))
            return out
        up=pose in ('UP','DIAGUP','JUMPUP','THROW','JUMPDIAGDOWN')
        pic,offset=atlas_pic(role,'SophiaBase','up' if up else 'horz')
        out.alpha_composite(pic,(foot[0]+offset[0],foot[1]+offset[1]-(8 if up else 2)))
        wheel_label={'WALK1':'roll-1','WALK2':'roll-3','WALK3':'roll-4','HOVER':'hoverBigFlame','HOVERSMALL':'hoverSmallFlame'}.get(pose,'roll-1')
        for component,x in [('SophiaFrontWheel',8),('SophiaBackWheel',-8)]:
            parts=ATLAS[component][wheel_label]['parts']
            for entry in parts:
                pic=cell(sheet(role),entry['crop']);dx,dy=entry['offset']
                out.alpha_composite(pic,(foot[0]+x+dx,foot[1]+dy-(0 if pose=='JUMP' else 4)))
        if pose in ('WALL','CEILING','DIAGUP','DIAGDOWN','THROW','JUMPDIAGDOWN'):
            bounds=out.getbbox();pic=out.crop(bounds)
            if pose in ('CEILING','DIAGUP'):
                # The source reverses local scale on the ceiling. Its muzzle
                # keeps the same horizontal facing while the body inverts.
                pic=pic.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                anchor=(foot[0]-pic.width//2,39)
            else:
                origin_y=pic.width-1-(foot[0]-bounds[0])
                pic=pic.rotate(90,expand=True)
                if pose in ('DIAGDOWN','JUMPDIAGDOWN'):
                    pic=pic.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                    origin_y=pic.height-1-origin_y
                # Right-side contact is x+14. Tangential source origin is
                # y+18; keep it fixed as the cannon turns or reverses.
                anchor=(47-pic.width,50-origin_y)
            out=Image.new('RGBA',out.size);out.alpha_composite(pic,anchor)
    return out

def rygar_walk(frame,foot,out):
    base=ROOT/f'build/rygar-audit/walk/rygar-{frame}'
    data=base.with_suffix('.chr').read_bytes();pal=base.with_suffix('.pal').read_bytes();oam=base.with_suffix('.oam').read_bytes()
    # Native OAM trails the actor by one update. Keep its actual logical origin
    # ($0512 + 8), not the center of a varying arm/leg bounding rectangle.
    previous=(base.parent/f'rygar-{frame-1}.ram').read_bytes()
    origin=previous[0x512]+8
    # The middle walking frame expands to SIX native pieces, using slots2/3
    # for its lower body. Other frames hide those slots above$ef.
    for i in range(2,8):
        sy,t,a,sx=oam[i*4:i*4+4]
        if sy>=240:continue
        for y in range(16):
            yy=15-y if a&128 else y
            addr=(t&1)*4096+(t&254)*16+(yy//8)*16
            for x in range(8):
                xx=7-x if a&64 else x
                v=((data[addr+yy%8]>>(7-xx))&1)|(((data[addr+8+yy%8]>>(7-xx))&1)<<1)
                if v:out.putpixel((foot[0]+sx+x-origin,foot[1]+sy+1+y-195),RGB[pal[16+(a&3)*4+v]&63]+(255,))
    return out

def rygar_walk_left(pose):
    # The native left middle frame has its own one-pixel seam placements;
    # mirroring the right silhouette loses those original per-piece offsets.
    frame={'WALK1':432,'WALK2':440,'WALK3':447}[pose]
    return rygar_walk(frame,(40,64),Image.new('RGBA',(96,80)))

def rygar_native_raw(lines,name,right,left):
    packing.raw(lines,name,right,mirror=False)
    packing.raw(lines,name+'NativeLeft',left,mirror=False)
    lines.append(name+'Left = '+name+'NativeLeftRight')

def native_tile(role,frame,tile,height=8):
    base=ROOT/f'build/reference-native/{role.lower()}-{frame}';data=base.with_suffix('.chr').read_bytes();pal=base.with_suffix('.pal').read_bytes()
    out=Image.new('RGBA',(8,height))
    for y in range(height):
        addr=tile*16 if height==8 else (tile&1)*4096+(tile&254)*16+(y//8)*16
        for x in range(8):
            v=((data[addr+y%8]>>(7-x))&1)|(((data[addr+y%8+8]>>(7-x))&1)<<1)
            if v:out.putpixel((x,y),RGB.get(pal[16+v]&63,RGB[0x30])+(255,))
    return out

def weapons(role):
    # Four horizontal animation phases, four vertical phases, then a special.
    if role=='PIT':
        p=native_tile(role,655,60);long=p.resize((16,8),Image.Resampling.NEAREST)
        fire=long.copy()
        for y in range(2,6):
            for x in range(3):fire.putpixel((x,y),RGB[0x16]+(255,))
        pics=[p,long,fire,fire]+[p.rotate(90,expand=True),long.rotate(90,expand=True),fire.rotate(90,expand=True),fire.rotate(90,expand=True)]
        # A hammer is an adaptation of Pit's native weapon, drawn in 2bpp.
        hammer=Image.new('RGBA',(12,12));pix=hammer.load()
        for y in range(2,10):
            for x in range(2,10):
                if y<5 or 5<=x<=6:pix[x,y]=RGB[0x30]+(255,)
        pics += [hammer]
    elif role=='RYGAR':
        discs=[]
        for tile in (70,72):
            half=native_tile(role,655,tile,16);disc=Image.new('RGBA',(16,16));disc.alpha_composite(half,(0,0));disc.alpha_composite(half.transpose(Image.Transpose.FLIP_LEFT_RIGHT).transpose(Image.Transpose.FLIP_TOP_BOTTOM),(8,0));discs.append(disc)
        a,b=discs
        pics=[a,b,a,b]*2+[native_tile(role,655,76,16)]
    elif role=='BASS':
        source=sheet(role);p=cell(source,(253,115,271,133));p=p.crop(p.getbbox());pics=[p]*8+[p]
    elif role=='RYU':
        source=sheet(role);pics=[]
        for c in range(4):
            p=cell(source,(130+c*21,222,150+c*21,242));pics.append(p.crop(p.getbbox()))
        large=[]
        for c in range(4):
            p=cell(source,(130+c*21,243,150+c*21,264));large.append(p.crop(p.getbbox()))
        pics=pics+large+[pics[0]]
    elif role=='LUIGI':
        pics=[atlas_pic(role,'MarioFireBall','#'+str(c))[0] for c in range(1,5)];pics=[p.crop(p.getbbox()) for p in pics];pics=pics+pics+[pics[0]]
    else:
        # Apply the source SWF masks/matrices before packing. The first eight
        # entries are normal, Hyper and Crusher; the next eight are the same
        # source pixels rotated upward. Missiles and impacts use the same stable native prefix so all body
        # poses preserve simultaneous primary/secondary/effect graphics.
        import xml.etree.ElementTree as ET
        from build_remaining_art import extract
        from prepare_crossover import frames
        items=list(ET.parse(ROOT/'reference/crossover2/main.xml').getroot().iter('item'))
        symbols={}
        for t in items:
            if t.get('type') in ('SymbolClassTag','ExportAssetsTag') and t.find('tags') is not None:
                symbols.update({n.text:i.text for i,n in zip(t.find('tags'),t.find('names'))})
        timeline=next(t for t in items if t.get('type')=='DefineSpriteTag' and t.get('spriteId')==symbols['SophiaBullet'])
        source=extract(frames(timeline),44,sheet(role))
        pics=[source[c-1].crop(source[c-1].getbbox()) for c in (1,2,3,1,8,9,10,11)]
        horizontal=pics[:]
        for turn in (90,180,270):pics += [p.rotate(turn,expand=True) for p in horizontal]
        missiles=[source[c-1].crop(source[c-1].getbbox()) for c in (5,6,7)]
        for turn in (0,90,180,270):pics += [p.rotate(turn,expand=True) for p in missiles]
        unlit=source[3].crop(source[3].getbbox())
        pics += [unlit.rotate(turn,expand=True) for turn in (0,90,180,270)]
        # Small source impact effects share the same stable weapon prefix.
        for frame in range(1,6):
            if ATLAS['SophiaExplosion']['#'+str(frame)]['parts']:
                p=atlas_pic(role,'SophiaExplosion','#'+str(frame))[0]
                pics.append(p.crop(p.getbbox()))
            else:pics.append(Image.new('RGBA',(1,1)))
    return pics

def native_pit_flight_tables():
    """Reuse existing body records and CHR banks without repacking other guests."""
    path=ROOT/'src/pit_metasprites.inc'
    text=path.read_text()
    tables={}
    for suffix in ('LeftLo','LeftHi','RightLo','RightHi','Banks'):
        marker='XgPIT'+suffix+':\n .byte '
        assert text.count(marker)==1,suffix
        values=text.split(marker,1)[1].split('\n',1)[0].split(',')
        assert len(values)==len(POSES)*3,(suffix,len(values))
        tables[suffix]=values
    for power in range(3):
        offset=power*len(POSES)
        for pose,base in PIT_FLIGHT_BASE.items():
            dest=offset+POSES.index(pose);source=offset+POSES.index(base)
            for values in tables.values():values[dest]=values[source]
    for suffix,values in tables.items():
        marker='XgPIT'+suffix+':\n .byte '
        prefix,tail=text.split(marker,1)
        old,rest=tail.split('\n',1)
        text=prefix+marker+','.join(values)+'\n'+rest
    path.write_text(text)
    print('Pit flight uses existing native wing/body/bow records; CHR and other guests unchanged',flush=True)


def main():
    global ROLE,COLORS,BASS_PROJECTILE
    parser=argparse.ArgumentParser()
    parser.add_argument('--sophia-only',action='store_true',help='Replace only the final Sophia banks and tables, preserving all other guest assets')
    parser.add_argument('--pit-flight-only',action='store_true',help='Bind flight to Pit native wing/body records while retaining existing CHR placement')
    args=parser.parse_args()
    if args.pit_flight_only:
        assert not args.sophia_only
        native_pit_flight_tables()
        return
    assets.layers=layers;assets.OAM_PRIORITY=True
    all_banks=[];manifest={};first=0xd1+len((ROOT/'chr/characters/crossover-roster-high.chr').read_bytes())//1024
    roles=ROLES
    if args.sophia_only:
        manifest=json.loads((ROOT/'docs/reference/expanded-assets.json').read_text())
        old=(ROOT/'chr/characters/crossover-expanded.chr').read_bytes()
        boundary=(manifest['SOPHIA']['first_chr']-first)*1024
        all_banks=[old[i:i+1024] for i in range(0,boundary,1024)]
        roles=['SOPHIA']
    for role in roles:
        ROLE=role;COLORS=targets(role);assets.SCANLINE_PRIORITY=role in ('BASS','RYU');packing.RAW_CACHE.clear();pool=[];weapon_parts=[];lines=['; Generated from pinned native guest references.','.pushseg',f'.segment "XG_{role}_GFX"']
        BASS_PROJECTILE=role=='BASS'
        for i,pic in enumerate(weapons(role)):
            rotated_from=(i-16 if 16<=i<32 else i-6 if 38<=i<44 else i-2 if 46<=i<48 else None) if role=='SOPHIA' else None
            if rotated_from is not None:
                # Rotating a complete metasprite by 180 degrees needs only
                # coordinate/attribute changes, preserving exact tile pixels.
                ps=[(t,p^0xc0,-x-8,-y-16) for t,p,x,y in weapon_parts[rotated_from]]
            else:
                im=Image.new('RGBA',(48,48));im.alpha_composite(pic,((48-pic.width)//2,(48-pic.height)//2));ps=packing.parts(im,(24,24),pool)
            weapon_parts.append(ps);packing.raw(lines,'Xg'+role+'Weapon'+str(i),ps,axis=0)
        assert len(pool)<26,(role,'weapon pairs',len(pool))
        BASS_PROJECTILE=False
        groups=[];group_death=[];entries=[];maxsprites=0;maxscanline=0
        cache={};shared_body_pool=pool[:]
        for power in range(3):
            for pose in POSES:
                im=body(role,pose,power)
                left_im=rygar_walk_left(pose) if role=='RYGAR' and pose in ('WALK1','WALK2','WALK3') else None
                key=im.tobytes()+(left_im.tobytes() if left_im else b'')
                if key not in cache:
                    death=role=='SOPHIA' and pose.startswith('DEATH')
                    local=[] if death else shared_body_pool[:] if role=='RYU' else pool[:]
                    ps=packing.parts(im,(32,32),local)
                    if role=='RYU':
                        shared_body_pool=local[:]
                        compact=pool[:]
                        for t,p,x,y in ps:
                            if local[t//2]not in compact:compact.append(local[t//2])
                        ps=[(compact.index(local[t//2])*2,p,x,y)for t,p,x,y in ps];local=compact
                    left_ps=packing.parts(left_im,(32,32),local) if left_im else None
                    assert len(local)<=32,(role,pose,len(local));cache[key]=(ps,local,left_ps)
                ps,local,left_ps=cache[key];maxsprites=max(maxsprites,len(ps),len(left_ps or []))
                if ps:maxscanline=max(maxscanline,max(sum(y<=scan<y+16 for t,p,x,y in ps) for scan in range(-32,64)))
                death=role=='SOPHIA' and pose.startswith('DEATH')
                candidates=[(sum(data not in g for data in local),len(g),i) for i,g in enumerate(groups) if group_death[i]==death and len(g)+sum(data not in g for data in local)<=32]
                if candidates:gi=min(candidates)[2]
                else:gi=len(groups);groups.append([] if death else pool[:]);group_death.append(death)
                for data in local:
                    if data not in groups[gi]:groups[gi].append(data)
                ps=[(groups[gi].index(local[t//2])*2,p,x,y) for t,p,x,y in ps]
                name=f'Xg{role}{power}_{pose}'
                if left_ps is not None:
                    left_ps=[(groups[gi].index(local[t//2])*2,p,x,y)for t,p,x,y in left_ps]
                    rygar_native_raw(lines,name,ps,left_ps)
                else:packing.raw(lines,name,ps)
                entries.append((name,gi))
                out=ROOT/f'build/reference-frames/{role}-{power}-{pose}.png';out.parent.mkdir(parents=True,exist_ok=True);im.save(out)
        if role=='RYU':assert maxscanline<=8,f'Sword/body color layers exceed the native scanline budget: {maxscanline}'
        if role=='BASS':assert maxscanline<=8,'Bass body alone exceeds the native scanline budget'
        ids=[]
        for group in groups:
            data=b''.join(group)+bytes(1024-32*len(group))
            if data not in all_banks:all_banks.append(data)
            logical=first+all_banks.index(data)
            ids.append(logical if logical<0xf4 else 0xad+logical-0xf4)
        for suffix,fmt in [('LeftLo','<{}Left'),('LeftHi','>{}Left'),('RightLo','<{}Right'),('RightHi','>{}Right')]:lines += ['Xg'+role+suffix+':',' .byte '+','.join(fmt.format(n) for n,g in entries)]
        lines+=['Xg'+role+'Banks:',' .byte '+','.join(f'${ids[g]:02x}' for n,g in entries)]
        for suffix,fmt in [('WeaponLo','<{}Right'),('WeaponHi','>{}Right'),('WeaponLeftLo','<{}Left'),('WeaponLeftHi','>{}Left')]:lines+=['Xg'+role+suffix+':',' .byte '+','.join(fmt.format('Xg'+role+'Weapon'+str(i)) for i in range(len(weapon_parts)))]
        lines+=['.popseg'];(ROOT/f'src/{role.lower()}_metasprites.inc').write_text('\n'.join(lines)+'\n')
        manifest[role]={'poses':len(entries),'weapon_pairs':len(pool),'maximum_sprites':maxsprites,'maximum_sprites_per_scanline':maxscanline,'chr_banks':len(ids),'first_chr':ids[0]}
        if role=='SOPHIA':
            live=sorted({ids[i] for i,death in enumerate(group_death) if not death})
            manifest[role]['live_chr']=live
            manifest[role]['death_chr']=sorted({ids[i] for i,death in enumerate(group_death) if death})
            (ROOT/'tests/fixtures/sophia-live-banks.lua').write_text('-- Generated bank coverage only; expected pixels are independently pinned.\nreturn {'+','.join(map(str,live))+'}\n')
        print(role,manifest[role],flush=True)
    # $f4 onward belongs to Bass's independent special body banks.
    assert first+len(all_banks)<=0xf8,(first,len(all_banks))
    split=0xf4-first
    (ROOT/'chr/characters/crossover-expanded.chr').write_bytes(b''.join(all_banks[:split]))
    (ROOT/'chr/characters/crossover-sophia-extra.chr').write_bytes(b''.join(all_banks[split:]))
    if not args.sophia_only:
        (ROOT/'src/expanded_poses.inc').write_text('XG_POSE_COUNT='+str(len(POSES))+'\n'+'\n'.join('XG_POSE_'+p+'='+str(i) for i,p in enumerate(POSES))+'\n')
    manifest['unique_chr_banks']=len(all_banks);manifest['source']='Crossover 2.02 default NES sheets; Pit/Rygar controller captures of local original NES ROMs'
    (ROOT/'docs/reference/expanded-assets.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Expanded CHR',len(all_banks),'banks; Sophia live',manifest['SOPHIA'].get('live_chr'),'auxiliary',manifest['SOPHIA'].get('death_chr'),flush=True)

if __name__=='__main__':main()
