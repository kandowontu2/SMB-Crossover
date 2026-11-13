"""Root-only bounded actual Downloads DMC-alias timing observation."""
from hashlib import sha256
import json

import replay_smb2_dmc_alias_native_1113 as Replay
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=Replay.Terrain.Flag.R/'build/smb2-flag-native-1113'
LUA='b80d9992f21e4b9632de3a9b8abd4352270368f8394285deb226be0968d10e46'
MODULE='c39e3abea1bd7ada4397e28635038ceb281fcc3f36d2e18816051f6aa1b9e95e'


def main():
    assert sha256(Replay.Path(Replay.__file__).read_bytes()).hexdigest()==MODULE
    assert check(Replay.NIGHTLY)['ROM_sha256']==Replay.PIN
    raw=Replay.NIGHTLY.read_bytes()
    text=Replay.controller(raw)
    assert sha256(text.encode()).hexdigest()==LUA
    script=OUT/'controller.lua'
    script.write_text(text,encoding='utf-8',newline='\n')
    q=run(script,Replay.NIGHTLY,OUT/'capture',Replay.PIN,240)
    receipt=q['receipt']
    trace=receipt.get('dmc_alias',{})
    events=[]
    keep=('kind','frame','Main','cycle','pc','sp','a','world','level','engine',
          'status4015','active_bank','pending_bank','enable','bankA','bankC',
          'mapped_pc','resident','smc_target','smc_next_bank','tail_target',
          'tail_bank','stack_return','apu','address','value','writer',
          'expected_target','expected_bank')
    for _,event in sorted(trace.get('events',{}).items(),key=lambda item:int(item[0])):
        events.append({k:event[k]for k in keep if k in event})
    compact={k:v for k,v in trace.items()if k!='events'}
    compact['events']=events
    print(json.dumps(dict(passed=q['passed'],ROM_SHA256=Replay.PIN,Lua_SHA256=LUA,
        receipt_SHA256=q['receipt_SHA256'],physical_frames=receipt.get('physical_frames'),
        all_returned_Main=receipt.get('all_returned_Main'),terminal=receipt.get('terminal'),
        reason=receipt.get('reason'),trace=compact,outputs_written=q['outputs_written']),
        separators=(',',':')),flush=True)
    assert check(Replay.NIGHTLY)['ROM_sha256']==Replay.PIN
    assert q['passed'],'Native DMC timing observer or retained full route failed'


if __name__=='__main__':main()
