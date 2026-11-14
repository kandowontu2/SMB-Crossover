"""Readonly explicit421 DK CLI/reuse/default checks; zero generated files."""
import argparse
import ast
from contextlib import redirect_stdout,redirect_stderr
from functools import lru_cache
from hashlib import sha256
import io
import json
from pathlib import Path
import subprocess
from unittest.mock import patch

import run_dkjr_descending_native_1113 as CLI
import compose_dkjr_direct_postbg_current_1113 as Merge
import current_smb2_hidden_input_1114 as Current

PIN='df130d5dba8d21e74f5bc2899aad4d77b681381c8f8dfa34b72b392131eedada'


def measure():
    reused=(CLI.OUT/'candidate.nes').read_bytes()
    assert sha256(reused).hexdigest()==Merge.DK.PIN
    routes={}
    for route in CLI.DIRECT_PINS:
        original=CLI.direct_controller(reused,route)
        assert original.count(Merge.DK.PIN)==1
        text=original.replace(Merge.DK.PIN,PIN,1)
        assert text.replace(PIN,Merge.DK.PIN,1)==original
        routes[route]=sha256(text.encode()).hexdigest()
        print(json.dumps(dict(progress_route=route,Lua_SHA256=routes[route])),flush=True)
    return dict(passed=True,measurement_only=True,ROM_SHA256=PIN,route_Lua_SHA256=routes,
        only_ROM_pin_rebound=True,native_run=False,outputs=0)


