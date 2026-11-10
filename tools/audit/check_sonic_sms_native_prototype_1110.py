"""Source-only authentic SMS-art/native-host prototype on exact74fde."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import tempfile

import check_sonic_sms_skin_runtime_1110 as Render
import check_remaining_roster_starts_1110 as Current
import check_manual_vertical_platform_1110 as P
import audit_mega_giant_chr_candidates_1110_v1 as Carrier
import compose_remaining_roster_starts_1110 as Roster
from check_tmnt_render_oa import address,location

R,N=Current.R,P.N
SOURCE=R/'tools/reference/sonic_sms_native_frontend_1110.s'
OUT=R/'build/sonic-native-prototype-1110'
NAME_RECIPE=R/'build/mike-alternate-prototypes-1110/linked.json'


def digest(raw):return sha256(raw).hexdigest()


def chr_authority(raw):
    b=Current.W.bundle(raw)
    prior_path=R/'build/mini-mario-owner-1103-v15/carrier-audit-v16.json'
    prior=json.loads(prior_path.read_text());assert prior['passed']
    pages=set(Render.S.PAGES)
    assert not any(pages.intersection(v) for v in prior['exact_finite_domains'].values())
    # Four historical arrays are retired, not current selector data. Rebind
    # the actual source-proven Form0+offset reader below instead of treating
    # stale symbol ranges as live tables merely because they retain a name.
    changed=[];exact=0
    rows={r['name']:r for r in prior['current_table_bindings']}
    for row in prior['current_table_bindings']:
        at,n=row['offset'],row['bytes'];blob=raw[at:at+n]
        if digest(blob)==row['SHA256']:exact+=1;continue
        name=row['name'];assert name in ('M3Form2ChrLo','M3Form3ChrLo','M3Form4ChrLo','M3Form6ChrLo'),name
        assert n==81
        changed.append(name)
    m3_path=R/'build/prince-actor-1101-v1/smb3-pages.json'
    m3=json.loads(m3_path.read_text());constraint=m3['current_source_constraint']
    sites={}
    for key in ('exact_live_caller_bytes','exact_live_helper_bytes'):
        sequence=bytes.fromhex(constraint[key]);assert raw.count(sequence)==1
        sites[key]=raw.index(sequence)
    lows=raw[location(b,'M3ChrLoTableLo'):location(b,'M3ChrLoTableLo')+7]
    highs=raw[location(b,'M3ChrLoTableHi'):location(b,'M3ChrLoTableHi')+7]
    assert [lo+256*hi for lo,hi in zip(lows,highs,strict=True)]==[address(b,'M3Form0ChrLo')]*7
    base=raw[location(b,'M3Form0ChrLo'):location(b,'M3Form0ChrLo')+81]
    offsets=raw[location(b,'MbChrOffsets'):location(b,'MbChrOffsets')+7]
    assert set(base)=={24,25,26,27} and list(offsets)==constraint['form_offsets']
    actual=sorted({512+((v+off)&255) for v in base for off in offsets})
    assert actual==list(range(524,544)) and not pages.intersection(actual)
    for row in prior['inherited_private_writer_chunks_exact']:
        assert any(digest(raw[1048592+p*1024:1048592+(p+1)*1024])==row['SHA256'] for p in row['pages'])
    _,native=Carrier.table(b,'ChrPhysicalMap',256)
    assert not pages.intersection(native)
    assert all(raw[Carrier.prg_at(bank,0xe36):Carrier.prg_at(bank,0xe36)+256]==native
               for bank in Carrier.MAP_BANKS)
    weapon=Carrier.compiled_readers(b)
    assert not pages.intersection(v for row in weapon.values() for v in row['actual_mmc5_outputs'])
    giant=json.loads((R/'build/mega-giant-chr-lease-1110/proof.json').read_text())
    assert giant['passed'] and set(giant['additions']['exact_modified_pages'])==set(range(168,215,2))
    return dict(prior_domains=len(prior['exact_finite_domains']),current_tables_exact=exact,
                retired_changed_SMB3_tables=changed,
                actual_SMB3_reader=dict(sites=sites,pages=actual,all7pointers_Form0=True),
                private_writer_chunks_exact=15,
                native_map_mirrors=list(Carrier.MAP_BANKS),weapons=weapon,
                Giant_pages=list(range(168,215,2)),Sonic_even_pages=sorted(pages),
                odd_neighbors_preserved=True,
                limitations='Uses finite source selector domains and exact current tables/chunks, '
                            'not a claim about arbitrary malformed mapper/header values.')


def front(out,sonic_name):
    areas=(('NAME_GATE',0xac7d,40),('NAME_PACKET',0xacc0,18),('COLORS',0xbaa4,85))
    memory=''.join(f'M{i}:start=${pc:x},size=${n:x},file=%O,fill=yes,fillval=$ea;'
                   for i,(_,pc,n) in enumerate(areas))
    seg=''.join(f'{s}:load=M{i},type=ro;' for i,(s,_,_) in enumerate(areas))
    with tempfile.TemporaryDirectory(dir=out) as tmp:
        cfg=Path(tmp)/'link.cfg';cfg.write_text('MEMORY{'+memory+'}SEGMENTS{'+seg+'}')
        data,labels=P.compile_source(Path(tmp),f'SONIC_NAME_ENTRY=${sonic_name:04x}\n'+SOURCE.read_text(),cfg)
    rows=[];at=0
    for s,pc,n in areas:rows.append((62 if s=='COLORS' else 66,pc,data[at:at+n]));at+=n
    assert at==len(data)
    return rows,labels


def compose(out,sonic_name=None):
    original,_,rows,labels,authority=Render.construct(out)
    parent,roster,_,_,_=Roster.compose()
    assert parent==original
    shared=json.loads(NAME_RECIPE.read_text())
    assert shared['prepared'] and shared['parent_SHA256']==digest(roster)
    for path,wanted in shared['source_bindings'].items():
        assert digest((R/path).read_bytes())==wanted,path
    dependency=P.install(roster,shared['patches'])
    assert digest(dependency)==shared['expected_memory_only_SHA256']
    endpoint=shared['exports']['PrototypeSonicName']
    assert endpoint==0xa358
    if sonic_name is None:sonic_name=endpoint
    assert sonic_name==endpoint
    b=Current.W.bundle(original)
    code,extra=front(out,sonic_name);labels|=extra
    def add(bank,pc,value,role):
        at=P.at(bank,pc)
        rows.append(dict(file_offset=at,old_hex=original[at:at+len(value)].hex(),
                         new_hex=value.hex(),physical_PRG=bank,
                         CPU_half_open=[pc,pc+len(value)],role=role))
    assert original[P.at(66,0xac7d):P.at(66,0xaca5)]==original[P.at(66,0xaca5):P.at(66,0xaca5)+20]*2
    assert original[P.at(62,0xbaa4):P.at(62,0xbaf9)].hex()==(
        '8d6a01a93d8d6c01a9a08d6d01a9ce205a010848ad0260d033ad0a73c905902c'
        'c907b0288a489848ad0a73a000c905f002a003aeae04b9f3ba9dac04b9f4ba9dad04'
        'b9f5ba9dae0468a868aa682860163027163027')
    for bank,pc,blob in code:add(bank,pc,blob,'Sonic named prototype / old native palette parity')
    hint_reads=[]
    for pc,wanted in ((0xac55,0xac91),(0xac5b,0xac7d)):
        at=P.at(66,pc)
        assert original[at:at+3]==b'\xb9'+wanted.to_bytes(2,'little')
        add(66,pc+1,(0xaca5).to_bytes(2,'little'),'Exact two identical hint readers alias canonical DwHint')
        hint_reads.append(pc)
    # 11-entry cycle; leave ADE9..ADEE to the separately coordinated Mike gate.
    for pc,old,value in ((0xadd2,10,11),(0xade7,0,10),(0xade8,234,0)):
        assert original[P.at(124,pc)]==old,(hex(pc),original[P.at(124,pc)])
        add(124,pc,bytes((value,)),'AppendSonic10; preserve all0..9 except intentional9→10')
    # Actual source pose pixels, explicit NES palette/width conversion.
    sms=Render.S.SMS.read_bytes();assert digest(sms)==Render.S.SMS_PIN
    art,records=Render.S.atlas(sms)
    reference=original[1048592+2*1024:1048592+3*1024]
    for i,page in enumerate(Render.S.PAGES):
        at=1048592+page*1024
        assert original[at:at+1024]==reference
        rows.append(dict(file_offset=at,old_hex=reference.hex(),new_hex=art[i*1024:(i+1)*1024].hex(),
                         physical_CHR=page,role='Original SMS pose art, reduced to native16px canvas/3colors'))
    combined=P.install(dependency,rows)
    authority.update(hint_readers=hint_reads,hint_canonical=0xaca5,
                     FmNames_rows_0_1_preserved_live_pending_code=True,
                     Mike_reserved_cycle_tail=[0xade9,0xadee],CHR=chr_authority(original),
                     source_parent_SHA256=digest(original),
                     effective_parent_SHA256=digest(dependency),
                     required_name_recipe=str(NAME_RECIPE.relative_to(R)),
                     required_name_recipe_SHA256=digest(NAME_RECIPE.read_bytes()),
                     required_name_endpoint=dict(physical_PRG=97,PC=endpoint,no_C_borrow=True),
                     shared_name_CPU_pending=shared['CPU_pending'])
    return dependency,combined,rows,labels,authority,art,records


def view(m):
    return (bytes(m[0:0x100]),bytes(m[0x200:0x800]),bytes(m[0x6000:0x8000]),
            tuple(m.rawtags),bytes(m[0x145:0x17b]),bytes(m.ram[2]),bytes(m.ram[3]))


def frontend(before,after):
    pairs=[Current.W.bundle(r) for r in (before,after)]
    count=0;new_row=None
    fields=sorted(n for n,s in pairs[0]['syms'].items() if 'Variant' in n and '::' not in n
                  and not n.startswith('.') and int(s['val'],0)<0x8000)+['FmAlts','FmGroups']
    for slot in range(32):
        models=[Current.I.UI.seed(b,slot) for b in pairs]
        seen=set()
        for cycle in range(33):
            old_name=Current.menu_name(models[0])[0]
            sig=(N.get(models[0],'SelectedCharacter'),old_name,
                 tuple(N.get(models[0],n)for n in fields))
            if sig in seen:break
            seen.add(sig)
            if Current.menu_name(models[1])[0]!=old_name:
                old_cpu=N.NesMPU;old_front=Current.I.F.NesMPU;log=[]
                class Trace(old_cpu):
                    def step(self):
                        target=self.memory[0x16c]|self.memory[0x16d]<<8
                        if (self.pc in (0x15a,0x15d,0x161) and target in
                            (0xa80e,0xb0ab,0xb720,0xbba3)) or (
                            self.memory.rawtags[1] in (191,194) and self.pc in
                            (0xac7d,0xacc0,0xacc6,0xa80e,0xa84a)):
                            log.append([self.pc,self.a,self.x,self.y,self.memory[0x16a],
                                        target,
                                        self.memory[0x162],self.memory.rawtags[1]])
                        return super().step()
                N.NesMPU=Trace
                Current.I.F.NesMPU=Trace
                try:
                    mm=N.fresh(pairs[1]);N.put(mm,CrossoverMenuIndex=slot,CmActive=0);mm[0x5ffe]=0
                    def watch(c):
                        if c.pc in (0x15a,0x15d,0x161,0xacc0,0xac7d,0xacc6,0xa80e,0xa84a):
                            log.append([c.pc,c.a,c.x,c.y,c.memory[0x16a],c.memory[0x16c]|c.memory[0x16d]<<8,
                                        c.memory[0x162],c.memory.rawtags[1]])
                    Current.I.F.invoke(mm,'MenuResolveCharacter',watch=watch)
                    Current.I.F.invoke(mm,'QueueSelection',watch=watch)
                finally:N.NesMPU=old_cpu;Current.I.F.NesMPU=old_front
                print('TRACE',json.dumps(log),flush=True)
            assert Current.menu_name(models[1])[0]==old_name,(slot,cycle,old_name,Current.menu_name(models[1])[0],
                [(N.get(m,'SelectedCharacter'),N.get(m,'MarioVariant'),N.get(m,'CrossoverMenuIndex'),
                  N.get(m,'VRAM_Buffer1_Offset'),list(m[0x16a:0x16e])) for m in models])
            assert N.get(models[0],'SelectedCharacter')==N.get(models[1],'SelectedCharacter')
            assert view(models[0])==view(models[1]),('foreign_complete_menu',slot,cycle,old_name)
            # Public queue selection final outputs are exact for every old entry;
            # hint pointers alone are dead before all actual public continuations.
            for key in (16,128):
                forks=[N.fork(m) for m in models]
                for m in forks:Current.I.UI.key(m,key)
                assert N.get(forks[0],'CrossoverMenuState')==N.get(forks[1],'CrossoverMenuState')
                assert N.get(forks[0],'SelectedCharacter')==N.get(forks[1],'SelectedCharacter')
            count+=1
            for m in models:Current.I.UI.key(m,32)
            if slot==0 and N.get(models[1],'MarioVariant')==10:
                new_row=dict(name=Current.menu_name(models[1])[0],raw=N.get(models[1],'SelectedCharacter'),
                             variant=N.get(models[1],'MarioVariant'))
                assert new_row==dict(name='SONIC',raw=0,variant=10),new_row
                for key in (16,128):
                    m=N.fork(models[1]);Current.I.UI.key(m,key)
                    assert N.get(m,'CrossoverMenuState')==0 and N.get(m,'SelectedCharacter')==0
                Current.I.UI.key(models[1],32)
        else:raise AssertionError(('UnboundedSelect',slot))
    assert count==Current.inventory(before)['select_states'] and new_row
    return dict(legacy_select_profiles=count,legacy_Start_A_cases=count*2,new_Sonic=new_row)


def colors(before,after):
    bundles=[Current.W.bundle(r) for r in (before,after)]
    cases=0
    for owner,var in ((0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(0,8),(0,9),
                      (1,0),(5,0),(16,0),(25,0),(34,0),(39,0),(41,0),(42,0)):
      for tier in (0,1,2):
        scenes=[]
        for b in bundles:
            m=N.fresh(b);N.put(m,SelectedCharacter=owner,MarioVariant=var,PlayerStatus=tier,
                              VRAM_Buffer1_Offset=0,BackgroundColorCtrl=0,AreaType=1)
            z=N.invoke(m,'BmColors',a=91,x=73,y=142,p=0x71)
            scenes.append((m,z))
        a,b=scenes
        assert {k:v for k,v in a[1].items()if k not in ('CPU','minimum_SP','counts')}=={
            k:v for k,v in b[1].items()if k not in ('CPU','minimum_SP','counts')},(owner,var,tier)
        assert view(a[0])==view(b[0]),(owner,var,tier)
        cases+=1
    for tier in (0,1,2):
        m=N.fresh(bundles[1]);N.put(m,SelectedCharacter=0,MarioVariant=10,PlayerStatus=tier,
             VRAM_Buffer1_Offset=0,BackgroundColorCtrl=0,AreaType=1)
        N.invoke(m,'GetPlayerColors')
        end=N.get(m,'VRAM_Buffer1_Offset');base=address(m.bundle,'VRAM_Buffer1')
        assert bytes(m[base+end-3:base+end])==bytes((0x16,0x12,0x30)),(tier,end,list(m[base:base+end]))
    return dict(legacy_colors=cases,Sonic_native_palette_tiers=3)


def body_seed(bundle):
    m=N.fresh(bundle)
    N.put(m,SelectedCharacter=0,MarioVariant=10,OperMode=1,FamilyMainCommit=1,
          DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,NumberofLives=2,
          AreaPointer=0x25,Mirror_PPUCTRL=160)
    N.invoke(m,'InitScreen')
    N.put(m,DisableScreenFlag=0,Mirror_PPUMASK=30,OperMode_Task=3,
          GameEngineSubroutine=8,PlayerStatus=0,PlayerSize=1,Player_X_Position=40,
          Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,PlayerFacingDir=1,
          AreaType=1,AreaParserTaskNum=7,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,
          ScreenRight_X_Pos=255,ScreenRight_PageLoc=0)
    for name in ('Block_Buffer_1','Block_Buffer_2'):
        at=address(bundle,name);m[at:at+208]=bytes(176)+bytes([0x54])*32
    m[address(bundle,'GameTimerDisplay')]=4
    return m


def body(after):
    bundle=Current.W.bundle(after)
    m=body_seed(bundle)
    rows=[]
    phases=(('idle',0,20),('right',65,30),('left',66,30),('jump',128,24),('land',0,60))
    for label,pad,epochs in phases:
        for epoch in range(epochs):
            z=P.frame(m,pad)
            row=dict(phase=label,x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
                     y=N.get(m,'Player_Y_Position'),state=N.get(m,'Player_State'),
                     chr=m.chr_latches[0],mode=N.get(m,'X5ChrMode'),
                     pose=N.get(m,'ObjectMetasprite'),CPU=z['CPU'])
            assert row['mode']==0x85 and row['chr'] in Render.S.PAGES,row
            assert N.get(m,'NumberofLives')==2 and N.get(m,'GameEngineSubroutine')==8,row
            rows.append(row)
    idle=[r for r in rows if r['phase']=='idle'];right=[r for r in rows if r['phase']=='right']
    left=[r for r in rows if r['phase']=='left'];jump=[r for r in rows if r['phase']=='jump']
    assert all(r['x']==40 and r['y']==176 for r in idle)
    assert right[-1]['x']>right[0]['x']+16,(right[0],right[-1])
    assert left[-1]['x']<max(r['x']for r in left)-8,(left[0],left[-1])
    assert min(r['y'] for r in jump)<168 and rows[-1]['state']==0 and rows[-1]['y']==176
    return dict(epochs=len(rows),idle_no_drift=True,right=right[-1],left=left[-1],
                jump_min_y=min(r['y']for r in jump),land=rows[-1],lives=2,
                real_native_CHR_mapping=True,no_new_RAM=True)


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--body-only',action='store_true')
    args=cli.parse_args();assert args.output.resolve()==OUT
    before,after,patches,labels,funding,art,records=compose(args.output)
    palette=colors(before,after);print('COLORS',json.dumps(palette),flush=True)
    if args.body_only:
        trial=body(after)
        (args.output/'body-progress.json').write_text(json.dumps(dict(passed=True,ROM_written=False,
            menu_pending=True,interrupt_pending=True,CPU=trial,palette=palette,
            parent_SHA256=digest(before),expected_memory_only_SHA256=digest(after)),indent=2)+'\n')
        print('BODY',json.dumps(trial));return
    menu=frontend(before,after);print('MENU',json.dumps(menu),flush=True)
    q=dict(passed=True,prototype=True,source_CPU_only=True,ROM_written=False,
        native_pending=True,interrupt_pending=True,parent_SHA256=digest(before),
        expected_memory_only_SHA256=digest(after),patches=patches,labels=labels,
        native_config=dict(menu_slot=0,MarioVariant=10,raw=0,Select_presses=10,
                           menu_name='SONIC',
                           physics='Existing native host Mario',physical_CHR=list(Render.S.PAGES),palette=[22,18,48]),
        CPU=dict(menu=menu,palette=palette),source_funding=funding,
        scope='StartableSonicSMS art prototype with nativehost movement/collision/lifecycle. '
              'OriginalSMS physics, rolling, rings, sound and source-size silhouette are incomplete. '
              'NativeMesen/IRQ/fullstage qualification pending; this is not a completedSMSport.',
        bindings={p.relative_to(R).as_posix():digest(p.read_bytes()) for p in
                  (Path(__file__),Path(Render.__file__),Path(Render.S.__file__),SOURCE,Render.S.SOURCE,
                   Render.S.BASE,Render.S.SMS,R/'src/metasprite.s',R/'src/character_select.s',
                   R/'build/mega-giant-chr-lease-1110/proof.json',
                   R/'build/mike-alternate-prototypes-1110/funding.json',NAME_RECIPE,
                   Path(Roster.__file__))})
    (args.output/'prototype-progress.json').write_text(json.dumps(q,indent=2)+'\n')
    (args.output/'sonic-native.chr').write_bytes(art)
    print(json.dumps(dict(passed=True,expected_memory_only_SHA256=digest(after),patches=len(patches))))


if __name__=='__main__':main()
