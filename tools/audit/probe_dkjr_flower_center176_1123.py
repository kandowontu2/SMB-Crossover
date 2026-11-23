"""Exactffd708 private Flower lift176 trial, in memory and controller only.

No ROM/asset writer or emulator launcher. The frozen188 proposal remains
reconstructible. This changes only its new row9 oscillator byte and cookie.
"""
import argparse
import inspect
import json
from pathlib import Path
import probe_dkjr_flower_helper_1123 as Previous
import probe_dkjr_flower_top_1123 as Upper

C,Check,Head,H=Previous.C,Previous.Check,Previous.Head,Previous.H
PIN=C.PIN
PRIVATE188=C.CANDIDATE
CANDIDATE='32bfc7365f85e3b36a915b5165c0a228ec4c326e56351f81b47cc060659426a2'
TOP_SOURCE='3fd2d3127e9e3bf5ba7300b195bc8152f5e8d344f897e5d60ab2d9cdc3e778b8'
LEGACY_CONTROLLER='28341004a2a05f3181a6bcd702429576b4f9da8dba0a55469126aec5c1bfa386'


def pins():
    Upper.pins()
    assert H(Path(Upper.__file__).read_bytes())==TOP_SOURCE


def center_location():
    p=C.program()
    pc=p['symbols']['OscillatorY']+9
    rows=list(C.Old.chunks(pc,b'\xbc'))
    assert len(rows)==1 and rows[0][1]==b'\xbc'
    return pc,rows[0][0]


def proposal(parent):
    pins();assert H(parent)==PIN
    old,base=C.proposal(parent)
    pc,at=center_location();assert old[at]==188
    image=bytearray(old);image[at]=176
    cookie_at=C.Old.Head.COOKIE_AT
    cookie=b'\xa7\x28\x01'+bytes.fromhex(H(C.Old.Head.payload(image)))[:13]
    image[cookie_at:cookie_at+16]=cookie
    raw=bytes(image)
    changed={i for i,(a,b) in enumerate(zip(old,raw,strict=True))if a!=b}
    assert changed<={at,*range(cookie_at,cookie_at+16)} and at in changed
    restored=bytearray(raw);restored[at]=188
    restored[cookie_at:cookie_at+16]=old[cookie_at:cookie_at+16]
    assert bytes(restored)==old and H(old)==PRIVATE188
    if CANDIDATE is not None:assert H(raw)==CANDIDATE
    return raw,dict(parent_SHA256=PIN,private188_SHA256=PRIVATE188,candidate_SHA256=H(raw),
        changed_from188=len(changed),center_PC=pc,center_ROM_offset=at,cookie=cookie.hex(),
        helper=dict(character='Donkey Kong Jr.',stage='1-1',left=1264,center=1280,initial_top=192,
            native_ID=37,collision_width=32,oscillator_center=176),
        original14_placements_and_centers_preserved=True,original_jump_and_fall_guard_preserved=True,
        executable_bytes_identical_to188=True,constructor_return=0xd1f0,horizontal_ordinal=10,
        native_qualified=False,outputs=0)


def inverse(raw):
    pins();assert CANDIDATE is not None and H(raw)==CANDIDATE
    pc,at=center_location();assert raw[at]==176
    image=bytearray(raw);image[at]=188
    cookie_at=C.Old.Head.COOKIE_AT
    image[cookie_at:cookie_at+16]=b'\xa7\x28\x01'+bytes.fromhex(H(C.Old.Head.payload(image)))[:13]
    old=bytes(image);assert H(old)==PRIVATE188
    parent=C.inverse(old);assert H(parent)==PIN and proposal(parent)[0]==raw
    return old


