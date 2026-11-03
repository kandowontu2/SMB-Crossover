"""Prepare controller-only Mini smoke; bind final cartridge and compiled kernel."""
from pathlib import Path
import argparse,json,re,sys
from prepare_selected_native_packet_v1 import R,prepare,sha
from check_tmnt_render_oa import load,address,location
from observe_chip_committed_write import lua

O=R/'build/mini-mario-native-packet-1103-v25'
PARENT=R/'build/combined-owner-auth-root-1103-v116/combined-auth-private.nes'
GLOBALS=R/'build/roster-combined-1101-v3/candidate.lbl'
SOURCE=Path(__file__).with_suffix('.lua')

def source_plan():
    """One legal flat-floor run through the actual host22 source, no ROM."""
    import prepare_mini_mario_host_1103_v22 as H
    import check_mini_mario_step_1103_v18 as T
    data=(H.O/'mini-host-v22.bin').read_bytes();K=labels(H.O/'mini-host-v22.lbl');S=H.symbols()
    m=T.memory(data,K,0)
    for addr,path in[(0xd300,R/'build/mini-mario-native-tile-1103-v13/native-attributes.bin'),
                      (0xd000,R/'build/mini-mario-art-1103-v12/engine-animation-index.bin'),
                      (0xd160,R/'build/mini-mario-art-1103-v12/engine-animation-frames.bin')]:
        v=path.read_bytes();m.memory[addr:addr+len(v)]=v
    for n,v in dict(GameEngineSubroutine=8,Player_X_Position=40,Player_Y_Position=176,
                    Player_Y_HighPos=1,PlayerStatus=0,AreaType=1).items():m.memory[S[n]]=v
    T.call(m,K['MiniHostFresh']);phase='settle';n=0;events=[];epoch=0;startX=startY=minY=peakX=None
    def word(a):return m.memory[a]|m.memory[a+1]<<8
    for update in range(1,501):
        held={'right':1,'left':2,'jump':128}.get(phase,0)
        m.memory[S['FrameCounter']]=epoch;epoch=(epoch+1)&255;m.memory[S['SavedJoypadBits']]=held
        T.call(m,K['MiniHostMain']);n+=1
        x,y=word(0xc250),word(0xc252);vx=word(0xc200);vx=vx-65536 if vx>=32768 else vx
        supported=m.memory[0xc246]==2 and m.memory[0xc24c]&1
        assert not m.memory[0xc247]
        nextphase=None
        if minY is not None:minY=min(minY,y)
        if phase=='settle'and supported and vx==0:startX=x;startY=y;minY=y;nextphase='idle'
        elif phase=='idle':
            assert x==startX
            if n>=20:nextphase='right'
        elif phase=='right'and x>=startX+256:assert vx>0;peakX=x;nextphase='left'
        elif phase=='left':
            peakX=max(peakX,x)
            if vx<0 and x<=peakX-128:nextphase='brake'
        elif phase=='brake'and vx==0 and supported:startY=y;minY=y;nextphase='jump'
        elif phase=='jump'and n>=20:assert minY<=startY-256;nextphase='landing'
        elif phase=='landing'and supported and n>=2:
            assert startY-704<=minY<=startY-512 and abs(y-startY)<=16
            events.append(dict(phase='finish',update=update,x16=x,y16=y))
            return dict(passed=True,CPU_only=True,host_SHA256=sha(H.O/'mini-host-v22.bin'),
                updates=update,rise_pixels=(startY-minY)/16,events=events)
        assert n<180,(phase,n,x,y)
        if nextphase:phase=nextphase;n=0;events.append(dict(phase=phase,update=update,x16=x,y16=y))
    raise AssertionError('Source smoke phase bound')

