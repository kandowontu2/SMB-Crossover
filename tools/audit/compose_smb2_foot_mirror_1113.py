"""Exact source-authenticated fixed120 head/feet/side mirror synchronization."""
from hashlib import sha256
import json

import compose_smb2_flag_handoff_1113 as Flag
from compose_metal_head_bridge_1112 import assemble_segments

PARENTS=(Flag.PIN,'0e9e9254927236bcc651e79da36a77924eea5481421858a05f869b15298412e1')
START=0xe45b
SIZE=63
AT=16+120*8192+(START&8191)
OLD=bytes.fromhex('8d6a01a9e38d6c01a9b98d6d01a9854c5a01ad0260c904f010c90bf00cc916f008c91af004c91cd00fa9e78d6c01a9b68d6d01a9bf4c5a014c8695ea4ce490')
SOURCE=Flag.Check.R/'tools/reference/sonic_shared_feet_1110.s'
CLONE_SOURCE=Flag.Check.R/'build/thomas-natural-host-1031-v6/source/dmc-clones.s'
ORIGINS=dict(HEAD=0xe45b,FOOT=0xe46a,SIDE=0xe497,DEFAULT=0xbc93,UNION=0xbfb0,SH_TAIL=0xac10)
MIRRORS=(119,120,125)
ALL_IMAGES=dict(zip(PARENTS,('690482ef99abb5cc9c4e1cc1bcfecc81fce391722a60ff4bdb3c0f7aa1b87ac3',
    '2c62e1a0de1b732cfa57af59e71c0775396e067bf04aa101e78f644c3e4c9c4b'),strict=True))


def code():
    bodies,labels=assemble_segments(SOURCE.read_text(),ORIGINS,{})
    assert tuple(len(bodies[n])for n in('HEAD','FOOT','SIDE'))==(15,45,3)
    new=bodies['HEAD']+bodies['FOOT']+bodies['SIDE']
    assert len(new)==len(OLD)==SIZE
    return new,labels


def plan(raw):
    pin=sha256(raw).hexdigest();assert pin in PARENTS
    if pin==PARENTS[1]:assert sha256(Flag.inverse(raw)).hexdigest()==PARENTS[0]
    new,labels=code()
    assert raw[AT:AT+SIZE]==OLD
    canonical=16+127*8192+(START&8191)
    assert raw[canonical:canonical+SIZE]==new
    native=16+126*8192
    assert raw[native+0x1c0a:native+0x1c0d]==bytes.fromhex('206ae4')
    assert raw[native+0x1c13:native+0x1c16]==bytes.fromhex('206ae4')
    exact_old=[];exact_new=[];head_prefix=[];calls={};prefix_diffs={}
    for bank in range(128):
        at=16+bank*8192+(START&8191);body=raw[at:at+SIZE]
        if body==OLD:exact_old.append(bank)
        if body==new:exact_new.append(bank)
        if body[:18]==OLD[:18]:head_prefix.append(bank)
        page=raw[16+bank*8192:16+(bank+1)*8192]
        hits=[i for i in range(len(page)-2)if page[i:i+3]in(bytes.fromhex('206ae4'),bytes.fromhex('4c6ae4'))]
        if hits:calls[str(bank)]=[hex(i)for i in hits]
    reference=raw[16+127*8192:16+127*8192+4416]
    for bank in(119,120,125):
        copy=raw[16+bank*8192:16+bank*8192+4416]
        differences=[i for i,(a,b)in enumerate(zip(copy,reference,strict=True))if a!=b]
        spans=[]
        for at in differences:
            if spans and at==spans[-1][1]:spans[-1][1]+=1
            else:spans.append([at,at+1])
        prefix_diffs[str(bank)]=dict(bytes=len(differences),ranges=spans)
    clones=CLONE_SOURCE.read_text()
    assert clones.count(',0,4416')==2
    assert all('.segment "S2_DMC_E'+str(bank)+'"'in clones for bank in(119,120))
    assert START&8191<4416 and(START&8191)+SIZE<=4416
    writers=(Flag.Check.R/'src/smb2_roster_audio_writers.inc').read_text()
    assert'S2AudioSampleBank: .byte 120,120,120,119,120,120,119,119'in writers
    return dict(parent_SHA256=pin,source=str(SOURCE.relative_to(Flag.Check.R)),
        source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),fixed120_span=[AT,SIZE],
        fixed120_old_SHA256=sha256(OLD).hexdigest(),fixed127_source_SHA256=sha256(new).hexdigest(),
        old_hex=OLD.hex(),source_hex=new.hex(),old_body_banks=exact_old,new_body_banks=exact_new,
        old_head_prefix_banks=head_prefix,raw_JSR_JMP_E46A_matches=calls,
        clone_source=str(CLONE_SOURCE.relative_to(Flag.Check.R)),clone_source_SHA256=sha256(CLONE_SOURCE.read_bytes()).hexdigest(),
        clone_code_prefix=4416,code_prefix_differences=prefix_diffs,
        source_mirror_roles={'119':'SMB2 DMC requests128/64/8','120':'SMB2 DMC requests1/32/4/16',
            '125':'CV3 DMC E clone; prepare_cv3_dmc_mirror.py copies127 outside declared sample/manager intervals'},
        HEAD_bytes=15,FOOT_bytes=45,SIDE_bytes=3,extra_RAM_bytes=0,extra_ROM_bytes=0,
        following_fixed_bytes_unchanged=True,controller_or_physics_changes=False)


