"""Zero-output measurement of current native DK helper extents/lifetime."""
from hashlib import sha256
import json

import check_dkjr_head_bridge_1113 as H
import check_dkjr_powerups_current_1113 as B
import compose_dkjr_head_bridge_1113 as T

N,W,L=H.N,H.W,H.L


def draft():
    definitions=dict(EnemyID=0x17,EnemyFlag=0x10,EnemyState=0x1f,WorldNumber=0x764,
        LevelNumber=0x761,SelectedCharacter=0x6002,AreaDataLow=0xd6,EnemyBox=0x646,PlatformCollision=0x566,
        EnemyX=0x76,EnemyPage=0x5d,ScreenLeftX=0x71f,ScreenLeftPage=0x71d,R0=3,
        NativeLargeBBox=0xbe6f,NativeErase=0x8d2f,NativeSmallBBox=0xa1cb,
        FarTarget=0x16c,FarCall=0x15a)
    source=''.join(f'{name}=${value:x}\n'for name,value in definitions.items())
    source+=(B.R/'tools/reference/dkjr_helper_retire_1113.s').read_text()
    return T.assemble(source,dict(RETIRE=(0xb000,160)))


def draft_fixture(seed,**kwargs):
    # Only this isolated CPU fixture substitutes an unallocated native span.
    # This is not a composable candidate or a grant over the existing bytes.
    linked=draft();m=actor(seed,**kwargs);raw=bytearray(m.bundle['raw'])
    at=16+0x1000;image=linked['images']['RETIRE'];raw[at:at+len(image)]=image
    m.bundle=dict(m.bundle,raw=bytes(raw),syms=dict(m.bundle['syms']),segs=dict(m.bundle['segs']))
    m.bundle['segs']['DKRetireFixture']=dict(start=str(0xb000),ooffs=str(at))
    m.bundle['syms']['DkHelperRetireOrBBox']=dict(val=str(0xb000),seg='DKRetireFixture')
    return m


def actor(seed,*,left=560,camera=500,slot=3):
    m=L.clone(seed)
    N.put(m,ObjectOffset=slot,ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8,
        ScreenRight_X_Pos=(camera+255)&255,ScreenRight_PageLoc=(camera+255)>>8,
        AreaType=1,SecondaryHardMode=0,CloudTypeOverride=0,TimerControl=0)
    for name,value in dict(Enemy_Flag=1,Enemy_ID=37,Enemy_PageLoc=left>>8,
        Enemy_X_Position=left&255,Enemy_Y_Position=192,Enemy_Y_HighPos=1).items():
        m[W.address(m.bundle,name)+slot]=value
    N.invoke(m,'InitEnemyObject',x=slot)
    m[W.address(m.bundle,'Enemy_BoundBoxCtrl')+slot]=5
    m[0x47+slot]=128
    return m


def native_extents(seed):
    poses={}
    for size in ('Small','Large'):
        for suffix in ('','Frame2'):
            name='MetaspritePlatformGirder'+size+suffix
            at=W.location(seed.bundle,name);image=seed.bundle['raw'];count=image[at]//4
            records=[tuple(image[at+1+i*4:at+5+i*4])for i in range(count)]
            assert count in(4,6) and all(len(q)==4 for q in records)
            poses[name]=dict(file_offset=at,bytes=image[at:at+1+4*count].hex(),
                sprite_count=count,left=min(q[3]for q in records),right=max(q[3]+7 for q in records))
    selections=[]
    for area in(1,3):
        for hard in(0,1):
            for parity in(0,1):
                m=actor(seed);N.put(m,AreaType=area,SecondaryHardMode=hard,FrameCounter=parity)
                N.invoke(m,'DrawLargePlatform',x=3)
                pose=N.get(m,'EnemyMetasprite',3)
                expected=0x54+parity+(2 if area!=3 and not hard else 0)
                assert pose==expected,(area,hard,parity,pose)
                key='MetaspritePlatformGirder'+('Large'if pose>=0x56 else'Small')+('Frame2'if parity else'')
                selections.append(dict(area=area,hard=hard,frame_parity=parity,pose=pose,
                    visual_left=poses[key]['left'],visual_right=poses[key]['right']))
    m=actor(seed)
    N.invoke(m,'GetEnemyOffscreenBits',x=3);N.invoke(m,'RelativeEnemyPosition',x=3)
    N.invoke(m,'LargePlatformBoundBox',x=3)
    bbox=list(m[0x65c+4*3:0x660+4*3])
    at=W.location(m.bundle,'BoundBoxCtrlData')+5*4
    assert m.bundle['raw'][at:at+4]==bytes((0,0,32,13))
    assert bbox==[60,192,92,205],bbox
    return dict(poses=poses,selections=selections,normal_1_1_visual_width=48,
        normal_1_1_visual_right_inclusive=47,collision_offsets=[0,0,32,13],
        actual_visible_native_bbox=bbox,no_render_width_change=True)


def native_lifetime(seed):
    rows=[]
    for camera in(591,592,593,607,608,609,624,632,633):
        m=actor(seed,camera=camera)
        result=N.invoke(m,'OffscreenBoundsCheck',x=3)
        erased=N.get(m,'Enemy_Flag',3)==0
        assert erased==(camera>=633),(camera,erased)
        rows.append(dict(actor_left=560,camera=camera,erased=erased,
            visual_right_world=607,collision_right_world=592,
            complete_extents_off_left=607<camera and 592<camera,
            native_flag=N.get(m,'PlatformCollisionFlag',3)))
    return dict(rows=rows,native_erase_camera=633,conservative_safe_camera=609,
        next_880_admission_camera=[593,624],native_teardown_entry=hex(W.address(seed.bundle,'EraseEnemyObject')),
        scope='Declared native platform fixtures; no candidate, route or Mesen claim.')


