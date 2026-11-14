"""Current421 WorldTile ABI vectors; explicitly seeded primitive diagnostics.

These terrain/coordinate vectors isolate the translation. They are not normal
gameplay qualification, a mounted fix, a native run or permission to allocate.
"""
from collections import Counter
from hashlib import sha256
import json
import check_prince_pipe_usability_1114 as Base

F,P,N=Base.Factory,Base.P,Base.P.N


def word(s,at,value):s[at:at+2]=(value&65535).to_bytes(2,'little')


def invoke(m,pc=0xbde2):
    m.raw_page(1,3);m.raw_page(2,2)
    N.put(m,CurrentBank=3,CurrentBankC=2)
    c=N.NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=83,71,109,0x61,224
    c.stPushWord(0x5ffe);points=[]
    for _ in range(6000):
        if(c.pc,c.sp)==(0x5fff,224):break
        if c.pc==0xb310 and m.rawtags[1]==3:
            points.append([int.from_bytes(m.ram[3][0x1369:0x136b],'little'),
                int.from_bytes(m.ram[3][0x136b:0x136d],'little')])
        assert m[c.pc],('Primitive BRK',hex(c.pc),m.rawtags)
        c.step()
    else:raise AssertionError('WorldTile primitive bound')
    return dict(material=c.a,registers=[c.a,c.x,c.y,c.p,c.sp],
        cell=int.from_bytes(m.ram[2][0x7d:0x7f],'little'),points=points,
        surface=int.from_bytes(m.ram[2][0x7f:0x81],'little'))


def run(raw):
    m,_=Base.cold(raw);b=m.bundle
    buffer=P.W.address(b,'Block_Buffer_1');attr=P.W.address(b,'MTileAttribute')
    assert m[attr+0x54]&1 and m[attr+0x14]&1
    rows=[];counts=Counter()
    # Half-cells and a page boundary matter because a 32px donor cell may
    # contain independently solid/empty 16px native columns.
    for left in(240,256,448,464):
      for facing in(0,255):
       for delta in(-38,-32,-24,-16,-8,0,16,24,32):
        q=N.fork(m);s=q.ram[2];x=left+delta
        N.put(q,Player_X_Position=x&255,Player_PageLoc=x>>8,
            Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0)
        word(s,0x60f,x+8);s[0x611]=128;s[0x615]=facing
        s[0x616]=1;s[0x618]=1;s[0x617]=8
        # Constructor projection is kept explicit for the primitive ABI.
        word(s,0x89,77);s[0x8b]=128;s[0x88]=3
        s[0x4b1]=10;s[0x7a]=0;s[0x82]=0
        raw_query=x+8-(4 if facing else 40);word(s,0x78,raw_query)
        for page in range(2):
         for row in range(13):
          for col in range(16):
           wx=page*256+col*16;wy=row*16+32
           q[buffer+page*208+row*16+col]=0x54 if wy>=208 else 0x14 if left<=wx<left+16 and wy>=160 else 0
        result=invoke(q)
        body=[x+2,x+14];overlap=max(body[0],left)<min(body[1]+1,left+16)
        counts['vectors']+=1
        if result['material']==20 and not overlap:counts['wall_material_without_body_overlap']+=1
        rows.append(dict(left=left,facing=facing,native_x=x,body=body,
            real_body_overlap=overlap,raw_query=raw_query,**result))
    return dict(ROM_SHA256=F.PIN,primitive_fixture_only=True,normal_gameplay_claim=False,
        code_changes=0,outputs=0,Mesen=False,counts=dict(counts),vectors=rows)


if __name__=='__main__':
    q=run(F.ROM.read_bytes())
    digest=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    q['vectors']=[r for r in q['vectors']if r['material']==20 and not r['real_body_overlap']][:10]
    q['receipt_SHA256']=digest
    print(json.dumps(q,separators=(',',':')),flush=True)
