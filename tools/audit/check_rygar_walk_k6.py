"""Independent native-OAM pixel comparison and unchanged-pose asset check."""
from pathlib import Path
import hashlib,json,re,sys,traceback
R=Path(__file__).resolve().parents[2];O=R/'build/verification/rygar-walk-k4'
sys.path.append('C:/Users/kando/AppData/Local/Programs/Python/Python314/Lib/site-packages')
from verify_native_relocation import load
from PIL import Image
RGB={1:(216,40,0,255),2:(252,252,252,255),3:(0,0,0,255)}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def reference(frame):
    folder=R/'build/rygar-audit/walk';base=folder/f'rygar-{frame}'
    vram=base.with_suffix('.chr').read_bytes();oam=base.with_suffix('.oam').read_bytes()
    previous=(folder/f'rygar-{frame-1}.ram').read_bytes();origin=previous[0x512]+8
    im=Image.new('RGBA',(96,80));count=0
    # Inspect the whole original player's reserved0..7, never the old truncated
    # loop, and retain each original native OAM coordinate/flip/pattern index.
    for i in range(8):
        sy,t,attr,sx=oam[i*4:i*4+4]
        if sy>=240:continue
        assert attr&3==0
        count+=1
        for yy in range(16):
            row=15-yy if attr&128 else yy
            at=(t&1)*4096+(t&254)*16+(row//8)*16+row%8
            for xx in range(8):
                bit=xx if attr&64 else 7-xx
                color=((vram[at]>>bit)&1)|(((vram[at+8]>>bit)&1)<<1)
                if color:
                    # Original palette0 has white/red/black, mapped to the
                    # installed game's red/white/black indices respectively.
                    rgba={1:RGB[2],2:RGB[1],3:RGB[3]}[color]
                    im.putpixel((40+sx+xx-origin,64+sy+1+yy-195),rgba)
    return im,count
def linked(path):
    _,labels=load(path);raw=path.read_bytes()
    def c(address):return raw[16+32*8192+address-0xc000]
    def fixed(address):return raw[16+63*8192+address-0xe000]
    def render(index,left):
        side='Left' if left else 'Right'
        ptr=c(labels['XgRYGAR'+side+'Lo']+index)+256*c(labels['XgRYGAR'+side+'Hi']+index)
        logical=c(labels['XgRYGARBanks']+index);physical=fixed(labels['ChrPhysicalMap']+logical)
        data=raw[16+512*1024+physical*1024:16+512*1024+(physical+1)*1024]
        im=Image.new('RGBA',(96,80));count=c(ptr)//4
        for i in range(count):
            tile,attr,y,x=[c(ptr+1+i*4+j)for j in range(4)]
            x=x if x<128 else x-256;y=y if y<128 else y-256
            for yy in range(16):
                row=15-yy if attr&128 else yy
                at=(tile&0x3e)*16+(row//8)*16+row%8
                for xx in range(8):
                    bit=xx if attr&64 else 7-xx
                    color=((data[at]>>bit)&1)|(((data[at+8]>>bit)&1)<<1)
                    if color:im.putpixel((32+x+xx,32+y+yy),RGB[color])
        return im,count
    return raw,render
def main():
    out=O/'pixel-check-k7';assert not out.exists();out.mkdir()
    report=dict(status='RUNNING',scope=__doc__,mappers={})
    try:
        for mapper in ('mmc3','mmc5'):
            path=O/f'repaired-k5-{mapper}/smb-crossover-{mapper}.nes'
            old,oldrender=linked(R/f'build/checkpoints/ryu-overlap-hr/build/smb-crossover-{mapper}.nes')
            new,render=linked(path);assert len(old)==len(new) and old[:16]==new[:16]
            changedPRG=sorted({(i-16)//8192 for i,(a,b)in enumerate(zip(old[:16+512*1024],new[:16+512*1024]))if a!=b})
            assert changedPRG==[25,30,32,37],changedPRG
            def globals32(p):
                lines=p.with_suffix('.dbg').read_text().splitlines();segments={}
                for line in lines:
                    if line.startswith('seg\t')and'ooffs='in line:
                        f=dict(re.findall(r'(\w+)=("[^"]*"|[^,]+)',line.split('\t',1)[1]));segments[f['id']]=f
                result={}
                for line in lines:
                    if not line.startswith('sym\t'):continue
                    f=dict(re.findall(r'(\w+)=("[^"]*"|[^,]+)',line.split('\t',1)[1]))
                    if f.get('scope')=='1'and'val'in f and f.get('seg')in segments:
                        s=segments[f['seg']];value=int(f['val'],0);physical=int(s['ooffs'])+value-int(s['start'],0)
                        if (physical-16)//8192==32:result[f['name']]=value
                return result
            oldnames=globals32(R/f'build/checkpoints/ryu-overlap-hr/build/smb-crossover-{mapper}.nes');newnames=globals32(path)
            moved=[(v,newnames[n])for n,v in oldnames.items()if n in newnames and v!=newnames[n]]
            # Other changed PRG bytes are the actual relocated low-byte operands
            # of Rygar/Bill-flare graphic pointers, never instruction opcodes.
            for bank in (25,30,37):
                for i in range(16+bank*8192,16+(bank+1)*8192):
                    if old[i]!=new[i]:
                        assert any((a&255,b&255)==(old[i],new[i])or((a+8)&255,(b+8)&255)==(old[i],new[i])for a,b in moved),('unbound pointer byte',bank,i,old[i],new[i])
            changed=[];native=0
            for index in range(252):
                pose=index%84
                for left in (False,True):
                    a,_=oldrender(index,left);b,pieces=render(index,left)
                    if pose in (1,2,3):
                        frame=([432,440,447]if left else[302,309,316])[pose-1]
                        expected,count=reference(frame)
                        assert b.tobytes()==expected.tobytes(),('native pixels',mapper,index,left,frame)
                        assert count==pieces==(6 if pose==2 else 4)
                        native+=1
                    else:assert a.tobytes()==b.tobytes(),('unrelated pose changed',mapper,index,left)
                    if a.tobytes()!=b.tobytes():changed.append([index,left])
            report['mappers'][mapper]=dict(ROM_sha256=sha(path),native_pixel_cases=native,unchanged_other_pose_cases=486,changed_walk_images=changed,changed_PRG_banks=changedPRG)
        report['status']='PASS_ORIGINAL_NATIVE_WALK_PIXELS_BOTH_FACINGS_ALL_POWERS'
    except Exception as exc:report.update(status='FAIL_RETAINED',error=repr(exc),traceback=traceback.format_exc());raise
    finally:(out/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'])
if __name__=='__main__':main()
