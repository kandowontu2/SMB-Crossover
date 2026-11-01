"""Repeat the donor-frame route and inspect its final native OAM owners."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import check_thomas_all_pipes_bounded_v1 as A


def main():
    A.J=R/'build/thomas-native-render';A.O=A.J/'source-route'
    last=[];original=A.C.fresh
    def remember(bundle):
        m=original(bundle);last.append(m);return m
    A.C.fresh=remember
    A.main()
    m=last[-1];c=A.C
    at=c.address(m.bundle,'Sprite_Data');sprites=[]
    for i in range(64):
        y,t,attr,x=m[at+i*4:at+i*4+4]
        if y<240:sprites.append(dict(slot=i,X=x,Y=y,tile=t,attribute=attr))
    names=['FloateyNum_Control','FloateyNum_X_Pos','FloateyNum_Y_Pos',
           'Enemy_ID','Enemy_Flag','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position']
    fields={n:list(m[c.address(m.bundle,n):c.address(m.bundle,n)+6])for n in names if n in m.bundle['syms']}
    receipt=A.O/'controls.json';data=json.loads(receipt.read_text())
    data['bindings'][str(Path(__file__).resolve())]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    receipt.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    result=dict(source_CPU=True,native=False,sprites=sprites,fields=fields,scope='Final CPU-model native OAM/object inspection; not a raster snapshot.')
    (A.O/'OAM.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))


if __name__=='__main__':main()
