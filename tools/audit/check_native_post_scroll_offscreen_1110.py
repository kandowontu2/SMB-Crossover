"""Qualify shared offscreen composition and the live scroll-to-player handoff."""

import argparse
from collections import Counter, defaultdict
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_native_platform_box_reuse_1110_v1 as PlatformBox
import check_native_relative_offscreen_1110 as Relative
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork
from compose_mini_frame_budget_1108 import check_full_cpu
from prepare_mini_side_alias_1108 import compare_memory


P,N,R = Relative.P,Relative.N,Relative.R
BASE = R/'build/mini-box-transport-native-1110/candidate.nes'
PIN = '03c0cfe6d4562f6b7970199ce2d6ffa6f2f0f905a8cb8425945add6fcb71585d'
SOURCE = R/'tools/reference/native_post_scroll_offscreen_1110_v1.s'
SPANS = (('PLAYER_SITE',1,0xa13f,0xa142),('COMBINE',126,0x8b08,0x8b1a),
         ('Y_AND_POST_SCROLL',126,0x8b73,0x8bdb))
OLD = ('20ce8a','0a0a0a0a0503850368a8a50399a005a60d60',
       '8607b5a4c901f04ba001b9c48b38f5bd850aa901f5a43047d01aa9208509a9048508a50ac920b00c'
       '4a4a4ac001b0026904aa1003bec28bbdb88ba607c900d0038810c760ea00080c0e0f07030100040004'
       'ff00a000a9ff38f5bd850a4c8d8bbec18b4caa8beaeaea')
PLAYER, COMBINE, Y_ENTRY, END = 0x8ace,0x8afa,0x8b73,0x8bdb


def offset(bank,pc):
    return 16+8192*bank+(pc&8191)


def read(raw,bank,pc,expected):
    data = bytes.fromhex(expected)
    at = offset(bank,pc)
    assert raw[at:at+len(data)]==data,(bank,hex(pc))


def census(raw):
    source = (R/'src/common.s').read_text()
    assert source.count('GetYOffscreenBits')==2 and source.count('YOffscreenBitsData')==2
    assert source.count('DefaultYOnscreenOfs')==3 and source.count('HighPosUnitData')==2
    assert 'jsr GetYOffscreenBits\n    asl' in source
    player = (R/'src/player.s').read_text()
    assert player.count('jsr VvScrollBridge')==1 and 'jsr GetPlayerOffscreenBits' in player
    assert 'jsr GetXOffscreenBits' in player and 'sta R0                    ;save them here' in player
    read(raw,1,0xa13c,'2065ed20ce8a208c8a')
    read(raw,127,0xed65,'8d6a01a9868d6c01a9a28d6d01a9cd4c5a01')
    read(raw,77,0xa286,'2000a09064')
    read(raw,77,0xa000,'ad0260c912f00218603860')
    read(raw,77,0xa2ef,'8d6a01a9d48d6c01a9a98d6d01a9814c5a01')
    read(raw,1,0xaa3f,'a200201a8b8503a0000ab007c8a5032920f01c')
    read(raw,1,0xaa6e,'a9008d650560')
    read(raw,126,0x8b05,'20738b')

    code = raw[16:16+128*8192]
    direct = [(i//8192,i&8191,int.from_bytes(code[i+1:i+3],'little'))
              for i in range(len(code)-2) if code[i] in (0x20,0x4c,0x6c) and
              0x8b08<=int.from_bytes(code[i+1:i+3],'little')<END]
    # X's public entry and internal fixed geometry are left exactly in place.
    private = [site for site in direct if site[2]<0x8b1a or site[2]>=Y_ENTRY]
    false = [(6,0x125b,0x8bc9),(40,0x712,0x8b7d),(55,0x15ad,0x8bce),(69,0xd30,0x8bae)]
    old_code = [(126,0xb05,Y_ENTRY),(126,0xbcf,0x8b8d),(126,0xbd5,0x8baa)]
    assert private==false+old_code,private
    read(raw,6,0xb259,'bd9d6cc98b')        # Two adjacent operands, not JMP indirect.
    read(raw,69,0xad2e,'ad0720ae8b5d')    # PPUDATA load followed by ordinary LDX.
    music = R/'src/expanded_music.inc'
    for bank,index,at,n in ((40,'01',0x712,3),(55,'10',0x15ad,3)):
        stream = R/f'audio/expanded/playlist-{index}.bin'
        assert f'XG_MUSIC_{bank:02X}"\n.incbin "audio/expanded/{stream.name}"' in music.read_text()
        data = stream.read_bytes()
        assert len(data)>at+n and raw[offset(bank,0xa000):offset(bank,0xa000)+len(data)]==data
    tables = {0x8bb8:0x8baa,0x8bc1:0x8bd2,0x8bc2:0x8ba7,0x8bc4:0x8b7d}
    for addr,pc in tables.items():
        word = addr.to_bytes(2,'little')
        candidates = [i for i in range(len(code)-2) if code[i] in (0xb9,0xbd,0xbe,0xbc,0xac,0xad,0xae)
                      and code[i+1:i+3]==word]
        assert candidates==[offset(126,pc)-16],(hex(addr),candidates)
    for addr in range(Y_ENTRY,END):
        lo,hi = addr&255,addr>>8
        assert code.count(bytes((0xa9,lo,0x8d,0x6c,1,0xa9,hi,0x8d,0x6d,1)))==0,hex(addr)
    return dict(private_direct_JSR=[126,0x8b05,Y_ENTRY],old_internal_JMPs=old_code[1:],
                opcode_shaped_data_or_operands=false,private_table_loads=tables,
                one_rebound_typed_caller=[1,0xa13f],producer=[1,0xaa41,0xaa44,0xaa50,0xaa6e])


def compose(raw,output):
    assert P.sha(raw)==PIN
    callers = census(raw)
    with tempfile.TemporaryDirectory(prefix='link-',dir=output) as dirname:
        work = Path(dirname)
        cfg,obj,binary,lbl = (work/f'offscreen.{ext}' for ext in ('cfg','o','bin','lbl'))
        cfg.write_text('MEMORY {\n'+''.join(f'{name}: start=${lo:04x},size=${hi-lo:x},file=%O;\n'
            for name,_,lo,hi in SPANS)+'}\nSEGMENTS {\n'+''.join(f'{name}: load={name},type=ro;\n'
            for name,*_ in SPANS)+'}\n',encoding='utf-8')
        cc = R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary,'-Ln',lbl],check=True)
        labels = {line.split()[2][1:]:int(line.split()[1],16) for line in lbl.read_text().splitlines()}
        data = binary.read_bytes()
    assert labels['GetYOffscreenBitsHigh']==Y_ENTRY and labels['CombineOffscreen']==0x8b08
    assert END-labels['PostScrollPlayerOffscreen']>=18,labels
    patches = []
    for (name,bank,lo,hi),old in zip(SPANS,OLD,strict=True):
        read(raw,bank,lo,old)
        n = hi-lo
        assert len(bytes.fromhex(old))==n
        patches.append(dict(role=name,physical_PRG=bank,CPU_half_open=[lo,hi],
                            file_offset=offset(bank,lo),old_hex=old,new_hex=data[:n].hex()))
        data = data[n:]
    assert not data
    return install(raw,patches),patches,labels,callers


