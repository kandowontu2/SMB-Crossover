"""Isolated source compaction proof, not an additional native-ROM lease."""
from hashlib import sha256
from itertools import product
import argparse
import json
from pathlib import Path

import check_dkjr_platform_contact_1113 as Q

P,H,N,W,L,T=Q.P,Q.H,Q.N,Q.W,Q.L,Q.T
START,END=0xb963,0xb98e


def parts(raw):
    b=W.Symbols.bundle();b['raw']=raw
    source=(P.B.R/'src/sprite_render.s').read_text()
    body=source.split('.proc RyuPlatformCollisionBridge\n',1)[1].split('.endproc',1)[0]
    overlap=W.address(b,'RyuPlatformSourceOverlap')
    bank=((W.location(b,'RyuPlatformSourceOverlap')-16)//8192)|128
    assert(overlap,bank)==(0xb854,150)
    call=f'  sta $016a\n  lda #${overlap&255:x}\n  sta $016c\n  lda #${overlap>>8:x}\n  sta $016d\n  lda #{bank}\n  jsr $015a\n'
    assert body.count('  farcall RyuPlatformSourceOverlap\n')==1
    body=body.replace('  farcall RyuPlatformSourceOverlap\n',call)
    defs='SelectedCharacter=$6002\nCHARACTER_RYU=10\nEnemy_ID=$17\nProcLPlatCollisions=$9a2c\n'
    old=H.T.assemble(defs+'.segment "BRIDGE"\n'+body,dict(BRIDGE=(START,43)))
    assert old['used']['BRIDGE']==43
    assert raw[16+(START&8191):16+(END&8191)]==old['images']['BRIDGE']
    new=body
    for line,count in(('  php\n',1),('  pha\n',1),('  pla\n',2),('  plp\n',2)):
        assert new.count(line)==count
        new=new.replace(line,'')
    compact=H.T.assemble(defs+'.segment "BRIDGE"\n'+new,dict(BRIDGE=(START,43)))
    assert compact['used']['BRIDGE']==37
    bank0=raw[16:8208]
    assert bank0[0x1483:0x1489]==bytes.fromhex('2063b9a60d60')
    assert bank0.count(bytes.fromhex('2063b9'))==1 and bank0.count(bytes.fromhex('4c63b9'))==0
    assert bytes.fromhex('63b980')not in raw[16:16+1048576]
    external=[];flagged=[];farcall=[]
    for i in range(len(bank0)-2):
        target=bank0[i+1]|bank0[i+2]<<8
        if bank0[i]in(0x20,0x4c)and START<=target<END and not START<=0xa000+i<END:
            external.append((0xa000+i,bank0[i],target))
    for target in range(START,END):
        if bytes((target&255,target>>8,128))in raw[16:16+1048576]:flagged.append(target)
        prefix=bytes((0xa9,target&255,0x8d,0x6c,1,0xa9,target>>8,0x8d,0x6d,1,0xa9,128))
        if prefix in raw[16:16+1048576]:farcall.append(target)
    assert external==[(0xb483,0x20,START)]and flagged==[0xb97c]and not farcall,(external,flagged,farcall)
    # The sole raw tuple is an operand/opcode crossing in live PRG59 code,
    # not a pointer: LDA $7D7A,Y / ORA $7C42,X / STA $7C42,X /
    # LDA $7D80,Y / STA $7C66,X. Preserve this false positive explicitly.
    tuple_at=484603
    assert raw[tuple_at-8:tuple_at+11]==bytes.fromhex('b97a7d1d427c9d427cb9807d9d667cb9867d9d')
    assert raw.count(bytes.fromhex('7cb980'),16,16+1048576)==1
    fixture=bytearray(raw)
    fixture[16+(START&8191):16+(END&8191)]=compact['images']['BRIDGE'].ljust(43,b'\xea')
    return bytes(fixture),dict(old_hex=old['images']['BRIDGE'].hex(),
        new_37_hex=compact['images']['BRIDGE'].hex(),source_original_bytes=43,source_compacted_bytes=37,
        native0_reclaim_half_open=[START+37,END],sole_actual_caller=[0,0xb483],
        same_bank_direct_and_PRG_flagged_tuple_other_entry_targets=0,
        full43B_external_JSR_JMP_targets=external,full43B_standard_farcall_targets=farcall,
        benign_raw_tuple=dict(target=0xb97c,file_offset=tuple_at,physical_PRG=59,
            classified='STA abs,X operand crossing LDA abs,Y opcode/low operand'))


def callback(seed,parent,fixture):
    cases=0;handled=0;allow=0
    for scene,profile,kind,p in product(('ordinary','authored_underside','outside'),(25,27),(37,40),range(256)):
        m=L.clone(seed);slot=3
        N.put(m,SelectedCharacter=10,Player_X_Position=113,Player_PageLoc=0,Player_Y_Position=160,
            Player_Y_HighPos=1,Player_State=1,Player_Y_Speed=252,
            WorldNumber=0,LevelNumber=3 if scene!='ordinary'else 0,AreaType=3,
            SecondaryHardMode=0,GuestHurtTicks=0,RgCrouch=0,RgAttack=0,XgWall=0,RyPlatformSlot=0,
            RyWallSupported=1,RyWallOldHeight=25,RyWallWasGround=1,RyWallOldX=113,
            RyWallOldPage=0,RyWallOldY=192,RyuSourceBodyProfile=profile,
            ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ObjectOffset=slot)
        for field,value in dict(Enemy_ID=kind,Enemy_Flag=1,Enemy_State=0,Enemy_BoundBoxCtrl=5,
            Enemy_X_Position=111 if scene!='outside'else 200,Enemy_PageLoc=0,
            Enemy_Y_Position=184,Enemy_Y_HighPos=1).items():m[W.address(m.bundle,field)+slot]=value
        N.invoke(m,'RelativePlayerPosition',x=0);N.invoke(m,'HuFullBox',x=0)
        N.invoke(m,'GetEnemyOffscreenBits',x=slot);N.invoke(m,'RelativeEnemyPosition',x=slot)
        N.invoke(m,'LargePlatformBoundBox',x=slot)
        outputs=[]
        for raw in(parent,fixture):
            q=Q.mounted(m,raw);q[3]=184
            r=Q.direct(q,START,a=85,x=slot,y=4*(slot+1),p=p)
            assert(r['P']&12)==(p&12),(scene,profile,kind,p,r)
            outputs.append((bytes(q[0x200:0x800]),tuple(bytes(a)for a in q.ram),
                tuple(q.rawtags),r['X'],r['Y'],r['SP']))
        assert outputs[0]==outputs[1],(scene,profile,kind,p)
        handled+=scene=='authored_underside'and kind==40
        allow+=scene=='ordinary'and kind==40;cases+=1
    return dict(cases=cases,all256_incoming_flags_ID_preserved=True,physical_native_and_WRAM_XYSP_equal=True,
        Ryu_underside_fixture_cases=handled,Ryu_ordinary_allowed_fixture_cases=allow,
        A_NZCV_outputs_dead_at_the_proven_LPC_caller=True)


def mains(parent,fixture):
    inventory=Q.Roster.Starts.C.inventory(parent)['rows'];rows=[]
    for name in('RYU HAYABUSA','THOMAS','ZELDA II LINK','MINI MARIO','HULK HOGAN'):
        row=next(r for r in inventory if r['name']==name)
        b=W.Symbols.bundle();b['raw']=parent;_,seed=Q.Roster.cold(b,row)
        models=[Q.mounted(seed,raw)for raw in(parent,fixture)]
        counts=[0,0]
        for m in models:
            for slot in range(6):N.invoke(m,'EraseEnemyObject',x=slot)
            N.put(m,WorldNumber=0,LevelNumber=3,AreaType=3,SecondaryHardMode=0)
            slot=3
            for field,value in dict(Enemy_ID=40,Enemy_Flag=1,Enemy_State=0,Enemy_BoundBoxCtrl=5,
                Enemy_X_Position=N.get(m,'Player_X_Position')-2,Enemy_PageLoc=N.get(m,'Player_PageLoc'),
                Enemy_Y_Position=160 if name=='RYU HAYABUSA'else(N.get(m,'Player_Y_Position')+32)&255,
                Enemy_Y_HighPos=1).items():m[W.address(m.bundle,field)+slot]=value
            N.invoke(m,'InitEnemyObject',x=slot)
            m[W.address(m.bundle,'Enemy_BoundBoxCtrl')+slot]=5
        for age in range(32):
            for i,m in enumerate(models):
                def observe(mem,cpu):
                    if cpu.pc==START and mem.rawtags[1]==128:counts[i]+=1
                Q.frame(m,128 if age<12 else 0,observe)
            a,b=models
            assert a.contact_frame_registers==b.contact_frame_registers,(name,age,'Main return AXYP/SP')
            assert bytes(a[:0x100])==bytes(b[:0x100]),(name,age,'zero page')
            assert bytes(a[0x15a:0x17b])==bytes(b[0x15a:0x17b]),(name,age,'SMC')
            assert bytes(a[0x200:0x800])==bytes(b[0x200:0x800]),(name,age,'native fields')
            assert tuple(bytes(r)for r in a.ram)==tuple(bytes(r)for r in b.ram),(name,age,'WRAM')
            assert tuple(a.rawtags)==tuple(b.rawtags)and bytes(a.vram)==bytes(b.vram)
            assert bytes(a[0x5c00:0x8000])==bytes(b[0x5c00:0x8000]),(name,age,'SRAM')
        assert counts[0]==counts[1]and counts[1]>0,(name,counts)
        rows.append(dict(name=name,complete_Main_updates=32,bridge_calls=counts,
            returned_AXYP_SP_equal=True,all_game_WRAM_SMC_maps_SRAM_VRAM_equal=True))
        print('DKJR_RYU_BRIDGE_MAIN '+json.dumps(rows[-1],separators=(',',':')),flush=True)
    return rows


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--mains-only',action='store_true')
    args=ap.parse_args()
    parent=T.load_parent()
    assert sha256(parent).hexdigest()==T.PARENT
    fixture,info=parts(parent)
    if not args.mains_only:
        b=W.Symbols.bundle();b['raw']=parent
        _,seed=Q.Roster.cold(b,dict(name='RYU HAYABUSA',slot=10,cycle=0,raw=10))
        print('DKJR_RYU_BRIDGE_FUNDING '+json.dumps(dict(info,callback=callback(seed,parent,fixture)),separators=(',',':')),flush=True)
    rows=mains(parent,fixture)
    print('DKJR_RYU_BRIDGE_SCOPE '+json.dumps(dict(passed=True,parent_SHA256=T.PARENT,
        isolated_compaction_fixture_SHA256=sha256(fixture).hexdigest(),Main=rows,
        ROM_written=False,outputs_written=0,allocation_granted=False,
        request='Compact existing native0 B963..B98D source43→37; reserve tail4B B98A..B98D for moved descending ingress B98A..B9B9 and change sole B43F call target. Keep all other bytes exact.',
        scope='Isolated compaction component, no composable ROM candidate or lease amendment yet. Source callbacks and declared actor/scene Main fixtures, not natural stages.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
