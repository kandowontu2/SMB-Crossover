"""Restore Rygar's omitted native pieces in an isolated two-bank art rebuild."""
from pathlib import Path
import hashlib,json,shutil,sys
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/reference'));sys.path.insert(0,str(R/'tools'))
import build_expanded_assets as g
from workspace_storage import locate
O=R/'build/verification/rygar-walk-k4';S=O/'source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assert not O.exists();S.mkdir(parents=True)
    seed=json.loads(locate(R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json').read_text())
    names=set(seed['source_hashes'])|{p.relative_to(R).as_posix() for p in (R/'src').rglob('*') if p.is_file()}
    for name in names:
        dest=S/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/name,dest)
    for name in seed['generated11']:
        dest=S/'build/generated'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/'build/generated'/name,dest)
    g.ROLE='RYGAR';g.COLORS=g.targets('RYGAR');g.assets.layers=g.layers
    g.assets.OAM_PRIORITY=True;g.assets.SCANLINE_PRIORITY=False;g.packing.RAW_CACHE.clear()
    pool=[];weaponparts=[];lines=['; Generated from pinned native guest references.','.pushseg','.segment "XG_RYGAR_GFX"']
    from PIL import Image,ImageDraw
    for i,pic in enumerate(g.weapons('RYGAR')):
        im=Image.new('RGBA',(48,48));im.alpha_composite(pic,((48-pic.width)//2,(48-pic.height)//2))
        ps=g.packing.parts(im,(24,24),pool);weaponparts.append(ps);g.packing.raw(lines,'XgRYGARWeapon'+str(i),ps,axis=0)
    groups=[];entries=[];cache={};walk_images={}
    for power in range(3):
        for pose in g.POSES:
            im=g.body('RYGAR',pose,power)
            left_im=g.rygar_walk_left(pose) if pose in ('WALK1','WALK2','WALK3') else None
            key=im.tobytes()+(left_im.tobytes() if left_im else b'')
            if key not in cache:
                local=pool[:];ps=g.packing.parts(im,(32,32),local)
                left_ps=g.packing.parts(left_im,(32,32),local) if left_im else None
                assert len(local)<=32
                cache[key]=(ps,local,left_ps)
            ps,local,left_ps=cache[key]
            candidates=[(sum(d not in q for d in local),len(q),i) for i,q in enumerate(groups) if len(q)+sum(d not in q for d in local)<=32]
            if candidates:gi=min(candidates)[2]
            else:gi=len(groups);groups.append(pool[:])
            for d in local:
                if d not in groups[gi]:groups[gi].append(d)
            ps=[(groups[gi].index(local[t//2])*2,p,x,y) for t,p,x,y in ps]
            name=f'XgRYGAR{power}_{pose}'
            if left_ps is not None:
                left_ps=[(groups[gi].index(local[t//2])*2,p,x,y)for t,p,x,y in left_ps]
                g.rygar_native_raw(lines,name,ps,left_ps)
            else:g.packing.raw(lines,name,ps)
            entries.append((name,gi))
            if power==0 and pose in ('WALK1','WALK2','WALK3'):
                walk_images[pose]=im;assert len(ps)==(6 if pose=='WALK2' else 4),(pose,len(ps))
                im.save(O/(pose+'.png'));left_im.save(O/(pose+'-left.png'))
    meta=json.loads((R/'docs/reference/expanded-assets.json').read_text());assert len(groups)==meta['RYGAR']['chr_banks']==2
    ids=[meta['RYGAR']['first_chr']+i for i in range(len(groups))]
    for suffix,fmt in [('LeftLo','<{}Left'),('LeftHi','>{}Left'),('RightLo','<{}Right'),('RightHi','>{}Right')]:
        lines+=['XgRYGAR'+suffix+':',' .byte '+','.join(fmt.format(n)for n,_ in entries)]
    lines+=['XgRYGARBanks:',' .byte '+','.join(f'${ids[i]:02x}'for _,i in entries)]
    for suffix,fmt in [('WeaponLo','<{}Right'),('WeaponHi','>{}Right'),('WeaponLeftLo','<{}Left'),('WeaponLeftHi','>{}Left')]:
        lines+=['XgRYGAR'+suffix+':',' .byte '+','.join(fmt.format('XgRYGARWeapon'+str(i))for i in range(len(weaponparts)))]
    lines+=['.popseg'];(S/'src/rygar_metasprites.inc').write_text('\n'.join(lines)+'\n')
    path=S/'chr/characters/crossover-expanded.chr';before=path.read_bytes();first=meta['PIT']['first_chr'];offset=(ids[0]-first)*1024
    replacement=b''.join(b''.join(q)+bytes(1024-32*len(q))for q in groups)
    after=before[:offset]+replacement+before[offset+2048:];assert len(before)==len(after)
    path.write_bytes(after)
    # Patch exactly the existing physical copies, retaining both logical maps,
    # every other physical page and all mapper-specific paired publication.
    for mapper in ('mmc3','mmc5'):
        text=(S/f'src/chr_map_{mapper}.inc').read_text();table=text.split('ChrPhysicalMap:\n',1)[1].split('.popseg',1)[0]
        mapping=[int(v.strip())for line in table.splitlines()if'.byte'in line for v in line.split('.byte',1)[1].split(',')]
        packed=S/f'chr/characters/packed-{mapper}.chr';old=packed.read_bytes();new=bytearray(old)
        for i,logical in enumerate(ids):
            physical=mapping[logical];oldpage=before[offset+i*1024:offset+(i+1)*1024]
            assert old[physical*1024:(physical+1)*1024]==oldpage
            assert mapping.count(physical)==1,'Rygar private page must not alias another logical family'
            new[physical*1024:(physical+1)*1024]=replacement[i*1024:(i+1)*1024]
        packed.write_bytes(new)
    contact=Image.new('RGB',(480,190),(57,66,82));draw=ImageDraw.Draw(contact)
    for i,(pose,im) in enumerate(walk_images.items()):
        draw.text((i*160+8,8),pose,fill='white');contact.paste(im.resize((192,160),Image.Resampling.NEAREST),(i*160-16,24),im.resize((192,160),Image.Resampling.NEAREST))
    contact.save(O/'complete-walk-contact.png')
    report=dict(status='PRIVATE_ART_REPAIRED_NOT_ADOPTED',cause='Native middle walking pose uses slots2..7; old importer truncated to4..7.',original_reference=R.as_posix()+'/build/rygar-audit/walk/manifest.json',native_middle_sprites=6,previous_middle_sprites=4,logical_chr=ids,group_pairs=list(map(len,groups)),unchanged_total_chr_size=True,source_before={n:sha(R/n) for n in sorted(names)},outputs={n:sha(S/n)for n in ('src/rygar_metasprites.inc','chr/characters/crossover-expanded.chr','chr/characters/packed-mmc3.chr','chr/characters/packed-mmc5.chr')},main_assets_modified=False)
    (O/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in ('source_before','outputs')}))
if __name__=='__main__':main()
