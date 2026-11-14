"""Readonly live DK CLI opt-in/default/reuse checks; zero generated files."""
import ast
from contextlib import redirect_stdout
from hashlib import sha256
from functools import lru_cache
import io
import json
from pathlib import Path
import subprocess
from unittest.mock import patch

import run_dkjr_descending_native_1113 as CLI
import current_smb2_cheat_input_1114 as Current
import compose_dkjr_direct_postbg_current_1113 as Merge


def run():
    raw=CLI.NIGHTLY.read_bytes();assert sha256(raw).hexdigest()==Current.CHEAT
    reused=(CLI.OUT/'candidate.nes').read_bytes()
    assert sha256(reused).hexdigest()==Merge.DK.PIN,'Root canonical769 slot must be unchanged for this source check'
    # Read the immutable pre-change source from Git without creating a file.
    old=subprocess.run(['git','show','0c0c6bca:tools/audit/run_dkjr_descending_native_1113.py'],
        capture_output=True,check=True).stdout
    assert sha256(old).hexdigest()=='51e8530c5cd278a42e41ee1d9ca90e1b1fb9fdaf992fe5bd0d221cceabc4ee5f'
    assignments={n.targets[0].id:ast.literal_eval(n.value)for n in ast.parse(old).body
                 if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)
                 and n.targets[0].id in('PINS','DIRECT_PINS')}
    assert CLI.PINS==assignments['PINS']and CLI.DIRECT_PINS==assignments['DIRECT_PINS']
    rejects=[]
    def reject(name,fn):
        try:fn()
        except AssertionError:rejects.append(name)
        else:raise AssertionError(('Invalid CLI use accepted',name))
    def forbid(*args,**kwargs):raise RuntimeError('Source CLI check attempted a write or Mesen run')
    routes={};images=[]
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(CLI,'run',forbid),\
         patch.object(CLI,'direct_controller',lru_cache(maxsize=8)(CLI.direct_controller)):
        for route in CLI.DIRECT_PINS:
            image,text,info=CLI.prepare_current_cheat(raw,route=route,reuse_image=reused)
            original=text.replace(CLI.CURRENT_CHEAT_DK,Merge.DK.PIN,1)
            assert sha256(original.encode()).hexdigest()==CLI.DIRECT_PINS[route]
            assert sha256(image).hexdigest()==CLI.CURRENT_CHEAT_DK
            assert info['component_changed_bytes']==846 and info['current_fix_changed_bytes_preserved']==66
            routes[route]=sha256(text.encode()).hexdigest()
            if not images:images.append(image)
            print(json.dumps(dict(progress_route=route,controller_SHA256=routes[route])),flush=True)
        combined=images[0]
        for name,source in(('canonical769',reused),('descending14ae',Merge.DK.reverse(reused)),('current_a594',combined)):
            image,text,info=CLI.prepare_current_cheat(raw,route='first-item',reuse_image=source)
            assert image==combined and sha256(text.encode()).hexdigest()==routes['first-item']
        out=io.StringIO()
        with redirect_stdout(out):
            CLI.main(['--direct','--route','full-stair-universal','--reuse','--current-cheat-fa66','--metadata'])
        cli=json.loads(out.getvalue())
        assert not cli['native_run']and not cli['installed']and cli['ROM_SHA256']==CLI.CURRENT_CHEAT_DK
        assert cli['Lua_SHA256']==routes['full-stair-universal']and cli['current_preservation']['all_current_fixes_preserved']
        reject('default_fa66_rejected',lambda:CLI.main(['--direct','--route','first-item','--reuse','--metadata']))
        reject('opt_in_requires_direct',lambda:CLI.main(['--route','first-item','--current-cheat-fa66','--metadata']))
        reject('non_direct_route_rejected',lambda:CLI.main(['--direct','--route','first-pipe','--current-cheat-fa66','--metadata']))
        typed=Current.normalize(raw,kind='cheat-fa66')
        reject('postbg_not_current_fa66',lambda:CLI.prepare_current_cheat(typed.postbg,route='first-item',reuse_image=reused))
        bad=bytearray(raw);bad[Current.C.EDITS[0][0]]^=1
        reject('changed_current_gate_rejected',lambda:CLI.prepare_current_cheat(bytes(bad),route='first-item',reuse_image=reused))
        bad=bytearray(reused);bad[16]^=1
        reject('unknown_reuse_rejected',lambda:CLI.prepare_current_cheat(raw,route='first-item',reuse_image=bytes(bad)))
        reject('unsupported_route_rejected',lambda:CLI.prepare_current_cheat(raw,route='first-pipe',reuse_image=reused))
    assert CLI.NIGHTLY.read_bytes()==raw
    assert (CLI.OUT/'candidate.nes').read_bytes()==reused
    assert routes==CLI.CURRENT_CHEAT_PINS
    return dict(passed=True,current_input_SHA256=Current.CHEAT,private_current_DK_SHA256=CLI.CURRENT_CHEAT_DK,
        all8_direct_controller_SHA256=routes,original_5_legacy_and8_direct_hashes_unchanged=True,
        explicit_flag_required=True,exact14ae_769_a594_reuse_same_candidate=True,
        CLI_actual_readonly_metadata=True,rejected_cases=rejects,
        component_changed_bytes=846,current_fix_changed_bytes_preserved=66,
        candidate_file_unchanged=True,controller_writes_trapped=True,Downloads_bytes_unchanged=True,
        native_run=False,merged_native_qualified=False,outputs=0)


if __name__=='__main__':print(json.dumps(run(),separators=(',',':')),flush=True)
