"""Directed original Up/climb alignment sweep; no ROM or fixture files."""

from hashlib import sha256
import argparse
import json
import inspect
from pathlib import Path
from unittest.mock import patch

import check_prince_pickup_reach_1112 as Probe


PIN = 'a3c5fa63872fbb3103ae57d9748fef233e8b2273e26d985aa4006b2492d81b8a'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--placed-flower', action='store_true')
    parser.add_argument('--forward-nudge', action='store_true')
    args = parser.parse_args()
    assert not (args.placed_flower and args.forward_nudge)
    raw = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    assert sha256(raw).hexdigest() == PIN
    Probe.Packet.extract(raw)
    seed, _ = Probe.B.cold(raw)
    original_put, original_terrain, original_invoke = Probe.B.N.put, Probe.B.terrain, Probe.B.N.invoke
    episode = Probe.current_episode
    if args.placed_flower:
        namespace = dict(Probe.__dict__)
        source = inspect.getsource(episode)
        assert source.count('range(180)') == 1
        exec(source.replace('range(180)', 'range(280)'), namespace)
        episode = namespace['current_episode']
    rows = []
    cases = ((255, (1218, 1220, 1224)),) if args.placed_flower else (
        ((255, (1214,)),) if args.forward_nudge else (
        (255, range(1214, 1232, 2)), (0, range(1278, 1296, 2))))
    controls = [(n, pause) for n in (1, 4, 8, 12, 16, 24) for pause in (0, 8)] if args.forward_nudge else [(0, 0)]
    for forward, pause in controls:
      for face, positions in cases:
        for x in positions:
            returning, picked = False, None
            def put(model, **fields):
                nonlocal returning
                if fields.get('SelectedCharacter') == 38:
                    fields.update(Player_X_Position=x & 255, Player_PageLoc=x >> 8,
                                  Player_Rel_XPos=x-1148, ScreenLeft_X_Pos=124,
                                  ScreenLeft_PageLoc=4, ScreenRight_X_Pos=123, ScreenRight_PageLoc=5)
                    if args.placed_flower:
                        fields['PlayerStatus'] = 1
                        for name, value in dict(Enemy_Flag=1, Enemy_ID=46, Enemy_State=128,
                                PowerUpType=1, Enemy_X_Position=224, Enemy_PageLoc=4,
                                Enemy_Y_Position=119, Enemy_Y_HighPos=1,
                                Enemy_BoundBoxCtrl=9, Enemy_MovingDir=1).items():
                            model[Probe.B.N.address(model.bundle, name)+5] = value
                elif args.placed_flower and 'FrameCounter' in fields:
                    returning |= Probe.B.N.get(model, 'Player_Y_Position') <= 114
                    if returning:
                        fields.update(SavedJoypad1Bits=2, SavedJoypadBits=2)
                elif args.forward_nudge and 'FrameCounter' in fields:
                    epoch = fields['FrameCounter']
                    pad = 0 if epoch < 16 else 1 if epoch < 16+forward else 0 if epoch < 16+forward+pause else 8
                    fields.update(SavedJoypad1Bits=pad, SavedJoypadBits=pad)
                return original_put(model, **fields)

            def terrain(model, _historical_fixture):
                return original_terrain(model, lambda col, y:
                    (0xc4 if col == 224 else 0x51) if col in (208, 224, 240) and y == 144
                    else 0x54 if y >= 208 else 0)

            def invoke(model, entry, *call_args, **call_fields):
                nonlocal picked
                result = original_invoke(model, entry, *call_args, **call_fields)
                if args.placed_flower and entry == 'PlayerCtrlRoutine':
                    world_x = Probe.B.N.get(model, 'Player_X_Position')+256*Probe.B.N.get(model, 'Player_PageLoc')
                    camera = Probe.B.N.get(model,'ScreenLeft_X_Pos')+256*Probe.B.N.get(model,'ScreenLeft_PageLoc')
                    original_put(model, Player_Rel_XPos=(world_x-camera)&255,
                                 Player_Rel_YPos=Probe.B.N.get(model, 'Player_Y_Position'))
                    original_invoke(model, 'HuFullBox', x=0)
                    if Probe.B.N.get(model, 'Enemy_Flag', 5):
                        original_invoke(model, 'PowerUpObjHandler', x=5)
                    if model.ram[2][0x6ee] and picked is None:
                        picked = dict(x=world_x, y=Probe.B.N.get(model,'Player_Y_Position'),
                                      sword=model.ram[2][0x6ee], actor_erased=not Probe.B.N.get(model,'Enemy_Flag',5))
                return result

            with patch.object(Probe.B.N, 'put', put), patch.object(Probe.B, 'terrain', terrain), \
                    patch.object(Probe.B.N, 'invoke', invoke):
                result = episode(seed, dict(poses=[]), b'', row=True, facing=face)
            frames = result['rows']
            climbed = [p for p in frames if p['native_y'] <= 114]
            rows.append(dict(x=x, facing=face, forward=forward, neutral=pause,
                             minimum_y=min(p['native_y'] for p in frames),
                             first_cap=climbed[0] if climbed else None,
                             last=frames[-1], native_effects=len(result['native_effects']),
                             placed_flower_collected=picked))
    print(json.dumps(dict(passed=True, ROM_SHA256=PIN, rows=rows, output_files=0,
        scope='Directed position and terrain fixtures executing the live original controller. '
              'Optional flower is explicitly placed mature; no natural route or Mesen claim.')), flush=True)
    if args.placed_flower:
        assert all(row['placed_flower_collected'] and row['placed_flower_collected']['sword']==1
                   and row['placed_flower_collected']['actor_erased'] for row in rows)


if __name__ == '__main__':
    main()
