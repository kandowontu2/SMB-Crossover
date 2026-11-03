"""Freeze powered trajectory/native negative and an unexecuted receiver-only correction."""
import json,zipfile
from pathlib import Path
import prepare_bub_adaptive_flower_1103_v97 as P
from prepare_selected_native_packet_v1 import R,sha


def corrected_helper():
    """Wait for actual support; retain the support assertion before requesting A."""
    before='if kind==2 and dx>=30 and dx<=36 and dy<=-16 and dy>=-20 then'
    after='if kind==2 and dx>=30 and dx<=36 and dy<=-16 and dy>=-20 and full_normal_jump_ready(actor)then'
    assert P.HELPER.count(before)==1
    return P.HELPER.replace(before,after)


def main():
    O=P.P.O;capture=O/'bub-flower/capture';error=json.loads((capture/'callback-error.json').read_text())
    assert 'Powered takeoff requires actual native foot/zeroDY support'in error['error']
    assert error['source_failures']==0
    sources=[R/'tools/audit'/name for name in[
        'check_bub_powered_bubble_1103_v92.py','check_bub_powered_bubble_1103_v93.py',
        'check_bub_powered_bubble_1103_v94.py','check_bub_powered_terrain_1103_v95.py',
        'check_bub_powered_terrain_1103_v96.py','prepare_bub_adaptive_flower_1103_v97.py',
        'check_bub_adaptive_controller_1103_v98.py','freeze_bub_powered_trajectory_1103_v99.py']]
    files=sources+[p for p in O.rglob('*')if p.is_file()and p.suffix not in['.zip']and p.name not in['powered-trajectory-freeze-v99.json','commit-files-v99.txt']]
    assert len(files)==len(set(files))
    archive=O/'powered-trajectory-freeze-v99.zip';assert not archive.exists()
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in files:z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        for p in files:assert z.read(p.relative_to(R).as_posix())==p.read_bytes()
    corrected_helper()
    receipt=dict(frozen=True,native_passed=False,ROM_SHA256=P.P.PIN,
        native_negative=error,source_hardware_failures=0,
        first_failure='Controller asserted rather than waiting when observed bubble gap/height matched during nativeState2. CSV shows stationaryX678/Y176/source0 and state0/2 alternating; this does not establish a game physics defect.',
        source_only_receiver_correction='corrected_helper() adds unchanged full_normal_jump_ready(actor) to the takeoff condition; the assertion remains before A. It waits instead of claiming a transient unsupported state is a failure. Not emitted/run/qualified; no weakening of genuine foot/zeroDY/freshA assertions.',
        CPU_scope='All8 measured original source trajectories earned support1/79px rise; the old80px assertion stays negative. Both IDs cross32/48px native columns in95 and64px in96. Lua98 exactly matches568 input decisions. These are initialized CPU arenas, not an earned flower claim.',
        archive=archive.relative_to(R).as_posix(),archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,
        members={p.relative_to(R).as_posix():sha(p)for p in files},
        capture_files_safe_for_root_cleanup_after_exact_ZIP_compare=[dict(path=p.relative_to(R).as_posix(),SHA256=sha(p),bytes=p.stat().st_size)for p in capture.rglob('*')if p.is_file()],
        source_commit_files=[p.relative_to(R).as_posix()for p in sources])
    (O/'powered-trajectory-freeze-v99.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (O/'commit-files-v99.txt').write_text('\n'.join(receipt['source_commit_files'])+'\n')
    print(json.dumps(dict(frozen=True,native_passed=False,archive=str(archive),SHA256=sha(archive),bytes=archive.stat().st_size,members=len(files))))


if __name__=='__main__':main()
