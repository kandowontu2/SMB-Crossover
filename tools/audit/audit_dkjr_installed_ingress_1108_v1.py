"""Bounded read-only-ROM DK Jr ingress audit on exact installed 244734.

The CPU fixture explicitly selects dormant raw40; it is not a claim that the
public menu can select it. Native entrance chooses the final anchor itself.
No ROM is written and no emulator is launched.
"""
from collections import Counter
from pathlib import Path
import hashlib, json, sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools/reference')]
import assess_dkjr_menu_current_1103_v11 as UI
import audit_current_menu_indicators_1102_v1 as SYMBOLS
import check_prince_strike_cold_1103_v131 as C
import check_dkjr_entrance_order_1103_v88 as ENTRANCE

N, F = C.N, UI.F
O = R / 'build/dkjr-current-ingress-1108-v1'
ROM = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN = '244734bbc2690b4e97e654cc72f8f153bedbe3fcc799f714e9508784e4f33af4'
BASE = R / 'build/dkjr-native-source-1102-v2'
UIBASE = R / 'build/dkjr-menu-current-1103-v1'
UISTUDY = R / 'build/dkjr-menu-ca90-1103-v11/readiness-v11.json'
CURRENT_MINI = R / 'build/mini-two-fireballs-1103/candidate.json'
sha = lambda b: hashlib.sha256(b).hexdigest()


def patch_status(raw, rows):
    answer = []
    for r in rows:
        a = r['file_offset']; old = bytes.fromhex(r['old_hex']); new = bytes.fromhex(r['new_hex'])
        assert len(old) == len(new)
        current = raw[a:a+len(new)]
        answer.append(dict(file_offset=a, bytes=len(old), role=r['role'],
            physical_PRG=r.get('physical_PRG'), physical_CHR=r.get('physical_CHR'),
            CPU_half_open=r.get('CPU_half_open'), current_SHA256=sha(current),
            preimage_matches=current==old, already_replacement=current==new))
    return answer