def offscreen_leaves(before,after):
    cpus = []
    for image in (before,after):
        mem = bytearray(65536)
        start = offset(126,0x8000)
        mem[0x8000:0xa000] = image[start:start+8192]
        cpus.append(N.NesMPU(memory=mem))
    costs = Counter()
    geometry = ((0,0,255,0,112,0),(43,0,42,1,112,0),(43,0,42,1,42,0),
                (43,0,42,1,42,1),(255,255,254,0,16,0),(255,255,16,127,20,128),
                (14,128,200,9,37,127),(210,127,100,128,242,128))

    def check(pc,index,dest,page,ypos,xfields,flags):
        row = []
        left,lpage,right,rpage,xpos,xpage = xfields
        for cpu in cpus:
            mem = cpu.memory
            mem[:11] = bytes.fromhex('6542328657766897a65227')
            mem[0x0d] = 6
            mem[0x71d:0x721] = bytes((lpage,rpage,left,right))
            mem[0xa4+index],mem[0xbd+index] = page,ypos
            mem[0x75+index],mem[0x5c+index] = xpos,xpage
            mem[0x5a0:0x6a0] = b'\xf2'*256
            cpu.pc,cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp = pc,0x61,index,dest,flags,248
            cpu.processorCycles = 0
            cpu.stPushWord(0x5aff)
            run(cpu,lambda c:(c.pc,c.sp)==(0x5b00,248))
            row.append((registers(cpu),bytes(mem[:11]),mem[0x5a0+(dest if pc==COMBINE else 0)],cpu.processorCycles))
        a,b = row
        assert a[:-1]==b[:-1],(hex(pc),index,dest,page,ypos,xfields,flags,a,b)
        costs[hex(pc),a[-1]-b[-1]] += 1

    for page,ypos in product(range(256),repeat=2):
        xfields = geometry[(page+ypos)%len(geometry)]
        p = (0x20,0x65,0xad,0x21)[ypos&3]
        check(PLAYER,0,0,page,ypos,xfields,p)
        check(COMBINE,(page+ypos)%23,(page*3+ypos)%13,page,ypos,xfields,p)
    return dict(cases=sum(costs.values()),savings_histogram=[[*key,n] for key,n in sorted(costs.items())])


