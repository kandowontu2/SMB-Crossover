"""Verify a two-page compressed Jay cold stage with native compact transport."""
from pathlib import Path
from unittest.mock import patch
from collections import Counter
import json

import check_jay_silius_scene_lifecycle_1110 as C
import check_jay_silius_resident_funding_1110 as Funding
import measure_prince_lossless_storage_1102_v1 as Codec

H,W,N,Jay = C.H,C.W,C.N,C.Jay
SOURCE = H.ROOT/'tools/reference/jay_silius_stream_decode_1110.s'
PIN = Funding.PIN


def images(donor, original_program, linked):
    symbols = original_program['symbols']
    source = C.SOURCE.read_text()
    helper = source[source.index('JayConstruct:'):source.index('HotCookie:')]
    variables = {k:v for k,v in symbols.items() if k not in ('JayConstruct','PublishPosition','HotCookie',
        'DonorActorTemplate','CopyActorTemplate','ScaleVY','PublishState')}
    constants = ''.join(f'{key} = ${value:04x}\n' for key,value in variables.items())
    ordered = sorted((a,l) for l,a in linked['ram'].items() if a<0xc0f0)
    template = bytes(donor.memory.ram[logical] for _,logical in ordered)
    guards=source[source.index(' lda OperMode\n'):source.index(' jmp CheckHeaders\n')]
    guards=guards.replace('GoLegacy','Unsupported')
    driver = '''
.segment "EXTRA"
PrivateUpdate:
'''+guards+'''
 lda Ready
 bne HasActor
 jsr JayConstruct
 jmp Update
HasActor:
 lda FrameCounter
 cmp Epoch
 beq ReturnUpdate
Update:
 lda FrameCounter
 sta Epoch
 lda Player_X_Position
 sta OldX
 lda PadNow
 sta PadPrevious
 lda SavedJoypadBits
 sta PadNow
 jsr OriginalInput
 jsr PositionSetup
 ldx #0
 jsr Integrate
 jsr PublishPosition
ReturnUpdate:
 sec
 rts
Unsupported:
 clc
 rts
'''
    text = constants+driver+helper+'DonorActorTemplate:\n.byte '+','.join(map(str,template))+'\n'
    extra = H.assemble(text,{'EXTRA':(0xa785,1024)})
    runtime = linked['images']['PRIVATE'] + extra['images']['EXTRA']
    packed = Codec.encode(runtime)
    definitions = f'DecodedEnd = ${0xa000+len(runtime):04x}\nPackedEnd = $d800\n'
    decoder = H.assemble(definitions+SOURCE.read_text(),{'DECODE':(0xd000,512)})
    size = len(decoder['images']['DECODE'])+len(packed)
    assert size<=2048, (len(runtime),len(packed),len(decoder['images']['DECODE']),size)
    definitions = f'DecodedEnd = ${0xa000+len(runtime):04x}\nPackedEnd = ${0xd000+size:04x}\n'
    decoder = H.assemble(definitions+SOURCE.read_text(),{'DECODE':(0xd000,512)})
    stage = decoder['images']['DECODE']+packed
    return runtime,stage.ljust(2048,b'\xea'),decoder,extra,dict(runtime=len(runtime),
        extra=len(extra['images']['EXTRA']),packed=len(packed),decoder=len(decoder['images']['DECODE']),
        two_page_stage=size,spare=2048-size)


