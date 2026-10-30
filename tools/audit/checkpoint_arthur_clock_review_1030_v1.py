"""Retain the reviewed Arthur smoke and severe timing hold without ROM files."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2]
P=R/'build/arthur-physical-clock-v2'
OLD=R/'docs/qa/checkpoints/2026-10-30/arthur-physical-clock'
Q=R/'docs/qa/checkpoints/2026-10-30/arthur-clock-reviewed-performance-hold'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not Q.exists()
    expected=[(P/'handoff.json','505c20f7fa29c0f62bdcdff2bd996ee6562101b601369a84f8afd8e41b0308e3'),
        (P/'native-handoff-v3.json','dde1e2e66e9806280efe97bca88a6ea41800a6874d0ce01709db620dc6fc8259'),
        (OLD/'manifest.json','4a7c3c46eda52f6c4980b4bc34837db202e4cb06c913efcc78a4cb3c2e0ee350')]
    counts=[]
    for p,want in expected:
        assert sha(p)==want,p
        h=json.loads(p.read_text())
        for n,v in h.get('bindings',{}).items():assert sha(n)==v,n
        counts.append(len(h.get('bindings',{})))
    manifest=json.loads((OLD/'manifest.json').read_text())
    archive=OLD/'source-native-evidence.zip'
    assert sha(archive)==manifest['evidence']['sha256']
    Q.mkdir(parents=True)
    output=Q/'source-native-no-rom.zip';omitted=[];members=0
    with zipfile.ZipFile(archive)as src,zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=7)as dst:
        for info in src.infolist():
            data=src.read(info.filename)
            assert hashlib.sha256(data).hexdigest()==sha(R/info.filename),info.filename
            if info.filename.lower().endswith('.nes'):
                omitted.append(dict(path=info.filename,sha256=hashlib.sha256(data).hexdigest()));continue
            dst.writestr(info,data);members+=1
    assert len(omitted)==1 and members==746
    for p,want in expected:(Q/p.name).write_bytes(p.read_bytes())
    native=json.loads((P/'native-handoff-v3.json').read_text())
    proof=dict(status='CONTROLLER_GRAPHICS_PASS_SEVERE_PERFORMANCE_HOLD',
        candidate_sha256=native['candidate'],native_handoff_sha256=sha(P/'native-handoff-v3.json'),
        source_handoff_sha256=sha(P/'handoff.json'),verified_binding_counts=counts,
        installed=False,full_1_1_clear=False,earned_upgrade_completion=False,
        reviewed_whole_frames=['menu-arthur.png','lives-arthur.png','game-start.png','double-jump.png','source-lance.png','game-controlled.png'],
        review=['Menu/lives/gameplay body, double jump and lance coherent in the bounded cold controller run.',
            'Initial game-start frame precedes the first source body update; later actual body/black-detail assertions pass.',
            'Inherited cyan menu band is visible; it is not declared fixed.',
            'Normal hardware eight-sprite limit remained enabled, with no script RAM writes.'],
        result=native['result'],timing=native['timing'],same_controller_comparison=native['same_controller_matched_300frame_comparison'],
        hold_reason='266 lag NMIs in400 physical gameplay frames; the source clock/input repair does not solve rendering or Main cadence.',
        source_archive_sha256=sha(output),source_archive_bytes=output.stat().st_size,
        source_archive_members=members,all_archived_members_verified_against_original_files=True,
        omitted_ROMs=omitted,original_frozen_archive_sha256=sha(archive),
        no_new_native_run=True,no_download_change=True,
        next_work='Reduce measured foreground/interrupt cost, then qualify the exact shared successor before replacing Downloads.',
        binding={str(Path(__file__).resolve()):sha(__file__)})
    (Q/'review.json').write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(status=proof['status'],ROM=proof['candidate_sha256'],bindings=counts,
        archive_members=members,archive_bytes=output.stat().st_size)),flush=True)


if __name__=='__main__':main()
