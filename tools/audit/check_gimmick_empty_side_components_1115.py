"""Declared CPU fixtures for exact Gimmick side filter/renderer composition."""
from copy import deepcopy
from hashlib import sha256
import itertools,json
from pathlib import Path
from unittest.mock import patch
import compose_gimmick_empty_side_1115 as C

N,W=C.N,C.W


def bundle(raw,new=False):
    b=dict(W.Symbols.bundle(),raw=raw)
    if new:
        b['syms']=deepcopy(b['syms'])
        for name,value in(('GmBodyProbe',0xb882),('GmCameraPoint',0xb913)):
            b['syms'][name]=dict(b['syms'][name],val=hex(value))
    return b


def seed(b):
    m=N.fresh(b)
    N.put(m,SelectedCharacter=26,GmReady=71,NumberofLives=2,GameEngineSubroutine=8,OperMode=1,OperMode_Task=3,
        Player_X_Position=207,Player_PageLoc=4,Player_Y_Position=137,Player_Y_HighPos=1,Player_State=2,
        Player_X_Speed=254,Player_Y_Speed=0,R0=166,R1=57,GmTemp2=109)
    return m


def regs(z):return tuple(z[k]for k in('A','X','Y','P'))


def query_pair(old,new,role,index,tile,p=0x31,x=207,y=137,page=4,owner=26):
    out=[]
    for m in(old,new):
        N.put(m,SelectedCharacter=owner,Player_X_Position=x,Player_PageLoc=page,Player_Y_Position=y,R0=166,R1=57,GmTemp2=109)
        dx=(8,5,11,5,5,11,11)[index];dy=(18,32,32,22,30,22,30)[index]
        xx=x+page*256+dx;row=(((y+dy)&255)&240)-32;row&=255
        ptr=W.address(m.bundle,'Block_Buffer_2'if xx//256&1 else'Block_Buffer_1')+(xx%256)//16
        m[(ptr+row)&65535]=tile
        z=N.invoke(m,role,a=93,x=77,y=index-1 if role=='GmFoot'else index,p=p)
        out.append((z,[N.get(m,'R'+str(i))for i in range(8)]))
    (za,ra),(zb,rb)=out
    intended=owner==26 and role=='GmSide'and tile==35
    expected=list(regs(za))
    if intended:expected[0]=0;expected[3]=(expected[3]&~130)|2
    assert tuple(expected)==regs(zb),(role,index,tile,owner,regs(za),regs(zb))
    assert ra==rb,(role,index,tile,ra,rb)
    return intended


def run(raw):
    candidate,layout=C.proposal(raw);assert C.inverse(candidate)==raw
    old,new=seed(bundle(raw)),seed(bundle(candidate,True));tiles=changes=0
    for tile,index,p in itertools.product(range(256),range(7),(0x20,0x31,0x69,0xe5)):
        role='GmHead'if index==0 else'GmFoot'if index<3 else'GmSide'
        changes+=query_pair(old,new,role,index,tile,p);tiles+=1
    geometry=0
    for x,y,page,index,tile in itertools.product((0,7,15,248,255),(0,16,176,207,239,255),(0,1,255),range(7),(0,35,81,96)):
        role='GmHead'if index==0 else'GmFoot'if index<3 else'GmSide'
        query_pair(old,new,role,index,tile,x=x,y=y,page=page);geometry+=1
    foreign=0
    for owner,index,p in itertools.product([i for i in range(256)if i!=26],range(7),(0x31,0xe5)):
        role='GmHead'if index==0 else'GmFoot'if index<3 else'GmSide'
        query_pair(old,new,role,index,35,p,owner=owner);foreign+=1
    renderer=0;cycles=set()
    for slot,xx,yy,screen,iy,p in itertools.product((0,1),(0,1,15,16,4095,65535),(0,15,16,3839,65535),(0,255,4095),(0,77,255),(0x31,0x69)):
        results=[]
        for m in(old,new):
            for name,value in(('GmRam00AE',xx&255),('GmRam00B8',xx>>8),('GmRam009A',yy&255),('GmRam00A4',yy>>8)):
                m[W.address(m.bundle,name)+slot]=value
            N.put(m,ScreenLeft_X_Pos=screen&255,ScreenLeft_PageLoc=screen>>8,R0=166,R1=57,R2=93,R3=231)
            z=N.invoke(m,'GmScreenPoint',a=83,x=slot,y=iy,p=p)
            results.append((z,[N.get(m,'R'+str(i))for i in range(8)]))
        (za,ra),(zb,rb)=results
        assert regs(za)==regs(zb)and ra==rb,(slot,xx,yy,screen,iy,p,regs(za),regs(zb),ra,rb)
        cycles.add(zb['cycles']-za['cycles']if'cycles'in za else zb['CPU']-za['CPU']);renderer+=1
    assert cycles=={20},cycles  # Taken backward loop branch crosses B9/B8 page.
    materials=[];b=old.bundle;at=W.location(b,'MTileAttribute')
    for tile in range(256):
        attr=raw[at+tile]
        read_solid=tile not in(0,35,38,194,195,95,96)and bool(attr&1)
        materials.append((tile,attr,read_solid,tile==35))
    result=dict(passed=True,layout=layout,exhaustive_tile_role_status_pairs=tiles,intended_side23_return_changes=changes,
        coordinate_wrap_geometry_pairs=geometry,foreign_owner_pairs=foreign,ScreenPoint_AXYP_R0_R7_pairs=renderer,ScreenPoint_added_cycles=sorted(cycles),
        material_rows_SHA256=sha256(json.dumps(materials).encode()).hexdigest(),tile23_attribute=materials[35][1],
        fixture='Declared native query/tile/renderer CPU components, not seeded ordinary gameplay',outputs=0,Mesen_run=False)
    return result


if __name__=='__main__':
    raw,boundary=C.load590()
    def forbid(*args,**kwargs):raise RuntimeError('Gimmick component fixture attempted files')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid):q=run(raw)
    q['input_binding']=boundary;q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
