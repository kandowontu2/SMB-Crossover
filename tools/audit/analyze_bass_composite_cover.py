"""Bounded read-only exact composite set-cover search for Bass WALK1."""
from pathlib import Path
import argparse,hashlib,json,time
import numpy as np
from scipy.optimize import Bounds,LinearConstraint,milp
from scipy.sparse import coo_matrix
from check_mm_bass_injury_packing import Rom
from analyze_sprite_vertical_alignment import decode,encode,flip,signed,canonical

def main():
    p=argparse.ArgumentParser();p.add_argument('rom',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();rom=Rom(a.rom)
    bank=rom.read('XgBASSBanks',86)[85];mapping=rom.read('ChrPhysicalMap',256);raw=rom.chr()[mapping[bank]*1024:(mapping[bank]+1)*1024]
    pool=[decode(raw[i*32:(i+1)*32])for i in range(32)];data=rom.pose('XgBASS0_WALK1Right');parts=[];image={}
    for o in range(1,len(data),4):
        t,at,y,x=data[o:o+4];parts.append((flip(pool[(t&62)//2],at&64,at&128),at&3,signed(x),signed(y)))
    # Last record receives the first hardware slot, hence wins opaque overlaps.
    for pixels,pal,x,y in reversed(parts):
        for yy,row in enumerate(pixels):
            for xx,c in enumerate(row):
                if c:image.setdefault((x+xx,y+yy),(pal,c))
    pixels=sorted(image);index={xy:i for i,xy in enumerate(pixels)};candidates=[]
    for pal in(0,2,3):
        own=[xy for xy in pixels if image[xy][0]==pal]
        xmin,xmax=min(x for x,y in own),max(x for x,y in own);ymin,ymax=min(y for x,y in own),max(y for x,y in own)
        for y in range(ymin-15,ymax+1):
            for x in range(xmin-7,xmax+1):
                covered=[index[xy]for xy in own if x<=xy[0]<x+8 and y<=xy[1]<y+16]
                if not covered:continue
                pattern=tuple(tuple(image.get((x+xx,y+yy),(None,0))[1]if image.get((x+xx,y+yy),(None,0))[0]==pal else 0 for xx in range(8))for yy in range(16))
                packed,flags=min((encode(flip(pattern,h,v)),(64 if h else 0)|(128 if v else 0))for h,v in((0,0),(1,0),(0,1),(1,1)))
                assert flip(decode(packed),flags&64,flags&128)==pattern
                candidates.append(dict(x=x,y=y,pal=pal,flags=flags,cover=covered,pattern=packed.hex()))
    # Pixel symbols, not merely the current RGB, are preserved. This also
    # preserves future palette cycling, special suits and star transitions.
    rr=[];cc=[];vv=[];n=len(candidates);lines=list(range(-16,49));lineoff=len(pixels);totalrow=lineoff+len(lines)
    for j,c in enumerate(candidates):
        for i in c['cover']:rr.append(i);cc.append(j);vv.append(1)
        for i,y in enumerate(lines):
            if c['y']+1<=y<c['y']+17:rr.append(lineoff+i);cc.append(j);vv.append(1)
        rr.append(totalrow);cc.append(j);vv.append(1)
    matrix=coo_matrix((vv,(rr,cc)),shape=(totalrow+1,n)).tocsc()
    lower=np.r_[np.ones(len(pixels)),np.zeros(len(lines)+1)]
    upper=np.r_[np.full(len(pixels),np.inf),np.full(len(lines),6),11]
    started=time.monotonic();result=milp(c=np.ones(n),integrality=np.ones(n),bounds=Bounds(0,1),constraints=LinearConstraint(matrix,lower,upper),options={'time_limit':20,'mip_rel_gap':0.0})
    report=dict(rom_sha256=hashlib.sha256(rom.data).hexdigest(),scope='One-frame feasibility; immutable ROM only. Preserves exact final palette/color-index symbols as well as opaque coordinates; no sprite/asset/runtime writes.',
                candidates=n,pixels=len(pixels),elapsed_seconds=time.monotonic()-started,status=result.message,feasible=result.x is not None)
    if result.x is not None:
        chosen=[c for c,x in zip(candidates,result.x)if x>.5];actual={}
        for c in chosen:
            for i in c['cover']:actual[pixels[i]]=image[pixels[i]]
        assert actual==image
        profile={y:sum(c['y']+1<=y<c['y']+17 for c in chosen)for y in lines}
        assert max(profile.values())<=6 and len(chosen)<=11
        existing={canonical(p).hex()for p in pool};new={c['pattern']for c in chosen if c['pattern']not in existing}
        report.update(parts=len(chosen),peak_all_rows=max(profile.values()),peak_with_one_goomba=max(profile[y]+2 for y in range(17,33)),
                      unique_patterns=len({c['pattern']for c in chosen}),patterns_new_to_existing_bank=len(new),
                      existing_zero_pairs=sum(not any(p)for p in(raw[i*32:(i+1)*32]for i in range(32))),
                      rectangles=[{k:v for k,v in c.items()if k!='cover'}for c in chosen])
    a.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='rectangles'},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
