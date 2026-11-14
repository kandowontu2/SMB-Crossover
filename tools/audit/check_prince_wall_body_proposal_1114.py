"""Unallocated wall-read proposal: exact current preimage and primitive pairs.

The only writes beyond seeded primitive inputs are an isolated CPU arena and
one cloned decoded call operand. This is not a mounted gameplay/native fix.
"""
from hashlib import sha256
import json
from py65.assembler import Assembler
from py65.devices.mpu6502 import MPU
import re
import check_prince_world_mapping_1114 as World

SOURCE=World.F.R/'tools/reference/prince_wall_body_point_1114.s'
ARENA=0x7000


def assemble(*,labels_only=False):
    lines=[q.split(';',1)[0].strip()for q in SOURCE.read_text().splitlines()]
    labels={q[:-1]:ARENA for q in lines if q.endswith(':')}
    asm=Assembler(MPU())
    for _ in range(4):
        code=bytearray()
        for line in lines:
            if not line or line.startswith('.'):continue
            if line.endswith(':'):labels[line[:-1]]=ARENA+len(code);continue
            line=re.sub(r'\b([A-Za-z_][A-Za-z_0-9]*)\b',lambda m:f'${labels[m[1]]:04x}'if m[1]in labels else m[0],line)
            code.extend(asm.assemble(line,pc=ARENA+len(code)))
    return labels if labels_only else bytes(code)


def metadata(raw):
    World.F.authenticate(raw);packet=World.F.Packet.extract(raw)
    pattern=bytes.fromhex('209aa49003ee8cc0')
    found=[(bank,origin+i)for bank,origin,data in((3,0xa000,packet[1][0]),(2,0xc800,packet[1][1]),(2,0xc100,packet[1][2]))
        for i in range(len(data)-len(pattern)+1)if data[i:i+len(pattern)]==pattern]
    assert len(found)==1,found
    code=assemble();labels=assemble(labels_only=True)
    runtime=packet[1][0]
    calls=[dict(PC=pc,preimage=runtime[pc-0xa000:pc-0xa000+8].hex(),
        target=labels['WallBodyPoint'if pc==0xbe8f else'FloorBodyPoint'])
        for pc in(0xbe8f,0xbecb,0xbef5)]
    assert all(bytes.fromhex(q['preimage'])[:3]==bytes.fromhex('209aa4'if q['PC']==0xbe8f else'2010b3')for q in calls)
    return dict(ROM_SHA256=World.F.PIN,caller_bank=found[0][0],caller_PC=found[0][1],
        caller_preimage=pattern.hex(),calls=calls,
        proposed_helper_bytes=len(code),helper_hex=code.hex(),helper_SHA256=sha256(code).hexdigest(),
        source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),
        arena_is_unallocated=True,production_funding_granted=False,
        caller_contract='Retain wall Hand A49A including flag25 filter; specialize wall/floor/top reads only. Each caller consumes C then reloads A. Other PointRead callers unchanged.',
        body_contract='Current Source ActorX minus8 through plus7; source position, not a possibly stale native export or sprite width.',
        outputs=0,Mesen=False)


