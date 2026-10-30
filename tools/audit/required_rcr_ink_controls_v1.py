"""Execute all RCR source poses and real Main with mandatory intrinsic ink."""
from pathlib import Path
import itertools
import json
import sys

R = Path(__file__).resolve().parents[2]
O = R/'build/required-rcr-ink-v2'
sys.path[:0] = [str(R/'tools'), str(R/'tools/audit')]
from prepare_required_rcr_ink_v2 import sha
from link_pit_rygar_sophia_audit_cpu import scoped_load
from river_city_pipe_contact_controls_v2 import fixture, position, pipe
from sunny_integrated_controls_v1 import run, registers, app
from prepare_river_city_controls import address
from prepare_river_city_assets import POSES, decode
from prepare_river_city_reference import NATIVE, native_pixels


def pixels(q, bundle):
    image = {}
    count = q.get('CurrentOAMOffset')//4
    for part in range(count-1, -1, -1):
        tile = q.get('Sprite_Tilenumber', part*4)
        attr = q.get('Sprite_Attributes', part*4)
        xx = q.get('Sprite_X_Position', part*4)-96
        yy = q.get('Sprite_Y_Position', part*4)-96
        window = tile//64
        page = q.get('CurrentCHRBank', window)+256*(q.get('X5ChrMode', window)&3)
        at = 1048592+page*1024+(tile%64)*16
        pattern = decode(bundle['raw'][at:at+32])
        for y in range(16):
            for x in range(8):
                color = pattern[15-y if attr&128 else y][7-x if attr&64 else x]
                if color:
                    image[xx+x, yy+y] = 1 if attr&3 == 3 else {1:3, 2:2, 3:4}[color]
    return image, count


def draw(bundle, variant, face, pose, off):
    q = fixture(bundle, variant)
    q.put(PlayerFacingDir=face, PlayerOutlinesOff=off, OutlineSourceHi=204,
          CurrentOAMOffset=0)
    q.array('OutlineTinyHi', [204]*4)
    q.array('CurrentCHRBank', [99,100,101,102])
    q.array('X5ChrMode', [129]*4)
    q.invoke('RcSetPose', x=pose)
    q.invoke('RcPublish')
    ptr = q.get('SmPosePtr')+256*q.get('SmPosePtr', 1)
    q.put(R0=ptr&255, R1=ptr>>8, R3=0, R4=96, R5=0, R6=96, R7=1,
          GuestOamRotationActive=0)
    c, _ = q.invoke('MetaspriteRenderLoop')
    assert c.p&1 and q.get('PlayerOutlinesOff') == off
    image, count = pixels(q, bundle)
    return image, count


def main():
    target = O/'controls.json'
    assert not target.exists()
    proof = json.loads((O/'build-proof.json').read_text())
    for path, digest in proof['bindings'].items():
        assert sha(path) == digest, path
    assert sha(O/'candidate/candidate.nes') == proof['ROM_sha256']
    old, new = [scoped_load(p) for p in [R/'build/character-host-union-resources-v1/ice/candidate.nes',
                                        O/'candidate/candidate.nes']]
    original = NATIVE.read_bytes()
    rows, missing = [], []
    for variant, face, pose in itertools.product(range(2), [1,2], range(18)):
        source, _, _ = native_pixels(original, POSES[pose][1], variant, face)
        expected, expected_parts = draw(old, variant, face, pose, 0)
        assert expected == source, ('Original native-source pixels', variant, face, pose)
        omitted, _ = draw(old, variant, face, pose, 1)
        missing.append(len(set(expected)-set(omitted)))
        for off in range(2):
            actual, parts = draw(new, variant, face, pose, off)
            assert actual == expected and parts == expected_parts, (variant, face, pose, off)
            assert sum(color == 1 for color in actual.values()) > 0
            rows.append(dict(variant=variant, face=face, pose=pose, Shadows_off=off,
                             original_opaque_pixels=len(source),
                             original_black_pixels=sum(c == 1 for c in source.values()),
                             actual_parts=parts))
    assert min(missing) > 0, 'Retained old setting must reproduce real missing opaque pixels'
    main_rows = []
    for variant, face, bits, off in itertools.product(range(2), [1,2], [0,64,128], range(2)):
        pair = []
        for bundle, setting in [(old,0), (new,off)]:
            q = fixture(bundle, variant)
            pipe(q, 448)
            position(q, 400, 176, 0, face, state=0)
            q.put(OperMode_Task=3, GameEngineSubroutine=8, PlayerEntranceCtrl=2,
                  GameTimerDisplay=4, RcHudDirty=0, PlayerOutlinesOff=setting,
                  SavedJoypadBits=face|bits, Left_Right_Buttons=face, A_B_Buttons=bits,
                  Player_Rel_XPos=96, Player_Rel_YPos=176,
                  ScreenRight_PageLoc=1, ScreenRight_X_Pos=255)
            c, writes, _ = run(q, 'GameLoop', p=0x71)
            assert q.get('RcClock') == 1 and q.get('PlayerOutlinesOff') == setting
            state = (registers(c), app(q, skip=[address(bundle,'PlayerOutlinesOff')]),
                     tuple(q.m.banks), bytes(q.m[0x100:0x17b]))
            pair.append((state, c.processorCycles))
        assert pair[0][0] == pair[1][0], ('Actual complete Main', variant, face, bits, off)
        main_rows.append(dict(variant=variant, face=face, buttons=bits, Shadows_off=off,
                              CPU_delta=pair[1][1]-pair[0][1]))
    bindings = dict(proof['bindings'])
    for path in [Path(__file__).resolve(), O/'build-proof.json', NATIVE,
                 R/'tools/river_city_pipe_contact_controls_v2.py',
                 R/'tools/prepare_river_city_controls.py',
                 R/'tools/prepare_river_city_assets.py', R/'tools/prepare_river_city_reference.py',
                 R/'tools/audit/sunny_integrated_controls_v1.py']:
        bindings[str(path)] = sha(path)
    result = dict(passed=True, native=False, source_CPU_only=True,
                  ROM_sha256=proof['ROM_sha256'], actual_original_pixel_pose_pairs=rows,
                  original_ShadowOff_missing_opaque_pixels_range=[min(missing), max(missing)],
                  actual_complete_Main_pairs=main_rows,
                  comparison='Candidate bothsettings vs unchanged original ShadowsON, only the user preference byte excluded from fullMain RAM equality. AXYP/SP/livepage1/maps/all other application bytes exact.',
                  unchanged_foreign_code_header_CHR_and_all_symbol_values=True,
                  global_preference_never_changed=True, bindings=bindings,
                  limits=['Actual assembled CPU/OAM/native-source pixel comparison, not native video/FPS.',
                          'Arthur is separately audited; this leaf changes only Ryan/Alex.'])
    target.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(passed=True, pose_pairs=len(rows), complete_Main_pairs=len(main_rows),
                          old_off_missing_pixels=result['original_ShadowOff_missing_opaque_pixels_range'])))


if __name__ == '__main__':
    main()
