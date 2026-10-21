"""Prepare an ordinary Sophia route discovery on the frozen working image."""
from pathlib import Path
import hashlib
import json

R=Path(__file__).resolve().parents[2]
D=R/'build/verification/root49-sophia-current-c-route-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not D.exists()
    D.mkdir(parents=True)
    identity=R/'build/verification/root49-current-c-transfers-a/identity.lua'
    (D/'identity.lua').write_bytes(identity.read_bytes())
    base=(R/'tools/playthroughs/roster_policy.lua').read_text()
    # Ordinary coin metatiles are pickups, not floor support. Keep this a
    # controller decision; no runtime or test mutation is made here.
    assert base.count('t~=0xc2')==1
    base=base.replace('t~=0xc2','t~=0xc2 and t~=0xc3')
    (D/'base-a.lua').write_text(base)
    text='dofile('+json.dumps((D/'identity.lua').as_posix())+')\nreturn dofile('+json.dumps((D/'base-a.lua').as_posix())+')\n'
    (D/'policy-a.lua').write_text(text)
    checkpoint=R/'build/checkpoints/roster-audit-v49-combined-ground-audio-samus-c/manifest.json'
    assert sha(checkpoint)=='7bde77980e47d11ed78b9348384016b1a805ff40a02ff180b33f0e8e727b5305'
    (D/'preparation.json').write_text(json.dumps(dict(status='PREPARED_ORDINARY_SOPHIA_CURRENT_C_DISCOVERY',
        script_sha256=sha(__file__),checkpoint_sha256=sha(checkpoint),
        files={p.name:sha(p) for p in [D/'identity.lua',D/'base-a.lua',D/'policy-a.lua']},
        phase_cap_bytes=1000000000,final_reserve_bytes=100000000,global_cap_bytes=70000000000,
        emulated_writes=False,discovery_only=True,final_clear=False),indent=2)+'\n')
    print('Prepared ordinary current-C Sophia discovery with actual identity guard.')


if __name__=='__main__':main()
