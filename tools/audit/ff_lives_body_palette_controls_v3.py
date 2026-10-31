"""Track genuine foreground SFC's bank/returned-A operands, not ISR ABI."""
from pathlib import Path
P=Path(__file__).with_name('ff_lives_body_palette_controls_v2.py')
s=P.read_text(encoding='utf-8').replace('controls-v2.json','controls-v3.json')
s=s.replace("a==address(b,'NextBank_SMC')+1", "a in [address(b,'NextBank_SMC')+1,address(b,'SafereturnA_SMC')+1]")
exec(compile(s,str(P),'exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
