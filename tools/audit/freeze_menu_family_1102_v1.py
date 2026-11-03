"""Small reproducible menu patch/source/native checkpoint; no ROM copies."""
import json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/menu-family-checkpoint-1102-v1'
D=R/'docs/qa/checkpoints/2026-11-02/menu-family-v1'
def main():
    p=R/'build/menu-family-root-candidate-1102-v1';d=R/'build/menu-family-delivery-1102-v1'
    receipt=json.loads((d/'published-receipt.json').read_text());proof=json.loads((p/'mr-gimmick-family-v18.json').read_text())
    assert receipt['downloads_launch_verified']and proof['ROM_sha256']==receipt['ROM_sha256']
    base=(R/'build/thomas-current-candidate-1102-v3/candidate.nes').read_bytes();raw=bytearray(base)
    for patch in proof['patches']:
        at=patch['offset'];old=bytes.fromhex(patch['old']);new=bytes.fromhex(patch['new'])
        assert raw[at:at+len(old)]==old;raw[at:at+len(new)]=new
    assert bytes(raw)==(p/'mr-gimmick-family.nes').read_bytes()
    paths={p/'producer-snapshot.py',p/'mr-gimmick-family-v18.json',d/'published-receipt.json',Path(__file__)}
    paths.update(p.glob('family-v18-*.s'))
    for directory in [p/'native-browse',p/'native-bub',p/'native-bob',p/'native-mr-gimmick',d/'downloads-smoke']:
        paths.update(x for x in directory.rglob('*')if x.is_file()and x.suffix in {'.json','.lua','.py','.png','.csv','.log'})
    for name in ['build_menu_family_root_candidate_1102_v1','prepare_menu_family_native_1102_v1','deliver_menu_family_1102_v1','publish_menu_family_1102_v1','audit_current_menu_indicators_1102_v1','prepare_playable_marker_cleanup_1102_v1','prepare_battletoads_silhouette_1102_v1']:
        paths.add(R/'tools/audit'/(name+'.py'))
    assert len(paths)<100 and sum(x.stat().st_size for x in paths)<4_000_000
    assert not D.exists();D.mkdir(parents=True);O.mkdir(exist_ok=True)
    archive=D/'inputs.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for x in sorted(paths):z.write(x,x.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        for x in paths:assert z.read(x.relative_to(R).as_posix())==x.read_bytes()
    q=dict(passed=True,ROM_sha256=receipt['ROM_sha256'],IPS_SHA256=receipt['IPS_SHA256'],exact_delta_reconstruction=True,archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,files={x.relative_to(R).as_posix():sha(x)for x in paths})
    (D/'receipt.json').write_text(json.dumps(q,indent=2)+'\n');(O/'receipt.json').write_text(json.dumps(q,indent=2)+'\n');print(q['archive_bytes'])
if __name__=='__main__':main()
