"""Current original source facing and native hardware-format body raster proof."""
import json
from pathlib import Path
import check_bubble_native_event_1102_v9 as E
import prepare_bubble_bobble_native_art_1101_v2 as ART
from PIL import Image,ImageDraw

N,Q,P,R,address=E.N,E.Q,E.P,E.R,E.address
O=R/'build/bub-menu-candidate-1102-v2'
CURRENT=R/'build/menu-family-root-candidate-1102-v1/mr-gimmick-family.nes'
PIN='22d09909bf952ef007d1582589dc869073262784bf38b92d2c7b206ce3c45b19'

def main():
    _,b,q,route=E.bundle();before=b['raw'];b['raw']=CURRENT.read_bytes();assert P.sha(b['raw'])==PIN
    carriers=[301,305,337,362,363,440,819,666,441]
    assert all(before[1048592+p*1024:1048592+(p+1)*1024]==b['raw'][1048592+p*1024:1048592+(p+1)*1024]for p in carriers)
    donor=ART.B.ROM.read_bytes()[16+131072:]
    def original(tile):
        at=(2 if tile&1 else 1)*4096+(tile&254)*16
        return donor[at:at+32]
    def native(tile):
        assert tile&1
        at=1048592+441*1024+(tile&254)*16
        return b['raw'][at:at+32]
    rows=[];preview=Image.new('RGB',(352,304),(24,24,30));draw=ImageDraw.Draw(preview)
    for identity in[0,1]:
        for direction in[1,2]:
            m=Q.fresh(b,route,identity);E.main_fields(m);oy=8 if identity else 0
            N.put(m,Player_X_Position=96,PlayerFacingDir=direction)
            xs=[]
            for epoch in range(18):
                N.put(m,FrameCounter=epoch,SavedJoypadBits=direction,SavedJoypad1Bits=direction,VRAM_Buffer1_Offset=0)
                N.invoke(m,'GameCoreRoutine',x=0,y=0)
                xs.append(N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'))
            assert(xs[-1]>xs[0])==(direction==1),(identity,direction,xs)
            assert N.get(m,'PlayerFacingDir')==direction
            N.put(m,CurrentOAMOffset=0,GuestOamRotationActive=0,RgOamUsed=0,VRAM_Buffer1_Offset=0)
            m[512:768]=[248,0,0,0]*64
            N.invoke(m,'HuDraw',a=0,x=0,y=0)
            cached=list(m.ram[2][0x100+oy:0x108+oy]);native_rows=[list(m[512+i:516+i])for i in range(0,256,4)if m[512+i]<240]
            assert len(native_rows)==2,(identity,direction,native_rows)
            assert all(row[2]&64==(64 if direction==1 else 0)for row in native_rows)
            assert cached[2]&64==cached[6]&64==(64 if direction==1 else 0)
            source_rows=[]
            for i in[0,4]:
                y,t,a,x=cached[i:i+4];source_rows.append([y,t,a,(x-16)&255])
            sr=ART.raster(source_rows,original);nr=ART.raster(native_rows,native)
            assert sr==nr,(identity,direction,source_rows,native_rows)
            assert sr
            left=min(x for x,y in sr);top=min(y for x,y in sr)
            ox=16+176*(direction-1);oypic=22+148*identity
            draw.text((ox,oypic),('Bob'if identity else'Bub')+(' RIGHT'if direction==1 else' LEFT'),fill='white')
            colors=[(0,0,0),((80,205,80)if not identity else(80,190,230)),((230,130,80)if not identity else(120,120,230)),(245,245,245)]
            for(x,y),(_,value)in sr.items():
                xx=ox+8*(x-left);yy=oypic+16+8*(y-top);draw.rectangle((xx,yy,xx+7,yy+7),fill=colors[value])
            rows.append(dict(identity=identity,direction='right'if direction==1 else'left',source_attr=cached[2],native_facing=N.get(m,'PlayerFacingDir'),
                initial_x=96,final_x=xs[-1],source_OAM=cached,actual_native_OAM=native_rows,opaque_pixels=len(sr),original_source_raster_exact=True))
    preview.save(O/'runtime-facing-v19.png')
    result=dict(passed=True,ROM_sha256=PIN,source_original_ROM_sha256=ART.B.PIN,ROM_written=False,source_changed=False,native_emulator=False,
        cases=rows,scope='Bothidentities original-input nativeGameCore direction and HuDraw physical-format OAM; bothspriteattrs and allactual renderedpixels equal original donorart/pairedtiles. Current22d099 runtimebody/bridge equals613b. No visual gameplay correction needed. Compactpanel uses displayRGB for inspection; nativepalette assertion remains existingpass.',
        bindings={str(p.relative_to(R))if p.is_relative_to(R)else str(p):P.sha(p.read_bytes())for p in[Path(__file__),CURRENT,E.O/'native-event-v9-image.bin',R/'tools/reference/bubble_bobble_native_leaves_1101_v3.inc',ART.B.ROM]})
    (O/'runtime-facing-v19.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,ROM_sha256=PIN,cases=rows)))

if __name__=='__main__':main()
