from pathlib import Path
import sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;O=D/'mmc3-menu-packed-pz-v1';O.mkdir(exist_ok=False)
(O/'ports/mmc3-oversized').mkdir(parents=True);(O/'chr/characters').mkdir(parents=True)
f=R/'tools/reference/pack_mmc3_menu.py';t=f.read_text();assert t.count("len(manifest['identities'])==33")==1;assert t.count('len(pages)==66')==1
for a,b in [("len(manifest['identities'])==33","len(manifest['identities'])==37"),('len(pages)==66','len(pages)==74'),('identities=33','identities=37')]:t=t.replace(a,b)
ns={'__name__':'_private_pack','__file__':str(f)};exec(compile(t,str(f),'exec'),ns);ns['ROOT']=O
sys.argv=[str(f),'--captures',str(D/'mmc3-menu-source-pz-v1')];ns['main']()
