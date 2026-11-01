"""Keep block preparation behind authentication without nested bank calls."""
from prepare_karnov_pickup_host_1101_v3 import transform_sources as previous


ROUTE='''; Reached only after KrCheckCode authenticates both selected cache banks.
; This is a JMP, so no helper return address adds to the deepest block stack.
KrPickupDispatchChoice:
 lda FarcallJmpTarget_SMC+1
 cmp #60                    ; public row20: prepare real block item
 beq KrPickupPrepareDirect
 clc
 adc #<KrCacheServices
 sta FarcallJmpTarget_SMC+1
 lda #>KrCacheServices
 adc #0
 sta FarcallJmpTarget_SMC+2
 jmp KrDispatchMapped
KrPickupPrepareDirect:
 lda #2
 sta CurrentBankC
 sta $5116
 tsx
 lda $0108,x                ; the genuine caller's object X
 tax
 jsr KrPickupPrepareBody
 jcc KrDispatchNo
 tsx
 lda $010a,x
 ora #1
 jmp KrDispatchSet          ; retain caller AXYP except the handled carry
'''


def transform_sources(**kwargs):
    q=previous(**kwargs)
    text=q['resident']
    original=''' jsr KrCheckCode
 bcc KrDispatchNo
 lda FarcallJmpTarget_SMC+1
 clc
 adc #<KrCacheServices
 sta FarcallJmpTarget_SMC+1
 lda #>KrCacheServices
 adc #0
 sta FarcallJmpTarget_SMC+2
'''
    assert text.count(original)==1
    text=text.replace(original,''' jsr KrCheckCode
 bcc KrDispatchNo
 jmp KrPickupDispatchChoice
KrDispatchMapped:
''')
    assert text.count('KrResidentEnd:\n')==1
    text=text.replace('KrResidentEnd:\n','.include "kr-pickup-rom-route-v4.inc"\nKrResidentEnd:\n')
    q['resident']=text
    q['fragments']['kr-pickup-rom-route-v4.inc']=ROUTE
    name='kr-pickup-rom-tail-v3.inc';worker=q['fragments'][name]
    original='KrPickupPrepare:\n php\n pha\n'
    assert worker.count(original)==1
    worker=worker.replace(original,'''KrPickupPrepare:
 php
 pha
 jsr KrPickupPrepareBody
 bcc KrPickupPrepareRestoreNo
 pla
 plp
 sec
 rts
KrPickupPrepareRestoreNo:
 pla
 plp
 clc
 rts
KrPickupPrepareBody:
''')
    original=''' sta InvPickupSaveHi,x
 pla
 plp
 sec
 rts
KrPickupPrepareNo:
 pla
 plp
 clc
 rts
'''
    assert worker.count(original)==1
    worker=worker.replace(original,''' sta InvPickupSaveHi,x
 sec
 rts
KrPickupPrepareNo:
 clc
 rts
''')
    q['fragments'][name]=worker
    q['constraints']+=['Row20 retains full two-bank authentication, C2 mapping and saved SMC. Its simple prepare body uses one direct JSR; the dispatcher restores original AXYP except handled carry. Other rows retain their original typed route and live child results. The standalone worker wrapper and all kernel vectors remain available.']
    return q
