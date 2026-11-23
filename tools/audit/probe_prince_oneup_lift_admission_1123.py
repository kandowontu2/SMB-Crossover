"""Test an isolated 1-1 lift admission leaf using the stock platform constructor."""

import json

from compose_gimmick_empty_side_1115 import assemble
import probe_prince_wram1_funding_1123 as Funding

F, H, N, W = Funding.F, Funding.H, Funding.N, Funding.W
ORIGIN = 0xA200  # An isolated CPU fixture address, with no production allocation.
FIRST_CAMERA_X = 721
LAST_CAMERA_X = 752

ASM = """
 php
 pha
 lda SelectedCharacter
 cmp #38
 bne Finish
 lda GameEngineSubroutine
 cmp #8
 bne Finish
 lda WorldNumber
 ora LevelNumber
 ora TimerControl
 bne Finish
 lda GamePauseStatus
 lsr a
 bcs Finish
 lda AreaType
 cmp #1
 bne Finish
 lda AreaAddrsLOffset
 cmp #5
 bne Finish
 lda ScreenLeft_PageLoc
 cmp #2
 bne Finish
 lda ScreenLeft_X_Pos
 cmp #FirstCameraLow
 bcc Finish
 cmp #AfterCameraLow
 bcc Eligible
Finish:
 pla
 plp
 rts
Eligible:
 txa
 pha
 tya
 pha
 ldx #5
 ldy #$FF
Scan:
 lda Enemy_Flag,x
 bne InUse
 cpy #$FF
 bne Next
 txa
 tay
 bpl Next
InUse:
 lda Enemy_ID,x
 cmp #$25
 bne Next
 lda Enemy_PageLoc,x
 cmp #3
 bne Next
 lda Enemy_X_Position,x
 cmp #$F0
 beq Restore
Next:
 dex
 bpl Scan
 tya
 bmi Restore
 tax
 lda ObjectOffset
 pha
 stx ObjectOffset
 lda #1
 sta Enemy_Flag,x
 sta Enemy_Y_HighPos,x
 lda #$25
 sta Enemy_ID,x
 lda #3
 sta Enemy_PageLoc,x
 lda #$F0
 sta Enemy_X_Position,x
 lda #$C0
 sta Enemy_Y_Position,x
 lda #0
 sta Enemy_State,x
 sta SafeA
 lda #ConstructorLow
 sta TargetLo
 lda #>Constructor
 sta TargetHi
 lda #ConstructorBank
 jsr FarCallCommon
 ldx ObjectOffset
 lda #5
 sta Enemy_BoundBoxCtrl,x
 lda #$FF
 sta PlatformCollisionFlag,x
 pla
 sta ObjectOffset
Restore:
 pla
 tay
 pla
 tax
 jmp Finish
"""


def machine_code(seed):
    bundle = seed.bundle
    keys = ('SelectedCharacter GameEngineSubroutine WorldNumber LevelNumber '
            'TimerControl GamePauseStatus AreaType AreaAddrsLOffset '
            'ScreenLeft_PageLoc ScreenLeft_X_Pos Enemy_Flag Enemy_ID Enemy_PageLoc '
            'Enemy_X_Position Enemy_Y_Position Enemy_Y_HighPos Enemy_State '
            'Enemy_BoundBoxCtrl PlatformCollisionFlag ObjectOffset FarCallCommon')
    symbols = {name: W.address(bundle, name) for name in keys.split()}
    target = W.address(bundle, 'FarcallJmpTarget_SMC') + 1
    constructor = W.address(bundle, 'CheckpointEnemyID')
    bank = (W.location(bundle, 'CheckpointEnemyID') - 16) // 8192
    assert 0xA000 <= constructor < 0xC000 and 0 <= bank < 128
    symbols.update(SafeA=W.address(bundle, 'SafecallA_SMC') + 1,
                   TargetLo=target, TargetHi=target + 1, Constructor=constructor,
                   ConstructorLow=constructor & 255, ConstructorBank=bank | 128,
                   FirstCameraLow=FIRST_CAMERA_X & 255,
                   AfterCameraLow=(LAST_CAMERA_X + 1) & 255)
    code, _ = assemble(ASM, symbols, ORIGIN)
    assert len(code) <= 208
    return code


FIELDS = ('Enemy_Flag Enemy_ID Enemy_State Enemy_PageLoc Enemy_X_Position '
          'Enemy_Y_Position Enemy_Y_HighPos Enemy_BoundBoxCtrl '
          'PlatformCollisionFlag YPlatformTopYPos YPlatformCenterYPos').split()


