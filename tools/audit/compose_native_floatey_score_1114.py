"""Exact ten-byte native award-table correction; all artifacts stay in memory."""
from hashlib import sha256
import json
from pathlib import Path

import compose_battletoads_camera_handoff_1114 as Parent

R=Path(__file__).resolve().parents[2]
PIN=Parent.CANDIDATE
CANDIDATE='5715bb7e3c772350a2a7420ec9061eabd948964a8789e5d348c49d3cfb3c57ee'
AT=1034694
OLD=bytes.fromhex('04040404040303030303')
NEW=bytes.fromhex('03030303030202020202')
GRANT=R/'docs/qa/allocations/native-floatey-score-digits-1114.json'
GRANT_SHA='dfda114f8ef6a6ba71bcc87c6690db007c017c2ae21867f5feae6c5742b383c6'


def digest(raw):return sha256(raw).hexdigest()


def allocation():
    data=GRANT.read_bytes();assert digest(data)==GRANT_SHA;q=json.loads(data)
    assert(q['eligible_input_SHA256'],q['PRG_bank'],q['CPU'],q['file'],q['bytes'])==(PIN,126,0x89b6,AT,10)
    assert bytes.fromhex(q['preimage_hex'])==OLD and bytes.fromhex(q['replacement_hex'])==NEW
    return digest(data)


def proposal(raw):
    assert isinstance(raw,bytes)and digest(raw)==PIN,'Expected exact delivered F11'
    grant=allocation();assert raw[AT:AT+11]==OLD+b'\0'
    # The sole indexed table consumer and its preceding amount table stay exact.
    assert raw[AT-11:AT]==bytes((1,2,4,5,8,1,2,4,5,8,0))
    assert raw[AT-82:AT-11].count(bytes.fromhex('beb589'))==1
    image=raw[:AT]+NEW+raw[AT+10:]
    assert digest(image)==CANDIDATE
    assert len(image)==len(raw)and sum(a!=b for a,b in zip(raw,image,strict=True))==10
    assert image[:AT]==raw[:AT]and image[AT+10:]==raw[AT+10:]
    return image,dict(parent_SHA256=PIN,candidate_SHA256=digest(image),allocation_SHA256=grant,
        changed_bytes=10,extra_life_and_all_other_bytes_exact=True,source_qualified=False,
        native_qualified=False,installed=False,outputs=0)


def inverse(raw):
    assert isinstance(raw,bytes)and digest(raw)==CANDIDATE and raw[AT:AT+11]==NEW+b'\0'
    parent=raw[:AT]+OLD+raw[AT+10:]
    assert digest(parent)==PIN and proposal(parent)[0]==raw
    return parent


if __name__=='__main__':
    _,q=proposal(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
