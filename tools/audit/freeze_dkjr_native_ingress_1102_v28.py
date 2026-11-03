"""Compact freeze of qualified private DK ingress leaves, not admission."""
import json,zipfile
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
R=A.R;O=A.O


def main():
    receipts=['native-pause-world-v21-CPU.json','native-vector-v22-layout.json','native-vector-v23-CPU.json','native-display-v24-layout.json','native-display-v25-CPU.json','native-powerup-v26-layout.json','native-powerup-v27-CPU.json']
    proofs={n:json.loads((O/n).read_text())for n in receipts};assert all(q['passed']for q in proofs.values())
    sources=[R/'tools/audit'/n for n in ['check_dkjr_pause_world_1102_v21.py','prepare_dkjr_native_vector_1102_v22.py','check_dkjr_native_vector_1102_v23.py','prepare_dkjr_native_display_1102_v24.py','check_dkjr_native_display_1102_v25.py','prepare_dkjr_native_powerup_1102_v26.py','check_dkjr_native_powerup_1102_v27.py','freeze_dkjr_native_ingress_1102_v28.py']]
    generated=receipts+['native-vector-v22.s','native-vector-v22.bin','native-vector-main-v22.bin','native-vector-pause-v22.bin','native-display-v24.s','native-display-v24.bin','native-display-main-v24.bin','native-display-pause-v24.bin','native-display-ports-v24.bin','native-powerup-v26.s','native-powerup-v26.cfg','native-powerup-v26.lbl','native-powerup-v26.bin','native-powerup-main-v26.bin','native-powerup-pause-v26.bin','native-powerup-ports-v26.bin']
    paths=sources+[O/n for n in generated]+[R/'docs/qa/allocations/dkjr-private-resources-1102-v20.json']
    archive=O/'native-ingress-v28-inputs.zip';members=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(set(paths)):
            rel=p.relative_to(R).as_posix();data=p.read_bytes();z.writestr(rel,data);members.append(dict(path=rel,bytes=len(data),SHA256=A.sha(data)))
    assert archive.stat().st_size<256000
    q=proofs['native-powerup-v26-layout.json'];out=dict(passed=True,status='FROZEN_PRIVATE_INGRESS_LEAVES_UNFINISHED_NATIVE_OWNER',ROM_written=False,native_owner_admitted=False,shared_mutation=False,base_current_delivered_SHA256='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15',source_base_SHA256=A.PIN,private_model_Prince_reference=proofs['native-powerup-v27-CPU.json']['historical_Prince_reference'],archive=archive.relative_to(R).as_posix(),archive_bytes=archive.stat().st_size,archive_SHA256=A.sha(archive.read_bytes()),members=members,source_files=[dict(path=p.relative_to(R).as_posix(),SHA256=A.sha(p.read_bytes()))for p in sources],
        assembly=dict(body_bytes=q['body_bytes'],body_end=q['body_end'],header_spare=q['header_spare'],metadata_ports_bytes=q['ports_bytes'],metadata_end=q['metadata_end'],metadata_spare=q['metadata_spare'],actual_vector_entries=38,implemented_rows=q['implemented_vector_rows'],unfinished_rows=q['unimplemented_rows']),
        proven=['Earned native fruit defeat captureepoch1 retains normal native AI; next60D1AE updates pause; terminal61paused, normal62thaws.','Real CannonVar33 both enemy/cannon ingresses, native platform/firebar mechanical pause and genuine DrawAll2/6/6sprites. Earlier frozen ID09 explanatory cannon assumption corrected visibly in v21.','Actual38entry vector/Fresh/Main/Draw, original constructor/15px jump/44airupdates and native motion caches.','Original120contact rectangles, real native typedCHR publication959..961, originalF3A1palettes/nativebackdrop160legal/96busy buffers.','Genuine60 native PlayerChangeSize/NrNativePowerupDispatch/Hu33/GuestPowerupUpdate, nestedGetPlayerColors→own26, source2048B unchanged, completionrearmsTimerbeforeAI, actualHuMovement resumes, foreignretirethaws; minimumforegroundSP156.'],
        remaining=['29 rows remain explicit unfinished CLCRTS; no functional public caller/admission claim for them.','Real IRQ/lagNMI of changed owner and nested powerup; scene/death/contact/head/side/pickup/weapon/bounce full actual routes.','Complete hanging/falling/hit/points art/native OAM, worldfruit/vine/helper placement, palette retry lifetime and exact physical coldpacking/header cookies.','Rebind final Prince successor and exact current Bub/Sunny fingerprints. Current v27 model is historicalv65, matching-cookie CPU fixture, not final authentication/coldcopy.','Separate root grant for all shared/menu/public mutations and actual Mesen/native1-1 qualification.'],
        immutable_prior_checkpoint='docs/qa/checkpoints/2026-11-02/dkjr-admission-proposal-v20',scope='Source/CPU native leaves only. No shared/resource/menu change beyond the previously formal private lease, no ROM file, Mesen, install or Git operation.')
    (O/'native-ingress-v28.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['passed','status','archive_bytes','archive_SHA256','assembly']}))


if __name__=='__main__':main()
