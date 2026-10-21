"""Compare immutable pre/post injury-art ROMs; no emulator state is authored."""
from pathlib import Path
import argparse,hashlib,json,re

def debug(path):
    segs={};symbols={}
    for line in path.read_text().splitlines():
        if not line.startswith(('seg\t','sym\t')):continue
        d=dict(re.findall(r'(\w+)=("[^"]*"|[^,]+)',line.split('\t',1)[1]))
        d={k:v.strip('"')for k,v in d.items()}
        if line.startswith('seg\t'):segs[int(d['id'])]=d
        elif d.get('type')=='lab'and 'seg'in d:symbols[d['name']]=d
    return segs,symbols

class Rom:
    def __init__(self,path):
        self.path=path;self.data=path.read_bytes();self.segs,self.syms=debug(path.with_suffix('.dbg'))
    def read(self,name,n):
        s=self.syms[name];g=self.segs[int(s['seg'])]
        off=int(g['ooffs'])+int(s['val'],0)-int(g['start'],0)
        return self.data[off:off+n]
    def pose(self,name):return self.read(name,1+self.read(name,1)[0])
    def chr(self):
        g=next(g for g in self.segs.values()if g['name']=='CHR')
        return self.data[int(g['ooffs']):int(g['ooffs'])+int(g['size'],0)]

def check(before,after):
    old,new=Rom(before),Rom(after);oldchr,newchr=old.chr(),new.chr()
    assert newchr[:len(oldchr)]==oldchr,'Every preexisting physical CHR byte remains identical'
    assert len(newchr)==len(oldchr)+2048 and len(newchr)<=256*1024
    om,nm=old.read('ChrPhysicalMap',256),new.read('ChrPhysicalMap',256)
    assert all(om[i]==nm[i]for i in range(256)if i not in(0x81,0x82))
    changed=[];unchanged=0;bodyparts=0
    for name in sorted(old.syms.keys()&new.syms.keys()):
        if not re.fullmatch(r'(MmMM_.*|XgBASS.*)(Left|Right)',name):continue
        a,b=old.pose(name),new.pose(name)
        if '_HURT'not in name:
            assert a==b,('Unchanged non-hurt record',name);unchanged+=1;continue
        assert a[0]==b[0]and a[0]%4==0
        role=name.startswith('MmMM_');ob=0x49 if role else 0xe1;nb=0x81 if role else 0x82
        for o in range(1,len(a),4):
            assert a[o+1:o+4]==b[o+1:o+4],('Body palette/flip/offset preserved',name,o)
            ot=(a[o]&0x3e)*16;nt=(b[o]&0x3e)*16
            assert oldchr[om[ob]*1024+ot:om[ob]*1024+ot+32]==newchr[nm[nb]*1024+nt:nm[nb]*1024+nt+32],('Body source CHR preserved',name,o)
            bodyparts+=1
        changed.append(name)
    assert len(changed)==10 and unchanged>100
    for table,length,allowed in(('MegaManSpriteBanks',64,{15,31,47,63}),('XgBASSBanks',252,{11,95,179})):
        a,b=old.read(table,length),new.read(table,length)
        assert {i for i in range(length)if a[i]!=b[i]}==allowed
        assert all(b[i]==(0x81 if table=='MegaManSpriteBanks'else 0x82)for i in allowed)
    return dict(before_sha256=hashlib.sha256(old.data).hexdigest(),after_sha256=hashlib.sha256(new.data).hexdigest(),
                preserved_chr_bytes=len(oldchr),used_chr_kib=len(newchr)//1024,capacity_kib=256,
                preserved_non_hurt_records=unchanged,preserved_hurt_records=len(changed),preserved_hurt_hardware_parts=bodyparts,
                only_logical_banks_changed=[0x81,0x82])

def main():
    p=argparse.ArgumentParser();p.add_argument('before',type=Path);p.add_argument('after',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    report={m:check(a.before/f'smb-crossover-{m}.nes',a.after/f'smb-crossover-{m}.nes')for m in('mmc3','mmc5')}
    a.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
