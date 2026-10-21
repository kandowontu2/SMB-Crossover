from pathlib import Path
import importlib.util,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';O=V/'root49-components-land-l-ia'
p=V/'agent49g-samus-crouch-fix-proposal-b/image.py';s=importlib.util.spec_from_file_location('l_ib_image',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
old=m.Image(V/'root49-components-combined-k/source/build/smb-crossover-mmc3.nes');new=m.Image(O/'source/build/smb-crossover-mmc3.nes')
def names(im):return{z['name']:z for z in im.data['sym']if z.get('scope')==1 and 'seg'in z and 'val'in z}
a,b=names(old),names(new);changes=[dict(name=n,before=z,after=b.get(n))for n,z in a.items()if n not in b or z['val']!=b[n]['val']]
out=O/'symbol-delta-ib.json';assert not out.exists();out.write_text(json.dumps(changes,indent=2),encoding='utf-8');print(json.dumps(changes))
