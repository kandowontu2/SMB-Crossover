"""Freeze decoded baseline-ROM patterns for independent body-layout tests."""
from pathlib import Path
import sys,json,hashlib
from check_mm_bass_injury_packing import Rom
from analyze_sprite_vertical_alignment import decode,flip,signed
root=Path(__file__).resolve().parents[2]
def lua(v):
    if isinstance(v,dict):return'{'+','.join(('['+str(k)+']'if isinstance(k,int)else'['+json.dumps(k)+']')+'='+lua(x)for k,x in v.items())+'}'
    if isinstance(v,list):return'{'+','.join(lua(x)for x in v)+'}'
    if isinstance(v,str):return json.dumps(v)
    return str(v)
def main():
    path=Path(sys.argv[1]);r=Rom(path);mapping=r.read('ChrPhysicalMap',256);raw=r.chr();refs={}
    for role,prefix,poses,stride,anchor in(('bass','XgBASS',(1,3,13),84,'XgBASS0_STANDRight'),('bill','RgBILL',(2,),48,'RgBILL0_STANDRight'),('lance','RgLANCE',(2,),48,'RgLANCE_UPWALK2Right')):
        seg=r.segs[int(r.syms[anchor]['seg'])];offset=int(seg['ooffs'])-int(seg['start'],0);refs[role]={}
        for power in range(3):
            refs[role][power]={}
            for pose in poses:
                i=power*stride+pose;bank=r.read(prefix+'Banks',i+1)[i];block=raw[mapping[bank]*1024:(mapping[bank]+1)*1024];refs[role][power][pose]={}
                for side in ('Left','Right'):
                    ptr=r.read(prefix+side+'Lo',i+1)[i]+256*r.read(prefix+side+'Hi',i+1)[i];d=r.data[offset+ptr:offset+ptr+1+r.data[offset+ptr]];parts=[]
                    for o in range(1,len(d),4):
                        t,a,y,x=d[o:o+4];pic=flip(decode(block[(t&62)//2*32:(t&62)//2*32+32]),a&64,a&128)
                        parts.append(dict(x=signed(x),y=signed(y),a=a,rows=[''.join(map(str,row))for row in pic]))
                    refs[role][power][pose][side]=dict(bank=bank,parts=parts)
    d=r.pose('XgBASSWeapon0Right');bank=raw[mapping[0xe0]*1024:(mapping[0xe0]+1)*1024];refs['buster']=[]
    for o in range(1,len(d),4):
        t,a,y,x=d[o:o+4];pic=flip(decode(bank[(t&62)//2*32:(t&62)//2*32+32]),a&64,a&128)
        refs['buster'].append(dict(x=signed(x),y=signed(y),a=a,rows=[''.join(map(str,row))for row in pic]))
    target=root/'tests/fixtures/ordinary-body-composite-v30.lua'
    target.write_text('-- Independent immutable30 hardware pose/CHR decode; does not read31 assets.\n-- ROM SHA256 '+hashlib.sha256(r.data).hexdigest()+'\nreturn '+lua(refs)+'\n')
    print('PASS frozen30 reference',len(target.read_bytes()),'bytes',hashlib.sha256(target.read_bytes()).hexdigest());return 0
if __name__=='__main__':raise SystemExit(main())
