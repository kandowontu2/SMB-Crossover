"""Finite shared import/consumer closure and compact completed-source freeze."""
from pathlib import Path
import hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_mini_live_shared_isr_1103_v25 as V
O=V.O;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    # Reconstruct finalhost30 only in memory. Exact fixed candidate inputs
    # v24/v28 are never regenerated or overwritten by this freezer.
    q=json.loads((O/'final-payload-v28.json').read_text());raw=bytearray(V.S.F.P.M.BASE.read_bytes());checked=0
    receipts=['owner-fit-v15.json','carrier-audit-v16.json','existing-owner-CPU-v17.json','publication-CPU-v18.json',
        'five-cold-CPU-v22.json','shared-ISR-v23.json','final-payload-v24.json','live-shared-ISR-v25.json','live-shared-nested-v26.json','final-payload-v28.json']
    for name in receipts:
        proof=json.loads((O/name).read_text());assert proof['passed'],name
        for name,digest in proof.get('bindings',{}).items():assert sha(R/name)==digest,name;checked+=1
    for row in q['patches']:
        at=row['file_offset'];old=bytes.fromhex(row['old_hex']);new=bytes.fromhex(row['new_hex']);assert raw[at:at+len(old)]==old
        raw[at:at+len(new)]=new
    assert hashlib.sha256(raw).hexdigest()==q['memory_SHA256']
    old=json.loads((V.S.F.P.M.P/'combined-auth-v83-measurement.json').read_text())['labels']
    new=json.loads((O/'owner-fit-v15.json').read_text())['labels']
    parent=V.S.F.P.M.BASE.read_bytes();origin=16+65*8192;bank=parent[origin:origin+8192]
    owner_spans=[(0x740,0x7f0),(0x800,0x849),(0xb72,0xbd4),(0xe00,0x1013)]
    outside=[]
    for name,value in old.items():
        if name not in new or new[name]==value:continue
        for i in range(8191):
            if bank[i:i+2]!=value.to_bytes(2,'little')or any(a<=i<z for a,z in owner_spans):continue
            assert name=='CoRetire'and i in [0x1027,0x1101],(name,hex(0xa000+i))
            assert raw[origin+i:origin+i+2]==new[name].to_bytes(2,'little')
            outside.append(dict(symbol=name,old=value,new=new[name],operand_CPU=0xa000+i))
    assert len(outside)==2
    # Every fixed-bank193 standard FarCall target remains a declared public
    # entry. Two local native retire imports above are source-rebound.
    standard=[];prg=parent[16:1048592];moved={value for name,value in old.items()if name in new and new[name]!=value}
    for opcode in [32,76]:
        needle=bytes([169,193,opcode,90,1]);pos=0
        while(pos:=prg.find(needle,pos))>=0:
            prefix=prg[pos-10:pos]
            assert prefix[:1]==b'\xa9'and prefix[2:6]==bytes.fromhex('8d6c01a9')and prefix[7:]==bytes.fromhex('8d6d01')
            target=prefix[1]+256*prefix[6];assert target not in moved
            at=16+pos-10;assert raw[at:16+pos+5]==parent[at:16+pos+5]
            standard.append(dict(offset=at,target=target));pos+=1
    assert len(standard)==11
    # The first instructions prove incomingA dead at the cold/publisher
    # targets. Retire paths are separately source-bound below.
    assert raw[16+123*8192+0xf40:16+123*8192+0xf40+2]==bytes.fromhex('a902')
    assert raw[16+62*8192+0x3d:16+62*8192+0x3d+3]==bytes.fromhex('adee73')
    assert (R/'build/prince-actor-1101-v1/cold-worker-v158.bin').read_bytes()[:2]==bytes.fromhex('0868')
    assert (O/'cold-v19.bin').read_bytes()[:2]==bytes.fromhex('a900')
    source=(O/'owner-final-v28.s').read_text();mapper=(O/'common-v15.s').read_text();selector=(O/'selector-v15.s').read_text()
    assert source.count('cmp #5\n bcs CoSelectNo')==2 and 'CoRetireOwners:\n ldx #4'in source
    assert 'ldx #5\n jsr CoCheckIndex'in source and 'cmp #36\n bne CoNativeNo'in source
    assert 'cmp #5\n bcc PrOdd'in selector
    assert 'lda $2007\n rts\nBbColdMapEnd:'in mapper
    assert 'MiniDescriptor:\n .byte 1,0,9,$d0\n .word 967'in mapper
    boundary=dict(passed=True,parent_SHA256=V.S.F.P.M.PIN,memory_SHA256=q['memory_SHA256'],
        source_bound_external_imports=outside,unchanged_constant_bank193_FarCalls=standard,
        finite_indices='Cookieindices0..4 only for Selected37..41; exactSelected36 supplies5. Descriptors/retireindices0..4 only. Selected>=42/legacy rejects beforelookup. Retireloop4..0 then genuineShRetire.',
        dead_A_contracts=[
            'CommonAF40 beginsLDA#2; incomingA is overwritten before anyA consumer.',
            'Prince coldD25E beginsPHP/PLA; DK/Mini beginLDA#0. Constructor inputs are not passed inA.',
            'Physical62:A03D X5PublishChr beginsLDA X5WideChrActive. Cold caller overwrites its returnedA before use.',
            'PrinceRetire beginsLDA#0. BBRetire LDX0→JSRProxyRestore→JSRValidate→CPX6/STX→TXA overwritesA before a semantic read. DKRetire saves inputA solely for its own AXYP restore, thenTXA/LDAoverwrite; caller immediately entersCoInvalidate which LDA0overwrites the restoredA. OuterpublicAXYP/fiveSMC are restored exactly, as17/22/28 prove.'
        ],
        cold_mapper_upper='Removing post-pair STY5130 changes only transient upperlatch underforcedblank/SEI/invalidheaders. Currentphysical5123 pair is alreadylatched. Each nextMap sets its ownupper before5123, andresidentCoPublishChr restoresall12hardwarelatches beforecookiecommit. Actual23 replaysIRQ/genuineI1FF at reached map/copy/FarCall cuts; oldnativehandler parity protects the held upperlatch.',
        cold_only_execution='MiniD25E..D2CF is inside its one immutable967 row. Only guardedtypedcold38/40/41 canenterD25E, with correctC2 ownerlayout, invalidheaders/forcedblank/SEI. Raw41 commonclearsC000..C8FF, copies/verifies967 then113Bboot copies/verifies962..966 beforepublishingbothheaders. No publicMini vector targetsD25E. Warmvalidheaders skipworker. Sourceinit belongsfirstactualnative8, nevercoldpreentrance.',
        current_shared_invariants='All13 fulltwo16Bheader checks retained; no authcache, partialsignature or borrowedglobalRAM. CurrentPrince44/Bub9/DK11 payloads andallotherbytesoutsideexactrecipe remainparent. Mini sourceMotion/nativeWorld/render/scene/frontend are separatelyroot-owned.',
        helpers='No native helperplatform added by this transport/resource work.',
        bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),O/'final-payload-v28.json',O/'owner-final-v28.s',O/'common-v15.s',O/'selector-v15.s',R/'src/mmc5_expanded.s',R/'tools/reference/bubble_bobble_native_leaves_1101_v3.inc',R/'build/prince-actor-1101-v1/native-services-v157.s',R/'tools/audit/check_dkjr_native_pause_1102_v16.py',R/'build/prince-actor-1101-v1/cold-worker-v158.bin']})
    (O/'source-boundaries-v27.json').write_text(json.dumps(boundary,indent=2)+'\n')
    sources=[R/'tools/audit'/name for name in [
        'measure_mini_private_owner_1103_v15.py','audit_mini_carriers_1103_v16.py','check_mini_existing_owners_1103_v17.py',
        'check_mini_carrier_publication_1103_v18.py','prepare_mini_owner_payload_1103_v19.py','check_mini_five_cold_1103_v20.py',
        'check_mini_shared_isr_1103_v21.py','check_mini_current_cold_1103_v22.py','check_mini_current_isr_1103_v23.py',
        'qualify_mini_final_cold_1103_v24.py','check_mini_live_shared_isr_1103_v25.py','check_mini_live_shared_nested_1103_v26.py',
        'rebind_mini_final_payload_1103_v28.py',Path(__file__).name]]
    generated=[p for p in O.iterdir()if p.is_file()and p.suffix in ['.s','.cfg','.lbl','.bin','.json']and p.name!='source-stage.json']
    files=sources+sorted(generated)
    archive=O/'mini-shared-source-v27.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in files:z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        for p in files:assert hashlib.sha256(z.read(p.relative_to(R).as_posix())).hexdigest()==sha(p)
    stage=dict(passed=True,status='SHARED_SOURCE_QUALIFIED_ROOT_NATIVE_PENDING',ROM_written=False,emulator_run=False,
        parent_SHA256=V.S.F.P.M.PIN,memory_SHA256=q['memory_SHA256'],Mini_cookie=q['Mini_cookie'],kernel_SHA256=q['kernel_SHA256'],
        final_manifest='final-payload-v28.json',current_source='owner-final-v28.s',resource_grant='docs/qa/allocations/mini-mario-private-resources-1103-v24.json',
        archive=archive.relative_to(R).as_posix(),archive_bytes=archive.stat().st_size,archive_SHA256=sha(archive),members=len(files),direct_positive_receipt_bindings_checked=checked,
        qualification='Fiveactualcold/25transitions/160poisons; finalhost30cold plus8to/from transitions/32ownpoisons/8faults;23cold2919IRQ4770FF,min161;25active840IRQ840FF,min176;26deepestnested5463IRQ/26FFcontexts,min171. Fullarchitectural/private/native/SMC/maps/PPU/audio preservation per exactscopes.',
        reuse='23/25/26 retain exactearlierpayload hashes; finalhost30 changes onlyMini private kernel andpayloadcookie, leaving allsharedcode/113Bcopier/metadata/art exact. Perroot no largeISR rerun. Root separately owns nativeHost/scene/menu/gates andnightlyadmission.',
        negative='v20 retained overstrict emulatorB-bit fixturefailure. v21 wasstopped beforefinalv26pin and isnot acompletedproof. Bothsources preserved; no negativeROM/gameplaysuccess claimed.',
        source_files=[p.relative_to(R).as_posix()for p in sources],bindings={p.relative_to(R).as_posix():sha(p)for p in files})
    (O/'source-stage.json').write_text(json.dumps(stage,indent=2)+'\n')
    print(json.dumps({k:v for k,v in stage.items()if k not in ['bindings','source_files']}))


if __name__=='__main__':main()
