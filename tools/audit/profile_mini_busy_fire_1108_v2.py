"""Attribute complete busy Mini GameCore work to real linked routines and banks."""

import argparse
from collections import Counter
import json
from pathlib import Path

from measure_mini_busy_fire_1108_v1 import N, PARENT, PIN, address, apply, bundle, game_seed, location, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = PARENT.read_bytes()
    assert sha(raw) == PIN
    result = json.loads((args.output / 'result.json').read_text())
    images = [('baseline', bundle(raw)), ('successor', bundle(apply(raw, result['patches'])))]
    routines = ('GameCoreRoutine FireballObjCore FireballEnemyCollision FireballBGCollision '
                'DrawFireball RelativeFireballPosition GetFireballOffscreenBits GetXOffscreenBits '
                'GetYOffscreenBits GetFireballBoundBox BoundingBoxCore CheckRightScreenBBox '
                'SprObjectCollisionCore EnemiesAndLoopsCore RunEnemyObjectsCore EnemyGfxHandler '
                'RunNormalEnemiesProc RelativeEnemyPosition GetEnemyOffscreenBits GetEnemyBoundBox '
                'EnemyToBGCollision GetOffScreenBitsSet MoveNormalEnemy DrawAll MetaspriteRenderLoop '
                'PlayerEnemyCollision EnemyCollisionCore ProcFireball_Bubble ChkUnderEnemy '
                'GetMaskedOffScrBits BlockBufferCollision EnemyToEnemyCollision RunEnemyObjectsCore '
                'RedPTroopaDraw EnemyMovementSubs RunNormalEnemies NormalEnemyOffscreenBits '
                'EnemyGraphicsEngine ProcessGoomba SprObjectOffscrChk NormalEnemyBoundBox '
                'Mmc5GroundGoombaTerrain EnemyToBGCollisionDet EnemiesCollision '
                'RemainingNormalPlayerCollision OffscreenBoundsCheck JumpEngine '
                'RemainingEnemyFrozen PlayerCollisionCore EasyPlayerEnemyCollision '
                'InventoryUpdateDrops Z2UpdateDropsGate FloateyNumbersCore DrawAllMetasprites '
                'SamusFreezeDrawAll HpProcessFireballsBridge GuestGameRoutinesBridge '
                'GuestPostEnemyCollision PlayerGfxHandler Main MiniNativeDraw '
                'PlayerOAMReservation PlayerMovementSubs ColorRotation ScrollHandler').split()
    points = {}
    for name in routines:
        if name in images[0][1]['syms']:
            physical = (location(images[0][1], name)-16)//8192
            points[physical|128, address(images[0][1], name)] = name
    points.update({(217, 0xbcc0): 'MiniFireballTail', (217, 0xbdba): 'MiniFireballDraw'})
    rows = []
    native = N.NesMPU
    for label, image in images:
        for enemies in (0, 3, 5):
            m = game_seed(image, enemies)
            frame_rows = []
            bank_cycles, routine_cycles, routine_entries = Counter(), Counter(), Counter()
            call_frames = []

            class Trace(native):
                def step(self):
                    pc = self.pc
                    while call_frames and call_frames[-1][:2] == (pc, self.sp):
                        call_frames.pop()
                    tag = m.rawtags[(pc-0x8000)//8192] if pc >= 0x8000 else -1
                    name = points.get((tag, pc))
                    if name:
                        return_pc = (m[0x100+((self.sp+1)&255)] | (m[0x100+((self.sp+2)&255)]<<8)) + 1
                        call_frames.append((return_pc, (self.sp+2)&255, name))
                        routine_entries[name] += 1
                    before = self.processorCycles
                    exits_dispatch = call_frames and call_frames[-1][2] == 'JumpEngine' and m[pc] == 0x6c
                    native.step(self)
                    cost = self.processorCycles-before
                    bank_cycles[tag] += cost
                    if call_frames:
                        routine_cycles[call_frames[-1][2]] += cost
                    if exits_dispatch:
                        call_frames.pop()

            N.NesMPU = Trace
            try:
                for frame in range(32, 48):
                    call_frames.clear()
                    buttons = 64 if frame in (35, 37) else 0
                    N.put(m, FrameCounter=frame, SavedJoypadBits=buttons, SavedJoypad1Bits=buttons,
                          A_B_Buttons=buttons, PreviousA_B_Buttons=64 if frame in (36, 38) else 0,
                          Left_Right_Buttons=0, Up_Down_Buttons=0)
                    out = N.invoke(m, 'GameCoreRoutine', x=0, y=0)
                    active = sum(N.get(m, 'Fireball_State', slot) == 1 for slot in (0, 1))
                    frame_rows.append((frame, out['CPU'], active))
            finally:
                N.NesMPU = native
            assert sum(bank_cycles.values()) == sum(row[1] for row in frame_rows)
            rows.append(dict(image=label, initial_native_enemies=enemies, frames=frame_rows,
                             bank_cycles=bank_cycles.most_common(), entries=routine_entries.most_common(),
                             exclusive_attributed_cycles=routine_cycles.most_common()))
    (args.output/'busy-profile.json').write_text(json.dumps(rows, indent=2)+'\n')
    for row in rows:
        if row['initial_native_enemies'] in (3, 5):
            print(row['image'], row['initial_native_enemies'], row['exclusive_attributed_cycles'][:20])


if __name__ == '__main__':
    main()
