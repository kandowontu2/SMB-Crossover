"""Exercise the Giant atlas through the native buffered copier and live OAM."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

import check_mega_giant_compound_1110 as C
import check_mega_giant_ppu_mapping_1110_v1 as P
from check_mega_giant_resident_rogue_nmi_1110 import current_images
from audit_mega_giant_chr_candidates_1110_v1 import MAP_BANKS, compiled_readers, prg_at, table


R,M=C.R,C.M
RESIDENT=R/'build/mega-giant-mario-resident-1110/proof-v2.json'
ROGUE_NMI=RESIDENT.with_name('rogue-nmi-v2.json')
OLD=R/'build/mega-giant-mario-host-1110'
SOURCE=R/'tools/reference/mega_giant_mario_render_1110.s'
WORKER=R/'build/mini-mario-owner-1103-v15/common-v15.bin'
ART=tuple(range(168,212,2))
ATLAS,CODE=212,214
FIRST_WINDOW=6


def digest(data):
    return hashlib.sha256(data).hexdigest()


def atlas(donor):
    cpu=bytearray(65536)
    cpu[0x8000:]=donor[16:32784]
    art=donor[32784:]
    source=art[8*1024:30*1024]
    assert source==(OLD/'giant-render-source-pages.chr').read_bytes()
    masks=[]
    for pose,(top,bottom) in enumerate(zip(cpu[0xee07:0xee14],cpu[0xee14:0xee21],strict=True)):
        mask=[]
        for page in (top,bottom):
            data=art[page*1024:(page+1)*1024]
            mask.extend(sum(bool(any(data[(8*row+i)*32:(8*row+i+1)*32]))<<i for i in range(8)) for row in range(4))
        assert 43<=sum(x.bit_count() for x in mask)<=62
        masks.append(bytes((ART[top-8],ART[bottom-8],*mask)))
    body=b''.join(masks)
    cookie=bytes((0xa7,0,9,1))+hashlib.sha256(body+source).digest()[:12]
    return cpu,source,masks,cookie


def assemble(out,b,cookie):
    globals_=('SelectedCharacter','MarioVariant','OperMode','GameEngineSubroutine','CurrentBankC',
              'GuestOamRotationActive','ObjectMetasprite','R0','R1','R2','R3','R4','R6','R7',
              'Player_X_Position','ScreenLeft_X_Pos',
              'Player_PageLoc','ScreenLeft_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_SprAttrib',
              'PlayerFacingDir','X5SetPhysicalChr')
    defs=''.join(f'{n}=${C.address(b,n):04x}\n' for n in globals_)
    defs+='.define GIANT_ATLAS_SIGNATURE '+','.join(f'${v:02x}' for v in cookie)+'\n'
    with tempfile.TemporaryDirectory(prefix='draw-',dir=out) as p:
        s,g,o,z,l=(Path(p)/f'giant.{ext}' for ext in ('s','cfg','o','bin','lbl'))
        s.write_text(defs+SOURCE.read_text())
        g.write_text('MEMORY { CODE:start=$a000,size=$400,file=%O; } SEGMENTS { GIANT_RENDER:load=CODE,type=ro; }\n')
        cc=R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',s,'-o',o],check=True)
        s.unlink()
        subprocess.run([cc/'ld65.exe','-C',g,o,'-o',z,'-Ln',l],check=True)
        labels={row.split()[2][1:]:int(row.split()[1],16) for row in l.read_text().splitlines()}
        return z.read_bytes(),labels


def media(b,art,meta,code):
    raw=bytearray(b['raw'])
    pages=(*ART,ATLAS,CODE)
    map_at,legacy=table(b,'ChrPhysicalMap',256)
    assert not set(pages)&set(legacy)
    assert all(raw[prg_at(bank,0xe36):prg_at(bank,0xe36)+256]==legacy for bank in MAP_BANKS)
    readers=compiled_readers(b)
    assert all(not set(pages)&set(q['actual_mmc5_outputs']) for q in readers.values())
    blank=P.chr_page(raw,2)
    source=[art[i:i+1024] for i in range(0,len(art),1024)]+[meta,code]
    patches=[]
    for p,data in zip(pages,source,strict=True):
        assert len(data)==1024 and P.chr_page(raw,p)==blank
        at=P.CHR_START+p*1024
        raw[at:at+1024]=data
        patches.append(dict(page=p,file_offset=at,old_SHA256=digest(blank),new_SHA256=digest(data)))
    assert raw[:P.CHR_START]==b['raw'][:P.CHR_START]
    return C.bundle(bytes(raw)),dict(prg_unchanged=True,legacy_map_file_offset=map_at,compiled_exclusions=readers,
                    physical_candidate_pages=patches,all_publisher_lease=False)


def run_cpu(m,pc,a=0,x=0,y=0,p=0x31,observe=None,limit=100000):
    c=M.NesMPU(memory=m,pc=pc)
    c.sp,c.a,c.x,c.y,c.p=252,a,x,y,p
    c.stPushWord(C.STOP-1)
    for _ in range(limit):
        if c.pc==C.STOP:
            break
        if observe:
            observe(c)
        assert m[c.pc],(hex(pc),hex(c.pc),m.rawtags)
        c.step()
    else:
        raise AssertionError(('CPU call bound',hex(pc),hex(c.pc)))
    assert c.sp==252
    return c


def load_rows(m,code,meta,*,corrupt=False):
    assert m.bundle['raw'][prg_at(123,0xf40):prg_at(123,0xf40)+WORKER.stat().st_size]==WORKER.read_bytes()
    assert all(m.ram[i][0x1fe0]!=0xa7 for i in (2,3))
    owner=M.get(m,'SelectedCharacter'),M.get(m,'MarioVariant')
    assert owner==(0,9)
    entry=list(m.rawtags)
    saved={n:M.get(m,n) for n in ('DisableScreenFlag','Mirror_PPUMASK')}
    buf=0x500
    old=bytes(m[buf:buf+8])
    m[buf:buf+8]=bytes((2,1,1,0xd0,CODE,0,ATLAS,0))
    M.put(m,R3=buf&255,R4=buf>>8,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255)
    m[0x2001]=0
    M.put(m,CurrentBank=251)
    m[0x5115]=251
    if corrupt:
        m.corrupt_at=(2,0x1000+15)
    reads=m.ppu_reads
    c=run_cpu(m,0xaf40,p=0x35)
    count=m.ppu_reads-reads
    m.corrupt_at=None
    m[buf:buf+8]=old
    M.put(m,CurrentBank=entry[1],CurrentBankC=entry[2],ReloadCHRBank=1,**saved)
    m[0x5115],m[0x5116]=entry[1:3]
    assert bool(c.p&1)==(not corrupt)
    if not corrupt:
        assert count==4100 and bytes(m.ram[2][0x1000:0x1400])==meta and bytes(m.ram[3][:1024])==code
    M.consume(m)
    return dict(readback=bool(c.p&1),actual_buffered_reads=count,CPU=c.processorCycles)


def draw(m,labels,pose,cursor,cut=None):
    before=m.rawtags[:]
    M.put(m,CurrentBankC=2,NmiDisable=255)
    m[0x5116]=2
    pc=labels['GiantDraw']
    m[0x16a],m[0x16c],m[0x16d]=pose,pc&255,pc>>8
    cuts=[]
    def observe(c):
        if cut and not cuts and c.pc==labels['GiantFirstPublishDone'] and m.rawtags[1]==3:
            latches=m.chr_latches[:]
            cuts.append(C.vector(c,cut))
            assert m.chr_latches==latches
    c=run_cpu(m,0x15a,a=3,x=cursor,observe=observe)
    assert m.rawtags[1]==before[1] and bool(cuts)==bool(cut)
    M.put(m,CurrentBankC=before[2])
    m[0x5116]=before[2]
    assert m.rawtags==before
    return c,cuts


def candidate_parts(donor,m,record,x,y,left,attr,cap):
    donor_oam=P.donor_oam(donor,x&255,y&255,left,0,attr)
    records=[]
    for i,(old_y,old_tile,old_attr,old_x) in enumerate(donor_oam):
        col,row=i%8,i//8
        assert old_tile==2*(i%32)+1
        if not record[2+row]&(1<<col):
            continue
        py=y-96+16*row
        px=x+(32-8*col if left else -24+8*col)
        assert (old_y,old_x)==(py&255,px&255)
        if not(0<=px<=255 and 0<=py<240):
            continue
        tile=0x81+2*i
        src_page=record[int(i>=32)]
        pattern=P.chr_page(m.bundle['raw'],src_page)[(i%32)*32:(i%32+1)*32]
        assert P.sprite_pair(m,tile)==pattern and any(pattern)
        records.append(bytes((py,tile,old_attr,px)))
    return records[:cap],len(records)


def game_frame(m,keys):
    M.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,NmiDisable=255)
    world=[]
    def observe(c):
        if C.tag(m,c.pc)==132 and c.pc==0xa24b:
            world.append(m[0x100+((c.sp+1)&255)])
    run_cpu(m,C.address(m.bundle,'GameLoop'),observe=observe)
    assert len(world)==1 and world[0]>=16 and not world[0]&3,world
    return world[0]


def check_frame(m,donor,records,labels,pose,tail,cut=None):
    x=C.world_x(m)-M.get(m,'ScreenLeft_X_Pos')-256*M.get(m,'ScreenLeft_PageLoc')
    y=M.get(m,'Player_Y_Position')+256*(M.get(m,'Player_Y_HighPos')-1)
    left=bool(M.get(m,'PlayerFacingDir')&2)
    attr=M.get(m,'Player_SprAttrib')
    native=bytes(m[0x210:0x200+tail])
    visible=[tuple(native[i:i+4]) for i in range(0,len(native),4) if native[i]<240]
    patterns=[P.sprite_pair(m,t) for _,t,_,_ in visible]
    latches=m.chr_latches[:]
    c,cuts=draw(m,labels,pose,tail,cut)
    assert c.p&1 and m.chr_latches==latches
    M.consume(m)
    assert m.chr_latches[6:8]==list(records[pose][:2]),(pose,m.chr_latches)
    assert m.chr_latches[:6]==latches[:6] and m.chr_latches[8:]==latches[8:]
    assert bytes(m[0x210:0x200+tail])==native
    assert [P.sprite_pair(m,t) for _,t,_,_ in visible]==patterns
    assert list(m[0x200:0x210:4])==[248]*4
    wanted,n=candidate_parts(donor,m,records[pose],x,y,left,attr,(256-tail)//4)
    got=[bytes(m[i:i+4]) for i in range(0x200+tail,0x300,4) if m[i]<240]
    assert got==wanted,(pose,x,y,left,tail,len(got),len(wanted))
    return dict(pose=pose,x=x,y=y,left=left,world_tail=tail,parts=len(wanted),capacity_clipped=n-len(wanted),
                foreign_visible=len(visible),draw_CPU=c.processorCycles,cuts=cuts)


def walk(m,donor,records,labels):
    hold=0
    jumped=grounded=False
    conflicts={}
    rows=[]
    old_art=(OLD/'giant-native-even-pages.chr').read_bytes()
    for age in range(230):
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
        tail=game_frame(m,keys)
        for at in range(0x210,0x200+tail,4):
            y,t,_,_=m[at:at+4]
            if y>=240:
                continue
            assert (((t&1)<<2)+(t>>6)) not in (6,7),(age,x,hex(t))
            if not t&1 and 64<=t<128 and t not in conflicts:
                original=P.sprite_pair(m,t)
                slot=(t&0x3f)//2*32
                changed=[p for p in range(22) if old_art[p*1024+slot:p*1024+slot+32]!=original]
                if any(original) and changed:
                    conflicts[t]=dict(tile=t,frame=age,world_x=x,OAM_slot=(at-0x200)//4,
                                      stock_pattern=original.hex(),old_art_rows_that_corrupt=changed)
        if age in (0,40,86,95,96,100,120,126,180,185,199,210,228):
            rows.append(check_frame(m,donor,records,labels,len(rows),tail))
        else:
            M.consume(m)
        hold=max(0,hold-1)
        m.writes.clear()
        m.ram_writes.clear()
        m.ppu_log.clear()
    assert C.world_x(m)>=482 and M.get(m,'NumberofLives')==2 and grounded
    assert 0x70 in conflicts and len(rows)==13
    return rows,list(conflicts.values())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(exist_ok=True)
    proof=json.loads(RESIDENT.read_text())
    _,resident=current_images(proof)
    assert C.sha(C.DONOR)==C.DONOR_PIN
    donor,art,records,cookie=atlas(C.DONOR.read_bytes())
    code,labels=assemble(args.output,resident,cookie)
    code_row=code.ljust(1024,b'\xff')
    meta=(cookie+b''.join(records)).ljust(1024,b'\xff')
    candidate,allocation=media(resident,art,meta,code_row)
    seed,_=C.start_stage(candidate)
    M.put(seed,MarioVariant=9)
    bad=load_rows(M.fork(seed),code_row,meta,corrupt=True)
    cold=load_rows(seed,code_row,meta)
    frames,conflicts=walk(M.fork(seed),donor,records,labels)
    all_poses=[]
    for pose in range(13):
        for left in (1,2):
            m=M.fork(seed)
            tail=game_frame(m,0)
            M.put(m,PlayerFacingDir=left)
            all_poses.append(check_frame(m,donor,records,labels,pose,tail,
                'irq' if pose==0 and left==1 else 'lag_nmi' if pose==0 else None))
    guards=[]
    for i in range(17):
        m=M.fork(seed)
        tail=game_frame(m,0)
        if i<16:
            m.ram[2][0x1000+i]^=1
        else:
            tail=0
        before=bytes(m[0x200:0x300]),m.chr_latches[:]
        c,_=draw(m,labels,0,tail)
        assert not c.p&1 and (bytes(m[0x200:0x300]),m.chr_latches)==before
        guards.append(i)
    # Actual cold Mini loads and executes its original independent carriers.
    ordinary=[C.enter_owner(b,0,8) for b in (resident,candidate)]
    results=[C.play(m,proof['storage']['symbols']) for m in ordinary]
    assert results[0]==results[1]
    C.compare_memory(*ordinary)
    refs=(Path(__file__),SOURCE,RESIDENT,ROGUE_NMI,C.HOST,C.DONOR,WORKER,OLD/'giant-render-source-pages.chr',
          OLD/'giant-native-even-pages.chr',OLD/'ppu-proof.json')
    q=dict(passed=True,source_CPU_only=True,ROM_written=False,parent_SHA256=proof['expected_memory_only_SHA256'],
           memory_only_art_SHA256=digest(candidate['raw']),allocation=allocation,pose_count=13,atlas_bytes=130,
           atlas_cookie_bytes=16,atlas_SHA256=digest(meta),worker_bytes=len(code),worker_SHA256=digest(code_row),
           worker_symbols=labels,actual_banked_cold_copy=cold,readback_failure=bad,live_world_draw_frames=frames,
           old_window1_conflicts=conflicts,all_donor_poses_both_facings=all_poses,stale_or_full_guards=guards,
           actual_cold_Mini_and_next_GameLoop_exact=True,
           limits=['Temporary trusted call into the real $FB:AF40 copier; no Giant scene/menu/retirement hook',
                   'Foreground hook and pose index are supplied by the CPU witness after native DrawAllMetasprites',
                   'Physical carrier exclusions are finite, not a global publication grant',
                   'CHR windows 6/7 checked against live first-pipe OAM; further areas and power/transition states require checks',
                   'Tail capacity and 8-sprite hardware priority preserve native sprites, with possible Giant clipping'],
           bindings={str(p):C.sha(p) for p in refs})
    (args.output/'proof-v2.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(passed=True,worker_bytes=len(code),atlas_bytes=130,conflicts=len(conflicts),
                          live_frames=len(frames),all_poses=len(all_poses),cold_copy=cold),sort_keys=True))


if __name__=='__main__':
    main()