def rows(model):
    return [tuple(N.get(model, field, index) for field in FIELDS) for index in range(6)]


def exercise(seed, code, camera=FIRST_CAMERA_X, occupied=(), existing=None, **override):
    model = N.fork(seed)
    fields = dict(SelectedCharacter=38, GameEngineSubroutine=8, WorldNumber=0,
                  LevelNumber=0, TimerControl=0, GamePauseStatus=0, AreaType=1,
                  AreaAddrsLOffset=5, ScreenLeft_PageLoc=camera >> 8,
                  ScreenLeft_X_Pos=camera & 255, ObjectOffset=3)
    N.put(model, **(fields | override))
    for i in range(6):
        F.slot(model, 'Enemy_Flag', int(i in occupied), i)
        F.slot(model, 'Enemy_ID', 6, i)
    if existing is not None:
        for name, value in (('Enemy_Flag', 1), ('Enemy_ID', 37),
                            ('Enemy_PageLoc', 3), ('Enemy_X_Position', 240)):
            F.slot(model, name, value, existing)

    start = ORIGIN - 0xA000
    model.ram[1][start:start + len(code)] = code
    model.raw_page(1, 1)
    model.raw_page(2, 2)
    N.put(model, CurrentBank=1, CurrentBankC=2)
    before = rows(model)
    cpu = Funding.call(model, ORIGIN, a=85, x=71, y=109, p=0x31)
    assert cpu['regs'] == [85, 71, 109, 0x31, 224], cpu
    assert model.rawtags[1:3] == [1, 2] and N.get(model, 'ObjectOffset') == 3
    assert N.get(model, 'CurrentBank') == 1 and N.get(model, 'CurrentBankC') == 2
    return model, before, rows(model), cpu['cycles']


def main():
    raw = F.Q.P.G.ROM.read_bytes()
    proof = Funding.binding(raw)

    def authenticate(image):
        assert image == raw
        return proof

    seed = F.Q.P.clone(F.Q.P.cold, dict(authenticate=authenticate))(raw)
    for _ in range(12):
        seed.controller_pad = 0
        F.Q.Engine.Frames.frame(seed, cold=True)
    code = machine_code(seed)
    negatives = [dict(camera=FIRST_CAMERA_X - 1), dict(camera=LAST_CAMERA_X + 1),
                 dict(SelectedCharacter=39), dict(GameEngineSubroutine=7),
                 dict(WorldNumber=1), dict(LevelNumber=1), dict(TimerControl=1),
                 dict(GamePauseStatus=1), dict(AreaType=0), dict(AreaAddrsLOffset=6),
                 dict(occupied=tuple(range(6))), dict(existing=1), dict(existing=5)]
    negative_cycles = [exercise(seed, code, **case) for case in negatives]
    for case, (_, before, after, _) in zip(negatives, negative_cycles):
        assert before == after, (case, before, after)
    positives = []
    for camera, occupied in ((FIRST_CAMERA_X, ()), (LAST_CAMERA_X, ()),
                             (FIRST_CAMERA_X, (3, 4, 5))):
        model, before, after, cycles = exercise(seed, code, camera, occupied)
        index = max(i for i in range(6) if i not in occupied)
        assert after[index] == (1, 37, 0, 3, 240, 192, 1, 5, 255, 64, 128), after
        assert [i for i in range(6) if before[i] != after[i]] == [index]
        for screen_left, active in ((camera, 1), (1008, 1), (1088, 0)):
            screen_right = screen_left + 255
            N.put(model, ScreenLeft_PageLoc=screen_left >> 8,
                  ScreenLeft_X_Pos=screen_left & 255,
                  ScreenRight_PageLoc=screen_right >> 8,
                  ScreenRight_X_Pos=screen_right & 255, ObjectOffset=index)
            N.invoke(model, 'OffscreenBoundsCheck', x=index)
            assert N.get(model, 'Enemy_Flag', index) == active, (screen_left, index)
        positives.append(dict(camera=camera, slot=index, cycles=cycles))

    report = dict(ROM=H(raw), code=H(code), size=len(code), negatives=len(negatives),
                  positives=positives, stage='1-1 overworld', initial_top=192,
                  left=1008, center=1024, width=32, stock_actor=37,
                  stock_offscreen_checks=3 * len(positives),
                  isolated_CPU=True, integrated=False, outputs=0)
    digest = H(json.dumps(report, sort_keys=True, separators=(',', ':')).encode())
    print('PRINCE_LIFT_ADMISSION ' + json.dumps(dict(report, SHA256=digest),
                                                 separators=(',', ':')))


if __name__ == '__main__':
    main()
