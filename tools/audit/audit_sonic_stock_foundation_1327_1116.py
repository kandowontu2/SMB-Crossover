"""Read-only Sonic/Super Sonic current packets, native policies and cold scope."""
from functools import lru_cache
from pathlib import Path
from hashlib import sha256
from unittest.mock import patch
from collections import Counter
import argparse,json,re,struct
import compose_jay_status_size_publication_00bb_1116 as C
import current_jay_natural_stock_00bb_1116 as Metadata

R,ROM,H=Metadata.R,Metadata.ROM,Metadata.H
N,W,Frames=Metadata.N,Metadata.W,Metadata.Frames
PIN=C.CANDIDATE
C_SHA='7f1c0eab5a08a7a7e3fbf922aaff1a1c2b8b7513c9c3bd11ed8eee50d01e8d0c'
META_SHA='4bff33bfc8895d86dc1a405ebd0d7b2b041ca27d73c7d536068588b7e372abb1'
CHR=1048592
CODE_PAGES=(*range(321,328),330)
COOKIE_PAGES=CODE_PAGES+(328,333,334,224,226)
FORMS={'sonic':(3,'SONIC',224),'super':(4,'SUPER SONIC',226)}
SYMBOL_INPUTS={
 'build/kirby-approach-owner-1101-v3/candidate.nes':'367266d2ec4e62fcefc15fffb3a05095a16060ad52f9d68348f213d94b31268c',
 'build/kirby-approach-owner-1101-v3/candidate.dbg':'cada90f529ff56f943eed27979a51d723f4273c2a077274a35eee5d115fa1e54',
 'build/bub-menu-candidate-1102-v2/combined-event.nes':'613b3300b09e530ec920835b95df53f3115d865ed854e273809d4cafa52407ce',
 'build/bub-menu-candidate-1102-v2/combined-event.dbg':'a54fadb57dbd7bb620a6b37a0ba8324cecc698c32a0dc5e0cde5855a347f41b4',
 'build/thomas-current-candidate-1102-v3/candidate.nes':'d0b445a71d6c539804d7c559fafc2c328ebf97ab4e35e8f3273f94ff8a25d01d',
 'build/thomas-current-candidate-1102-v3/candidate.dbg':'a54fadb57dbd7bb620a6b37a0ba8324cecc698c32a0dc5e0cde5855a347f41b4'}


def prg(bank,pc):return 16+8192*bank+(pc&8191)


