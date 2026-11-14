"""Root-only private UI-earned cheat diagnostic; metadata is the default.

Explicit --run reuses the existing Bub two-file slot, with no backup/new file.
The installed12397 ROM is read only. Known E037 debt blocks any delivery.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import compose_smb2_cheat_owner_1113 as Compose
import replay_smb2_cheat_owner_native_1113 as Replay
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

R=Path(__file__).resolve().parents[2]
OUT=R/'build/bub-empty-native-1113'
NIGHTLY=Compose.D.C.Owner.NIGHTLY
PARENT='12397b1c2557834f6a2b7e23c9915d5dc40c6cabff7a6ee844c1adebf6564c52'
CANDIDATE='e8cd1e48bdc48412c30e31b2d0f5decf3a86c49aed85890e8452989e34cc1e17'
COMPOSER='17d915df6bd6d28e7608d8f644e32294f76cefee38cf3e272994da2422c45fa8'
FACTORY='2f0a5f42434d161fe5250aa41862e1c37f36d1a809099f15f72d836178bf0ae6'
LUA='53055897759c775a4f27c7a27d1b9af437bf4c566b3e1a6058bf8d34a98f4755'
SUPERSEDED_ROM='f88cfe5aee15bb3921c691b7f06d905246be9ff88b9b43eea71c2405722724a7'
SUPERSEDED_LUA='79c3859f14c6b32546e04fa82376a605e3884c2222d6efad2d0b29cedf798d4d'
COMPONENT_BYTES=8*1024*1024
EVENT_KEYS=('kind','label','frame','Main','cycle','pc','sp','a','bank','resident','bankA','bankC',
    'world','level','engine','cheat','hurt','menu','focus','start_level','status4015',
    'bytesRemaining','literal_target','literal_bank','smc_target','stack_return',
    'token','stage','entry_Main','entry_sp','caller_return','target','rawbank',
    'target_seen','resident_return','farcall_return')


def component():
    assert OUT.resolve()==R.resolve()/'build/bub-empty-native-1113' and OUT.is_dir()
    size,count=Storage.inventory(OUT,COMPONENT_BYTES,2)
    files={p.relative_to(OUT).as_posix():p for p in OUT.rglob('*')if p.is_file()}
    assert set(files)=={'candidate.nes','controller.lua'} and count==2,sorted(files)
    # Existing empty capture directories are allowed, but never extra files
    # or arbitrary neighboring directories. The generic watchdog owns capture.
    dirs=[p.relative_to(OUT).as_posix()for p in OUT.rglob('*')if p.is_dir()]
    assert all(d=='capture'or d.startswith('capture/')for d in dirs),dirs
    rom=sha256(files['candidate.nes'].read_bytes()).hexdigest()
    lua=sha256(files['controller.lua'].read_bytes()).hexdigest()
    assert rom in(SUPERSEDED_ROM,CANDIDATE),'Unknown private ROM in reusable slot'
    assert lua in(SUPERSEDED_LUA,LUA),'Unknown controller in reusable slot'
    state=('superseded_f88'if(rom,lua)==(SUPERSEDED_ROM,SUPERSEDED_LUA)
           else'exact_private_e8'if(rom,lua)==(CANDIDATE,LUA)else'known_partial_stage')
    return dict(files=count,bytes=size,ROM_SHA256=rom,Lua_SHA256=lua,
                staging_state=state,empty_capture_directories=len(dirs))


def prepare():
    assert sha256(Path(Compose.__file__).read_bytes()).hexdigest()==COMPOSER
    assert sha256(Path(Replay.__file__).read_bytes()).hexdigest()==FACTORY
    before=check(NIGHTLY);raw=NIGHTLY.read_bytes()
    assert before['ROM_sha256']==PARENT and sha256(raw).hexdigest()==PARENT
    assert Compose.PIN==PARENT and Compose.CANDIDATE==CANDIDATE
    image,info=Compose.proposal(raw)
    assert sha256(image).hexdigest()==CANDIDATE and Compose.inverse(image)==raw
    assert info['all_unowned_bytes_exact']and info['E037_debt_untouched']
    text=Replay.controller(image);assert sha256(text.encode()).hexdigest()==LUA
    assert 'cheat_option_diagnostic=true'in text and 'standard_stage_qualification=false'in text
    assert "local function read(at)return emu.read(at,emu.memType.nesDebug)end"in text
    assert all(word not in text for word in('emu.write','emu.setState','takeScreenshot','io.open'))
    current=component()
    projected=len(image)+len(text.encode())
    assert projected<=COMPONENT_BYTES
    return raw,image,text,before,current,projected


def project(q):
    assert q['ROM_SHA256']==CANDIDATE and q['script_SHA256']==LUA
    receipt=q['receipt'];trace=receipt.get('cold_gate',{})
    events=[{k:value[k]for k in EVENT_KEYS if k in value}
        for _,value in sorted(trace.get('events',{}).items(),key=lambda item:int(item[0]))]
    assert len(events)<=64
    menu=[v for v in events if v.get('kind')=='menu']
    calls=trace.get('calls',{});exposed=calls.get('obsolete_UI_tail',0)>0
    if exposed:outcome='real_causal_obsolete_E037_private_negative'
    elif not calls.get('entries'):outcome='UI_or_ingress_not_calibrated'
    elif q['passed']:outcome='cheat_route_completed_without_obsolete_E037_witness'
    else:outcome='cheat_route_failed_without_obsolete_E037_witness'
    return dict(passed=bool(q['passed'])and not exposed,original_route_passed=bool(q['passed']),
        diagnostic_outcome=outcome,reason=receipt.get('reason'),original_reason=receipt.get('reason'),
        cheat_option_diagnostic=True,standard_stage_qualification=False,private_only=True,
        delivery_blocked=True,E037_alias_debt_unrepaired=True,
        ROM_SHA256=CANDIDATE,installed_ROM_SHA256=PARENT,Lua_SHA256=LUA,
        composer_SHA256=COMPOSER,factory_SHA256=FACTORY,actual_Downloads_launch=False,
        native_run=True,emulator_SHA256=q.get('emulator_SHA256'),
        receipt_SHA256=q['receipt_SHA256'],physical_frames=receipt.get('physical_frames'),
        all_returned_Main=receipt.get('all_returned_Main'),terminal=receipt.get('terminal'),
        flag=receipt.get('flag'),castle=receipt.get('castle'),entrance=receipt.get('entrance'),
        next_area_updates=receipt.get('next_area_updates'),calls=calls,
        obsolete_E037_target_observed=exposed,retained_records=len(events),
        dropped_records=trace.get('dropped',0),menu_checkpoints=menu,
        last_observed_menu=menu[-1]if menu else None,
        menu_state_is_checkpoint_not_failure_snapshot=True,
        target_and_return_events=[v for v in events if v.get('kind')!='menu'],
        capture_files=0,outputs_written=q['outputs_written'])


def metadata():
    raw,image,text,before,current,projected=prepare()
    after=check(NIGHTLY)
    assert after['ROM_sha256']==PARENT and NIGHTLY.read_bytes()==raw
    assert component()==current,'Metadata must leave both slot files untouched'
    return dict(cheat_option_diagnostic=True,standard_stage_qualification=False,private_only=True,
        ROM_SHA256=CANDIDATE,parent_SHA256=PARENT,Lua_SHA256=LUA,
        composer_SHA256=COMPOSER,factory_SHA256=FACTORY,Lua_compile=True,
        exact_inverse_parent=True,only_exact_ROM_pin_rebound=True,
        frozen_UI_inputs_route_assertions_and_observer=True,
        E037_alias_debt_unrepaired=True,delivery_blocked=True,actual_Downloads_launch=False,
        native_run=False,explicit_run_required=True,existing_component=current,
        prospective_component_bytes=projected,prospective_component_files=2,
        queue_guard_before_either_overwrite=True,installed_bytes_preserved=True,
        sidecar_guards_before_after=True,emitted_files=0,capture_files=0)


def invoke():
    raw,image,text,before,current,projected=prepare()
    rom,script=OUT/'candidate.nes',OUT/'controller.lua'
    # Queue admission is deliberately before the first write of EITHER file.
    # The generic runner repeats admission and owns the shared capture lease.
    require_free_workspace(R,rom,allow_interactive=True)
    Storage.preflight(private_root=OUT,reserved_bytes=max(0,projected-current['bytes']),
                      reserved_files=0,fresh=True)
    assert component()==current,'Reusable slot changed before staging'
    q=None;errors=[];attempted=False;write_attempted=False;staged=False;installed=False;guarded=False;final=None
    try:
        write_attempted=True
        rom.write_bytes(image)
        script.write_text(text,encoding='utf-8',newline='\n')
        assert rom.read_bytes()==image and sha256(script.read_bytes()).hexdigest()==LUA
        staged=True;attempted=True
        q=run(script,rom,OUT/'capture',CANDIDATE,240)
        assert q['outputs_written']==0 and not q['images']
    except Exception as error:
        errors.append(type(error).__name__+': '+str(error)[:4096])
    finally:
        # Run both installed checks even when staging, Mesen, or a route
        # assertion fails. Never restore/copy/change the installed ROM here.
        try:
            after=check(NIGHTLY);guarded=after['ROM_sha256']==PARENT
            installed=NIGHTLY.read_bytes()==raw
            assert guarded and installed,'Installed12397 bytes/sidecars changed'
        except Exception as error:errors.append('post-installed-guard: '+str(error)[:4096])
        try:
            final=component()
            if staged:assert(final['ROM_SHA256'],final['Lua_SHA256'])==(CANDIDATE,LUA)
        except Exception as error:errors.append('post-component-guard: '+str(error)[:4096])
    result=project(q)if q is not None else dict(passed=False,
        diagnostic_outcome='private_runner_or_receipt_failure',original_reason=None,
        cheat_option_diagnostic=True,standard_stage_qualification=False,private_only=True,
        ROM_SHA256=CANDIDATE,installed_ROM_SHA256=PARENT,Lua_SHA256=LUA,
        composer_SHA256=COMPOSER,factory_SHA256=FACTORY,actual_Downloads_launch=False,
        E037_alias_debt_unrepaired=True,delivery_blocked=True,menu_checkpoints=[],calls={},
        capture_files=0,outputs_written=0,native_run=False)
    if errors:result.update(passed=False,runner_errors=errors)
    result.update(native_run_attempted=attempted,native_receipt_received=q is not None,
        staged_exact_candidate_and_frozen_controller=staged,existing_files_overwritten_only=write_attempted,
        queue_guard_before_either_overwrite=True,installed_bytes_preserved=installed,
        sidecar_guards_before_after=guarded,component_before=current,component_after=final,
        created_backups_or_ROM_copies=False)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    mode=p.add_mutually_exclusive_group()
    mode.add_argument('--run',action='store_true',help='Root only, after freeing its single native queue.')
    mode.add_argument('--metadata',action='store_true',help='Read/compile only; the default.')
    args=p.parse_args();q=invoke()if args.run else metadata()
    line=json.dumps(q,separators=(',',':'));assert len(line.encode())<=256*1024
    print(line,flush=True)
    if args.run:raise SystemExit(0 if q['passed']else 1)
