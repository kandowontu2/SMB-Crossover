; Existing WWF row8 is the guest death-tick contract.
; Replace Target WfNoop with Target MegaManDeathUpdate; all other35 rows stay exact.
MegaManDeathUpdate=$af3a
NativeDeathBank=$88
.word MegaManDeathUpdate
.byte NativeDeathBank