@lru_cache(maxsize=1)
def bindings(raw):
    assert isinstance(raw,bytes)and H(raw)==PIN,'Exact current1327 only'
    assert H(Path(C.__file__).read_bytes())==C_SHA and H(Path(Metadata.__file__).read_bytes())==META_SHA
    for path,pin in SYMBOL_INPUTS.items():assert H((R/path).read_bytes())==pin,'Changed retained metadata input: '+path
    parent=C.inverse(raw);assert H(parent)==Metadata.PIN
    old=Metadata.bindings(parent)['bundle'];b=dict(old,raw=raw);assert b['raw']is raw
    page=lambda p:raw[CHR+p*1024:CHR+(p+1)*1024]
    for p in COOKIE_PAGES:assert page(p)==parent[CHR+p*1024:CHR+(p+1)*1024]
    kernel=b''.join(map(page,CODE_PAGES));meta=page(328);cookie=raw[1034472:1034488]
    assert cookie==bytes.fromhex('a72b01')+sha256(b''.join(map(page,COOKIE_PAGES))).digest()[:13]
    assert cookie==parent[1034472:1034488]and meta[:8].startswith(b'SMSONIC')
    table,main,fresh,power,contextlo,contexthi,ctor,rows=struct.unpack('<8H',meta[46:62])
    assert table==0xd100 and rows==38
    def loaded(pc):
        if 0xa000<=pc<0xc000:return kernel[pc-0xa000:]
        if 0xd000<=pc<0xd400:return meta[pc-0xd000:]
        if 0xd400<=pc<0xd800:return page(333)[pc-0xd400:]
        if 0xd800<=pc<0xdc00:return page(334)[pc-0xd800:]
        raise AssertionError(('Outside actual current Sonic loaded domain',hex(pc)))
    services=[]
    for row in range(38):
        data=loaded(table+3*row);assert data[0]==0x4c
        target=int.from_bytes(data[1:3],'little');code=loaded(target)
        services.append(dict(row=row,PC=table+3*row,target=target,first16=code[:16].hex()))
    assert services[0]['target']==main and services[15]['target']==fresh and services[33]['target']==power
    names=('SelectedCharacter','OperMode','OperMode_Task','GameEngineSubroutine','GamePauseStatus','NmiDisable',
        'Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State','Player_Y_Speed','PlayerSize','PlayerStatus',
        'NumberofLives','FrameCounter','GuestPowerupActive','GuestPowerupAge','GuestPowerupTarget','TimerControl',
        'StarInvincibleTimer','Square2SoundQueue','AreaMusicQueue','Enemy_Flag','Enemy_ID','Enemy_State','PowerUpType',
        'FloateyNum_Control','FloateyNum_Timer','InvPickup','InvPickupOwner','WorldNumber','LevelNumber','AreaType','AreaAddrsLOffset')
    fields={n:W.address(b,n)for n in names}
    hooks={}
    for name in('GameLoop','SetupPowerUp','PlayerHeadCollision','HandlePowerUpCollision','MarioSourcePowerupCollision',
        'GuestBeginPowerup','GuestPowerupUpdate','FloateyNumbersCore','SetupFloateyNumber','InjurePlayer'):
        at=W.location(b,name);pc=W.address(b,name);assert raw[at:at+32]==parent[at:at+32]
        hooks[name]=dict(PC=pc,tag=((at-16)//8192)|128,file=at,first32=raw[at:at+32].hex())
    for name,pc in(('SonicHostMain',main),('SonicHostFresh',fresh),('SonicHostPowerup',power),('SonicHostConstruct',ctor)):
        hooks[name]=dict(PC=pc,tag=3 if pc<0xc000 else 2,first32=loaded(pc)[:32].hex())
    return dict(bundle=b,fields=fields,hooks=hooks,cookie=cookie,kernel=kernel,metadata=meta,
        packet_pages=[dict(page=p,SHA256=H(page(p)))for p in COOKIE_PAGES],services=services,
        service_table=table,host_context=[contextlo,contexthi],loaded=loaded,
        metadata00bb_only_SHA256=C.PIN,normalizer_SHA256=C_SHA,actual1327_CPU_bytes_retained=True)


def state(m):
    r=lambda n:N.get(m,n)
    out={n:r(n)for n in('SelectedCharacter','PlayerStatus','PlayerSize','NumberofLives','GuestPowerupActive','GuestPowerupAge',
        'GuestPowerupTarget','StarInvincibleTimer','GameEngineSubroutine','GamePauseStatus','TimerControl')}
    out.update(x=r('Player_X_Position')+256*r('Player_PageLoc'),y=r('Player_Y_Position'),
        form=m[0x5ffe],ringBCD=m.ram[2][0x340],ringLives=m.ram[2][0x341],hurt=m.ram[2][0x34f],
        source_star_flags=m.ram[2][0x350],drop=m.ram[2][0x351],ready=m.ram[2][0x119],have_epoch=m.ram[2][0x11a],
        source_tick=m.ram[2][0x92],source_flags=m.ram[2][0x30],source_width=m.ram[2][0x41],source_height=m.ram[2][0x42])
    return out


def cold(raw,form):
    q=bindings(raw);selects,label,page=FORMS[form];b=q['bundle']
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    W.UI.key(m,4);W.UI.key(m,4);W.UI.key(m,4);W.UI.key(m,1)
    assert N.get(m,'CrossoverMenuIndex')==25 and W.UI.menu_name(m)[0]=='MR GIMMICK'
    for _ in range(selects):W.UI.key(m,32)
    assert W.UI.menu_name(m)[0]==label and N.get(m,'SelectedCharacter')==43 and m[0x5ffe]==selects
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for epoch in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
        m.controller_pad=0;Frames.frame(m,cold=True,whole_pass=True)
    else:raise AssertionError('Current Sonic genuine cold bound')
    assert m.bundle['raw']is raw and tuple(bytes(m.ram[k][0x1fe0:0x1ff0])for k in(2,3))==(q['cookie'],)*2
    assert bytes(m.ram[3][:0x1fe0])==q['kernel'][:0x1fe0]
    assert bytes(m.ram[2][0x1000:0x1400])==q['metadata']
    return m,dict(form=form,name=label,Select=selects,CHR=page,initial_epoch_steps=epoch,state=state(m))


def run(raw,actual_cold=False):
    q=bindings(raw)
    files=('tools/audit/replay_sonic_vol2_forms_1111.py','tools/audit/check_sonic_ring_physical_1110.py',
        'tools/playthroughs/sonic_original_full_stage_stdout_1110.lua','tools/playthroughs/sonic_earned_injury_stdout_1110_v2.lua',
        'tools/playthroughs/sonic_ring_feedback_stdout_1110_v3.lua','tools/reference/super_sonic_roster_1111.s',
        'tools/reference/sonic_sms_native_host_services_1110.py','tools/reference/sonic_sms_ring_adapter_1110.s',
        'tools/reference/sonic_sms_ring_live_1110.s','tools/reference/sonic_sms_ring_contact_1110.s',
        'src/guest_powerups.s','src/mario_source.s')
    inventory={f:H((R/f).read_bytes())for f in files}
    out=dict(passed=True,read_only=True,parent_SHA256=PIN,reference00bb_only_SHA256=C.PIN,
        normalizer_SHA256=C_SHA,metadata_SHA256=META_SHA,actual_current_CPU_bytes_retained=True,
        forms=[dict(key=k,Select=v[0],name=v[1],raw=43,menu_slot=25,CHR=v[2])for k,v in FORMS.items()],
        packet_cookie=q['cookie'].hex(),cookie_file=1034472,kernel_SHA256=H(q['kernel']),metadata_page328_SHA256=H(q['metadata']),
        metadata_magic=q['metadata'][:8].decode(),packet_pages=q['packet_pages'],services=q['services'],
        private_source=dict(bank=2,ringBCD=0xc340,ringLives=0xc341,hurt_flags=0xc34f,source_star_flags=0xc350,drop_flags=0xc351,
            ring_music=0xc34e,actor_flags=0xc030,source_input=0xc0a8,
            source_tick=0xc092,x24=0xc070,y24=0xc073,velocityX24=0xc020,velocityY24=0xc060,host_context=q['host_context']),
        hooks=q['hooks'],source_inventory=inventory,retained_symbol_inputs=SYMBOL_INPUTS,cold16=[],
        historical_closed=dict(ROM='c4568faf4f472d4d6c3915c9b4258d5c04d6dcbb562b3e5602a5d580bb3046a2',
            both_forms_separate_fullstage_ringloss_and_M=True,not_replayed=True,natural_F_S_L_missing=True),
        no_item_route_or_seed_or_code_or_asset_or_helper_change=True,native=False,outputs=0)
    if actual_cold:
        for form in FORMS:
            m,row=cold(raw,form);counts=Counter();pending=[];objects=[];base=N.NesMPU
            hooks=q['hooks'];points={(hooks[n]['tag'],hooks[n]['PC']):n for n in('GameLoop','SonicHostMain')}
            def tag(pc):return m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
            class CPU(base):
                def __init__(self,*a,**kw):super().__init__(*a,**kw);objects.append(self);self.pending=[]
                def settle(self):
                    while self.pending and(self.pc,self.sp,tag(self.pc))==self.pending[-1][1]:counts[self.pending.pop()[0]+'_returns']+=1
                def step(self):
                    self.settle();name=points.get((tag(self.pc),self.pc))
                    if name:
                        counts[name+'_entries']+=1;sp=self.sp
                        pc=(m[0x100+((sp+1)&255)]+256*m[0x100+((sp+2)&255)]+1)&65535
                        self.pending.append((name,(pc,(sp+2)&255,tag(pc))))
                    return super().step()
            with patch.object(N,'NesMPU',CPU):
                for _ in range(16):
                    m.controller_pad=0;Frames.frame(m,whole_pass=True)
                    for cpu in objects:cpu.settle();assert not cpu.pending
                    objects.clear()
            assert counts['GameLoop_entries']==counts['GameLoop_returns']==16
            assert counts['SonicHostMain_entries']==counts['SonicHostMain_returns']and counts['SonicHostMain_returns']>=16
            assert m[0x5ffe]==FORMS[form][0]and state(m)['x']==40 and N.get(m,'NumberofLives')==2
            row.update(counts=dict(counts),terminal=state(m));out['cold16'].append(row)
    out['source_SHA256']=H(Path(__file__).read_bytes());out['receipt_SHA256']=H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cold16',action='store_true');a=p.parse_args()
    raw=ROM.read_bytes();assert H(raw)==PIN
    def deny(*a,**kw):raise AssertionError('Sonic foundation attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw,a.cold16)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
