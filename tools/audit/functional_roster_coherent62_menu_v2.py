"""Use actual FmNames FF indices5..8; retain v1's fixture index negative.

The cart and controls remain unchanged. Explicitly compare the eight live
full16-character names rather than confusing FF indices with WWF18..23.
"""
from pathlib import Path
p=Path(__file__).with_name('functional_roster_coherent62_menu_v1.py')
s=p.read_text().replace("out=O/'menu-controls.json'", "out=O/'menu-controls-v2.json'")
s=s.replace("assert idx in(range(18,22)if slot==21 else range(10,14)),(slot,variant,idx)","""assert idx==(5+variant if slot==21 else 10+variant),(slot,variant,idx)
     names=['   FF FIGHTER   ','  FF WHITE MAGE ','  FF BLACK MAGE ','    FF THIEF    ']if slot==21 else['   SMB2 MARIO   ','   SMB2 LUIGI   ','    SMB2 TOAD   ','   SMB2 PEACH   ']
     encoded=[36 if c==' 'else ord(c)-ord('A')+10 if c.isalpha()else int(c)for c in names[variant]]
     assert packets[1][0]['data']==encoded,('actual complete prefix',slot,variant,packets[1],encoded)""")
exec(compile(s,__file__,'exec'),globals())
