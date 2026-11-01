.setcpu "6502"
.import FmGroups,CurrentBankC,VRAM_Buffer1,VRAM_Buffer1_Offset,WfRolePackets
.importzp R0,R2,R3
.export WfQueueRolesWorker,WfStatusHeaderWorker
.segment "WF_ROSTER_WORKERS"
WfQueueRolesWorker:
 ldx VRAM_Buffer1_Offset
 cpx #71
 bcs RolesDone
 lda #$c1
 sta CurrentBankC
 sta $5116
 lda FmGroups
 and #7
 sta R2
 asl
 clc
 adc R2
 asl
 asl
 clc
 adc R2                       ; thirteen-byte packet per menu variant
 tay
 lda #12
 sta R3
CopyRole:
 lda WfRolePackets+$2000,y
 sta VRAM_Buffer1,x
 inx
 iny
 dec R3
 bne CopyRole                 ; palette00 is real data, not a terminator
 lda #0
 sta VRAM_Buffer1,x
 stx VRAM_Buffer1_Offset
RolesDone:rts
WfStatusHeaderWorker:
 lda FmGroups
 and #7
 sta R0
 asl
 asl
 asl
 sec
 sbc R0
 tay
 ldx #0
Header:
 lda WfRosterHudNames,y
 sta VRAM_Buffer1+11,x
 iny
 inx
 cpx #7
 bne Header
 rts
.include "inc/charmap.inc"
WfRosterHudNames:
.byte " HOGAN ","DIBIASE","BIGELOW"," HONKY ","SAVAGE "," ANDRE "
.assert *<=$c000,lderror,"Use only verified native121 tail"
