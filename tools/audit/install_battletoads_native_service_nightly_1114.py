"""Direct Downloads replacement; repeat the exact private native gates."""
from hashlib import sha256
import json
from pathlib import Path

import compose_battletoads_native_service_1114 as C
import replay_battletoads_native_service_1114 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run

OUT=C.R/'build/smb2-flag-native-1113'
DESTINATION=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
SOURCE_PINS={C:'8538602ad33401a7083f5c83a18f3b72f9ba60a2390c8a5b1cc297890cb742fa',
             F:'82c0001e03582ad10dea43bab78a87d27b1a0f8d5d220cf95441aa40aa91475a'}
CASES={
 'reads':('404f3208118e9061fe242b20954ea0c61b5b16473f32f65eafc139d79f612854','46bb457dc547b0660cb80a68d2895c993c9570a6c23b4544389cbf363f1bfb0a'),
 'rash':('b178e16d40681ffa08e4fc24f7fcd3c6df247a4aa490544e0efd400b368c8a80','a57a3339a6c5e42e777f9b1b0368e3a6c27ba35d5fce71417afca1ec13d63652'),
 'zitz':('a93c56ff35f877a2c14a8229b59a4fe89709ff81abadddd114f9efc4d996d15d','581e7f685679393638d9b5e54f1ace1815dee83d3b609e4128d820bbac2219e8')}


def digest(data):return sha256(data).hexdigest()


def install():
    for module,pin in SOURCE_PINS.items():assert digest(Path(module.__file__).read_bytes())==pin
    assert{p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    image=(OUT/'candidate.nes').read_bytes();parent=C.inverse(image);assert C.proposal(parent)[0]==image
    before=check(DESTINATION);previous=DESTINATION.read_bytes()
    assert digest(previous)==before['ROM_sha256']and before['ROM_sha256']in(C.PIN,C.CANDIDATE)
    texts={'reads':F.cadence_reads(image),'rash':F.controller(image,'rash'),'zitz':F.controller(image,'zitz')}
    for key,text in texts.items():assert digest(text.encode())==CASES[key][0]
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    require_free_workspace(C.R,DESTINATION,allow_interactive=True)
    assert DESTINATION.read_bytes()==previous
    DESTINATION.write_bytes(image)
    assert DESTINATION.read_bytes()==image==(OUT/'candidate.nes').read_bytes()
    after=check(DESTINATION);assert after['ROM_sha256']==C.CANDIDATE
    rows=[]
    try:
        for key,text in texts.items():
            script=OUT/'controller.lua';script.write_bytes(text.encode())
            q=run(script,DESTINATION,OUT/'capture',C.CANDIDATE,240)
            assert q['passed']and(q['script_SHA256'],q['receipt_SHA256'])==CASES[key]
            assert not q['images']and q['outputs_written']==0
            receipt=q['receipt']
            rows.append(dict(case=key,script_SHA256=q['script_SHA256'],receipt_SHA256=q['receipt_SHA256'],
                Main=receipt['Main_returned'],physical_frames=receipt['physical_frames'],terminal=receipt['terminal'],
                read_observations=receipt.get('controller_read_observations'),next_updates=receipt.get('next_area_updates')))
            print('VERIFIED '+json.dumps(rows[-1],separators=(',',':')),flush=True)
        assert DESTINATION.read_bytes()==image==(OUT/'candidate.nes').read_bytes()and check(DESTINATION)==after
    except BaseException:
        assert DESTINATION.read_bytes()==image,'Concurrent destination change; left untouched'
        DESTINATION.write_bytes(previous)
        assert digest(DESTINATION.read_bytes())==before['ROM_sha256']and check(DESTINATION)==before
        print('ROLLED_BACK_TO_VERIFIED_INPUT '+before['ROM_sha256'],flush=True)
        raise
    return dict(passed=True,installed_ROM=str(DESTINATION),SHA256=C.CANDIDATE,previous_SHA256=before['ROM_sha256'],
        installed_bytes_equal_tested_candidate=True,actual_Downloads_launches=rows,pre_and_post_patch_guard=True,
        partial_performance_improvement=True,literal_idle_walk_lag_still_open=True,
        backups=0,patch_assets=0,releases_created=0,capture_files=0)


if __name__=='__main__':print('RESULT '+json.dumps(install(),separators=(',',':')),flush=True)
