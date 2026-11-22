"""Strict combined346 full1-1 controller; default source-only, Root-only --run.

The native opening-smoke sources stay frozen and their verified lifecycle is
reused in memory. Shared-slot replacement/restoration belongs only to --run.
"""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse
import contextlib
import io
import json
import re

import run_sonic_original_motion_smoke_1122 as Smoke
import compose_sonic_roll_wall_restart_1122 as Wall

R,ROM,SHARED=Smoke.R,Smoke.Motion.ROM,Smoke.SHARED
PIN='3466637dc3e75d7768eb6ba3c49af03e548e24a44a027394e3934b22579605cf'
WALL_PIN='8f8d4a13507799fff9de2351b4b1da59d7f0d3bd0eb0675c476d061d7e8c98bc'
BASE='32eaf1786695d7ac1e69eb4957cc76dee011664e642710d02acc7ae624ca3ad1'
SMOKE_RUNNER_SHA='d5e2acc8e74e25d5f8daa0d4087f1307daaf400687583e8d816646b2ed2624f8'
SMOKE_LUA_SHA='80a278b2288f5a089f94d5ff193823a754384c1cfe015921f8fb983cc1184389'
STAGE=R/'tools/playthroughs/sonic_original_full_stage_stdout_1110.lua'
STAGE_SHA='2c2ee3f821affcff8c8748a35918fd7c9531760332a3e6d0b5d392f4154fa4ee'
LUA=R/'tools/playthroughs/sonic_original_full11_1122.lua'
FORMS=('sonic','super')


def H(data): return sha256(data).hexdigest()


def strict(parent,candidate):
    assert H(Path(Smoke.__file__).read_bytes())==SMOKE_RUNNER_SHA
    assert H(Smoke.LUA.read_bytes())==SMOKE_LUA_SHA
    assert H(parent)==BASE and H(candidate) in (PIN,WALL_PIN),'Exact installed Beans32 and reviewed Sonic candidate'
    expected,receipt=Smoke.proposal(parent)
    assert receipt['declared_spans_disjoint'] and receipt['Beans_preserved']
    if H(candidate)==WALL_PIN:
        expected,wall=Wall.proposal(parent,expected)
        receipt=dict(receipt,wall_recovery=wall,cookie=wall['cookie'],candidate_SHA256=WALL_PIN)
    assert candidate==expected
    return receipt


