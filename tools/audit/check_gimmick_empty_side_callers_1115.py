"""Private caller/scratch closure and full current Gimmick Draw equivalence."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json,re
import compose_gimmick_empty_side_1115 as C
import check_gimmick_empty_side_components_1115 as Units
import replay_gimmick_empty_side_current_1115 as Factory
import check_mr_gimmick_full11_current_1114 as Cold

N,W=C.N,C.W


def proc(text,name):return text.split('.proc '+name+'\n',1)[1].split('.endproc',1)[0]


def closure(old):
    q=C.recipe(old);host=(C.R/'src/gimmick_host.s').read_text();render=(C.R/'src/gimmick_render.s').read_text()
    registry={name:[]for name in('GmBodyProbe','GmCameraPoint','GmTemp2')}
    for path in sorted((C.R/'src').glob('*')):
        if path.suffix not in('.s','.inc'):continue
        for number,line in enumerate(path.read_text().splitlines(),1):
            code=line.split(';',1)[0].strip()
            for name in registry:
                if re.search(r'\b'+name+r'\b',code):registry[name].append((path.name,number,code))
    assert {p for p,n,line in registry['GmBodyProbe']}=={'gimmick_host.s'}
    assert {p for p,n,line in registry['GmCameraPoint']}=={'gimmick_render.s'}
    assert {p for p,n,line in registry['GmTemp2']}=={'gimmick_state.inc','gimmick_host.s','gimmick_render.s'}
    assert [line for p,n,line in registry['GmCameraPoint']]==['jmp GmCameraPoint','.proc GmCameraPoint','jsr GmCameraPoint','jsr GmCameraPoint']
    # The component's symbol export is not a host ingress. The actual linked
    # admission's explicitly imported service set has neither private label.
    admission=(C.R/'tools/prepare_gimmick_admission_v3.py').read_text()
    exported=re.search(r" exports='([^']+)'\.split\(\)",admission)[1].split()
    assert all(name not in exported for name in('GmBodyProbe','GmCameraPoint','GmScreenPoint','GmStarRecord','GmEmitRecord'))
    assert all(name in exported for name in('GmHead','GmFoot','GmSide','GmDraw','GmPortrait','GmNmiClock'))
    # Actual legal emit callers set facing themselves. No previous probe-Y is
    # part of any public query ABI or a source input to graphics/audio/ISR.
    portrait,draw,emit=(proc(render,name)for name in('GmPortrait','GmDraw','GmEmitRecord'))
    assert portrait.index('and #1\n sta GmTemp2')<portrait.index('lda GmTemp2')<portrait.index('GmFar GmEmitRecord,24')
    assert 'lda GmTemp2' in emit and 'GmTemp2'not in proc(render,'GmScreenPoint')+proc(render,'GmCameraPoint')
    assert draw.index('lda GmRam030B\n sta GmTemp2')<draw.index('Trail:')
    assert draw.index('lda #0\n sta GmTemp2')<draw.index('Effect:')
    assert draw.index('lda GmRam030A\n sta GmTemp2')<draw.rindex('jsr GmEmitRecord')
    assert render.count('GmFar GmEmitRecord,24')==1 and render.count('jsr GmEmitRecord')==2 and render.count('jmp GmEmitRecord')==1
    assert 'GmTemp2'not in(C.R/'src/gimmick_core.s').read_text()
    return dict(source_reference_registry=registry,host_service_exports=exported,private_indirect_domain='Neither moved private label is admitted/published by a host service; all actual references are the source-bound calls inside the four spans',
        deleted_scratch_write='Only old Body STY GmTemp2=probe index is removed. Each actual renderer ingress writes its own facing before every legal read; direct EmitRecord unit ABI requires caller-facing input.',
        no_blanket_private_RAM_exception=True)


def run(actual):
    raw,layout=C.current_proposal(actual);assert C.current_inverse(raw)==actual
    old=C.load590()[0] if sha256(actual).hexdigest()==C.PIN else __import__('compose_prince_body_transition_590_1115').inverse(actual)
    close=closure(old)
    with patch.object(Cold,'Factory',Factory):new=Cold.cold(raw,'flower')
    parent=N.fork(new);parent.bundle=Units.bundle(actual)
    for win,tag in enumerate(parent.rawtags[:]):
        if tag&128:parent.raw_page(win,tag)
    cases=0;screen_calls=0;deltas=set()
    def compare(name,pair,a=83):
        nonlocal cases
        before=[N.get(m,'GmTemp2')for m in pair]
        results=[N.invoke(m,name,a=a,x=71,y=109,p=0xe1)for m in pair]
        assert all(results[0][k]==results[1][k]for k in('A','X','Y','P')),(name,results)
        assert bytes(pair[0][512:768])==bytes(pair[1][512:768]),('Complete ordered OAM',name)
        assert N.get(pair[0],'CurrentOAMOffset')==N.get(pair[1],'CurrentOAMOffset')
        assert bytes(pair[0][0:256])==bytes(pair[1][0:256]),('Full zero page',name)
        assert bytes(pair[0][0x5c00:0x5c80])==bytes(pair[1][0x5c00:0x5c80]),('All private source state including Temp2',name,before)
        assert bytes(pair[0][0x15a:0x17b])==bytes(pair[1][0x15a:0x17b]),('Farcall SMC',name)
        assert pair[0].rawtags==pair[1].rawtags and pair[0].chr_latches==pair[1].chr_latches
        deltas.add(results[1]['CPU']-results[0]['CPU']);cases+=1
    def freshpair():
        pair=[N.fork(parent),N.fork(new)]
        for m in pair:
            N.put(m,GmVisible=1,CurrentOAMOffset=0,GuestOamRotationActive=0,GmRam0091=0,GmRam0300=8)
            # Explicitly distinct historical query outputs. All graphics must
            # overwrite these with actual facing, not compare with a mask.
            N.put(m,GmTemp2=3 if m is pair[0]else 109)
            m[512:768]=bytes((73*i+29)&255 for i in range(256))
            for name,size in(('GmHistory',20),('GmEffects',28)):
                at=W.address(m.bundle,name);m[at:at+size]=bytes(size)
        return pair
    for pose in range(22):
        for face in(0,1):
            pair=freshpair()
            for m in pair:N.put(m,GmRam0300=pose,GmRam030A=face)
            compare('GmDraw',pair)
    for frame in range(66):
        pair=freshpair()
        for m in pair:
            N.put(m,GmRam0091=1,GmRam0301=frame,GmRam030B=frame&1,GmRam00AF=128,GmRam00B9=8,GmRam009B=128,GmRam00A5=7)
            at=W.address(m.bundle,'GmHistory');m[at:at+20]=bytes((128,8,120,0,128|8))*4
        compare('GmDraw',pair)
    for effect in range(4):
        pair=freshpair()
        for m in pair:
            at=W.address(m.bundle,'GmEffects');m[at:at+4]=bytes((128,8,128,((1 if effect==0 else effect*4)<<4)|7))
        compare('GmDraw',pair)
    for face in(0,1):
        pair=freshpair()
        for m in pair:N.put(m,R4=96,R5=0,R6=120)
        compare('GmPortrait',pair,a=face)
    return dict(passed=True,runtime_SHA256=sha256(raw).hexdigest(),caller_closure=close,complete_Draw_Portrait_pairs=cases,
        full_AXYP_zero_page_private_state_SMC_OAM_maps_exact=True,no_private_RAM_mask=True,graphics_cycle_deltas=sorted(deltas),
        scope='Actual current16a+Gimmick cold constructor and declared full renderer component regressions; no native picture or gameplay claim',outputs=0,Mesen_run=False)


if __name__=='__main__':
    actual=C.ROM.read_bytes()
    def forbid(*args,**kwargs):raise AssertionError('Gimmick caller/art check attempted output/launch')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch('subprocess.Popen',forbid):q=run(actual)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
