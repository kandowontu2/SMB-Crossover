"""Qualify Bob's terminal route on the already delivered, unchanged ROM."""
import json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
from deliver_bub_root_wip_1102_v43 import proof,PIN,D
from nightly_patch_guard_v1 import check
O=R/'build/bob-delivered-qualification-1102-v45'
C=R/'docs/qa/checkpoints/2026-11-02/bob-full11-v45'

def main():
    run=R/'build/bub-menu-candidate-1102-v2/native-current-landing-bob-full11-source-wall';p=proof(run)
    assert p['frames']==13513 and p['completed_Main']==5253 and p['checks']==61696 and p['failures']==0
    assert p['native_pops']==17 and p['original_rides']==6 and sha(D)==PIN
    guard=check(D);assert guard['passed']
    prior=R/'build/bub-root-delivery-1102-v43/published-receipt.json';delivery=json.loads(prior.read_text())
    assert delivery['ROM_sha256']==PIN and delivery['downloads_launch_verified']and delivery['release_is_latest']
    O.mkdir(exist_ok=True);assert not C.exists();C.mkdir(parents=True)
    paths={Path(__file__),R/'tools/audit/prepare_bob_reachable_rearm_native_1102_v42.py',R/'tools/audit/check_bob_reachable_rearm_1102_v41.py',R/'build/bub-menu-candidate-1102-v2/bob-reachable-rearm-v41-CPU.json',prior,run/'ready.json',run/'controller.lua',run/'run.py'}
    for name in['binding.json','full11.json','bub-observer.json','result.json','capture-budget.json','route.csv','observations.csv','actual-active-1-2.png']:
        paths.add(run/'capture'/name)
    assert sum(p.stat().st_size for p in paths)<1_000_000
    archive=C/'inputs.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for path in sorted(paths):z.write(path,path.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        for path in paths:assert z.read(path.relative_to(R).as_posix())==path.read_bytes()
    receipt=dict(passed=True,ROM_sha256=PIN,ROM_changed=False,installed_bytes_verified=True,patch_guard=guard,Bob_candidate_full11=p,actual_Downloads_Bob_full11=False,actual_Downloads_Bub_full11=True,prior_delivery=str(prior.relative_to(R)),archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,files={path.relative_to(R).as_posix():sha(path)for path in sorted(paths)},remaining='Original source-preserving bridge performance, all powerups/audio, modes/shortcut routes and remaining roster integrations remain open.')
    for path in[C/'receipt.json',O/'receipt.json']:path.write_text(json.dumps(receipt,indent=2)+'\n')
    old=R/'build/bub-root-delivery-1102-v43/release-notes.txt';notes=old.read_text();notes+='\nFollow-up on the same ROM/IPS: Bob also clears non-shortcut Hard 1-1 into active 1-2, lives 2 to 2, all four pipes/three gaps, 17 natural pops and six original bubble rides. 13,513 physical frames / 5,253 Main updates; 61,696 source/hardware checks with zero failures. This completes the candidate Bob route; actual Downloads full route was tested as Bub. No new ROM bytes or IPS.\n'
    (O/'release-notes.txt').write_text(notes)
    print(json.dumps({k:v for k,v in receipt.items()if k!='files'}))

if __name__=='__main__':main()
