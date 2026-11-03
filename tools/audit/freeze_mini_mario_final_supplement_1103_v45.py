"""Tiny final43 source/packet supplement; existing19/42 checkpoints reused."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import hashlib,json
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/mini-mario-final-supplement-1103-v45'

def main():
    O.mkdir(exist_ok=True);source=R/'tools/audit/prepare_mini_mario_native_final_1103_v43.py'
    files=[source,Path(__file__)];packets=R/'build/mini-mario-native-packets-1103-v43'
    for name in ['smoke43','full43']:
        p=packets/name;ready=json.loads((p/'ready.json').read_text())
        assert ready['ROM_sha256']=='8daf59cc958e2a3a645882ea53c6bd75e9a7c641793054f8ce534358f369a7d7'
        for path,digest in ready['bindings'].items():assert sha(path)==digest,path
        files.extend(p/n for n in ['ready.json','controller.lua','run.py'])
    archive=O/'mini-final43-source.zip'
    with ZipFile(archive,'w',ZIP_DEFLATED,compresslevel=9)as z:
        for p in files:z.writestr(p.relative_to(R).as_posix(),p.read_bytes())
    members={p.relative_to(R).as_posix():dict(bytes=p.stat().st_size,SHA256=sha(p))for p in files}
    with ZipFile(archive)as z:
        for n,q in members.items():assert hashlib.sha256(z.read(n)).hexdigest()==q['SHA256']
    refs=[R/'build/mini-mario-menu-1103-v14/mini-art-menu-source-v19.zip',
          R/'build/mini-mario-frontend-final-1103-v42/mini-frontend-native-source-v42.zip',
          R/'build/mini-mario-candidate-root-1103-v44/candidate.json',
          R/'build/mini-mario-delivery-cold-root-1103-v43/receipt.json']
    receipt=dict(frozen=True,source_only=True,ROM_written=False,native_claim=False,
        final_candidate_SHA256='8daf59cc958e2a3a645882ea53c6bd75e9a7c641793054f8ce534358f369a7d7',
        archive=archive.relative_to(R).as_posix(),archive_bytes=archive.stat().st_size,archive_SHA256=sha(archive),members=members,
        references={p.relative_to(R).as_posix():dict(bytes=p.stat().st_size,SHA256=sha(p))for p in refs},
        commit_files=[source.relative_to(R).as_posix(),Path(__file__).relative_to(R).as_posix()],
        scope='Finalsource43 actualrotation+SmPose4onepart reservation, unchangedsourcecontrols/physics. Root runs/nativequalification/Downloads/LatestIPS and pause.19/42are immutable reused inputs, not nested/copied; actual negatives preserved, no cleanup. Full1-1 remains pending until root result.')
    (O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (O/'commit-files.txt').write_text('\n'.join(receipt['commit_files'])+'\n')
    print(json.dumps(dict(frozen=True,archive=str(archive),bytes=receipt['archive_bytes'],members=len(files),SHA256=receipt['archive_SHA256'])))

if __name__=='__main__':main()
