"""Fund and qualify native initial-right112px horizontal manual girders."""
import argparse
from collections import Counter
from hashlib import sha256
import inspect
import json
from pathlib import Path
import re
import tempfile

import check_manual_dual_platform_1110 as D

P,N,R=D.P,D.N,D.R
BASE=R/'build/getsu-fast-head-native-1110/candidate.nes'
PIN='66a7b9325d90efb7751387e0c1c95a756fde57d92f13d6180178ade3e535090c'
PRIOR=R/'build/manual-dual-platform-1110/rebase-proof.json'
SOURCE=R/'tools/reference/manual_wide_horizontal_1110.s'
OUT=R/'build/manual-wide-horizontal-1110'
DATA=R/'src/crossover_helper_data.inc'


def sha(data):return sha256(data).hexdigest()


def mini_source():
    s=D.mini_source()
    s=P.replace_one(s,'''    lda PlayerFacingDir
    cmp #2
    bne @call
    ldy #$d4
''','')
    s=P.replace_one(s,'    and #$2c\n    cmp #$24',
                       '    and #$2c\n    beq @pending\n    cmp #$24')
    copy='    ldx #2\n    jsr MiniCopyToScan'
    at=s.rfind(copy)
    assert at>=0 and s.count(copy)==2
    s=s[:at]+'''    lda MiniCoord
    sta MiniScanY
    lda MiniCoord+1
    sta MiniScanY+1'''+s[at+len(copy):]
    return s


def table(raw):
    text=DATA.read_text().split('HpSineHorizontal:\n',1)[1].split('HpSineVertical:',1)[0]
    values=bytes(int(v) for line in text.splitlines() if '.byte' in line
                 for v in line.split('.byte',1)[1].strip().split(','))
    assert len(values)==256 and values==bytes(sorted(values)) and max(values)==30
    bank=raw[P.at(26,0xa000):P.at(26,0xa000)+8192]
    assert bank.count(values)==1
    pc=0xa000+bank.index(values)
    opcode=b'\xb9'+pc.to_bytes(2,'little')
    assert bank.count(opcode)==1
    reader=0xa000+bank.index(opcode)
    thresholds=bytes([0]+[values.index(i)-1 for i in range(1,31)]+[255])
    return values,pc,reader,thresholds


def build(out):
    raw=BASE.read_bytes();assert sha(raw)==PIN
    prior=json.loads(PRIOR.read_text());assert prior['passed'] and prior['parent_SHA256']==PIN
    for path,digest in prior['bindings'].items():assert sha((R/path).read_bytes())==digest,path
    baseline=P.install(raw,prior['patches']);assert sha(baseline)==prior['expected_memory_only_SHA256']
    values,pc,reader,thresholds=table(raw)
    with tempfile.TemporaryDirectory(dir=out) as tmp:
        work=Path(tmp)
        (work/'thresholds.bin').write_bytes(thresholds)
        old=baseline[P.at(26,0xae6b):P.at(26,0xae6b)+3]
        assert old==bytes.fromhex('b51738')
        b=P.L.M.bundle(raw)
        defs=''.join(f'{n}=${P.L.M.address(b,n):04x}\n' for n in ('HpTemp2','HpSineIndex'))
        defs+='NativeMotionResume=$ae6e\n'
        asm=work/'motion.s';asm.write_text(defs+SOURCE.read_text().replace('"thresholds.bin"','"'+str(work/'thresholds.bin').replace('\\','/')+'"'),encoding='utf-8')
        code,labels=P.link(work,asm,(('HORIZONTAL',pc,256),))
        assert len(code)<=256 and labels['ManualHorizontalEnd']==pc+len(code)
        kernel,ml=P.compile_source(work,mini_source()+'\n.export MiniHeadEvent,MiniTempPixel\n',P.L.CONFIG)
        assert len(kernel)==5120
        public={k:v for k,v in prior['labels'].items() if k.startswith('MiniHost') or k in ('MiniStep','MiniAnimate','MiniNativeTile','MiniNativeDraw','MiniVectors','MiniWorldEnd')}
        assert all(ml[k]==v for k,v in public.items())
        ks=D.KARNOV_SOURCE.read_text()
        ks=P.replace_one(ks,'''    lda Facing
    cmp #2
    bne Call
    ldy #$d8
    bne Call
''','    bne Call\n')
        ka=work/'karnov.s';ka.write_text(ks,encoding='utf-8')
        k,kl=P.link(work,ka,(('OPTIONS',0xb378,136),('RESET',0xddf7,9)))
        count=kl['KrManualOptionsEnd']-0xb378
        assert count<130
    patches=list(prior['patches'])
    patches=[p for p in patches if p['file_offset'] not in (P.L.CODE,P.L.COOKIE+3,P.at(11,0xb378))]
    patches.extend((P.L.patch(raw,P.L.CODE,kernel,'Same five Mini pages; always-right+idle fast lane'),
        P.L.patch(raw,P.L.COOKIE+3,sha256(kernel+raw[P.L.CODE+5120:P.L.CODE+7168]).digest()[:13],'Authentic Mini payload cookie'),
        P.L.patch(raw,P.at(11,0xb378),k[:count],'Always-right Karnov manual horizontal caller'),
        P.L.patch(raw,P.at(26,pc),code.ljust(256,b'\xea'),'Exact horizontal sine thresholds fund owned native112px triangle'),
        P.L.patch(raw,P.at(26,reader),b'\x20'+labels['ManualSineDecode'].to_bytes(2,'little'),'Only horizontal sine reader; preserved numeric output+Y/P'),
        P.L.patch(raw,P.at(26,0xae6b),b'\x4c'+labels['ManualMotionGate'].to_bytes(2,'little'),'Source-bound native platform marker ingress')))
    final=P.install(raw,patches)
    return raw,baseline,final,patches,prior['labels']|ml|kl|labels,kernel,dict(table_pc=pc,reader_pc=reader,table_values=values.hex(),thresholds=thresholds.hex(),code_bytes=len(code))


