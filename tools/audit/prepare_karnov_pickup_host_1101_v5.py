"""Reuse the dispatch save frame while authenticating the real runtime owner."""
from prepare_karnov_pickup_host_1101_v4 import transform_sources as previous

HEAD='''; Immutable ROM entry; the dispatch frame already owns AXYP/maps/SMC.
KrDispatchAuthenticate:
 lda SelectedCharacter
 cmp #34
 jeq KrDispatchAuthBanks
 jsr KrCheckCode            ; retain legacy menu-alias and foreign rejection
 jcc KrDispatchNo
 jmp KrPickupDispatchChoice
'''

BANKS='''; Both complete16-byte cookies are still checked before any RAM opcode.
; Unlike the standalone public checker, no duplicate register-save frame is
; needed: all success/failure paths return through KrDispatch's saved frame.
KrDispatchAuthBanks:
 ldx #3
KrDispatchAuthBank:
 stx CurrentBankC
 stx $5116
 ldx #15
KrDispatchAuthByte:
 lda $dfe0,x
 cmp KrCookie,x
 jne KrDispatchNo
 dex
 bpl KrDispatchAuthByte
 ldx CurrentBankC
 dex
 cpx #1
 bne KrDispatchAuthBank
; C2 remains mapped; fall through into the common typed target choice.
'''


def transform_sources(**kwargs):
    q=previous(**kwargs);text=q['resident']
    original=''' jsr KrCheckCode
 bcc KrDispatchNo
 jmp KrPickupDispatchChoice
KrDispatchMapped:
'''
    assert text.count(original)==1
    text=text.replace(original,''' jmp KrDispatchAuthenticate
KrDispatchMapped:
''')
    original='.include "kr-pickup-rom-align-v3.inc"'
    assert text.count(original)==1
    text=text.replace(original,'.include "kr-pickup-rom-auth-v5.inc"\n'+original)
    q['resident']=text
    q['fragments']['kr-pickup-rom-auth-v5.inc']=HEAD
    q['fragments']['kr-pickup-rom-route-v4.inc']=BANKS+q['fragments']['kr-pickup-rom-route-v4.inc']
    q['constraints']+=['Runtime raw34 authenticates both complete16-byte cookies inside the already saved dispatch frame. No guest state or RAM opcode is touched before this check. Legacy raw7/menu alias and foreign identities retain the public checker. No additional scratch or SMC ownership is introduced.']
    return q
