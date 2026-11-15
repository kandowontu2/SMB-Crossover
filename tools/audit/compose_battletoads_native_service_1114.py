"""Exact funded native-service optimization over the verified571 nightly."""
from hashlib import sha256
import json
from pathlib import Path

import compose_native_floatey_score_1114 as Parent
import check_battletoads_native_service_model_1114 as Model

R=Path(__file__).resolve().parents[2]
PIN=Parent.CANDIDATE
CANDIDATE='ae669c7ec7536f1c912b3000597be7b3416c20f312638b2589f52fab55f0bc01'
GRANT=R/'docs/qa/allocations/battletoads-native-service-candidate-1114.json'
GRANT_SHA='197cfe60a47f505ad818eb01a84d51cf3d4ed46f19c679cc62840d15553adae5'


def digest(data):return sha256(data).hexdigest()


def allocation():
    data=GRANT.read_bytes()
    assert digest(data)==GRANT_SHA
    q=json.loads(data)
    assert q['eligible_input_SHA256']==PIN and q['private_ROM_composition_and_native_authorized']
    assert q['funded_bytes']==347 and q['actual_changed_bytes']==160
    for name,pin in q['frozen_sources'].items():assert digest((R/name).read_bytes())==pin,name
    return q,digest(data)


def proposal(raw):
    assert isinstance(raw,bytes)and digest(raw)==PIN,'Expected exact verified571'
    grant,grant_sha=allocation();changes,model=Model.recipe(raw)
    assert len(changes)==347
    image=bytearray(raw)
    for at,value in changes.items():image[at]=value
    image=bytes(image)
    actual={at for at,(a,b)in enumerate(zip(raw,image,strict=True))if a!=b}
    assert len(actual)==160 and actual<=changes.keys()
    assert len(image)==len(raw)==2097168
    assert digest(image)==CANDIDATE
    assert image[Model.BT.BASE:Model.BT.BASE+8192]==raw[Model.BT.BASE:Model.BT.BASE+8192]
    assert image[765863:765879]==raw[765863:765879]
    assert image[Parent.AT:Parent.AT+10]==Parent.NEW
    assert all(image[at]==raw[at]for at in range(len(raw))if at not in changes)
    return image,dict(parent_SHA256=PIN,candidate_SHA256=digest(image),allocation_SHA256=grant_sha,
        envelope_bytes=347,changed_bytes=160,entire_BT8192_cookie_Check_score10_and_all_unowned_bytes_exact=True,
        source_model=model,outputs=0,native_qualified=False,installed=False)


def inverse(raw):
    assert CANDIDATE is not None and isinstance(raw,bytes)and digest(raw)==CANDIDATE
    grant,_=allocation();old=json.loads(Model.LEASE.read_bytes());parent=bytearray(raw)
    for row in old['envelopes']:
        lo,hi=row['file_half_open']
        # Exact old bytes are carried in the frozen source proposal receipt.
        # Obtain them from a strict owning571 input, never a mutable baseline.
        entry=next(r for r in grant['preimages']if r['file_half_open']==[lo,hi])
        data=(bytes.fromhex(entry['hex'])if'hex'in entry else
              bytes.fromhex(entry['repeat_hex'])*entry['repeat_count']+bytes.fromhex(entry['suffix_hex']))
        assert len(data)==hi-lo and digest(data)==row['old_SHA256']
        parent[lo:hi]=data
    for at in old['prefix_operand_file_bytes']:parent[at]=0xa7
    parent=bytes(parent);assert digest(parent)==PIN and proposal(parent)[0]==raw
    return parent


if __name__=='__main__':
    _,q=proposal(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
