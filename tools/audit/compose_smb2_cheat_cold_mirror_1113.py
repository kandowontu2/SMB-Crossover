"""Exact two-immediate private E037 repair over frozen e8; in-memory only."""
from hashlib import sha256
import json
from pathlib import Path
import re

import compose_smb2_cheat_owner_1113 as Owner
from compose_metal_head_bridge_1112 import assemble_segments

R=Path(__file__).resolve().parents[2]
W,N=Owner.W,Owner.N
PIN='e8cd1e48bdc48412c30e31b2d0f5decf3a86c49aed85890e8452989e34cc1e17'
CANDIDATE='fa66fa915d91ed125cf947b5c15d517c2919c62941378e10d62b0fdf184cdaae'
OWNER_SOURCE='17d915df6bd6d28e7608d8f644e32294f76cefee38cf3e272994da2422c45fa8'
GRANT=R/'docs/qa/allocations/smb2-cheat-cold-alias-1113.json'
GRANT_SHA='dc416ff5226f9110dededc3ff89ecd1f2bfe7a0d7f4a8f9e525870837f80e1d4'
BRIDGE=0xe02b
CANONICAL=bytes.fromhex('ad1c6f0dfb7ff0128d6a01a9f58d6c01a9bd8d6d01a9cf4c5a018d6a01a9218d6c01a9ad8d6d01a9bf4c5a01ea')
EDITS=((974919,0xde,0xf5),(983111,0xde,0xf5))
TARGET=bytes.fromhex('0848ad0260c918f01fc902d02fadee5fc901d02868288d6a01a9fe8d6c01a9b78d6d01a9df4c5a0168288d6a01a97f8d6c01a9b88d6d01a9d64c5a0168288d6a01a9528d6c01a9a28d6d01a9bf4c5a01')


def bindings(raw):
    assert sha256(raw).hexdigest()==PIN
    assert sha256(Path(Owner.__file__).read_bytes()).hexdigest()==OWNER_SOURCE
    public=Owner.inverse(raw);assert sha256(public).hexdigest()==Owner.PIN
    manifest=GRANT.read_bytes();assert sha256(manifest).hexdigest()==GRANT_SHA
    g=json.loads(manifest)
    assert g['parent_ROM_SHA256']==PIN
    assert [(q['file_half_open'][0],int(q['preimage_hex'],16),int(q['replacement_hex'],16))
            for q in g['spans']]==list(EDITS)
    assert g['canonical_source']['CPU_gate_half_open']==[BRIDGE,BRIDGE+43]
    assert sha256(CANONICAL[:43]).hexdigest()==g['canonical_source']['canonical_gate_SHA256']
    for bank in(119,120,125,127):
        at=16+bank*8192+(BRIDGE&8191);expected=bytearray(CANONICAL)
        if bank in(119,120):expected[0xe037-BRIDGE]=0xde
        assert raw[at:at+45]==expected,(bank,'complete45-byte gate preimage')
    b=dict(W.Symbols.bundle(),raw=raw)
    caller=16+126*8192+0x3a1;target=16+79*8192+0x1df5
    assert raw[caller:caller+3]==bytes.fromhex('202be0')
    assert W.address(b,'GuestGameRoutinesBridge')==BRIDGE
    assert W.address(b,'HuGameColdDispatch')==0xbdf5
    assert raw[target:target+80]==TARGET
    # Assemble the exact retained current owner, rather than calling the
    # obsolete BDDE UI-tail an alternative canonical implementation.
    union=R/'build/karnov-host-resource-base-1101-v1/union.s'
    source=union.read_bytes()
    assert sha256(source).hexdigest()=='fa55d0b6aa95afb111261b6c2634b4054bf0439b59ef14332f7de742f0bcbbe2'
    body=source.decode().replace('\r\n','\n').split('.proc HuGameColdDispatch\n',1)[1].split('.endproc',1)[0]
    targets={}
    def expand(match):
        name=match[1];pc,at=W.address(b,name),W.location(b,name);bank=((at-16)//8192)|128
        targets[name]=dict(pc=pc,rawbank=bank)
        return('\n'.join((' sta SafeA',f' lda #${pc&255:02x}',' sta TargetLo',
            f' lda #${pc>>8:02x}',' sta TargetHi',f' lda #${bank:02x}',' jmp FarCallCommon')))
    body=re.sub(r'^ farcall (\w+),jmp$',expand,body,flags=re.M)
    symbols={n:W.address(b,n)for n in('SelectedCharacter','RdVariant','FarCallCommon')}
    symbols.update(SafeA=0x16a,TargetLo=0x16c,TargetHi=0x16d)
    code,_=assemble_segments('.segment "COLD_SOURCE"\n'+body,dict(COLD_SOURCE=0xbdf5),symbols)
    assert code['COLD_SOURCE']==TARGET
    previous=Owner.D.C
    sample_info=previous.bindings(previous.inverse(public))
    return dict(grant_SHA256=GRANT_SHA,parent_owner_source_SHA256=OWNER_SOURCE,
        canonical_gate43_SHA256=sha256(CANONICAL[:43]).hexdigest(),
        canonical_gate45_SHA256=sha256(CANONICAL).hexdigest(),
        current_target80_SHA256=sha256(TARGET).hexdigest(),
        target_source_path=str(union.relative_to(R)),target_source_SHA256=sha256(source).hexdigest(),
        target_source_assembled_exact=True,target_owner_routes=targets,
        caller=dict(physical_bank=126,pc=0x83a1,return_pc=0x83a4,bytes='202be0'),
        samples=sample_info['samples'],source_RAM_CHR_stack_bytes=0)


def proposal(raw):
    info=bindings(raw);out=bytearray(raw)
    for at,old,new in EDITS:assert raw[at]==old;out[at]=new
    image=bytes(out)
    assert sha256(image).hexdigest()==CANDIDATE and len(image)==len(raw)
    assert {i for i,(a,b)in enumerate(zip(raw,image,strict=True))if a!=b}=={at for at,_,_ in EDITS}
    for bank in(119,120,125,127):
        at=16+bank*8192+(BRIDGE&8191);assert image[at:at+45]==CANONICAL
    for q in info['samples']:
        assert image[q['file']:q['file']+q['bytes']]==raw[q['file']:q['file']+q['bytes']]
    for at,old,new in Owner.SPANS:assert image[at:at+len(new)]==new
    return image,dict(**info,parent_SHA256=PIN,ROM_SHA256=CANDIDATE,changed_operand_bytes=2,
        all_four_complete45byte_gate_windows_equal=True,all_unowned_bytes_exact=True,
        all_sample_payloads_and_previous_owner_fix_exact=True,outputs=0,native_qualified=False)


def inverse(raw):
    assert sha256(raw).hexdigest()==CANDIDATE
    out=bytearray(raw)
    for at,old,new in EDITS:assert raw[at]==new;out[at]=old
    parent=bytes(out)
    assert sha256(parent).hexdigest()==PIN and proposal(parent)[0]==raw
    return parent


reverse=inverse


if __name__=='__main__':
    parent,_=Owner.proposal(Owner.D.C.Owner.NIGHTLY.read_bytes())
    image,q=proposal(parent);assert inverse(image)==parent
    print(json.dumps(q,separators=(',',':')),flush=True)
