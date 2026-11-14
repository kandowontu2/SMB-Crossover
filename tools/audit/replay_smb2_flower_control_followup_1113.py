"""Separate ordinary neutral-braking retreat correction; frozen controls intact."""
from hashlib import sha256
import argparse
import json
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

import replay_smb2_postbg_flower_native_1113 as Frozen
import check_smb2_natural_powerups_1113 as Runner
import replay_smb2_natural_powerups_1113 as OldReplay

PIN=Frozen.C.CANDIDATE
FROZEN_ADAPTER_SHA='04577796b7789175fbf8178ee780f116b82888cfec804d1de16d7a295abce01d'
OLD=" elseif natural.phase=='flower-left'then\n  pad=settle(300)\n"
NEW=" elseif natural.phase=='flower-left'then\n  pad=flowerRetreatSettle(300)\n"
HELPER=r'''local function flowerRetreatSettle(target)
 local at=x();local vx=r('S2VX');if vx>=128 then vx=vx-256 end
 local speed=math.abs(vx)
 local stopping=speed*(speed+1)//32+1
 if vx<0 and at-stopping<=target+1 then return 0 end
 if vx>0 and at+stopping>=target-1 then return 0 end
 if at>target+1 then return 2 elseif at<target-1 then return 1 end
 return 0
end
'''


def bindings(raw):
    """Original neutral friction/integrator; controller estimate is conservative."""
    W=Frozen.Flower.Parent.Root.Base.W;b=dict(W.Symbols.bundle(),raw=raw)
    archive=W.R/'docs/qa/checkpoints/2026-11-01/ready85-doki-native-v1/source.zip'
    member='build/doki-current-component-1101-v1/src/smb2_roster_native.inc'
    with ZipFile(archive)as z:source=z.read(member)
    assert sha256(source).hexdigest()=='c929f894f8d6f4723e6371d140c85fef76de47eb9f53bff0af6b544325f80cb0'
    at=W.location(b,'S2D8D2A');assert raw[at:at+2]==bytes.fromhex('fd03')
    add=W.location(b,'S2N8D40');assert raw[add:add+3]==b'\x79'+W.address(b,'S2D8D2A').to_bytes(2,'little')
    shift=W.location(b,'S2N8EB5');assert raw[shift:shift+4]==b'\x4a'*4
    return dict(original_neutral_friction_table=[253,3],current_table_file=at,
        current_ADC_file=add,velocity_1_over_16_integrator_shift_file=shift,
        stopping_estimate='Existing charged-pipe controller v(v+1)/32+1; conservative, not exact friction1',
        no_original_motor_constant_changed=True)


def controller(raw,variant=0,scope='collect'):
    assert sha256(raw).hexdigest()==PIN
    assert sha256(Path(Frozen.__file__).read_bytes()).hexdigest()==FROZEN_ADAPTER_SHA
    bindings(raw)
    before=Frozen.controller(raw,variant,scope)
    assert before.count(OLD)==1 and before.count('local pendingItem=nil')==1
    after=before.replace(OLD,NEW).replace('local pendingItem=nil',HELPER+'local pendingItem=nil')
    assert after.replace(HELPER,'').replace(NEW,OLD)==before
    assert after.count("assert(updates<2600,'Finite ordinary Flower/vegetable route')")==1
    Frozen.Flower.Parent.Root.Base.LuaRuntime().compile(after)
    assert not any(word in after for word in('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    return after


def metadata(raw,variant=0,scope='collect'):
    before=Frozen.controller(raw,variant,scope);text=controller(raw,variant,scope)
    return dict(ROM_SHA256=PIN,variant=variant,scope=scope,controller_SHA256=sha256(text.encode()).hexdigest(),
        frozen_controller_SHA256=sha256(before.encode()).hexdigest(),
        only_flower_left_ordinary_settling_changed=True,reverse_text_exact=True,
        original_assertions_and_2600_bound_exact=True,original_motor_binding=bindings(raw),game_changes=0,outputs=0,Mesen_run=False)


def source_run(raw,variant=0,scope='collect',limit=1500):
    runtime=Frozen.Flower.Parent.Root.Base.LuaRuntime
    def bounded_runtime(*args,**kwargs):
        lua=runtime(*args,**kwargs);lua.globals().CPU_FLOWER_MAIN_LIMIT=limit-2
        return lua
    with patch.object(OldReplay,'controller',lambda image,v,mode:controller(image,v,scope)),\
        patch.object(Runner,'PIN',PIN),patch.object(Frozen.Flower.Parent.Root.Base,'LuaRuntime',bounded_runtime):
        result=Runner.run_controller(raw,variant,'retreat-followup-'+scope,limit)
    compact=Frozen.Flower.compact(result)
    compact['frozen_controller_SHA256']=sha256(Frozen.controller(raw,variant,scope).encode()).hexdigest()
    return compact


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant',choices=tuple(map(str,range(8)))+('all',),default='0')
    p.add_argument('--scope',choices=Frozen.SCOPES,default='collect')
    p.add_argument('--cpu',action='store_true');p.add_argument('--limit',type=int,default=1500)
    args=p.parse_args();raw=Frozen.C.Owner.NIGHTLY.read_bytes();assert sha256(raw).hexdigest()==PIN
    for variant in(range(8)if args.variant=='all'else(int(args.variant),)):
        q=source_run(raw,variant,args.scope,args.limit)if args.cpu else metadata(raw,variant,args.scope)
        print(json.dumps(q,separators=(',',':')),flush=True)
        if args.cpu:assert q['passed'],'Corrected ordinary route must satisfy unchanged scope'
