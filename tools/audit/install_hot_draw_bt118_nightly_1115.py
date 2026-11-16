"""Direct no-backup delivery of the native-qualified Battletoads drawing change."""
from pathlib import Path
import json
import compose_hot_draw_bt_67e_1115 as C
import replay_hot_draw_bt_67e_1115 as F
import replay_battletoads_stair_progress_1115 as S
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check

OUT=C.R/'build/smb2-flag-native-1113'
GRANT=C.R/'docs/qa/allocations/hot-draw-bt118-delivery-1115.json'

if __name__=='__main__':
    g=json.loads(GRANT.read_bytes())
    assert g['direct_Downloads_replacement_authorized']and not g['backups_allowed']and not g['releases_and_patch_assets_allowed']
    assert set(g['private_native_receipts'])=={'cadence','rash','zitz'}
    assert g['parent_SHA256']==C.PIN and g['candidate_SHA256']==C.CANDIDATE and Path(g['destination'])==C.ROM
    for module,key in((C,'composer_SHA256'),(F,'cadence_factory_SHA256'),(S,'stage_factory_SHA256')):
        assert C.H(Path(module.__file__).read_bytes())==g[key]
    before=check(C.ROM);old=C.ROM.read_bytes();assert C.H(old)in(C.PIN,C.CANDIDATE)
    candidate=(OUT/'candidate.nes').read_bytes();assert C.H(candidate)==C.CANDIDATE
    parent=C.inverse(candidate);assert C.H(parent)==C.PIN and old in(parent,candidate)
    assert candidate[:C.FILE]==parent[:C.FILE]and candidate[C.FILE+C.SIZE:]==parent[C.FILE+C.SIZE:]
    assert candidate[C.FILE:C.FILE+C.SIZE]==C.NEW and len(candidate)==2097168
    assert check(OUT/'candidate.nes')['ROM_sha256']==C.CANDIDATE
    require_free_workspace(C.R,C.ROM,allow_interactive=True)
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    C.ROM.write_bytes(candidate);after=check(C.ROM);assert C.ROM.read_bytes()==candidate
    print(json.dumps(dict(installed=True,SHA256=C.CANDIDATE,bytes=len(candidate),destination=str(C.ROM),
        before=before,after=after,backups=0,actual_Downloads_repeats_still_required=True),separators=(',',':')),flush=True)
