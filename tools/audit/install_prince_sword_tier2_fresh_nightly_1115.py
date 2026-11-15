"""Install only root-approved40a, then verify the actual Downloads context."""
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import sys
import compose_prince_sword_tier2_fresh_1115 as C
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run

OUT=C.R/'build/smb2-flag-native-1113'
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
GRANT=C.R/'docs/qa/allocations/prince-sword-tier2-fresh-delivery-1115.json'
LUA='e1614ed60e1bb2d3990df26c4f1f16e97fcda6a744ca9950bf346cc2a3ddbc2f'

def cli_guard():
    subprocess.run([sys.executable,'-B',str(C.R/'tools/audit/nightly_patch_guard_v1.py'),str(ROM)],check=True)
    return check(ROM)

def execute():
    g=json.loads(GRANT.read_bytes())
    assert g['root_Downloads_delivery_authorized']
    assert g['candidate_SHA256']==C.CANDIDATE and g['parent_SHA256']==C.PIN
    assert g['source_full_and_required_checks_passed']and g['private_native_full_passed']
    assert sha256(Path(C.__file__).read_bytes()).hexdigest()==g['composer_SHA256']
    before=cli_guard()
    parent=ROM.read_bytes()
    assert sha256(parent).hexdigest()==C.PIN
    target=OUT/'candidate.nes'
    script=OUT/'controller.lua'
    image=target.read_bytes()
    assert sha256(image).hexdigest()==C.CANDIDATE
    assert C.inverse(image)==parent and C.proposal(parent)[0]==image
    # Reuse the exact script that passed private native; no historical
    # controller reconstruction or extra ROM/capture files are needed.
    assert sha256(script.read_bytes()).hexdigest()==LUA==g['Lua_SHA256']
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    require_free_workspace(C.R,ROM,allow_interactive=True)
    ROM.write_bytes(image)
    try:
        assert check(ROM)['ROM_sha256']==C.CANDIDATE
        q=run(script,ROM,OUT/'capture',C.CANDIDATE,240,variant=3)
        assert q['passed']and q['receipt']['persistent_sword']=={'native_PlayerStatus':2,'Sword':1}
        assert q['script_SHA256']==LUA and not q['images']and q['outputs_written']==0
        assert q['receipt_SHA256']==g['private_native_receipt_SHA256'],'Actual Downloads replay differs from tested private route'
        assert ROM.read_bytes()==image and target.read_bytes()==image
        after=cli_guard()
        return dict(delivered=True,no_backup_created=True,installed_bytes_equal_tested_candidate=True,
            pre_guard=before,post_guard=after,**q)
    except BaseException:
        # Retain no backup file. Restore our own unverified install from the
        # held parent bytes; leave any concurrent user replacement untouched.
        if ROM.read_bytes()==image:
            ROM.write_bytes(parent)
            assert check(ROM)==before
        raise

if __name__=='__main__':
    print('RESULT '+json.dumps(execute(),separators=(',',':')),flush=True)
