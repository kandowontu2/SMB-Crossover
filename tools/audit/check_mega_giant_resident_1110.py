"""Qualify a resident Giant worker with byte-complete Rogue audio reads."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

import check_mega_giant_compound_1110 as C
from check_tmnt_render_oa import location


R,M=C.R,C.M
SOURCE=R/'tools/reference/mega_giant_mario_resident_1110.s'
ROGUE=R/'src/rogue_dawn_audio_pages_v3.s'
READER=R/'src/rogue_dawn_audio_reader_v6.s'
PAGES=((90,0xb09e,0xb180),(90,0xb705,0xb744),(90,0xb744,0xb890),(90,0xbc40,0xbd00),
       (97,0xc42c,0xc451),(97,0xc469,0xc480),(93,0xafa7,0xaff3))
OLD_ADAPTER=bytes.fromhex('0848ad0260f039c902f017c91af013c91cf00fc920f00bc909d02cade55f2920f025'
                         '68288d6a01a9448d6c01a9b78d6d01a9bf8d620168684c6101ffffffffff'
                         'ad0a73c902f0db68284cf8bf')
DRIVER=0xc410
DATA_WINDOW=0xda
BODY_CALL=0xb969
VIRTUAL_ROWS=(80,81,87,88,92)
OLD_MAP=bytes.fromhex('8d45018d1551a000b1e88d5170a9be8d45018d15516038e9a0aabd5fbe85e9bd3fbe4c2cc4')


def at(bank,pc):
    return 16+bank*8192+(pc&8191)


def native_slice(raw,bank,pc,n):
    start=at(bank,pc)
    return raw[start:start+n]


def checksum(raw):
    return hashlib.sha256(raw).hexdigest()


def source_pages(b):
    text=ROGUE.read_text()
    payload=[]
    for index in range(63,80):
        row=re.search(rf'^RdaPage{index}:\s*(.*?)^(?:RdaPage|\.segment)',text,re.M|re.S)[1]
        page=bytes(int(x,16) for x in re.findall(r'\$([0-9a-fA-F]{2})\b',row))
        assert len(page)==256 and page==native_slice(b['raw'],90,0xaf00+(index-63)*256,256),index
        payload.append(page)
    read=READER.read_text()
    assert '.res $77-(*-RdaDriverStart),$ff' in read
    assert C.address(b,'RdaDriverStart')==0xc409 and C.address(b,'RdaUpperStart')==0xc480
    assert C.address(b,'RdaReadRomValue')==DRIVER
    assert [C.address(b,n) for n in ('RdaLowerBankTable','RdaLowerHighTable',
          'RdaUpperRawBankTable','RdaUpperRawHighTable')]==[0xbba7,0xbc67,0xbe3f,0xbe5f]
    return dict(authored_pages=17,exact_bytes=17*256,SHA256=checksum(b''.join(payload)),
                consumer='C97:RdaReadRomValue, lower and upper raw page maps in physical62')


def assemble(out,b):
    crush=C.CRUSH.read_text()
    names=[n for line in crush.splitlines() if line.startswith('.import')
           for n in line.split(' ',1)[1].split(', ')]
    names+=['DisableCollisionDet','SwimmingFlag','Player_X_Speed','PlayerBGCollision']
    defs=''.join(f'{n}=${C.address(b,n):04x}\n' for n in sorted(set(names)))
    route=C.ROUTE.read_text()
    fallback='Legacy:\n    cmp #2\n    jmp $afec\nNative:\n    jmp $afee'
    assert route.count(fallback)==1
    route=route.replace(fallback,'Legacy:\nNative:\n    jmp GiantResidentLegacy')
    src='\n'.join((defs,route,re.sub(r'^\.import(?:zp)? .*\n','',crush,flags=re.M),
                   C.SOURCE.read_text(),SOURCE.read_text()))
    names=('SIDE','VIEW','BODY','CRUSH','MAP','MUX','ADAPTER')
    layout=''.join(f'{n}:start=${pc:04x},size=${end-pc:x},file=%O,fill=yes,fillval=${255 if bank==97 else 0:02x};'
                   for n,(bank,pc,end) in zip(names,PAGES,strict=True))
    cfg='MEMORY{'+layout+'} SEGMENTS{GIANT_ROUTE:load=SIDE,type=ro;GIANT_AUDIO_VIEW:load=VIEW,type=ro;'
    cfg+='GIANT_RESIDENT:load=BODY,type=ro;GIANT:load=BODY,type=ro;GIANT_CRUSH:load=CRUSH,type=ro;'
    cfg+='GIANT_AUDIO_MAP:load=MAP,type=ro;GIANT_AUDIO_MUX:load=MUX,type=ro;GIANT_ADAPTER:load=ADAPTER,type=ro;}'
    with tempfile.TemporaryDirectory(prefix='asm-',dir=out) as tmp:
        paths=[Path(tmp)/f'giant.{ext}' for ext in ('s','cfg','o','bin','lbl')]
        source,config,obj,binary,labels=paths
        source.write_text(src)
        config.write_text(cfg)
        cc=R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',source,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',config,obj,'-o',binary,'-Ln',labels],check=True)
        symbols={row.split()[2][1:]:int(row.split()[1],16) for row in labels.read_text().splitlines()}
        data=binary.read_bytes()
    assert len(data)==sum(end-pc for _,pc,end in PAGES)
    assert symbols['GiantResidentEntry']==0xb744 and symbols['GiantHostAdapter']==0xafa7
    return data,symbols


def compose(raw,data,labels):
    out=bytearray(raw)
    patches=[]
    def add(bank,pc,old,new):
        i=at(bank,pc)
        assert old==raw[i:i+len(old)] and len(new)==len(old),(bank,hex(pc))
        out[i:i+len(new)]=new
        patches.append(dict(physical_PRG=bank,PC=pc,file_offset=i,old_hex=old.hex(),new_hex=new.hex()))
    step=0
    for bank,pc,end in PAGES:
        n=end-pc
        old=OLD_ADAPTER if bank==93 else OLD_MAP if pc==0xc42c else bytes([255 if bank==97 else 0])*n
        add(bank,pc,old,data[step:step+n])
        step+=n
    assert native_slice(raw,97,0xc412,4)==bytes.fromhex('c9a0b02c')
    add(97,0xc415,bytes((0x2c,)),bytes((labels['GiantRogueUpper']-0xc416,)))
    for row in VIRTUAL_ROWS:
        add(62,0xbba7+row,bytes((DATA_WINDOW,)),bytes((DATA_WINDOW&127,)))
    packet=bytes.fromhex('a9a78d6c01a9af8d6d01a9dd4c5a01')
    assert native_slice(raw,1,BODY_CALL,len(packet))==packet
    prg=raw[16:16+128*8192]
    assert prg.count(packet[:10])==1 and bytes.fromhex('20a7af') not in prg and bytes.fromhex('4ca7af') not in prg
    return bytes(out),patches


def call_audio(m,logical,offset,bank,flags,cut=None):
    M.put(m,CurrentBank=190,CurrentBankC=225,NmiDisable=255)
    m.raw_page(1,190)
    m.raw_page(2,225)
    m[0xe8],m[0xe9],m[0x23]=offset,logical,bank
    c=M.NesMPU(memory=m,pc=DRIVER)
    c.sp,c.p,c.a,c.x,c.y=240,flags,0x83,0x69,0x77
    c.stPushWord(C.STOP-1)
    observed=None
    for _ in range(300):
        if c.pc==C.STOP:
            break
        if cut and not observed and c.pc==cut[1]:
            observed=C.vector(c,cut[0])
        assert m[c.pc],(logical,offset,bank,hex(c.pc),m.rawtags)
        c.step()
    else:
        raise AssertionError(('Audio read bound',logical,offset,bank,hex(c.pc)))
    assert c.sp==240 and bool(observed)==bool(cut)
    assert m.rawtags[1:3]==[190,225] and M.get(m,'CurrentBank')==190
    value=M.get(m,'RdaReadValue')
    return (c.a,c.x,c.y,c.p&0xef,value,m[0xe8],m[0xe9]),c.processorCycles,observed


def audio_rows(b):
    for mode,stem,count in (('lower','RdaLower',192),('upper','RdaUpperRaw',32)):
        bank,high=(location(b,stem+suffix) for suffix in ('BankTable','HighTable'))
        for i,(tag,hi) in enumerate(zip(b['raw'][bank:bank+count],b['raw'][high:high+count],strict=True)):
            assert tag&128 and 0xa0<=hi<=0xbf
            yield mode,i,tag,hi


def audio_checks(b,new,labels):
    pair=[M.fresh(image) for image in (b,new)]
    hit=Counter()
    cost={}
    for mode,i,tag,hi in audio_rows(b):
        logical=0x80+i%32 if mode=='lower' else 0xa0+i
        bank=i//32 if mode=='lower' else 0
        for offset in range(256):
            flags=(0x20,0x21,0x60,0x65,0x2c,0xe9)[(i+offset)%6]
            (before,old_cycles,_),(after,new_cycles,_)= [call_audio(m,logical,offset,bank,flags) for m in pair]
            desired=native_slice(b['raw'],tag&127,256*hi+offset,1)[0]
            assert before==after and desired==after[4],(mode,i,offset,tag,hi,before,after,desired)
            new_cell=native_slice(new['raw'],tag&127,256*hi+offset,1)[0]
            group=mode+('_bank90' if tag==DATA_WINDOW else '_other')
            if mode=='lower' and i in VIRTUAL_ROWS:
                group='virtual_rows'
            hit[group]+=1
            if new_cell!=desired:
                assert tag==DATA_WINDOW and desired==0
                hit['overwritten_bytes_reconstructed']+=1
            added=new_cycles-old_cycles
            low,high=cost.get(group,(added,added))
            cost[group]=[min(low,added),max(high,added)]
            for m in pair:
                m.writes.clear()
                m.ram_writes.clear()
    assert sum(n for k,n in hit.items() if k!='overwritten_bytes_reconstructed')==57344
    assert hit['overwritten_bytes_reconstructed']>650
    assert all(lo==hi==(0 if name=='upper_other' else 2) for name,(lo,hi) in cost.items()
               if name!='virtual_rows'),cost

    # Compare genuine vectors while the real A map is $da in both cases.
    vector_rows=[]
    basepc=0xc434
    for mode,i,tag,hi in audio_rows(b):
        if tag!=DATA_WINDOW or hi not in (0xb0,0xb1,0xb7,0xb8,0xbc):
            continue
        offset={0xb0:0x9e,0xb1:0x7f,0xb7:5,0xb8:0x8f,0xbc:0x40}[hi]
        assert mode=='lower'
        for kind in ('irq','lag_nmi'):
            for candidate_cut in (labels['GiantRogueMux']+8,labels['GiantRogueRead']):
                x,z=[M.fresh(image) for image in (b,new)]
                old=call_audio(x,0x80+i%32,offset,i//32,0x21,(kind,basepc))
                now=call_audio(z,0x80+i%32,offset,i//32,0x21,(kind,candidate_cut))
                assert old[0]==now[0] and old[2]['handler']==now[2]['handler']
                C.compare_memory(x,z)
                vector_rows.append(dict(logical_row=i,physical_page=hi,old=old[2],new=now[2]))
    assert len(vector_rows)==20
    return dict(read_counts=hit,added_cycles_per_reader=cost,real_vectors=vector_rows)


def foreign_checks(normal,b,candidate,labels):
    rows=[]
    seeds=[(C.enter_owner(b,slot,cycle),slot,cycle,8,0,0,False)
           for slot,cycle in [(0,i) for i in range(9)]+[(2,1),(9,2)]]
    seeds += [(normal,0,None,engine,disabled,water,True)
              for engine,disabled,water in ((7,0,0),(8,1,0),(8,0,1))]
    for seed,slot,cycle,engine,disabled,water,inactive in seeds:
        pair=[M.fork(seed),M.fork(seed)]
        pair[1].bundle=candidate
        for m in pair:
            if inactive:
                M.put(m,MarioVariant=9,GameEngineSubroutine=engine,DisableCollisionDet=disabled,SwimmingFlag=water)
        a,z=[C.play(m,labels) for m in pair]
        assert (a['AXYP'],a['box'],a['effects'],a['native_bg'])==(z['AXYP'],z['box'],z['effects'],z['native_bg'])
        C.compare_memory(*pair)
        rows.append(dict(slot=slot,select_presses=cycle,raw=M.get(seed,'SelectedCharacter'),
                         variant=M.get(pair[0],'MarioVariant'),engine=engine,disabled=disabled,swimming=water,
                         added_cycles=z['cycles']-a['cycles']))
    assert any(q['raw']==41 and q['variant']==8 and q['added_cycles']==0 for q in rows)
    assert any(q['raw']==9 and q['select_presses']==2 for q in rows)
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(exist_ok=True)
    assert C.sha(C.HOST)==C.PIN and C.sha(C.DONOR)==C.DONOR_PIN
    raw=C.HOST.read_bytes()
    b=C.bundle(raw)
    ownership=source_pages(b)
    packed,labels=assemble(args.output,b)
    after,patches=compose(raw,packed,labels)
    candidate=C.bundle(after)
    normal,_=C.start_stage(b)
    resident,_=C.start_stage(candidate)
    foreign=foreign_checks(normal,b,candidate,labels)
    route=C.route(M.fork(resident),labels)
    print('Actual cold CPU path, resident code and route',route['world_X'],route['update'],flush=True)
    # Match the previously tested precise foreground cut coordinates. The
    # only executable payload is in the banked cartridge image this time.
    from check_mega_giant_pipe_ingress_1110_v1 import reach_pipe
    m,_=reach_pipe(candidate)
    donor=bytearray(65536)
    donor[0x8000:]=C.DONOR.read_bytes()[16:32784]
    vectors=C.seeded(m,labels,donor)
    audio=audio_checks(b,candidate,labels)
    refs=(Path(__file__),SOURCE,C.ROUTE,C.CRUSH,C.SOURCE,ROGUE,READER,C.HOST,C.DONOR,
          R/'tools/audit/check_mega_giant_compound_1110.py')
    proof=dict(passed=True,source_CPU_only=True,ROM_written=False,menu_admitted=False,
               parent_SHA256=C.PIN,expected_memory_only_SHA256=checksum(after),
               resident_PRG=True,storage=dict(candidate_intervals=PAGES,source=ownership,
                    complete_link_image_SHA256=checksum(packed),symbols=labels),
               patches=patches,controller_trajectory=route,foreign=foreign,
               prior_fixture_negative='Quick Man failed at $24FF on both images in the old executable-RAM fixture. '
                    'Both actual banked foreground updates complete when that private payload write is omitted.',
               foreground_vectors=vectors,audio=audio,bindings={str(p):C.sha(p) for p in refs})
    (args.output/'proof-v2.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(passed=True,expected_memory_only_SHA256=proof['expected_memory_only_SHA256'],
           audio_reads=audio['read_counts'],audio_added_cycles=audio['added_cycles_per_reader'],
           native_box_plus_BG=route['native_BG_with_Giant'],last_X=route['world_X']),sort_keys=True))


if __name__=='__main__':
    main()
