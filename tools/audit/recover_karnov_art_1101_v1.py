"""Execute original Karnov sprite renderer and pack its exact body tile pairs."""
from pathlib import Path
import hashlib,json,sys
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from verify_native_relocation import NesMPU
from recover_karnov_actor_1101_v1 import ROM,EXPECTED
O=R/'build/karnov-original-art-1101-v1';REF=R/'build/karnov-native-reference-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


class Memory(list):
    def __init__(self,raw,ram):
        super().__init__([0]*65536);self.raw=raw;self.select=0;self.banks=[0,11,14,15];self.writes=[]
        self[:2048]=ram
        for i,b in enumerate(self.banks):self.page(i,b)
    def page(self,i,b):self.banks[i]=b;list.__setitem__(self,slice(0x8000+i*8192,0xa000+i*8192),self.raw[16+b*8192:16+(b+1)*8192])
    def __setitem__(self,k,v):
        if isinstance(k,int):
            self.writes.append((k,v))
            if k==0x8000:self.select=v&7;return
            if k==0x8001:
                assert self.select in [6,7];self.page(self.select-6,v&15);return
            assert k<0x8000,('Renderer ROM write',hex(k),v)
        list.__setitem__(self,k,v)


def pixels(pattern,attr):
    out={}
    for y in range(16):
        yy=15-y if attr&128 else y;lo=pattern[(yy//8)*16+yy%8];hi=pattern[(yy//8)*16+yy%8+8]
        for x in range(8):
            bit=x if attr&64 else 7-x;v=((lo>>bit)&1)|(((hi>>bit)&1)<<1)
            if v:out[x,y]=v
    return out


def main():
    O.mkdir(exist_ok=True);assert not(O/'source-stage.json').exists()
    raw=ROM.read_bytes();assert sha(ROM)==EXPECTED;chr=raw[16+131072:];assert len(chr)==65536
    palette_proof=R/'build/karnov-palette-native-1101-v1/controls.json';pal=json.loads(palette_proof.read_text());assert pal['passed']and pal['donor_sha256']==EXPECTED
    for p,h in pal['bindings'].items():assert sha(p)==h,p
    palette_path=R/'tools/Windows/NEXXT 3.0/defaults/nes.pal';palette_rgb=palette_path.read_bytes();colors={v:tuple(palette_rgb[3*pal['body_palette'][v]:3*pal['body_palette'][v]+3])for v in [1,2,3]}
    ref=json.loads((REF/'capture/reference.json').read_text());assert ref['passed'];ram=ref['initial_fixture'];rows=[];glyphs=[];patterns={};source_pages=set();cycles=[]
    for state in range(32):
        for face in [0,128]:
            for hurt in [0,64]:
                for phase in [0,1]:
                    m=Memory(raw,ram)
                    for at,v in {0x62:state|face,0x63:128,0x64:144,0x68:hurt,0xe8:phase,0x61:0}.items():m[at]=v
                    c=NesMPU(memory=m,pc=0xa070);c.sp=224;c.p=0x31;c.stPushWord(0x7ffe)
                    for _ in range(6000):
                        if c.pc==0x7fff:break
                        assert m[c.pc]!=0,('Original render BRK',hex(c.pc));c.step()
                    else:raise AssertionError('Original renderer bound')
                    assert m.banks[0]==0 and c.sp==224
                    page=m[0x15];source_pages.add(page);packet=[];before={};after={}
                    for n in range(6):
                        y,t,attr,x=m[0x214+4*n:0x218+4*n]
                        if y>=240:continue
                        base=(t&1)*4096+(t&254)*16
                        assert base//1024==4,('Body must use its original1KiB sprite window',state,t)
                        pattern=chr[page*1024+(base&1023):page*1024+(base&1023)+32];assert len(pattern)==32
                        if pattern not in patterns:patterns[pattern]=len(glyphs);glyphs.append(pattern)
                        # Original renderer already selects one1KiB page per
                        # pose. Keep that bank switch and move its odd tiles
                        # from source sprite window4 into host window0.
                        tile=t&254;dx=(x-128)&255;dy=(y-144)&255
                        packet.extend([tile,attr,dy,dx]);xx=dx-256 if dx>=128 else dx;yy=dy-256 if dy>=128 else dy
                        for(p,q),value in pixels(pattern,attr).items():
                            before.setdefault((xx+p,yy+q),value);after.setdefault((xx+p,yy+q),value)
                    assert before==after
                    rows.append(dict(state=state,facing=face,hurt=hurt,phase=phase,source_CHR_page=page,cells=len(packet)//4,packet=[len(packet),*packet],pixels=len(before),pixel_sha256=hashlib.sha256(json.dumps(sorted((x,y,c)for(x,y),c in before.items())).encode()).hexdigest()));cycles.append(c.processorCycles)
    assert source_pages=={0,1,2,3,24},source_pages
    physical_order=sorted(source_pages);packed=b''.join(chr[p*1024:(p+1)*1024]for p in physical_order);pages=len(physical_order);(O/'body.chr').write_bytes(packed)
    # Verify every emitted record addresses the same pattern after reindexing.
    for row in rows:
        row['packed_page']=physical_order.index(row['source_CHR_page']);after={}
        for i in range(1,len(row['packet']),4):
            t,a,y,x=row['packet'][i:i+4];assert t<64 and not t&1
            at=row['packed_page']*1024+t*16;pattern=packed[at:at+32]
            assert pattern==chr[row['source_CHR_page']*1024+t*16:row['source_CHR_page']*1024+t*16+32]
            x=x-256 if x>=128 else x;y=y-256 if y>=128 else y
            for(px,py),v in pixels(pattern,a).items():after.setdefault((x+px,y+py),v)
        assert len(after)==row['pixels']and hashlib.sha256(json.dumps(sorted((x,y,c)for(x,y),c in after.items())).encode()).hexdigest()==row['pixel_sha256']
    img=Image.new('RGB',(8*64,4*96),'#131c29');draw=ImageDraw.Draw(img)
    for state in range(32):
        x0=(state%8)*64;y0=(state//8)*96;draw.text((x0+2,y0+1),str(state),fill='white')
        row=next(r for r in rows if r['state']==state and r['facing']==0 and r['hurt']==0 and r['phase']==0)
        for i in range(1,len(row['packet']),4):
            t,a,y,x=row['packet'][i:i+4];x=x-256 if x>=128 else x;y=y-256 if y>=128 else y
            at=row['packed_page']*1024+t*16
            for(px,py),v in pixels(packed[at:at+32],a).items():
                xx=x0+24+2*(x+px);yy=y0+82+2*(y+py)
                if x0<=xx<x0+64 and y0+12<=yy<y0+96:draw.rectangle((xx,yy,xx+1,yy+1),fill=colors[v])
    img.save(O/'original-poses.png')
    report=dict(passed=True,original_renderer=True,native_port=False,installed=False,donor_sha256=EXPECTED,renderer_bank=11,renderer_CPU=0xa070,original_render_cases=len(rows),source_CHR_pages=sorted(source_pages),unique_8x16_patterns=len(glyphs),packed_CHR_pages=pages,packed_CHR_bytes=len(packed),original_body_palette=pal['body_palette'],hidden_source_cases=sum(not q['cells']for q in rows),renderer_cycle_range=[min(cycles),max(cycles)],poses=rows,scope='Actual original six-cell renderer, all32 states/two facings/two hurt flags/two clock phases. Original pattern-value/position/flip preservation after window4-to-window0 tile reindexing. Native cold-start PPU palette retained; host physical pages, palette lifecycle and resource integration still required.',bindings={str(p.resolve()):sha(p)for p in[Path(__file__),ROM,REF/'capture/reference.json',palette_proof,palette_path,O/'body.chr']})
    (O/'art-controls.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items()if k not in ['bindings','poses']}))


if __name__=='__main__':main()
