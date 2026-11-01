; Intentional NES palette adaptation for the selected Metal Storm player only.
; The original body uses P0 and the original shots P1. SMB keeps P1/P2/P3
; for native actors, so remapped body/shot bitplanes share this one P0.
; No shape/alpha/geometry change and no native-world palette/CHR edit.
; Invoke these two macros at the exact source sites verified by the v9 recipe.
; Neither macro grants PRG/CHR/RAM ownership or supplies a cold-loader gate.
.import Ms9Color1,Ms9Color2,Ms9Color3
.macro Ms9ShotPalette0
 and #$fc                  ; retain every non-palette attribute, including H/V
.endmacro
.macro Ms9PalettePacket
 .byte $3f,$11,3
 .lobytes Ms9Color1,Ms9Color2,Ms9Color3
.endmacro
