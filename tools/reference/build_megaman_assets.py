"""Build NES metasprites and CHR directly from the pinned hosted game frames."""
from __future__ import annotations

import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OAM_PRIORITY = False
SCANLINE_PRIORITY = False
REF = ROOT/'reference/crossover'
POSES = ['STAND', 'WALK1', 'WALK2', 'WALK3', 'WALK4', 'SHOOT',
         'WALKSHOOT1', 'WALKSHOOT2', 'WALKSHOOT3', 'WALKSHOOT4',
         'JUMP', 'JUMPSHOOT', 'SLIDE', 'CLIMB1', 'CLIMB2', 'HURT']
BODY_FRAMES = [4,5,6,7,8,3,9,10,11,12,15,16,19,17,18,13]


def read_meta(id):
    return json.loads((REF/f'frames-{id}.json').read_text())


def sprite_image(meta, frame):
    return Image.open(ROOT/meta['png_directory']/f'{frame}.png').convert('RGBA')


def encode_pair(pixels):
    return bytes(sum(((pixels[y+half*8][x] >> plane)&1) << (7-x) for x in range(8))
                 for half in range(2) for plane in range(2) for y in range(8))


def layers(image, projectile=False):
    # The hosted art uses standard NES colors. Skin shares palette 3 and
    # white shares palette 2; suit colors use palette 0.
    targets = [(0,0,0),(0,112,236),(0,232,216),(252,252,252),
               (252,216,168),(216,40,0),(240,188,60)]
    colors = ((3 if projectile else 0,1),(0,2),(0,3),(2,2),(3,2),(0,2),(0,3))
    result = {palette: [[0]*image.width for _ in range(image.height)] for palette in (0,2,3)}
    for y in range(image.height):
        for x in range(image.width):
            value = image.getpixel((x,y))
            if value[3] < 128:
                continue
            closest = min(range(len(targets)), key=lambda i: sum((value[c]-targets[i][c])**2 for c in range(3)))
            palette, color = colors[closest]
            result[palette][y][x] = color
    return result


def parts(image, origin, pool, projectile=False):
    result = []
    for palette, pixels in layers(image,projectile).items():
        occupied = [(x,y) for y,row in enumerate(pixels) for x,value in enumerate(row) if value]
        if not occupied:
            continue
        xmin=min(x for x,y in occupied); xmax=max(x for x,y in occupied)
        ymin=min(y for x,y in occupied); ymax=max(y for x,y in occupied)
        best=None
        for dx in range(8):
            for dy in range(16):
                candidate=[]
                for y in range(ymin-dy,ymax+1,16):
                    for x in range(xmin-dx,xmax+1,8):
                        block = [[pixels[yy][xx] if 0<=yy<image.height and 0<=xx<image.width else 0
                                  for xx in range(x,x+8)] for yy in range(y,y+16)]
                        data=encode_pair(block)
                        if any(data): candidate.append((data,x,y))
                new=sum(data not in pool for data,x,y in candidate)
                if SCANLINE_PRIORITY:
                    # Different palette layers can use different tile grids.
                    # Count their combined scanline load before choosing the
                    # next grid, rather than minimizing each layer in isolation.
                    load=max(sum(py<=line<py+16 for _,_,_,py in result)+sum(py-origin[1]<=line<py-origin[1]+16 for _,_,py in candidate) for line in range(-origin[1]-16,image.height-origin[1]+16))
                    score=(load,len(candidate),new,dx+dy)
                else:
                    score=(len(candidate),new,dx+dy) if OAM_PRIORITY else (new,len(candidate),dx+dy)
                if best is None or score<best[0]: best=(score,candidate)
        for data,x,y in best[1]:
            if data not in pool: pool.append(data)
            result.append((pool.index(data)*2,palette,x-origin[0],y-origin[1]))
    return result


def emit_metasprite(lines, name, parts_, mirrored=True, bank='SPRITE_BANK_0', axis=16):
    left = f'Mm{name}Left'
    right = f'Mm{name}Right'
    lines.append(f'MetaspriteData "{name}", {left if mirrored else right}, {right}')
    for facing in (('Left','Right') if mirrored else ('Right',)):
        lines += [f'Mm{name}{facing}:', f'  .byte {len(parts_)*4}']
        for tile,palette,x,y in parts_:
            if facing == 'Left':
                x = axis-x-8
                palette |= 0x40
            lines.append(f'  .byte MetaspriteVramOffset{{${tile:02x}}}, {{{bank}}}, ${palette:02x}, {y}, {x}')


