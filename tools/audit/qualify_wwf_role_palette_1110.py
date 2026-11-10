"""Bounded CPU qualification of packed masks, native packets and role palettes."""
from collections import Counter
from hashlib import sha256
import json

import check_wwf_role_palette_1110 as P

W,N,L=P.W,P.N,P.L


def direct(m,pc,a=83,x=0,y=37,p=0x31,observe=None):
    m.raw_page(1,224)
    m.raw_page(2,2)
    N.put(m,CurrentBank=224,CurrentBankC=2)
    W.clear_logs(m)
    c=N.NesMPU(memory=m,pc=pc)
    c.a,c.x,c.y,c.p,c.sp=a,x,y,p,224
    c.stPushWord(0x5aff)
    return L.finish(m,c,(0x5b00,224),observe)


def snapshot(m,ignore=()):
    r=[bytearray(z) for z in m.ram]
    for bank,offset,size in ignore:r[bank][offset:offset+size]=bytes(size)
    return (bytes(m[:0x100]),bytes(m[0x200:0x800]),bytes(m[0x5c00:0x8000]),
            tuple(bytes(z) for z in r),tuple(m.rawtags))


def main():
    parent,_=P.Stage.reconstruct();image,record=P.proposal(parent)
    b=W.Symbols.bundle();b['raw']=image
    rows=P.P.C.Starts.C.inventory(image)['rows']
    seeds=[];cases=Counter()
    for role in range(6):
        row=next(r for r in rows if r['slot']==28 and r['cycle']==role)
        cold,m=P.P.C.cold(b,row)
        assert cold['passed']
        assert bytes(m.ram[2][0x1fe0:0x1ff0])==P.cookies(image,b)[16*role:16*(role+1)]
        assert N.get(m,'SelectedCharacter')==29 and N.get(m,'FmGroups')&7==role
        m.raw_page(1,224);m.raw_page(2,2)
        N.put(m,CurrentBank=224,CurrentBankC=2)
        seeds.append(m);cases['six_actual_native_cold_and_full_owner_cookie']+=1
    source_mask=parent[W.location(b,'WfNativeP1Mask'):W.location(b,'WfNativeP1Mask')+145]
    syms=record['symbols']
    # Literal original masks, including $f and $3, not an all-native assumption.
    for obj in range(145):
        for actor in (1,5,23):
            for flags in (0x20,0x31,0x70,0xf9):
                m=L.clone(seeds[0]);before=snapshot(m,[(2,W.address(b,'WfP1Temp')&8191,1)])
                c=direct(m,syms['WfReadPackedMask'],a=obj,x=actor,p=flags)
                assert (c.a,c.x,c.sp)==(source_mask[obj],actor,224)
                assert bool(c.p&2)==(source_mask[obj]==0) and not c.p&128
                # Only the already-owned scratch byte is used by the leaf.
                assert snapshot(m,[(2,W.address(b,'WfP1Temp')&8191,1)])==before
                assert bytes(m[3:11])==before[0][3:11]
                assert m.ram[2][W.address(b,'WfP1Temp')&8191]==source_mask[obj]
                cases['literal_mask_actor_flags']+=1
    early=W.address(b,'WfP1Early')
    parent_c2=P.private_images(parent,b)[1]
    early_delta=[i for i,(a,z) in enumerate(zip(parent_c2,P.private_images(image,b)[1])) if a!=z]
    ignores=[(2,i,1) for i in early_delta]+[(2,0x1fe0,16)]
    for obj in range(256):
        for attr in range(4):
            results=[]
            for raw in (parent,image):
                m=L.clone(seeds[0]);m.bundle=dict(b,raw=raw)
                # Genuine current selected RAM, with only the versioned code and
                # cookie rebound to the corresponding source image for the pair.
                cc=P.private_images(raw,b)[1]
                for i in early_delta:m.ram[2][i]=cc[i]
                m.ram[2][0x1fe0:0x1ff0]=P.cookies(raw,b)[:16]
                N.put(m,NmiDisable=255)
                for actor in range(24):
                    m[W.address(b,'ObjectMetasprite')+actor]=(obj+actor-1)&255
                    m[W.address(b,'SprObject_SprAttrib')+actor]=(attr+actor)&255
                c=direct(m,early,a=83,x=7,y=46,p=0xf1)
                results.append((L.regs(c),snapshot(m,ignores)))
            assert results[0]==results[1],('whole EarlyActor differential',obj,attr)
            cases['whole_EarlyActor_exact_AXYP_and_application']+=1
    packets=W.location(b,'WfRolePackets')
    first=[parent[packets+13*i+9] for i in range(6)]
    second=[parent[packets+13*i+10] for i in range(6)]
    for role,seed in enumerate(seeds):
        for area in range(4):
            for freeze in (0,1,2,3,4,5,8,255):
                for choice in (0,1):
                    pair=[]
                    for raw in (parent,image):
                        m=L.clone(seed);m.bundle=dict(b,raw=raw)
                        N.put(m,AreaType=area,SmFreezePaletteControl=freeze,WfP1Choice=choice)
                        c=direct(m,W.address(b,'WfP1MakePacket'))
                        value=bytes(m.ram[2][0x1eb8:0x1ebf]);pair.append(value)
                        assert value[:3]==bytes.fromhex('3f1503') and value[6]==0
                        if choice and raw==image:
                            assert value[3:6]==bytes((first[role],second[role],15)),(role,value.hex())
                    if not choice or role==0:assert pair[0]==pair[1]
                    cases['owned_role_or_unchanged_native_palette_packet']+=1
        # Cancellation recognizes all six source palettes without reading any
        # selected cookie, including when the invalid-cache restore path calls.
        for palette_role in range(6):
            m=L.clone(seed)
            command=bytes((63,21,3,first[palette_role],second[palette_role],15,0))
            start=W.address(b,'VRAM_Buffer1')
            for i,v in enumerate(command):m[start+i]=v
            N.put(m,VRAM_Buffer1_Offset=6,AreaType=1,SmFreezePaletteControl=0)
            m.ram[2][0x1fe0:0x1ff0]=bytes(16)
            direct(m,W.address(b,'WfP1CancelQueuedOwn'))
            assert bytes(m[start:start+7])==bytes((63,21,3,26,48,39,0))
            cases['all_source_palettes_cancel_without_private_cookie']+=1
        for command in (bytes.fromhex('3f150316060f00'),bytes.fromhex('3f150326001700'),
                        bytes.fromhex('3f110327070f00'),bytes.fromhex('3f154316050f00'),
                        bytes.fromhex('3f150016050f00')):
            m=L.clone(seed);start=W.address(b,'VRAM_Buffer1')
            for i,v in enumerate(command):m[start+i]=v
            N.put(m,VRAM_Buffer1_Offset=6)
            direct(m,W.address(b,'WfP1CancelQueuedOwn'))
            assert bytes(m[start:start+len(command)])==command
            cases['unrelated_or_malformed_packet_retained']+=1
    print(json.dumps(dict(passed=True,CPU_only=True,Mesen_run=False,ROM_written=False,
        output_files=0,parent_SHA256=P.Stage.PIN,ROM_SHA256=sha256(image).hexdigest(),
        cases=dict(cases),record=record),sort_keys=True),flush=True)


if __name__=='__main__':main()
