"""Qualify actual compiled Mike/Jay/Steve menu, input, art and death paths."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import inspect

import build_mike_alternate_prototypes_1110 as B
import smb3_asset_relocation_cpu_v4 as Render
from audit_mega_giant_chr_candidates_1110_v1 import compiled_readers, table

R, I, W, OUT = B.R, B.I, B.W, B.OUT


def reconstruct():
    receipt = B.read(OUT/'linked-v3.json')
    assert receipt['prepared'] and receipt['parent_SHA256']==B.PIN
    for name,pin in receipt['source_bindings'].items():
        assert B.digest((R/name).read_bytes())==pin,name
    old = B.source_bundle()
    raw = bytearray(old['raw'])
    for row in receipt['patches']:
        at = row['file_offset']
        before,after = (bytes.fromhex(row[key]) for key in ('old_hex','new_hex'))
        assert raw[at:at+len(before)]==before
        raw[at:at+len(after)] = after
    assert B.digest(raw)==receipt['expected_memory_only_SHA256']
    new = deepcopy(old)
    new['raw'] = bytes(raw)
    new['syms']['PrototypeVariant']={'val':'0x730b'}
    for name,pc in receipt['labels'].items():
        if name in new['syms']:
            new['syms'][name]['val']=hex(pc)
    return old,new,receipt


def menus(old,new):
    before = B.Menu.inventory(old['raw'])
    after = B.Menu.inventory(new['raw'])
    assert before['distinct_named_entries']==before['confirmable_named_entries']==97
    assert after['distinct_named_entries']==after['confirmable_named_entries']==99, (
        after['distinct_named_entries'],after['confirmable_named_entries'],
        [r for r in after['rows'] if r['slot']==15])
    old_rows = [r for r in before['rows'] if r['slot']!=15]
    new_rows = [r for r in after['rows'] if r['slot']!=15]
    assert old_rows==new_rows
    mike = [r for r in after['rows'] if r['slot']==15]
    assert [r['name'] for r in mike]==['MIKE JONES','JAY MCCRAY','STEVE HERMANN']
    assert all(r['raw']==16 for r in mike)
    cycles=0
    for low in range(32):
        model = I.UI.seed(new,15)
        I.N.put(model,PrototypeVariant=low)
        for value in (0x20,0x40,0):
            I.UI.key(model,32)
            assert I.N.get(model,'PrototypeVariant')&0x60==value,(low,value,I.N.get(model,'PrototypeVariant'))
            cycles+=1
    for slot in (28,30):
        for value in (0x20,0x40):
            model = I.UI.seed(new,slot)
            I.N.put(model,PrototypeVariant=value)
            for _ in range(6 if slot==28 else 4):
                I.UI.key(model,32)
                assert I.N.get(model,'PrototypeVariant')&0x60==value
                cycles+=1
    return dict(passed=True,profiles=99,all_Start_A_confirmations=True,
                unchanged_foreign_profiles=len(old_rows),selector_edges=cycles,
                Mike_family=mike,missing=after['requested'])


def continue_domains(old,new):
    # Execute the older complete routines with all original low-bit values.
    # Their fields and results must match the old byte with only60 removed.
    cases=0
    for owner,entry,slot in (('fresh','PrototypeFreshPredicate',15),('DK','DkHostResolve',27),
                              ('Ar','ArHostSelect',31),('Hu','HuResolve',27)):
        bundles=[deepcopy(old),deepcopy(new)]
        if owner=='fresh':
            for bundle in bundles:
                bundle['syms'][entry]=dict(bundle['syms']['CrossoverMenuInput'],val=hex(0xa82a))
        for native in list(range(32))+list(range(128,160)):
            for choice in (0x20,0x40):
                runs=[]
                for index,bundle in enumerate(bundles):
                    model=I.UI.seed(bundle,slot)
                    I.N.put(model,CrossoverContinue=native|(choice if index else 0),
                            JnHealth=2,JnMaxHearts=9,JnOwnedTier=3)
                    if owner in ('DK','Hu'):
                        I.N.put(model,DkTier=2,DkReady=0x44)
                    if owner=='Ar':
                        # This original leaf executes in its real C63 window;
                        # FarCallCommon still uses the normal A-bank transport.
                        model[0x5116]=0xbf
                        I.N.put(model,CurrentBankC=0xbf)
                    result=I.F.invoke(model,entry,a=32 if owner=='Ar' else 85,p=0x71)
                    ram=bytearray(model[0x5c00:0x8000])
                    ram[0x730b-0x5c00]&=0x9f
                    records=[]
                    for name,hi,count in (('SmPosePtr',B.address(bundle,'SmPosePtr')+1,1),
                                          ('HpNativeDrawLo',B.address(bundle,'HpNativeDrawHi'),7)):
                        for i in range(count):
                            at=B.address(bundle,name)+i-0x5c00
                            top=hi+i-0x5c00
                            pointer=ram[at]+256*ram[top]
                            if 0xc000<=pointer<0xc409:
                                source=B.off(97,pointer)
                                records.append((name,i,bundle['raw'][source:source+bundle['raw'][source]+1].hex()))
                                ram[at]=ram[top]=0
                    # Fresh's native return ORs Start into the packed field.
                    # ChkContinue subsequently consumes onlybit7 via ASL.
                    regs=(result['A']&(0x9f if owner=='fresh' else 255),result['X'],result['Y'],result['P'])
                    runs.append((regs,bytes(ram),records))
                assert runs[0]==runs[1],('Continue domain',owner,native,choice,
                    runs[0][0],runs[1][0],[(i,a,b)for i,(a,b)in enumerate(zip(runs[0][1],runs[1][1]))if a!=b][:15])
                cases+=1
    simultaneous=[]
    for before in (1,2):
        for confirm in (16,128):
            model=I.UI.seed(new,15)
            for _ in range(before):I.UI.key(model,32)
            I.N.put(model,JnHealth=2,JnMaxHearts=9,JnOwnedTier=3)
            I.UI.key(model,32|confirm)
            expected=(before+1)%3
            assert I.N.get(model,'CrossoverMenuState')==0
            assert I.N.get(model,'CrossoverContinue')&0x60==expected*32
            assert I.N.get(model,'JnMaxHearts')==0,(before,confirm,expected,
                I.N.get(model,'JnMaxHearts'),I.N.get(model,'JnHealth'))
            simultaneous.append(dict(previous_choice=before,buttons=32|confirm,started_choice=expected))
    return dict(passed=True,actual_routine_comparisons=cases,
                original_low_bits_preserved=list(range(32)),continue_modes=[0,128],
                prototype_bits=[32,64],simultaneous_Select_confirm=simultaneous)


def record_identity(old,new,labels):
    count=0
    for name,pc in labels.items():
        if name not in old['syms'] or not (name.startswith('JnPose') or name.startswith('JnShot')
                or name.startswith('JnItem') or name.startswith('JnBatNative')
                or name in ('JnHeart','JnStar','JnBigHeart')):
            continue
        if name.endswith(('Lo','Hi')):
            continue
        at = B.location(old,name)
        blob = old['raw'][at:at+old['raw'][at]+1]
        assert new['raw'][B.off(97,pc):B.off(97,pc)+len(blob)]==blob,name
        count+=1
    assert count==93
    return dict(passed=True,original_Mike_records_exact=count)


def canonical_render(bundle,cpu,model):
    raw = bytearray(model[:0x8000])
    # Canonicalize only genuine source record pointers. Aliased identical
    # records have the same full bytes, regardless of their physical offset.
    keys=[]
    for name in ('R0','SmPosePtr'):
        at = B.address(bundle,name)
        value = raw[at]+256*raw[at+1]
        if 0xc000<=value<0xc409:
            source = B.off(97,value)
            blob = bundle['raw'][source:source+bundle['raw'][source]+1]
            keys.append((name,blob.hex()))
            raw[at:at+2]=bytes(2)
    ordinary = bytes(raw[:0x100]+raw[0x200:])
    return (cpu.a,cpu.x,cpu.y,cpu.p&0xcf,cpu.sp,ordinary,keys,
            bytes(model[0x200:0x300]),tuple(model.banks))


def render_parity(old,new):
    cases=0
    for pose in range(7):
        for face in (1,2):
            cfg=dict(owner='mike',entry='JnSetPose',pose=pose,face=face,flags=0x31)
            runs = [Render.execute(bundle,cfg) for bundle in (old,new)]
            states=[canonical_render(bundle,cpu,model) for bundle,(cpu,model,_,_) in zip((old,new),runs)]
            assert states[0]==states[1],('Mike pose parity',pose,face,
                states[0][:5],states[1][:5],states[0][6:],states[1][6:],
                [(i,a,b)for i,(a,b)in enumerate(zip(states[0][5],states[1][5]))if a!=b][:20])
            cases+=1
    for kind in range(1,14):
        ages = range(1,31) if kind==4 else (0,4)
        for face in (1,2):
            for age in ages:
                cfg=dict(owner='mike',entry='JnDraw',shots=[(0,kind)],face=face,age=age,
                         vx=255 if face==2 else 1,x=128,y=160,offset=0,rotation=0,flags=0x31)
                runs = [Render.execute(bundle,cfg) for bundle in (old,new)]
                states=[canonical_render(bundle,cpu,model) for bundle,(cpu,model,_,_) in zip((old,new),runs)]
                assert states[0]==states[1],('Mike original shot parity',kind,face,age)
                cases+=1
    return dict(passed=True,actual_original_Mike_render_calls=cases,
                registers_RAM_original_records_OAM_exact=True,
                pointer_normalization='Only R0/SmPosePtr source records use complete-record identity; discarded stack omitted.')


def put_controls(model,keys):
    I.N.put(model,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,
            A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=keys&12,NmiDisable=255)


def startup(bundle,variant,confirm):
    previous = I.N.Bus
    I.N.Bus = I.C.C.C.C.V.ControllerBus
    try:
        model = I.UI.seed(bundle,15)
        for _ in range(variant):
            I.UI.key(model,32)
        name = B.Menu.menu_name(model)[0]
        # A real fresh game must discard old progression, rather than pass
        # only because this fixture happened to begin with an empty profile.
        I.N.put(model,JnHealth=2,JnMaxHearts=9,JnOwnedTier=3)
        started = I.UI.key(model,confirm)
        assert I.N.get(model,'SelectedCharacter')==16 and I.N.get(model,'CrossoverMenuState')==0
        I.F.invoke(model,'ChkContinue',a=started['A'],x=started['X'],y=started['Y'],p=started['P'])
        I.N.invoke(model,'PauseRoutine',a=0)
    finally:
        I.N.Bus = previous
    def frame(keys=0):
        put_controls(model,keys)
        B.Current.invoke_game(model,'GameLoop')
        I.N.consume(model)
        B.Current.Cold.clear(model)
    for entrance in range(600):
        if (I.N.get(model,'OperMode_Task'),I.N.get(model,'GameEngineSubroutine'))==(3,8):
            break
        frame()
    else:
        raise AssertionError('Prototype entrance bound')
    assert (I.N.get(model,'JnMaxHearts'),I.N.get(model,'JnHealth'))==(3,6),(name,
        I.N.get(model,'JnMaxHearts'),I.N.get(model,'JnHealth'))
    xs=[];ys=[];pages=[]
    for epoch in range(150):
        keys = 0 if epoch<24 else 1 if epoch<84 else 129 if epoch<102 else 1 if epoch<138 else 0
        frame(keys)
        assert I.N.get(model,'GameEngineSubroutine')==8 and I.N.get(model,'NumberofLives')==2
        assert I.N.get(model,'PrototypeVariant')&0x60==variant*32
        xs.append(I.N.get(model,'Player_X_Position')+256*I.N.get(model,'Player_PageLoc'))
        ys.append(I.N.get(model,'Player_Y_Position'))
        pages.append(I.N.get(model,'SmChrBank'))
    assert xs[137]>xs[23]+16 and min(ys[84:])<ys[23]-3,(name,xs[-1],min(ys))
    expected_page=(708,216,220)[variant]
    assert set(pages)=={expected_page&255},(name,set(pages))
    # A legal active-stage native death ingress; no life/callback implementation
    # is stubbed. Terrain/enemy reachability is left to root's native replay.
    I.F.invoke(model,'KillPlayer')
    death_engine=I.N.get(model,'GameEngineSubroutine')
    for death_age in range(650):
        frame()
        if I.N.get(model,'NumberofLives')==1 and (I.N.get(model,'OperMode_Task'),I.N.get(model,'GameEngineSubroutine'))==(3,8):
            break
    else:
        raise AssertionError(('Prototype death/respawn bound',name,I.N.get(model,'NumberofLives'),I.N.get(model,'GameEngineSubroutine')))
    assert I.N.get(model,'PrototypeVariant')&0x60==variant*32
    for _ in range(16):
        frame(1)
    assert I.N.get(model,'JnHealth')>0 and I.N.get(model,'JnReady')==0x4a
    return dict(passed=True,name=name,variant=variant,confirm=confirm,entrance_updates=entrance,
                ordinary_updates=150,x_before=xs[23],x_after=xs[137],ground_y=ys[23],minimum_y=min(ys),
                body_page=expected_page,death_ingress='Native KillPlayer on active stage; fixture-only',
                first_death_engine=death_engine,death_respawn_updates=death_age+1,respawn_lives=1,
                selected_skin_retained=True,post_respawn_right_updates=16)


def chr_lease(old,new):
    pages={216,220}
    # Reuse the independently authored finite-source checker without editing
    # its Sonic-bound module or original four-page reservation.
    import check_sonic_sms_native_prototype_1110 as SonicLease
    source=inspect.getsource(SonicLease.chr_authority)
    assert source.count('pages=set(Render.S.PAGES)')==1
    namespace=dict(vars(SonicLease))
    exec(compile(source.replace('pages=set(Render.S.PAGES)','pages={216,220}'),
                 str(Path(__file__)),'exec'),namespace)
    authority=namespace['chr_authority'](old['raw'])
    changed={p for p in range(1024) if old['raw'][1048592+p*1024:1048592+(p+1)*1024]!=new['raw'][1048592+p*1024:1048592+(p+1)*1024]}
    assert changed==pages
    assert all(old['raw'][1048592+(p+1)*1024:1048592+(p+2)*1024]==new['raw'][1048592+(p+1)*1024:1048592+(p+2)*1024] for p in pages)
    return dict(passed=True,physical_1KB_pages=sorted(pages),odd_neighbors_exact=True,
                source_authority=authority,
                scope='Finite compiled-selector/table inheritance on exact d133. Root native publication/frame verification remains required.')


def main():
    old,new,linked=reconstruct()
    results={}
    results['continue_domains']=continue_domains(old,new)
    print('Original Continue low-bit domains and simultaneous Select/confirm passed',flush=True)
    results['menus']=menus(old,new)
    print('All99 menu identities and group ownership passed',flush=True)
    results['records']=record_identity(old,new,linked['labels'])
    results['render']=render_parity(old,new)
    print('Original Mike actual art/shot rendering passed',flush=True)
    results['startup']=[startup(new,variant,confirm) for variant in (0,1,2) for confirm in (16,128)]
    print('Six actual CPU startup/input/death/respawn paths passed',flush=True)
    results['CHR']=chr_lease(old,new)
    proof=linked|dict(passed=True,CPU_pending=False,native_pending=True,CPU=results,
                      source_bindings=linked['source_bindings']|{
                          path.relative_to(R).as_posix():B.digest(path.read_bytes()) for path in
                          (Path(__file__),R/'tools/audit/check_sonic_sms_native_prototype_1110.py',
                           R/'build/prince-actor-1101-v1/smb3-pages.json',
                           R/'build/mega-giant-chr-lease-1110/proof.json',
                           R/'build/mini-mario-owner-1103-v15/carrier-audit-v16.json')})
    (OUT/'proof-v3.json').write_text(json.dumps(proof,indent=2)+'\n')
    print('CPU PASS',proof['expected_memory_only_SHA256'],flush=True)


if __name__=='__main__':
    main()