def right_offset(owner,horizontal,facing=1):return (4 if owner==41 else 8)+(16 if horizontal else -16)


def sample(m,slot):
    return dict(x=N.get(m,'Enemy_X_Position',slot)+256*N.get(m,'Enemy_PageLoc',slot),
        player_x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
        y=N.get(m,'Enemy_Y_Position',slot),player_y=N.get(m,'Player_Y_Position'),
        travelled=N.get(m,'Enemy_Y_Speed',slot),direction=N.get(m,'Enemy_Y_MoveForce',slot),
        speed=N.get(m,'Enemy_X_Speed',slot),collision=N.get(m,'PlatformCollisionFlag',slot))


def native_triangle(seed,labels):
    # Direct actual native dispatch at a legal constructor result. No player
    # carry here; whole-frame physical controls qualify carrying separately.
    m=P.slim_fork(seed)
    N.put(m,Player_X_Position=100,Player_PageLoc=1,Player_Y_Position=144,Player_Y_HighPos=1,
          ObjectOffset=0)
    r=N.invoke(m,'ManualPlatform',x=0x42,y=20)
    slot=r['X']-1
    assert slot>=0
    N.put(m,ObjectOffset=slot)
    before=sample(m,slot)
    assert (before['travelled'],before['direction'])==(0,0)
    points=[]
    for epoch in range(337):
        P.set_slot(m,slot,PlatformCollisionFlag=255)
        z=N.invoke(m,'HpNativePlatformDispatch',x=slot,a=0)
        q=sample(m,slot)
        phase=(epoch+1)%224
        expect=phase if phase<=112 else 224-phase
        assert q['x']==before['x']+expect,(epoch,q,before,expect)
        assert 0<=q['travelled']<=112 and q['direction'] in (0,1)
        if epoch in (0,111,112,223,224,335,336):points.append(dict(epoch=epoch+1,**q))
    return dict(birth=before,points=points,updates=337,stroke=112,native_speed=[16,240])


def carrying(seed,owner):
    code=inspect.getsource(D.motion).replace('def motion(','def check(')
    code=code.replace('P.frame(m,0 if kind==0x25 else 1)','P.frame(m,0 if kind==0x25 else 65)')
    code=code.replace('for age in range(64):','for age in range(192):')
    env=dict(D.__dict__);exec(code,env)
    return env['check'](seed,owner,0x24)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fit',action='store_true')
    a=p.parse_args();OUT.mkdir(exist_ok=True)
    raw,old,new,rows,labels,kernel,format=build(OUT)
    print(json.dumps(dict(expected_memory_only_SHA256=sha(new),patches=len(rows),format=format|{'table_values':'omitted','thresholds':'omitted'})),flush=True)
    if a.fit:return
    before,after=P.bundles(old,new)
    D.offset=right_offset
    for b in (before,after):
        # Actual linked shared entry, retained public address.
        b['segs']['native_platform']=dict(start=str(0xae40),ooffs=str(P.at(26,0xae40)))
        b['syms']['HpNativePlatformDispatch']=dict(val=str(0xae40),seg='native_platform')
    owners={}
    for owner in (41,34):
        seed=P.scene(after,owner)
        owners[owner]=dict(controls=D.controls(seed,owner,labels),
            carry=carrying(seed,owner),triangle=native_triangle(seed,labels))
        print(owner,owners[owner],flush=True)
    result=dict(passed=True,interrupt_pending=True,parent_SHA256=PIN,expected_memory_only_SHA256=sha(new),ROM_written=False,Mesen_run=False,
        patches=rows,labels=labels,success_PC=labels['ManualPlatformCreated'],success_bank=64,
        owners=owners,format=format,native_config=dict(actor=0x28,marker=0x42,width=32,stroke=112,initial_direction='right'),
        bindings=json.loads(PRIOR.read_text())['bindings']|{q.relative_to(R).as_posix():sha(q.read_bytes())for q in (Path(__file__).resolve(),SOURCE,DATA,PRIOR,BASE)})
    (OUT/'proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (OUT/'kernel.bin').write_bytes(kernel)


if __name__=='__main__':main()
