"""Source-retire unused FF gate for a temporary native platform-foot query."""
import argparse
from hashlib import sha256
import inspect
import json
from pathlib import Path
import re

import check_manual_roster_input_1110 as I
import check_manual_roster_carry_1110 as Carry
import check_manual_roster_motion_1110 as Motion

P,N,W,R=I.P,I.N,I.W,I.R
SOURCE=R/'tools/reference/manual_roster_ff_foot_1110.s'
PROOF=I.OUT/'leaf-proof.json'
OUT=I.OUT
SHA=lambda p:sha256(Path(p).read_bytes()).hexdigest()


def input_source():
    s=I.SOURCE.read_text()
    for block in ('    lda OperMode\n    cmp #1\n    jne Inactive\n',
                  '    lda OperTask\n    cmp #3\n    jne Inactive\n'):
        s=P.replace_one(s,block,'')
    return s


def horizontal_source(s):
    s=P.replace_one(s,'    cmp #22\n    beq ManualWideHorizontal',
        '    cmp #22\n    beq FfManualHorizontal')
    return P.replace_one(s,'ManualWideHorizontal:\n',
        '''FfManualHorizontal:
    lda $065b
    cmp #$ff
    beq ManualWideHorizontal
    lda #<FfManualFootQuery
    sta TargetLo
    lda #>FfManualFootQuery
    sta TargetHi
    lda #$be
    jsr FarCall
ManualWideHorizontal:
''')


def old_foot(raw,work):
    source=work/'old-foot.s';source.write_text('FOOT_ORIGINAL=1\n'+SOURCE.read_text())
    code,labels=P.link(work,source,(('FF_ROSTER_FOOT',0xadc4,26),))
    assert len(code)==26 and labels['FfManualFootQueryEnd']==0xadde
    assert raw[P.at(62,0xadc4):P.at(62,0xadde)]==code


def build():
    # Derive only this exact frozen recipe; no archived tree or old object is
    # restored. The original31B/12B ingress and167B horizontal are reproduced.
    s=inspect.getsource(I.build).replace('def build(out):','def derive(out):',1)
    anchor="    with tempfile.TemporaryDirectory(dir=out) as tmp:"
    s=P.replace_one(s,anchor,'    roster=horizontal_source(roster)\n'+anchor)
    s=P.replace_one(s,"        src=work/'roster.s';",'        old_foot(raw,work)\n'+"        src=work/'roster.s';")
    s=P.replace_one(s,'paths(SOURCE.read_text())','paths(input_source())')
    s=P.replace_one(s,"+'\\n'+INGRESS.read_text())","+'\\n'+INGRESS.read_text()+'\\n'+FOOT.read_text())")
    s=s.replace("('HORIZONTAL',hpc,175)","('HORIZONTAL',hpc,197)")
    s=s.replace("('ROSTER_INPUT_HEAD',hpc+175,81)","('ROSTER_INPUT_HEAD',hpc+197,59)")
    anchor="('ROSTER_DISPATCH',0xb134,12)))"
    assert s.count(anchor)==2
    first,last=s.rsplit(anchor,1)
    s=first+"('ROSTER_DISPATCH',0xb134,12),('FF_ROSTER_FOOT',0xadc4,26)))"+last
    s=s.replace("-(hpc+175)","-(hpc+197)")
    s=s.replace("sizes[0]==175 and sizes[1]<=81","sizes[0]==197 and sizes[1]<=59")
    s=s.replace('sum(sizes)+43','sum(sizes)+43+22')
    s=s.replace('(hpc,hpc+175,vpc),sizes,(175,81,256)',
                '(hpc,hpc+197,vpc),sizes,(197,59,256)')
    s=P.replace_one(s,'    old_reader=raw[',
        "    patches.append(P.L.patch(raw,P.at(62,0xadc4),code[at+43:at+65].ljust(26,b'\\xea'),\n"
        "        'Retire unused FwSide gate; temporary selected22 manual-H foot query'))\n"
        '    old_reader=raw[')
    env=dict(I.__dict__);env.update(horizontal_source=horizontal_source,input_source=input_source,
        old_foot=old_foot,FOOT=SOURCE)
    exec(s,env)
    return env['derive'](OUT)