def controller(raw,*,staging_limit=1320):
    assert staging_limit in (1304,1320)
    old=inverse(raw);text=Previous.controller(old);original=text;changes=[]
    before_cookie=old[C.Old.Head.COOKIE_AT:C.Old.Head.COOKIE_AT+16].hex()
    after_cookie=raw[C.Old.Head.COOKIE_AT:C.Old.Head.COOKIE_AT+16].hex()
    for before,after in (
        (f'local rom="{PRIVATE188}"',f'local rom="{CANDIDATE}"'),
        (f"assert(rom=='{PRIVATE188}'",f"assert(rom=='{CANDIDATE}'"),
        (f"cookie=='{before_cookie}'",f"cookie=='{after_cookie}'"),
        ('local centers={[1264]=188,','local centers={[1264]=176,'),
        ('top>=146 and top<=160','top>=146 and top<=156')):
        text=Check.Replay.one(text,before,after);changes.append((before,after))
    # Top156 puts the takeoff atY124. The unchanged15px jump reachesY109,
    # giving the normal rowY144 landing atY112 a useful geometric margin.
    restored=text
    for before,after in reversed(changes):restored=Check.Replay.one(restored,after,before)
    assert restored==original and PRIVATE188 not in text
    assert H(text.encode())==LEGACY_CONTROLLER
    if staging_limit!=1304:
        text=Check.Replay.one(text,'assert(player<=1304,','assert(player<=1320,')
        assert H(Check.Replay.one(text,'assert(player<=1320,','assert(player<=1304,').encode())==LEGACY_CONTROLLER
    assert not any(t in text for t in ('emu.write','emu.setState','io.open','takeScreenshot','loadState','saveState'))
    Check.LuaRuntime().compile(text)
    return text


def strict_runner(*,staging_limit=1320):
    """Retain the complete real item observer; strengthen its post-growth gate."""
    pins();source=inspect.getsource(Previous.run);original=source;changes=[]
    def edit(before,after):
        nonlocal source
        source=Check.Replay.one(source,before,after);changes.append((before,after))
    edit('    row_jump=[];row_jump_min=256;prior_motion=None\n',
         '    row_jump=[];row_jump_min=256;prior_motion=None\n    grounded=0;grounded_start=None\n')
    edit('        nonlocal pending,collected,work,returns,post,frozen\n',
         '        nonlocal pending,collected,work,returns,post,frozen,grounded,grounded_start\n')
    edit('            if collected:post+=1\n', '''            if collected:
                post+=1;s=Head.state(m)
                if len(ages)==60 and N.get(m,'GuestPowerupActive')==0 and s['status']==2 and s['source']==s['prior']==1 and N.get(m,'Player_State')==0 and m.ram[2][0x210]==s['y']+15 and s['lives']==2 and s['hurt']==0:
                    grounded+=1
                    if grounded_start is None:grounded_start=dict(return_number=returns,hero=s)
                else:grounded=0;grounded_start=None
''')
    edit("            if post>=25 and s['source']==s['prior']==1 and N.get(m,'Player_State')==0:\n",
         "            if post>=25 and grounded>=25 and s['source']==s['prior']==1 and N.get(m,'Player_State')==0:\n")
    edit('        completed_source_returns=returns,post_collection_source_returns=post,events=events,recent=recent,\n',
         '        completed_source_returns=returns,post_collection_source_returns=post,grounded_source_returns=grounded,grounded_start=grounded_start,events=events,recent=recent,\n')
    restored=source
    for before,after in reversed(changes):restored=Check.Replay.one(restored,after,before)
    assert restored==original
    namespace=dict(Previous.__dict__,controller=lambda raw:controller(raw,staging_limit=staging_limit))
    exec(compile(source,str(Path(__file__))+'::<strict-original-observer>','exec'),namespace)
    return namespace['run']


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--compose-only',action='store_true')
    ap.add_argument('--old-stage-limit',action='store_true');args=ap.parse_args()
    parent=C.Old.M.ROM.read_bytes();raw,q=proposal(parent)
    print('DK FLOWER176 BINDING '+json.dumps(q,separators=(',',':')),flush=True)
    if args.compose_only:return
    assert inverse(raw)==C.proposal(parent)[0]
    limit=1304 if args.old_stage_limit else 1320
    result=strict_runner(staging_limit=limit)(raw)
    result.update(source_SHA256=H(Path(__file__).read_bytes()),observer_grounded_after_all60=True,
        diagnostic_only=False,ordinary_menu_and_controller_only=True,staging_limit=limit)
    print('DK FLOWER176 '+json.dumps(result,separators=(',',':')),flush=True)
    print('RECEIPT '+H(json.dumps(result,sort_keys=True,separators=(',',':')).encode()),flush=True)


if __name__=='__main__':main()
