"""Record the verified nightly and compact source/negative replay checkpoint."""
import json,subprocess,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
from nightly_patch_guard_v1 import check
O=R/'build/bub-delivery-freeze-1103-v99'
D=R/'docs/qa/checkpoints/2026-11-03/bub-earned-delivery-v99'
HEAD=R/'docs/qa/checkpoints/2026-11-03/bub-head-source-v59'
PIN='cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd'
read=lambda p:json.loads(Path(p).read_text())

def main():
    O.mkdir(exist_ok=True)
    delivery=R/'build/bub-earned-delivery-1103-v98';q=read(delivery/'verified-delivery.json')
    assert q['downloads_launch_verified']and q['ROM_sha256']==PIN and q['IPS_roundtrip']and not q['backup_created']
    guard=check(q['destination']);assert guard['ROM_sha256']==PIN
    release=subprocess.run(['gh','api','repos/kandowontu2/SMB-Crossover/releases/latest'],capture_output=True,text=True,check=True)
    release=json.loads(release.stdout);assert release['tag_name']=='Current'and len(release['assets'])==1
    asset=release['assets'][0];assert asset['name']=='SMB-Crossover-Latest-WIP-MMC5.ips'and asset['digest']=='sha256:'+q['IPS_SHA256']
    assert sha(delivery/asset['name'])==q['IPS_SHA256']
    published=dict(q,release_tag='Current',release_is_latest=True,sole_asset=asset['name'],release_asset_digest=asset['digest'],final_patch_guard=guard,checkpoint=D.relative_to(R).as_posix())
    (O/'published-receipt.json').write_text(json.dumps(published,indent=2)+'\n')
    # The head helper's final archive contains source/compact aggregates only.
    headroot=R/'build/bub-menu-candidate-1102-v2';hm=read(headroot/'head-source-v59.json')
    archive=R/hm['archive'];assert hm['passed']and sha(archive)==hm['archive_SHA256']and archive.stat().st_size<1_000_000
    with zipfile.ZipFile(archive)as z:
        assert len(z.namelist())==len(hm['members'])
        for name,h in hm['members'].items():
            f=R/name;assert sha(f)==h,name
            assert z.read(name.replace('\\','/'))==f.read_bytes(),name
    HEAD.mkdir(parents=True)
    (HEAD/'source.zip').write_bytes(archive.read_bytes())
    (HEAD/'receipt.json').write_text(json.dumps(hm,indent=2)+'\n')
    (HEAD/'qualified.json').write_bytes((headroot/'head-projection-v59-qualified.json').read_bytes())
    files=[Path(__file__),R/'tools/audit/check_bub_current_cold_1103_v97.py',R/'tools/audit/deliver_bub_earned_1103_v98.py',R/'build/bub-current-cold-1103-v97/receipt.json',delivery/'delivery.json',delivery/'verified-delivery.json',delivery/'release-notes.txt',O/'published-receipt.json',HEAD/'receipt.json',HEAD/'qualified.json']
    for identity,name in[(0,'bub'),(1,'bob')]:
        for task in['mushroom','full11']:
            p=delivery/f'downloads-{name}-{task}';c=p/'capture'
            files.extend([p/'controller.lua',p/'run.py',p/'ready.json',c/'binding.json',c/'result.json',c/('earned-mushroom.json'if task=='mushroom'else'full11.json'),c/('earned-first-mushroom-complete.png'if task=='mushroom'else'actual-active-1-2.png')])
            if task=='full11':files.append(c/'bub-observer.json')
    tools=['prepare_bub_earned_flower_1103_v91.py','prepare_bub_flower_first_pipe_1103_v92.py','prepare_bub_powered_bubble_control_1103_v93.py','prepare_bub_vertical_ride_takeoff_1103_v94.py','prepare_bub_vertical_ride_trace_1103_v95.py','prepare_bub_forward_bubble_control_1103_v96.py']
    files.extend(R/'tools/audit'/n for n in tools)
    for version in range(91,97):
        p=R/f'build/bub-earned-flower-1103-v{version}/bub-flower'
        files.extend([p/'controller.lua',p/'ready.json'])
        for name in['callback-error.json','full11.json','result.json','binding.json','bubble-relative.csv']:
            f=p/'capture'/name
            if f.exists():files.append(f)
    files=list(dict.fromkeys(files));D.mkdir(parents=True);target=D/'inputs.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for f in files:z.writestr(f.relative_to(R).as_posix(),f.read_bytes())
    assert target.stat().st_size<1_000_000
    with zipfile.ZipFile(target)as z:
        for f in files:assert z.read(f.relative_to(R).as_posix())==f.read_bytes()
    sources=[Path(__file__),R/'tools/audit/check_bub_current_cold_1103_v97.py',R/'tools/audit/deliver_bub_earned_1103_v98.py',*(R/'tools/audit'/n for n in tools)]
    head_sources=(headroot/'head-source-commit-files-v59.txt').read_text().splitlines()
    receipt=dict(passed=True,installed=True,ROM_SHA256=PIN,archive_SHA256=sha(target),archive_bytes=target.stat().st_size,members=len(files),head_checkpoint=HEAD.relative_to(R).as_posix(),head_archive_SHA256=sha(HEAD/'source.zip'),candidate_checkpoint='docs/qa/checkpoints/2026-11-03/bub-earned-native-v90',candidate_rows=q['candidate_rows'],downloads_rows=q['downloads_rows'],source_files=[f.relative_to(R).as_posix()for f in sources]+head_sources,scope='Verified same-name Downloads nightly and sole Latest IPS. Exact cf7 candidate and actual Downloads both pass two earned first-mushroom and two separate nonshortcut full1-1 replays; all4Downloads endpointPNG viewed. Parent cc7 head/brick IRQ proofs preserved under their own hash, exactcf7 init delta/cold/250pairedMain bound separately. Six later flower controller negatives retained, none relabeled. No videos, ROM/debug copies or helper additions. Flower route/audio-fidelity/performance and remaining roster remain incomplete.',bindings={f.relative_to(R).as_posix():sha(f)for f in files})
    (D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    handoff=R/'docs/qa/continuation-current.json';h=read(handoff)
    h['previous_installed_nightly_9cf']=h['installed_nightly'];h['installed_nightly']=published
    b=h['bub_original_upgrades_current_1102'];b.update(status='INSTALLED_HEAD_MUSHROOM_BOTH_FULL11_PASS_FLOWER_PERF_PENDING',installed=True,installed_SHA256=PIN,candidate='build/bub-initial-tier-1103-v87/bub-initial-tier.nes',candidate_SHA256=PIN,cookie='a72701f3691d419fd9ae7473840ce393',current_delivery_checkpoint=D.relative_to(R).as_posix(),head_checkpoint=HEAD.relative_to(R).as_posix(),current_cold='build/bub-current-cold-1103-v97/receipt.json')
    b['latest_candidate'].update(installed=True,fully_qualified=False,native_progress='Candidate and actual Downloads both mushroom+full1-1 x2 PASS; all4Downloads endpoints viewed; samecf7installed,no backup. SoleCurrentLatestIPS roundtrip/API verified. Laterflower, originalaudio/performance/fullgoal incomplete.')
    b['remaining']='Installed cf7 source head+nativecold tier fixes, earnedmushroom and separatefull1-1 bothIDs validatedcandidateandDownloads. Parenthead64 8506FF+6244nested min122; additionalbrick138FF+10480nested min122/124, final59freeze. Exactcurrent97cold/readback/32poison/fault/protection/retire and250pairedMain pass. Six actualflower controllers91..96 remain negatives: firstnormalpipe supportconstraint corrected92;93 actualbubble ride butLeft latchesbackward jump;94/95 unreachableverticaltakeoffwindows;96 noLeft butstallsunsupportedfirstpipeedgeX441/Y144. No flower pass/helpers or physicschange. Next prioritize measuredidle/walklag and Prince/DK Jr completion; then earnedflower route/allpowerups.'
    h['root_queue_current_1102'].update(status='FREE',last_candidate=PIN,installed_nightly=PIN,last_sessions={'DownloadsBubMushroom':83251,'DownloadsBubFull11':61468,'DownloadsBobMushroom':67565,'DownloadsBobFull11':66321},next='Exact cf7 fullydelivered/published; helperBubperformance investigation, Prince deferredcombatISR/lifecycle/cold and DKJr typedservices/bbox remainprivate. Laterflowercontroller remainsnegative, no newhelpers.')
    handoff.write_text(json.dumps(h,indent=2)+'\n')
    note=R/'docs/qa/bub-original-upgrades-1102.md'
    with note.open('a')as f:f.write('\nNovember3 delivery: the exactcf7 nightly now replaces Downloads directly, without a backup. Both identities pass actual Downloads first-mushroom and separate full1-1 replays, matching candidate frames/updates/checks exactly; all four endpoint images were viewed. The sole Current/Latest IPS reconstructs cf7 and its GitHub API digest matches7fae59278cda3952d5b12a89670e0a623bb114a5f4fd92c3d667f13d704dd5a1. Patch guards pass before/after and after all replays.\n\nParent head qualification now passes8,506 expanded genuine FF contexts and6,244 nested IRQs, minimumSP122. Plain-brick checks add138 actual FF profile minima and10,480 nested IRQs: small bump minimum122, mushroom-powered shatter124. All four exact native sound clocks are tracked. The compact head source checkpoint is `docs/qa/checkpoints/2026-11-03/bub-head-source-v59`. These CPU runs retain their cc7 hash. Separate exactcf7 cold/readback/warm/32header-poison/code+helperfault/protection/retire tests pass, together with250 paired Main updates proving original instruction/state/AXYP/SP and zero-cycle-delta after initialization. The only cartridge differences fromcc7 are14 initializer bytes and its authenticated cookie; new initializer instructions separately pass10IRQ+10genuineFF.\n\nThe later flower route remains unverified. Controller91..96 negatives are preserved in `docs/qa/checkpoints/2026-11-03/bub-earned-delivery-v99`, including the actual original jump-direction latch and unreachable test takeoff windows. They do not establish a physics regression or a helper need. Idle/walk lag, acoustic fidelity and broader roster work remain open. No new helper platform was added.\n')
    print(json.dumps(dict(passed=True,ROM_SHA256=PIN,checkpoint=D.relative_to(R).as_posix(),archive_bytes=target.stat().st_size,head_archive_bytes=(HEAD/'source.zip').stat().st_size,sources=receipt['source_files'])))

if __name__=='__main__':main()
