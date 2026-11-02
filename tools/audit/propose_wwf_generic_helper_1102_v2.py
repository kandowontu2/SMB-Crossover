"""Keep every late helper entry stable while adding the isolated WWF pit helper."""
import hashlib
import json
from pathlib import Path
import propose_wwf_generic_helper_1102_v1 as P

O = P.R / 'build/wwf-helper-stable-1102-v2'

def main():
    assert P.sha(P.BASE) == P.PIN
    O.mkdir(exist_ok=True)
    P.O = O
    b = P.scoped_load(P.BASE)
    source = P.expanded_source()
    old, oldlabels = P.assemble('original', source, b)
    start = 16 + 26 * 8192 + 0x800
    assert old == b['raw'][start:start+0xb2a]
    revised = P.successor(source)
    marker = '.proc HpGetCharacterMask'
    assert revised.count(marker) == 1
    revised = revised.replace(marker, '.res 2,$ea ; Preserve all original late public entry PCs.\n'+marker)
    new, labels = P.assemble('proposed', revised, b)
    assert len(new) == len(old) == 0xb2a
    fixed = {name:pc for name,pc in oldlabels.items() if pc >= oldlabels['HpGetCharacterMask']}
    assert all(labels.get(name) == pc for name,pc in fixed.items())
    assert labels['HpPauseCold'] == oldlabels['HpPauseCold'] == 0xb0f0
    checks, _ = P.cpu_checks(b, new, labels)
    relocations = {n:dict(old=pc,new=labels[n]) for n,pc in oldlabels.items() if n in labels and pc != labels[n]}
    q = dict(passed=True, proposal_only=True, ROM_written=False, installed=False,
        base_ROM_SHA256=P.PIN, physical_PRG=26, CPU_half_open=[0xa800,0xb32a],
        original_SHA256=hashlib.sha256(old).hexdigest(), proposed_SHA256=hashlib.sha256(new).hexdigest(),
        fixed_public_entries=fixed, relocations=relocations, labels=labels, original_labels=oldlabels,
        checks=checks, remaining='Full actual outside-span caller/data census, scene/ISR regression and native assisted crossings before admission.',
        helper=dict(raw=29,all_six_WWF=True,stage='1-1',area=37,center_x=1400,left_x=1376,initial_y=208,width=48,native_actor=40))
    (O/'proposal.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(passed=True,stable_entries=len(fixed),relocations=relocations,ROM_written=False)))

if __name__ == '__main__':
    main()
