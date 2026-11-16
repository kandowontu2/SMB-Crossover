"""Strict leased HotNew118 join over exact owning67, in memory only."""
from functools import lru_cache
from pathlib import Path
import json
import plan_hot_draw_bt_67e_1115 as Plan
import compose_battletoads_carry_current_1115 as Carry

R,ROM,H=Plan.R,Plan.ROM,Plan.H
PIN=Plan.PIN
CANDIDATE='bc5e275d1dd4dabab4b5b2def66f7643ae46aee17a31ab37887528b791594040'
GRANT=R/'docs/qa/allocations/hot-draw-bt118-source-1115.json'
GRANT_SHA='ae2d0689d230314f1cc1adb665cf633efe6bdfbb37910e142a5a3b9fc74ddebf'
PLAN_SHA='0bc656412e3c1a2d32bd4fea10ebb6574ceb81207d0d510a021d5536a35a197d'
CHECK_SHA='65f5256467adfe862d62b131933e2081abbcd8458c8d43b173c89c8ee3f7a221'
FILE,SIZE,BASE=Plan.FILE,Plan.SIZE,Plan.BASE
OLD=bytes.fromhex('08488a489848ad0260c909d009adeb5ff004a200f027ad0260c914b01ec90ad00cade55f2944c940f011ad0260c90e900638e90caad006a201d002a208bdffb48d6c01bd08b58d6d01bd11b58d620168a868aa688d6a01284c5d01ecf0f09ec1e80dfaa2b0a8a8a5a6aaaaa3a1cfcfcfdde0dacdd9fc')
NEW=bytes.fromhex('08488a489848a20cad0260c909d005adeb5fd027ad0260c914b018c90fb011c90ad009ade55f2944c940f007a20dd00baad008a214c921d002a20ebdf1b48d6c01bdfab48d6d01bd03b58d620168a868aa688d6a01284c5d01ecf0269ec1e80dfaa2b0a8b0a5a6aaaaa3a1cfcfd7dde0dacdd9fcd9fc')


@lru_cache(maxsize=1)
def lease():
    assert H(GRANT.read_bytes())==GRANT_SHA
    assert H(Path(Plan.__file__).read_bytes())==PLAN_SHA
    assert H((R/'tools/audit/check_hot_draw_bt_classifier_67e_1115.py').read_bytes())==CHECK_SHA
    q=json.loads(GRANT.read_text());e=q['envelope']
    assert q['owning_parent_SHA256']==PIN and q['owned_bytes']==SIZE==118 and q['changed_bytes']==106
    assert(e['file'],e['bytes'],e['physical_PRG_bank'],e['CPU_half_open'])==(FILE,SIZE,66,[BASE,BASE+SIZE])
    assert bytes.fromhex(e['before'])==OLD and bytes.fromhex(e['after'])==NEW
    assert H(OLD)==e['before_SHA256']==Plan.OLD_SHA
    assert H(NEW)==e['after_SHA256']=='dd8cd717d8bb2f8e97a768e2b346d488060fd80d3d7bf56924cd460ca7a6b869'
    assert q['source_in_memory_composition_and_mounts_authorized']
    assert not any(q[k]for k in('physical_ROM_file_writes_authorized','native_Mesen_authorized','Downloads_delivery_authorized'))
    return q


@lru_cache(maxsize=1)
def reference(parent):
    lease();assert isinstance(parent,bytes)and H(parent)==PIN,'Exact owning67 parent required'
    old=Plan.reference(parent)
    assert parent[FILE:FILE+SIZE]==OLD and Plan.new_code(parent)[0]==NEW
    return old


@lru_cache(maxsize=1)
def proposal(parent):
    reference(parent)
    out=bytearray(parent);out[FILE:FILE+SIZE]=NEW;out=bytes(out)
    differences={i for i,(a,b)in enumerate(zip(parent,out,strict=True))if a!=b}
    owned=set(range(FILE,FILE+SIZE));assert differences<=owned and len(differences)==106
    assert out[:FILE]==parent[:FILE]and out[FILE+SIZE:]==parent[FILE+SIZE:]
    assert H(out[FILE+SIZE:FILE+226])==Plan.FOLLOW_SHA
    if CANDIDATE is not None:assert H(out)==CANDIDATE
    return out,dict(parent_SHA256=PIN,candidate_SHA256=H(out),grant_SHA256=GRANT_SHA,
        file_half_open=[FILE,FILE+SIZE],owned_bytes=118,changed_bytes=106,
        before_SHA256=H(OLD),after_SHA256=H(NEW),all_unowned_bytes_exact=True,
        live_following108_SHA256=H(out[FILE+SIZE:FILE+226]),
        private_RAM_CHR_cookie_carrier_changes=0,source_only=True,
        physical_file_native_delivery_authorized=False,outputs=0)


@lru_cache(maxsize=1)
def inverse(raw):
    lease();assert CANDIDATE is not None and isinstance(raw,bytes)and H(raw)==CANDIDATE,'Exact HotNew118 candidate required'
    assert raw[FILE:FILE+SIZE]==NEW
    parent=bytearray(raw);parent[FILE:FILE+SIZE]=OLD;parent=bytes(parent)
    assert H(parent)==PIN and proposal(parent)[0]==raw
    return parent


def load_current_image():
    raw=ROM.read_bytes()
    if H(raw)==PIN:reference(raw)
    else:inverse(raw)
    return raw


if __name__=='__main__':
    parent=load_current_image();assert H(parent)==PIN
    raw,q=proposal(parent)
    if CANDIDATE is not None:assert inverse(raw)==parent
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
