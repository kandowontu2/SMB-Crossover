"""Repack exact colored pixels into8x16 sprites with less empty overlap.

Each palette may choose its horizontal grid. Each column then chooses its
vertical grid independently. The objective counts the hardware's full16 rows,
including transparent rows; shortening opaque bounds alone cannot reduce NES
scanline occupancy. No pixels or colors are discarded by this optimizer.
"""


def pack_layers(layers):
    palettes=sorted(p for p,pixels in layers.items()if pixels)
    domains={}
    for p in palettes:
        pixels=layers[p];minx=min(x for x,y in pixels);maxx=max(x for x,y in pixels)
        for phase in range(8):
            columns=[]
            for left in range((minx-phase)//8*8+phase,maxx+1,8):
                column={(x,y):v for(x,y),v in pixels.items()if left<=x<left+8}
                if not column:continue
                miny=min(y for x,y in column);maxy=max(y for x,y in column)
                options=[]
                for vertical in range(16):
                    first=(miny-vertical)//16*16+vertical
                    if first < -32:continue
                    parts=[];rows=[0]*80
                    for top in range(first,maxy+1,16):
                        px=[[column.get((left+x,top+y),0)for x in range(8)]for y in range(16)]
                        if not any(any(row)for row in px):continue
                        parts.append((px,p,top,left))
                        for y in range(top,top+16):rows[y+32]+=1
                    options.append((parts,rows))
                assert options
                columns.append(options)
            domains[p,phase]=columns

    def score(rows,count):
        return sum(n*n for n in rows)+count*32+max(rows,default=0)*24

    def fit(phases):
        choices=[];rows=[0]*80;count=0
        for p in palettes:
            for options in domains[p,phases[p]]:
                parts,occupied=min(options,key=lambda z:(len(z[0]),score([a+b for a,b in zip(rows,z[1])],count+len(z[0]))))
                choices.append([options,parts,occupied])
                rows=[a+b for a,b in zip(rows,occupied)];count+=len(parts)
        for _ in range(3):
            changed=False
            for choice in choices:
                options,oldparts,oldrows=choice
                other=[a-b for a,b in zip(rows,oldrows)];base=count-len(oldparts)
                parts,occupied=min(options,key=lambda z:(score([a+b for a,b in zip(other,z[1])],base+len(z[0])),len(z[0])))
                changed|=occupied!=oldrows
                choice[1:]=parts,occupied
                rows=[a+b for a,b in zip(other,occupied)];count=base+len(parts)
            if not changed:break
        parts=[part for _,column,_ in choices for part in column]
        return (score(rows,count),count,max(rows,default=0)),parts

    starts=[{p:phase for p in palettes}for phase in(0,3,5)]
    starts.append({p:min(range(8),key=lambda phase:sum(min(len(z[0])for z in options)for options in domains[p,phase]))for p in palettes})
    results=[]
    for phases in starts:
        value,parts=fit(phases)
        for _ in range(2):
            changed=False
            for p in palettes:
                alternatives=[]
                for phase in range(8):
                    candidate={**phases,p:phase};quality,items=fit(candidate)
                    alternatives.append((quality,phase,items))
                quality,phase,items=min(alternatives,key=lambda z:(z[0],z[1]))
                if quality < value:
                    phases[p]=phase;value,parts=quality,items;changed=True
            if not changed:break
        results.append((value,parts))
    return min(results,key=lambda z:z[0])[1]
