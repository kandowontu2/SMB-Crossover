from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'run_mmc3_mac_jump_v37.py').read_text(encoding='utf-8')
s=s.replace('mac-jump-v1','grant-jump-v1').replace('mac-easy','grant-easy').replace("'mac'","'grant'")
s=s.replace('Source Mac already uses Mario movement.','Grant keeps his existing source movement.')
exec(compile(s,str(D/'run_mmc3_mac_jump_v37.py'),'exec'),globals())
