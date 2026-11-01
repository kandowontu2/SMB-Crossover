"""Honor the previous completed native platform landing before advancing the donor."""
from pathlib import Path
from rebuild_selected_thomas_bounded_v2 import R,build,sha
P=R/'build/thomas-safe-melee';O=R/'build/thomas-platform-ground'


def main():
    assert sha(P/'candidate.nes')=='541091bd88a7c77c72862e4052832b9c40c05e8e58bab26f0bad06d22a971c3d'
    cache=(P/'cache.s').read_text()
    old=' jsr ThomasHostAfterTerrain ; import prior completed native support/carry before donor motion'
    assert cache.count(old)==1
    cache=cache.replace(old,' jsr ThPreviousSupport ; honor the previous completed native landing/carry',1)
    assert cache.count('ThCacheEnd:')==1
    cache=cache.replace('ThCacheEnd:','''ThPreviousSupport:
 lda Player_State
 bne ThPreviousImport
 lda ThomasState+$69
 and #4
 beq ThPreviousGrounded
 jsr Th_A884                  ; genuine donor end-jump state reset
 lda #$87
 sta ThomasState+$b6
ThPreviousGrounded:
 lda #0
 sta ThFalling
ThPreviousImport:
 jmp ThomasHostAfterTerrain
ThCacheEnd:''',1)
    build(P,O,cache,(P/'lift.s').read_text(),
          extra_refs=[Path(__file__),R/'build/thomas-native-carry/all-pipes/controls.json'],
          adaptation='When the prior completed native actor phase grounded Thomas, end the old source jump through its ownA884 reset before importing the corrected support plane. This prevents advancing the old airborne trajectory after a real platform landing. Native platform, donor actor and jump-table instructions remain unchanged.')


if __name__=='__main__':main()
