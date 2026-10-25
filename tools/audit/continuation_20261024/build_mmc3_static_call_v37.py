from pathlib import Path
D=Path(__file__).resolve().parent
# V36 passed isolated CPU ABI checks, but its proposed SRAM gap has explicit
# Zelda II attack-state owners. Never run/adopt that allocation.
s=(D/'build_mmc3_static_call_v36.py').read_text(encoding='utf-8')
s=s.replace("s=s.replace(\"O=D/'mmc3-static-call-v34'\", \"O=D/'mmc3-static-call-v36'\")", "s=s.replace(\"O=D/'mmc3-static-call-v34'\", \"O=D/'mmc3-static-call-v37'\")")
s=s.replace("assert \"O=D/'mmc3-static-call-v36'\" in s", "assert \"O=D/'mmc3-static-call-v37'\" in s")
anchor="exec(compile(s,str(D/'build_mmc3_static_call_v34.py'),'exec'),globals())"
replacement="""s=s.replace('\\n    M3_CALL_RAM:start=$73fa,size=6,type=rw,file=\\"\\"; # Explicit final six-byte alignment gap before history.','')
s=s.replace('run = M3_CALL_RAM','run = SP')
s=s.replace('.assert SMCCODE=$73fa,error,\\"MMC3 tiny call uses only the final six-byte gap\\"','.assert SMCCODE=$0155,error,\\"MMC3 tiny call retains original base and shrinks to six bytes\\"')
s=s.replace('.assert Z2UiState+1<=SMCCODE,error,\\"Tiny call does not overlap preceding live state\\"','')
s=s.replace('.assert M3FarReturn+1<=XgLzHistory,error,\\"Tiny call stays below native audio/history\\"','.assert M3FarReturn=$015a,error,\\"Native stack must remain above six-byte tiny code\\"')
s=s.replace('tiny_call_and_return_gap=[0x73fa,0x7400]','tiny_call_and_return_gap=[0x155,0x15b]')
s=s.replace('hardware_stack_code_bytes=0','hardware_stack_code_bytes=6')
s=s.replace('five-byte LDA/JMP trampoline plus one private return byte in the six-byte alignment gap after Z2UiState/before XgLzHistory','five-byte LDA/JMP trampoline plus one private return byte at original stack-page base0155..015a; Zelda II state73fa..73ff untouched')
s=s.replace('executable bytes live in a proven SRAM alignment gap','only six executable/data bytes retain the original stack-page base')
exec(compile(s,str(D/'build_mmc3_static_call_v34.py'),'exec'),globals())"""
assert s.count(anchor)==1
s=s.replace(anchor,replacement)
exec(compile(s,str(D/'build_mmc3_static_call_v36.py'),'exec'),globals())
