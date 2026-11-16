"""Two passive missile-tank/HUD RAM pictures over the qualified MF route."""
from hashlib import sha256
from pathlib import Path
import json
import replay_rogue_natural_mf_1327_1116 as F
import run_rogue_tank_images_root_1116 as Pictures
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run

OUT = F.R/'build/smb2-flag-native-1113'
BASE_FACTORY = '1e91a4a715c7aaad49323ceb78a6572c63267debf363d2188f0569cff1853d22'
BASE_LUA = '5ac547235ec8a2f5a4f9d2675d34ab8fc1b105e3e725452e2c349e392a75db85'
PICTURES = '7823bb1bc64c7f8c31ef9afa286cbc66f44ccb05587c833dd40a068d9118b694'
NATIVE = '0bb87954b6b9cb9d19b0441a31f0a4d8f21726f06965f3328375c059ec1ca1ab'


def controller(raw):
    assert F.H(Path(F.__file__).read_bytes()) == BASE_FACTORY
    assert F.H(Path(Pictures.__file__).read_bytes()) == PICTURES
    base = F.controller(raw)
    assert F.H(base.encode()) == BASE_LUA
    edits = [
        ('if finished then return end;finished=true',
         "if finished then return end;if reason=='natural-tank-missile-credit-and25workers'then assert(#visual.pictures==2,'Both actual missile pictures')end;finished=true"),
        ('Mesen_images=0}', 'Mesen_images=2,visual=visual}'),
    ]
    text = base
    for a, b in edits:
        assert text.count(a) == 1
        text = text.replace(a, b, 1)
    restored = text
    for a, b in reversed(edits):
        restored = restored.replace(b, a, 1)
    assert restored == base
    observer = Pictures.OBSERVER
    changes = [
        ('#visual.pictures==0 and mature and not collector',
         "#visual.pictures==0 and stock=='missile'and mature and not collector"),
        ('#visual.pictures==1 and credit', "#visual.pictures==1 and stock=='missile-credit'and credit"),
        ('Mature Rogue energy tank', 'Mature Rogue missile tank'),
        ('Earned tank and resumed Rogue', 'Earned missiles and Rogue HUD'),
        ('state=state(),PNG_bytes=#png', 'state=state(),item=mature.actor,PNG_bytes=#png'),
    ]
    for a, b in changes:
        assert observer.count(a) == 1
        observer = observer.replace(a, b, 1)
    text = 'local visual={pictures={}}\n'+text+'\n'+observer
    F.LuaRuntime().compile(text)
    return text


def main():
    raw = F.ROM.read_bytes()
    assert F.H(raw) == F.PIN
    before = check(F.ROM)
    assert not before['matching_patch_files']
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    assert (OUT/'candidate.nes').read_bytes() == raw
    text = controller(raw)
    Storage.preflight(private_root=OUT, fresh=True)
    require_free_workspace(F.R, F.ROM, allow_interactive=True)
    script = OUT/'controller.lua'
    script.write_bytes(text.encode())
    q = run(script, F.ROM, OUT/'capture', F.PIN, 180)
    assert F.ROM.read_bytes() == (OUT/'candidate.nes').read_bytes() == raw
    assert check(F.ROM) == before and q['outputs_written'] == 0
    functional = dict(q['receipt'])
    functional.pop('visual', None)
    functional['Mesen_images'] = 0
    digest = sha256(json.dumps(functional, sort_keys=True).encode()).hexdigest()
    report = {k: v for k, v in q.items() if k not in ('images', 'capture_preflight')}
    report.update(actual_Downloads=True, functional_receipt_SHA256=digest,
                  exact_functional_match=digest == NATIVE,
                  image_metadata=[{k: v for k, v in im.items() if k != 'base64'} for im in q['images']])
    for im in q['images']:
        assert im['bytes'] <= 65536
        print('IMAGE '+json.dumps(im, separators=(',', ':')), flush=True)
    print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
    assert q['passed'] and len(q['images']) == 2 and digest == NATIVE


if __name__ == '__main__':
    main()
