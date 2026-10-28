; Rogue Dawn1.21 source-state projection. Exclusive new-identity overlay.
; ROM SHA9271411a...61077. Original addresses in comments are SOURCE addresses.
; ROOT reserves persistent5FB0..BF and active5C00..7F. No generic hero arrays.
.ifndef __ROGUE_DAWN_STATE_INC
__ROGUE_DAWN_STATE_INC=1
.ifndef RdVariant
RdVariant=$5fee
.endif
RdGear=$5fb0                    ; source6878:01bomb,02high,04wall,08screw,
                               ; 10spring,20environment,40wave,80ice.
RdMissiles=$5fb1                ; source6879
RdMaxMissiles=$5fb2             ; source687A
RdTanks=$5fb3                   ; source6877
RdHealthLo=$5fb4                ; source0106 BCD image
RdHealthHi=$5fb5                ; source0107 BCD image
RdAction=$5c00                  ; source0300, unchanged source action numbers
RdRadiusY=$5c01
RdRadiusX=$5c02
RdAnimFrame=$5c03
RdAnimDelay=$5c04
RdAnimReset=$5c05
RdAnimIndex=$5c06
RdElevator=$5c07
RdVY=$5c08
RdVX=$5c09
RdHit=$5c0a
RdRoomHi=$5c0c
RdY=$5c0d
RdX=$5c0e
RdJumpDistance=$5c0f
RdVerticalPhase=$5c10            ; source0310 nonlinear counter
RdHorizontalPhase=$5c11          ; source0311 nonlinear counter
RdVerticalFraction=$5c12         ; source0312 linear counter
RdHorizontalFraction=$5c13       ; source0313 linear counter
RdGravity=$5c14
RdAcceleration=$5c15
RdMaxSpeed=$5c16
RdSfx=$5c20                     ; source0680..0686 request image; NOT hostAPU
RdMissileMode=$5c27              ; source010E
RdFresh=$5c28                    ; source0012, canonical NES button bits
RdHeld=$5c29                     ; source0014
RdPreviousSpring=$5c2a           ; source00CD
RdEnvironment=$5c2b              ; source780E bit7=normal,clear=reducedgravity
RdFacing=$5c2c                   ; source004D:0right,1left
RdFrozenSupport=$5c2d            ; source007D
RdClock=$5c2e                    ; source002D frame parity, caller owns ticking
RdSlot=$5c2f                     ; source004B, projectile source offsetsD0/E0/F0
RdDelta=$5c30                   ; source0000 signed pixel delta
RdMath1=$5c31                   ; source0001
RdMath2=$5c32                   ; source0002
RdMath3=$5c33                   ; source0003
RdRepeat=$5c34                  ; source0016
RdGravityFlagProbe=$5c38        ; source07A0 read by overlapping BIT opcode
RdSpeedFlagProbe=$5c39          ; source0AA9 mirrored02A9; flags-only BIT read
; The two flag-probe bytes preserve source leaf AXYP for finite differentials.
; They are NOT abilities; no caller may derive a game event from those flags.
; Future host adapter must prove flag liveness or provide its source projection.
RdShotRecords=$5c40             ; reserved3*16 source-projectile records; not
                               ; implemented by this kinematics-only leaf.
.export RdGear,RdMissiles,RdMaxMissiles,RdTanks,RdHealthLo,RdHealthHi
.export RdVY,RdVX,RdGravity,RdDelta,RdFresh,RdHeld,RdEnvironment
.endif
