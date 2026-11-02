"""Real cached contact and native defeat; reproduce crouch miss and seam controls."""
import collections,json
import prepare_shinobi_contact_visible_1101_v23 as P
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
def main():
 b=scoped_load(P.O/'candidate.nes');lab=P.S.labels(P.O/'combat.lbl');rows=[]
 raw=b['raw'];pages=P.PAGES
 kernel=b''.join(raw[16+1048576+p*1024:16+1048576+(p+1)*1024]for p in pages)
 meta=b''.join(raw[16+1048576+p*1024:16+1048576+(p+1)*1024]for p in [516,517])
 cases=[dict(name='trace-crouch',sx=189,sy=196,ex=187,ey=184,hit=True),
 dict(name='standing-above',sx=189,sy=182,ex=187,ey=184,hit=False),
 dict(name='left-seam',sx=2,sy=196,ex=-8,ey=184,hit=True),
 dict(name='right-seam',sx=250,sy=196,ex=248,ey=184,hit=True),
 dict(name='koopa-visible',sx=189,sy=196,ex=187,ey=184,kind=0,hit=True),
 dict(name='red-koopa-visible',sx=189,sy=196,ex=187,ey=184,kind=1,hit=True),
 dict(name='miss-then-hit',sx=189,sy=196,ex=187,ey=184,decoy=True,hit=True),
 dict(name='horizontal-miss',sx=189,sy=196,ex=210,ey=184,hit=False),
 dict(name='wrong-world-page',sx=189,sy=196,ex=187+256,ey=184,hit=False),
 dict(name='vertical-miss',sx=189,sy=196,ex=187,ey=160,hit=False),
 dict(name='bottom-wrap',sx=189,sy=8,ex=187,ey=240,hit=False),
 dict(name='wrong-Y-page',sx=189,sy=196,ex=187,ey=184,yhigh=2,hit=False),
 dict(name='phase',sx=189,sy=196,ex=187,ey=184,phase=0,hit=False),
 dict(name='dead',sx=189,sy=196,ex=187,ey=184,state=32,hit=False),
 dict(name='squashed',sx=189,sy=196,ex=187,ey=184,state=2,hit=False),
 dict(name='duplicate',sx=189,sy=196,ex=187,ey=184,flag=128,hit=False),
 dict(name='platform',sx=189,sy=196,ex=187,ey=184,kind=0x25,hit=False),
 dict(name='firebar',sx=189,sy=196,ex=187,ey=184,kind=0x24,hit=False),
 dict(name='item',sx=189,sy=196,ex=187,ey=184,kind=0x2e,hit=False),
 dict(name='undefined-pose',sx=189,sy=196,ex=187,ey=184,pose=0x57,hit=False)]
 for case in cases:
  for camera in [256,506,768]:
   for victim in [0,5]:
    m=M.Bus(b);m.ram[3][:len(kernel)]=kernel;m.ram[2][0x1000:0x1800]=meta;m.raw_page(1,3);m.raw_page(2,2)
    M.put(m,CurrentBank=3,CurrentBankC=2,SelectedCharacter=36,ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8,ScreenRight_X_Pos=(camera+255)&255,ScreenRight_PageLoc=(camera+255)>>8,ObjectOffset=3,PlayerFacingDir=1,Player_Y_HighPos=1,OperMode=1,GameEngineSubroutine=8,AreaType=1)
    world=camera+case['ex']
    for n,v in dict(Enemy_Flag=case.get('flag',1),Enemy_ID=case.get('kind',6),Enemy_State=case.get('state',0),Enemy_X_Position=world&255,Enemy_PageLoc=world>>8,Enemy_Y_Position=case['ey'],Enemy_Y_HighPos=case.get('yhigh',1),Enemy_BoundBoxCtrl=9).items():m[address(b,n)+victim]=v
    if case.get('decoy')and victim==0:
     for n,v in dict(Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_X_Position=(camera+220)&255,Enemy_PageLoc=(camera+220)>>8,Enemy_Y_Position=184,Enemy_Y_HighPos=1).items():m[address(b,n)+5]=v
    for at,v in {0xc301:case.get('pose',9),0xc30c:0,0xc364:0,0xc37a:case['sx'],0xc385:0,0xc390:case['sy'],0xc39b:0,0xc554:0,0xc553:case.get('phase',1)}.items():m[at]=v
    fire=address(b,'BoundingBox_UL_Corner')+28;m[fire:fire+8]=[17,23,31,47,55,61,75,81];saved=bytes(m[fire:fire+8]);oam=bytes(m[0x200:0x300]);enemy_box=bytes(m[address(b,'BoundingBox_UL_Corner'):fire])
    shot=bytes(m[0xc300:0xc420]);events=collections.Counter();c=NesMPU(memory=m,pc=lab['ShNativeShotContact']);c.x=1;c.sp=239;c.stPushWord(0x5aff)
    for step in range(100000):
     if c.pc==0x5b00:break
     for n in ['HandleEnemyFBallCol','SprObjectCollisionCore','SetupFloateyNumber']:
      if c.pc==address(b,n)and(m.rawtags[(c.pc-0x8000)//8192]&127)==((location(b,n)-16)//8192):events[n]+=1
     assert m[c.pc],('BRK',case['name'],hex(c.pc));c.step()
    else:raise AssertionError('Step cap')
    assert bool(c.a)==case['hit'],(case,camera,victim,c.a,dict(events))
    assert c.sp==239 and c.x==1 and M.get(m,'ObjectOffset')==3
    assert bytes(m[fire:fire+8])==saved and bytes(m[0x200:0x300])==oam
    assert bytes(m[address(b,'BoundingBox_UL_Corner'):fire])==enemy_box,'Native enemy/body boxes changed'
    assert bytes(m[0xc300:0xc420])==shot,'Source shot motion/state changed'
    assert m.rawtags[1:3]==[3,2]and[M.get(m,n)for n in ['CurrentBank','CurrentBankC']]==[3,2]
    if case['hit']:assert events['HandleEnemyFBallCol']==1 and M.get(m,'Enemy_State',victim)&32 and M.get(m,'FloateyNum_Control',victim)
    else:assert events['HandleEnemyFBallCol']==0
    rows.append(dict(case=case['name'],camera=camera,slot=victim,hit=bool(c.a),cycles=c.processorCycles,score=M.get(m,'FloateyNum_Control',victim),sfx=M.get(m,'Square1SoundQueue'),events=dict(events)))
 q=dict(passed=True,cases=len(rows),ROM_sha256=P.S.sha(P.O/'candidate.nes'),rows=rows,scope='Actual cached source bbox/contact and native score/defeat. Explicit fixture coordinates; no Mesen/Main/ISR/full-route claim. Source projectile state, both borrowed boxes, all native enemy/player boxes, native OAM, mapper and caller index preserved. Miss-then-hit verifies recomputed world scratch.')
 (P.O/'contact-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='rows'}))
if __name__=='__main__':main()
