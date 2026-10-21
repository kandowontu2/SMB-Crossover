"""Pack the remaining hosted characters into the unused MMC3 CHR banks."""
from pathlib import Path
import json
from PIL import Image
import build_megaman_assets as assets
import build_samus_assets as packing

ROOT=assets.ROOT
NAMES=['STAND','WALK1','WALK2','WALK3','JUMP1','JUMP2','JUMP3','JUMP4','CROUCH',
 'ATTACK1','ATTACK2','ATTACK3','THROW1','THROW2','THROW3','CLIMB1','CLIMB2',
 'UPSTAND','DIAGUP','DIAGDOWN','UPWALK1','UPWALK2','UPWALK3',
 'DIAGUPWALK1','DIAGUPWALK2','DIAGUPWALK3','DIAGDOWNWALK1','DIAGDOWNWALK2','DIAGDOWNWALK3',
 'DOWNTHRUST','UPTHRUST','HURT','DIE1','DIE2','DIE3','DIE4','SLIDE',
 'CROUCHATTACK1','CROUCHATTACK2','CROUCHATTACK3','CROUCHTHROW1','CROUCHTHROW2','CROUCHTHROW3',
 'DIEFLASH1','DIEFLASH2','DIEGRAY','DIECROSS1','DIECROSS2']

TARGETS=[]
CACHE={}
CURRENT_ROLE=''
CURRENT_POWER=0

def layers(image,projectile=False):
    result={p:[[0]*image.width for _ in range(image.height)] for p in (0,2,3)}
    body_columns=[]
    if CURRENT_ROLE=='SIMON' and CURRENT_POWER==2:
        body_columns=[x for y in range(image.height) for x in range(image.width)
          if image.getpixel((x,y))[3]>=128 and image.getpixel((x,y))[:3] in ((0,0,0),(222,59,60))]
    body_bounds=(min(body_columns),max(body_columns)) if body_columns else (1,0)
    for y in range(image.height):
        for x in range(image.width):
            v=image.getpixel((x,y))
            if v[3]<128:continue
            rgb,(p,c)=min(TARGETS,key=lambda item:sum((v[i]-item[0][i])**2 for i in range(3)))
            # The body and flame have the same NES white but different palettes.
            # Keep the body's three colors together instead of laying white
            # sprites over both the body and the long flame.
            if CURRENT_ROLE=='SIMON' and CURRENT_POWER==2 and min(v[:3])>=230 and body_bounds[0]<=x<=body_bounds[1]:
                p,c=0,3
            result[p][y][x]=c
    return result

def targets(role,power):
    global TARGETS,CURRENT_ROLE,CURRENT_POWER
    CURRENT_ROLE,CURRENT_POWER=role,power
    if role=='BILL':
        main=[(25,57,139),(0,88,248),(255,0,0)][power]
        body=[main,(248,56,0),(255,206,198)]
    elif role=='LINK':
        main=[(138,217,1),(184,248,248),(220,67,22)][power]
        body=[main,(151,78,0),(255,160,68)]
    else:
        body=[[(82,33,0),(136,20,0),(0,0,0)][power],
          [(231,156,33),(255,146,41),(222,59,60)][power],(247,214,165)]
    TARGETS=[(rgb,(0,i+1)) for i,rgb in enumerate(body)]
    if role!='SIMON' or power<2:TARGETS += [((0,0,0),(3,1))]
    TARGETS += [((255,255,255),(2,2)),((252,252,252),(2,2))]
    if role=='BILL':
        TARGETS=[(main,(0,1)),((255,206,198),(0,2)),((255,224,168),(0,2)),
          ((0,0,0),(0,3)),((248,56,0),(0,1) if power==2 else (2,1)),((255,255,255),(2,2))]
    if role=='SIMON':
        # Preserve the world-object palette. Axe outlines share palette 3's
        # black; its two blade tones use the existing white/tan entries.
        TARGETS += [((152,120,248),(2,2)),((248,184,248),(2,3)),
          ((198,115,255),(2,2)),((247,198,255),(2,3))]
        if power==2:
            TARGETS=[((0,0,0),(0,1)),((222,59,60),(0,2)),
              ((255,255,255),(2,2)),((248,56,0),(2,1)),((252,152,56),(2,3))]

