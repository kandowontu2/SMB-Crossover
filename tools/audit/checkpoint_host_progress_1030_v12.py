"""Preserve the finished minimum FF/Arthur source integrations separately."""
from pathlib import Path
import json
from checkpoint_host_progress_1030_v9 import packets
from checkpoint_roster_progress_1030_v2 import R, save, sha


def main():
    reports, bindings = packets([
        ('build/ff-joint-full-render-qualified-v1/handoff.json',
         '33da4500485b1c1ebcf0613c95a01484740aec74f6267f87e0d07f3c2b66aa71'),
        ('build/arthur-joint-live-v5/handoff.json',
         '81c80a0557b7794c8f8c90878353913aaccf27c6d24ce233dbd8bfb7ab199df8')])
    bindings[str(Path(__file__).resolve())] = sha(__file__)
    save('ff-full-draw-and-arthur-live-source', dict(
        status='SOURCE_INTEGRATIONS_PRESERVED_NATIVE_PLAY_AND_PERFORMANCE_PENDING',
        FF_ROM_sha256='07cda1d4b0812717334dc15e886f56474953e30b2cb2f6ddc5ecfd5ace52ea13',
        Arthur_ROM_sha256='1d17a00a2fa48da5a020bcebc22e7d72fe1111599692a45c2d1b1ee0ec05e0d9',
        evidence=[
            'FF actual early native DrawAll path:96 full Main cases, correct body reservation/window0 and normal NMI publication; parent4608 transport/allflags plus6856 ISR controls retained.',
            'Arthur actual visible-menu fresh defers copying; real InitScreen calls original FF/native clear first, loads7485buffered reads and publishes Ready last, then24 Main updates.',
            'Arthur real native/pending menu resolution retires before selected identity; unloaded/poisoned cookies prevent source access; source RGB/foreign Main/NMI/ISR comparisons pass within prior leases.'
        ],
        limits=[
            'Neither candidate is the expanded-playable WIP release; both characters remain pending there.',
            'FF feet/postBG/native enemy/flash/palette/audio integration remains incomplete. Heavy spell and full Main costs remain high.',
            'Arthur current-rollout rebase/controller-native entry and severe lag remain open. Full goal and all-character1-1/every-upgrade checks remain active.'
        ]), bindings)
    p = R / 'docs/qa/host-integration-progress-2026-10-30.json'
    j = json.loads(p.read_text())
    j['latest_user_priority'] = 'Unlock implemented characters for play; new DK and authentic Contra Force roster sprites; corrected Kamikaze V1 sprites as native Mario skin.'
    j['active_work']['Final_Fantasy'] = '07cda1d4 actual early source draw/96 Main cases frozen; still pending in rollout while feet/postBG/enemy/flash/palette/audio and native/performance work remain.'
    j['active_work']['Arthur'] = 'Minimum real menu/reset→InitScreen/cache→Main source1d17a00a frozen, source/lifecycle/ISR/sourcepixels pass. Pending in rollout; source rebase/native controller and severe lag remain open.'
    j['active_work']['Rogue_Dawn'] = 'Natural fresh constructor and recursive area reset fixed;7e418 actual cold selection→healthy walk/jump/land passed. e706 adds correct final menu/lives portrait callback and priority; composing52-ready rollout.'
    j['active_work']['playable_rollout'] = 'Source e706 has52ready/28pending. Authentic DK/CF menu art and Kamikaze V1 native skin composing; no download replacement until final smoke/visual review.'
    p.write_text(json.dumps(j, indent=2) + '\n')


if __name__ == '__main__':
    main()
