"""Donor differential and actual native item-consumer CPU boundary evidence."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from recover_karnov_actor_1101_v1 import ROM,EXPECTED
from check_karnov_actor_1101_v1 import Memory
from verify_native_relocation import NesMPU
import battletoads_current_loader_controls_v1 as L
import ff_wram_host_controls_v7 as H
from check_tmnt_render_oa import address
O=R/'build/karnov-pickup-component-1101-v2';BASE=R/'build/karnov-host-resource-base-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    q=dict(passed=False,source_CPU=True,native_boundary_CPU=True,native_emulator=False,installed=False,host_modified=False,component_overlay_only=True)
    try:
        a=json.loads((O/'assembly.json').read_text())
        for p,h in a['bindings'].items():assert sha(p)==h,p
        assert sha(ROM)==EXPECTED
        labels=a['labels'];thinlabels=a['thin_labels'];splitlabels=a['split_labels'];blob=(O/'component.bin').read_bytes();thinblob=(O/'component-thin.bin').read_bytes();splitblob=(O/'component-split.bin').read_bytes();origin=a['origin'];raw=ROM.read_bytes()
        labs={1:labels,2:thinlabels,3:splitlabels}
        donor=Memory();donor[0xc000:]=raw[16+14*8192:16+16*8192];donor[0xa000:0xc000]=raw[16+11*8192:16+12*8192]
        initial=bytes((i*17+13)&255 for i in range(2048))
        for i in [0x70f,0x710,0x65,0x68,0x5f,0xba,0xbb,0xbc,0xbd,0xbe,0xbf,0x40b]:
            donor[i]=0
        donor[:2048]=initial
        def make(port,values):
            m=Memory()
            if port:
                m[:256]=bytes((i*37+19)&255 for i in range(256));m[0xc000:0xc800]=initial
                if port==3:
                    for z in a['split_placement']:m[z['origin']:z['origin']+z['bytes']]=splitblob[z['file_offset']:z['file_offset']+z['bytes']]
                elif port==2:m[origin:origin+len(thinblob)]=thinblob
                else:m[origin:origin+len(blob)]=blob
            else:m[:]=donor
            for n,v in values.items():m[(0xc000 if port else 0)+n]=v
            m.writes=[];return m
        cases=0;normalizations=0;digest=hashlib.sha256();lowest=224;counts={}
        xops={'LDX','TAX','TSX','INX','DEX'}
        def run(m,port,pc,av,flags=0x71,stop=None,xv=7,yv=91):
            nonlocal lowest
            lab=labs.get(port,labels)
            c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=av,xv,yv,flags,224;c.stPushWord(0x5ffe);events=[];lastx=None;zp=bytes(m[:256]);low=c.sp
            for tick in range(2000):
                if c.pc==0x5fff:break
                if not port and c.pc==stop:
                    c.pc=(c.stPopWord()+1)&65535;continue
                if c.pc==(lab['KrPickupSourceSound']if port else 0xc81d):
                    lx=(lab['KrPickupDispatch']+11 if port else 0xc83c)
                    events.append((c.a,'relocated-dispatch-low'if lastx==lx else c.x,c.y))
                    if not port:c.pc=(c.stPopWord()+1)&65535;continue
                mn,_=c.disassemble[m[c.pc]]
                if mn in xops:lastx=c.pc
                assert m[c.pc]!=0,('BRK',port,hex(c.pc));low=min(low,c.sp);c.step()
            else:raise AssertionError(('Leaf timeout',port,hex(c.pc)))
            assert c.sp==224
            lowest=min(lowest,low)
            if port:
                assert bytes(m[:256])==zp,'Foreground/global ZP was not restored'
                assert not any(i<3 for i in m.writes),'Native NMI scratch0..2 touched'
                assert all(0xc000<=i<0xc865 or 0x100<=i<0x200 or i in [3,4]for i in m.writes),('foreign write',m.writes)
            return c,events,lastx,low
        def pair(name,opc,npc,av,values,flags=0x71,stop=None,xv=7,yv=91):
            nonlocal cases,normalizations
            old=make(0,values);oc,oe,ox,_=run(old,0,opc,av,flags,stop,xv,yv)
            for port,lab in labs.items():
                if name=='option_HUD_bookkeeping'and port!=1:continue
                new=make(port,values);nc,ne,nx,_=run(new,port,lab[npc],av,flags,None,xv,yv)
                assert oe==ne,(name,av,port,'events',oe,ne)
                assert(oc.a,oc.y,oc.p&0xcf)==(nc.a,nc.y,nc.p&0xcf),(name,av,port,'AYP',oc.a,nc.a,oc.y,nc.y,oc.p,nc.p)
                if oc.x!=nc.x:
                    assert ox==0xc83c and nx==lab['KrPickupDispatch']+11,(name,av,port,'X provenance',oc.x,nc.x,ox,nx)
                    assert old[0x58]==oc.x
                    normalizations+=1
                skip=set(range(0x100,0x200))|{0x58,0x59,0x7fe,0x7ff}
                if port!=1:
                    # Exact old-C534 private HUD boundary: six queue bytes,
                    # two source tile rows of20bytes; all earned state stays.
                    skip|=set(range(0xb4,0xba))|set(range(0x58f,0x5a3))|set(range(0x5af,0x5c3))
                delta=[i for i in range(2048)if i not in skip and old[i]!=new[0xc000+i]]
                assert not delta,(name,av,port,'RAM',[(hex(i),old[i],new[0xc000+i])for i in delta[:10]])
                digest.update(bytes(new[0xc034:0xc096])+bytes(new[0xc0ba:0xc0c0]));digest.update(repr(ne).encode())
            cases+=1;counts[name]=counts.get(name,0)+1
        # Both health polarities, every unrelated health bit, all source shot
        # encodings, active special flags, ring limits and incoming NES flags.
        for health,weapon,flags in itertools.product(range(256),[0,1,2,3,4,8,12,0x10,0x20,0x40,0x80,0x82],[0x30,0xf9]):
            pair('SuperFireball',0xad79,'KrPickupSuperFireball',85,{0x68:health,0x65:weapon,0x69:37,0x70f:0,0x710:7},flags,0xadb1)
        for value,flags in itertools.product(range(256),[0x30,0xf9]):
            pair('BCD_increment',0xcf7e,'KrPickupOriginal_CF7E',value,{},flags)
        for item,mode in itertools.product(range(10),[0,255]):
            pair('option_HUD_bookkeeping',0xc534,'KrPickupOriginal_C534',item,{0xa1:0xe0,0xa2:0x20},xv=mode)
        for item,lo,hi in itertools.product(range(10),[0,85,255],[0,170,255]):
            pair('earned_option_bit',0xc847,'KrPickupOriginal_C847',item,{0x8f:lo,0x90:hi},xv=0,yv=0x8f)
        validBCD=[(n//10)*16+n%10 for n in range(100)]
        for item,stock,ring,flags in itertools.product(range(10),validBCD,[0,8],[0x30,0xf9]):
            pair('full_option_grant',0xef61,'KrPickupGrantOption',item,{0xbb:stock,0xbc:stock,0xbd:stock,0xbe:stock,0xbf:stock,0xba:0x49,0x40b:stock,0x70f:ring,0x710:7,0x8f:0,0x90:0,0x5f:0},flags)
        # K marks have their own50-count BCD conversion, including native
        # extra-life request even when the private source life ledger is99.
        for marks,life in itertools.product(validBCD[:50],[0,9,0x19,0x99]):
            pair('Kmark_life',0xef61,'KrPickupGrantOption',9,{0xba:marks,0x40b:life,0x70f:0,0x710:0,0x8f:0,0x90:0})
        labels=thinlabels;blob=thinblob
        b=H.C.qualified(BASE/'candidate.nes');seed=L.make(b,SelectedCharacter=34,FmAlts=1,CurrentPlayer=0)
        c,_=L.call(seed,'KrLoad');assert c.p&1
        c,_=L.call(seed,'KrServiceVeneers',slot=15);assert c.p&1
        # Deliberate component preload, retaining original resident/cookies.
        # It is NOT a new authenticated image or a native emulator admission.
        seed.ram[3][origin-0xa000:origin-0xa000+len(blob)]=blob
        for row,name in [(20,'KrPickupPrepare'),(23,'KrPickupMature'),(24,'KrPickupCollect')]:
            pc=labels[name];seed.ram[3][row*3:row*3+3]=bytes([0x4c,pc&255,pc>>8])
        def obj(m,slot,kind=0,state=0x80):
            H.put(m,ObjectOffset=slot,VRAM_Buffer1_Offset=0,Square2SoundQueue=0,PlayerStatus=0,StarInvincibleTimer=0)
            for n,v in [('Enemy_Flag',1),('Enemy_ID',0x2e),('Enemy_State',state),('PowerUpType',kind),('Enemy_Y_Position',160),('Enemy_X_Position',173)]:m[address(b,n)+slot]=v
            H.put(m,ScreenLeft_X_Pos=21)
        native=[];nativelow=224
        for kind,state,slot in itertools.product(range(4),[0,1,17,0x7f,0x80],[0,5]):
            m=L.fork(seed);obj(m,slot,kind,state);before=bytes(m.ram[2][:2048]);zp=bytes(m[3:11])
            c,low=L.call(m,'NrPrepare',x=slot);nativelow=min(nativelow,low)
            assert bytes(m.ram[2][:2048])==before,'Block hit granted upgrade before contact'
            assert m[address(b,'InvPickupOwner')+slot]==34 and m[address(b,'InvPickup')+slot]==0xfc
            c,low=L.call(m,'NrPickupCollision',x=slot);nativelow=min(nativelow,low)
            assert bool(c.p&1)==bool(kind>=2 or state>=128),(kind,state,slot,c.p)
            assert bytes(m[3:11])==zp
            native.append([kind,state,slot,int(bool(c.p&1))])
        spawn=[]
        for health,weapon,saved,kind in itertools.product([0,0x80],[0,1,2,8,12],[0,1,2],[0,2,3]):
            m=L.fork(seed);obj(m,5,kind);m.ram[2][0x68]=health|saved;m.ram[2][0x65]=weapon
            before=bytes(m.ram[2][:2048]);zp=bytes(m[3:11]);c,low=L.call(m,'UnionPwrUpCore',x=5);nativelow=min(nativelow,low)
            base=saved if weapon&12 else weapon&3
            expected=kind if kind>=2 else int(not health and bool(base))
            assert m[address(b,'PowerUpType')+5]==expected,(health,weapon,saved,kind,expected,m[address(b,'PowerUpType')+5])
            assert bytes(m.ram[2][:2048])==before and bytes(m[3:11])==zp,'Spawn consumed earned state'
            assert m[address(b,'Enemy_Flag')+5]==1 and m[address(b,'Enemy_State')+5]==1
            spawn.append([health,weapon,saved,kind,expected])
        progression=[]
        for kind,health,weapon,cycle in [(0,0x80,0,0),(0,0,0,0),(0,0,1,0),(0,0,2,0),(1,0x80,2,0),(1,0,1,0)]+[(1,0,2,i)for i in range(10)]+[(1,0,8|0x10,7)]:
            m=L.fork(seed);obj(m,5,kind);m.ram[2][0x68]=health|(2 if weapon&12 else 0);m.ram[2][0x69]=37;m.ram[2][0x65]=weapon;m.ram[2][0x860]=cycle
            for i in [0xba,0xbb,0xbc,0xbd,0xbe,0xbf,0x8f,0x90,0x70f,0x710]:m.ram[2][i]=0
            zp=bytes(m[3:11]);c,low=L.call(m,'NrPickup',x=5);nativelow=min(nativelow,low)
            assert bytes(m[3:11])==zp
            assert m[address(b,'Enemy_Flag')+5]==0 and m[address(b,'Enemy_ID')+5]==0
            assert all(m[address(b,n)+5]==0 for n in ['InvPickupOwner','InvPickup','InvRisePhase','InvPickupSaveLo','InvPickupSaveHi'])
            assert m[address(b,'FloateyNum_Control')+5]==6 and m[address(b,'FloateyNum_X_Pos')+5]==152
            assert H.get(m,'Square2SoundQueue')==0x20 and H.get(m,'PlayerStatus')==0 and m.ram[2][0x69]==37
            if health&128:assert m.ram[2][0x68]&128==0 and m.ram[2][0x65]==weapon
            elif kind==0 or weapon&3<2 and not weapon&12:assert m.ram[2][0x65]==(weapon&252)|min(2,(weapon&3)+1)
            else:assert m.ram[2][0x8f+(cycle>>3)]&(1<<(cycle&7)) and m.ram[2][0x860]==(cycle+1)%10
            assert bytes(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+7])==bytes([63,17,3,40,22,15,0]),'Palette changed sky/backdrop'
            earned=bytes(m.ram[2][:2048]);c,_=L.call(m,'NrPickup',x=5);assert bytes(m.ram[2][:2048])==earned,'Same dead object awarded twice'
            progression.append(dict(type=kind,health=health,weapon=weapon,option=cycle,result65=m.ram[2][0x65],result68=m.ram[2][0x68],stock=list(m.ram[2][0xba:0xc0]),earned=list(m.ram[2][0x8f:0x91]),minimum_SP=low))
        special=[]
        for kind in [2,3]:
            m=L.fork(seed);obj(m,5,kind);before=bytes(m.ram[2][:2048]);zp=bytes(m[3:11]);c,low=L.call(m,'NrPickup',x=5);nativelow=min(nativelow,low)
            assert bytes(m.ram[2][:2048])==before and bytes(m[3:11])==zp
            assert H.get(m,'StarInvincibleTimer')==(0x23 if kind==2 else 0)
            assert m[address(b,'FloateyNum_Control')+5]==(6 if kind==2 else 11)
            special.append(dict(type=kind,minimum_SP=low))
        # All combinations of original hurt timer and bits40/80 stay intact
        # except the explicit source health restore80; source timer never ticks.
        restore=[]
        for h in [0x80,0xc0,0xc3]:
            m=L.fork(seed);obj(m,5);m.ram[2][0x68]=h;m.ram[2][0x69]=73;c,low=L.call(m,'NrPickup',x=5)
            assert(m.ram[2][0x68],m.ram[2][0x69])==(h&127,73);restore.append([h,m.ram[2][0x68],73])
        oneups=[]
        for life in [0,9,0x99]:
            m=L.fork(seed);obj(m,5,1);m.ram[2][0x68]=0;m.ram[2][0x65]=2;m.ram[2][0x860]=9;m.ram[2][0xba]=0x49;m.ram[2][0x40b]=life
            lives=H.get(m,'NumberofLives');c,low=L.call(m,'NrPickup',x=5)
            assert m.ram[2][0xba]==0 and m[address(b,'FloateyNum_Control')+5]==11 and H.get(m,'NumberofLives')==lives
            # Real native floaty-number consumer awards the pending extra life.
            m[address(b,'FloateyNum_Timer')+5]=0x2b
            c,low=L.call(m,'FloateyNumbersCore',x=5);nativelow=min(nativelow,low)
            assert H.get(m,'NumberofLives')==lives+1
            oneups.append(dict(source_BCD_lives=life,result_BCD_lives=m.ram[2][0x40b],host_lives_before=lives,host_lives_after=H.get(m,'NumberofLives')))
        denied=0
        for ready,state,active,ident in [(0,128,1,46),(167,17,1,46),(167,128,0,46),(167,128,1,0)]:
            m=L.fork(seed);obj(m,5);m.ram[2][0x810]=ready;m[address(b,'Enemy_State')+5]=state;m[address(b,'Enemy_Flag')+5]=active;m[address(b,'Enemy_ID')+5]=ident
            before=bytes(m.ram[2][:2048]);c,_=L.call(m,'NrPickup',x=5);assert bytes(m.ram[2][:2048])==before;denied+=1
        q.update(passed=True,base_ROM_sha256=a['base_ROM_sha256'],donor_sha256=EXPECTED,full_source_component_bytes=a['bytes'],native_HUD_component_bytes=a['thin_bytes'],source_fixtures=cases,source_private_executions=3*cases-2*counts['option_HUD_bookkeeping'],source_cases=counts,source_layouts=['full_original_private_RAM3','native_HUD_private_RAM3','flat_source_model_of_native_HUD_split_ROM29_RAM3'],native_HUD_exclusions=['source00B4..00B9','source058F..05A2','source05AF..05C2','source58/59 dispatch pointer and0100..01FF stack common to all relocations'],source_X_dispatch_byte_normalizations=normalizations,source_trace_sha256=digest.hexdigest(),source_minimum_SP=lowest,native_minimum_SP=nativelow,native_source_earned_spawn_cases=len(spawn),native_maturity_cases=len(native),native_contact_progression=progression,native_star_1up=special,native_health_restore=restore,native_Kmark_lives=oneups,native_rejected_immature_inactive_stale_cases=denied,global_ZP_R0_R7_preserved=True,native_maturity_results=native,scope='Full original source/private RAM, AY/P/SP and callback events for declared pickup/option leaves; nativeHUD layouts exclude only unused sourceC534 old-HUD tile publication/queue with exact finalV behavior. Split proof is a flat source arena, not mapped native ingress. X differences only last-writer-proven relocated dispatch low bytes. Actual native UnionPwrUpCore/NrPrepare/NrPickupCollision/NrPickup/erase/score-popup/star/1UP/extra-life consumers execute with an explicit contiguous nativeHUD component overlay. No new ROM/loader image, ISR/SMC cuts, native emulator, source sound/nativeHUD publication or full-character admission claim.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),R/'tools/reference/karnov_pickups_1101_v2.inc',O/'assembly.json',O/'component.bin',BASE/'candidate.nes',BASE/'candidate.dbg',ROM]}
    (O/'CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','native_maturity_results','native_contact_progression']}));assert q['passed']
if __name__=='__main__':main()
