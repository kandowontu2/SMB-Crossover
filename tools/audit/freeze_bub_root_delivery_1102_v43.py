"""Keep the exact delivered Bub delta and two bounded native stage receipts."""
import json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/bub-root-checkpoint-1102-v43'
D=R/'docs/qa/checkpoints/2026-11-02/bub-landing-delivery-v43'

def main():
    p=R/'build/bub-root-delivery-1102-v43';q=json.loads((p/'published-receipt.json').read_text())
    assert q['installed']and q['downloads_launch_verified']and q['release_is_latest']and q['IPS_roundtrip']
    assert q['ROM_sha256']=='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'
    assert q['IPS_SHA256']=='08ac42e7613f8d236c621713bee7f1c4b280e991b692cf5f3e84f936a73630ec'
    paths={Path(__file__),R/'tools/audit/deliver_bub_root_wip_1102_v43.py',R/'tools/audit/compose_bub_current_landing_1102_v32.py',R/'build/bub-menu-candidate-1102-v2/combined-current-landing.json',p/'published-receipt.json',p/'verified-delivery.json',p/'release-notes.txt'}
    for row in[q['candidate_Bub_full11'],q['downloads_Bub_full11']]:
        run=R/row['path'];paths.update([run/'ready.json',run/'run.py',run/'controller.lua'])
        for name in['binding.json','bub-observer.json','full11.json','result.json','capture-budget.json','route.csv','observations.csv','actual-active-1-2.png']:
            paths.add(run/'capture'/name)
    assert len(paths)<64 and sum(x.stat().st_size for x in paths)<2_000_000
    assert not D.exists();D.mkdir(parents=True);archive=D/'inputs.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for x in sorted(paths):
            assert x.is_relative_to(R)and x.suffix not in['.nes','.mp4','.dbg']
            z.write(x,x.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        assert len(z.namelist())==len(paths)
        for x in paths:assert z.read(x.relative_to(R).as_posix())==x.read_bytes()
    receipt=dict(passed=True,ROM_sha256=q['ROM_sha256'],IPS_SHA256=q['IPS_SHA256'],native_scope='Candidate and actual Downloads Bub full non-shortcut Hard1-1 into active1-2, no life loss, no new helpers. Bob remains partial; broad roster/all-powerup/audio/performance work incomplete.',delivery=q,archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,files={x.relative_to(R).as_posix():sha(x)for x in sorted(paths)},source_dependencies=['docs/qa/checkpoints/2026-11-02/bub-landing-v27','docs/qa/checkpoints/2026-11-02/bub-landing-v35','docs/qa/checkpoints/2026-11-02/sunny-palette-v9'])
    (D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    O.mkdir(exist_ok=True);(O/'receipt.json').write_text(json.dumps(dict(passed=True,checkpoint=D.relative_to(R).as_posix(),archive_SHA256=receipt['archive_SHA256'],archive_bytes=receipt['archive_bytes'],files=len(paths)),indent=2)+'\n')
    print(json.dumps(dict(checkpoint=D.relative_to(R).as_posix(),archive_SHA256=receipt['archive_SHA256'],archive_bytes=receipt['archive_bytes'],files=len(paths))))

if __name__=='__main__':main()
