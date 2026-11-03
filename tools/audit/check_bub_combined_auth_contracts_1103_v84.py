"""Qualify exact83 combined constructors/public contracts without a ROM."""
import inspect,json
from pathlib import Path
from types import SimpleNamespace
import check_bub_shared_auth_contracts_1103_v77 as C
import measure_bub_combined_auth_1103_v83 as P

R,O,sha=P.R,P.O,P.sha


def image():
    old,manifest=P.D.image()
    proof=O/'combined-auth-v83-measurement.json';q=json.loads(proof.read_text())
    for rel,value in q['bindings'].items():assert sha(R/rel)==value,rel
    raw=bytearray(old['raw'])
    for row in q['patches']:
        at=16+65*8192+row['CPU']-0xa000
        before,after=bytes.fromhex(row['old_hex']),bytes.fromhex(row['new_hex'])
        assert raw[at:at+len(before)]==before
        raw[at:at+len(after)]=after
    for row in [9,14,34]:
        at=16+65*8192+0x108c+row*3
        assert raw[at:at+3]==bytes.fromhex('4c40a7')
        raw[at:at+3]=bytes([76])+q['labels']['CoNativePrimitive'].to_bytes(2,'little')
    return old,dict(old,raw=bytes(raw)),manifest,q


def adapter():
    old,new,manifest,q=image()
    _,route,private,_,_,_=P.P.P.P.F.C.bundle()
    return old,new,route,private,manifest,manifest['manager_labels'],q['labels'],q['patches'],[]


def main():
    source=inspect.getsource(C.main)
    replacements={
        "'shared-auth-v77-contracts.json'":"'combined-auth-v84-contracts.json'",
        "'shared-auth-v76-funding.json'":"'combined-auth-v83-measurement.json'",
        "'shared-auth-v76.s'":"'combined-auth-v83.s'",
        "'shared-auth-v76.bin'":"'combined-auth-v83.bin'",
        "'shared-auth-v76-extra.bin'":"'combined-auth-v83-extra.bin'",
        "'shared-auth-v76-Sh.bin'":"'combined-auth-v83-Sh.bin'",
        "'shared-auth-v76.lbl'":"'combined-auth-v83.lbl'",
        'source_fit_keeps_cookie_addresses_bytes_and_15B_end_pad=True':'source_fit_keeps_cookie_addresses_bytes_and_8B_end_pad=True',
    }
    for before,after in replacements.items():
        assert before in source,before
        source=source.replace(before,after)
    source=source.replace('Path(__file__),Path(P.__file__),','Path(__file__),Path(P.__file__),Path(LegacyContracts.__file__),')
    source=source.replace("'Pending Prince/DK changes still require exact composition/rebind; no native candidate permission.'",
        "'Exact combined101/83 placement is checked; full ISR/nested and external references remain before root candidate permission.'")
    env=dict(C.__dict__,__file__=__file__,LegacyContracts=C,P=SimpleNamespace(build=adapter,__file__=P.__file__))
    exec(compile(source,__file__,'exec'),env);env['main']()


if __name__=='__main__':main()