def proposal(raw,donor):
    assert C.digest(raw)==PIN
    with patch.object(C,'ROM_PIN',PIN):
        _,_,prior,linked,_,_,_=C.proposal(raw,donor)
    runtime,stage,decoder,extra,sizes=images(donor,prior,linked)
    worker = ''' lda #$fb
 jmp FarCall
OriginalCopy:'''
    successor = ''' lda #$fb
 jsr FarCall
 bcc StreamReturn
 lda #0
 sta FarTargetLo
 lda #$d0
 sta FarTargetHi
 lda #3
 jmp FarCall
StreamReturn:
 rts
OriginalCopy:'''
    original_assembler = C.HostAssemble

    def assemble(text,layout):
        assert text.count(worker)==1 and text.count('.byte 2,2,1,$4b,1,$4c,1')==1
        text=text.replace(worker,successor).replace('.byte 2,2,1,$4b,1,$4c,1','.byte 2,0,1,$4b,1,$4c,1')
        return original_assembler(text,layout)

    # The frozen proposal's descriptor equality refers to its old code-rows
    # format. Supply it unchanged first, then alter only the isolated program.
    with patch.object(C,'ROM_PIN',PIN):
        base,trial,program,_,_,_,redirects=C.proposal(raw,donor)
    text=program['source']
    program=assemble(text,C.LAYOUT)
    descriptor=program['images']['DESCRIPTOR']
    cookie=bytes((0xa7,16,32,2))+C.sha256(stage+runtime+descriptor).digest()[:12]
    for section,label in (('COLD','ColdCookie'),('HOT','HotCookie')):
        data=bytearray(program['images'][section])
        at=program['symbols'][label]-C.LAYOUT[section][0]
        data[at:at+16]=cookie
        program['images'][section]=bytes(data)
    image=bytearray(raw)
    for bank,pc,old,label in ((65,0xac2c,'2026b0','JaySceneOrRetire'),
        (65,0xaf00,'ad0260','JaySelect'),(65,0xae85,'2072ab','JayCopyOrLegacy'),(96,0xa53d,'4ccba2','JayHot')):
        at=C.offset(bank,pc)
        assert image[at:at+3]==bytes.fromhex(old)
        image[at:at+3]=bytes((0x20 if old.startswith('20')else 0x4c,))+program['symbols'][label].to_bytes(2,'little')
    for i,page in enumerate(C.PAGES):
        image[C.CHR+1024*page:C.CHR+1024*(page+1)]=stage[1024*i:1024*(i+1)]
    return base,dict(base,raw=bytes(image)),program,linked,runtime,stage,cookie,decoder,extra,sizes


def decoder_vectors(trial,program,decoder,runtime,cookie):
    m=C.Common.blank(trial)
    C.stage_fixture(m,program)
    C.Common.scene(m,16)
    m[0x730b]=32
    c=C.ColdVector.entry(m)
    instructions={i['pc']for i in decoder['instructions']}
    seen=set()
    counts=Counter()
    resumed=set()
    for _ in range(2_000_000):
        if (c.pc,c.sp)==(C.STOP,224):break
        if m.rawtags[2]==2 and c.pc in instructions:
            assert not m.ram[2][0x1fe0] and not m.ram[3][0x1fe0] and c.p&4
            key=(c.pc,c.sp,m[6] if c.pc in (decoder['symbols']['ReadByte'],decoder['symbols']['WriteByte']) else None)
            if key not in seen:
                seen.add(key)
                q,d=C.Vector.clone(m,c)
                C.ColdVector.interrupt(d,'FF')
                counts['actual_forcedblank_NMI']+=1
                q,d=C.Vector.clone(m,c)
                before=C.Vector.regs(d)
                d.irq()
                assert C.Vector.regs(d)==before
                counts['actual_SEI_masked_IRQ']+=1
            if c.pc==decoder['symbols']['WriteByte'] and m[6] not in resumed:
                resumed.add(m[6])
                C.ColdVector.interrupt(c,'FF')
                counts['resumed_NMI_output_pages']+=1
        C.ColdVector.step(c)
    else:raise AssertionError(('stream cold bound',hex(c.pc)))
    assert c.p&1 and C.Common.headers(m)==(cookie,)*2 and bytes(m.ram[3][:len(runtime)])==runtime
    assert len(resumed)==9
    for encoded in (bytes((1,0,0)),bytes((1,1,0))):
        q=C.Vector.clone(m)
        q.raw_page(1,3);q.raw_page(2,2)
        N.put(q,CurrentBank=3,CurrentBankC=2)
        at=decoder['symbols']['PackedData']-0xc000
        q.ram[2][at:at+len(encoded)]=encoded
        q.ram[2][0x1fe0]=q.ram[3][0x1fe0]=0
        d=N.NesMPU(memory=q,pc=0xd000)
        d.a,d.x,d.y,d.p,d.sp=0,0,0,0x35,224
        d.stPushWord(C.STOP-1)
        C.Motion.run(d,(C.STOP,224))
        assert not d.p&1 and not q.ram[2][0x1fe0] and not q.ram[3][0x1fe0]
        counts['malformed_reference_rejected']+=1
    return dict(counts)


