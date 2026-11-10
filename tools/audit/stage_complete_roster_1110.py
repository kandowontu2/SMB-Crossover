"""Compose qualified frozen components into one ROM and one small manifest."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

R=Path(__file__).resolve().parents[2]
BASE=R/'build/remaining-roster-native-1110/candidate.nes'
BASE_PIN='d1333adf3d9e62354ccfab9c21490f95bc972200c513183a309d90eed09728d8'
HELPER=R/'build/manual-roster-platform-1110/final-qualified-proof.json'
HELPER_PIN='659c5ca3650331e90ac7806383a0669a855d3632f3c8b23fc6acedd0560615cb'
HELPER_RESULT='5f072bfdacdf4fc2e5bf81d1a46eb5b3720fecbc8d6b9b4e94766babfad01b70'
MIKE_RESULT='2e93b0f51aada085eb9936c2011fcdc9588ef1abe04d4f2a9ce8dd610a950766'
digest=lambda raw:sha256(raw).hexdigest()
SHA=lambda path:digest(Path(path).read_bytes())


def ref(path):
    path=path.resolve()
    return path.relative_to(R).as_posix() if path.is_relative_to(R) else str(path)


def qualify(path,bindings):
    path=path.resolve();q=json.loads(path.read_text())
    assert q.get('passed') is True,('Unqualified component',str(path))
    assert q.get('CPU_pending') is not True,('CPU pending',str(path))
    assert q.get('interrupt_pending') is not True,('Interrupt pending',str(path))
    assert isinstance(q.get('patches'),list) and q['patches'],('No strict patch rows',str(path))
    declared={}
    for field in ('bindings','source_bindings'):
        for name,expected in q.get(field,{}).items():
            source=Path(name);source=source if source.is_absolute() else R/source
            actual=SHA(source);assert actual==expected,('Changed component binding',str(source),expected,actual)
            key=ref(source);assert key not in declared or declared[key]==actual,key
            declared[key]=actual
    assert declared,('Component has no source bindings',str(path))
    declared[ref(path)]=SHA(path)
    for key,value in declared.items():
        assert key not in bindings or bindings[key]==value,('Conflicting qualified source',key)
        bindings[key]=value
    return q


def apply(raw,rows,component):
    image=bytearray(raw);extents=[]
    for row in rows:
        at=row['file_offset'];old=bytes.fromhex(row['old_hex']);new=bytes.fromhex(row['new_hex'])
        assert isinstance(at,int) and 16<=at and at+len(old)<=len(raw)
        assert old and len(old)==len(new)
        assert raw[at:at+len(old)]==old,(component,'Preimage',at)
        assert all(at>=end or at+len(old)<=start for start,end in extents),(component,'Overlapping rows',at)
        extents.append((at,at+len(old)));image[at:at+len(old)]=new
    return bytes(image)


def main():
    cli=argparse.ArgumentParser();cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--mike-proof',type=Path,required=True);cli.add_argument('--sonic-proof',type=Path,required=True)
    args=cli.parse_args();out=args.output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build'
    assert not out.exists() or not any(out.iterdir()),'Use a new empty scoped output'
    bindings={ref(Path(__file__)):SHA(Path(__file__)),ref(BASE):SHA(BASE)}
    base=BASE.read_bytes();assert digest(base)==BASE_PIN and SHA(HELPER)==HELPER_PIN
    helper=qualify(HELPER,bindings);mike=qualify(args.mike_proof,bindings);sonic=qualify(args.sonic_proof,bindings)
    assert helper['parent_SHA256']==mike['parent_SHA256']==BASE_PIN
    assert helper.get('source_ready') is True and helper.get('interrupt_pending') is False
    assert helper['expected_memory_only_SHA256']==HELPER_RESULT
    assert mike.get('CPU_pending') is False and mike['expected_memory_only_SHA256']==MIKE_RESULT
    helper_image=apply(base,helper['patches'],'helpers')
    mike_image=apply(base,mike['patches'],'MikeV3')
    assert digest(helper_image)==HELPER_RESULT and digest(mike_image)==MIKE_RESULT
    assert sonic['parent_SHA256']==MIKE_RESULT,('Sonic must be rebased onto qualified MikeV3',sonic['parent_SHA256'])
    assert sonic.get('interrupt_pending') is False,'Sonic final vector qualification required'
    sonic_image=apply(mike_image,sonic['patches'],'Sonic')
    assert digest(sonic_image)==sonic['expected_memory_only_SHA256']
    assert len(helper['patches'])==8 and len(sonic['patches'])==17
    # This final composition grants no overlapping ownership. If a future
    # component shares identical bytes, its producers must publish an explicit
    # co-owned merge receipt before this strict composer can accept that case.
    rows=[];claims=[]
    for name,q in (('helpers',helper),('MikeV3',mike),('Sonic',sonic)):
        for row in q['patches']:
            at=row['file_offset'];end=at+len(bytes.fromhex(row['old_hex']))
            assert all(at>=stop or end<=start for start,stop,owner in claims),('Cross-component overlap',name,at,claims)
            assert base[at:end]==bytes.fromhex(row['old_hex']),(name,'Not a disjoint d133 preimage',at)
            rows.append(dict(row,component=name));claims.append((at,end,name))
    rows.sort(key=lambda row:row['file_offset'])
    final=apply(base,rows,'CompleteRoster');expected=digest(final)
    assert apply(sonic_image,helper['patches'],'helpers last')==final
    assert apply(apply(helper_image,mike['patches'],'Mike after helpers'),sonic['patches'],'Sonic last')==final
    native_plan=[f'ff-22-{v}' for v in range(4)]+[f'wwf-29-{v}' for v in range(6)]+[
        'mini-full-1-1-zero-lag','getsu-real-powerup','prince-opening','dkjr-opening','jay-opening','steve-opening','sonic-opening']
    assert len(native_plan)==17
    prototype_replay=R/'tools/playthroughs/native_skin_opening_1110.lua'
    bindings[ref(prototype_replay)]=SHA(prototype_replay)
    manifest=dict(prepared=True,passed=True,source_ready=True,source_CPU_only=True,
        Mesen_run=False,native_pending=True,ROM_written=True,
        parent_SHA256=BASE_PIN,expected_memory_only_SHA256=expected,ROM_SHA256=expected,
        ROM=ref(out/'candidate.nes'),strict_disjoint=True,identical_overlap_exceptions=[],
        patches=rows,components={name:dict(proof=ref(path),proof_SHA256=SHA(path),
            parent_SHA256=q['parent_SHA256'],expected_memory_only_SHA256=q['expected_memory_only_SHA256'],
            patch_rows=len(q['patches']),native_pending=q.get('native_pending',True),
            interrupt_pending=q.get('interrupt_pending','not declared in CPU proof'))
            for name,path,q in (('helpers',HELPER,helper),('MikeV3',args.mike_proof,mike),('Sonic',args.sonic_proof,sonic))},
        reconstruction=dict(helpers_alone=HELPER_RESULT,MikeV3_alone=MIKE_RESULT,
            MikeV3_then_Sonic=digest(sonic_image),all_component_orders_exact=True),
        native_packet_plan=dict(count=17,cases=native_plan,staging_owner='root',
            staged=False,ROM_copies_per_packet=0,all_packets_must_reference_this_single_ROM=True,
            prototype_replay=ref(prototype_replay)),
        scope='Frozen source composition only. Helper V/H/carry and mask vector proofs, qualified MikeV3 CPU proof and final Sonic vector proof remain bound. No native final-composition, stage-clear or delivery claim; root must run all17 final-hash packets, including zero-lag Mini.',
        bindings=dict(sorted(bindings.items())))
    serialized=json.dumps(manifest,indent=2,ensure_ascii=True)+'\n'
    out.mkdir(exist_ok=True);rom=out/'candidate.nes';proof=out/'combined-proof.json'
    rom.write_bytes(final);proof.write_text(serialized)
    assert SHA(rom)==expected
    print(json.dumps(dict(source_READY=True,ROM=ref(rom),ROM_SHA256=expected,
        proof=ref(proof),proof_SHA256=SHA(proof),rows=len(rows),files=2,native_pending=True)))


if __name__=='__main__':main()