def scroll_cases(before,after,labels):
    pair = [N.fresh(P.bundle(im)) for im in (before,after)]
    costs = defaultdict(list)
    owner_count = Counter()
    # Each raw owner gets the genuine nested bridge, its own scroll policy,
    # independent edges, center and both clamps. A13F is the sole new ingress.
    geometry = ((0,0,255,0,112,0,164,1,0),(0,0,255,0,0,0,176,1,0),
                (0,0,255,0,248,0,224,1,0),(250,255,249,0,27,0,32,2,0),
                (12,127,200,9,33,128,245,0,0),(43,0,42,1,112,0,166,1,2))
    for owner,engine,geom,p in product(range(42),(5,7,8,9),geometry,(0x21,0x65)):
        left,lpage,right,rpage,x,xpage,y,ypage,force = geom
        buses = [slim_fork(m) for m in pair]
        result = []
        for m in buses:
            m.raw_page(1,129)
            N.put(m,CurrentBank=129,SelectedCharacter=owner,GameEngineSubroutine=engine,
                  ScreenLeft_X_Pos=left,ScreenLeft_PageLoc=lpage,
                  ScreenRight_X_Pos=right,ScreenRight_PageLoc=rpage,
                  Player_X_Position=x,Player_PageLoc=xpage,Player_Y_Position=y,
                  Player_Y_HighPos=ypage,Player_X_Scroll=force,Player_Pos_ForScroll=112,
                  Left_Right_Buttons=1,NmiDisable=255)
            m[3] = 0xe7
            c = N.NesMPU(memory=m,pc=0xa13c)
            c.sp,c.a,c.x,c.y,c.p = 226,0x4c,0x81,0x19,p
            publish,entries = [],set()

            def visit(z):
                if z.pc==0xa13f:
                    publish.append((z.x,m[3]))
                if z.pc in (0xaa44,labels['PostScrollPlayerOffscreen'],PLAYER):
                    entries.add(z.pc)

            run(c,lambda z:z.pc==0xa142,visit)
            assert c.sp==226 and len(publish)==1
            result.append((registers(c),live_stack(c),publish[0],entries,c.processorCycles))
        a,b = result
        assert a[:3]==b[:3],(owner,engine,geom,p,a,b)
        compare_memory(*buses)
        assert buses[0][0x15a:0x17b]==buses[1][0x15a:0x17b]
        assert PLAYER in a[3] and labels['PostScrollPlayerOffscreen'] in b[3]
        hot = owner!=18 and a[2][1]==0
        if hot:
            assert a[2][0]==0 and 0xaa44 in a[3] and PLAYER not in b[3],(owner,geom,a,b)
        else:
            assert PLAYER in b[3],(owner,geom,a,b)
        lane = 'hot' if hot else 'Vic_full' if owner==18 else 'clamp_or_edge_full'
        costs[lane].append(a[-1]-b[-1])
        owner_count[owner,hot] += 1
    assert all(owner_count[owner,True] for owner in range(42) if owner!=18)
    return {lane:dict(cases=len(values),cycles_saved=[min(values),max(values)]) for lane,values in costs.items()}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and not (out/'proof.json').exists()
    out.mkdir(exist_ok=True)
    raw = BASE.read_bytes()
    final,patches,labels,callers = compose(raw,out)
    leaf = offscreen_leaves(raw,final)
    print(f"Public offscreen parity passed for {leaf['cases']} geometry cases.",flush=True)
    handoff = scroll_cases(raw,final,labels)
    core = check_full_cpu(raw,final,{})
    loop = PlatformBox.whole(raw,final)
    refs = (Path(__file__),SOURCE,BASE,R/'src/common.s',R/'src/player.s',R/'src/vic_adapter.s',
            R/'src/expanded.s',R/'src/expanded_music.inc',R/'audio/expanded/playlist-01.bin',
            R/'audio/expanded/playlist-10.bin',R/'tools/reference/mini_shared_offscreen_1110_v1.s')
    q = dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(final),
             patches=patches,labels=labels,caller_census=callers,public_offscreen=leaf,
             scroll_to_offscreen=handoff,whole_GameCore=core,whole_GameLoop=loop,
             bindings={p.resolve().relative_to(R).as_posix():P.sha(p.read_bytes()) for p in refs})
    (out/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:q[k] for k in ('expected_memory_only_SHA256','labels','scroll_to_offscreen',
                                      'whole_GameCore','whole_GameLoop')}),flush=True)


if __name__=='__main__':
    main()
