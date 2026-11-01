"""Detach the12byte melee save while preserving actual callback A/X/Y/P inputs."""
from pathlib import Path
from rebuild_selected_thomas_bounded_v2 import R,build,sha
import json
P=R/'build/thomas-native-carry';O=R/'build/thomas-safe-melee'


def main():
    assert sha(P/'candidate.nes')=='2f68f566b1adcbff9b92fe385715b06897d06736bf4d429aadac09a39cfe543b'
    inputs=json.loads((P/'final-link.json').read_text())['command']
    old=next(Path(p).with_suffix('.s')for p in inputs if Path(p).name=='boundary.o')
    boundary=old.read_text();boundary='.export ThMeleeDetached\nThMeleeDetached=$c860\n'+boundary
    before=' stx R1\n ThFar HandleEnemyFBallCol,jsr,Bank_HandleEnemyFBallCol'
    assert boundary.count(before)==1
    boundary=boundary.replace(before,''' stx R1
 ; Preserve the real outgoing A/P before copying the exact ThSave12 frame.
 sta ThMeleeDetached+12
 php
 pla
 sta ThMeleeDetached+13
 ldx #0
ThMeleeDetach:
 pla
 sta ThMeleeDetached,x
 inx
 cpx #12
 bne ThMeleeDetach
 ldx ThHostTemp+1
 lda ThMeleeDetached+13
 pha
 lda ThMeleeDetached+12
 plp
 ThFar HandleEnemyFBallCol,jsr,Bank_HandleEnemyFBallCol
 ldx #11
ThMeleeAttach:
 lda ThMeleeDetached,x
 pha
 dex
 bpl ThMeleeAttach''',1)
    build(P,O,(P/'cache.s').read_text(),(P/'lift.s').read_text(),boundary=boundary,
          extra_refs=[Path(__file__),old,P/'all-pipes/controls.json'],
          adaptation='Detach only the12byte melee scope into own C860..C86B while native defeat/drop executes; preserve real callback A/P in C86C/D and restore callback X. Old actual SP140 cut reached119 and corrupted SMC. No masking or native/donor actor opcode edits.')


if __name__=='__main__':main()
