"""Wire the exact real InitScreen consumer and preserve state across areas."""
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'build/karnov-host-resource-base-1101-v1'
SCREEN=R/'build/hogan-thomas-current/src/screen_render.s'
POST=R/'build/hogan-thomas-current/src/hot_render_gate.s'

def once(t,a,b):
    assert t.count(a)==1,(a,t.count(a));return t.replace(a,b)

def prepare(resident,terrain,write):
    screen=once(SCREEN.read_text(),'farcall ThSceneInit ; private FF loader, genuine Move remains first','farcall KrSceneInit ; preserve old scene chain, then load the selected Karnov')
    write(O/'screen_render.s',screen)
    post=once(POST.read_text(),'''::ThPostNativeHot:
 php
 pha
 lda SelectedCharacter
''','''::ThPostNativeHot:
 php
 pha
 lda SelectedCharacter
 cmp #34
 beq KrOwn
''')
    post=once(post,''' farcall HuAfterTerrainGate,jmp
 .else''',''' farcall HuAfterTerrainGate,jmp
KrOwn:
 pla
 plp
 farcall KrServiceVeneers+81,jmp
 .else''')
    write(O/'hot_render_gate.s',post)
    # This resident wrapper runs from stable ROM29 while C2/C3 are replaced.
    # The existing callback and its entire loader chain always execute first.
    scene=(R/'tools/reference/karnov_host_scene_1101_v1.inc').read_text()
    resident=once(resident,'KrCookie:.incbin "kr-cookie.bin"',scene+'\nKrCookie:.incbin "kr-cookie.bin"')
    terrain=once(terrain,' lda #0\n sta KrReady\n sta R0',''' ; A real scene seam can keep the current life, including source gear and
 ; option stock. A different player or a lost life constructs fresh state.
 lda KrReady
 cmp #$a7
 bne KrNewLife
 lda CurrentPlayer
 cmp KrPlayer
 bne KrNewLife
 lda NumberofLives
 cmp KrLives
 bcc KrNewLife
 jmp KrKeepLife
KrNewLife:
 lda #0
 sta KrReady
 sta R0''')
    terrain=once(terrain,' lda #0\n sta KrHaveEpoch','''KrKeepLife:
 lda #0
 sta KrReady
 sta KrState+$1b            ; held/pressed input is rebuilt at the next Main
 sta KrState+$21
 sta KrState+$66            ; actor motion/action phase, not equipment
 sta KrState+$67
 sta KrState+$6a
 sta KrState+$6b
 lda KrState+$68
 and #$bf                  ; end transient hurt flash, keep source health bit
 sta KrState+$68
 lda #1
 sta KrState+$69
 jsr Kr_C2B7                ; original nine-projectile clear on scene transfer
 lda #0
 sta KrHaveEpoch''')
    terrain=once(terrain,' lda NumberofLives\n cmp KrLives\n jne KrMoveNo',''' lda NumberofLives
 cmp KrLives
 jcc KrMoveNo
 sta KrLives                ; an earned extra life must not stop movement''')
    return resident,terrain,[Path(__file__),SCREEN,POST,R/'tools/reference/karnov_host_scene_1101_v1.inc',O/'screen_render.s',O/'hot_render_gate.s']