@lru_cache(maxsize=2)
def bindings(parent,candidate,form):
    composition=strict(parent,candidate);assert form in FORMS
    baseline=Smoke.proposal(parent)[0]
    q=deepcopy(Smoke.bindings(parent,baseline,form))
    q.update(sha=H(candidate),cookie=composition['cookie'])
    if candidate!=baseline:
        hook=q['hooks']['SonicHostConstruct'];start=hook['pc']-0xa000
        hook['hex']=Smoke.Motion.kernel(candidate)[start:start+32].hex()
    import current_sonic_stock_binding_1122 as Metadata
    a6=Smoke.reference(parent)
    b=Metadata.Sonic.bindings(Metadata.reference(a6))['bundle']
    for name in ('FlagpoleCollision','KillPlayer'):
        pc,at=Metadata.W.address(b,name),Metadata.W.location(b,name)
        assert candidate[at:at+32]==parent[at:at+32]
        q['hooks'][name]=dict(pc=pc,tag=((at-16)//8192)|128,offset=at-16,hex=candidate[at:at+32].hex())
    kernel=Smoke.Motion.kernel(candidate)
    for name,pc,tag,size in (('MetaFeet',0xbfd2,3,14),('SceneFeet',0xd2e9,2,12),('MetaDeath',0xd0ec,2,16)):
        code=kernel[pc-0xa000:pc-0xa000+size] if tag==3 else Smoke.Motion.page(candidate,328)[pc-0xd000:pc-0xd000+size]
        q['hooks'][name]=dict(pc=pc,tag=tag,offset=tag*8192+(pc&8191),hex=code.hex())
    q.update(run_kind='full11',fatal={'KillPlayer':True,'MetaDeath':True},
             proven_sensor_source_SHA256=STAGE_SHA)
    return q


def once(text,before,after):
    assert text.count(before)==1,(before,text.count(before))
    return text.replace(before,after,1)


def body():
    assert H(Smoke.LUA.read_bytes())==SMOKE_LUA_SHA and H(STAGE.read_bytes())==STAGE_SHA
    text=Smoke.LUA.read_text(encoding='utf-8')
    pieces=LUA.read_text(encoding='utf-8').split('-- FULL_ROUTE_FINISH\n')
    declarations,pieces=pieces
    finish,functions=pieces.split('-- FULL_ROUTE_FUNCTIONS\n')
    old=STAGE.read_text(encoding='utf-8')
    sensors=old[old.index('local function solid('):old.index('local function drive()')]
    functions=once(functions,'FULL_ROUTE_SENSORS',sensors)
    text=once(text,"local jumpEvents,releaseReturns=0,0",'local jumpEvents,releaseReturns=0,0\n'+declarations)
    text=once(text,"local function r(n)return emu.read(assert(F[n],n),emu.memType.nesDebug)end",
              "local function r(n,i)return emu.read(assert(F[n],n)+(i or 0),emu.memType.nesDebug)end")
    text=once(text,"engine=r('GameEngineSubroutine'),native_state=r('Player_State')}",
              """engine=r('GameEngineSubroutine'),native_state=r('Player_State'),state=r('Player_State'),
  mode=r('OperMode'),task=r('OperMode_Task'),world=r('WorldNumber'),level=r('LevelNumber'),
  area=r('AreaAddrsLOffset'),area_type=r('AreaType'),source_flags=w(0xc030),
  selected=r('SelectedCharacter'),alternate=emu.read(0x5ffe,emu.memType.nesDebug),
  camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')}""")
    start,end=text.index('local function finish('),text.index('local function guard(')
    text=text[:start]+finish+'\n'+text[end:]
    start,end=text.index('local function grounded('),text.index('local function returned(')
    text=text[:start]+functions+'\n'+text[end:]
    text=once(text,'motor=motor+1;if game then drive(state())end','motor=motor+1')
    text=once(text,"if name~='GameLoop'and(not armed or not identity())then return end",
              "if name~='GameLoop'and(not armed or not identity())then return end\n if C.fatal[name]and game then error('Actual native death entry '..name)end")
    text=once(text,"frame<=6000,'Bounded physical motion frames'","frame<=16000,'Bounded physical full-route frames'")
    text=once(text,"'Exact private motion candidate'","'Exact authenticated full-route candidate'")
    return text


@lru_cache(maxsize=2)
def controller(parent,candidate,form):
    return 'local SONIC_CONFIG='+Smoke.value(bindings(parent,candidate,form))+'\n'+body()


def pickup_bindings(parent,candidate,form,item):
    """Bind an item replay to the same authenticated motion candidate."""
    kinds={'mushroom':0,'flower':1,'star':2,'life':3};assert item in kinds
    q=deepcopy(bindings(parent,candidate,form))
    import current_sonic_stock_binding_1122 as Metadata
    inherited=Metadata.bindings(Smoke.reference(parent),form,'star' if item=='star' else 'flower')
    for name,address in inherited['ram'].items():
        assert q['ram'].get(name,address)==address, name
        q['ram'][name]=address
    for name,h in inherited['hooks'].items():
        if name in q['hooks']:continue
        h=deepcopy(h);pc,tag=h['pc'],h['tag'];size=len(bytes.fromhex(h['hex']))
        if tag>=128:
            h['hex']=candidate[16+h['offset']:16+h['offset']+size].hex()
            bank=tag&127;h['bank_SHA256']=H(candidate[16+bank*8192:16+(bank+1)*8192])
        elif tag==3:h['hex']=Smoke.Motion.kernel(candidate)[pc-0xa000:pc-0xa000+size].hex()
        else:
            carriers=((0xd000,328),(0xd400,333),(0xd800,334))
            start,page=next((start,page)for start,page in carriers if start<=pc<start+1024)
            h['hex']=Smoke.Motion.page(candidate,page)[pc-start:pc-start+size].hex()
        q['hooks'][name]=h
    q.update(run_kind='pickup-binding',item=item,stockKind=kinds[item],
             new_motion_pickup_policy_native_pending=True)
    return q


def report(form,result,validation):
    print('SONIC FULL11 '+json.dumps(dict(form=form,script_SHA256=result['script_SHA256'],
          receipt_SHA256=result['receipt_SHA256'],validation=validation,receipt=result['receipt']),separators=(',',':')),flush=True)
    assert result['passed'] and result['outputs_written']==0 and not result['images'],result['receipt']


def validate(parent,candidate):
    from check_ff_stdout_controller_source_1110 import LuaRuntime,DLL,DLL_SHA
    assert H(DLL.read_bytes())==DLL_SHA
    source=body();executable='\n'.join(line.split('--',1)[0] for line in source.splitlines())
    assert not re.search(r'\bio\s*[.:]|\bemu\s*[.:]\s*(?:write|save|load)|os\s*\.\s*(?:execute|remove|rename)',executable)
    required=set(re.findall(r"r\('([A-Za-z0-9_]+)'",source))
    for lo,hi in re.findall(r"pos\('([A-Za-z0-9_]+)','([A-Za-z0-9_]+)'",source):required.update((lo,hi))
    rt=LuaRuntime();forms=[]
    for form in FORMS:
        q=bindings(parent,candidate,form);assert required<=set(q['ram'])
        text=controller(parent,candidate,form);rt.compile(text)
        forms.append(dict(form=form,select=q['select'],script_SHA256=H(text.encode()),bytes=len(text.encode()),
                          hooks={n:dict(pc=h['pc'],tag=h['tag'],bytes=len(bytes.fromhex(h['hex'])))for n,h in q['hooks'].items()}))
    stream=io.StringIO()
    with contextlib.redirect_stdout(stream):
        try:report('source-fixture',dict(passed=False,outputs_written=0,images=[],script_SHA256='fixture',receipt_SHA256='fixture',receipt={'reason':'failure diagnostic fixture'}),{})
        except AssertionError:pass
        else:raise AssertionError('Native failure accepted')
    assert 'failure diagnostic fixture'in stream.getvalue()
    return dict(passed=True,source_only=True,ROM_SHA256=H(candidate),base_SHA256=BASE,forms=forms,
                Lua_fragment_SHA256=H(LUA.read_bytes()),expanded_Lua_body_SHA256=H(source.encode()),
                runner_SHA256=H(Path(__file__).read_bytes()),retained_sensor_SHA256=STAGE_SHA,
                frozen_smoke_runner_SHA256=SMOKE_RUNNER_SHA,frozen_smoke_Lua_SHA256=SMOKE_LUA_SHA,
                failure_diagnostic_before_assertion=True,
                outputs=0,native_Mesen=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true')
    parser.add_argument('--validate',action='store_true')
    parser.add_argument('--shared-slot',action='store_true')
    parser.add_argument('--wall-restart',action='store_true',help='Test directional recovery after an airborne roll hits a wall')
    parser.add_argument('--form',choices=(*FORMS,'both'),default='both')
    args=parser.parse_args();assert not(args.run and args.validate)
    assert not args.shared_slot or args.run
    parent=ROM.read_bytes();candidate,_=Smoke.proposal(parent)
    if args.wall_restart:candidate=Wall.proposal(parent,candidate)[0]
    strict(parent,candidate)
    if not args.run:
        def deny(*a,**kw):raise AssertionError('Full-route source validation attempted output/process')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=validate(parent,candidate)
        print('RESULT '+json.dumps(q,separators=(',',':')),flush=True);return
    assert args.shared_slot,'Native Root runner requires the existing two-file shared slot'
    import build_storage_guard_v1 as Storage
    from nightly_patch_guard_v1 import check
    from run_stdout_mesen_1110 import run
    Storage.preflight(private_root=SHARED,reserved_files=0,fresh=True)
    validation=validate(parent,candidate)
    assert {p.name for p in SHARED.iterdir()}=={'candidate.nes','controller.lua'}
    guard=check(ROM);assert guard['ROM_sha256']==BASE and ROM.read_bytes()==parent
    target,script=SHARED/'candidate.nes',SHARED/'controller.lua'
    originals=target.read_bytes(),script.read_bytes()
    forms=FORMS if args.form=='both' else (args.form,)
    try:
        target.write_bytes(candidate)
        for form in forms:
            script.write_text(controller(parent,candidate,form),encoding='utf-8',newline='\n')
            try:q=run(script,target,SHARED/'capture',H(candidate),240,extra_env={'SMB_STDOUT_IMAGES':'0'})
            except Exception as error:
                print('SONIC FULL11 RUNNER FAILURE '+json.dumps(dict(form=form,ROM_SHA256=H(candidate),error=repr(error)),separators=(',',':')),flush=True);raise
            report(form,q,validation)
        assert target.read_bytes()==candidate and ROM.read_bytes()==parent
    finally:
        target.write_bytes(originals[0]);script.write_bytes(originals[1])
        assert (target.read_bytes(),script.read_bytes())==originals
        assert {p.name for p in SHARED.iterdir()}=={'candidate.nes','controller.lua'}
        assert check(ROM)==guard and ROM.read_bytes()==parent
        print('SONIC FULL11 SHARED RESTORED '+json.dumps(dict(files=2,Downloads_SHA256=BASE,patch_guards_before_after=True,no_delivery=True),separators=(',',':')),flush=True)


if __name__=='__main__':main()
