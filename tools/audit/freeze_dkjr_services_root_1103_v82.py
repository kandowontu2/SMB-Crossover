"""Verify a compact private DK Jr milestone, preserving its NMI scope limit."""
import hashlib,json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/dkjr-root-freeze-1103-v82'
D=R/'docs/qa/checkpoints/2026-11-03/dkjr-native-services-v50'

def main():
    O.mkdir(exist_ok=True)
    manifest=R/'build/dkjr-native-source-1102-v2/native-services-v50.json'
    q=json.loads(manifest.read_text());archive=R/q['archive']
    assert q['passed'] and not q['ROM_written'] and not q['native_owner_admitted']
    assert sha(archive)==q['archive_SHA256']=='9d5a804e3f038ccb86a92f92635e1dab8e9531a74923274ae0f2d03e6f2d8f1d'
    assert archive.stat().st_size==q['archive_bytes']==308226
    assert len(q['source_files'])==15
    with zipfile.ZipFile(archive) as z:
        assert set(z.namelist())=={m['path'] for m in q['members']}
        for m in q['members']:
            data=z.read(m['path']);assert len(data)==m['bytes']
            assert hashlib.sha256(data).hexdigest()==m['SHA256']
            assert not Path(m['path']).is_absolute() and '..' not in Path(m['path']).parts
            assert Path(m['path']).suffix.lower() not in ['.nes','.dbg','.o','.png','.mp4']
        for f in q['source_files']:
            assert sha(R/f['path'])==f['SHA256']
            assert z.read(f['path'])==(R/f['path']).read_bytes()
    assert q['assembly']['body_bytes']==8014 and q['assembly']['header_spare']==146
    D.mkdir(parents=True)
    (D/'inputs.zip').write_bytes(archive.read_bytes())
    (D/'helper-manifest.json').write_bytes(manifest.read_bytes())
    receipt=dict(passed=True,private_checkpoint_only=True,ROM_written=False,installed=False,
        archive_SHA256=sha(D/'inputs.zip'),archive_bytes=archive.stat().st_size,
        member_count=len(q['members']),source_files=q['source_files'],
        scope='Source/native-service progress only. Retains failed foreground and interrupt fixtures; no actual emulator gameplay or public admission.',
        NMI_scope_correction='Helper explicitly checked after freezing50:49 inherits NmiDisable=1, so its NMI is regular, not genuine FF lag audio. Historical archive wording is retained unchanged.51 must prove actual FF, INC NmiSkipped once, no regular branch, complete packet lifetime and audio/IRQ cuts before admission.',
        unfinished_vector_rows=q['assembly']['unfinished_rows'],
        bindings={str(p.relative_to(R)):sha(p) for p in [Path(__file__),manifest,D/'inputs.zip',D/'helper-manifest.json']})
    (D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (O/'receipt.json').write_text(json.dumps(dict(passed=True,checkpoint=D.relative_to(R).as_posix(),archive_bytes=archive.stat().st_size,source_files=q['source_files']),indent=2)+'\n')
    handoff=R/'docs/qa/continuation-current.json';h=json.loads(handoff.read_text());dk=h['dkjr_current_source_1102']
    dk['checkpoints'].append(D.relative_to(R).as_posix())
    dk['latest_unfrozen']='50 frozen private native-service milestone: body8014B/146spare,91B C460..C4BB save packets, actual62 GameCore epochs earned fruit/score1200 and pause60/thaw62;192 nativeDefeat architectural cases. Retained41/43/47 negatives. Correction:49 NmiDisable1 exercises regular NMI, not FF lag audio;51 must qualify actualFF branch, NmiSkipped, packet lifetime and full ISR/audio cuts.17 vector APIs unfinished. No ROM/native admission; historical65 model still needs current Prince/Bub rebind.'
    handoff.write_text(json.dumps(h,indent=2)+'\n')
    print(json.dumps(dict(passed=True,checkpoint=D.relative_to(R).as_posix(),archive_bytes=archive.stat().st_size,member_count=len(q['members']),source_files=len(q['source_files']),NMI='Regular only; FF qualification pending')))

if __name__=='__main__':main()
