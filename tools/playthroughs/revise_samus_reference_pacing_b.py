"""Resume reference timing across an actual noninteractive growth/injury interval."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[2]
D = R / 'build/verification/root49-samus-reference-pacing-a'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    source = D / 'policy.lua'
    target = D / 'policy-b.lua'
    assert not target.exists()
    text = source.read_text()
    text = text.replace("local lastStage=''", "local lastStage=''\nlocal lastPoll=nil")
    anchor = " local key=c.world..'-'..c.level..'-'..c.area\n if key~=lastStage then\n"
    replacement = " local resumed=lastPoll and c.poll-lastPoll>2\n lastPoll=c.poll\n local key=c.world..'-'..c.level..'-'..c.area\n if key~=lastStage or resumed then\n"
    assert text.count(anchor) == 1
    text = text.replace(anchor, replacement)
    text = text.replace('math.min(#ref,cursor+2500)', 'math.min(#ref,cursor+(key~=lastStage and 2500 or 180))')
    # Calculate the stage-transition range before publishing the new stage key.
    text = text.replace(" if key~=lastStage or resumed then\n  lastStage=key\n", " if key~=lastStage or resumed then\n  local transition=key~=lastStage\n  lastStage=key\n")
    text = text.replace('key~=lastStage and 2500 or 180', 'transition and 2500 or 180')
    target.write_text(text)
    report = dict(status='PREPARED_B_RESUMPTION_CONTROLLER_CORRECTION', before_sha256=sha(source), after_sha256=sha(target),
        first_actual_negative='A stalls against real pipe atX721/Y176 after its cursor stays before a60-update injury freeze. Actor/power state resumes, but the policy was not called during the noninteractive interval.',
        correction='On the first actual gameplay poll after a gap, search up to180 reference frames forward to resume matching the current engine/power/pose; stage transitions retain their2500-frame search.',
        no_runtime_or_emulated_state_changes=True, no_clear_claim=True)
    (D / 'revision-b.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Prepared B; A and its actual negative are retained.')


if __name__ == '__main__':
    main()