def run(raw):
    info=metadata(raw);code=assemble();base,_=World.Base.cold(raw)
    N=World.N;buffers=World.P.W.address(base.bundle,'Block_Buffer_1')
    checked=changed=0
    examples=[]
    for left in(240,256,448,464):
      for facing in(0,255):
       for delta in(-38,-32,-24,-16,-15,-8,0,15,16,24,32):
        pair=[N.fork(base),N.fork(base)];x=left+delta
        for fresh,m in enumerate(pair):
            s=m.ram[2]
            N.put(m,Player_X_Position=(x+91)&255,Player_PageLoc=(x+91)>>8)
            # Native X is deliberately stale in this primitive negative;
            # candidate must derive its body from the genuine source ABI.
            World.word(s,0x60f,x+8);s[0x611]=128;s[0x615]=facing
            s[0x616]=1;s[0x618]=1;s[0x617]=8
            World.word(s,0x89,77);s[0x8b]=128;s[0x88]=3
            s[0x4b1]=10;s[0x7a]=0;s[0x82]=0
            World.word(s,0x78,x+8-(4 if facing else 40))
            for page in range(2):
             for row in range(13):
              for col in range(16):
               wx=page*256+16*col;wy=32+16*row
               m[buffers+208*page+16*row+col]=0x54 if wy>=208 else 0x14 if left<=wx<left+16 and wy>=160 else 0
            if fresh:
                m[ARENA:ARENA+len(code)]=code
                for call in info['calls']:
                    at=call['PC']-0xa000
                    assert bytes(m.ram[3][at:at+8])==bytes.fromhex(call['preimage'])
                    m.ram[3][at+1:at+3]=call['target'].to_bytes(2,'little')
        actors=[bytes(m.ram[2][0x60e:0x747])for m in pair]
        a,b=[World.invoke(m)for m in pair]
        assert actors==[bytes(m.ram[2][0x60e:0x747])for m in pair]
        overlap=max(x,left)<min(x+16,left+16)
        cell=a['cell']
        selected_body=any(max(x,(cell+offset)&0xfff0)<min(x+16,((cell+offset)&0xfff0)+16)for offset in(24,40))
        expected=20 if overlap and a['material']==20 else 1 if selected_body else 0
        assert b['material']==expected,(left,facing,x,a,b,expected)
        assert a['surface']==b['surface']==208
        assert a['registers'][1:3]==b['registers'][1:3]and a['registers'][4]==b['registers'][4]
        assert(a['registers'][3]&0x7d)==(b['registers'][3]&0x7d)
        checked+=1;changed+=a['material']!=b['material']
        if len(examples)<6 and a['material']!=b['material']:examples.append(dict(left=left,x=x,facing=facing,old=a['material'],new=b['material']))
    # The new helper's actual callee result is retained byte-for-byte except
    # its intended carry rejection. Test flag25's existing Hand policy too.
    m=N.fork(base);m[ARENA:ARENA+len(code)]=code
    m.raw_page(1,3);m.raw_page(2,2)
    abi_pairs=0;carry_rejections=0
    def leaf(pc,p):
        c=N.NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=83,71,109,p,224
        c.stPushWord(0x5ffe)
        for _ in range(400):
            if(c.pc,c.sp)==(0x5fff,224):return(c.a,c.x,c.y,c.p,c.sp)
            c.step()
        raise AssertionError('Specialized reader ABI bound')
    for cell in(240,256,448,464):
     for delta in(-17,-16,-15,0,15,16,17):
      for same_row in(False,True):
       for action in(1,4):
        for wall,legacy in((True,0xa49a),(False,0xb310)):
         for tile in(0,0x10,0x12,0x14,0x25,0x54,0x58,0xc0):
          for flags in(0x20,0x21,0x60,0x61):
            s=m.ram[2];s[0x7c]=1 if same_row else 0;s[0x83]=1;s[0x616]=action
            World.word(s,0x60f,cell+delta+8)
            World.word(m.ram[3],0x1369,cell+8);World.word(m.ram[3],0x136b,184)
            m[buffers+((cell//256)&1)*208+((184-32)//16)*16+(cell&255)//16]=tile
            old=leaf(legacy,flags)
            target=info['calls'][0 if wall else 1]['target'];new=leaf(target,flags)
            admitted=not same_row or abs(delta)<=15
            expect_c=(old[3]&1)and admitted
            assert old[:3]==new[:3]and old[4]==new[4]
            # The modeled B bit reflects PHP/PLP, not an architectural 6502
            # flag. The enclosing WorldTile restores its original caller P.
            assert old[3]&0xee==new[3]&0xee and new[3]&1==expect_c,(cell,delta,same_row,action,wall,tile,flags,old,new,expect_c)
            abi_pairs+=1;carry_rejections+=(old[3]^new[3])&1
    # Isolate the documented original feet-context offsets on uninterrupted
    # native floor and on an actual pit. A lost own-feet floor is a rejection
    # of this proposal, not a failed gameplay route.
    feet_losses=[];feet_vectors=0
    m=N.fork(base);m[ARENA:ARENA+len(code)]=code
    for call in info['calls']:
        at=call['PC']-0xa000;m.ram[3][at+1:at+3]=call['target'].to_bytes(2,'little')
    for facing in(0,255):
     for alternate in(0,1):
      for x in range(224,256):
       for pit in(False,True):
        s=m.ram[2];World.word(s,0x60f,x+8);s[0x611]=128;s[0x615]=facing
        s[0x616]=1;s[0x618]=1;s[0x617]=8
        World.word(s,0x89,77);s[0x8b]=128;s[0x88]=3;s[0x4b1]=10;s[0x7a]=0;s[0x82]=0
        query=x+8-(20 if facing else 31)+(20 if alternate and not facing else 0)
        World.word(s,0x78,query)
        for page in range(2):
         for row in range(13):
          for col in range(16):m[buffers+208*page+16*row+col]=0x54 if row==11 and not pit else 0
        out=World.invoke(m);feet_vectors+=1
        expected=0 if pit else 1
        if out['material']!=expected:feet_losses.append(dict(facing=facing,alternate=alternate,x=x,pit=pit,material=out['material'],query=query))
    return dict(info,primitive_fixture_only=True,normal_gameplay_or_native_qualification=False,
        paired_vectors=checked,changed_material_vectors=changed,examples=examples,
        specialized_reader_ABI_pairs=abi_pairs,intended_carry_rejections=carry_rejections,
        above_row_result_registers_and_architectural_flags_exact=True,
        feet_floor_pit_vectors=feet_vectors,feet_floor_admission_mismatches=len(feet_losses),
        feet_mismatch_examples=feet_losses[:8],semantics_qualified=not feet_losses,
        stale_native_X_ignored=True,source_position_and_health_unchanged=True)


if __name__=='__main__':
    print(json.dumps(run(World.F.ROM.read_bytes()),separators=(',',':')),flush=True)
