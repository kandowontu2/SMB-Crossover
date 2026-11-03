"""Freeze only the compact current Prince source/CPU handoff; no archive/ROM."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit')]
import prepare_prince_pose_reservation_1103_v185 as M
import build_storage_guard_v1 as G
O=M.O


def main():
    G.preflight(private_root=O,reserved_bytes=20000,reserved_files=1,fresh=True)
    base,q=M.image()
    proofs=[]
    for name in ['pose-CPU-v187.json','pose-ISR-v188.json']:
        path=O/name;proof=json.loads(path.read_text())
        assert proof['passed'] and proof['memory_SHA256']==q['expected_memory_only_SHA256']
        for name,digest in proof['bindings'].items():assert M.sha(R/name)==digest,name
        proofs.append(path)
    sources=[R/'tools/audit'/name for name in [
        'prepare_prince_pose_reservation_1103_v185.py',
        'check_prince_pose_reservation_1103_v186.py',
        'check_prince_pose_reservation_1103_v187.py',
        'check_prince_pose_isr_1103_v188.py',
        'freeze_prince_pose_source_1103_v189.py']]
    inputs=[p for p in O.iterdir() if p.is_file()]
    assert not any(p.suffix.lower() in ['.nes','.dbg','.png','.o'] for p in inputs)
    manifest=json.loads((O/'pose-manifest.json').read_text())
    count=sum(p.stat().st_size for p in inputs)
    receipt=dict(passed=True,status='SOURCE_CPU_QUALIFIED_ROOT_PRIVATE_NATIVE_PENDING',
        ROM_written=False,emulator_run=False,installed=False,
        parent_ROM=manifest['parent_ROM'],parent_SHA256=manifest['parent_SHA256'],
        memory_SHA256=manifest['expected_memory_only_SHA256'],Prince_cookie=manifest['Prince_cookie'],
        cookie_CPU=manifest['cookie_CPU'],manifest='pose-manifest.json',
        runtime='pose-runtime.bin',metadata='pose-metadata.bin',pool='pose-pool.bin',
        source_bytes_unchanged=8159,metadata_bytes_unchanged=6092,state_bytes_unchanged=1607,
        physical_carriers_unchanged=44,physical_spare=manifest['physical_spare'],
        current_Mini_5077B_all_carriers_cookie_exact=True,
        source_count='Original compact packet header low4bits times4;408poses,3..13parts,12..52bytes.',
        native_header='Stable unbanked SmPose6B05; SmPosePtr6B06/07 points6B05. ObjectMetasprite0 independently prevents legacy native CHR0 selection.',
        source_funding='Renderer STA SmPose adds3B, unused native inputA initializer store removes3B. Existing545B renderer/public entry addresses and current31B PhysicalHi-funded owner helper retained. All5owner manager/selector/transport/13headerchecks and retired-entryimports unchanged.',
        qualification='Actualca90 fullPrincecold completeimages/both16Bheaders,408pose/2578part/82496finalpatternbytes differentials, actualfirst8GameLoop20B nativeheader/bodypreservation,32headerpoisons; bounded changed-private IRQ/actualFF/deepestnested per188.',
        reuse='Foreign/current5owner/cold/retire/fullIRQ proofs reused by exact shared+foreign byte equality; no broad matrix repeated. Typed13part scenario is an explicit CPU originalpose input, not an earned native state.',
        retained_negative='186 regenerated earlier palette1 instead of inherited42+ nativepalette0; firstattr0202=1 rather0. Both negative receipts retained, corrected187 asserts originalparity unchanged.',
        remaining='Root exactprivatecomposition/native body+turn/controls/jump/landing; original firstpipeUp climb and full1-1; earned sword/native battle; original music/SFX mapping. No helper added/justified and no public playable claim.',
        source_files=[p.relative_to(R).as_posix() for p in sources],
        generated_files=len(inputs)+1,generated_bytes_before_this_receipt=count,
        bindings={p.relative_to(R).as_posix():M.sha(p) for p in sources+inputs})
    (O/'source-stage.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ['bindings','source_files']}))


if __name__=='__main__':main()