def place(im,meta,frame,foot=(80,96),offset=(0,0)):
    im.alpha_composite(assets.sprite_image(meta,frame),
      (round(foot[0]+offset[0]-meta['origin'][0]),round(foot[1]+offset[1]-meta['origin'][1])))

def image(meta,frame,foot=(80,96),size=(256,128)):
    im=Image.new('RGBA',size);place(im,meta,frame,foot)
    return im.resize((size[0]//2,size[1]//2),Image.Resampling.NEAREST)

def getframe(meta,label,fallback=2):
    return next((f['frame'] for f in meta['frames'] if label in f['labels']),fallback)

def pose_image(role,power,pose,meta):
    if role=='BILL':
        im=Image.new('RGBA',(256,128));p=power+1
        legs=assets.read_meta('1141');torso=assets.read_meta('1152')
        if pose=='CROUCH':
            place(im,assets.read_meta('1131'),p)
        elif pose.startswith('JUMP'):
            frame=getframe(meta,f'jumpStart_{p}')+int(pose[-1])-1
            place(im,meta,frame)
        elif pose.startswith('CLIMB'):
            place(im,meta,getframe(meta,('climbStart' if pose.endswith('1') else 'climbEnd')+f'_{p}'))
        elif pose.startswith('DIE') or pose=='HURT':
            place(im,meta,10+min(4,int(pose[-1])-1) if pose.startswith('DIE') and pose[-1].isdigit() else 10)
        else:
            phase=int(pose[-1]) if pose[-1].isdigit() else 0
            legframe=getframe(legs,f'walk-{phase}_{p}',getframe(legs,f'walkEnd_{p}')) if phase else getframe(legs,f'stand_{p}')
            torsoframe=1
            if pose.startswith('UP'):torsoframe=2
            elif pose.startswith('DIAGUP'):torsoframe=3
            elif pose.startswith('DIAGDOWN'):torsoframe=4
            elif pose.startswith('WALK'):torsoframe=5+phase
            place(im,legs,legframe,offset=(0,-38))
            place(im,torso,torsoframe,offset=(0,-38))
        return im.resize((128,64),Image.Resampling.NEAREST)
    p=power+1
    labels={'STAND':'stand','WALK1':'walkStart','WALK2':'walkEnd','WALK3':'walkEnd',
      'JUMP1':'jump','JUMP2':'jump','JUMP3':'jump','JUMP4':'jump','CROUCH':'crouch',
      'ATTACK1':'attackStart','ATTACK2':'attack-2','ATTACK3':'attackEnd' if role=='SIMON' else 'attackEndGround',
      'THROW1':'throwStart','THROW2':'throw-2','THROW3':'throwEnd' if role=='SIMON' else 'throwEndGround',
      'CLIMB1':'climbStart','CLIMB2':'climbEnd','DOWNTHRUST':'dwnThrustStart','UPTHRUST':'upThrustStart',
      'HURT':'takeDamage','DIE1':'dieStart' if role=='SIMON' else 'dieDwn',
      'DIE2':'dieEnd' if role=='SIMON' else 'dieRht','DIE3':'dieEnd' if role=='SIMON' else 'dieUp',
      'DIE4':'dieEnd' if role=='SIMON' else 'dieLft','SLIDE':'slide',
      'CROUCHATTACK1':'crouchAttackStart','CROUCHATTACK2':'crouchAttack-2','CROUCHATTACK3':'crouchAttackEnd',
      'CROUCHTHROW1':'crouchThrowStart','CROUCHTHROW2':'crouchThrow-2','CROUCHTHROW3':'crouchThrowEnd'}
    labels.update({'DIEFLASH1':'dieFlash-1','DIEFLASH2':'dieFlash-2','DIEGRAY':'dieGray','DIECROSS1':'dieCross-1','DIECROSS2':'dieCross-2'})
    if role=='SIMON':labels.update({'WALK2':'walk-2','WALK3':'walk-3'})
    label=labels.get(pose,'stand')
    fallback=getframe(meta,f'{label}_1',getframe(meta,f'stand_{p}'))
    return image(meta,getframe(meta,f'{label}_{p}',fallback))

def pack(im,origin,pool):
    # Normalize palette indices before caching, so recolored copies share work.
    ls=layers(im)
    key=(im.size,origin,tuple((p,bytes(v for row in rows for v in row)) for p,rows in ls.items()),tuple(pool))
    if key not in CACHE:
        local=pool[:]
        parts=packing.parts(im,origin,local)
        CACHE[key]=(parts,local)
    parts,local=CACHE[key]
    return parts,local[:]

def choose_groups(jobs,initial,reserved):
    # Deterministic bounded search changes only tile allocation, never pixels.
    import random
    rng=random.Random(0xb11);best=None
    sets=[set(j[2])for j in jobs]
    for trial in range(512):
        order=sorted(range(len(jobs)),key=lambda i:(-len(sets[i])+(rng.random()*12 if trial else 0),i))
        groups=[g[:]for g in initial];records={}
        for n in order:
            current=sets[n];choices=[]
            for i,g in enumerate(groups):
                added=current-set(g)
                if len(g)+len(added)<=32:choices.append((len(added),-len(g),i))
            if choices:index=min(choices)[2]
            else:index=len(groups);groups.append(reserved[:])
            for value in jobs[n][2]:
                if value not in groups[index]:groups[index].append(value)
            records[n]=index
        key=(len(groups),sum(map(len,groups)))
        if best is None or key<best[0]:best=(key,groups,records)
    return best[1],best[2]

def choose_link_groups(jobs,reserved):
    # Death-only Link banks cannot draw shots: RosterDrawShots returns while
    # MmDeathFlag is set. Living poses retain the complete weapon prefix.
    needed=[list(dict.fromkeys(j[2][p[0]//2] for p in j[1]))for j in jobs]
    groups=[];death_groups=[];assignment={}
    for n in sorted(range(len(jobs)),key=lambda i:-len(needed[i])):
        death='_DIE' in jobs[n][0];choices=[]
        for i,g in enumerate(groups):
            if death_groups[i]!=death:continue
            add=[v for v in needed[n]if v not in g]
            if len(g)+len(add)<=32:choices.append((len(add),len(g),i))
        if choices:index=min(choices)[2]
        else:index=len(groups);groups.append([]if death else reserved[:]);death_groups.append(death)
        for v in needed[n]:
            if v not in groups[index]:groups[index].append(v)
        assignment[n]=index
    return groups,assignment

def main():
    assets.layers=layers
    assets.OAM_PRIORITY=True
    bank_ids=list(range(0x1d,0x3c))+list(range(0xd1,0xd5))+list(range(0x84,0x87))
    unique=[];files={};manifest={}
    roles=[('BILL','1194',0x13),('LINK','690',0x14),('SIMON','726',0x15)]
    for role,sid,prg in roles:
        assets.SCANLINE_PRIORITY=role=='SIMON'
        packing.RAW_CACHE.clear();CACHE.clear()
        lines=['; Generated from the pinned hosted SWF.', '.pushseg',f'.segment "{role}_GFX"']
        pool=[];weapons=[];targets(role,0)
        if role=='BILL':sources=[('1290',f'BULLET{i}',i) for i in range(1,3)]+[('1290',f'SPREAD{size}',2)for size in range(5,9)]+[('1290','IMPACT',3)]
        elif role=='LINK':sources=[('1535',f'BOOM{i}',i) for i in range(1,5)]+[('1542',f'BEAM{i}',i) for i in range(1,5)]+[('1551',f'BURST{i}',i) for i in range(1,5)]
        else:sources=[('1283',f'AXE{i}',i) for i in range(1,5)]
        for ident,name,frame in sources:
            global TARGETS
            if role=='BILL':
                # All bullet colors fit one palette/one 8x16 sprite.
                TARGETS=[((0,0,0),(2,3)),((248,56,0),(2,1)),((255,255,255),(2,2))]
            if role=='SIMON':
                TARGETS=[((0,0,0),(3,1)),((198,115,255),(2,2)),((247,198,255),(2,3))]
            meta=assets.read_meta(ident);im=image(meta,frame,(32,32),(64,64))
            if role=='BILL' and name.startswith('SPREAD'):
                # Flash10px art becomes5NES pixels at scale1. Source growth
                # .018/update is projected to nearest integer art dimension.
                size=int(name[6:]);bbox=im.getbbox();assert bbox[2]-bbox[0]==5 and bbox[3]-bbox[1]==5
                crop=im.crop(bbox).resize((size,size),Image.Resampling.NEAREST)
                im=Image.new('RGBA',(32,32));im.alpha_composite(crop,(16-(size+1)//2,16-(size+1)//2))
                out=ROOT/f'build/reference-frames/BILL-SPREAD-{size}.png';out.parent.mkdir(exist_ok=True,parents=True);im.save(out)
            parts=packing.parts(im,(16,16),pool)
            weapons.append((name,parts))
        if role=='LINK':
            # Mirror the packed parts, retaining the same canonical CHR pairs.
            weapons += [(f'BURSTDOWN{i}',[(t,p^0x80,x,-y-16) for t,p,x,y in weapons[7+i][1]]) for i in range(1,5)]
        maximum=0;names=[];banks=[];meta=assets.read_meta(sid);groups=[];pose_groups=[]
        if role=='BILL':
            original_plan=json.loads((ROOT/'chr/characters/ordinary-body-layout.json').read_text())
            original_bill=next(v for v in original_plan['replacements']if v['name']=='RgBILL0_WALK2')
            seed=bytearray.fromhex(original_bill['baseline_bank_hex'])
            for i,data in enumerate(pool):seed[i*32:(i+1)*32]=data
            # Keep the existing optimized WALK2 tile and all fallback records.
            seed[31*32:32*32]=bytes.fromhex(original_bill['pair_edits']['31'])
            groups.append([bytes(seed[i:i+32])for i in range(0,1024,32)])
        jobs=[]
        for power in range(3):
            targets(role,power)
            for pose in NAMES:
                name=f'Rg{role}{power}_{pose}';names.append(name)
                im=pose_image(role,power,pose,meta)
                parts,local=pack(im,(32,16),pool)
                maximum=max(maximum,len(parts))
                if len(local)>32:raise RuntimeError(f'{name} needs {len(local)} tile pairs')
                jobs.append((name,parts,local))
                out=ROOT/f'build/reference-frames/{role}-{power}-{pose}.png';out.parent.mkdir(exist_ok=True,parents=True);im.save(out)
        link_end=[]
        if role=='LINK':
            for power in range(3):
                targets(role,power)
                for kind,label,slot in [('AIR_END','attackEndJump',17),('DOWN_END','dwnThrustEnd',19),('UP_END','upThrustEnd',18)]:
                    name=f'RgLINKEASY{power}_{kind}'
                    frame=getframe(meta,label+f'_{power+1}',0);assert frame
                    im=image(meta,frame);parts,local=pack(im,(32,16),pool)
                    link_end.append((power*48+slot,len(jobs),name,frame))
                    jobs.append((name,parts,local))
            groups,assignment=choose_link_groups(jobs,pool)
        else:groups,assignment=choose_groups(jobs,groups,pool)
        for n,(name,parts,local)in enumerate(jobs):
            group_index=assignment[n];group=groups[group_index]
            parts=[(group.index(local[tile//2])*2,pal,x,y)for tile,pal,x,y in parts]
            pose_groups.append(group_index);packing.raw(lines,name,parts)
        group_banks=[]
        for group in groups:
            data=b''.join(group)+bytes(1024-len(group)*32)
            if data not in unique:unique.append(data)
            index=unique.index(data)
            if index>=len(bank_ids):raise RuntimeError(f'CHR capacity exceeded in {role}: {len(unique)} unique banks')
            group_banks.append(bank_ids[index])
        table_names=names[:];table_groups=pose_groups[:len(names)]
        for slot,job_index,name,frame in link_end:
            table_names[slot]=name;table_groups[slot]=pose_groups[job_index]
        banks=[group_banks[i] for i in table_groups]
        for suffix,expr in [('LeftLo','<{}Left'),('LeftHi','>{}Left'),('RightLo','<{}Right'),('RightHi','>{}Right')]:
            lines += [f'Rg{role}{suffix}:','  .byte '+','.join(expr.format(n) for n in table_names)]
        lines += [f'Rg{role}Banks:','  .byte '+','.join(f'${v:02x}' for v in banks)]
        for name,parts in weapons:packing.raw(lines,f'Rg{role}{name}',parts,axis=0)
        for suffix,expr in [('LeftLo','<{}Left'),('LeftHi','>{}Left'),('RightLo','<{}Right'),('RightHi','>{}Right')]:
            lines += [f'Rg{role}Weapons{suffix}:','  .byte '+','.join(expr.format('Rg'+role+n) for n,p in weapons)]
        lines += ['.popseg']
        (ROOT/f'src/{role.lower()}_metasprites.inc').write_text('\n'.join(lines)+'\n')
        manifest[role]={'poses':len(names),'maximum_sprites':maximum,'weapon_tile_pairs':len(pool),'prg_bank':prg,'standing_chr':banks[0]};manifest[role]['weapon_frames']=[name for name,_ in weapons]
        print(role,manifest[role], 'total unique CHR',len(unique),flush=True)
    low=unique[:31];high=unique[31:35];overflow=unique[35:]
    (ROOT/'chr/characters/crossover-roster-overflow.chr').write_bytes(b''.join(overflow))
    (ROOT/'chr/characters/crossover-roster-low.chr').write_bytes(b''.join(low)+bytes((35-len(low))*1024))
    (ROOT/'chr/characters/crossover-roster-high.chr').write_bytes(b''.join(high)+bytes((4-len(high))*1024))
    (ROOT/'src/roster_poses.inc').write_text('ROSTER_POSE_COUNT = '+str(len(NAMES))+'\n'+
      '\n'.join(f'RG_POSE_{n} = {i}' for i,n in enumerate(NAMES))+'\n')
    manifest['unique_chr_banks']=len(unique)
    (ROOT/'docs/reference/roster-assets.json').write_text(json.dumps(manifest,indent=2)+'\n')
    plan=json.loads((ROOT/'chr/characters/ordinary-body-layout.json').read_text())
    plan['growth_parent_plan_sha256']=__import__('hashlib').sha256((ROOT/'chr/characters/ordinary-body-layout.json').read_bytes()).hexdigest()
    item=next(v for v in plan['replacements']if v['name']=='RgBILL0_WALK2')
    old=bytes.fromhex(item['baseline_bank_hex']);new=bytearray(old)
    for i in range(2,6):new[i*32:(i+1)*32]=unique[0][i*32:(i+1)*32]
    item['baseline_bank_hex']=new.hex()
    plan['growth_owned_weapon_pairs']=[2,3,4,5]
    (ROOT/'chr/characters/ordinary-body-growth-layout.json').write_text(json.dumps(plan,indent=2)+'\n')
    print('Packed',len(unique),'of',len(bank_ids),'available 1K CHR banks.')

if __name__=='__main__':main()