def proposal(raw):
    info=plan(raw);new,_=code();out=bytearray(raw);out[AT:AT+SIZE]=new
    image=bytes(out);info.update(ROM_SHA256=sha256(image).hexdigest(),
        changed_bytes=sum(a!=b for a,b in zip(raw,image,strict=True)))
    return image,info


def inverse(raw):
    new,_=code();assert raw[AT:AT+SIZE]==new
    out=bytearray(raw);out[AT:AT+SIZE]=OLD;parent=bytes(out)
    assert sha256(parent).hexdigest()in PARENTS
    assert proposal(parent)[0]==raw
    return parent


def all_mirrors_proposal(raw):
    info=plan(raw);new,_=code()
    grant=json.loads((Flag.Check.R/'docs/qa/allocations/shared-feet-mirror-1113.json').read_text())
    assert grant['exact_existing_mirror_banks']==list(MIRRORS)
    assert grant['preimage_SHA256']==sha256(OLD).hexdigest()
    assert grant['new_source_SHA256']==sha256(new).hexdigest()
    out=bytearray(raw);spans=[]
    for bank in MIRRORS:
        at=16+bank*8192+(START&8191);assert raw[at:at+SIZE]==OLD
        out[at:at+SIZE]=new;spans.append([at,SIZE])
    image=bytes(out);info.update(ROM_SHA256=sha256(image).hexdigest(),all_mirrors=True,
        exact_changed_spans=spans,changed_bytes=sum(a!=b for a,b in zip(raw,image,strict=True)),
        grant='docs/qa/allocations/shared-feet-mirror-1113.json')
    assert info['ROM_SHA256']==ALL_IMAGES[info['parent_SHA256']]
    return image,info


def all_mirrors_inverse(raw):
    new,_=code();out=bytearray(raw)
    for bank in MIRRORS:
        at=16+bank*8192+(START&8191);assert raw[at:at+SIZE]==new
        out[at:at+SIZE]=OLD
    parent=bytes(out);assert sha256(parent).hexdigest()in PARENTS
    assert all_mirrors_proposal(parent)[0]==raw
    return parent


if __name__=='__main__':
    print(json.dumps(dict(**plan(Flag.Check.ROM.read_bytes()),proposal_only=True,outputs=0,Mesen_run=False)),flush=True)
