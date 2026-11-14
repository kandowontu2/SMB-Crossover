"""Scene-only passive successor to the frozen SMB2 DMC alias observer."""
from hashlib import sha256
import argparse
import json
from pathlib import Path

import replay_smb2_dmc_alias_native_1113 as Old

OLD_SOURCE = 'c39e3abea1bd7ada4397e28635038ceb281fcc3f36d2e18816051f6aa1b9e95e'
OLD_LUA = 'b80d9992f21e4b9632de3a9b8abd4352270368f8394285deb226be0968d10e46'
LUA_SHA = '5bd36d95616f88bc30946c7b6d0a2a6aa7d7948964848236ecef02b7e76e016f'


def once(text, before, after):
    assert text.count(before) == 1, before
    return text.replace(before, after, 1)


NATIVE = r'''
-- A target name alone is not causal evidence. A fresh same-Main token must
-- follow the exact tail, bank gateway and SMC JSR with matching live SP.
local sceneToken,sceneSequence=nil,0
local sceneContexts,sceneSeen,sceneReturnHooks={},{},{}
local sceneDetails,sceneReturnHookCount=0,0
aliasTrace.scene_only=true;aliasTrace.fresh_same_Main=true
aliasTrace.token_cycle_bound=120000;aliasTrace.token_frame_bound=4
aliasTrace.chain_counts={};aliasTrace.detail_context_cap=3
local function sceneCount(name)
 aliasTrace.chain_counts[name]=(aliasTrace.chain_counts[name]or 0)+1
end
local function sceneFresh(t)
 if not t or not aliasScene()or updates~=t.Main then return false end
 local c=emu.getState();local elapsed=c['cpu.cycleCount']-t.cycle
 return elapsed>=0 and elapsed<=120000 and frames-t.frame>=0 and frames-t.frame<=4
end
local function sceneLog(t,q)
 if not t.record then return end
 q.token=t.id;q.entry_Main=t.Main;q.entry_cycle=t.cycle;q.entry_sp=t.sp
 q.entry_return=t.ret;q.chain_stage=t.stage;q.native_target_seen=t.target_seen or false
 q.farcall_return_seen=t.farcall_return~=nil;q.resident_return_seen=t.returned or false
 if t.farcall_return then q.farcall_return=t.farcall_return end
 aliasRecord(q,true)
end
local function sceneInstallReturn(t)
 if sceneReturnHooks[t.ret]then return end
 if sceneReturnHookCount>=4 then sceneCount('return_hook_cap');return end
 sceneReturnHookCount=sceneReturnHookCount+1;sceneReturnHooks[t.ret]=true
 local pc=t.ret
 emu.addMemoryCallback(guard(function()
  local live=sceneToken;if not sceneFresh(live)or pc~=live.ret then return end
  local c=emu.getState();local at=aliasLocation(pc)
  if c['cpu.sp']~=(live.sp+2)&255 or at.kind~=live.ret_kind or at.offset~=live.ret_offset then return end
  live.returned=true;sceneCount('resident_returns')
  sceneLog(live,aliasSnapshot('scene_resident_return'))
  live.stage='resident_return'
 end),emu.callbackType.exec,pc)
end
sceneMainOutcome=function()
 for _,t in ipairs(sceneContexts)do
  if updates>t.Main then sceneLog(t,aliasSnapshot('scene_next_Main_outcome'))end
 end
 sceneContexts={};sceneToken=nil
end
emu.addMemoryCallback(guard(function()
 if not aliasScene()then return end
 local q=aliasSnapshot('scene_resident_entry');local bank=q.resident.bank
 if bank~=119 and bank~=120 and bank~=125 and bank~=127 then return end
 sceneCount('resident_entries');sceneSequence=sceneSequence+1
 local ret=aliasLocation(q.stack_return);local key=aliasInterest(q)
 local keep=not sceneSeen[key]and sceneDetails<3
 if keep then sceneSeen[key]=true;sceneDetails=sceneDetails+1 end
 local t={id=sceneSequence,Main=updates,cycle=q.cycle,frame=frames,sp=q.sp,
  ret=q.stack_return,ret_kind=ret.kind,ret_offset=ret.offset,stage='entry',record=keep}
 sceneToken=t
 if keep then sceneContexts[#sceneContexts+1]=t;sceneLog(t,q)end
 sceneInstallReturn(t)
end),emu.callbackType.exec,0xe5cc)
emu.addMemoryCallback(guard(function()
 local t=sceneToken;if not sceneFresh(t)or t.stage~='entry'then return end
 local q=aliasSnapshot('scene_tail');local b=q.resident.bank
 if q.sp~=t.sp or(b~=119 and b~=120 and b~=125 and b~=127)then return end
 t.target=q.tail_target;t.bank=q.tail_bank&127;t.rawbank=q.tail_bank;t.stage='tail'
 sceneCount('matched_tail')
end),emu.callbackType.exec,0xe5f5)
emu.addMemoryCallback(guard(function()
 local t=sceneToken;if not sceneFresh(t)or t.stage~='tail'then return end
 local q=aliasSnapshot('scene_gateway')
 if q.sp~=t.sp or q.a~=t.rawbank or q.smc_target~=t.target then return end
 t.stage='gateway';sceneCount('matched_gateway')
end),emu.callbackType.exec,0x15a)
emu.addMemoryCallback(guard(function()
 local t=sceneToken;if not sceneFresh(t)or t.stage~='gateway'then return end
 local q=aliasSnapshot('scene_matched_SMC')
 if q.sp~=(t.sp-1)&255 or q.smc_target~=t.target or q.bankA~=t.rawbank
  or not aliasMapped(t.target,t.bank)then return end
 t.stage='SMC';sceneCount('matched_SMC');sceneLog(t,q)
end),emu.callbackType.exec,0x16b)
for _,point in ipairs({{pc=0xbb87,bank=79,name='scene_matched_stale_target'},
 {pc=0xb438,bank=66,name='scene_matched_canonical_target'}})do
 emu.addMemoryCallback(guard(function()
  if not aliasScene()or not aliasMapped(point.pc,point.bank)then return end
  sceneCount('named_target_entries')
  local t=sceneToken;if not sceneFresh(t)or t.stage~='SMC'or t.target~=point.pc or t.bank~=point.bank then
   sceneCount('uncorrelated_named_target');return
  end
  local q=aliasSnapshot(point.name)
  if q.sp~=(t.sp-3)&255 or q.stack_return~=0x16e then sceneCount('target_stack_reject');return end
  t.stage='target';t.target_seen=true;sceneCount(point.name);sceneLog(t,q)
 end),emu.callbackType.exec,point.pc)
end
emu.addMemoryCallback(guard(function()
 local t=sceneToken;if not sceneFresh(t)or t.stage~='target'then return end
 local q=aliasSnapshot('scene_farcall_return')
 if q.sp~=(t.sp-1)&255 then return end
 t.farcall_return={cycle=q.cycle,frame=q.frame,sp=q.sp,a=q.a,bankA=q.bankA}
 t.stage='farcall_return';sceneCount('farcall_returns')
end),emu.callbackType.exec,0x16e)
'''


