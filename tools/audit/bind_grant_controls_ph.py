"""Freeze Grant's actual wall-leap input after observing the climb deadlock."""
from pathlib import Path
import argparse
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = Path('C:/Users/kando/Videos/SMB Crossover Archive')
TAIL = '''return function(c)
 local b=normal(c)
 if c.char==5 and c.variant==1 and c.world==0 and c.level==0 and c.r('Cv3Climb')~=0 then
  -- Cv3GrantClimb consumes a fresh A edge before its wall-retention probe.
  -- Holding Up alternated grab/loss without climbing the block corner.
  return{right=true,up=true,a=not c.lastA}
 end
 return b
end
'''


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    parent = ARCHIVE / '2026-10-24-roster-pg/controls-v2'
    original = parent / 'policy.lua'
    assert sha(original) == json.loads((parent / 'proof.json').read_text())['policy_sha256']
    observation = ARCHIVE / '2026-10-24-roster-ph/grant-observe-v2'
    proof = json.loads((observation / 'proof.json').read_text())
    assert proof['observation_complete'] and proof['exact_input_and_trace_prefix']
    rows = list(csv.DictReader((observation / 'completed.csv').open()))
    assert len(rows) == 201 and all((r['Player_X_Position'], r['Player_PageLoc'], r['Player_Y_Position']) == ('193', '6', '136') for r in rows)
    assert {r['Cv3Climb'] for r in rows} == {'0', '1'} and all(r['Cv3AttackAge'] == '0' and int(r['SavedJoypadBits']) in (1, 9) for r in rows)
    policy = a.output / 'policy.lua'
    text = 'local normal=(function()\n' + original.read_text() + '\nend)()\n' + TAIL
    assert 'emu.write(' not in text and 'dofile(' not in text
    policy.write_text(text)
    q = dict(prepared=True, game_changes=False, memory_writes=False,
        policy_sha256=sha(policy), parent_policy_sha256=sha(original),
        completed_observation_sha256=sha(observation / 'completed.csv'),
        observer_proof_sha256=sha(observation / 'proof.json'),
        wall_leap_source_sha256=sha(ROOT / 'src/cv3_abilities.s'),
        driver_sha256=sha(Path(__file__)),
        scope='201completed updates confirm x1729/y136grab-loss alternation with Right/Up, no attack and no A. Retry uses the already implemented native fresh-Awall leap, preserving jump table, speed, collision and all game bytes. Prior failures retained; this preparation is not a clear.')
    (a.output / 'proof.json').write_text(json.dumps(q, indent=2) + '\n')


if __name__ == '__main__':
    main()
