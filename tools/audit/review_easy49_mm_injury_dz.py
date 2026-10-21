"""Pin the passive DU replay and classify actual injury owners, not stale death X."""
from pathlib import Path
import csv
import hashlib
import json

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root49-du-megaman-injury-dz.json'
    assert not out.exists()
    a = R / 'build/roster-through-2-2/root49dw-megaman-union-1-v0-mmc3'
    b = R / 'build/roster-through-2-2/root49dx-megaman-injury-1-v0-mmc3'
    def rows(p):
        with p.open(newline='') as f:
            return list(csv.DictReader(f))
    assert (a / 'trace.csv').read_bytes() == (b / 'trace.csv').read_bytes()
    assert (a / 'inputs.csv').read_bytes() == (b / 'inputs.csv').read_bytes()
    entries = rows(b / 'mm-injury-owner.csv')
    injuries = [x for x in entries if x['event'] == 'InjurePlayer']
    contacts = []
    for row in injuries:
        slot = int(row['ObjectOffset'])
        actors = [list(map(int, x.split(':'))) for x in row['actors'].split(';')]
        actor = actors[slot]
        assert actor[0] == slot and int(row['cpuX']) == slot
        player = list(map(int, row['playerBox'].split(':')))
        enemy = actor[-4:]
        overlaps = player[0] <= enemy[2] and player[2] >= enemy[0] and player[1] <= enemy[3] and player[3] >= enemy[1]
        assert overlaps
        contacts.append(dict(frame=int(row['frame']), poll=int(row['poll']), selected=int(row['SelectedCharacter']),
            difficulty=int(row['CrossoverBehaviorVersion']), x=int(row['Player_X_Position']) + 256 * int(row['Player_PageLoc']),
            y=int(row['Player_Y_Position']), state=int(row['Player_State']), power_before=int(row['PlayerStatus']),
            slot=slot, enemy_ID=actor[2], enemy_X=actor[4], enemy_Y=actor[5],
            player_box=player, native_enemy_box=enemy, inclusive_native_overlap=True))
    assert contacts == [
        dict(frame=6867, poll=6866, selected=1, difficulty=0, x=1149, y=176, state=0, power_before=1,
             slot=0, enemy_ID=6, enemy_X=1161, enemy_Y=184, player_box=[117,184,131,208], native_enemy_box=[131,198,141,204], inclusive_native_overlap=True),
        dict(frame=7713, poll=7712, selected=1, difficulty=0, x=1811, y=176, state=0, power_before=0,
             slot=2, enemy_ID=6, enemy_X=1823, enemy_Y=184, player_box=[113,184,127,208], native_enemy_box=[127,198,137,204], inclusive_native_overlap=True)]
    result = json.loads((b / 'result.json').read_text())
    assert result['failure'] == 'death' and result['frames'] == 7713
    trace = rows(b / 'trace.csv')
    transitions = [dict(frame=int(z['frame']), world=int(z['world']), level=int(z['level']), x=int(z['x']),
                        y=int(z['y']), before=int(x['power']), after=int(z['power']))
                   for x, z in zip(trace, trace[1:]) if x['power'] != z['power']]
    refs = [V / 'root49-du-megaman-injury-dx/binding.json', a / 'trace.csv', a / 'inputs.csv',
            b / 'trace.csv', b / 'inputs.csv', b / 'mm-injury-owner.csv', b / 'result.json']
    report = dict(status='PASS_PASSIVE_REPLAY_IDENTITY_ACTUAL_GOOMBA_OWNERS_TWO_GROUNDED_SIDE_CONTACTS',
        script_sha256=sha(__file__), actual_ROM_sha256=sha(b / 'smb-crossover-mmc3.nes'),
        exact_original_trace_frames=len(trace), exact_original_controller_polls=len(rows(b / 'inputs.csv')),
        contacts=contacts, observed_power_transitions=transitions,
        classification='Both guarded injuries occur grounded at the native boxes horizontal inclusive edge. First loses a natural tier; second kills. Nearby Piranhas are not these injury owners. No new runtime defect or source-enemy fractional equivalence is inferred.',
        native_KillPlayer_X_not_owner='At KillPlayer the status query has changed cpuX to0; ObjectOffset2 and prior guarded injury/status hooks retain the actual fatal owner.',
        reference_files=[dict(path=p.relative_to(R).as_posix(), sha256=sha(p), bytes=p.stat().st_size) for p in refs],
        runtime_changes=False, accepted_release=False, goal_complete=False)
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], sha(out))


if __name__ == '__main__':
    main()
