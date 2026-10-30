"""Preserve native source pixels in one body window and one shared shot window."""
from pathlib import Path
import hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'build/arthur-source-v1';OUT=ROOT/'build/arthur-projected-leaf-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
WEAPONS={0x36,0x37,0x38,0x39,0x40,0x41,0x42,0x43,0x44,0x45,0x4f,0x56,0x66,0xa0,0xa1,0xa2,0xa9,0xaa,0xf8,0xf9}

def main():
    source=json.loads((BASE/'art-source.json').read_text());original=(BASE/'arthur-original-sprites.chr').read_bytes()
    records={r['pose']:r for r in source['records']}
    tiles={p:{x['tile']for x in r['parts']if x['tile']!=255}for p,r in records.items()}
    groups=[dict(poses=[p],tiles=tiles[p])for p in sorted(set(records)-WEAPONS)]
    while True:
        choices=[((len(groups[i]['tiles']&groups[j]['tiles']),len(groups[i]['tiles']|groups[j]['tiles'])),-i,-j,groups[i]['tiles']|groups[j]['tiles'])
           for i in range(len(groups))for j in range(i)if len(groups[i]['tiles']|groups[j]['tiles'])<=32]
        if not choices:break
        _,ni,nj,u=max(choices);i,j=-ni,-nj
        groups[j]=dict(poses=groups[j]['poses']+groups[i]['poses'],tiles=u);groups.pop(i)
    assert len(groups)==3
    groups.append(dict(poses=sorted(WEAPONS),tiles=set().union(*(tiles[p]for p in WEAPONS))))
    atlas=bytearray(4096);mapping={};plan=[]
    for page,g in enumerate(groups):
        assert len(g['tiles'])<=32
        lookup={t:i*2 for i,t in enumerate(sorted(g['tiles']))}
        for t,new in lookup.items():atlas[page*1024+new*16:page*1024+new*16+16]=original[t*16:t*16+16]
        for p in g['poses']:mapping[p]=(page,lookup)
        plan.append(dict(relative_page=page,hardware_window=6 if page==3 else 0,poses=sorted(g['poses']),
                         pair_count=len(lookup),source_tile_to_even_local_tile=lookup))
    def picture(parts,read):
        pixels={}
        for part in reversed(parts):
            a=part['attribute'];h=part['height']
            for yy in range(h):
                sy=h-1-yy if a&128 else yy
                for xx in range(8):
                    sx=7-xx if a&64 else xx;data=read(part,sy//8);at=sy%8
                    value=(data[at]>>(7-sx)&1)|((data[at+8]>>(7-sx)&1)<<1)
                    if value:pixels[part['x']+xx,part['y']+yy]=((a&3)*4+value,a&32)
        return sorted((x,y,v)for(x,y),v in pixels.items())
    cases=[]
    for pose,r in records.items():
        page,lookup=mapping[pose];window=6 if page==3 else 0
        for key,row in r['attribute_rows'].items():
            before=[];after=[]
            for i,p in enumerate(r['parts']):
                if p['tile']==255:continue
                attr=p['attribute']|row['values'][i]
                before.append(dict(tile=p['tile'],attribute=attr,x=p['x'],y=p['y'],height=8))
                after.append(dict(tile=lookup[p['tile']]|(0x81 if window==6 else 0),local_tile=lookup[p['tile']],
                   attribute=attr,x=p['x'],y=p['y']-(8 if attr&128 else 0),height=16,relative_page=page,hardware_window=window))
            left=picture(before,lambda p,half:original[p['tile']*16:p['tile']*16+16])
            right=picture(after,lambda p,half:atlas[page*1024+(p['local_tile']+half)*16:page*1024+(p['local_tile']+half)*16+16])
            assert left==right,(pose,key)
            # Actual8x16 tile decode must land in the declared hardware1KiB window.
            for p in after:
                ppupointer=(p['tile']&1)*4096+(p['tile']&254)*16
                assert ppupointer//1024==window and ppupointer%1024==p['local_tile']*16
            maximum=max((sum(p['y']<=y<p['y']+16 for p in after)for y in range(-64,96)),default=0)
            cases.append(dict(pose=pose,attribute_row=int(key),relative_page=page,hardware_window=window,
                 parts=after,max_8x16_sprites_on_one_scanline=maximum,
                 exact_index_alpha_priority_plane_sha256=hashlib.sha256(repr(left).encode()).hexdigest()))
    (OUT/'arthur-windowed.chr').write_bytes(atlas)
    result=dict(status='PASS_SOURCE_EXACT_PER_POSE_ONE_BODY_ONE_PROJECTILE_WINDOW_NO_PHYSICAL_LEASE',
       atlas=dict(path=str((OUT/'arthur-windowed.chr').resolve()),sha256=sha(OUT/'arthur-windowed.chr'),bytes=len(atlas),
           used_pairs=sum(g['pair_count']for g in plan),used_bytes=sum(g['pair_count']for g in plan)*32),
       pages=plan,exact_cases=len(cases),records=cases,
       ownership=dict(body_window=0,body_relative_pages=[0,1,2],all_projectiles_window=6,projectile_relative_page=3,
          native_world_windows_preserved=[1,2,3,4,5,7],simultaneous_projectile_pose_mixes_share_same_physical_page=True),
       bindings={str(p.resolve()):sha(p)for p in[Path(__file__),BASE/'art-source.json',BASE/'arthur-original-sprites.chr',BASE/'handoff.json']},
       limits='Original source pattern/index/alpha/priority projection only. No physical CHR allocation, palette quantization, host OAM/collision/native admission or aggregate world+body scanline budget claim.')
    p=OUT/'windowed-art-proof.json';p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],atlas=result['atlas'],pages=[{k:v for k,v in p.items()if k!='source_tile_to_even_local_tile'}for p in plan],exact_cases=len(cases),proof_sha256=sha(p))))
if __name__=='__main__':main()