def retired_gate(raw):
    debug=R/'build/roster-combined-1101-v3/candidate.dbg'
    symbols=[]
    for line in debug.read_text().splitlines():
        if line.startswith('sym\t') and 'name="FwSide"' in line:
            symbols.append(dict(x.split('=',1) for x in line[4:].split(',') if '=' in x))
    assert len(symbols)==1 and symbols[0]['type']=='lab' and symbols[0]['val']=='0xADC4'
    assert not any(s.get('type')=='imp' for s in symbols)
    prg=raw[16:1048592];bank=raw[P.at(62,0xa000):P.at(62,0xa000)+8192]
    assert not any(bank[i] in (0x20,0x4c) and bank[i+1:i+3]==bytes.fromhex('c4ad') for i in range(8190))
    assert bytes.fromhex('a9c48d6c01a9ad8d6d01a9be') not in prg
    assert bytes.fromhex('c4adbe') not in prg
    loader=R/'build/ff-lives-body-palette-v1/joint/loader.s'
    assert re.findall(r'\bFwSide\b',loader.read_text())==['FwSide']
    # Real live service14 goes through its typed terrain gate, not FwSide.
    b=P.L.M.bundle(raw)
    row=P.L.M.location(b,'FwServiceVeneers')+14*3
    target=P.L.M.address(b,'FwSvcSide')
    assert raw[row:row+3]==b'\x4c'+target.to_bytes(2,'little')
    game=(R/'src/game.s').read_text();menu=(R/'build/hogan-current/src/character_select.s').read_text()
    assert game.count('    jsr HpProcessFireballsBridge')==1
    assert '.word SecondaryGameSetup\n  .word GameCoreRoutine' in game
    assert '; Dedicated, non-gameplay front end. The title never runs GameCoreRoutine.' in menu
    assert 'sta DemoTimer                 ; never enter the native attract demo' in menu
    return dict(gate=[62,0xadc4,0xadde],exact_source26B=True,emitted_imports=0,
        samebank_direct_callers=0,literal_farcall_packets=0,banked_pointer_tokens=0,
        live_side_row14=dict(target='FwSvcSide',PC=target),
        native_input_ingress='Sole GameCoreRoutine post-GameRoutines bridge; GameMode task3; native crossover front end disables demos and never invokes GameCore.',
        source_paths={str(p.relative_to(R)):SHA(p) for p in (debug,loader,R/'src/game.s',R/'build/hogan-current/src/character_select.s')})


def bundle(raw,labels):
    b=I.bundle(raw,labels)
    b['segs']['ff_manual_foot']=dict(start=str(0xa000),ooffs=str(P.at(62,0xa000)))
    for n in ('FfManualFootQuery','FfManualFootQueryEnd'):
        b['syms'][n]=dict(val=str(labels[n]),seg='ff_manual_foot')
    return b


def overflow(b):
    m=Motion.scene(b,22,0)
    z=N.invoke(m,'ManualPlatform',x=0x42,y=24);slot=z['X']-1
    N.put(m,ObjectOffset=slot)
    m[0x65b]=255
    P.set_slot(m,slot,PlatformCollisionFlag=255)
    before=N.get(m,'Enemy_X_Position',slot)+256*N.get(m,'Enemy_PageLoc',slot)
    N.invoke(m,'HpNativePlatformDispatch',x=slot)
    after=N.get(m,'Enemy_X_Position',slot)+256*N.get(m,'Enemy_PageLoc',slot)
    assert m[0x65b]==255 and N.get(m,'PlatformCollisionFlag',slot)==255 and after==before+1
    return dict(bottom255_skips_query=True,bbox_byte_exact=True,native_motion_continues=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--fit',action='store_true');a=ap.parse_args()
    q=json.loads(PROOF.read_text())
    for name,digest in q['bindings'].items():assert SHA(R/name)==digest,name
    raw,new,rows,labels,layout,vertical=build()
    print('FF foot source fit',layout,'memory image',I.SHA(new),flush=True)
    if a.fit:return
    lease=retired_gate(raw);b=bundle(new,labels)
    edge=overflow(b);print('overflow guard',edge,flush=True)
    forms={};W.D.offset=W.right_offset
    for variant in range(4):
        m=Motion.scene(b,22,variant)
        h=Carry.horizontal(m,22)
        v=W.D.motion(Motion.scene(b,22,variant),22,0x28)
        t=W.native_triangle(Motion.scene(b,22,variant),labels)
        forms[variant]=dict(horizontal=h,vertical=v,triangle=t)
        print('FF genuine carry',variant,h,v,flush=True)
    result=dict(passed=True,source_CPU_only=True,Mesen_run=False,ROM_written=False,interrupt_pending=True,
        parent_SHA256=I.PIN,expected_memory_only_SHA256=I.SHA(new),patches=rows,labels=labels,
        layout=layout,retired_gate=lease,overflow=edge,forms=forms,
        frozen_input_predecessor_SHA256=q['expected_memory_only_SHA256'],
        scope='FF-only manualH temporarily extends bottom by1 for the existing native large-platform query, restores ordinarybox exactly, and keeps existingY+32 ctor/native movement. ActualGameCore carry proof; no Mesen/IRQ/fullstage claim.',
        bindings={p.relative_to(R).as_posix():SHA(p) for p in
            (Path(__file__),SOURCE,PROOF,Path(I.__file__),Path(Carry.__file__),Path(Motion.__file__),I.SOURCE,I.INGRESS,W.SOURCE,I.BASE)})
    (OUT/'ff-foot-proof.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
