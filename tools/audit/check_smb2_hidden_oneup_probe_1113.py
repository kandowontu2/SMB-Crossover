"""Read-only actual hidden-cell probe trace; base negative remains frozen."""
from hashlib import sha256
import json
from unittest.mock import patch

import replay_smb2_hidden_oneup_1113 as Route


def controller(raw,variant=0):
    text=Route.controller(raw,variant);W=Route.W
    _,b,_=Route.inputs(raw)
    _,new,info=Route.Current.Flag.source_recipe(raw)
    owner=Route.Current.Flag
    assert raw[owner.PROBE_AT:owner.PROBE_AT+owner.PROBE_SIZE]==new['probe']
    fields=('R2','R4','R5','S2HeadY','S2HeadX','S2HeadPage','S2ProbeDirection')
    field=','.join(n+'='+str(W.address(b,n))for n in fields)+','
    labels=info['labels'];at=labels['ProbeOtherTile'];result=labels['ProbeResult']
    literal='local oneupTrace={'+','.join(n+'='+str(W.address(b,n))for n in fields)+'}\n'
    for name,pc in(('entry',at),('result',result)):
        file=owner.PROBE_AT+pc-0xb128
        literal+='local oneupTrace_'+name+'={pc='+str(pc)+',offset='+str(file-16)+',hex="'+raw[file:file+4].hex()+'"}\n'
    trace=r'''
local pendingHiddenProbe=nil
local function traceRead(name)return read(oneupTrace[name])end
local function traceHook(h)
 local q=emu.convertAddress(h.pc);return q and q.memType==emu.memType.nesPrgRom and q.address==h.offset
end
for _,h in ipairs({oneupTrace_entry,oneupTrace_result})do for i=1,#h.hex,2 do assert(emu.read(h.offset+(i-1)//2,emu.memType.nesPrgRom)==tonumber(h.hex:sub(i,i+1),16),'Actual hidden probe trace preimage')end end
emu.addMemoryCallback(guard(function()
 if not game or not traceHook(oneupTrace_entry)then return end
 local c=emu.getState();if c['cpu.a']~=96 then return end
 local wx=traceRead('R4')+256*traceRead('R5');local yy=traceRead('R2')
 if wx~=1024 or yy~=128 then return end
 pendingHiddenProbe={s=state(),source=oneupSource(),tile=c['cpu.a'],worldX=wx,worldY=yy,direction=traceRead('S2ProbeDirection'),cacheY=traceRead('S2HeadY'),SP=c['cpu.sp']}
end),emu.callbackType.exec,oneupTrace_entry.pc)
emu.addMemoryCallback(guard(function()
 if not game or not pendingHiddenProbe or not traceHook(oneupTrace_result)then return end
 local c=emu.getState();local q=pendingHiddenProbe
 if c['cpu.sp']~=q.SP or q.s.updates~=updates then return end
 q.result_A=c['cpu.a'];q.result_cacheY=traceRead('S2HeadY')
 oneup.probe_count=(oneup.probe_count or 0)+1;oneup.probes=oneup.probes or{}
 if #oneup.probes<16 then oneup.probes[#oneup.probes+1]=q end
 pendingHiddenProbe=nil
end),emu.callbackType.exec,oneupTrace_result.pc)
'''
    marker='-- Observe every actual GameLoop return, including the native catch-up caller.'
    assert text.count(marker)==1
    out=literal+text.replace(marker,trace+'\n'+marker)
    assert out.removeprefix(literal).replace(trace+'\n','')==text
    Route.Terrain.Frozen.Flag.Root.Base.LuaRuntime().compile(out)
    return out,dict(probe_file=owner.PROBE_AT,probe_bytes=owner.PROBE_SIZE,
        probe_SHA256=sha256(new['probe']).hexdigest(),other_tile_PC=at,result_PC=result,
        base_controller_SHA256=sha256(text.encode()).hexdigest(),readonly_trace=True)


def trace(raw):
    text,bindings=controller(raw)
    with patch.object(Route.OldReplay,'controller',lambda image,v,mode:text),patch.object(Route.Runner,'PIN',Route.PIN):
        q=Route.Runner.run_controller(raw,0,'hidden1UP-readonly-probe-trace',2800)
    receipt=q.pop('receipt')or{};oneup=receipt.get('oneup',{})
    rows=list((oneup.get('probes')or{}).values())
    assert not q['passed'] and oneup['attempts']==oneup['landings']==6
    assert oneup.get('head')is None and oneup.get('birth')is None and rows
    assert all(r['tile']==96 and r['result_A']==0 and r['cacheY']==r['result_cacheY']==0 for r in rows)
    return dict(passed=True,expected_route_negative=True,reason=receipt.get('reason'),bindings=bindings,
        logical_iterations=q['logical_Main_NMI_iterations'],returned_Main=receipt.get('all_returned_Main'),
        terminal=q['terminal'],attempts=oneup['attempts'],landings=oneup['landings'],minimumY=oneup['minY'],
        actual_hidden_probe_count=oneup.get('probe_count'),probe_rows=rows,
        actual_native_head=False,actor_or_health_or_tile_seeds=0,outputs=0,Mesen_run=False)


if __name__=='__main__':
    raw=Route.Post.Owner.NIGHTLY.read_bytes()
    print(json.dumps(trace(raw),separators=(',',':')),flush=True)
