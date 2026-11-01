"""Pure source transformations for the isolated menu-input proposal.

No file writes or implicit build. Root owns composing these returned strings
into its own exact candidate and adding both source paths to its bindings.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REFERENCE=ROOT/'tools/reference/menu_input_1101_v3.inc'

def one(text,old,new):
    assert text.count(old)==1,('Menu-input source consumer is not unique',old[:90])
    return text.replace(old,new)

def proposal(select,characters,entry,cfg):
    """Return select, characters, entry, cfg with zero old-PC displacement.

    Caller must write characters.s beside its entrypoint so ca65 finds that
    private copy before inherited -I paths. Leave all other sources read-only.
    The full main link must retain every preexisting address/location and
    exact unaffected ROM bytes; this proposal alone does not establish that.
    """
    select=one(select,'''  lda SavedJoypad1Bits
  ora SavedJoypad2Bits
  tax
  stx CrossoverMenuPressed
  eor CrossoverMenuButtons
  and CrossoverMenuPressed
  sta CrossoverMenuPressed
  stx CrossoverMenuButtons''','''  MnMenuInputHook''')
    select=one(select,'''  lda #0
  sta FmAlts
  sta FmGroups
  farcall InitializeNameTables''','''  lda #0
  MnMenuRetainHook
  farcall InitializeNameTables''')
    select=one(select,'''.assert *-CrossoverMenuInput<=$c8c,lderror,"BT menu stays within original PROTO_MENU"''','''MnMenuEmitEdges
.assert *-CrossoverMenuInput<=$c8c,lderror,"BT menu stays within original PROTO_MENU"''')
    select+='''
; Actual original segment owners endBEB5 and restartBF00. This new fixed
; optional26-byte segment occupies only the audited unowned ROM fill gap.
.pushseg
.segment "MENU_INPUT_COLD_V3"
MnMenuEmitColdInit
.assert *-MnMenuColdInit=26,lderror,"Menu reset wrapper must stay26bytes"
.popseg
'''
    characters=one(characters,'''.proc CrossoverInit
 .if ::ENABLE_MMC5_EXPANDED
.if ::ENABLE_MMC5_EXPANDED
  farcall NrGlobalInit''','''.proc CrossoverInit
 .if ::ENABLE_MMC5_EXPANDED
.if ::ENABLE_MMC5_EXPANDED
  MnMenuColdHook''')
    entry=one(entry,'''.include "characters.s"''','''.include "'''+REFERENCE.as_posix()+'''"
.include "characters.s"''')
    old='    PROTO_PALETTE_ACK: load=X5_NEW_42_TAIL,type=ro,start=$be40;'
    cfg=one(cfg,old,old+'\n    MENU_INPUT_COLD_V3: load=X5_NEW_42_TAIL,type=ro,start=$beb5,optional=yes;')
    return select,characters,entry,cfg
