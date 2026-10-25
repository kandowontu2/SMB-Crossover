from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'build_mmc3_static_call_v34.py').read_text(encoding='utf-8')
s=s.replace("O=D/'mmc3-static-call-v34'", "O=D/'mmc3-static-call-v36'")
old="cold=body.replace('.proc MegaManResetBlockHealth','.proc M3ResetBlockHealthCold',1).replace('    rts','    jmp BillNativeCaptureP').replace('  rts','  jmp BillNativeCaptureP')\nassert cold.count('jmp BillNativeCaptureP')==2"
new="""cold='''.proc M3ResetBlockHealthCold
  jsr M3ResetBlockHealthCore
  jsr BillNativeCaptureP
  ; Match the existing rare-call ABI: the original selector is owned by
  ; this invocation on the native stack, six bytes above target entry SP.
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
assert "O=D/'mmc3-static-call-v36'" in s
exec(compile(s,str(D/'build_mmc3_static_call_v34.py'),'exec'),globals())
