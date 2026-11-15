"""Direct, no-backup delivery of the exact native-qualified point67 candidate."""
from hashlib import sha256
from pathlib import Path
import json
import compose_prince_hidden_point67_ace_1115 as C
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check

ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
OUT=C.R/'build/smb2-flag-native-1113'
GRANT=C.R/'docs/qa/allocations/prince-hidden-point67-delivery-1115.json'

if __name__=='__main__':
    grant=json.loads(GRANT.read_bytes())
    assert grant['direct_Downloads_replacement_authorized']
    assert set(grant['private_native_receipts'])=={'full','star'}
    assert all(len(x)==64 for x in grant['private_native_receipts'].values())
    assert not grant['backups_allowed']and not grant['releases_and_patch_assets_allowed']
    assert sha256(Path(C.__file__).read_bytes()).hexdigest()==grant['composer_SHA256']
    assert Path(grant['destination'])==ROM and grant['candidate_SHA256']==C.CANDIDATE
    before=check(ROM);old=ROM.read_bytes()
    assert sha256(old).hexdigest()in(C.PIN,C.CANDIDATE)
    candidate=(OUT/'candidate.nes').read_bytes();assert sha256(candidate).hexdigest()==C.CANDIDATE
    parent=C.inverse(candidate);assert old in(parent,candidate)and C.proposal(parent)[0]==candidate
    assert check(OUT/'candidate.nes')['ROM_sha256']==C.CANDIDATE
    require_free_workspace(C.R,ROM,allow_interactive=True)
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    ROM.write_bytes(candidate);after=check(ROM);assert ROM.read_bytes()==candidate
    print(json.dumps(dict(installed=True,SHA256=C.CANDIDATE,bytes=len(candidate),
        destination=str(ROM),before=before,after=after,backups=0,
        actual_Downloads_repeats_still_required=True),separators=(',',':')),flush=True)
