"""Assert genuine moved slotX31 for Goku; retain v1's oldslotX23 negative.

Only the deliberately moved profile has a new menu index. Every other
Start/A register and every unchanged profile remain exactly compared.
"""
from pathlib import Path
p=Path(__file__).with_name('arthur_goku_select_remap_controls_v1.py')
s=p.read_text().replace("out=O/'menu-controls.json'","out=O/'menu-controls-v2.json'")
s=s.replace("assert zz[0]==zz[1],('real Start/A AXYP/SP',slot,variant,dest,key,zz)","""if slot==23:
      assert zz[0]['X']==23 and zz[1]['X']==31
      assert {k:v for k,v in zz[0].items()if k!='X'}=={k:v for k,v in zz[1].items()if k!='X'},('moved Start/A exact other ABI',slot,variant,key,zz)
     else:assert zz[0]==zz[1],('real Start/A AXYP/SP',slot,variant,dest,key,zz)""")
exec(compile(s,__file__,'exec'),globals())
