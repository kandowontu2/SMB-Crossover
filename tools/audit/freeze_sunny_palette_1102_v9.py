"""Retain the exact small Sunny delta/source/native proof, with no ROM copies."""
import hashlib,json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/sunny-checkpoint-1102-v9'
D=R/'docs/qa/checkpoints/2026-11-02/sunny-palette-v9'

def main():
    delivery=R/'build/sunny-delivery-1102-v9';receipt=json.loads((delivery/'published-receipt.json').read_text())
    assert receipt['downloads_launch_verified'] and receipt['IPS_roundtrip']
    base=(R/'build/menu-family-root-candidate-1102-v1/mr-gimmick-family.nes').read_bytes();raw=bytearray(base);patches=[]
    paths={Path(__file__),R/'docs/qa/sunny-palette-deadline-1102.md',delivery/'published-receipt.json'}
    for folder in ['sunny-palette-dedup-1102-v5','sunny-growth-prelude-1102-v9']:
        p=R/'build'/folder;manifest=p/'candidate.json';q=json.loads(manifest.read_text());paths.add(manifest)
        for row in q['patches']:
            at=row['offset'];old=bytes.fromhex(row['old']);new=bytes.fromhex(row['new']);assert raw[at:at+len(old)]==old
            raw[at:at+len(new)]=new;patches.append(row)
        paths.update(x for x in p.iterdir()if x.is_file()and x.suffix in ['.s','.py','.bin'])
    assert hashlib.sha256(raw).hexdigest()==receipt['ROM_sha256']
    for directory in [R/'build/sunny-growth-native-1102-v9/native',delivery/'downloads-smoke',R/'build/sunny-queue-profile-1102-v4/native']:
        paths.update(x for x in directory.rglob('*')if x.is_file()and x.suffix in {'.json','.lua','.py','.csv','.log','.png'})
    paths.add(R/'build/sunny-palette-qualification-1102-v6/CPU.json')
    for name in ['prepare_sunny_current_full11_1102_v1','prepare_sunny_deadline_1102_v2','prepare_sunny_nmi_profile_1102_v3','prepare_sunny_queue_profile_1102_v4','prepare_sunny_palette_dedup_1102_v5','check_sunny_palette_dedup_1102_v6','prepare_sunny_candidate_profile_1102_v7','prepare_sunny_face_gate_1102_v8','prepare_sunny_growth_prelude_1102_v9','deliver_sunny_palette_1102_v9','publish_sunny_palette_1102_v9']:
        paths.add(R/'tools/audit'/(name+'.py'))
    assert len(paths)<100 and sum(p.stat().st_size for p in paths)<4_000_000
    assert not D.exists();D.mkdir(parents=True);O.mkdir(exist_ok=True)
    archive=D/'inputs.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(paths):z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        for p in paths:assert z.read(p.relative_to(R).as_posix())==p.read_bytes()
    q=dict(passed=True,installed=True,base_ROM_SHA256=hashlib.sha256(base).hexdigest(),ROM_sha256=receipt['ROM_sha256'],IPS_SHA256=receipt['IPS_SHA256'],patches=patches,exact_delta_reconstruction=True,archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,files={p.relative_to(R).as_posix():sha(p)for p in paths})
    (D/'receipt.json').write_text(json.dumps(q,indent=2)+'\n');(O/'receipt.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in ['passed','ROM_sha256','archive_bytes']}))
if __name__=='__main__':main()
