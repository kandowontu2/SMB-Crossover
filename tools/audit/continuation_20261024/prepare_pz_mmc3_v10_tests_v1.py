from pathlib import Path
import importlib.util,sys,json,hashlib
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent
f=D/'capture_pz_menu_37_v1.py';t=f.read_text();t=t.replace("O=D/'mmc3-menu-source-pz-v1'","O=D/'ryu-head-oversized-mmc3-v10/menu-v1'")
t=t.replace("D/'ryu-head-candidate-v5/candidate.nes'","D/'ryu-head-oversized-mmc3-v10/candidate.nes'")
t=t.replace("str(O/('source-sprite-'+setting))]","str(O/('source-sprite-'+setting)),'--trace','--rapid']")
assert "'--trace','--rapid'"in t
(D/'test_pz_mmc3_v10_menu_v1.py').write_text(t)
