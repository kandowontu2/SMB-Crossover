"""Pure source repair of the actual Doki-owned foreign body boundary."""
def repair_body_boundary(text):
    old='S2BoundaryGate S2BoundaryBody,S2MainBody,GuestBodyContact'
    assert text.count(old)==1
    new='''.import KbBodyDispatch
.export S2BoundaryBody
.proc S2BoundaryBody
 php
 pha
 lda SelectedCharacter
 cmp #25
 beq Own
 pla
 plp
 ; Already in A74: the existing guard admits Kirby/Meta, and its foreign
 ; tail enters the same GuestBodyContact legacy owner as before.
 jmp KbBodyDispatch
 .res 15,$ea
Own:pla
 plp
 farcall S2MainBody,jmp
 .assert *-S2BoundaryBody=49,lderror,"Exact own49B owner boundary"
.endproc'''
    return text.replace(old,new)

def repair_body_guard(text):
    start=text.index('.proc KbBodyDispatch\n');end=text.index('.endproc',start);part=text[start:end]
    for old,new in[(' lda SelectedCharacter\n',' php\n pha\n lda SelectedCharacter\n'),(' jeq Kirby\n',' beq Kirby\n'),(' farcall GuestBodyContact,jmp\n',' pla\n plp\n farcall GuestBodyContact,jmp\n'),('Kirby:\n phx','Kirby:\n pla\n plp\n phx'),(' jcc Ordinary\n',' bcc Ordinary\n')]:
        assert part.count(old)==1,(old,part.count(old));part=part.replace(old,new)
    return text[:start]+part+text[end:]

def repair_red_range(text):
    old='  lda KbShotKind,x\n  cmp #3\n  jne NotReturn\n  lda KbShotAge,x\n  cmp #24\n'
    assert text.count(old)==1
    return text.replace(old,old.replace('  cmp #24\n','  ; Preserve original92px outbound reach at3px:31updates=93px.\n  cmp #32\n'))
