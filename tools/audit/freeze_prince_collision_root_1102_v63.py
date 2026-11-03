"""Retain the exact reviewed Prince source packets without expansion."""
import hashlib,json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/prince-collision-root-freeze-1102-v63'

def main():
    source=R/'build/prince-actor-1101-v1';saved=[]
    for version,kind,digest in [(47,'battle','0fa522b6186b334c7c300f35f422c27134b6d8527c36bcee9756bcba6184bd2e'),(63,'collision','2c8e8852f7e728ba43c8719e6156385b9e58a927953961f401d0ff3205f3c4e4')]:
        manifest=source/f'native-{kind}-checkpoint-v{version}.json';q=json.loads(manifest.read_text())
        archive=source/f'native-{kind}-source-v{version}.zip'
        assert q['passed']and sha(archive)==q['checkpoint_SHA256']==digest
        with zipfile.ZipFile(archive)as z:
            assert set(z.namelist())==set(q['member_SHA256'])and sum(x.file_size for x in z.infolist())<4_000_000
            for name,h in q['member_SHA256'].items():
                assert not Path(name).is_absolute()and '..'not in Path(name).parts and not name.endswith(('.nes','.dbg','.o','.png','.mp4'))
                assert hashlib.sha256(z.read(name)).hexdigest()==h,name
            for name in q['explicit_source_commit_files']:assert sha(R/name)==q['member_SHA256'][name],name
        dest=R/f'docs/qa/checkpoints/2026-11-02/prince-native-{kind}-v{version}'
        assert not dest.exists();dest.mkdir(parents=True)
        for src,name in [(archive,'inputs.zip'),(manifest,'manifest.json')]:
            target=dest/name;target.write_bytes(src.read_bytes());assert sha(target)==sha(src)
        saved.append(dict(checkpoint=dest.relative_to(R).as_posix(),archive_SHA256=digest,members=len(q['member_SHA256'])))
    O.mkdir(exist_ok=True)
    (O/'receipt.json').write_text(json.dumps(dict(passed=True,source_only=True,ROM_written=False,installed=False,checkpoints=saved),indent=2)+'\n')
    print(json.dumps(saved))

if __name__=='__main__':main()
