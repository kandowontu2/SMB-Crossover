"""Qualify the source-funded Sonic native-skin renderer in memory only."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import zipfile

import prepare_sonic_sms_skin_1110 as S
import check_mini_funded_actor_1108_v3 as Cpu
from check_tmnt_render_oa import address,location

P,N,R=S.Host,S.Host.N,S.R


def digest(raw):return sha256(raw).hexdigest()


def funding(raw,b):
    # Reuse the exact named source input, not an expanded historical tree.
    with zipfile.ZipFile(R/'build/_recovery/legacy-sources-2026-10-31.zip') as archive:
        index=json.loads(archive.read('index.json'))
        row=next(r for r in index if r['path']=='benj-mario-native-host-v5/benj_graphics.s')
        original=archive.read('objects/'+row['sha256'])
    assert digest(original)==row['sha256']
    assert b'BmOwnCodeEnd:' in original and b'.res 1077-(*-BmOwnStart),$ff' in original
    assert address(b,'BmOwnCodeEnd')==0xbb9c and address(b,'BmOwnEnd')==0xbba7
    areas=((0xb6cb,33),(0xb70e,8),(0xbb9c,11),(0xa9c0,64))
    assert S.Current.W.bundle(raw)['raw']==raw
    assert raw[P.at(62,0xb70e):P.at(62,0xb70e)+8]==b'\xea'*8
    assert raw[P.at(62,0xbb9c):P.at(62,0xbb9c)+11]==b'\xff'*11
    assert raw[P.at(62,0xa9e0):P.at(62,0xaa00)]==b'\xff'*32
    assert raw[P.at(62,0xb6cb):P.at(62,0xb6cb)+33].hex()==(
        'ad0260d01bad0a73c903d014ade073c984f008a9848de073ee4601a9018dee7360')
    return dict(areas=[dict(bank=62,PC=p,bytes=n) for p,n in areas],
                Benj_source_archive_member=row,old_NMI=[0xa9c0,0xa9e0],
                new_NMI_gap=[0xa9e0,0xaa00],next_owner='FF_ROM_HOST at AA00')


def compile_source(out):
    spans=(('SELECT',0xb6cb,33),('COMPARE',0xb70e,8),('STORE',0xbb9c,11),('NMI',0xa9c0,64))
    memory=''.join(f'M{i}:start=${p:x},size=${n:x},file=%O,fill=yes,fillval=$ea;'
                   for i,(_,p,n) in enumerate(spans))
    segments=''.join(f'{name}:load=M{i},type=ro;' for i,(name,_,_) in enumerate(spans))
    with tempfile.TemporaryDirectory(dir=out) as work:
        config=Path(work)/'kernel.cfg'
        config.write_text('MEMORY{'+memory+'}SEGMENTS{'+segments+'}')
        blob,labels=P.compile_source(Path(work),S.SOURCE.read_text(),
                                      config)
    result=[];step=0
    for _,pc,n in spans:
        result.append((pc,blob[step:step+n]));step+=n
    assert step==len(blob)==116
    return result,labels


def construct(out):
    raw=S.BASE.read_bytes();assert digest(raw)==S.PIN
    b=S.Current.W.bundle(raw)
    authority=funding(raw,b)
    fragments,labels=compile_source(out)
    rows=[]
    def add(bank,pc,new,role):
        at=P.at(bank,pc);old=raw[at:at+len(new)]
        rows.append(dict(file_offset=at,old_hex=old.hex(),new_hex=new.hex(),
                         physical_PRG=bank,CPU_half_open=[pc,pc+len(new)],role=role))
    for pc,data in fragments:add(62,pc,data,'Existing skin/select/NMI source-owned extent')
    assert raw[P.at(62,0xb690):P.at(62,0xb690)+3]==bytes.fromhex('4c72b7')
    add(62,0xb690,b'\x4c'+labels['SonicGraphics'].to_bytes(2,'little'),
        'Exact KmGraphics public entry; old graphics followed by preserving skin dispatch')
    new=P.install(raw,rows)
    return raw,new,rows,labels,authority


def local(b,pc,**values):
    m=N.fresh(b);N.put(m,**values)
    m.raw_page(1,190);N.put(m,CurrentBank=190)
    cpu=N.NesMPU(memory=m,pc=pc);cpu.a=91;cpu.x=74;cpu.y=179;cpu.p=0x71;cpu.sp=224
    cpu.stPushWord(0x5aff)
    Cpu.run(cpu,lambda c:(c.pc,c.sp)==(0x5b00,224))
    return m,cpu


def core_state(m,c):
    return (c.a,c.x,c.y,c.p&0xef,c.sp,bytes(m[0x200:0x800]),
            bytes(m[0x6000:0x8000]),tuple(m.rawtags),bytes(m[0:0x100]),
            bytes(m[0x145:0x17b]))


def leaves(before,after,labels):
    bundles=[S.Current.W.bundle(r) for r in (before,after)]
    count=0
    for owner in (0,1,5,16,25,34,38,39,40,41,42):
      for variant in (0,1,2,3,4,5,6,7,8,9,11,255):
       for mode in (0,0x80,0x83,0x84,0x86,255):
        pair=[local(b,0xb6cb,SelectedCharacter=owner,MarioVariant=variant,
                    X5ChrMode=mode,ReloadCHRBank=17,X5WideChrActive=0) for b in bundles]
        assert core_state(*pair[0])==core_state(*pair[1]),(owner,variant,mode)
        count+=1
    nmi=0
    for mode in range(256):
      if mode==0x85:continue
      for page in (0,16,17,18,19,127,255):
       for flags in (0x30,0x31,0x71,0xf1):
        pair=[]
        for b in bundles:
            m=N.fresh(b);m.raw_page(1,190);N.put(m,CurrentBank=190,CurrentCHRBank=page)
            c=N.NesMPU(memory=m,pc=0xa9c0);c.a=mode;c.x=74;c.y=179;c.p=flags;c.sp=224;c.stPushWord(0x5aff)
            Cpu.run(c,lambda z:(z.pc,z.sp)==(0x5b00,224))
            pair.append((m,c))
        assert core_state(*pair[0])==core_state(*pair[1]),(mode,page,flags)
        nmi+=1
    own=[]
    for page,wanted in zip(range(16,20),S.PAGES,strict=True):
        m,c=local(bundles[1],0xa9c0,CurrentCHRBank=page)
        # local's initial A is arbitrary; run the actual new mode explicitly.
        c.pc=0xa9c0;c.a=0x85;c.sp=224;c.stPushWord(0x5aff)
        Cpu.run(c,lambda z:(z.pc,z.sp)==(0x5b00,224))
        assert c.a==wanted and m.mmc5_chr_upper==0 if hasattr(m,'mmc5_chr_upper') else c.a==wanted
        own.append(dict(native_page=page,physical=wanted))
    return dict(foreign_skin_cases=count,all_old_mode_NMI_cases=nmi,source_mapping=own)


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args=cli.parse_args();assert args.output.exists()
    before,after,patches,labels,authority=construct(args.output)
    tests=leaves(before,after,labels)
    q=dict(passed=True,render_component_only=True,prototype=True,ROM_written=False,
        interrupt_pending=True,menu_pending=True,palette_pending=True,
        parent_SHA256=S.PIN,expected_memory_only_SHA256=digest(after),
        patches=patches,labels=labels,funding=authority,CPU=tests,
        scope='Finite skin/NMI numeric+AXYP/state parity and new4page mapping only. '
              'No cartridge is written; menu, palette, source-owned CHR admission, '
              'native controls, whole-loop and interrupt closure remain pending.',
        bindings={p.relative_to(R).as_posix():digest(p.read_bytes()) for p in
                  (Path(__file__),Path(S.__file__),S.SOURCE,S.BASE,
                   R/'build/sonic-native-prototype-1110/art-proposal.json')})
    (args.output/'render-progress.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(passed=True,render_component_only=True,**tests)))


if __name__=='__main__':main()
