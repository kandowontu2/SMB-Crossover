.setcpu "6502"

; WorldTileY compares Row with CurrentRow immediately before this branch.
; Cell adds a signed room-row offset. A row above zero is stored as $FF,
; $FE, or $FD. The bounded subtraction has no signed overflow, so N marks
; a row above the current one even when the row wraps through zero.
    bmi AboveRow