def run():
    raw=CLI.NIGHTLY.read_bytes();assert sha256(raw).hexdigest()==Current.HIDDEN
    candidate=CLI.OUT/'candidate.nes'
    reused=candidate.read_bytes();assert sha256(reused).hexdigest()==Merge.DK.PIN
    # Only these actual mutable read dependencies are snapshotted. Metadata
    # never reads controller.lua, so no unread output is treated as an input.
    snapshots={CLI.NIGHTLY.resolve():raw,candidate.resolve():reused}
    old=subprocess.run(['git','show','7816d034:tools/audit/run_dkjr_descending_native_1113.py'],
        capture_output=True,check=True).stdout
    assert sha256(old).hexdigest()=='7a233d96675d82f6dd6884228662bffedec4305266ca880fb130616870f5327c'
    old_text=old.decode();current=Path(CLI.__file__).read_text()
    old_ast=ast.parse(old_text);current_ast=ast.parse(current)
    old_functions={q.name:ast.get_source_segment(old_text,q)for q in old_ast.body if isinstance(q,ast.FunctionDef)}
    current_functions={q.name:ast.get_source_segment(current,q)for q in current_ast.body if isinstance(q,ast.FunctionDef)}
    for name in('prepare_current_cheat','direct_controller','complete'):
        assert current_functions[name]==old_functions[name],('Frozen function changed',name)
    marker='    assert public_now in (PARENT, PUBLIC_BUB, PUBLIC_SMB2, PUBLIC_POSTBG)'
    assert current_functions['main'].split(marker,1)[1]==old_functions['main'].split(marker,1)[1]
    flag='    if args.current_cheat_fa66:\n'
    end='    assert public_now in (PARENT, PUBLIC_BUB, PUBLIC_SMB2, PUBLIC_POSTBG)'
    assert current_functions['main'].split(flag,1)[1].split(end,1)[0]==old_functions['main'].split(flag,1)[1].split(end,1)[0]
    names=('PINS','DIRECT_PINS','CURRENT_CHEAT_DK','CURRENT_CHEAT_PINS')
    assignments={q.targets[0].id:ast.literal_eval(q.value)for q in old_ast.body
                 if isinstance(q,ast.Assign)and isinstance(q.targets[0],ast.Name)and q.targets[0].id in names}
    for name in names:assert getattr(CLI,name)==assignments[name]
    rejects=[];writes=0;native_runs=0;read_paths=set()
    read=Path.read_bytes;mode=dict(nightly=raw,reuse=reused)
    def reading(path):
        key=path.resolve()
        if key in snapshots:
            read_paths.add(key)
            return mode['nightly']if key==CLI.NIGHTLY.resolve()else mode['reuse']
        return read(path)
    def no_write(*args,**kwargs):
        nonlocal writes
        writes+=1;raise RuntimeError('Source CLI check attempted a file write')
    def no_native(*args,**kwargs):
        nonlocal native_runs
        native_runs+=1;raise RuntimeError('Source CLI check attempted Mesen')
    def reject(name,fn):
        try:
            with redirect_stderr(io.StringIO()):fn()
        except AssertionError:rejects.append(name)
        except SystemExit as error:
            assert error.code==2;rejects.append(name)
        else:raise AssertionError(('Invalid CLI use accepted',name))
    def metadata(args,nightly=None,reuse=None):
        mode['nightly']=raw if nightly is None else nightly
        mode['reuse']=reused if reuse is None else reuse
        out=io.StringIO()
        with redirect_stdout(out):CLI.main(args)
        q=json.loads(out.getvalue())
        assert q['native_run']is False and q['installed']is False and q['private_only']is True
        return q
    routes={};combined=None;fa66_routes={};reuse_forms=[]
    with patch.object(Path,'read_bytes',reading),patch.object(Path,'write_bytes',no_write),patch.object(Path,'write_text',no_write),\
         patch.object(CLI,'run',no_native),patch.object(CLI,'direct_controller',lru_cache(maxsize=8)(CLI.direct_controller)),\
         patch.object(Current,'normalize',lru_cache(maxsize=2)(Current.normalize)),\
         patch.object(Current.Previous,'normalize',lru_cache(maxsize=4)(Current.Previous.normalize)):
        typed=Current.normalize(raw,kind='hidden-421')
        for route in CLI.DIRECT_PINS:
            image,text,info=CLI.prepare_current_hidden(raw,route=route,reuse_image=reused)
            assert sha256(image).hexdigest()==PIN==CLI.CURRENT_HIDDEN_DK
            original=text.replace(PIN,Merge.DK.PIN,1)
            assert sha256(original.encode()).hexdigest()==CLI.DIRECT_PINS[route]
            assert info['component_changed_bytes']==846 and info['current_fix_changed_bytes_preserved']==176
            assert info['hidden_response_changed_bytes_preserved']==110 and info['fa66_changed_bytes_preserved']==66
            routes[route]=sha256(text.encode()).hexdigest()
            if combined is None:combined=image
            else:assert image==combined
            prior,prior_text,prior_info=CLI.prepare_current_cheat(typed.fa66,route=route,reuse_image=reused)
            assert sha256(prior).hexdigest()==CLI.CURRENT_CHEAT_DK and prior_info['current_fix_changed_bytes_preserved']==66
            fa66_routes[route]=sha256(prior_text.encode()).hexdigest()
            assert fa66_routes[route]==CLI.CURRENT_CHEAT_PINS[route]
            print(json.dumps(dict(progress_route=route,hidden_Lua_SHA256=routes[route],fa66_unchanged=True)),flush=True)
        descending=Merge.DK.reverse(reused)
        for name,source in(('canonical769',reused),('descending14ae',descending),('current_df130',combined)):
            image,text,info=CLI.prepare_current_hidden(raw,route='first-item',reuse_image=source)
            assert image==combined and sha256(text.encode()).hexdigest()==routes['first-item']
            reuse_forms.append(name)
        q=metadata(['--direct','--route','full-stair-universal','--reuse','--current-hidden-421','--metadata'])
        assert q['ROM_SHA256']==PIN and q['Lua_SHA256']==routes['full-stair-universal']and q['current_hidden_421']
        assert q['current_preservation']['all_current_fixes_preserved']and q['current_preservation']['current_fix_changed_bytes_preserved']==176
        # Fresh in-memory source construction is the existing fa66 path's
        # responsibility. The new wrapper must produce the identical image.
        q=metadata(['--direct','--route','first-item','--current-hidden-421','--metadata'])
        assert q['ROM_SHA256']==PIN and q['Lua_SHA256']==routes['first-item']
        q=metadata(['--direct','--route','first-item','--reuse','--current-cheat-fa66','--metadata'],nightly=typed.fa66)
        assert q['ROM_SHA256']==CLI.CURRENT_CHEAT_DK and q['Lua_SHA256']==fa66_routes['first-item']and q['current_cheat_fa66']
        q=metadata(['--direct','--route','first-item','--reuse','--metadata'],nightly=typed.postbg)
        assert q['ROM_SHA256']==Merge.DK.PIN and q['Lua_SHA256']==CLI.DIRECT_PINS['first-item']
        q=metadata(['--route','first-item','--reuse','--metadata'],nightly=typed.postbg,reuse=descending)
        assert q['ROM_SHA256']==CLI.C.PIN and q['Lua_SHA256']==CLI.PINS['first-item']
        mode.update(nightly=raw,reuse=reused)
        reject('default421_rejected',lambda:CLI.main(['--direct','--route','first-item','--reuse','--metadata']))
        reject('hidden_requires_direct',lambda:CLI.main(['--route','first-item','--current-hidden-421','--metadata']))
        reject('hidden_direct_route_required',lambda:CLI.main(['--direct','--route','first-pipe','--current-hidden-421','--metadata']))
        reject('current_options_mutually_exclusive',lambda:CLI.main(['--direct','--route','first-item','--current-hidden-421','--current-cheat-fa66','--metadata']))
        reject('fa66_option_rejects421',lambda:CLI.main(['--direct','--route','first-item','--current-cheat-fa66','--metadata']))
        mode['nightly']=typed.fa66
        reject('default_fa66_rejected',lambda:CLI.main(['--direct','--route','first-item','--reuse','--metadata']))
        reject('fa66_requires_direct',lambda:CLI.main(['--route','first-item','--current-cheat-fa66','--metadata']))
        reject('fa66_direct_route_required',lambda:CLI.main(['--direct','--route','first-pipe','--current-cheat-fa66','--metadata']))
        reject('hidden_option_rejects_fa66',lambda:CLI.main(['--direct','--route','first-item','--current-hidden-421','--metadata']))
        reject('hidden_prepare_rejects_fa66',lambda:CLI.prepare_current_hidden(typed.fa66,route='first-item',reuse_image=reused))
        reject('hidden_prepare_rejects_postbg',lambda:CLI.prepare_current_hidden(typed.postbg,route='first-item',reuse_image=reused))
        reject('fa66_prepare_rejects421',lambda:CLI.prepare_current_cheat(raw,route='first-item',reuse_image=reused))
        reject('hidden_unsupported_route',lambda:CLI.prepare_current_hidden(raw,route='first-pipe',reuse_image=reused))
        reject('hidden_reuse_rejects_a594',lambda:CLI.prepare_current_hidden(raw,route='first-item',reuse_image=prior))
        reject('fa66_reuse_rejects_df130',lambda:CLI.prepare_current_cheat(typed.fa66,route='first-item',reuse_image=combined))
        dirty=bytearray(raw);dirty[971064]^=1
        reject('dirty421_rejected',lambda:CLI.prepare_current_hidden(bytes(dirty),route='first-item',reuse_image=reused))
        dirty_reuse=bytearray(combined);dirty_reuse[971064]^=1
        reject('dirty_df130_rejected',lambda:CLI.prepare_current_hidden(raw,route='first-item',reuse_image=bytes(dirty_reuse)))
        dirty_reuse=bytearray(reused);dirty_reuse[16]^=1
        reject('unknown_reuse_rejected',lambda:CLI.prepare_current_hidden(raw,route='first-item',reuse_image=bytes(dirty_reuse)))
    assert routes==CLI.CURRENT_HIDDEN_PINS and fa66_routes==CLI.CURRENT_CHEAT_PINS
    assert read_paths==set(snapshots)and writes==native_runs==0
    for path,original in snapshots.items():assert read(path)==original
    return dict(passed=True,CLI_source_SHA256=sha256(Path(CLI.__file__).read_bytes()).hexdigest(),
        current_input_SHA256=Current.HIDDEN,private_current_DK_SHA256=PIN,
        all8_ROM_only_rebound_Lua_SHA256=routes,all8_frozen_fa66_Lua_SHA256=fa66_routes,
        old_default_tail_fa66_branch_and_factory_bodies_exact=True,old_PIN_tables_exact=True,
        exact_reuse_forms=reuse_forms,fresh_source_build_and_reuse_equal=True,
        explicit_flag_requires_direct_and_mutual_exclusion=True,rejected_cases=rejects,
        read_dependencies_snapshotted=[str(path)for path in sorted(read_paths)],
        unread_controller_file_not_snapshotted=True,read_dependencies_unchanged=True,
        component_changed_bytes=846,current_fix_changed_bytes_preserved=176,
        file_write_attempts=writes,Mesen_attempts=native_runs,outputs=0,
        merged_native_qualified=False,installed=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--measure',action='store_true');args=p.parse_args()
    print(json.dumps(measure()if args.measure else run(),separators=(',',':')),flush=True)