def observer():
    marker = "emu.addMemoryCallback(guard(function()\n if not aliasScene()then return end\n local q=aliasSnapshot('resident_entry')"
    assert Old.OBSERVER.count(marker) == 1
    prefix = Old.OBSERVER[:Old.OBSERVER.index(marker)]
    prefix = once(prefix, 'local function aliasRecord(q,tail)\n',
                  'local function aliasRecord(q,tail)\n if not game or read(aliasFields.WorldNumber)~=0 or read(aliasFields.LevelNumber)~=1 then return end\n')
    prefix = once(prefix, 'local function aliasWrite(at,writer,value)', '''local function aliasInterest(q)
 local remaining=q.apu['apu.dmc.bytesRemaining']
 return (q.status4015&16)..':'..tostring(remaining)..':'..q.resident.bank..':'..q.engine..':'..q.level
end
local function aliasWrite(at,writer,value)''')
    prefix = once(prefix, 'if not game or not aliasMapped(writer,74)then return end',
                  'if not aliasScene()or not aliasMapped(writer,74)then return end')
    old = ''' local resident=aliasLocation(0xe5cc).bank
 local key=tostring(writer)..':'..value..':'..resident..':'..read(aliasFields.LevelNumber)..':'..read(aliasFields.GameEngineSubroutine)
 if aliasLastWrite[at]==key then return end
 aliasLastWrite[at]=key
 local q=aliasSnapshot(at==0x5117 and 'sample_alias_write'or'sample_status_write')'''
    new = ''' local q=aliasSnapshot(at==0x5117 and 'sample_alias_write'or'sample_status_write')
 local key=writer..':'..aliasInterest(q)..':'..(at==0x5117 and value or value&16)
 if aliasLastWrite[at]==key then return end
 aliasLastWrite[at]=key'''
    prefix = once(prefix, old, new)
    prefix = once(prefix, 'if not game or not aliasMapped(point.pc,74)then return end',
                  'if not aliasScene()or not aliasMapped(point.pc,74)then return end')
    prefix = once(prefix, "local key=q.resident.bank..':'..q.status4015..':'..q.level..':'..q.engine",
                  'local key=aliasInterest(q)')
    return prefix+NATIVE


def controller(raw):
    assert sha256(Path(Old.__file__).read_bytes()).hexdigest() == OLD_SOURCE
    base = Old.controller(raw)
    assert sha256(base.encode()).hexdigest() == OLD_LUA and base.endswith(Old.OBSERVER)
    text = base[:-len(Old.OBSERVER)]+observer()
    text = once(text, 'local function finish(ok,why)', 'local sceneMainOutcome\nlocal function finish(ok,why)')
    text = once(text, 'pending[#pending]=nil;updates=updates+1',
                'pending[#pending]=nil;updates=updates+1;if sceneMainOutcome then sceneMainOutcome()end')
    # The only base-policy insertion calls an observation function. Removing
    # it and restoring the frozen observer reproduces exact b80d byte text.
    stripped = text[:-len(observer())]+Old.OBSERVER
    stripped = stripped.replace('local sceneMainOutcome\n', '', 1).replace(
        ';updates=updates+1;if sceneMainOutcome then sceneMainOutcome()end', ';updates=updates+1', 1)
    assert stripped == base
    Old.Terrain.Frozen.Flag.Root.Base.LuaRuntime().compile(text)
    assert all(word not in text for word in ('emu.write', 'emu.setState', 'takeScreenshot', 'io.open'))
    assert sha256(text.encode()).hexdigest() == LUA_SHA
    return text


def metadata(raw):
    text = controller(raw)
    return dict(ROM_SHA256=Old.PIN, variant=1, base_observer_SHA256=OLD_LUA,
                original_control_SHA256=Old.BASE_SHA, controller_SHA256=sha256(text.encode()).hexdigest(),
                original_inputs_and_25_grounded_endpoint_exact=True, scene_only=True,
                event_cap=64, native_snapshot_cap=16, fresh_same_Main_tokens=True,
                runtime_state_writes=0, capture_files=0, outputs=0, Mesen_run=False)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, default=Old.NIGHTLY)
    args = p.parse_args()
    print(json.dumps(metadata(args.rom.read_bytes()), separators=(',', ':')), flush=True)
