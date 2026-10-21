"""Read immutable body CHR and test opaque-pixel-preserving rectangle shifts.

No asset is written. Coordinate descent gives demonstrated feasible plans, not
an assertion of global optimality. Pool availability is conservative: existing
patterns (all flips) plus currently zero-filled pairs; shared-bank plans must
still be allocated together before any future implementation.
"""
from pathlib import Path
import argparse,hashlib,json
from check_mm_bass_injury_packing import Rom

def decode(data):
    return tuple(tuple(((data[(y//8)*16+y%8]>>(7-x))&1)+2*((data[(y//8)*16+y%8+8]>>(7-x))&1)for x in range(8))for y in range(16))
def flip(p,h=False,v=False):
    return tuple(tuple(reversed(row))if h else row for row in(reversed(p)if v else p))
def encode(p):
    return bytes(sum(((p[y+half*8][x]>>plane)&1)<<(7-x)for x in range(8))for half in range(2)for plane in range(2)for y in range(8))
def canonical(p):return min(encode(flip(p,h,v))for h,v in((0,0),(1,0),(0,1),(1,1)))
def shift(p,s):return tuple(p[y+s]if 0<=y+s<16 else(0,)*8 for y in range(16))
def signed(v):return v-256 if v>=128 else v

def analyze(rom,label,bank,off):
    mapping=rom.read('ChrPhysicalMap',256);block=rom.chr()[mapping[bank]*1024:(mapping[bank]+1)*1024]
    pool=[decode(block[i*32:(i+1)*32])for i in range(32)]
    existing={canonical(p)for p in pool};free_indices=[i for i,p in enumerate(pool)if not any(x for row in p for x in row)];free=len(free_indices)
    lookup={}
    for n,p in enumerate(pool):
        for h,v in((0,0),(1,0),(0,1),(1,1)):lookup.setdefault(encode(flip(p,h,v)),(n*2,(64 if h else 0)|(128 if v else 0)))
    data=rom.pose(label);parts=[]
    for o in range(1,len(data),4):
        t,a,y,x=data[o:o+4]
        if off and a&4:continue
        p=flip(pool[(t&0x3e)//2],a&64,a&128)
        occupied=[yy for yy,row in enumerate(p)if any(row)]
        if not occupied:continue
        lo,hi=min(occupied),max(occupied);options=[]
        for s in range(hi-15,lo+1):
            q=shift(p,s);key=canonical(q)
            # Independent visible coordinates/colors must survive every option.
            assert {(signed(x)+xx,signed(y)+yy,c)for yy,row in enumerate(p)for xx,c in enumerate(row)if c}=={(signed(x)+xx,signed(y)+s+yy,c)for yy,row in enumerate(q)for xx,c in enumerate(row)if c}
            options.append(dict(s=s,pattern=key,reuse=key in existing,reuse_tile_flip=lookup.get(encode(q)),y=signed(y)+s))
        parts.append(dict(tile=t,attr=a,x=signed(x),y=signed(y),opaque_y=[signed(y)+lo,signed(y)+hi],opaque_height=hi-lo+1,
                          opaque_rows=[signed(y)+yy+1 for yy,row in enumerate(p)if any(row)],options=options))
    def profile(selection):
        rows=[0]*96
        for i,j in enumerate(selection):
            y=parts[i]['options'][j]['y']
            for yy in range(y+1,y+17):
                if -32<=yy<64:rows[yy+32]+=1
        return rows
    original=[next(j for j,o in enumerate(p['options'])if o['s']==0)for p in parts]
    def objective(sel,limited=True):
        rows=profile(sel);new={parts[i]['options'][j]['pattern']for i,j in enumerate(sel)if not parts[i]['options'][j]['reuse']}
        if limited and len(new)>free:return(999,999,999,999,999)
        band=rows[32+17:32+33]
        return(max(band,default=0),max(rows,default=0),sum(band),len(new),sum(abs(parts[i]['options'][j]['s'])for i,j in enumerate(sel)))
    def solve(limited,minimal=False):
        sel=original[:]
        for _ in range(32):
            score=objective(sel,limited);best=(score,sel)
            for i,p in enumerate(parts):
                for j in range(len(p['options'])):
                    trial=sel[:];trial[i]=j;s=objective(trial,limited)
                    if s<best[0]:best=(s,trial)
            if best[0]>=score:break
            sel=best[1]
        if minimal:
            target=objective(sel,limited)[:2]
            def resource_score(s):
                score=objective(s,limited)
                return(score[3],score[2],score[4])if score[0]<=target[0]and score[1]<=target[1]else(999,999,999)
            for _ in range(32):
                score=resource_score(sel);best=(score,sel)
                for i,p in enumerate(parts):
                    for j in range(len(p['options'])):
                        trial=sel[:];trial[i]=j;s=resource_score(trial)
                        if s<best[0]:best=(s,trial)
                if best[0]>=score:break
                sel=best[1]
        new={parts[i]['options'][j]['pattern']for i,j in enumerate(sel)if not parts[i]['options'][j]['reuse']}
        return dict(score=objective(sel,limited),peak_body_with_one_goomba=max(x+2 for x in profile(sel)[49:65]),
                    new_pairs=len(new),new_patterns=[p.hex()for p in sorted(new)],
                    moves=[dict(part=i,old_y=p['y'],new_y=p['options'][sel[i]]['y'],delta=p['options'][sel[i]]['s'],reuse_existing=p['options'][sel[i]]['reuse'],reuse_tile_flip=p['options'][sel[i]]['reuse_tile_flip'])for i,p in enumerate(parts)if p['options'][sel[i]]['s']!=0])
    return dict(label=label,bank=bank,outlines_off=off,parts=len(parts),zero_filled_pairs=free,zero_filled_pair_indices=free_indices,
                baseline_score=objective(original),baseline_peak_with_one_goomba=max(x+2 for x in profile(original)[49:65]),
                opaque_concurrent_peak_in_goomba_band=max(sum(y in p['opaque_rows']for p in parts)for y in range(17,33)),
                nonzero_shift_existing_pair_options=[dict(part=i,delta=o['s'],reuse_tile_flip=o['reuse_tile_flip'])for i,p in enumerate(parts)for o in p['options']if o['s']!=0 and o['reuse']],
                bounds=[{k:p[k]for k in('tile','attr','x','y','opaque_y','opaque_height','opaque_rows')}for p in parts],
                fits_zero_slots=solve(True),fewest_new_pairs_same_peak=solve(True,True),unconstrained=solve(False))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();rom=Rom(a.rom)
    rows=[]
    for role,table,stride,prefix,poses in(
        ('megaman','MegaManSpriteBanks',16,'MmMM_HELMET_',('STAND','WALK1','WALK2','WALK3','WALK4')),
        ('bass','XgBASSBanks',84,'XgBASS0_',('STAND','WALK1','WALK2','WALK3')),
        ('samus','SamusPoseBanks',31,'SmP0_',('STAND','WALK1','WALK2','WALK3')),
        ('bill','RgBILLBanks',48,'RgBILL0_',('STAND','WALK1','WALK2','WALK3'))):
        for i,pose in enumerate(poses):
            index=i if role!='samus'or pose=='STAND'else i+1
            bank=rom.read(table,stride+index+1)[stride+index]
            for side in('Left','Right'):
                label=prefix+pose+side
                for off in(0,1):
                    r=analyze(rom,label,bank,off);r['character']=role;r['pose']=pose;r['side']=side;rows.append(r)
    groups={}
    for row in rows:
        key=str(row['bank']);g=groups.setdefault(key,dict(zero_pairs=row['zero_filled_pairs'],zero_pair_indices=row['zero_filled_pair_indices'],conservative_new_patterns=set(),minimal_peak_new_patterns=set(),unconstrained_new_patterns=set()))
        g['conservative_new_patterns'].update(row['fits_zero_slots']['new_patterns']);g['unconstrained_new_patterns'].update(row['unconstrained']['new_patterns'])
        g['minimal_peak_new_patterns'].update(row['fewest_new_pairs_same_peak']['new_patterns'])
    for g in groups.values():
        for k in('conservative_new_patterns','minimal_peak_new_patterns','unconstrained_new_patterns'):g[k]=len(g[k])
    report=dict(rom_sha256=hashlib.sha256(rom.data).hexdigest(),scope='Read-only opaque-pixel-preserving vertical shifts; one-Goomba occupied scanlines193..208 with playerY176. Greedy feasible proposals, not global optima.',banks=groups,cases=rows)
    a.out.write_text(json.dumps(report,indent=2)+'\n')
    for r in rows:
        if r['side']=='Right'and r['outlines_off']==1:
            print(r['character'],r['pose'],'bank',hex(r['bank']),'pairsfree',r['zero_filled_pairs'],'row1Goomba',r['baseline_peak_with_one_goomba'],'->',r['fits_zero_slots']['peak_body_with_one_goomba'],'new',r['fits_zero_slots']['new_pairs'],'unconstrained',r['unconstrained']['peak_body_with_one_goomba'],'new',r['unconstrained']['new_pairs'])
    return 0
if __name__=='__main__':raise SystemExit(main())