def main():
    body = read_meta('691'); head = read_meta('73'); bullet = read_meta('1270')
    outline=read_meta('1643'); particle=read_meta('1673')
    head_labels = {label:frame['frame'] for frame in head['frames'] for label in frame['labels']}
    # All uncharged and weak shots share stable tile IDs in every body bank.
    # Full shots use the spare sprite area at PPU $0c00 on MMC3 (independent
    # sprite bank 4 on MMC5). Preserve Bowser's tile pairs in that area.
    common_frames = (1,2,3,4,5,10,11,12)
    pool = []
    bullet_parts = {}
    strong_pools = []
    for frames in (common_frames,(6,7,8),(13,14,15)):
        current = pool if frames == common_frames else []
        for frame in frames:
            canvas = Image.new('RGBA',(64,64))
            canvas.alpha_composite(sprite_image(bullet,frame),
                                   (round(32-bullet['origin'][0]),round(32-bullet['origin'][1])))
            canvas = canvas.resize((32,32),Image.Resampling.NEAREST)
            bullet_parts[frame] = parts(canvas,(16,16),current,True)
        if frames != common_frames:
            strong_pools.append(current)
    print('Common projectile tile pairs:',len(pool))
    lines = ['; Generated from the pinned hosted SWF; see docs/reference/crossover.json.',
             '.pushseg', '.segment "GUEST_GFX"']
    binary = bytearray()
    wind_binary = bytearray()
    banks = []
    maximum = 0
    body_groups=[]
    skins = ('HAIR','HELMET','FIRE','WIND')
    jobs = [(power, prefix, pose, frame) for power, prefix in enumerate(skins)
            for pose, frame in zip(POSES, BODY_FRAMES)]
    # Keep the original sixteen-pose skin strides and bullet IDs derived by
    # labels. The source 2.02 walk-0 timing uses this hosted skin's step frame.
    jobs += [(power, prefix, 'STEP', 2) for power, prefix in enumerate(skins)]
    for power, prefix, pose, frame in jobs:
        body_frame = frame+23 if power==2 else frame
        canvas = Image.new('RGBA',(64,64))
        canvas.alpha_composite(sprite_image(body,body_frame),
                               (round(32-body['origin'][0]),round(64-body['origin'][1])))
        if power!=2:
            state = body['frames'][body_frame-1]['display']
            placement = next(value for value in state.values() if value.get('characterId')=='73')
            matrix = placement['matrix']
            if pose.startswith('CLIMB'):
                action = 'climb'
            elif pose in ('JUMP','JUMPSHOOT','SLIDE'):
                action = 'openOpen'
            elif pose in ('WALK3','WALKSHOOT3'):
                action = 'covered'
            elif pose=='HURT':
                action='closedOpen'
            else:
                action = 'openClosed'
            wind = power==3 and pose not in ('STAND','STEP','SHOOT','CLIMB1','CLIMB2','HURT')
            if wind: action+='Wind'
            head_frame = head_labels[f'{action}_{2 if power==1 else 1}']
            head_canvas=Image.new('RGBA',(64,64))
            head_canvas.alpha_composite(sprite_image(head,head_frame),
                (round(32-head['origin'][0]),round(32-head['origin'][1])))
            if power in (0,3):
                head_canvas.alpha_composite(sprite_image(outline,2 if wind else 1),
                    (round(33-outline['origin'][0]),round(28-outline['origin'][1])))
            canvas.alpha_composite(head_canvas,
                (round(int(matrix.get('translateX',0))/20),
                 round(32+int(matrix.get('translateY',0))/20)))
        canvas = canvas.resize((32,32),Image.Resampling.NEAREST)
        local_pool = pool[:]
        body_parts = parts(canvas,(8,0),local_pool)
        maximum = max(maximum,len(body_parts))
        if len(local_pool)>32:
            raise RuntimeError(f'{prefix} {pose} needs {len(local_pool)} tile pairs; 1 KiB holds 32')
        extra=local_pool[len(pool):]
        choices=[(sum(t not in g for t in extra),i) for i,g in enumerate(body_groups)
                 if len(g)+sum(t not in g for t in extra)<=32]
        if choices:group=min(choices)[1]
        else:group=len(body_groups);body_groups.append(pool[:])
        for t in extra:
            if t not in body_groups[group]:body_groups[group].append(t)
        body_parts=[(body_groups[group].index(local_pool[t//2])*2,p,x,y)for t,p,x,y in body_parts]
        assert group<48,group
        banks.append(0x40+group)
        emit_metasprite(lines,f'MM_{prefix}_{pose}',body_parts)
        path = ROOT/f'build/reference-frames/{prefix}-{pose}.png'
        path.parent.mkdir(parents=True,exist_ok=True)
        canvas.save(path)
    binary=b"".join(b"".join(g)+bytes(1024-len(g)*32)for g in body_groups)
    binary+=bytes(48*1024-len(binary))
    wind_binary=bytes(16*1024)
    reserved = {offset//2 for offset in (4,6,8,10,12,14,32,34,36,38,40)}
    free = [i for i in range(32) if i not in reserved]
    for family, frames in enumerate(((6,7,8),(13,14,15))):
        assert len(strong_pools[family]) <= len(free)
        for frame in frames:
            bullet_parts[frame] = [(free[tile//2]*2,pal,x,y) for tile,pal,x,y in bullet_parts[frame]]
    bullet_parts[9] = bullet_parts[3]
    bullet_parts[16] = bullet_parts[15]
    for frame in range(1,17):
        emit_metasprite(lines,f'MM_BULLET_{frame}',bullet_parts[frame],
                        bank='SPRITE_BANK_4' if frame in (6,7,8,13,14,15,16) else 'SPRITE_BANK_0',axis=0)
    particle_pool=[]
    for frame in range(1,5):
        canvas=sprite_image(particle,frame).resize((16,16),Image.Resampling.NEAREST)
        part=parts(canvas,(8,8),particle_pool)
        emit_metasprite(lines,f'MM_PARTICLE_{frame}',part,False,axis=0)
    assert len(particle_pool)<=32
    particle_binary=b''.join(particle_pool)+bytes(1024-len(particle_pool)*32)
    lines += ['.popseg']
    # $40..$6f contain the body; $70..$7f contain full-charge variants.
    for mapper in ('mmc3','mmc5'):
        output = bytearray(binary)
        for current in strong_pools:
            for area in ('water','ground','underground','castle'):
                original = (ROOT/f'chr/mmc5/bg_{area}.chr').read_bytes()[2048:4096]
                block=bytearray(original)
                if mapper == 'mmc5':
                    block[1024:2048]=(ROOT/'chr/mmc5/sprites_enemies.chr').read_bytes()[2048:3072]
                for index,data in enumerate(current):
                    block[1024+free[index]*32:1024+(free[index]+1)*32]=data
                output += block
        output += wind_binary+particle_binary
        (ROOT/f'chr/characters/crossover-megaman-{mapper}.chr').write_bytes(output)
    lines += ['.pushseg','.segment "FIXED"','MegaManSpriteBanks:',
              '  .byte '+', '.join(f'${bank:02x}' for bank in banks), '.popseg',
              f'MEGAMAN_POSE_COUNT = {len(POSES)}', 'CHR_MM_DEATH = $90',f'MEGAMAN_MAX_SPRITES = {maximum}',
              'METASPRITE_MM_FIRST_BULLET = METASPRITE_MM_BULLET_1',
              'METASPRITE_MEGAMAN_STANDING = METASPRITE_MM_HAIR_STAND',
              'METASPRITE_MEGAMAN_RUNNING_1 = METASPRITE_MM_HAIR_WALK1',
              'METASPRITE_MEGAMAN_RUNNING_2 = METASPRITE_MM_HAIR_WALK2',
              'METASPRITE_MEGAMAN_JUMPING = METASPRITE_MM_HAIR_JUMP',
              'METASPRITE_MEGAMAN_SHOOTING = METASPRITE_MM_HAIR_SHOOT',
              'METASPRITE_MEGAMAN_BULLET = METASPRITE_MM_BULLET_1']
    (ROOT/'src/megaman_metasprites.inc').write_text('\n'.join(lines)+'\n')
    print(f'Built {len(banks)} character banks; max OAM entries {maximum}; {len(output)} CHR bytes per mapper')


if __name__=='__main__':
    main()