def cpu(raw, cookie):
    b = SYMBOLS.bundle(); b['raw'] = raw
    # Existing hardware-oriented MMC5 CPU bus from the current owners' cold
    # proofs. No source image is injected: native InitScreen must load it.
    N.Bus = C.C.C.C.V.ControllerBus
    m = N.fresh(b)
    C.fields(m,40)
    for bank in [2,3]:
        m.ram[bank][:] = bytes([0x9d])*8192
        m.ram[bank][0x1fe0:0x1ff0] = bytes(16)
    N.put(m,Player_X_Position=0,Player_PageLoc=0,Player_Y_Position=0,
          Player_Y_HighPos=0,GameEngineSubroutine=0,ScreenRoutineTask=0,VRAM_Buffer1_Offset=0)
    lab = json.loads((BASE/'native-entrance-v89-layout.json').read_text())['labels']
    pts={(0xb013,193):'CoSceneGate',(0xb062,193):'ExSceneOwn',(0xae00,193):'CoCold',
         (0xb0f8,193):'public_scene36',(0xb0b9,193):'public_Fresh15'}
    for name in ['DkjrInitialize','DkNativeFresh','DkNativeMain','DkPauseThaw','DkjrJumpRestart']:
        pc=lab[name];pts[pc,2 if pc>=0xc000 else 3]=name
    hits=Counter()
    def watch(c):
        if c.pc>=0x8000:
            name=pts.get((c.pc,c.memory.rawtags[(c.pc-0x8000)//8192]))
            if name:hits[name]+=1
    init=F.invoke(m,'InitScreen',watch=watch)
    assert all(hits[n] for n in ['CoSceneGate','ExSceneOwn','CoCold','public_scene36'])
    def headers():
        return all(bytes(m.ram[k][0x1fe0:0x1ff0])==cookie for k in [2,3])
    assert headers() and m.ram[2][0x8fe]==1
    phases=[dict(stage='real_InitScreen_cold_scene36',**ENTRANCE.snapshot(m))]
    N.put(m,PlayerEntranceCtrl=2,AltEntranceControl=0,JoypadOverride=0,AreaType=1,
          AreaPointer=0,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,
          ScreenRight_PageLoc=0,GameTimerSetting=1,FetchNewGameTimerFlag=1,
          AreaParserTaskNum=7,GameTimerCtrlTimer=24,GameTimerExpiredFlag=0,DisableIntermediate=1,
          PlayerSize=1,Player_BoundBoxCtrl=1,VRAM_Buffer1_Offset=0)
    F.invoke(m,'HuFresh',watch=watch);assert headers() and m.ram[2][0x8fe]==1
    F.invoke(m,'Entrance_GameTimerSetup',watch=watch);F.invoke(m,'PlayerEntrance',watch=watch)
    phases.append(dict(stage='real_table_entrance',**ENTRANCE.snapshot(m)))
    assert N.get(m,'GameEngineSubroutine')==8
    for name in ['Block_Buffer_1','Block_Buffer_2']:
        at=UI.address(b,name);m[at:at+208]=bytes(208)
        for row in [11,12]:m[at+16*row:at+16*row+16]=bytes([0x54])*16
    for i,v in enumerate([4,0,0]):m[UI.address(b,'GameTimerDisplay')+i]=v
    for i in range(6):m[UI.address(b,'Enemy_Flag')+i]=0
    N.put(m,DisableScreenFlag=0,Mirror_PPUMASK=30,TimerControl=0,OperMode_Task=3,NmiDisable=255)
    m[0x2001]=30
    epoch=0
    def main(keys):
        nonlocal epoch
        epoch+=1
        m.controller_pad=keys
        N.put(m,FrameCounter=epoch,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
        z=N.invoke(m,'GameCoreRoutine',a=83,x=0,y=0,p=0x31)
        assert N.get(m,'NumberofLives')==2 and headers() and m.ram[2][0x8fe]==2
        # Avoid growing hardware logs across repeated independent epochs.
        C.clear(m)
        return z['CPU']
    main(0);last=ENTRANCE.snapshot(m)
    assert tuple(last[k] for k in ['nativeX','nativeY','nativeHighY','sourceX','sourceY','ready'])==(40,176,1,32,191,2),last
    phases.append(dict(stage='first_real_engine8_Main',**last))
    def worldx():return N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
    rows=[]
    for name,pads in [('idle',[0]*12),('right',[1]*32),('left',[2]*16),
                      ('jump_right_then_left',[129]+[1]*3+[2]*32+[0]*28)]:
        start=worldx();xs=[];ys=[];cycles=[];directions=[];states=[]
        for keys in pads:
            cycles.append(main(keys));xs.append(worldx());ys.append(N.get(m,'Player_Y_Position'))
            directions.append(m.ram[2][0x54]);states.append(m.ram[2][0x6b])
        dx=xs[-1]-start
        if name=='idle':assert dx==0 and min(ys)==max(ys)==176
        if name=='right':assert dx==20 and ys[-1]==176
        if name=='left':assert dx==-10 and ys[-1]==176
        if name.startswith('jump'):
            assert min(ys)==161 and ys[-1]==176 and 3 in states and states[-1]==1
            assert all(d==4 for d,y in zip(directions[4:36],ys[4:36]) if y<176)
        rows.append(dict(control=name,updates=len(pads),deltaX=dx,minY=min(ys),endY=ys[-1],
                         mean_CPU=sum(cycles)/len(cycles),max_CPU=max(cycles)))
    F.invoke(m,'HuReset',watch=watch)
    assert m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0 and N.get(m,'SelectedCharacter')==40
    return dict(fixture='Explicit CPU raw40 selection and legal flat BlockBuffers. No ready/actor/final native-Y seeds.',
                init_min_SP=init['minimum_SP'],source_anchor=phases,entry_hits=dict(hits),
                controls=rows,real_HuReset_invalidates_headers=True)


def main():
    O.mkdir(exist_ok=True)
    receipt=O/'installed-ingress.json';assert not receipt.exists()
    raw=ROM.read_bytes();assert sha(raw)==PIN
    assert json.loads(CURRENT_MINI.read_text())['candidate_SHA256']==PIN
    backend=BASE/'native-combined-owner-v101-measurement.json'
    mb=json.loads(backend.read_text());backend_rows=patch_status(raw,mb['patches'])
    carriers=[r for r in backend_rows if r['physical_CHR'] is not None]
    assert len(carriers)==11 and all(r['already_replacement'] for r in carriers)
    cookie=(BASE/'native-cookie-v90.bin').read_bytes()
    i=UI.off(65,0xa7c5);assert raw[i:i+16]==cookie
    scene=raw[UI.off(65,0xb013):UI.off(65,0xb026)]
    assert scene==bytes.fromhex('0848ad026038e925c905904368284c1daceaea')
    rare=raw[UI.off(124,0xa7cb)];assert rare==42
    old=UIBASE/'current-menu-v7.json'
    menu=patch_status(raw,json.loads(old.read_text())['proposed_patch_list'])
    factor=patch_status(raw,json.loads(UISTUDY.read_text())['source_funding_measurement']['patches'])
    assert all(r['preimage_matches'] for r in factor)
    b=SYMBOLS.bundle();b['raw']=raw
    m=UI.seed(b,27);assert UI.menu_name(m)[0]=='DONKEY KONG' and N.get(m,'SelectedCharacter')==28
    for pad in [1,2]:
        UI.key(m,32,pad);assert UI.menu_name(m)[0]=='DONKEY KONG' and N.get(m,'SelectedCharacter')==28
    for key in [16,128]:
        t=N.fork(m);UI.key(t,key);assert N.get(t,'SelectedCharacter')==28 and N.get(t,'CrossoverMenuState')==0
    result=dict(passed=True,CPU_only=True,ROM_written=False,native_run=False,menu_admitted=False,
        installed_SHA256=PIN,exact_existing_DK_cookie=cookie.hex(),exact_DK_payload_carriers=[r['physical_CHR'] for r in carriers],
        current_five_owner_scene=scene.hex(),current_rare_upper_bound=rare,
        old_backend_rebase_rows=backend_rows,old_menu_rebase_rows=menu,current_partial_nav_factor_preimages=factor,
        actual_CPU_menu='DK slot27 selects raw28 and displays DONKEY KONG. P1/P2 Select do not expose40; Start/A still start28.',
        dormant_raw40_ingress=cpu(raw,cookie),
        remaining=['Fund and qualify one exact focused DK/Jr selector + menu name/portrait layer without reverting Mini or touching five-owner/Prince spans.',
                   'Run actual cold menu/P1/P2 Select/confirm and engine8 movement, palette/OAM/CHR and idle/walk cadence in root Mesen.',
                   'Natural combat/fruit/vines, first pipe and all 1-1 crossings are open. Keep original 15px jump; prove intended native vine traversal or use existing native platforms and record placements/crossings.'],
        bindings={str(p.resolve()):sha(p.read_bytes()) for p in [Path(__file__),ROM,backend,BASE/'native-entrance-v89-layout.json',BASE/'native-cookie-v90.bin',old,UISTUDY,CURRENT_MINI,Path(UI.__file__),Path(C.__file__),Path(ENTRANCE.__file__)]})
    assert sha(ROM.read_bytes())==PIN
    receipt.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['passed','installed_SHA256','actual_CPU_menu','dormant_raw40_ingress']}))


if __name__=='__main__':main()
