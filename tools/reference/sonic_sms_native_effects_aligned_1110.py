"""D100-aligned38-row envelope within the same Sonic source grants.

Moves only separately assembled bridge/effect code and table; the frozen
motor, PointRead, contact code and original frame prefix stay exact.
"""
from hashlib import sha256
import struct
import sonic_sms_native_effects_1110 as Base
from sonic_sms_compact_cold_worker_1110 import assemble


def between(source,start,end):
    return source.split(start+':',1)[1].split(end+':',1)[0].join((start+':',''))


def build(bundle):
    p=Base.build(bundle);source=Base.SOURCE
    parts={name:between(source,name,end)for name,end in(
        ('MetaHorizontal','MetaVertical'),('MetaVertical','MetaClassify'),('MetaClassify','MetaBounds'),
        ('MetaBounds','MetaAdder'),('MetaAdder','MetaHead'),('MetaHead','MetaGraphics'),('MetaGraphics','MetaDraw'))}
    draw,death=source.split('MetaDraw:',1)[1].split('MetaDeath:',1)
    parts['MetaDraw']='MetaDraw:'+draw
    death='MetaDeath:'+death
    adder,body=parts['MetaAdder'].split('MetaBody:',1)
    body='MetaBody:'+body
    # Only the three viewport-empty branches cross code windows after this
    # packing; inverse+absoluteJMP preserves every original branch predicate.
    vertical=parts['MetaVertical']
    inverses={'bne':'beq','bcc':'bcs','bcs':'bcc'}
    for i,(old,new)in enumerate(inverses.items()):
        needle=f' {old} MetaEmpty';assert vertical.count(needle)==1
        label=f'MetaViewportInRange{i}'
        vertical=vertical.replace(needle,f' {new} {label}\n jmp MetaEmpty\n{label}:')
    head,feet=parts['MetaHead'].split('MetaFeet:',1)
    feet='MetaFeet:'+feet
    feet=feet.replace(' bmi MetaEffectReturn',' bpl MetaFootCoins\n jmp MetaEffectReturn\nMetaFootCoins:')
    # The predecessor's definition/import preamble is retained, and every
    # moved symbol is rebound by an actual assembler label in this program.
    common='\n'.join(f'{n}=${v:04x}'for n,v in p['metadata']['symbols'].items())+'\n'
    svc=p['service']['source']
    needle='.segment "SERVICES"\nSonicServices:';assert svc.count(needle)==1
    svc=svc.replace(needle,'.segment "VECTORS"\nSonicServices:')
    text=(common+svc+'\n.segment "SERVICES"\n'+parts['MetaHorizontal']+parts['MetaClassify']+
        parts['MetaGraphics']+feet+'\n.segment "META1"\n'+vertical+parts['MetaBounds']+body+death+
        '\n.segment "META2"\n'+head+parts['MetaDraw']+adder)
    start=p['service']['code_half_open'][0]
    program=assemble(text,{'SERVICES':(start,0xbfe0-start),'META1':(0xd040,0xc0),
        'VECTORS':(0xd100,114),'META2':(0xd172,0xec)})
    images=program['images'];used=program['used'];assert used['VECTORS']==114
    private_end=start+used['SERVICES']
    result=dict(p['service'],image=images['SERVICES'],source=text,symbols=program['symbols'],
        instructions=[i for i in program['instructions']if i['segment']=='SERVICES'],
        code_half_open=[start,private_end],remaining_before_header=0xbfe0-private_end,
        image_SHA256=sha256(images['SERVICES']).hexdigest())
    kernel=bytearray(p['packet']['kernel']);metadata=bytearray(p['packet']['metadata'])
    oldlo,oldhi=p['service']['code_half_open'];kernel[oldlo-0xa000:oldhi-0xa000]=b'\xff'*(oldhi-oldlo)
    kernel[start-0xa000:private_end-0xa000]=images['SERVICES']
    for pc,old,new in p['frame_terrain_calls']:
        assert kernel[pc-0xa000]==0x20
        name='MetaHorizontal'if old==p['packet']['frame']['symbols']['SweptH']else'MetaVertical'
        kernel[pc-0xa000+1:pc-0xa000+3]=struct.pack('<H',program['symbols'][name])
    selector=p['packet']['frame']['selector'];pc=selector['symbols']['Classify']
    assert kernel[pc-0xa000]==0x20
    kernel[pc-0xa000+1:pc-0xa000+3]=struct.pack('<H',program['symbols']['MetaClassify'])
    metadata[0x40:0x25e]=b'\xff'*(0x25e-0x40)
    for segment,at in(('META1',0xd040),('VECTORS',0xd100),('META2',0xd172)):
        metadata[at-0xd000:at-0xd000+used[segment]]=images[segment]
    metadata[:8]=b'SMSONIC4';metadata[8:10]=struct.pack('<H',private_end-0xa000)
    metadata[44:46]=struct.pack('<H',0xd100)
    metadata[46:62]=struct.pack('<8H',0xd100,program['symbols']['SonicHostMain'],program['symbols']['SonicHostFresh'],
        program['symbols']['SonicHostPowerup'],*result['context_half_open'],program['symbols']['SonicHostConstruct'],38)
    assert metadata[62:64]==b'\xff\xff'
    assert metadata[0x25e:0x2e9]==p['packet']['metadata'][0x25e:0x2e9]
    assert kernel[:5526]==p['packet']['kernel'][:5526]
    cookie=bytes((0xa7,43,1))+sha256(kernel+metadata).digest()[:13]
    packet=dict(p['packet'],kernel=bytes(kernel),metadata=bytes(metadata),cookie=cookie,
        source_payload_bytes=private_end-0xa000,remaining_before_header=0xbfe0-private_end,
        proposed_service_base=0xd100,host_services=result)
    return dict(p,packet=packet,service=result,metadata=program,metadata_half_open=[0xd040,0xd25e],
        metadata_segments={name:[at,at+used[name]]for name,at in(('META1',0xd040),('VECTORS',0xd100),('META2',0xd172))},
        remaining_metadata_bytes=0x21e-used['META1']-used['VECTORS']-used['META2'],remaining_private_bytes=0xbfe0-private_end,
        scope='Unqualified aligned transport derivative; dedicatedD100 envelope inside authenticated RAM2 metadata, original core atA000 exact. Root public dispatcher must selecthighD1 onlyforraw43 afterfullheaders; no public gate/ROM/RAMlease.')