def isolated_predicate(seed):
    rows=0
    for left in(0,240,256,560,3040,65520):
        for delta in(-1,0,31,32,47,48,49,50,72,73):
            camera=left+delta
            if not 0<=camera<=65535:continue
            for slot in range(6):
                m=draft_fixture(seed,left=left,camera=camera,slot=slot)
                N.put(m,WorldNumber=0,LevelNumber=0,AreaDataLow=0xce)
                m[W.address(m.bundle,'PlatformCollisionFlag')+slot]=255
                N.invoke(m,'DkHelperRetireOrBBox',x=slot)
                expected=delta>=49
                assert (N.get(m,'Enemy_Flag',slot)==0)==expected,(left,delta,slot)
                if expected:
                    for name in('Enemy_ID','Enemy_State','FloateyNum_Control','EnemyIntervalTimer',
                        'ShellChainCounter','Enemy_SprAttrib','EnemyFrameTimer','EnemyMetasprite','EnemyVerticalFlip'):
                        assert N.get(m,name,slot)==0,(name,slot)
                rows+=1
    negative=0
    for name,values in dict(SelectedCharacter=(28,39,41),WorldNumber=(1,255),LevelNumber=(1,255),AreaDataLow=(0,0xcf),
        Enemy_Flag=(2,128,255),Enemy_ID=(6,36,38,40,43,44,46),Enemy_State=(1,64,128),
        Enemy_BoundBoxCtrl=(0,4,6),PlatformCollisionFlag=(0,1,5,127)).items():
        for value in values:
            m=draft_fixture(seed,camera=609)
            N.put(m,WorldNumber=0,LevelNumber=0,AreaDataLow=0xce)
            m[W.address(m.bundle,'PlatformCollisionFlag')+3]=255
            index=3 if name.startswith(('Enemy','Platform'))else 0
            m[W.address(m.bundle,name)+index]=value
            prior=N.get(m,'Enemy_Flag',3)
            N.invoke(m,'DkHelperRetireOrBBox',x=3)
            assert N.get(m,'Enemy_Flag',3)==prior,(name,value)
            negative+=1
    return dict(geometry_slot_cases=rows,nonowner_state_passenger_guards=negative,
        measured_service_bytes=draft()['used']['RETIRE'],native_teardown_used=True,
        allocated=False,scope='Unallocated isolated CPU fixture only, no ROM candidate or natural-route proof.')


def fallback_parity(seed):
    linked=T.girder_images()[0];labels=linked['symbols'];rows=0
    dispatch=T.assemble('FarCallStub=$%x\n.segment "WRAP"\nlda #0\nldy #$b0\nclc\njmp FarCallStub\n'%labels['DkNativeFarCall'],
        dict(WRAP=(0xb7ca,17)))['images']['WRAP']
    assert len(dispatch)==8
    for kind in range(36,45):
        for state in(0,1,64,128):
            for slot in range(6):
                results=[]
                for candidate in(False,True):
                    m=draft_fixture(seed,slot=slot)if candidate else actor(seed,slot=slot)
                    for i in range(6):m[W.address(m.bundle,'Enemy_Flag')+i]=0
                    m[W.address(m.bundle,'Enemy_Flag')+slot]=1
                    m[W.address(m.bundle,'Enemy_ID')+slot]=kind
                    m[W.address(m.bundle,'Enemy_State')+slot]=state
                    N.put(m,WorldNumber=0,LevelNumber=0,AreaDataLow=0xce)
                    m.ram[2][0x8fd]=255
                    if candidate:m.ram[3][0x17ca:0x17ca+len(dispatch)]=dispatch
                    c=H.call(m,labels['DkRefreshPlatform'],a=83,x=71,y=109,p=0x61)
                    code=bytearray(m.ram[3]);code[0x17ca:0x17ca+len(dispatch)]=bytes(len(dispatch))
                    results.append(((c.a,c.x,c.y,c.p,c.sp),bytes(m[:0x800]),tuple(m.rawtags),
                        bytes(m.ram[2]),bytes(code)))
                assert results[0]==results[1],(kind,state,slot)
                rows+=1
    return dict(full_refresh_paired_cases=rows,caller_AXYP_SP=True,all_native_fields_and_WRAM_equal=True,
        source_wrapper_bytes=8,existing_prelude_grant=17,constructor_FarCall_entry_unchanged=True,
        allocated=False)


def main():
    raw=B.C.ROM.read_bytes();assert sha256(raw).hexdigest()==B.STEVE_SUCCESSOR
    _,seed=H.cold(raw,B.COOKIE)
    print('DKJR_NATIVE_HELPER_EXTENTS '+json.dumps(native_extents(seed),separators=(',',':')),flush=True)
    print('DKJR_NATIVE_HELPER_LIFETIME '+json.dumps(native_lifetime(seed),separators=(',',':')),flush=True)
    print('DKJR_RETIRE_ISOLATED '+json.dumps(isolated_predicate(seed),separators=(',',':')),flush=True)
    print('DKJR_RETIRE_FALLBACK '+json.dumps(fallback_parity(seed),separators=(',',':')),flush=True)
    for name in ('EnemyData','EnemyDataLow','EnemyDataHigh','AreaData','AreaDataLow'):
        try:
            pc=W.address(seed.bundle,name)
            print('DKJR_LEVEL_POINTER '+json.dumps(dict(name=name,address=pc,bytes=list(seed[pc:pc+2]))),flush=True)
        except KeyError:pass


if __name__=='__main__':main()
