"""Render actual cold-menu Battletoads OAM as source-derived roster art."""
import json,hashlib
from PIL import Image
import audit_current_menu_indicators_1102_v1 as A
import check_hogan_current_bounded_v1 as M
from check_tmnt_render_oa import address
O=A.R/'build/battletoads-silhouette-1102-v1'
def main():
    b=A.bundle();m=M.fresh(b);M.put(m,CrossoverMenuIndex=23)
    M.invoke(m,'MenuResolveCharacter');M.invoke(m,'QueueSelection')
    assert M.get(m,'SelectedCharacter')==33
    page=M.get(m,'CurrentCHRBank')+768
    assert page==915
    art=b['raw'][1048592+page*1024:1048592+(page+1)*1024]
    parts=[list(m[512+i:516+i])for i in range(0,256,4)if m[512+i]<240]
    x0=min(p[3]for p in parts);y0=min(p[0]for p in parts)
    pixels=[[0]*24 for _ in range(40)]
    for y,t,a,x in reversed(parts):
        assert t<64 and not t&1
        for yy in range(16):
            for xx in range(8):
                sy=15-yy if a&128 else yy;sx=7-xx if a&64 else xx
                at=t*16+(sy//8)*16+sy%8
                v=(art[at]>>(7-sx)&1)+2*(art[at+8]>>(7-sx)&1)
                if v:pixels[y-y0+yy][x-x0+xx]=v
    occupied=[y for y,row in enumerate(pixels)if any(row)]
    pixels=pixels[min(occupied):max(occupied)+1]
    height=len(pixels)
    O.mkdir(exist_ok=True)
    im=Image.new('RGB',(24,height));colors=[(0,0,0),(100,100,100),(180,180,180),(248,248,248)]
    im.putdata([colors[v]for row in pixels for v in row]);im.resize((192,256),Image.Resampling.NEAREST).save(O/'source-silhouette.png')
    q=dict(slot=23,top_tile=12,left_tile=25,width=24,height=height,pixels=pixels,actual_menu_OAM=parts,source_CHR_page=page,source_CHR_SHA256=hashlib.sha256(art).hexdigest(),base_ROM_SHA256=hashlib.sha256(b['raw']).hexdigest(),scope='Actual Rash cold-menu OAM and current source CHR, no invented pixels; same body silhouette applies to Zitz alternate. Fit to at most32px high before menu placement.')
    (O/'pixels.json').write_text(json.dumps(q,indent=2)+'\n');print({k:v for k,v in q.items()if k!='pixels'})
if __name__=='__main__':main()
