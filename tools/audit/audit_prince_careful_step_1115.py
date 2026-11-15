"""Original variable-length careful-step selector; explicit CPU primitives."""
from hashlib import sha256
from pathlib import Path
import json,re
import audit_prince_sword_control_map_1115 as Map

R,Original,Packet=Map.R,Map.Original,Map.Packet


def run(raw):
    assert sha256(raw).hexdigest()=='16a385654e80105f83470e14cd328d8bbceaa659730f4a81a2f36ca039cfbcfb'
    donor=Original.donor();core=R/'build/prince-actor-1101-v1/contact-core';names=Map.labels(core.with_suffix('.lbl'))
    parts=Packet.extract(raw)[1];lo=names['PpN_7_F615'];hi=names['PpN_7_F646']+3
    expected=core.with_suffix('.bin').read_bytes()[lo-0xa000:hi-0xa000]
    assert parts[0][lo-0xa000:hi-0xa000]==expected
    source=core.with_suffix('.s').read_text();count=0
    for pc,encoded in re.findall(r'; native bank7 \$([\da-fA-F]{4}) ([\da-fA-F]+): ',source):
        pc=int(pc,16)
        if 0xf55b<=pc<0xf649:
            data=bytes.fromhex(encoded);at=16+7*16384+pc-0xc000
            assert donor[at:at+len(data)]==data;count+=1
    results=[]
    for distance in range(2,64):
        q=Map.leaf(5,0xf615,{0x4f:distance,0x360:0,0x361:0,0x616:0,0x618:0})
        assert q['action']==min(29+(distance>>1),42)
        if distance%2==0 and distance<=32:results.append(dict(raw_distance=distance,halved_distance=distance>>1,action=q['action']))
    q=dict(passed=True,ROM_SHA256=sha256(raw).hexdigest(),donor_SHA256=Original.SHA,
        authenticated_original_instruction_rows=count,current_selector_extent=[lo,hi],current_selector_SHA256=sha256(expected).hexdigest(),
        primitive_cases=62,representative_cases=results,
        actual_B_gate='F55B requires pose15;F56C/56F reads held040A bit40',
        selector='F61D LSR4F; nonzero values1..13 select29+value atF62C/F62F;14+ select42 atF644',
        action35='Valid partial careful step: raw4F12 becomes6;29+6=35. Not a missing admission or inferred bump.',
        valid_nonzero_step_actions=list(range(30,43)),old_controller_accepted_only=[30,42],
        scope='Explicit work-distance control primitives, not ordinary gameplay, measured body geometry or a full-stage clear',
        outputs=0,Mesen=False)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':print(json.dumps(run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()),separators=(',',':')),flush=True)