def labels(path):
    return {n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',path.read_text(),re.M)}

def prepare_packet(rom,expected,*,kernel,kernel_labels,refs=(),output=None):
    """Only root calls this after exact candidate grant; no emulator or ROM writes."""
    rom,kernel,kernel_labels=map(lambda p:Path(p).resolve(),[rom,kernel,kernel_labels])
    assert sha(rom)==expected
    raw=rom.read_bytes();data=kernel.read_bytes();K=labels(kernel_labels)
    assert K['MiniVectors']==0xa000 and 0<len(data)<=5120
    required=['MiniHostMain','MiniStep','MiniAnimate','MiniHostBox','MiniNativeDraw']
    hooks={n:dict(name=n,pc=K[n],physical=3*8192+K[n]-0xa000,
                 memory='nesWorkRam',bytes=list(data[K[n]-0xa000:K[n]-0xa000+4]))for n in required}
    assert all(len(h['bytes'])==4 for h in hooks.values())
    # These native globals are unchanged public ABI, also used by host22 itself.
    L=labels(GLOBALS);L.update(labels(rom.with_suffix('.lbl')))
    names=['SelectedCharacter','OperMode','OperMode_Task','GameEngineSubroutine',
           'CrossoverMenuState','CrossoverMenuIndex','MarioVariant','NumberofLives',
           'Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos',
           'Player_State','Player_Y_Speed','CurrentOAMOffset','ObjectMetasprite',
           'SmPosePtr','Player_Rel_XPos','BoundingBox_UL_Corner']
    L={n:L[n]for n in names}
    b=load(PARENT);pc=address(b,'GameCoreRoutine');at=location(b,'GameCoreRoutine')
    assert raw[at:at+4]==b['raw'][at:at+4]
    hooks['GameCoreRoutine']=dict(name='GameCoreRoutine',pc=pc,physical=at-16,
        memory='nesPrgRom',bytes=list(raw[at:at+4]))
    render=R/'build/mini-mario-native-render-1103-v15/native-render.s'
    tables=[]
    for name in ['MiniPoseTile','MiniPoseAttribute']:
        values=[int(v)for v in re.search(name+r':\s*\.byte ([0-9,]+)',render.read_text())[1].split(',')]
        assert len(values)==78;tables.append(values)
    assert data[K['MiniNativeDrawEnd']-0xa000-156:K['MiniNativeDrawEnd']-0xa000]==bytes(tables[0]+tables[1])
    body=R/'build/mini-mario-art-1103-v12/body.chr'
    cfg=dict(ROM_sha256=expected,kernel_SHA256=sha(kernel),hooks=hooks,pose_tiles=tables[0],pose_attrs=tables[1],art=list(body.read_bytes()),
        expected_chr4=968,max_frames=3200,
        menu_variants=[1,5,6,2,3,4,7,8],
        name=[36]*3+[ord(c)-55 if c!=' 'else 36 for c in 'MINI MARIO']+[36]*3)
    text='local L='+lua(L)+'\nlocal C='+lua(cfg)+'\n'+SOURCE.read_text()
    # Syntax-only validation never executes Lua or accesses an emulator.
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    output=Path(output or O/'smoke')
    prepare(output,rom,text,[Path(__file__),SOURCE,kernel,kernel_labels,GLOBALS,render,body,
        PARENT.with_suffix('.dbg'),R/'build/mini-mario-menu-1103-v14/menu-CPU-v17.json',*map(Path,refs)],
        expected=expected,timeout=180,allow_interactive=True,
        scope='Mini controller-only cold Mario Select cycle to variant8/raw41/name; actual constructor ready2; source-epoch idle/right/reversal/jump/landing. Physical kernel/preimages, native Main returns, original6x7 bbox, stable zero header, real DMA CHR968/OAM. Two PNGs. No writes, cheats, ability seeds, helpers or full-stage claim.')
    return output/'ready.json'

def main():
    a=argparse.ArgumentParser();a.add_argument('--rom',type=Path);a.add_argument('--sha')
    a.add_argument('--kernel',type=Path);a.add_argument('--labels',type=Path)
    a.add_argument('--ref',type=Path,action='append',default=[])
    a.add_argument('--source-only',action='store_true');q=a.parse_args()
    O.mkdir(exist_ok=True)
    if q.source_only:
        sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
        from lupa.lua54 import LuaRuntime
        LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')('local L={} local C={}\n'+SOURCE.read_text())
        receipt=dict(prepared_template=True,native=False,ROM_written=False,source_SHA256=sha(SOURCE),
            producer_SHA256=sha(__file__),pending='Exact granted ROM/hash and compiled host kernel/labels are required before READY.',
            required_labels=['MiniVectors','MiniHostMain','MiniStep','MiniAnimate','MiniHostBox','MiniNativeDraw'],
            max_PNGs=2,emulated_writes=False,flat_source_plan=source_plan())
        (O/'template.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt));return
    assert q.rom and q.sha and q.kernel and q.labels
    print(prepare_packet(q.rom,q.sha,kernel=q.kernel,kernel_labels=q.labels,refs=q.ref))

if __name__=='__main__':main()
