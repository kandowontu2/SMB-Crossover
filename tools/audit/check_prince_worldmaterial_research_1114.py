"""Oversize research routine in a relocated FLAT CPU fixture only.

Root explicitly authorized this virtual primitive fixture. It does not mount
the new routine in NesBus, change a decoded packet, compose a ROM or claim a
449-byte fit. Coordinates/terrain are seeded diagnostic vectors, not play.
"""
from collections import Counter
from hashlib import sha256
import json
from py65.devices.mpu6502 import MPU
import build_prince_worldmaterial_research_1114 as Build
import check_prince_world_mapping_1114 as World

VIRTUAL=0x6000


class Flat(list):
    def __init__(self,values):super().__init__(values);self.former_reads=0
    def __getitem__(self,key):
        if isinstance(key,int)and Build.Old.START<=key<Build.Old.END:self.former_reads+=1
        return super().__getitem__(key)


def word(m,at,value):m[at:at+2]=(value&65535).to_bytes(2,'little')


def run(raw,*,expanded=False):
    raw=Build.parent(raw);code,_,info=Build.build(raw)
    _,symbols=Build.Old.source()
    virtual,labels,_=Build.assemble(Build.SOURCE.read_text(),symbols,origin=VIRTUAL)
    old_code,old_labels=Build.Old.assemble(*Build.Old.source())
    base,_=World.Base.cold(raw);base.raw_page(1,3);base.raw_page(2,2)
    # Snapshot only RAM and mapped work/ROM windows. No PPU/APU/MMC I/O reads.
    image=[0]*65536
    for first,last in((0,0x2000),(0x6000,0x10000)):
        for at in range(first,last):image[at]=base[at]
    assert bytes(image[Build.Old.START:Build.Old.END])==old_code
    buffer=World.P.W.address(base.bundle,'Block_Buffer_1')
    attrs=World.P.W.address(base.bundle,'MTileAttribute')
    counts=Counter();failures=[];changes=[];costs=[];former_reads=0
    def solid(m,x,y):
        x&=65535
        if not 32<=y<240:return False
        tile=m[buffer+((x//256)&1)*208+((y-32)//16)*16+((x&255)//16)]
        return bool(m[attrs+tile]&1)
    def policy(m):
        return m[0xc07c]==m[0xc083]and m[0xc618]not in(2,6)and m[0xc616]not in(10,24)
    def oracle(m,c):
        if not policy(m):return
        # The authenticated original wall JSR at BE8F returns at BE92.
        if c.pc==0xbe92 and c.p&1:
            actor=m[0xc60f]+256*m[0xc610]
            delta=(((m[0xb369]+256*m[0xb36a])&0xfff0)-actor)&65535
            if not(delta<8 or delta>=0xffe9):c.p&=254;counts['oracle_wall_rejections']+=1
        if c.pc==old_labels['TopDone']and not m[0xc085]:
            top=m[0xc095];actor=m[0xc60f]+256*m[0xc610]
            if top<(m[0xc084]&0xf0)and not any(solid(m,actor+d,top)for d in(-6,5)):
                c.pc=old_labels['NextColumn'];counts['oracle_higher_floor_rejections']+=1
    def invoke(memory,entry,flags,observer=None):
        c=MPU(memory=memory,pc=entry);c.a,c.x,c.y,c.p,c.sp=83,71,memory[0xc4b1],flags,224
        c.stPushWord(0x5ffe);point_calls=0
        for _ in range(9000):
            if(c.pc,c.sp)==(0x5fff,224):break
            if observer:observer(memory,c)
            if c.pc==0xb310:point_calls+=1
            assert memory[c.pc],('Primitive BRK',hex(c.pc))
            c.step()
        else:raise AssertionError(('Primitive bound',hex(c.pc)))
        return dict(material=c.a,registers=[c.a,c.x,c.y,c.p,c.sp],
            surface=memory[0xc07f]+256*memory[0xc080],surface_row=memory[0xc081],
            cell=memory[0xc07d]+256*memory[0xc07e],cycles=c.processorCycles,point_calls=point_calls)
    layouts=('flat','pit-left','pit-right','empty','pipe16','pipe32','brick16','brick32')
    samples=[(x,208,0,1,1)for x in range(224,288,4)]
    if expanded:
        samples.extend((x,foot,room,action,mode)
            for x in(240,248,256,264)for foot in(144,160,176,209)
            for room,action,mode in((-1,1,1),(0,1,1),(1,1,1),(0,24,2),(0,10,1),(0,24,6)))
    for layout in layouts:
     for facing in(0,255):
      for alternate in(0,1):
       for x,foot,room,action,mode in samples:
        for delta in(20 if facing else 31,4 if facing else 40):
         seed=image.copy();sy=foot-80;current_row=max(0,sy-29)//64
         word(seed,0xc60f,x+8);seed[0xc611]=sy;seed[0xc615]=facing
         seed[0xc616]=action;seed[0xc618]=mode;seed[0xc617]=8
         word(seed,0xc089,77);seed[0xc08b]=sy;seed[0xc088]=3
         seed[0xc4b1]=10*current_row;seed[0xc07a]=0;seed[0xc082]=room&255
         query=x+8-delta+(20 if alternate and not facing else 0);word(seed,0xc078,query)
         # Native export is intentionally stale. All refinement must use the
         # current donor coordinate, including its full world-page carry.
         seed[0x86]=(x+91)&255
         for page in range(2):
          for row in range(13):
           for col in range(16):
            wx=page*256+16*col;wy=32+16*row
            floor=layout!='empty'and not(layout=='pit-left'and wx<256)and not(layout=='pit-right'and wx>=256)
            raised=layout.startswith(('pipe','brick'))and 256<=wx<256+(16 if layout.endswith('16')else 32)and wy>=160
            seed[buffer+208*page+16*row+col]=(0x14 if layout.startswith('pipe')else 0x51)if raised else 0x54 if floor and wy>=208 else 0
         a,b,d=Flat(seed),Flat(seed),Flat(seed)
         # Former function bytes are poisoned in the relocated model. Reads
         # from the old instruction addresses would be a relocation failure.
         d[Build.Old.START:Build.Old.END]=[0]*(Build.Old.END-Build.Old.START)
         d[VIRTUAL:VIRTUAL+len(virtual)]=virtual
         entry_offset=3 if counts['vectors']&1 else 0;flags=(0x20,0x21,0x60,0x61)[counts['vectors']%4]
         old=invoke(a,Build.Old.START+entry_offset,flags)
         reference=invoke(b,Build.Old.START+entry_offset,flags,oracle)
         new=invoke(d,VIRTUAL+entry_offset,flags)
         former_reads+=d.former_reads;counts['vectors']+=1
         keys=('material','registers','surface','surface_row','cell')
         if any(reference[k]!=new[k]for k in keys):
            if len(failures)<8:failures.append(dict(layout=layout,x=x,foot=foot,room=room,action=action,mode=mode,facing=facing,alternate=alternate,delta=delta,old=old,reference=reference,new=new))
            counts['mismatches']+=1
         if any(old[k]!=new[k]for k in keys):
            counts['changed_vectors']+=1
            if len(changes)<8:changes.append(dict(layout=layout,x=x,foot=foot,room=room,old=old['material'],new=new['material'],surface=new['surface']))
         if layout in('flat','pit-left','pit-right','empty')or room or mode in(2,6)or action in(10,24):
            counts['preservation_vectors']+=1
            if any(old[k]!=new[k]for k in keys):counts['preservation_mismatches']+=1
         costs.append(new['cycles']-old['cycles'])
         counts['new_point_calls']+=new['point_calls'];counts['old_point_calls']+=old['point_calls']
    q=dict(info,flat_primitive_fixture_only=True,virtual_CPU_half_open=[VIRTUAL,VIRTUAL+len(virtual)],
        virtual_code_SHA256=sha256(virtual).hexdigest(),former_function_reads=former_reads,
        counts=dict(counts),failure_examples=failures,change_examples=changes,
        whole_call_added_cycles=dict(minimum=min(costs),maximum=max(costs),total=sum(costs)),
        preserved_ABI='Both entries, caller X/Y/SP/P except final material N/Z, material, Surface/SurfaceRow and Cell.',
        not_a_fit_or_candidate=True,ordinary_gameplay_overlay=False,seeded_primitives_not_gameplay=True)
    q['primitive_semantics_passed']=not counts['mismatches']and not counts['preservation_mismatches']and former_reads==0
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--expanded',action='store_true');a=p.parse_args()
    q=run(Build.Old.F.ROM.read_bytes(),expanded=a.expanded)
    print(json.dumps(q,separators=(',',':')),flush=True)
