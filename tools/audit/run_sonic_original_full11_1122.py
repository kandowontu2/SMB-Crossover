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
import compose_sonic_slow_roll_1122 as Slow
import compose_sonic_air_roll_1122 as Air

R,ROM,SHARED=Smoke.R,Smoke.Motion.ROM,Smoke.SHARED
PIN='3466637dc3e75d7768eb6ba3c49af03e548e24a44a027394e3934b22579605cf'
WALL_PIN='8f8d4a13507799fff9de2351b4b1da59d7f0d3bd0eb0675c476d061d7e8c98bc'
SLOW_PIN='fe58e7d9f498ebc2a863027eaf71916574de206d414f4659e661708826c7c77d'
AIR_PIN='c40ca81acc3bb271041c79c2062806e06c93314e097bac5dd48b4586a0ad2bcc'
SPIN_CONTACT_PIN='59e1a591d5ea31d62dafa9332990598b74b5b0852194ef7cc7ad22788196b723'
SPIN_PRIVATE_PASSES={
    'sonic': ('3c2e48641dc04bca3d94f78ccc1d8562b9223e0062cdf2791c00369f053c7d4d',
              '97003aac6624560c660eb51580631c15d958b1119247f75f6e8772f3d9733c81'),
    'super': ('d4ceab5565878691b76789a1699d9a1c93c8581355e0a84e3a3e45d72ca201c4',
              '2952a5effe7b7ebbe6d9d8c8b0842ceb969211568d91ac25a3fc0b80b74ff457'),
}
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
    digest=H(candidate)
    assert H(parent)==BASE and digest in (PIN,WALL_PIN,SLOW_PIN,AIR_PIN,SPIN_CONTACT_PIN),'Exact installed Beans32 and reviewed Sonic candidate'
    expected,receipt=Smoke.proposal(parent)
    assert receipt['declared_spans_disjoint'] and receipt['Beans_preserved']
    if digest in (WALL_PIN,SLOW_PIN,AIR_PIN,SPIN_CONTACT_PIN):
        expected,wall=Wall.proposal(parent,expected)
        receipt=dict(receipt,wall_recovery=wall,cookie=wall['cookie'],candidate_SHA256=WALL_PIN)
    if digest in (SLOW_PIN,AIR_PIN,SPIN_CONTACT_PIN):
        expected,slow=Slow.proposal(expected)
        receipt=dict(receipt,slow_roll=slow,cookie=slow['cookie'],candidate_SHA256=SLOW_PIN)
    if digest in (AIR_PIN,SPIN_CONTACT_PIN):
        expected,air=Air.proposal(expected)
        receipt=dict(receipt,air_roll=air,cookie=air['cookie'],candidate_SHA256=AIR_PIN)
    if digest==SPIN_CONTACT_PIN:
        import compose_sonic_original_contact_1122 as Contact
        expected,contact=Contact.proposal(expected,expected_parent=AIR_PIN)
        receipt=dict(receipt,spin_contact=contact,cookie=contact['cookie'],candidate_SHA256=SPIN_CONTACT_PIN)
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
    for name in ('FloateyNum_Control','Square1SoundQueue'):
        q['ram'][name]=Metadata.W.address(b,name)
    for name in ('FlagpoleCollision','KillPlayer'):
        pc,at=Metadata.W.address(b,name),Metadata.W.location(b,name)
        assert candidate[at:at+32]==parent[at:at+32]
        q['hooks'][name]=dict(pc=pc,tag=((at-16)//8192)|128,offset=at-16,hex=candidate[at:at+32].hex())
    kernel=Smoke.Motion.kernel(candidate)
    for name,pc,tag,size in (('MetaFeet',0xbfd2,3,14),('SceneFeet',0xd2e9,2,12),('MetaDeath',0xd0ec,2,16)):
        code=kernel[pc-0xa000:pc-0xa000+size] if tag==3 else Smoke.Motion.page(candidate,328)[pc-0xd000:pc-0xd000+size]
        q['hooks'][name]=dict(pc=pc,tag=tag,offset=tag*8192+(pc&8191),hex=code.hex())
    if 'slow_roll' in composition:
        pc=Slow.RESUME_PC
        code=Smoke.Motion.page(candidate,Slow.RESUME_PAGE)[pc-0xd800:pc-0xd800+16]
        q['hooks']['ResumeRunning']=dict(pc=pc,tag=2,offset=2*8192+(pc&8191),hex=code.hex())
    if 'spin_contact' in composition:
        pc,tag=0xd37c,2
        code=Smoke.Motion.page(candidate,328)[pc-0xd000:pc-0xd000+16]
        q['hooks']['SpinContact']=dict(pc=pc,tag=tag,offset=tag*8192+(pc&8191),hex=code.hex())
        pc,bank=0x9b04,126
        offset=bank*8192+(pc&8191)
        code=candidate[16+offset:16+offset+16]
        assert code==parent[16+offset:16+offset+16]
        q['hooks']['NativeSpinDefeat']=dict(pc=pc,tag=bank|128,offset=offset,hex=code.hex())
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
    text=once(text,"count(p.name..'_returns')","count(p.name..'_returns')\n if p.name=='SpinContact'then finishSpinContact(p,c)end")
    text=once(text,"count(name..'_entries');pending[#pending+1]={name=name,pc=pc,sp=(sp+2)&255,tag=mapped(pc)}",
              """count(name..'_entries')
 local p={name=name,pc=pc,sp=(sp+2)&255,tag=mapped(pc)}
 if name=='SpinContact'then beginSpinContact(p,c)end
 pending[#pending+1]=p""")
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
    parser.add_argument('--deliver-nightly',action='store_true',
                        help='Install the pinned private two-form pass and replay both forms from Downloads')
    motion=parser.add_mutually_exclusive_group()
    motion.add_argument('--wall-restart',action='store_true',help='Test directional recovery after an airborne roll hits a wall')
    motion.add_argument('--slow-roll',action='store_true',help='Also test returning to running from a slow grounded roll')
    motion.add_argument('--air-roll',action='store_true',help='Also test directional recovery from a slow airborne roll')
    motion.add_argument('--spin-contact',action='store_true',help='Also verify actual native enemy defeat from Sonic spin contact')
    parser.add_argument('--form',choices=(*FORMS,'both'),default='both')
    args=parser.parse_args();assert not(args.run and args.validate)
    assert not args.shared_slot or args.run
    assert not args.deliver_nightly or (args.run and args.spin_contact and args.form=='both')
    parent=ROM.read_bytes();candidate,_=Smoke.proposal(parent)
    if args.wall_restart or args.slow_roll or args.air_roll or args.spin_contact:candidate=Wall.proposal(parent,candidate)[0]
    if args.slow_roll or args.air_roll or args.spin_contact:candidate=Slow.proposal(candidate)[0]
    if args.air_roll or args.spin_contact:candidate=Air.proposal(candidate)[0]
    if args.spin_contact:
        import compose_sonic_original_contact_1122 as Contact
        candidate=Contact.proposal(candidate,expected_parent=AIR_PIN)[0]
        assert H(candidate)==SPIN_CONTACT_PIN,'Requested contact candidate has not been pinned'
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
    launch=target
    installed_guard=None
    delivery_started=False
    delivered=[]
    if args.deliver_nightly:
        from mesen_session_guard_v1 import require_free_workspace
        assert originals[0]==parent,'Exact previous nightly in the shared slot'
        for form in forms:
            assert H(controller(parent,candidate,form).encode())==SPIN_PRIVATE_PASSES[form][0]
        require_free_workspace(R,ROM,allow_interactive=True)
        launch=ROM
    try:
        if args.deliver_nightly:
            assert ROM.read_bytes()==parent and check(ROM)==guard
            delivery_started=True
            ROM.write_bytes(candidate)
            installed_guard=check(ROM)
            assert ROM.read_bytes()==candidate and installed_guard['ROM_sha256']==SPIN_CONTACT_PIN
            assert not installed_guard['matching_patch_files']
        else:
            target.write_bytes(candidate)
        for form in forms:
            script.write_text(controller(parent,candidate,form),encoding='utf-8',newline='\n')
            try:q=run(script,launch,SHARED/'capture',H(candidate),240,extra_env={'SMB_STDOUT_IMAGES':'0'})
            except Exception as error:
                print('SONIC FULL11 RUNNER FAILURE '+json.dumps(dict(form=form,ROM_SHA256=H(candidate),error=repr(error)),separators=(',',':')),flush=True);raise
            report(form,q,validation)
            if args.deliver_nightly:
                assert ROM.read_bytes()==candidate and check(ROM)==installed_guard
                assert q['script_SHA256']==SPIN_PRIVATE_PASSES[form][0]
                delivered.append(dict(form=form,script_SHA256=q['script_SHA256'],
                                      private_receipt_SHA256=SPIN_PRIVATE_PASSES[form][1],
                                      Downloads_receipt_SHA256=q['receipt_SHA256']))
        if args.deliver_nightly:
            target.write_bytes(candidate)
            assert target.read_bytes()==candidate and check(ROM)==installed_guard
            delivery_started=False
        else:
            assert target.read_bytes()==candidate and ROM.read_bytes()==parent
    finally:
        if delivery_started:
            ROM.write_bytes(parent)
        if not args.deliver_nightly or delivery_started:
            target.write_bytes(originals[0])
        script.write_bytes(originals[1])
        assert {p.name for p in SHARED.iterdir()}=={'candidate.nes','controller.lua'}
        assert script.read_bytes()==originals[1]
        if not args.deliver_nightly or delivery_started:
            assert target.read_bytes()==originals[0] and check(ROM)==guard and ROM.read_bytes()==parent
            print('SONIC FULL11 SHARED RESTORED '+json.dumps(dict(files=2,Downloads_SHA256=BASE,patch_guards_before_after=True,no_delivery=True),separators=(',',':')),flush=True)
    if args.deliver_nightly:
        assert target.read_bytes()==ROM.read_bytes()==candidate and check(ROM)==installed_guard
        print('SONIC NIGHTLY DELIVERED '+json.dumps(dict(files=2,backups=0,Downloads_SHA256=SPIN_CONTACT_PIN,
              patch_guards_before_after=True,real_Downloads_launches=delivered),separators=(',',':')),flush=True)


if __name__=='__main__':main()
