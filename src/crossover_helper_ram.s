; Occupy only the pre-existing alignment gap; every following RAM address stays.
.pushseg
.segment "SRAM"
.if ::MAPPER_MMC5
.assert * = $7382, error, "MMC5 helper state must start in its original alignment gap"
.else
.assert * = $736a, error, "MMC3 helper state must start in its original alignment gap"
.endif
HpRamStart:
HpValid: .res 1
HpKey: .res 1
HpArea: .res 1
HpCharacter: .res 1
HpMode: .res 1
HpCount: .res 1
HpEngine: .res 1
HpSupport: .res 1
HpRecord: .res 3
HpPhaseLo: .res 3
HpPhaseMid: .res 3
HpPhaseHi: .res 3
HpXLo: .res 3
HpXHi: .res 3
HpY: .res 3
HpPreviousXLo: .res 3
HpPreviousXHi: .res 3
HpPreviousY: .res 3
HpVisible: .res 3
HpActorSlot: .res 3
HpActorOwner: .res 6
HpWidth: .res 3
HpKind: .res 3
; Native drawing only needs seven low/high pointers and its nine-byte girder.
HpRects: .res 23
HpDrawBuffer = HpRects
HpAxisFlags: .res 1
HpAxis: .res 1
HpDeferred: .res 1
HpSlot: .res 1
HpMovedX: .res 1
HpTemp: .res 1
HpTemp2: .res 1
HpTemp3: .res 1
HpSineIndex: .res 1
HpOffset: .res 1
HpCountDown: .res 1
HpLoop: .res 1
HpRamEnd:
.assert HpRamEnd-HpRamStart=91,error,"Preserve the native helper91-byte ABI"
.if ::MAPPER_MMC5
.assert * <= $73dd,error,"Helpers must end before ProtoVariant"
.else
.assert * <= $7400,error,"Preserve original history alignment"
.endif
.popseg
