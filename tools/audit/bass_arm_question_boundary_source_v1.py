"""One real compiled ARM -> question transaction; no native/emulator run."""
from pathlib import Path
import argparse
import hashlib
import json
import traceback
from link_pit_rygar_sophia_audit_cpu import scoped_load, Arena

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
B = D / 'root-current-roster-composition-v1'
SHA = '3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    rows = []
    try:
        assert sha(B/'candidate.nes') == SHA
        b = scoped_load(B/'candidate.nes')
        q = Arena(b, 9)
        q.put(CrossoverBehaviorVersion=0, PlayerStatus=1, OperMode_Task=3,
              Player_X_Position=32, Player_PageLoc=0, Player_Y_Position=176,
              Player_Y_HighPos=1, Player_State=0, PlayerFacingDir=1, PlayerSize=0,
              ScreenLeft_PageLoc=0, ScreenLeft_X_Pos=0, ScreenRight_PageLoc=0,
              ScreenRight_X_Pos=255, AreaType=1)
        q.set('InvOwnedLo', 3, 9)
        q.set('InvSelected', 1, 9)
        q.set('InvAmmo', 112, 145)
        for i in range(416):
            for n in ['Block_Buffer_1', 'MmSolidTerrain', 'MmBrickHealth']:
                q.set(n, 0, i)
        for page in range(2):
            for col in range(16):
                q.set('Block_Buffer_1', 0x54, page*208+176+col)
        q.set('Block_Buffer_1', 0x51, 163)
        q.set('Block_Buffer_1', 0xc1, 116)
        q.set('Block_Buffer_1', 0x51, 117)
        player = ['Player_X_Position', 'Player_PageLoc', 'Player_Y_Position',
                  'Player_Y_HighPos', 'PlayerSize', 'CrouchingFlag', 'Player_Y_Speed']
        for tick in range(65):
            q.set('FrameCounter', tick)
            pressed = 64 if tick in [0, 4] else 0
            q.set('SavedJoypadBits', pressed)
            q.set('InvFresh', pressed)
            before = [q.get(n) for n in player]
            c, writes = q.invoke('SpecialWeapons')
            assert before == [q.get(n) for n in player], ('Player restore', tick)
            rows.append(dict(tick=tick, cycles=c.processorCycles,
                held=q.get('SsHeld'), ammo=q.get('InvAmmo',145),
                lift_cell=q.get('Block_Buffer_1',163), question=q.get('Block_Buffer_1',116),
                neighbor=q.get('Block_Buffer_1',117),
                types=[q.get('RgShotType',i) for i in range(10)],
                reward={n:q.get(n,5) for n in ['Enemy_Flag','Enemy_ID','Enemy_State',
                    'InvPickup','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position']},
                player_restored=True))
            if q.get('Enemy_Flag',5):
                break
        assert rows[0]['held'] > 0 and rows[0]['lift_cell'] == 0
        assert rows[4]['held'] == 0 and rows[4]['ammo'] == 104
        last = rows[-1]
        assert last['reward']['Enemy_Flag'] != 0 and last['reward']['Enemy_ID'] == 0x2e
        assert last['reward']['Enemy_X_Position'] == 64 and last['reward']['Enemy_PageLoc'] == 0
        assert last['neighbor'] == 0x51 and last['types'].count(21) == 4
        proof = dict(passed=True,source_only=True,native_run=False,ROM_sha256=SHA,
            component_calls=len(rows),question_contact_tick=last['tick'],
            free_actual_lift=True,actual_throw_cost=8,four_independent_fragments=True,
            native_powerup_actor_and_question_origin=True,adjacent_masonry_preserved=True,
            player_seven_fields_restored_on_all_returns=True,
            limits='One configured CPU transaction. Before inputs explicitly set powered Bass/ARM ownership/stock/selection, map and source button-edge fields. FrameCounter is stepped by fixture; complete GameLoop/real controller/NMI/PPU/bounce/rise/acquisition are NOT executed or claimed. No current source hardlock established; this cannot close the native reported freeze.',
            tool_sha256=sha(__file__))
        (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
        print(json.dumps(proof,indent=2))
    except BaseException as error:
        (a.output/'failure.json').write_text(json.dumps(dict(passed=False,error=repr(error),traceback=traceback.format_exc(),completed_calls=len(rows)),indent=2)+'\n')
        (a.output/'failed-tool.py').write_bytes(Path(__file__).read_bytes())
        raise
    finally:
        (a.output/'calls.json').write_text(json.dumps(rows,indent=2)+'\n')


if __name__=='__main__':
    main()
