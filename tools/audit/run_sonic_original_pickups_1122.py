"""Independent input-only baseline346 native pickups; default source-only.

Mushroom is the first ready native case. Star/Flower/hidden1UP retain their
pinned ordinary routes; reaching later obstacles remains a real runtime gate.
No full-route receipt is required to construct or run these independent cases.
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

R,ROM,SHARED=Smoke.R,Smoke.Motion.ROM,Smoke.SHARED
PIN='3466637dc3e75d7768eb6ba3c49af03e548e24a44a027394e3934b22579605cf'
RESTART_PIN='8f8d4a13507799fff9de2351b4b1da59d7f0d3bd0eb0675c476d061d7e8c98bc'
SLOW_PIN='fe58e7d9f498ebc2a863027eaf71916574de206d414f4659e661708826c7c77d'
RESTART_SOURCE_SHA='539a4a4156375b86e901ccb211a922e5bcb157532f7dda3e4a3aa3f54efc9197'
BASE='32eaf1786695d7ac1e69eb4957cc76dee011664e642710d02acc7ae624ca3ad1'
SMOKE_SHA='d5e2acc8e74e25d5f8daa0d4087f1307daaf400687583e8d816646b2ed2624f8'
SMOKE_LUA_SHA='80a278b2288f5a089f94d5ff193823a754384c1cfe015921f8fb983cc1184389'
LUA=R/'tools/playthroughs/sonic_original_pickup_observer_1122.lua'
FORMS=('sonic','super')
ITEMS={'mushroom':0,'flower':1,'star':2,'life':3}
PINS={
 'tools/audit/run_sonic_natural_stock_1122.py':'2c31487a07d13047204cc6853e54904a6565848e17fdd0daa3068f47f470c038',
 'tools/playthroughs/sonic_natural_stock_1122.lua':'d88a9fe4500dae8c481eef32bf0d16bbb596ec3946ef55c4a5ce9acc859e9811',
 'tools/audit/replay_sonic_ceiling_life_resources_a2d9_1116.py':'09b1f486b1650847eaf469275e6068be78961cdd0e8ebf530f1baf6930909ff5',
 'tools/audit/sonic_ceiling_life_right_policy_a2d9_1116.py':'88a4e2f5a3ac55bec9c5b18fc87e67d81385c953d7ff443f0654dbfceebb46a8',
 'tools/audit/replay_sonic_hidden_life_f7c9_1116.py':'3d8bd46b6e35507986dc1ee1180e597b3663a4f6cc76be56320bbdd1691e1ad5',
 'tools/audit/sonic_natural_stock_policy_1327_1116.py':'e1891238461f31a7211460f1eb232f9a868769f8404760e87f2e7698ef9fd73b',
}


def H(data):return sha256(data).hexdigest()


@lru_cache(maxsize=3)
def candidate(parent,wall_restart=False,slow_roll=False):
    assert not slow_roll or wall_restart
    assert H(Path(Smoke.__file__).read_bytes())==SMOKE_SHA and H(Smoke.LUA.read_bytes())==SMOKE_LUA_SHA
    assert H(parent)==BASE,'Exact delivered Beans32 base only'
    raw,receipt=Smoke.proposal(parent)
    assert H(raw)==PIN and receipt['Beans_preserved'] and receipt['whole_length_same_index_delta']
    if wall_restart:
        import compose_sonic_roll_wall_restart_1122 as Restart
        assert H(Path(Restart.__file__).read_bytes())==RESTART_SOURCE_SHA
        previous=raw;raw,repair=Restart.proposal(parent,previous)
        assert H(raw)==RESTART_PIN and len(raw)==len(previous)==len(parent)
        owned={i for at,size in repair['owned_spans']for i in range(at,at+size)}
        changed={i for i,(a,b)in enumerate(zip(previous,raw,strict=True))if a!=b}
        assert changed<=owned
        assert all(raw[i]==previous[i]for i in range(len(raw))if i not in owned)
        complete_delta={i for i,(a,b)in enumerate(zip(parent,raw,strict=True))if a!=b}
        original_owned={i for r in receipt['spans']for i in range(r['file'],r['file']+r['bytes'])}
        original_owned.update(range(Smoke.Motion.COOKIE_AT,Smoke.Motion.COOKIE_AT+16))
        assert complete_delta<=original_owned
        receipt=dict(receipt,candidate_SHA256=RESTART_PIN,cookie=repair['cookie'],wall_restart=repair,
                     wall_restart_source_SHA256=RESTART_SOURCE_SHA,
                     baseline_component_changed_bytes=receipt['changed_bytes'],changed_bytes=len(complete_delta))
    if slow_roll:
        import compose_sonic_slow_roll_1122 as Slow
        raw,repair=Slow.proposal(raw)
        assert H(raw)==SLOW_PIN
        receipt=dict(receipt,candidate_SHA256=SLOW_PIN,cookie=repair['cookie'],slow_roll=repair)
    return raw,receipt


def once(text,before,after):
    assert text.count(before)==1,(before,text.count(before))
    return text.replace(before,after,1)


def loaded(raw,pc):
    if 0xa000<=pc<0xc000:return Smoke.Motion.kernel(raw)[pc-0xa000:]
    for start,page in ((0xd000,328),(0xd400,333),(0xd800,334)):
        if start<=pc<start+1024:return Smoke.Motion.page(raw,page)[pc-start:]
    raise AssertionError(('Outside combined source domain',hex(pc)))


@lru_cache(maxsize=16)
def bindings(parent,raw,form,item,wall_restart=False,slow_roll=False):
    expected,receipt=candidate(parent,wall_restart,slow_roll);assert raw==expected and form in FORMS and item in ITEMS
    import current_sonic_stock_binding_1122 as Metadata
    inherited=Metadata.bindings(Smoke.reference(parent),form,'star' if item=='star' else 'flower')
    q={k:deepcopy(inherited[k])for k in ('form','select','name','CHR','ram')}
    names=('GameLoop','SonicHostMain','OriginalFrame','PlayerHeadCollision','HandlePowerUpCollision')
    if item=='life':names+=('Selector','Helper','LifeINC','CeilingStore','TimerCancel')
    else:names+=('GuestPowerupUpdate',)
    hooks={}
    for name in names:
        h=deepcopy(inherited['hooks'][name]);pc,tag=h['pc'],h['tag'];size=len(bytes.fromhex(h['hex']))
        if tag>=128:
            at=16+(tag&127)*8192+(pc&8191);h['hex']=raw[at:at+size].hex()
            bank=tag&127;h['bank_SHA256']=H(raw[16+bank*8192:16+(bank+1)*8192])
        else:h['hex']=loaded(raw,pc)[:size].hex()
        h['offset']=(tag&127)*8192+(pc&8191);hooks[name]=h
    q.update(sha=H(raw),cookie=receipt['cookie'],hooks=hooks,item=item,stockKind=ITEMS[item],run_kind='pickup',
             actual_base_SHA256=BASE,metadata_reference_a6_SHA256=Smoke.Motion.PIN,
             independent_of_full_route=True,legacy_ground_bit8_replaced_by_actual_bit7=True,
             accepted_motor_clock=True,wall_restart=wall_restart,baseline_later_tall_pipe_gate_remains=not wall_restart)
    return q


def pinned_sources():
    for path,pin in PINS.items():assert H((R/path).read_bytes())==pin,'Changed pinned pickup source '+path


def common(body,item):
    body=once(body,"saved=r('SavedJoypadBits'),source_input=w(0xc0a8)",
              "saved=r('SavedJoypadBits'),source_input=w(0xc0a8),previous_pad=w(0xc097),charge=w(0xc098),drop=w(0xc351),shoes=w(0xc090),width=w(0xc041),height=w(0xc042),sx=signed(0xc070),sy=signed(0xc073),guest_active=r('GuestPowerupActive'),guest_age=r('GuestPowerupAge'),guest_target=r('GuestPowerupTarget')")
    body=once(body,'local function actor(i)',LUA.read_text(encoding='utf-8')+'\nlocal function actor(i)')
    body=once(body,'physical_frames=frame,input_polls=polls,Main=main,route_Main=updates,motor=motor,counts=counts,pending=#pending,',
              "run_kind='pickup',item=C.item,physical_frames=frame,input_polls=polls,Main=main,route_Main=updates,motor=motor,counts=counts,pending=#pending,guest_proof=guestProof,private_resource_observations=pickupResources,adaptation={ground_bit=128,accepted_motor_clock=true,old_Suppress_bit8_assertion_removed=true,no_ROM_change=true},")
    # Bit8 is the retired SMS latch; bit7 is actual current ground state.
    body=body.replace('s.source_flags&8~=0','s.source_flags&128~=0')
    assert 's.source_flags&8~=0'not in body
    if item!='life':
        body=once(body,"local jumpReady=ground and s.motor-launch>25",
                  "local jumpReady=ground and s.motor-launch>25 and s.previous_pad&128==0 and s.source_input&128==0")
        body=once(body,"elseif p.name=='HandlePowerUpCollision'and p.actor", "elseif p.name=='GuestPowerupUpdate'then guestReturned(p)\n elseif p.name=='HandlePowerUpCollision'and p.actor")
        body=once(body,"local p={name=name,pc=pc,sp=(sp+2)&255,tag=mapped(pc)}",
                  "local p={name=name,pc=pc,sp=(sp+2)&255,tag=mapped(pc)}\n if name=='GuestPowerupUpdate'then p.guestBefore=state()end")
        body=once(body," phase='reward'", " collections[index].guest_start=guestProof.returns\n collections[index].private_resources=collectorResource(p.before,state())\n phase='reward'")
        body=once(body,'   collections[index].credit=awarded',
                  "   if i.kind<2 then assert(guestProof.returns-collections[index].guest_start==60,'Exactly60 actual returned native transformation updates')end\n   collections[index].credit=awarded")
        body=once(body," pad=0\n if phase=='reward' then", " if s.engine~=8 or phase=='reward'then pad=0 end\n if phase=='reward' then")
        body=once(body,' if s.engine==8 then pad=stockInput(s,a,i.x) end',
                  ' if s.engine==8 and motor>acceptedInputMotor then acceptedInputMotor=motor;pad=stockInput(s,a,i.x)end')
        if item=='mushroom':
            body=once(body,"local items=C.item=='star' and {{kind=2,x=1616}} or {{kind=0,x=336},{kind=1,x=1248}}",
                      "local items={{kind=0,x=336}}")
    else:
        body=once(body,"w(0xc058)==0 and s.vy>=0 and s.source_flags&8==0,'Original Suppress/gravity after nativeceiling'",
                  "w(0xc058)==0 and s.vy>=0,'Actual ceiling canceled new held-rise latch'")
        body=once(body,"pad=policy:decide(s,aa);assert(type(pad)=='number'and pad>=0 and pad<=255)",
                  "if motor>acceptedInputMotor then acceptedInputMotor=motor;pad=policy:decide(s,aa)end;assert(type(pad)=='number'and pad>=0 and pad<=255)")
        body=once(body,"  target={item=a,before=p.before,after=state(),popup=11,cue32=sounds[32]-p.cue32};collections[1]=target",
                  "  target={item=a,before=p.before,after=state(),popup=11,cue32=sounds[32]-p.cue32};target.private_resources=collectorResource(p.before,state());collections[1]=target") if "popup=11,cue32=sounds[32]-p.cue32"in body else once(body,
                  "target={item=a,before=p.before,after=state(),popup=11,boxes=p.boxes};collections[1]=target",
                  "target={item=a,before=p.before,after=state(),popup=11,boxes=p.boxes};target.private_resources=collectorResource(p.before,state());collections[1]=target")
    assert 's.source_flags&8==0'not in body
    return body


@lru_cache(maxsize=16)
def controller(parent,raw,form,item,wall_restart=False,slow_roll=False):
    pinned_sources();q=bindings(parent,raw,form,item,wall_restart,slow_roll)
    if item=='life':
        import replay_sonic_ceiling_life_resources_a2d9_1116 as Life
        body=Life.body().replace('POLICY_TEXT',Life.Frozen.Policy.text())
    else:
        import run_sonic_natural_stock_1122 as Stock
        old=Stock.controller(Smoke.reference(parent),form,'star' if item=='star' else 'flower')
        body=old.split('\n',1)[1]
    body=common(body,item)
    return 'local SONIC_CONFIG='+Smoke.value(q)+'\n'+body


def report(form,item,result,validation):
    print('SONIC PICKUP '+json.dumps(dict(form=form,item=item,script_SHA256=result['script_SHA256'],
          receipt_SHA256=result['receipt_SHA256'],validation=validation,receipt=result['receipt']),separators=(',',':')),flush=True)
    assert result['passed']and result['outputs_written']==0 and not result['images'],result['receipt']


def validate(parent,raw,wall_restart=False,slow_roll=False):
    from check_ff_stdout_controller_source_1110 import LuaRuntime,DLL,DLL_SHA
    assert H(DLL.read_bytes())==DLL_SHA
    rt=LuaRuntime();rows=[]
    for item in ITEMS:
        for form in FORMS:
            q=bindings(parent,raw,form,item,wall_restart,slow_roll);text=controller(parent,raw,form,item,wall_restart,slow_roll)
            executable='\n'.join(line.split('--',1)[0]for line in text.splitlines())
            assert not re.search(r'\bio\s*[.:]|\bemu\s*[.:]\s*(?:write|save|load)|os\s*\.\s*(?:execute|remove|rename)',executable)
            assert 's.source_flags&8~=0'not in text and 's.source_flags&8==0'not in text
            required=set(re.findall(r"r\('([A-Za-z0-9_]+)'",text));assert required<=set(q['ram'])
            rt.compile(text)
            rows.append(dict(item=item,form=form,select=q['select'],script_SHA256=H(text.encode()),bytes=len(text.encode())))
    stream=io.StringIO()
    with contextlib.redirect_stdout(stream):
        try:report('fixture','fixture',dict(passed=False,outputs_written=0,images=[],script_SHA256='fixture',receipt_SHA256='fixture',receipt={'reason':'failure order fixture'}),{})
        except AssertionError:pass
        else:raise AssertionError('Pickup failure accepted')
    assert 'failure order fixture'in stream.getvalue()
    return dict(passed=True,source_only=True,ROM_SHA256=H(raw),base_SHA256=BASE,wall_restart=wall_restart,slow_roll=slow_roll,cases=rows,
                runner_SHA256=H(Path(__file__).read_bytes()),Lua_additions_SHA256=H(LUA.read_bytes()),pinned_sources=PINS,
                actual_ground_bit=128,accepted_motor_input_clock=True,failure_diagnostic_before_assertion=True,
                no_full_route_prerequisite=True,baseline_tall_pipe_limitation_not_bypassed=not wall_restart,
                wall_restart_source_SHA256=RESTART_SOURCE_SHA if wall_restart else None,outputs=0,native_Mesen=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true');parser.add_argument('--validate',action='store_true')
    parser.add_argument('--shared-slot',action='store_true')
    motion=parser.add_mutually_exclusive_group()
    motion.add_argument('--wall-restart',action='store_true',help='Use the separately pinned8f8d wall-restart successor')
    motion.add_argument('--slow-roll',action='store_true',help='Use the separately pinned fe58 slow-roll successor')
    parser.add_argument('--form',choices=(*FORMS,'both'),default='both')
    parser.add_argument('--items',nargs='+',choices=tuple(ITEMS),default=['mushroom'])
    args=parser.parse_args();assert not(args.run and args.validate);assert not args.shared_slot or args.run
    parent=ROM.read_bytes()
    wall_restart=args.wall_restart or args.slow_roll
    raw,composition=candidate(parent,wall_restart,args.slow_roll)
    if not args.run:
        def deny(*a,**kw):raise AssertionError('Pickup source validation attempted output/process')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            q=validate(parent,raw,wall_restart,args.slow_roll)
            q['other_modes']=[
                validate(parent,candidate(parent,wall,slow)[0],wall,slow)
                for wall,slow in ((False,False),(True,False),(True,True))
                if (wall,slow)!=(wall_restart,args.slow_roll)]
        print('RESULT '+json.dumps(q,separators=(',',':')),flush=True);return
    assert args.shared_slot,'Root native pickup runner uses the existing two-file shared slot'
    forms=FORMS if args.form=='both'else(args.form,)
    assert len(forms)*len(args.items)<=2,'Use at most two native cases per bounded invocation'
    import build_storage_guard_v1 as Storage
    from nightly_patch_guard_v1 import check
    from run_stdout_mesen_1110 import run
    Storage.preflight(private_root=SHARED,reserved_files=0,fresh=True)
    validation=validate(parent,raw,wall_restart,args.slow_roll)
    assert {p.name for p in SHARED.iterdir()}=={'candidate.nes','controller.lua'}
    guard=check(ROM);assert guard['ROM_sha256']==BASE and ROM.read_bytes()==parent
    target,script=SHARED/'candidate.nes',SHARED/'controller.lua';originals=target.read_bytes(),script.read_bytes()
    try:
        target.write_bytes(raw)
        for item in args.items:
            for form in forms:
                script.write_text(controller(parent,raw,form,item,wall_restart,args.slow_roll),encoding='utf-8',newline='\n')
                try:q=run(script,target,SHARED/'capture',H(raw),180,extra_env={'SMB_STDOUT_IMAGES':'0'})
                except Exception as error:
                    print('SONIC PICKUP RUNNER FAILURE '+json.dumps(dict(form=form,item=item,ROM_SHA256=H(raw),error=repr(error)),separators=(',',':')),flush=True);raise
                report(form,item,q,validation)
        assert target.read_bytes()==raw and ROM.read_bytes()==parent
    finally:
        target.write_bytes(originals[0]);script.write_bytes(originals[1])
        assert (target.read_bytes(),script.read_bytes())==originals
        assert {p.name for p in SHARED.iterdir()}=={'candidate.nes','controller.lua'}
        assert check(ROM)==guard and ROM.read_bytes()==parent
        print('SONIC PICKUP SHARED RESTORED '+json.dumps(dict(files=2,Downloads_SHA256=BASE,patch_guards_before_after=True,no_delivery=True),separators=(',',':')),flush=True)


if __name__=='__main__':main()
