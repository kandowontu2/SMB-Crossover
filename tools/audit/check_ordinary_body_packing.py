"""Independent immutable-ROM preservation check for the ordinary layout slice."""
from pathlib import Path
import argparse, hashlib, json, re
from check_mm_bass_injury_packing import Rom
from analyze_sprite_vertical_alignment import decode, flip, signed

def image(data, bank):
    out={}
    for o in range(len(data)-4, 0, -4):
        t,a,y,x=data[o:o+4]
        pic=flip(decode(bank[(t&62)//2*32:(t&62)//2*32+32]),a&64,a&128)
        for yy,row in enumerate(pic):
            for xx,c in enumerate(row):
                if c:out.setdefault((signed(x)+xx,signed(y)+yy),(a&3,c))
    return out

def check(oldpath,newpath):
    old,new=Rom(oldpath),Rom(newpath)
    oc,nc=old.chr(),new.chr();om,nm=old.read('ChrPhysicalMap',256),new.read('ChrPhysicalMap',256)
    assert len(nc)==len(oc)+1024 and len(nc)<=256*1024
    assert all(om[i]==nm[i]for i in range(256)if i!=0x83)
    assert oc[om[0x83]*1024:(om[0x83]+1)*1024]==bytes(1024) and nm[0x83]*1024==len(oc)
    allowed=set(range(om[0xe1]*1024+30*32,om[0xe1]*1024+31*32))|set(range(om[0x1d]*1024+31*32,om[0x1d]*1024+32*32))
    changed={i for i,(a,b)in enumerate(zip(oc,nc))if a!=b}
    assert changed<=allowed and len(changed)>0
    assert all(oc[i]==0 for i in allowed),'Only original zero pairs are allocated'
    records=0
    for name in old.syms.keys()&new.syms.keys():
        if re.fullmatch(r'(XgBASS|RgBILL|RgLANCE).*?(Left|Right)',name):
            assert old.pose(name)==new.pose(name),name;records+=1
    assert records>100
    tables=0;references=0
    for role,n in(('XgBASS',252),('RgBILL',144),('RgLANCE',144)):
        assert old.read(role+'Banks',n)==new.read(role+'Banks',n);tables+=1
        for side in('Left','Right'):
            def resolved(r):
                g=r.segs[int(r.syms[role+side+'Lo']['seg'])];base=int(g['ooffs'])-int(g['start'],0)
                lo,hi=r.read(role+side+'Lo',n),r.read(role+side+'Hi',n)
                return [r.data[base+lo[i]+256*hi[i]:base+lo[i]+256*hi[i]+1+r.data[base+lo[i]+256*hi[i]]]for i in range(n)]
            assert resolved(old)==resolved(new),(role,side);tables+=2;references+=n
    composites=[]
    for label,source,b in(('OrdBassWalk1','XgBASS0_WALK1',0x83),('OrdBassWalk3','XgBASS0_WALK3',0xe1),('OrdBillWalk2','RgBILL0_WALK2',0x1d)):
        ob=0xe0 if b==0x83 else b
        for side in('Left','Right'):
            a=image(old.pose(source+side),oc[om[ob]*1024:(om[ob]+1)*1024])
            z=image(new.pose(label+side),nc[nm[b]*1024:(nm[b]+1)*1024])
            assert a==z,(label,side)
            composites.append(dict(pose=label+side,opaque_pixels=len(a)))
    for b in(0xe0,0xe1,0xe2,0xe3,0xe4,0xe5,0xe6,0x82):
        assert nc[nm[b]*1024:nm[b]*1024+32]==oc[om[b]*1024:om[b]*1024+32],('Original normal buster',b)
    assert nc[nm[0x83]*1024:nm[0x83]*1024+32]==oc[om[0xe0]*1024:om[0xe0]*1024+32]
    return dict(before_sha256=hashlib.sha256(old.data).hexdigest(),after_sha256=hashlib.sha256(new.data).hexdigest(),used_chr_kib=len(nc)//1024,capacity_kib=256,original_records_preserved=records,original_table_semantics_preserved=tables,original_pointer_references_preserved=references,original_chr_changed_bytes=len(changed),allowed_spare_pairs=['E1:30','1D:31'],new_logical_bank='83',new_physical_bank=nm[0x83],normal_buster_preserved=True,composites=composites)

def main():
    p=argparse.ArgumentParser();p.add_argument('before',type=Path);p.add_argument('after',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    report={m:check(a.before/f'smb-crossover-{m}.nes',a.after/f'smb-crossover-{m}.nes')for m in('mmc3','mmc5')}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,indent=2)+'\n');print('PASS ordinary body original records, tables, all unrelated CHR bytes, six exact palette-symbol composites and buster banks');return 0
if __name__=='__main__':raise SystemExit(main())
