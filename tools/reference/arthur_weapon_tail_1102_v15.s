; Actual Main uses HuWeaponTail (row34), not HuWeapons (row4).
; Reuse Arthur's existing row4 transport/contact worker. The genuine
; NrObjectWeaponTail continues with native air bubbles after this returns.
.setcpu "6502"
.segment "WEAPON_TAIL"
 jmp ArOwnSet4
