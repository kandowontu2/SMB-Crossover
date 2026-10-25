from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'build_mmc3_static_call_v34.py').read_text(encoding='utf-8')
s=s.replace("O=D/'mmc3-static-call-v34'", "O=D/'mmc3-static-call-v39'")
unused=r'\n    M3_CALL_RAM:start=$73fa,size=6,type=rw,file=""; # Explicit final six-byte alignment gap before history.'
assert s.count(unused)==1
s=s.replace(unused,'').replace('run = M3_CALL_RAM','run = SP')
s=s.replace('.assert SMCCODE=$73fa,error,"MMC3 tiny call uses only the final six-byte gap"','.assert SMCCODE=$0155,error,"MMC3 tiny call retains original base and shrinks to six bytes"')
s=s.replace('.assert Z2UiState+1<=SMCCODE,error,"Tiny call does not overlap preceding live state"','')
s=s.replace('.assert M3FarReturn+1<=XgLzHistory,error,"Tiny call stays below native audio/history"','.assert M3FarReturn=$015a,error,"Native stack must remain above six-byte tiny code"')
old="cold=body.replace('.proc MegaManResetBlockHealth','.proc M3ResetBlockHealthCold',1).replace('    rts','    jmp BillNativeCaptureP').replace('  rts','  jmp BillNativeCaptureP')\nassert cold.count('jmp BillNativeCaptureP')==2"
new="""cold='''.proc M3ResetBlockHealthCold
  jsr M3ResetBlockHealthCore
  jsr BillNativeCaptureP
  ; Original invocation selector, not the common dispatcher's selector7.
  txa
  pha
  tsx
  lda $0107,x
  sta BillNativeReturnSelector
  pla
  tax
  lda BillNativeReturnSelector
  rts
.endproc
'''+body.replace('.proc MegaManResetBlockHealth','.proc M3ResetBlockHealthCore',1)"""
assert s.count(old)==1
s=s.replace(old,new).replace('+96<=8192 and parent[tail:tail+96]==bytes([255])*96','+128<=8192 and parent[tail:tail+128]==bytes([255])*128')
s=s.replace('tiny_call_and_return_gap=[0x73fa,0x7400]','tiny_call_and_return_gap=[0x155,0x15b]').replace('hardware_stack_code_bytes=0','hardware_stack_code_bytes=6')
s=s.replace('five-byte LDA/JMP trampoline plus one private return byte in the six-byte alignment gap after Z2UiState/before XgLzHistory','five-byte LDA/JMP trampoline plus one private return byte at original stack-page base0155..015a; Zelda II state73fa..73ff untouched')
s=s.replace('executable bytes live in a proven SRAM alignment gap','only six executable/data bytes retain the original stack-page base')
assert 'M3_CALL_RAM'not in s
exec(compile(s,str(D/'build_mmc3_static_call_v34.py'),'exec'),globals())
assert (O/'candidate.nes').read_bytes()==(D/'mmc3-static-call-v37/candidate.nes').read_bytes()
print('V39 removes only the unused misleading memory declaration; complete ROM is byte-identical to V37.',flush=True)
