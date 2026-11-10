"""Packed ordinary-source payload and partial eighth-row cold boot, in RAM.

Physical330 is conditional on its new ledger/preimage and mandatory Z2 alias.
No file/cartridge is produced; Prince329, canonical319/320 and world335 stay.
The final row copies992 bytes only, preserving BFE0..BFFF header/envelope.
"""
import ast
from hashlib import sha256
import inspect
import struct
from types import SimpleNamespace
from unittest.mock import patch

import sonic_sms_native_frame_bridge_1110 as Frame
import sonic_sms_cold_payload_1110 as OldCold

CODE_PAGES=(*range(321,328),330)
META_PAGE=328
COPY_BYTES=0x1fe0


def packed():
    s=Frame.Selector;w=s.Witness;h=w.Shape;p=h.Point
    core=h.Core.build()
    point=p.build(code=core['code_half_open'][1])
    # The frozen shape builder pins the old PointRead address image.  This
    # derivative changes that one dependency pin to the newly assembled image;
    # relocation_proof below independently checks every operand/data byte.
    source=inspect.getsource(h.build)
    old_pin="'82ee77ec5d6923e2e28e7bec31c9fb8a9b55922ec72dd525b1be74e61749771d'"
    assert source.count(old_pin)==1
    source=source.replace(old_pin,repr(sha256(point['image']).hexdigest()))
    scope=dict(h.__dict__);scope['Point']=SimpleNamespace(build=lambda:point)
    exec(compile(source,'<relocated frozen shape builder>','exec'),scope)
    shape=scope['build'](code=point['code_half_open'][1])
    with patch.object(w.Shape,'build',return_value=shape):
        witness=w.build(code=shape['code_half_open'][1])
    with patch.object(s.Witness,'build',return_value=witness):
        selector=s.build(code=witness['code_half_open'][1])
    with patch.object(Frame.Selector,'build',return_value=selector):
        frame=Frame.build(code=selector['code_half_open'][1])
    return frame


def blocks(frame):
    selector=frame['selector'];witness=selector['witness'];shape=selector['shape']
    return dict(core=shape['core'],point=shape['point'],shape=shape,witness=witness,selector=selector,frame=frame)


def relocation_proof(old,new):
    a,b=blocks(old),blocks(new)
    assert a['core']['image']==b['core']['image']
    def translate(value):
        for name,block in a.items():
            lo,hi=block['code_half_open']
            if lo<=value<hi:return value+b[name]['code_half_open'][0]-lo
        return value
    counts={}
    for name in('point','shape','witness','selector','frame'):
        left,right=a[name],b[name]
        assert len(left['image'])==len(right['image'])
        li,ri=left['instructions'],right['instructions'];assert len(li)==len(ri)
        covered=set()
        for x,y in zip(li,ri,strict=True):
            assert (x['op'],x['mode'])==(y['op'],y['mode'])
            assert x['pc']-left['code_half_open'][0]==y['pc']-right['code_half_open'][0]
            expected=translate(x['operand'])if x['mode']in('abs','abx','aby','ind','rel')else x['operand']
            assert y['operand']==expected,(name,x,y,expected)
            size=Frame.Selector.Witness.Shape.Core.SIZES[x['mode']]
            covered.update(range(x['pc']-left['code_half_open'][0],x['pc']-left['code_half_open'][0]+size))
        assert all(left['image'][i]==right['image'][i]for i in range(len(left['image']))if i not in covered)
        counts[name]=len(li)
    return dict(instructions=counts,core5526_exact=True,all_code_targets_relocated_only=True,
        private_and_host_operands_immediates_and_noninstruction_data_exact=True,
        recovered_gap_bytes=old['code_half_open'][1]-new['code_half_open'][1])


def startup():
    tree=ast.parse(OldCold.REFERENCE.read_text())
    assignment=next(n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='BOOT'for t in n.targets))
    source=ast.literal_eval(assignment.value)
    for label in('Copy','Verify'):
        old=f' iny\n bne {label}\n inc R1'
        new=(f' iny\n beq {label}PageDone\n cpy #$e0\n bne {label}\n'
             f' lda R1\n cmp #$bf\n bne {label}\n{label}PageDone:\n inc R1')
        assert source.count(old)==1
        source=source.replace(old,new)
    result=OldCold.boot(source,CODE_PAGES)
    assert len(result['image'])==139 and OldCold.BOOT_PC+len(result['image'])<=0xd300
    return result


def build():
    old=Frame.build();frame=packed();parts=blocks(frame);proof=relocation_proof(old,frame)
    image=bytearray(b'\xff'*8192)
    cursor=0xa000
    for name,block in parts.items():
        lo,hi=block['code_half_open'];assert lo==cursor
        image[lo-0xa000:hi-0xa000]=block['image'];cursor=hi
    assert cursor==frame['code_half_open'][1] and cursor<=0xbfe0
    metadata=bytearray(b'\xff'*1024);metadata[:8]=b'SMSONIC2'
    core=parts['core'];metadata[8:22]=struct.pack('<7H',cursor-0xa000,
        frame['symbols']['SonicNativeOrdinaryFrame'],0xc000,0xc100,0xa000,0xbfe0,4)
    metadata[22:30]=struct.pack('<4H',*core['SMC_operands'])
    metadata[30:46]=struct.pack('<8H',frame['symbols']['SonicOriginalObjectConstructor'],
        parts['selector']['symbols']['SonicSweptHorizontal'],parts['selector']['symbols']['SonicSweptVertical'],
        parts['witness']['symbols']['SonicSweepCapture'],Frame.RECORD,Frame.SNAPSHOT,
        core['symbols']['OrdinaryFrame'],cursor)
    boot=startup();offset=OldCold.BOOT_PC-0xd000
    metadata[offset:offset+len(boot['image'])]=boot['image']
    cookie=bytes((0xa7,43,1))+sha256(image+metadata).digest()[:13]
    return dict(frame=frame,core=core,kernel=bytes(image),metadata=bytes(metadata),cookie=cookie,
        startup=boot,code_pages=CODE_PAGES,metadata_page=META_PAGE,copy_bytes=COPY_BYTES,
        source_payload_bytes=cursor-0xa000,remaining_before_header=0xbfe0-cursor,
        relocation=proof,proposed_service_base=cursor,
        descriptor_three_byte=bytes((1,0,9,META_PAGE&255,META_PAGE>>8)),
        descriptor_legacy=bytes((1,0,9,0xd0,META_PAGE&255,META_PAGE>>8)),
        zero_state_half_open=[0xc000,0xc900],
        scope='Conditional packed eighth330 source payload/cold boot only. No live RAM, service table, actor epoch, publicraw43, render/effects or native gameplay grant.')
