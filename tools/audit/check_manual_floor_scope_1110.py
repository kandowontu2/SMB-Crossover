"""Restore the authored-lift coarse reject when neither manual kind exists."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import tempfile

import check_manual_wide_horizontal_1110 as W

P,N,R=W.P,W.N,W.R
OUT=W.OUT
PROOF=OUT/'proof.json'


def sha(path):return sha256(path.read_bytes()).hexdigest()


def source():
    s=W.mini_source()
    s=P.replace_one(s,' jsr MiniManualInput\n nop\n nop\n nop\n jsr MiniStep',
                       ' jsr MiniManualInput\n jsr MiniStep')
    s=P.replace_one(s,'''MiniPlatformFloor:
    lda MiniAssistState
    ora MiniHorizontalState
    ora MiniLiftActor
    beq @miss''','''MiniPlatformFloor:
    lda MiniAssistState
    ora MiniHorizontalState
    bne @collision
    ldx MiniLiftActor
    beq @miss
    lda MiniX+1
    and #$e0
    cmp #$20
    bne @miss
@collision:''')
    return P.replace_one(s,' .res 8,$ea\nMiniHostGraphics:\n','MiniHostGraphics:\n')


def build():
    q=json.loads(PROOF.read_text())
    for path,digest in q['bindings'].items():assert sha(R/path)==digest,path
    base=W.BASE.read_bytes();assert W.sha(base)==W.PIN
    old=P.install(base,q['patches']);assert W.sha(old)==q['expected_memory_only_SHA256']
    with tempfile.TemporaryDirectory(dir=OUT) as tmp:
        kernel,labels=P.compile_source(Path(tmp),source()+'\n.export MiniHeadEvent,MiniTempPixel\n',P.L.CONFIG)
    assert len(kernel)==5120
    assert all(labels[k]==v for k,v in q['labels'].items() if k.startswith('MiniHost') or k in
               ('MiniStep','MiniAnimate','MiniNativeTile','MiniNativeDraw','MiniVectors','MiniWorldEnd'))
    rows=[p for p in q['patches'] if p['file_offset'] not in (P.L.CODE,P.L.COOKIE+3)]
    rows.extend((P.L.patch(base,P.L.CODE,kernel,'Restore no-manual authored-lift scope and remove retired NOPs'),
        P.L.patch(base,P.L.COOKIE+3,sha256(kernel+base[P.L.CODE+5120:P.L.CODE+7168]).digest()[:13],
                  'Exact complete Mini payload digest')))
    new=P.install(base,rows)
    return base,old,new,rows,q['labels']|labels,kernel,q


def floor(m,pc):
    m.raw_page(1,3);m.raw_page(2,2)
    c=N.NesMPU(memory=m,pc=pc);c.sp=224;c.a=85;c.x=0;c.y=91;c.p=0x31;c.stPushWord(0x5aff)
    P.run(c,lambda z:(z.pc,z.sp)==(0x5b00,224))
    return c


def cases(bundles,before_pc,after_pc):
    seeds=[P.scene(b,41) for b in bundles]
    xs=sorted(set(range(0,4096,17))|set(range(504,900))|{511,512,1023,1024,1583,1908,4095})
    count=hits=0
    for manual in (False,True):
      for x in xs:
        worlds=[P.slim_fork(seed) for seed in seeds]
        for m in worlds:
            for slot,left in enumerate((560,688,864)):
                P.set_slot(m,slot,Enemy_Flag=1,Enemy_ID=0x25,Enemy_State=0x40,
                           Enemy_X_Position=left&255,Enemy_PageLoc=left>>8,Enemy_Y_Position=192,Enemy_Y_HighPos=1)
            m.ram[2][0x30b]=3;m.ram[2][0x30d]=0
            m.ram[2][0x30e]=128 if manual else 0;m.ram[2][0x30f]=0
            m.ram[2][0x227]=0
            m.ram[2][0x250:0x252]=(x*16).to_bytes(2,'little')
            m.ram[2][0x270:0x272]=(184*16).to_bytes(2,'little')
            N.put(m,Player_Y_Position=160,Player_Y_HighPos=1)
        a,b=(floor(m,pc) for m,pc in zip(worlds,(before_pc,after_pc)))
        assert bool(a.p&1)==bool(b.p&1),(manual,x)
        for lo,hi in ((0,0x272),(0x274,0x1fe3),(0x1ff0,8192)):
            assert worlds[0].ram[2][lo:hi]==worlds[1].ram[2][lo:hi],(manual,x,lo,hi)
        if a.p&1:assert worlds[0].ram[2][0x272:0x274]==worlds[1].ram[2][0x272:0x274]
        assert worlds[0].ram[2][0x1ff0:]==worlds[1].ram[2][0x1ff0:]
        assert (a.a,a.p)==(b.a,b.p),(manual,x,(a.a,a.p),(b.a,b.p))
        if a.p&1:assert (a.x,a.y)==(b.x,b.y)
        count+=1;hits+=bool(a.p&1)
    return dict(cases=count,hits=hits,source_world_domain=[0,4095],
        authored_lefts=[560,688,864],supported_world_span=[554,894],coarse_world_span=[512,1023],
        manual_pending_or_active_unchanged=True,
        volatile_miss_XY='Internal missX/Y are dead before first native tile/host export use; complete GameCore/HostMain comparison retains publicAXYP.')


def late_core(before,after,old,new):
    result={}
    for x in (40,511,512,554,560,864,894,1023,1024,1048,1583,1908,3500):
      for assist in ('none','vertical','horizontal','pending'):
        worlds=[P.scene(b,41) for b in (before,after)]
        for m in worlds:
            camera=max(0,x-112)
            N.put(m,Player_X_Position=x&255,Player_PageLoc=x>>8,Player_Y_Position=176,Player_Y_HighPos=1,
                  ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8,
                  ScreenRight_X_Pos=(camera+255)&255,ScreenRight_PageLoc=(camera+255)>>8)
            m.ram[2][0x30b]=3
            if assist in ('vertical','horizontal'):
                h=assist=='horizontal'
                z=N.invoke(m,'ManualPlatform',x=0x42 if h else 0x41,y=20 if h else 244)
                assert z['X'] in range(1,7)
                m.ram[2][0x30f if h else 0x30e]=z['X']
            elif assist=='pending':m.ram[2][0x30f]=128
        result[f'{x}:{assist}']=P.regular_parity(worlds,41,old,new)
    return result


def main():
    a=argparse.ArgumentParser();a.parse_args();OUT.mkdir(exist_ok=True)
    base,old,new,rows,labels,kernel,q=build()
    print('new exact memory image',W.sha(new),flush=True)
    before,after=P.bundles(old,new)
    leaf=cases((before,after),q['labels']['MiniPlatformFloor'],labels['MiniPlatformFloor'])
    print('Floor scope',leaf,flush=True)
    regular={owner:P.regular_parity([P.scene(before,owner),P.scene(after,owner)],owner,old,new)
             for owner in (0,5,25,29,34,41,42)}
    late=late_core(before,after,old,new)
    W.D.offset=W.right_offset
    owners={owner:dict(controls=W.D.controls(P.scene(after,owner),owner,labels),
                       carry=W.carrying(P.scene(after,owner),owner)) for owner in (41,34)}
    refs=(Path(__file__).resolve(),PROOF,W.SOURCE,W.DATA,W.BASE,Path(W.__file__))
    result=q|dict(passed=True,interrupt_pending=True,expected_memory_only_SHA256=W.sha(new),
        patches=rows,labels=labels,floor_scope=leaf,regular=regular,late_core=late,owners=owners,
        scope='Source-restored coarse reject for the three fixed authored lifts only when manualV/H bothzero. Active/pending manual helpers retain fullworld scan; native carry/physics/publicPCs unchanged.',
        predecessor_SHA256=W.sha(old),predecessor_proof_SHA256=sha(PROOF),
        bindings=q['bindings']|{p.relative_to(R).as_posix():sha(p) for p in refs})
    (OUT/'floor-proof.json').write_text(json.dumps(result,indent=2)+'\n')
    (OUT/'floor-kernel.bin').write_bytes(kernel)
    print('PASS',regular,flush=True)


if __name__=='__main__':main()
