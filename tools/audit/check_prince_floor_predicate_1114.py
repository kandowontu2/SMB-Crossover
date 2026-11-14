"""Reference predicate only: wall/body versus floor/exposed-roof criteria.

This explicitly alters carry in seeded primitive CPU fixtures. It is not
assembled production code, a source overlay, ordinary gameplay qualification
or a funding grant. The actual WorldTile caller executes around the oracle.
"""
from collections import Counter
from hashlib import sha256
import json
import check_prince_world_mapping_1114 as World

F,P,N=World.F,World.P,World.N


def run(raw,compiled=None,expanded=False):
    F.authenticate(raw);base,_=World.Base.cold(raw);b=base.bundle
    buffer=P.W.address(b,'Block_Buffer_1');attrs=P.W.address(b,'MTileAttribute')
    counts=Counter();failures=[];changed=[];qcycles=[]
    def native_solid(m,x,y):
        if not(0<=x<65536 and 32<=y<240):return False
        tile=m[buffer+((x//256)&1)*208+((y-32)//16)*16+((x&255)//16)]
        return bool(m[attrs+tile]&1)
    def predicate(m,c):
        if c.pc not in(0xbe92,0xbece,0xbef8)or not c.p&1:return
        s=m.ram[2]
        if s[0x7c]!=s[0x83]:return
        qx=int.from_bytes(m.ram[3][0x1369:0x136b],'little')
        qy=int.from_bytes(m.ram[3][0x136b:0x136d],'little')
        actor=int.from_bytes(s[0x60f:0x611],'little')-8;cell=qx&0xfff0
        if max(cell,actor)<min(cell+16,actor+16):return
        if c.pc==0xbe92:
            c.p&=0xfe;counts['wall_body_rejections']+=1;return
        counts['extra_roof_queries']+=1
        roof=(qy&0xfff0)-1
        if native_solid(m,qx,roof):
            c.p&=0xfe;counts['raised_column_floor_rejections']+=1
        else:counts['exposed_foot_surface_retained']+=1
    # Authored/native material families, actual gap edges, half-cells and
    # pages. Floor criteria retain coarse donor feet queries; only a higher
    # solid column outside the physical body is refused.
    layouts=('flat','pit-left','pit-right','empty','pipe16','pipe32','brick16','brick32')
    samples=[(x,208,0)for x in range(224,288,4)]
    if expanded:samples.extend((x,foot,room)for x in(240,248,256,264)for foot in(144,160,176,209)for room in(-1,0,1))
    for layout in layouts:
     for facing in(0,255):
      for alternate in(0,1):
       for x,foot,room in samples:
        for delta in(20 if facing else 31,4 if facing else 40):
         pair=[N.fork(base),N.fork(base)]
         for m in pair:
            sy=foot-80;current_row=max(0,sy-29)//64
            s=m.ram[2];World.word(s,0x60f,x+8);s[0x611]=sy;s[0x615]=facing
            s[0x616]=1;s[0x618]=1;s[0x617]=8
            World.word(s,0x89,77);s[0x8b]=sy;s[0x88]=3;s[0x4b1]=10*current_row;s[0x7a]=0;s[0x82]=room&255
            query=x+8-delta+(20 if alternate and not facing else 0);World.word(s,0x78,query)
            for page in range(2):
             for row in range(13):
              for col in range(16):
               wx=page*256+16*col;wy=32+16*row
               floor=layout!='empty'and not(layout=='pit-left'and wx<256)and not(layout=='pit-right'and wx>=256)
               raised=layout.startswith(('pipe','brick'))and 256<=wx<256+(16 if layout.endswith('16')else 32)and wy>=160
               tile=(0x14 if layout.startswith('pipe')else 0x51)if raised else 0x54 if floor and wy>=208 else 0
               m[buffer+208*page+16*row+col]=tile
         if compiled:
            code,calls,peek=compiled
            pair[1][0x7000:0x7000+len(code)]=code
            for call in calls:
                at=call['PC']-0xa000
                assert bytes(pair[1].ram[3][at:at+8])==bytes.fromhex(call['preimage'])
                pair[1].ram[3][at+1:at+3]=call['target'].to_bytes(2,'little')
            def spy(m,c):
                if c.pc==peek:counts['extra_roof_queries']+=1
            observer=spy
         else:observer=predicate
         old=World.invoke(pair[0],with_cycles=True);new=World.invoke(pair[1],observe=observer,with_cycles=True)
         qcycles.append(new['cycles']-old['cycles'])
         counts['vectors']+=1
         assert old['registers'][1:3]==new['registers'][1:3]and old['registers'][4]==new['registers'][4]
         assert old['registers'][3]&0x7d==new['registers'][3]&0x7d
         if layout in('flat','pit-left','pit-right','empty'):
            keys=('material','registers','cell','surface')
            if any(old[k]!=new[k]for k in keys):failures.append(dict(layout=layout,facing=facing,alternate=alternate,x=x,foot=foot,room=room,delta=delta,old=old,new=new))
         elif room:
            if any(old[k]!=new[k]for k in('material','registers','cell','surface')):failures.append(dict(layout=layout,x=x,foot=foot,room=room,old=old,new=new))
         elif old['material']!=new['material']:
            counts['raised_material_changes']+=1
            width=16 if layout.endswith('16')else 32
            supported=max(x,256)<min(x+16,256+width)
            unsupported_floor_removed=old['material']==1 and new['material']==0 and not supported and foot>160
            if unsupported_floor_removed:counts['unsupported_higher_surface_removed']+=1
            elif new['material']!=20 and new['surface']!=208:failures.append(dict(layout=layout,x=x,foot=foot,room=room,old=old,new=new))
            if len(changed)<8:changed.append(dict(layout=layout,x=x,facing=facing,old=old['material'],new=new['material'],surface=new['surface']))
    return dict(ROM_SHA256=F.PIN,reference_predicate_only=not bool(compiled),carry_oracle_not_production_code=not bool(compiled),
        unallocated_primitive_assembly=bool(compiled),
        counts=dict(counts),failures=len(failures),failure_examples=failures[:4],change_examples=changed,
        whole_WorldTile_added_cycles=dict(minimum=min(qcycles),maximum=max(qcycles),total=sum(qcycles),vectors=len(qcycles)),
        no_gameplay_or_allocation_claim=True,outputs=0,Mesen=False)


if __name__=='__main__':
    q=run(F.ROM.read_bytes());q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print(json.dumps(q,separators=(',',':')),flush=True)
