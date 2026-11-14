"""Root-only actual-Downloads cheat-option diagnostic; metadata by default.

An explicit --run reuses only the existing SMB2 controller.lua. No ROM,
capture, receipt or backup file is created. The frozen Lua is not modified.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import replay_smb2_cold_gate_native_1113 as Replay
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

R=Path(__file__).resolve().parents[2]
OUT=R/'build/smb2-flag-native-1113'
NIGHTLY=Replay.C.Owner.NIGHTLY
PIN='12397b1c2557834f6a2b7e23c9915d5dc40c6cabff7a6ee844c1adebf6564c52'
MODULE='6e1a95017100d08193b5c7298d89125066eaa6e6832bd55cde7bbd0fe4c042d1'
LUA='eb9ae28a623d58d75b5795e3620643c7e2b945a047e75df46ae3fbd9bec6102b'
COMPONENT_BYTES=8*1024*1024


def component():
    assert OUT.is_dir(),'Root must reuse its existing SMB2 two-file component'
    files={p.relative_to(OUT).as_posix():p for p in OUT.rglob('*')if p.is_file()}
    assert set(files)=={'candidate.nes','controller.lua'},sorted(files)
    size=sum(p.stat().st_size for p in files.values())
    assert size<=COMPONENT_BYTES
    digest=sha256(files['candidate.nes'].read_bytes()).hexdigest()
    assert digest==PIN,'Existing component ROM must already be exact installed12397'
    return dict(files=2,bytes=size,retained_component_ROM_SHA256=digest)


def prepare():
    before=check(NIGHTLY)
    raw=NIGHTLY.read_bytes()
    assert before['ROM_sha256']==PIN and sha256(raw).hexdigest()==PIN
    assert sha256(Path(Replay.__file__).read_bytes()).hexdigest()==MODULE
    text=Replay.controller(raw)
    assert sha256(text.encode()).hexdigest()==LUA
    assert "local function read(at)return emu.read(at,emu.memType.nesDebug)end" in text
    assert 'cheat_option_diagnostic=true' in text and 'standard_stage_qualification=false' in text
    assert all(word not in text for word in('emu.write','emu.setState','takeScreenshot','io.open'))
    return raw,text,before,component()


EVENT_KEYS=('kind','label','frame','Main','cycle','pc','sp','a','bank','resident','bankA','bankC',
            'world','level','engine','cheat','hurt','menu','focus','start_level','status4015',
            'bytesRemaining','literal_target','literal_bank','smc_target','stack_return',
            'token','stage','entry_Main','entry_sp','caller_return','target','rawbank',
            'target_seen','resident_return','farcall_return')


def project(q):
    receipt=q['receipt'];trace=receipt.get('cold_gate',{})
    rows=trace.get('events',{})
    events=[{k:value[k]for k in EVENT_KEYS if k in value}
            for _,value in sorted(rows.items(),key=lambda item:int(item[0]))]
    assert len(events)<=64
    menu=[value for value in events if value.get('kind')=='menu']
    calls=trace.get('calls',{})
    exposed=calls.get('obsolete_UI_tail',0)>0
    if exposed:outcome='obsolete_target_exposure_observed'
    elif not q['passed'] and not calls.get('entries'):outcome='UI_or_ingress_not_calibrated'
    elif q['passed']:outcome='ordinary_cheat_route_completed_without_old_target_witness'
    else:outcome='cheat_route_failed_without_old_target_witness'
    return dict(passed=bool(q['passed']),diagnostic_outcome=outcome,
        cheat_option_diagnostic=True,standard_stage_qualification=False,
        ROM_SHA256=PIN,Lua_SHA256=LUA,factory_SHA256=MODULE,actual_Downloads_launch=True,
        native_run=True,emulator_SHA256=q.get('emulator_SHA256'),
        receipt_SHA256=q['receipt_SHA256'],reason=receipt.get('reason'),
        physical_frames=receipt.get('physical_frames'),all_returned_Main=receipt.get('all_returned_Main'),
        terminal=receipt.get('terminal'),flag=receipt.get('flag'),castle=receipt.get('castle'),
        entrance=receipt.get('entrance'),next_area_updates=receipt.get('next_area_updates'),
        obsolete_target_observed=exposed,calls=calls,retained_records=len(events),
        dropped_records=trace.get('dropped',0),menu_checkpoints=menu,
        last_observed_menu=menu[-1]if menu else None,
        menu_state_is_checkpoint_not_failure_snapshot=True,
        target_and_return_events=[value for value in events if value.get('kind')!='menu'],
        capture_files=0,outputs_written=q['outputs_written'])


def metadata():
    raw,text,before,current=prepare()
    after=check(NIGHTLY)
    assert after['ROM_sha256']==PIN and NIGHTLY.read_bytes()==raw
    return dict(cheat_option_diagnostic=True,standard_stage_qualification=False,
        ROM_SHA256=PIN,Lua_SHA256=LUA,factory_SHA256=MODULE,Lua_compile=True,
        source_opening_qualified=False,actual_Downloads_launch=True,native_run=False,
        explicit_run_required=True,queue_required='Root single workspace queue; checked before controller overwrite',
        existing_component=current,controller_is_exact_frozen_Lua=True,
        installed_bytes_preserved=True,sidecar_guards_before_after=True,
        prospective_controller_overwrite='build/smb2-flag-native-1113/controller.lua',
        emitted_files=0,capture_files=0)


def invoke():
    raw,text,before,current=prepare()
    # Check the existing queue before mutating even the generated script.
    # The shared stdout runner repeats this guard and owns its capture lease.
    require_free_workspace(R,NIGHTLY,allow_interactive=True)
    Storage.preflight(private_root=OUT,reserved_bytes=COMPONENT_BYTES,reserved_files=2,fresh=True)
    script=OUT/'controller.lua'
    q=None;failure=None;attempted=False
    try:
        script.write_text(text,encoding='utf-8',newline='\n')
        assert sha256(script.read_bytes()).hexdigest()==LUA
        attempted=True
        q=run(script,NIGHTLY,OUT/'capture',PIN,240)
        assert q['outputs_written']==0 and not q['images']
    except Exception as error:
        failure=type(error).__name__+': '+str(error)[:4096]
    finally:
        after=check(NIGHTLY)
        assert after['ROM_sha256']==PIN and NIGHTLY.read_bytes()==raw,'Installed bytes changed'
        final=component()
        assert final['retained_component_ROM_SHA256']==current['retained_component_ROM_SHA256']
    result=project(q)if q is not None else dict(passed=False,cheat_option_diagnostic=True,
        standard_stage_qualification=False,diagnostic_outcome='runner_or_receipt_failure',
        ROM_SHA256=PIN,Lua_SHA256=LUA,factory_SHA256=MODULE,actual_Downloads_launch=True,
        menu_checkpoints=[],calls={},capture_files=0,outputs_written=0)
    if failure:result['runner_error']=failure;result['passed']=False
    result.update(native_run_attempted=attempted,native_receipt_received=q is not None,
                  installed_bytes_preserved=True,sidecar_guards_before_after=True,
                  retained_component_ROM_preserved=True,component_files=final['files'],
                  controller_overwritten_only=True)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    mode=p.add_mutually_exclusive_group()
    mode.add_argument('--run',action='store_true',help='Root only, after freeing the single native queue.')
    mode.add_argument('--metadata',action='store_true',help='Read/compile only; this is the default.')
    args=p.parse_args()
    q=invoke()if args.run else metadata()
    line=json.dumps(q,separators=(',',':'))
    assert len(line.encode())<=256*1024,'Compact stdout aggregate bound'
    print(line,flush=True)
    if args.run:raise SystemExit(0 if q['passed']else 1)