def main():
    donor=C.actual_donor()
    base,trial,program,linked,runtime,stage,cookie,decoder,extra,sizes=proposal(H.ROM.read_bytes(),donor)
    print('Jay exact streamed sizes',sizes,flush=True)
    m=C.Common.blank(trial)
    C.stage_fixture(m,program)
    C.Common.scene(m,16)
    m[0x730b]=32
    c,cuts=C.native_cold(m,program,vectors=True)
    assert c.p&1 and C.Common.headers(m)==(cookie,)*2
    assert bytes(m.ram[3][:len(runtime)])==runtime
    assert bytes(m.ram[2][0x1000:0x1800])==stage
    assert m.ppu_reads==4100
    before=m.ppu_reads
    assert C.native_cold(m,program)[0].p&1 and m.ppu_reads==before
    before_headers=C.Common.headers(m)
    for bank,at in ((3,0),(3,len(runtime)-1),(2,0x1000)):
        q=C.Vector.clone(m)
        q.ram[2][0x1fe0]=q.ram[3][0x1fe0]=0
        q.corrupt_at=(bank,at)
        assert not C.native_cold(q,program)[0].p&1
        assert all(not h[0] for h in C.Common.headers(q))
    assert C.Common.headers(m)==before_headers
    native=C.menu(trial,1,program)
    hot=C.ready(native,program,donor,linked,1,[0]*8+[1]*28+[128]*14+[0]*36)
    assert hot['counts']['private_motion']==hot['counts']['real_donor_weapon_import']==86
    assert hot['snapshots'][-1][1]==3072 and min(y for _,y in hot['snapshots'])==2232
    assert bytes(native.ram[3][:len(runtime)])==runtime and C.Common.headers(native)==(cookie,)*2
    decoder_cuts=decoder_vectors(trial,program,decoder,runtime,cookie)
    transitions=[]
    for owner in range(37,44):
        q=C.Common.blank(trial)
        C.stage_fixture(q,program)
        C.Common.scene(q,owner)
        assert C.native_cold(q,program)[0].p&1
        previous=C.Common.headers(q)
        C.Common.scene(q,16)
        q[0x730b]=32
        assert C.native_cold(q,program)[0].p&1
        assert bytes(q.ram[3][:len(runtime)])==runtime and C.Common.headers(q)==(cookie,)*2
        C.Common.scene(q,owner)
        assert C.native_cold(q,program)[0].p&1 and C.Common.headers(q)==previous
        transitions.append(owner)
    print(json.dumps(dict(passed=True,ROM_SHA256=PIN,ROM_written=False,Mesen=False,build_files=0,
        sizes=sizes,runtime_SHA256=C.digest(runtime),stage_SHA256=C.digest(stage),cookie=cookie.hex(),
        compact_worker_PPU_reads=4100,warm_PPU_reads=0,current_cold_vectors=cuts,decoder_vectors=decoder_cuts,
        bidirectional_cold_owner_transitions=transitions,
        natural_Main_updates=86,terminal_native=hot['reports'][-1],donor_center=hot['snapshots'][-1],
        private_entry=hex(extra['symbols']['PrivateUpdate']),resident_still_ungranted=program['used']),sort_keys=True),flush=True)


if __name__=='__main__':
    main()
