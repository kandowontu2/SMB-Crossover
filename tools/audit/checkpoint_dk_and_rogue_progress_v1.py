"""Preserve bounded source/negative-native evidence without ROM or capture copies."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
from checkpoint_roster_packets_v1 import ROOT, archive, verify


def bound(path):
    path = Path(path).resolve()
    data = path.read_bytes()
    return dict(path=str(path), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def save_once(path, text):
    if path.exists():
        assert path.read_text() == text, path
    else:
        path.write_text(text)


def main():
    acq = ROOT / 'build/source-acquisition/dk-bowser-2026-10-29/acquisition.json'
    match = ROOT / 'build/dk-original-source-match-v1/proof.json'
    art = ROOT / 'build/dk-source-assets-v1/handoff.json'
    aq, mt, at = [json.loads(p.read_text()) for p in [acq, match, art]]
    assert mt['passed'] and mt['full_PRG_CHR_payload_exact']
    assert len(at['frames']) == 9 and all(f['pixel_exact'] for f in at['frames'])
    dk_report = ROOT / 'docs/qa/dk-bowser-source-progress-2026-10-29.txt'
    dk_text = '''Original Donkey Kong and SMB3 Bowser source progress, 29 October 2026

The pinned RussianManSMWC Donkey Kong disassembly at commit
343f4c81880a253c0e8ede81fe7c21f205815280 assembles with the existing local asm6.
Every PRG and CHR payload byte matches the user's Donkey Kong (World) (Rev1).
Only header7/12/15 differ. No downloaded ROM or executable was used.
Source/credit: https://github.com/RussianManSMWC/Donkey-Kong-NES-Disassembly

Nine original poses are packed as native8x16 parts into4KBCHR without scaling.
Eight are actual48x32 background records; the ninth is the native falling
sprite. Their source pixels and decoded packed output match, including OAMY+1.
The source25M background2/falling sprite3 palette is0F/30/36/06. Root viewed
the complete nine-pose contact sheet; its RGB display approximates NES hues.
CHR820..823 is now exclusively reserved for this DK implementation. No PRG
or active RAM is allocated here. Full host integration/native remains open.

Original DK is an NPC, not Jumpman. Original player physics for a playable
Donkey Kong do not exist in this source. The crossover's controls, traversal,
collision, walk choices and pickup rules need an explicit authored adapter.
Source poses, barrel behavior, chest animation and sound remain the reference.

The Southbird SMB3 disassembly is pinned to
09b1bd81a788de8ceec664a34094e84ddb463117. All32PRG assembly leaves plus master
andREADME were acquired and authenticated against Git blob hashes. Its Bowser
movement/fire/break-floor/9-frame sprite tables are located inPRG001.
Source/credit: https://github.com/captainsouthbird/smb3 and
http://www.sonicepoch.com/sm3mix/ . No complete SMB3 rebuild or ROM-byte match
has yet been established, and no Bowser host port/native result is claimed.

The local assembly match and packed assets are useful implementation inputs,
not a completed DK/Bowser character. This checkpoint contains source/receipts
and the derived DK assets; original ROMs, full CHR, compiler and runtime files
remain hash-bound local references.
'''
    save_once(dk_report, dk_text)
    own_tools = [ROOT / 'tools/audit' / n for n in [
        'acquire_dk_bowser_source_v1.py', 'match_original_dk_source_v1.py',
        'prepare_original_dk_assets_v1.py']]
    wrapper = dict(status='DK source payload exact and9 authentic packed poses; SMB3 source acquired only',
                   native=False, acquisition=bound(acq), source_match=bound(match), assets=bound(art),
                   owned_files=[bound(p) for p in own_tools + [dk_report]],
                   source_files=aq['files'], outputs=at['outputs'],
                   CHR_reservation=dict(owner='Original Donkey Kong', first=820, last=823, bytes=4096),
                   limits='No DK/Bowser host, fullMain, native1-1 or earned-powerup claim; SMB3 source not yet ROM matched.')
    wrapper_path = ROOT / 'build/dk-source-assets-v1/root-handoff.json'
    save_once(wrapper_path, json.dumps(wrapper, indent=2)+'\n')
    previous = ROOT/'docs/qa/checkpoints/2026-10-28/dk-exact-source-assets-and-bowser-source/root-review.json'
    if previous.exists():
        # A completed DK packet is immutable even if the later Rogue stage
        # needs repair. Verify it in place; never delete or recreate it.
        frozen = json.loads(previous.read_text())
        assert frozen['handoff_sha256'] == bound(wrapper_path)['sha256']
        assert frozen['archive_sha256'] == bound(previous.parent/'frozen-source-packet.zip')['sha256']
        for path, digest in frozen['original_bound_files'].items():
            assert bound(path)['sha256'] == digest, path
    else:
        archive('dk-exact-source-assets-and-bowser-source', str(wrapper_path.relative_to(ROOT)),
                lambda d: d['owned_files'] + d['source_files'] + d['outputs'],
                [str(p.relative_to(ROOT)) for p in [acq, match, art, Path(__file__).resolve()]],
                dict(DK_payload_exact=True, original_frames=9, native=False, SMB3_ROM_match=False))

    source_handoff = ROOT / 'build/rogue-dawn-scheduler-v5/handoff.json'
    sh = json.loads(source_handoff.read_text())
    assert bound(source_handoff)['sha256'] == '26834b7df8653cec66022f3b1ac731c0d799b9f3a46cb6818aad0c4174f27fa1'
    seen = {}
    verify(sh, seen)
    assert len(sh['bindings']) == 614
    owned = json.loads((ROOT / 'build/rogue-dawn-scheduler-v5/owned-files.json').read_text())
    rows = []
    for name in ['rogue-dawn-scheduler-native-easy-v1', 'rogue-dawn-scheduler-native-easy-v2']:
        folder = ROOT / 'build/verification' / name
        ready, result, review, launch = [json.loads((folder / f).read_text())
                                         for f in ['ready.json', 'result.json', 'review.json', 'launch.json']]
        assert not result['passed'] and result['zero_deaths']
        assert not launch['changed_inputs'] and launch['settings_before'] == launch['settings_after']
        assert review['container']['full_frames'] == result['full_frames']
        rows.append(dict(name=name, source_ROM=ready['ROM_sha256'], route_passed=False,
                         reason=result['reason'], frames=result['frames'], completed_Main=result['completed_loops'],
                         decoded_whole_frames=result['full_frames'], whole_frames_visually_viewed=5,
                         min_SP=result['min_SP'], strict_guard_failure=False,
                         ready=bound(folder/'ready.json'), result=bound(folder/'result.json'),
                         review=bound(folder/'review.json'), launch=bound(folder/'launch.json'),
                         stream_reference=bound(folder/'captures.nesppuv1'),
                         sheet=bound(folder/'selected-whole-frames.png')))
    native_report = ROOT / 'docs/qa/rogue-dawn-first-native-pilots-2026-10-29.json'
    assert not native_report.exists()
    nr = dict(status='Two terminal failed-route discovery pilots; no playable promotion', runs=rows,
              confirmed_visual_issue='Overworld sky is black; source triage finds missing native BG restoration in Rogue color dispatch. New private fix is in progress, not this frozen ROM.',
              corrected_hypothesis='Original uses freshUp to unmorph. Base controller overwrites that intent during first-block phase. Player_State from gravity is not a stable grounded predicate; source stand0/aim4 accepts freshA.',
              controller_successor='Unlaunched rogue_dawn_11_v2 uses source action/support and exact fixed-ROM metatile attributes, strips incidental morph inputs. No movement code fix is inferred.',
              preflight_note='Initial old launcher refused changed global settings bytes before any emulator launch. Semantic comparison found ONLY RecentFiles change; v2 retains all hardware checks and verifies before=after. User settings untouched.',
              scope='Every lossless frame structurally decoded;5selected wholeframes/run visually viewed. No all-ability, full-level, music-audibility or FPS qualification. Retain original negative routes and streams.',
              active_own_native_processes=[], Downloads_unchanged=True)
    native_report.write_text(json.dumps(nr, indent=2)+'\n')
    extra = [ROOT / p for p in [
        'tools/audit/rogue_dawn_native_prepare_v1.py', 'tools/audit/rogue_dawn_native_prepare_v2.py',
        'tools/audit/run_frozen_roster_ready_v2.py', 'tools/playthroughs/rogue_dawn_11_v1.lua',
        'tools/playthroughs/rogue_dawn_11_v2.lua',
        'docs/qa/rogue-dawn-first-pilot-triage-2026-10-29.json',
        'docs/qa/rogue-dawn-ground-support-source-2026-10-29.json',
        'tools/rogue_dawn_scheduler_pilot_triage_v1.py', 'tools/rogue_dawn_ground_support_v1.py']]
    for row in rows:
        folder = Path(row['ready']['path']).parent
        extra += [folder/n for n in ['ready.json', 'prepared-with-2gb-reservation.json', 'result.json',
                                    'review.json', 'launch.json', 'run.lua', 'inputs.csv',
                                    'trace.csv', 'events.jsonl', 'selected-whole-frames.png']]
    root_handoff = dict(sh)
    root_handoff.update(original_handoff=bound(source_handoff), native_pilot_report=bound(native_report),
                        owned_files=owned['final_source_and_cpu_packet'] + owned['historical_source_and_negatives']
                        + [bound(p) for p in extra+[native_report, Path(__file__).resolve()]],
                        actual_ASM_dependencies={}, limits=nr['scope'])
    rp = source_handoff.parent/'root-handoff.json'
    assert not rp.exists()
    rp.write_text(json.dumps(root_handoff, indent=2)+'\n')
    subprocess.run([sys.executable, '-B', str(ROOT/'tools/audit/checkpoint_roster_component_v5.py'),
                    '--handoff', str(rp), '--name', 'rogue-owned-nmi-source-and-first-native-negatives'],
                   cwd=ROOT, check=True)
    progress = ROOT/'docs/qa/new-character-source-progress-2026-10-28.json'
    state = json.loads(progress.read_text())
    state['DK_original_source'] = dict(source_match=bound(match), assets=bound(art),
                                      source_report=bound(dk_report), CHR=[820,823],
                                      status='All PRG/CHR source payload exact;9poses packed/pixel exact. Host/native still open.')
    state['SMB3_Bowser_source'] = dict(acquisition=bound(acq), status='Pinned source acquired; original Bowser routines located, not yet ROM-matched or ported.')
    state['Rogue_first_native_pilots'] = bound(native_report)
    state['Rogue_owned_NMI_source'] = dict(handoff=bound(source_handoff), status='Frozen private source-NMI unit; first native routes fail controller acquisition, confirmed black-sky fix and performance work remain open.')
    progress.write_text(json.dumps(state, indent=2)+'\n')
    print(json.dumps(dict(DK_frames=9, source_bindings=len(seen), native_failed_routes=2,
                          source_report=bound(dk_report), native_report=bound(native_report))))


if __name__ == '__main__':
    main()
