"""Freeze the finite00fb source-only body experiment, preserving negatives."""
from pathlib import Path
import argparse,ast,hashlib,json,shutil,sys,zipfile
from check_tmnt_audio_fallback_oc import qualified

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT=D/'mm-proto-clean-menu-candidates-v1/clean-menu-irq'
CANDIDATE=D/'mm-proto-body-priority-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    assert not a.output.resolve().is_relative_to(R);a.output.mkdir(parents=True,exist_ok=False)
    assert sha(PARENT/'candidate.nes')=='731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'
    assert sha(CANDIDATE/'candidate.nes')=='00fb4a72ec9788f7b2878d6201f70a96ae6e47b4935ba186648c7edc04806a62'
    old=json.loads((PARENT/'source-manifest.json').read_text());new=json.loads((CANDIDATE/'source-manifest.json').read_text())
    assert old.keys()==new.keys()
    for root,manifest in [(PARENT,old),(CANDIDATE,new)]:
        for rel,h in manifest.items():assert sha(root/'source'/rel)==h,rel
    changed={rel:dict(parent=old[rel],candidate=new[rel])for rel in old if old[rel]!=new[rel]}
    assert set(changed)=={'src/metasprite_engine.s','src/megaman_weapons.s','smb1base-mmc5-expanded.cfg'}
    put(a.output/'source-inputs.json',new);put(a.output/'production-delta.json',changed)
    shutil.copyfile(CANDIDATE/'source.patch',a.output/'source-review.patch')
    zipname=a.output/'source.zip'
    with zipfile.ZipFile(zipname,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for rel in sorted(new):z.write(CANDIDATE/'source'/rel,rel)
    with zipfile.ZipFile(zipname)as z:
        assert z.testzip()is None and set(z.namelist())==set(new)
        assert all(hashlib.sha256(z.read(rel)).hexdigest()==h for rel,h in new.items())
    qb,qa=[qualified(root/'candidate.nes')for root in [PARENT,CANDIDATE]]
    moved={n:(v,qa.get(n))for n,v in qb.items()if qa.get(n)!=v}
    expected={('WorldFirebarAdmission',),('WorldFirebarDrawAdmission',),('RosterOamReady',),('DrawAllMetasprites','RosterPriorityInRange'),('DrawAllMetasprites','LegacyTailClear'),('DrawAllMetasprites','PlayerBankReady'),('DrawAllMetasprites','DoneDrawingPlayer'),('DrawAllMetasprites','ClearPlayerOAM'),('RosterProjectileOamReady',),('MegaManProjectileOamReady',),('DrawAllMetasprites','RosterShots'),('DrawAllMetasprites','ClearReservedPlayer'),('DrawAllMetasprites','RotateGuestOAM'),('_FARCALL_COUNT',)}
    assert set(moved)==expected and all(v[1]is not None for v in moved.values())
    assert qa[('WorldFirebarAdmissionDone',)]==qb[('WorldFirebarAdmissionDone',)]
    assert qa[('_FARCALL_COUNT',)]==qb[('_FARCALL_COUNT',)]+1
    put(a.output/'genuine-symbol-movement.json',[dict(name=list(n),old=v[0],new=v[1])for n,v in moved.items()])
    proof_names=['proof.json','cpu-probe-v1/proof.json','partition-v6/proof.json','callers-v3/proof.json','ownership-v1/proof.json','records-v1/proof.json']
    proofs={}
    (a.output/'proofs').mkdir()
    for name in proof_names:
        q=CANDIDATE/name;data=json.loads(q.read_text());assert data['passed']is True and data.get('native_run')is False
        assert data.get('ROM_sha256',data.get('candidate_ROM_sha256'))=='00fb4a72ec9788f7b2878d6201f70a96ae6e47b4935ba186648c7edc04806a62'
        dest=a.output/'proofs'/name.replace('/','--');shutil.copyfile(q,dest);proofs[name]=dict(path=str(q),sha256=sha(q))
    put(a.output/'qualification.json',dict(passed=True,source_only=True,native_run=False,installed=False,ROM_sha256=sha(CANDIDATE/'candidate.nes'),proofs=proofs,complete_unmodified_parent_AXYP_SP_retained=True,only_persistent_owned_RAM_delta=['GuestOamRotationActive:1->128','RgOamRotation:originalPhase->0'],foreign_cost=[-23,0],active_owned_cost=[159,160],native_visibility_cadence_and_starvation_acceptance=False,errata=['Build-layout proof retains pre-correction mode2 prose; final assembled owner is80hex, validated by all final CPU receipts.','Caller-v3 prose inherits former liveness wording; its direct assertion now requires the unmodified draw return itself to match.','13 genuine address movements plus one compile-time farcall-count increment, not13 additional movements beyond world-entry.']))
    own=sorted((R/'tools/audit').glob('mm_proto_body_priority_*.py'))
    assert Path(__file__)in own
    (a.output/'tools').mkdir();deps=set(own);pending=own[:]
    while pending:
        q=pending.pop();tree=ast.parse(q.read_text())
        for node in ast.walk(tree):
            names=[node.module]if isinstance(node,ast.ImportFrom)else[n.name for n in node.names]if isinstance(node,ast.Import)else[]
            for name in names:
                if not name:continue
                possible=R/'tools/audit'/(name.split('.')[0]+'.py')
                if possible.exists()and possible not in deps:deps.add(possible);pending.append(possible)
    for q in own:shutil.copyfile(q,a.output/'tools'/q.name)
    import py65
    import py65.devices.mpu6502
    import py65.utils.conversions
    for module in [py65,py65.devices.mpu6502,py65.utils.conversions]:deps.add(Path(module.__file__))
    deps|={Path(sys.executable),R/'tools/Windows/cc65/bin/cl65.exe',R/'tools/Windows/cc65/bin/ca65.exe',R/'tools/Windows/cc65/bin/ld65.exe'}
    deps|={PARENT/('candidate'+ext)for ext in ['.nes','.dbg','.lbl','.map']}
    deps|={CANDIDATE/('candidate'+ext)for ext in ['.nes','.dbg','.lbl','.map']}
    deps|={PARENT/'source-manifest.json',CANDIDATE/'source-manifest.json',CANDIDATE/'source.patch'}
    deps|={CANDIDATE/name for name in proof_names}
    negative_paths=[D/'mm-proto-body-priority-v1/failure.json',D/'mm-proto-body-priority-v2/partition-v1/failure.json',D/'mm-proto-body-priority-v2/partition-v2/failure.json',D/'mm-proto-body-priority-v2/partition-v3/failure.json',D/'mm-proto-body-priority-v2/callers-v1/failure.json',D/'mm-proto-body-priority-v2/callers-v2/failure.json']
    deps|=set(negative_paths)
    report=R/'docs/qa/mm-proto-body-priority-2026-10-26.txt';deps.add(report);shutil.copyfile(report,a.output/'report.txt')
    put(a.output/'dependency-bindings.json',{str(q.resolve()):sha(q)for q in sorted(deps)})
    catalog={str(q.relative_to(a.output)).replace('\\','/'):dict(bytes=q.stat().st_size,sha256=sha(q))for q in sorted(a.output.rglob('*'))if q.is_file()}
    put(a.output/'catalog.json',catalog)
    receipt=dict(passed=True,source_only=True,native_run=False,installed=False,ROM_sha256=sha(CANDIDATE/'candidate.nes'),parent_ROM_sha256=sha(PARENT/'candidate.nes'),source_members=len(new),source_zip_sha256=sha(zipname),source_zip_CRC_and_all_member_hashes_verified=True,changed_source=changed,retained_qualified_symbols=len(qb)-len(moved),genuine_moved_addresses=13,compile_time_count_increment=1,proof_count=len(proofs),owned_tools=len(own),dependency_bindings=len(deps),catalog_files=len(catalog),catalog_sha256=sha(a.output/'catalog.json'),qualification_sha256=sha(a.output/'qualification.json'),dependency_bindings_sha256=sha(a.output/'dependency-bindings.json'),limits='Reviewable source/CPU candidate only. Body/shot/world visibility tradeoff and +159..160owned cost remain native unqualified. No emulator, production, settings or Git action.')
    put(a.output/'receipt.json',receipt)
    print(json.dumps(dict(receipt=str(a.output/'receipt.json'),receipt_sha256=sha(a.output/'receipt.json'),**receipt),indent=2))


if __name__=='__main__':main()
