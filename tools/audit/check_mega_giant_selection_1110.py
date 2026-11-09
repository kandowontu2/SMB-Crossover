"""Select the private Giant alternate and acquire its render rows on the real scene call."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

import check_mega_giant_compound_1110 as C
import check_mega_giant_render_storage_1110 as G
import check_mega_giant_ppu_mapping_1110_v1 as P
import check_mega_giant_resident_1110 as Rr
from check_mega_giant_resident_rogue_nmi_1110 import campaign, current_images
from inventory_playable_menu_1101_v3 import menu_name
from check_tmnt_render_oa import location


R,M=C.R,C.M
SOURCE=R/'tools/reference/mega_giant_mario_selection_1110.s'
RENDER=R/'build/mega-giant-render-storage-1110/proof-v2.json'
AREAS=((63,0xa7b2,192),(84,0xbe00,256),(97,0xc469,23),(84,0xbf00,102),
       (90,0xb15c,36),(90,0xb86b,37))


def assemble(out,b,cookie):
    symbols=('SelectedCharacter','CrossoverMenuIndex','MarioVariant','VRAM_Buffer1','VRAM_Buffer1_Offset',
             'CurrentBankC','OperMode','FamilyMainCommit','R3','R4','M0','M1',
             'GameEngineSubroutine','Player_State','CrouchingFlag','Player_X_Speed',
             'Left_Right_Buttons','PlayerAnimCtrl')
    defs=''.join(f'{n}=${C.address(b,n):04x}\n' for n in symbols)
    assert len(cookie)==16 and cookie[12:]==bytes((2,1,1,0xd0))
    defs+='.define GIANT_SCENE_SIGNATURE '+','.join(f'${n:02x}' for n in cookie[:12])+'\n'
    cfg='MEMORY{M:start=$a7b2,size=$c0,file=%O,fill=yes;S:start=$be00,size=$100,file=%O,fill=yes;'
    cfg+='A:start=$c469,size=$17,file=%O,fill=yes,fillval=$ff;T:start=$bf00,size=$66,file=%O,fill=yes;'
    cfg+='U:start=$b15c,size=$24,file=%O,fill=yes;V:start=$b86b,size=$25,file=%O,fill=yes;'
    cfg+='D:start=$a200,size=$80,file=%O,fill=yes,fillval=$ff;} '
    cfg+='SEGMENTS{GIANT_MENU:load=M,type=ro;GIANT_SCENE:load=S,type=ro;GIANT_AUDIO_MUX:load=A,type=ro;'
    cfg+='GIANT_SCENE_TAIL:load=T,type=ro;GIANT_TAIL_CLEAN:load=U,type=ro;GIANT_TAIL_OWNER:load=V,type=ro;GIANT_STAGE_DRAW:load=D,type=ro;}'
    with tempfile.TemporaryDirectory(prefix='linked-',dir=out) as f:
        s,g,o,z,l=(Path(f)/f'giant.{ext}' for ext in ('s','cfg','o','bin','lbl'))
        s.write_text(defs+SOURCE.read_text())
        g.write_text(cfg)
        cc=R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',s,'-o',o],check=True)
        s.unlink()
        subprocess.run([cc/'ld65.exe','-C',g,o,'-o',z,'-Ln',l],check=True)
        labels={line.split()[2][1:]:int(line.split()[1],16) for line in l.read_text().splitlines()}
        data=z.read_bytes()
        return data[:-0x80],data[-0x80:],labels


def compose(base,b,code,labels):
    raw=bytearray(b['raw'])
    patches=[]
    def add(bank,pc,old,new):
        at=Rr.at(bank,pc)
        assert raw[at:at+len(old)]==old and len(old)==len(new),(bank,hex(pc),old.hex(),raw[at:at+len(old)].hex())
        raw[at:at+len(new)]=new
        patches.append(dict(physical_PRG=bank,PC=pc,file_offset=at,old_hex=old.hex(),new_hex=new.hex()))
    def retarget(bank,pc,pre,target,tag):
        add(bank,pc,bytes.fromhex(pre),bytes((0xa9,target&255,0x8d,0x6c,1,0xa9,target>>8,0x8d,0x6d,1,0xa9,tag)))
    step=0
    for bank,pc,n in AREAS:
        old=Rr.native_slice(b['raw'],bank,pc,n)
        if bank in (84,90):
            assert not any(old)
        add(bank,pc,old,code[step:step+n])
        step+=n
    assert step==len(code)
    add(63,0xa74a,bytes.fromhex('bdb2a7'),bytes((0x20,))+labels['GiantAmmoLookup'].to_bytes(2,'little'))
    retarget(66,0xacc3,'a9208d6c01a9b78d6d01a9cf',labels['GiantMenuName'],0xbf)
    retarget(3,0xb24d,'a9138d6c01a9b08d6d01a9c1',labels['GiantScene'],0xd4)
    target=labels['GiantTailClear']
    old=bytes.fromhex('684a850b4a650b692c850ba9a36900850ca9f84cb585')
    new=bytes((0x68,0x8d,0x6a,1,0xa9,target&255,0x8d,0x6c,1,0xa9,target>>8,
               0x8d,0x6d,1,0xa9,0xda,0x4c,0x5a,1))
    add(4,0xa24b,old,new.ljust(len(old),b'\xea'))
    add(124,0xadd2,bytes((9,)),bytes((10,)))
    add(124,0xade6,bytes((0,0xea)),bytes((9,0)))
    rows=[]
    for mode,i,tag,hi in Rr.audio_rows(base):
        if tag!=0xd4 or hi not in (0xbe,0xbf):
            continue
        at=0xbba7 if mode=='lower' else 0xbe3f
        add(62,at+i,bytes((0xd4,)),bytes((0x54,)))
        rows.append((mode,i))
    assert len(rows)>30
    return C.bundle(bytes(raw)),patches,rows


def ammo(old,new):
    pair=[M.fresh(b) for b in (old,new)]
    for m in pair:
        M.put(m,CurrentBank=191)
        m[0x5115]=191
    cases=0
    for x in range(256):
        for flags in (0x30,0x31,0x70,0xf1):
            outcomes=[]
            for m in pair:
                # Stop at the original LDA's continuation. Only its A/NZ
                # are defined and X/Y/CVID are live to the cheat loop.
                cpu=M.NesMPU(memory=m,pc=0xa74a)
                cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=173,x,71,flags,241
                while cpu.pc!=0xa74d:
                    assert m[cpu.pc]
                    cpu.step()
                outcomes.append((cpu.a,cpu.x,cpu.y,cpu.p&0xef,cpu.sp))
            assert outcomes[0]==outcomes[1],(x,flags,outcomes)
            cases+=1
    return cases


def frame(m,key,labels=None):
    M.put(m,SavedJoypadBits=key,SavedJoypad1Bits=key,SavedJoypad2Bits=0,NmiDisable=255)
    seen=[]
    def visit(c):
        if labels and C.tag(m,c.pc)==212:
            if c.pc in (labels['GiantScene'],labels['GiantSceneCommit'],labels['GiantSceneRetire']):
                seen.append(c.pc)
    G.run_cpu(m,C.address(m.bundle,'GameLoop'),observe=visit)
    name=menu_name(m)[0] if M.get(m,'CrossoverMenuState')==2 else None
    M.consume(m)
    m.writes.clear()
    m.ram_writes.clear()
    m.ppu_log.clear()
    return name,seen


def reset_menu(b,labels,mode=0):
    m=P.ColdBus(b)
    c=M.NesMPU(memory=m,pc=None)
    c.reset()
    idle=C.address(b,'IdleLoop')
    for _ in range(200000):
        if c.pc==idle:
            break
        assert m[c.pc]
        c.step()
    else:
        raise AssertionError('Native reset did not reach IdleLoop')
    m.vblank_at_boot=False
    for update in range(120):
        if M.get(m,'CrossoverMenuState')==2:
            return m,update
        frame(m,16 if update==40 else 0,labels)
    raise AssertionError('Title did not enter the native menu')


def select_and_start(b,labels,pages,meta,code,n=9,corrupt=False):
    m,title=reset_menu(b,labels)
    rows=[]
    for _ in range(n):
        frame(m,0,labels)
        name,_=frame(m,32,labels)
        rows.append((M.get(m,'SelectedCharacter'),M.get(m,'MarioVariant'),name))
    frame(m,0,labels)
    wrapped=None
    if n==9:
        branch=M.fork(m)
        name,_=frame(branch,32,labels)
        wrapped=(M.get(branch,'SelectedCharacter'),M.get(branch,'MarioVariant'),name)
        assert wrapped==(0,0,'MARIO'),wrapped
        assert rows[-2:]==[(41,8,'MINI MARIO'),(0,9,'MEGA GIANT MARIO')],rows
    frame(m,16,labels)
    if corrupt:
        m.corrupt_at=(2,0x100f)
    reads=m.ppu_reads
    hits=[]
    for age in range(600):
        if (M.get(m,'OperMode'),M.get(m,'OperMode_Task'),M.get(m,'GameEngineSubroutine'))==(1,3,8):
            break
        _,hits_now=frame(m,0,labels)
        hits.extend(hits_now)
    else:
        raise AssertionError(('Native Start did not enter 1-1',rows))
    m.corrupt_at=None
    if corrupt:
        assert labels['GiantSceneCommit'] not in hits and all(m.ram[i][0x1fe0]!=0xa7 for i in (2,3)),hits
    elif n==9:
        assert hits.count(labels['GiantSceneCommit'])==1,(hits,m.ppu_reads-reads)
        assert bytes(m.ram[2][0x1000:0x1400])==meta
        assert bytes(m.ram[3][:0x380])==code[:0x380] and bytes(m.ram[3][0x398:0x400])==code[0x398:]
        assert all(bytes(m.ram[i][0x1fe0:0x1ff0])==pages for i in (2,3))
    return m,dict(title_updates=title,select_rows=rows,wrap=wrapped,start_updates=age,
                  actual_PPU_reads_after_Start=m.ppu_reads-reads,scene_hits=hits)


def draw_frame(m,keys,labels,render,donor,records,interrupt=None):
    M.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,NmiDisable=255)
    captures=[]
    cuts=[]
    before_chr=m.chr_latches[:]
    def visit(c):
        if c.pc==render['GiantDraw'] and m.rawtags[1]==3:
            assert m.rawtags[2]==2 and c.x>=16
            x=C.world_x(m)-M.get(m,'ScreenLeft_X_Pos')-256*M.get(m,'ScreenLeft_PageLoc')
            y=M.get(m,'Player_Y_Position')+256*(M.get(m,'Player_Y_HighPos')-1)
            captures.append((c.a,c.x,x,y,bool(M.get(m,'PlayerFacingDir')&2),M.get(m,'Player_SprAttrib'),
                             bool(M.get(m,'ObjectMetasprite')),bytes(m[0x210:0x200+c.x])))
        if interrupt and c.pc==render['GiantFirstPublishDone'] and m.rawtags[1]==3 and not cuts:
            cuts.append(C.vector(c,interrupt))
            assert m.chr_latches==before_chr
    G.run_cpu(m,C.address(m.bundle,'GameLoop'),observe=visit)
    M.consume(m)
    assert len(captures)<=1
    if not captures:
        return None
    pose,tail,x,y,left,attr,visible,native=captures[0]
    if not visible:
        return None
    assert m.chr_latches[6:8]==list(records[pose][:2])
    assert bytes(m[0x210:0x200+tail])==native
    assert all((((native[i+1]&1)<<2)+(native[i+1]>>6)) not in (6,7)
               for i in range(0,len(native),4) if native[i]<240)
    want,valid=G.candidate_parts(donor,m,records[pose],x,y,left,attr,(256-tail)//4)
    got=[bytes(m[i:i+4]) for i in range(0x200+tail,0x300,4) if m[i]<240]
    assert got==want,(pose,x,y,tail,len(got),len(want))
    return dict(pose=pose,actor_tail=tail,parts=len(got),parts_clipped=valid-len(got),world_x=C.world_x(m),native_y=y,cuts=cuts)


def walk(seed,labels,render,donor,records):
    m=M.fork(seed)
    effects=[]
    drawn=0
    hold=0
    jumped=grounded=False
    for age in range(260):
        x=C.world_x(m)
        if x>=264 and not jumped:
            jumped=True
            hold=35
        keys=65+(128 if hold else 0)
        if x>=402 and not grounded:
            if M.get(m,'Player_Y_Position')==176 and M.get(m,'Player_State')==0:
                grounded=True
            else:
                keys=2 if 0<M.get(m,'Player_X_Speed')<128 else 0
        q=draw_frame(m,keys,labels,render,donor,records,{1:'irq',2:'lag_nmi'}.get(age))
        drawn+=bool(q)
        if q and (age<3 or age%40==0 or C.world_x(m)>=480):
            effects.append(q)
        hold=max(0,hold-1)
        m.writes.clear()
        m.ram_writes.clear()
        m.ppu_log.clear()
        if C.world_x(m)>=482 and M.get(m,'Player_Y_Position')==176:
            break
    assert grounded and C.world_x(m)>=482 and M.get(m,'NumberofLives')==2
    assert drawn>220 and sum(bool(x['cuts']) for x in effects)==2
    return dict(updates=age+1,drawn=drawn,world_x=C.world_x(m),witnesses=effects)


def retire(seed,labels,cookie):
    m=M.fork(seed)
    assert all(bytes(m.ram[i][0x1fe0:0x1ff0])==cookie for i in (2,3))
    # Seed only the native terminal GameOver mode. Its own screen/Start
    # routines carry the same live RAM back through title and selection.
    M.put(m,OperMode=3,OperMode_Task=0,NumberofLives=255)
    events=[]
    for i in range(220):
        _,seen=frame(m,16 if i%20==10 else 0,labels)
        events+=seen
        if M.get(m,'CrossoverMenuState')==2:
            break
    else:
        raise AssertionError('Native GameOver did not return to selection')
    assert labels['GiantSceneRetire'] in events and all(m.ram[i][0x1fe0]==0 for i in (2,3)),events
    assert not any(p in G.ART for p in m.chr_latches[6:8]),m.chr_latches
    frame(m,0,labels)
    for _ in range(12):
        if M.get(m,'SelectedCharacter')==41:
            break
        frame(m,32,labels)
        frame(m,0,labels)
    else:
        raise AssertionError('Mini not reachable after Giant GameOver')
    frame(m,16,labels)
    for age in range(600):
        if (M.get(m,'OperMode'),M.get(m,'OperMode_Task'),M.get(m,'GameEngineSubroutine'))==(1,3,8):
            break
        frame(m,0,labels)
    else:
        raise AssertionError('Mini did not reach its own stage after Giant')
    raw=m.bundle['raw']
    assert bytes(m.ram[3][:5120])==b''.join(P.chr_page(raw,p) for p in range(962,967))
    assert all(m.ram[i][0x1fe1]==41 for i in (2,3))
    return dict(native_gameover_to_menu_updates=i+1,retire_hits=events,Mini_entrance_updates=age,
                final_C2_C3_cookies=[bytes(m.ram[i][0x1fe0:0x1ff0]).hex() for i in (2,3)])


def ordinary(old,new,labels,body):
    rows=[]
    for n in range(9):
        x,p=select_and_start(old,labels,b'',b'',b'',n)
        z,q=select_and_start(new,labels,b'',b'',b'',n)
        assert p['select_rows']==q['select_rows'],(n,p,q)
        for name in ('MarioVariant','SelectedCharacter','PlayerStatus','NumberofLives'):
            assert M.get(x,name)==M.get(z,name),(n,name)
        deltas=[]
        for key in (0,1,129,0):
            a,b=[C.play(m,body,key) for m in (x,z)]
            assert a['AXYP']==b['AXYP'] and a['box']==b['box'],(n,a,b)
            C.compare_memory(x,z)
            deltas.append(b['cycles']-a['cycles'])
            M.consume(x)
            M.consume(z)
        if n==8:
            assert deltas==[0]*4,deltas
        rows.append(dict(selects=n,raw=M.get(z,'SelectedCharacter'),cycles=deltas))
    return rows


def audio(base,old,new,rows):
    pair=[M.fresh(b) for b in (old,new)]
    verified=0
    touched=set(map(tuple,rows))
    maximum=0
    for mode,index,tag,hi in Rr.audio_rows(base):
        if (mode,index) not in touched and tag!=0xda:
            continue
        for offset in range(256):
            logical=0x80+index%32 if mode=='lower' else 0xa0+index
            bank=index//32 if mode=='lower' else 0
            (a,ac,_),(b,bc,_)=[Rr.call_audio(m,logical,offset,bank,0x21+(index%2)*0x40) for m in pair]
            assert a==b and a[4]==Rr.native_slice(base['raw'],tag&127,256*hi+offset,1)[0],(mode,index,offset,a,b)
            maximum=max(maximum,bc-ac)
            verified+=1
            for m in pair:
                m.writes.clear()
                m.ram_writes.clear()
    return dict(actual_reader_comparisons=verified,largest_reader_cycle_delta=maximum)


def ownership_guards(seed,failed,labels,render,donor,records):
    for bank in (2,3):
        for byte in range(16):
            m=M.fork(seed)
            m.ram[bank][0x1fe0+byte]^=1
            assert draw_frame(m,0,labels,render,donor,records) is None,(bank,byte)
    assert draw_frame(failed,0,labels,render,donor,records) is None
    return dict(poisoned_header_bytes=32,failed_cold_blocks_RAM3_draw=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(exist_ok=True)
    resident_proof=json.loads(G.RESIDENT.read_text())
    base,resident=current_images(resident_proof)
    donor,art,records,atlas_cookie=G.atlas(C.DONOR.read_bytes())
    render,render_labels=G.assemble(args.output,resident,atlas_cookie)
    render=render.ljust(1024,b'\xff')
    meta=(atlas_cookie+b''.join(records)).ljust(1024,b'\xff')
    old,storage=G.media(resident,art,meta,render)
    previous=json.loads(RENDER.read_text())
    assert G.digest(old['raw'])==previous['memory_only_art_SHA256']
    cookie=bytes((0xa7,0,9,2))+hashlib.sha256(meta+render+SOURCE.read_bytes()).digest()[:8]+bytes((2,1,1,0xd0))
    code,draw,labels=assemble(args.output,old,cookie)
    render=render[:0x200]+draw+render[0x280:]
    art_image,storage=G.media(resident,art,meta,render)
    new,patches,rows=compose(base,art_image,code,labels)
    draw_at=P.CHR_START+G.CODE*1024+0x200
    draw_before=old['raw'][draw_at:draw_at+len(draw)]
    assert draw_before==bytes([255])*len(draw)
    patches.append(dict(physical_CHR=G.CODE,page_offset=0x200,file_offset=draw_at,
                        old_hex=draw_before.hex(),new_hex=draw.hex()))
    replay=bytearray(old['raw'])
    for patch in patches:
        pos=patch['file_offset']
        pre,post=(bytes.fromhex(patch[k]) for k in ('old_hex','new_hex'))
        assert replay[pos:pos+len(pre)]==pre and len(pre)==len(post)
        replay[pos:pos+len(post)]=post
    assert replay==new['raw']
    checks=ammo(old,new)
    seed,selection=select_and_start(new,labels,cookie,meta,render)
    print('Giant menu and native Start',selection,flush=True)
    route=walk(seed,labels,render_labels,donor,records)
    print('Genuine selected draw route',route,flush=True)
    retired=retire(seed,labels,cookie)
    print('Genuine scene retirement',retired,flush=True)
    foreign=ordinary(old,new,labels,resident_proof['storage']['symbols'])
    reads=audio(base,old,new,rows)
    failed,fail_scene=select_and_start(new,labels,cookie,meta,render,corrupt=True)
    guards=ownership_guards(seed,failed,labels,render_labels,donor,records)
    audio_nmis=campaign((old,new),dict(GiantRogueMux=labels['GiantAudioMux']))
    out=dict(passed=True,ROM_written=False,source_CPU_only=True,provisional_CHR=True,
             parent_SHA256=G.digest(old['raw']),memory_only_SHA256=G.digest(new['raw']),patches=patches,
             symbols=labels,render_symbols=render_labels,physical_carriers=storage['physical_candidate_pages'],
             canonical_Rogue_rows=rows,cheat_lookup_cases=checks,selection=selection,route=route,
             retirement=retired,foreign=foreign,Rogue_reader=reads,Rogue_ordered_NMI=audio_nmis,
             ownership_guards=guards,rejected_cold_readback=fail_scene,
             limits=['GameOver entry is seeded at its native terminal mode; actual screen/Start/title and alternate selection run from there',
                     'Animation uses host state projected onto original donor poses. Full source timers, interactions and stage completion remain open',
                     'CHR carriers remain provisional; no global publisher grant or Mesen test'],
             bindings={str(p):C.sha(p) for p in (Path(__file__),SOURCE,RENDER,G.SOURCE,G.RESIDENT,G.ROGUE_NMI,C.HOST,C.DONOR)})
    (args.output/'proof-v2.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(passed=True,canonical_Rogue_rows=len(rows),audio=reads,guards=guards,
                          ordered_Rogue_NMIs=sum(x['ticks'] for x in audio_nmis),foreign=len(foreign),
                          memory_only_SHA256=out['memory_only_SHA256']),sort_keys=True),flush=True)


if __name__=='__main__':
    main()
