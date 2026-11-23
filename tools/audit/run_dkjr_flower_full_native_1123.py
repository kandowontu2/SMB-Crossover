"""Exact32bf full-stage binding of the retained qualified DK Jr policy.

Default is compile only. Root may use --run in the existing shared two-file
slot. No new input maneuver, source engine change or Downloads write.
"""
import argparse
import json
from pathlib import Path

import run_dkjr_flower_native_1123 as Flower
import run_dkjr_mushroom_native_1123 as Retained

S,H=Flower.Source,Flower.H
CANDIDATE=S.CANDIDATE
FLOWER_FACTORY='adc1832d2c9fc9d4b44d1779d9f604a853e25585a53e9292e9a5aedbb4d2281a'
QUALIFIED_POLICY='07c051dfc544c1b82004672d22d935a6c1f1b0d0c1d64b3e0428fdf7781d30a0'
QUALIFIED_RECEIPT='fe1de52fb1b4d6a1f0632734421801fd77c84a04df8b3f74ba21a2ed1f048d06'
FULL_SHA='9779651532d7679769f8cd63b33d798ebcb8efd986d7d88a59a51df1789461f9'


def controller(raw):
    assert H(Path(Flower.__file__).read_bytes())==FLOWER_FACTORY
    assert H(Path(S.__file__).read_bytes())==Flower.SOURCE_SHA and H(raw)==CANDIDATE
    private188=S.inverse(raw);parent=S.C.inverse(private188)
    assert H(parent)==S.PIN==Retained.Fixed.CANDIDATE
    # This retains the already-qualified riser3 backward preparation and
    # the25 actual grounded original-work + native-wrapper1-2 endpoints.
    base=Retained.controller(Retained.Fixed,parent,parent,'full').decode()
    assert H(base.encode())==QUALIFIED_POLICY
    before_cookie=parent[S.C.Old.Head.COOKIE_AT:S.C.Old.Head.COOKIE_AT+16].hex()
    after_cookie=raw[S.C.Old.Head.COOKIE_AT:S.C.Old.Head.COOKIE_AT+16].hex()
    text=base;changes=[]
    for before,after in (
        (f'local rom="{S.PIN}"',f'local rom="{CANDIDATE}"'),
        (f"assert(rom=='{S.PIN}'",f"assert(rom=='{CANDIDATE}'"),
        (f"cookie=='{before_cookie}'",f"cookie=='{after_cookie}'"),
        ('local centers={','local centers={[1264]=176,')):
        text=S.Check.Replay.one(text,before,after);changes.append((before,after))
    marker='ram(2,0x8fd)~=9';assert text.count(marker)==2
    text=text.replace(marker,'ram(2,0x8fd)~=10')
    restored=text.replace('ram(2,0x8fd)~=10',marker)
    for before,after in reversed(changes):restored=S.Check.Replay.one(restored,after,before)
    assert restored==base and H(restored.encode())==QUALIFIED_POLICY
    assert 'if finalRiser>=3 and finalRiser<=6 then'in text
    assert text.count('local centers={[1264]=176,')==1
    assert not any(v in text for v in ('emu.write','emu.setState','io.open','takeScreenshot','loadState','saveState'))
    S.Check.LuaRuntime().compile(text)
    if FULL_SHA is not None:assert H(text.encode())==FULL_SHA
    return text


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',action='store_true');args=ap.parse_args()
    installed=Flower.ROM.read_bytes();guard=Flower.check(Flower.ROM)
    parent,recovery=Flower.parent_image(installed)
    with Flower.recipe_cache():
        image,layout=S.proposal(parent);program=controller(image).encode()
    print('DK FLOWER FULL BINDING '+json.dumps(dict(ROM_SHA256=CANDIDATE,controller_SHA256=H(program),
        qualified_policy=QUALIFIED_POLICY,qualified_receipt=QUALIFIED_RECEIPT,
        qualified_policy_recovered_exactly=True,changes='ROM,cookie,new1264 observation,horizontal ordinal only',
        parent_recovery=recovery,layout=layout,factory_SHA256=H(Path(__file__).read_bytes()),outputs=0),separators=(',',':')),flush=True)
    if not args.run:return 0
    target,script=Flower.OUT/'candidate.nes',Flower.OUT/'controller.lua'
    assert set(Flower.OUT.iterdir())=={target,script} and not guard['matching_patch_files']
    previous_target,previous_script=target.read_bytes(),script.read_bytes()
    assert H(previous_target)in(guard['ROM_sha256'],S.PIN)
    Flower.require_free_workspace(Flower.R,target,allow_interactive=True)
    try:
        target.write_bytes(image);script.write_bytes(program)
        private=Flower.check(target)
        assert private['ROM_sha256']==CANDIDATE and not private['matching_patch_files']
        result=Flower.run(script,target,Flower.OUT/'capture',CANDIDATE,360,long_no_capture=True)
        assert result['script_SHA256']==H(program) and result['outputs_written']==0 and not result['images']
        assert target.read_bytes()==image and script.read_bytes()==program and Flower.check(target)==private
        print('DK FLOWER FULL NATIVE '+json.dumps(result,separators=(',',':')),flush=True)
        return int(not result['passed'])
    finally:
        script.write_bytes(previous_script);target.write_bytes(previous_target)
        assert set(Flower.OUT.iterdir())=={target,script} and target.read_bytes()==previous_target and script.read_bytes()==previous_script
        assert Flower.ROM.read_bytes()==installed and Flower.check(Flower.ROM)==guard


if __name__=='__main__':raise SystemExit(main())
