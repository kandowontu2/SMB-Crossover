; Two ordered helper calls inside the original private native-world scanner.
; The donor stores horizontal query endpoints as 8-bit screen coordinates.
; Keep the admitted modular width (0..32) but restore its world page.
.export DkWorldEndPage, DkWorldEndPageEnd, DkWorldStartPage, DkWorldStartPageEnd

WLeft = $c8e8
WRight = $c8e9
WX = $c8de
WEndX = $c8e0
WEndPage = $c8e1
PlayerX = $75
PlayerPage = $5c
CameraX = $071f
CameraPage = $071d

.segment "RIGHT"
DkWorldEndPage:
    sta WEndPage
    lda WRight
    cmp WLeft
    bcs EndReady

    ; Wrapped windows on the right half end beyond screen X255. A native
    ; anchor on the left half or just left of the camera instead makes the
    ; left endpoint negative. Test the actual 16-bit native-camera delta.
    lda PlayerX
    sec
    sbc CameraX
    tax
    lda PlayerPage
    sbc CameraPage
    bmi EndReady
    bne NextPage
    txa
    bpl EndReady
NextPage:
    inc WEndPage
EndReady:
    rts
DkWorldEndPageEnd:
    .assert *-DkWorldEndPage <= 43, error, "DK metadata tail after cold boot"

.segment "LEFT"
DkWorldStartPage:
    ; A <=32-pixel interval crosses at most one 256-pixel boundary.
    ; If its rounded left low byte exceeds its right, subtract one page.
    lda WEndX
    cmp WX
    lda WEndPage
    sbc #0
    rts
DkWorldStartPageEnd:
    .assert *-DkWorldStartPage <= 30, error, "DK metadata before cold boot"
