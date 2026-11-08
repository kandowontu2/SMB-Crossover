"""Rebind v200 to two source-declared post-RTS tails on the 244734 nightly."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import prepare_prince_pose_reservation_1103_v185 as M
import check_prince_pose_reservation_1103_v186 as A
import check_prince_control_recipe_1103_v190 as V
import check_prince_deep_foot_branch_isr_1103_v201 as P
O=R/'build/prince-deep-foot-1108-v1'
PARENT=R/'build/mini-two-fireballs-1103/mini-empty-draw.nes'
PIN='244734bbc2690b4e97e654cc72f8f153bedbe3fcc799f714e9508784e4f33af4'
CURRENT=R/'build/prince-resume-1108/prince-current.nes'
CURRENT_PIN='b6df037eeb47743366586a1fe4c91bf9ebe0d922cd5ed6731c4248a86aae943b'
OLD=R/'build/prince-landing-funding-1103-v198'
I,N=A.I,A.N
sha=lambda data:hashlib.sha256(data).hexdigest()


def image():
    source=R/'src/cv3_remaining_source_fx.s'
    prior=OLD/'deep-branch-measurement.json';r=json.loads(prior.read_text())
    proof=OLD/'deep-branch-ABI-ISR.json';assert json.loads(proof.read_text())['passed']
    parent=PARENT.read_bytes();raw=CURRENT.read_bytes()
    assert sha(parent)==PIN and sha(raw)==CURRENT_PIN
    base=dict(M.OLD.image()[0],raw=raw);changes=[]
    src=source.read_text()
    for n,size in [('Cv3FxBatEnter',61),('Cv3FxCancel',57)]:
        body=src.split('.proc '+n+'\n',1)[1].split('.endproc',1)[0]
        assert '\n rts\n .assert *-::'+n in body and f'.res {size}-(*-::{n}),$ea' in body
    def at(b,pc):return 16+8192*b+(pc&0x1fff)
    def change(offset,old,new):
        assert len(old)==len(new) and raw[offset:offset+len(old)]==old,(hex(offset),old.hex())
        changes.append(dict(offset=offset,preimage=old.hex(),replacement=new.hex()))
    assert I.address(base,'Cv3FxBatEnter')==0xb11d and I.address(base,'Cv3FxSceneRequest')==0xb15a
    assert I.address(base,'Cv3FxCancel')==0xb163 and I.address(base,'Cv3FxDeathDispatch')==0xb19c
    assert all((location-16)//8192==82 for location in [I.location(base,n) for n in ['Cv3FxBatEnter','Cv3FxSceneRequest','Cv3FxCancel','Cv3FxDeathDispatch']])
    intervals=[]
    for name,begin,start,end in [('Cv3FxBatEnter',0xb11d,0xb12e,0xb15a),('Cv3FxCancel',0xb163,0xb16d,0xb19c)]:
        before=raw[at(82,begin):at(82,start)];assert before[-1]==0x60
        assert raw[at(82,start):at(82,end)]==b'\xea'*(end-start)
        # The declared live bodies are straight-line except for the same
        # out-of-span direct JSR (queue command). Neither can enter padding.
        assert before==bytes.fromhex({'Cv3FxBatEnter':'089848a9072009bc68a828a9018d145c60',
            'Cv3FxCancel':'9848a9082009bc68a860'}[name])
        pcs=[(n,v['val']) for n,v in base['syms'].items() if v.get('seg') and 'val'in v
            and start<=int(v['val'],0)<end and (I.location(base,n)-16)//8192==82]
        assert not pcs,(name,pcs)
        intervals.append(dict(source=name,CPU_half_open=[start,end],live_body_hex=before.hex(),preceding_RTS=start-1,declared_tail_bytes=end-start))
    assert raw[at(20,0xbd86):at(20,0xbd86)+66]!=b'\xea'*66,'Old v200 span deliberately rejected because Mini uses it'
    orig=r['patches'];first=orig[0]
    change(first['offset'],bytes.fromhex(first['preimage']),bytes.fromhex(first['replacement']))
    wrapper=bytes.fromhex('8d6a01a92e8d6c01a9b18d6d01a9d24c5a01')
    for row in orig[1:5]:change(row['offset'],bytes.fromhex(row['preimage']),wrapper)
    old=bytes.fromhex(orig[5]['replacement']);guard=old[:27]+bytes.fromhex('4c6db1');foreign=old[27:]
    assert len(guard)==30 and len(foreign)==39
    assert foreign[:-2]+foreign[-1:]==raw[at(22,0xba60):at(22,0xba60)+38]
    change(at(82,0xb12e),b'\xea'*len(guard),guard)
    change(at(82,0xb16d),b'\xea'*len(foreign),foreign)
    out=bytearray(raw)
    for p in changes:
        off=p['offset'];b=bytes.fromhex(p['replacement'])
        assert parent[off:off+len(b)]==bytes.fromhex(p['preimage'])
        out[off:off+len(b)]=b
    return base,dict(base,raw=bytes(out)),changes,intervals


def main():
    M.STORAGE.preflight(private_root=O,reserved_bytes=20000,reserved_files=2,fresh=True);O.mkdir(exist_ok=True)
    base,new,changes,tails=image();e,m,lab=A.first8(new)
    foreign=P.foreign(base,new,m);assert foreign['foreign_cases']==61422 and foreign['intended_owned_cases']==18
    native=N.NesMPU;epoch=0;calls=[];back=[]
    class Trace(native):
        def step(self):
            mem=self.memory;pc=self.pc
            old=N.get(mem,'Player_X_Position')+256*N.get(mem,'Player_PageLoc')
            if pc==0xb12e and mem.rawtags[1]==0xd2:calls.append(dict(event='guard',Main=epoch,SP=self.sp,A=self.a,saved_Amap=mem[0x103+self.sp]))
            if pc==0x9c54 and calls and calls[-1]['event']=='guard':calls.append(dict(event='land',Main=epoch,SP=self.sp,A=self.a,Amap=mem.rawtags[1]))
            result=super().step();now=N.get(mem,'Player_X_Position')+256*N.get(mem,'Player_PageLoc')
            if now<old:back.append([epoch,pc,old,now])
            return result
    stage='run';begin=None;rows=[]
    for epoch in range(100):
        s=m.ram[2]
        if stage=='run' and s[0x616]==1 and s[0x618]==1 and 6<=s[0x617]<14:stage='A'
        pad=129 if stage=='A' else 1;m.controller_pad=pad;N.put(m,SavedJoypad1Bits=pad,SavedJoypadBits=pad)
        N.NesMPU=Trace
        try:e['run'](m,'GameLoop',lab)
        finally:N.NesMPU=native
        now=V.row(m,epoch)
        if stage=='A' and now['action']==4:stage='flight';begin=now
        if begin:rows.append(now)
        assert N.get(m,'GameEngineSubroutine')==8 and N.get(m,'NumberofLives')==2 and s[0x6cf]==5
        if begin and epoch>begin['Main']+8 and now['mode']==1 and now['action']==1 and now['foot']>=207:break
    assert not back and rows[-1]['X']==180 and min(r['foot'] for r in rows)==193,(rows[-1],back)
    assert [r['nativeY'] for r in rows if r['Main']==47]==[176]
    assert calls==[dict(event='guard',Main=47,SP=196,A=84,saved_Amap=148),dict(event='land',Main=47,SP=201,A=84,Amap=148)],calls
    result=dict(passed=True,parent_SHA256=PIN,patches=changes,CPU_only=True,ROM_written=False,Mesen_run=False,
        body_frontend_SHA256=CURRENT_PIN,body_frontend_and_landing_memory_SHA256=sha(new['raw']),
        source_funding=dict(physical_bank=82,source='src/cv3_remaining_source_fx.s',intervals=tails,
            no_reachable_fallthrough=True,no_source_labels_inside_tails=True,displaced_Mini_BD86_span_preserved=True),
        comparison=foreign,original_run_jump=dict(last=rows[-1],first_wrong_write_removed=True,source_foot_min=193,calls=calls),
        remaining='Current 244 landing ABI/full Main proved; same 37/37 historical v201 asynchronous topology; current relocated ISR cuts and root native remain separate.',
        bindings={p.relative_to(R).as_posix():M.sha(p) for p in [Path(__file__),PARENT,CURRENT,OLD/'deep-branch-measurement.json',OLD/'deep-branch-ABI-ISR.json',R/'src/cv3_remaining_source_fx.s',R/'src/characters.s',R/'src/collision.s']})
    (O/'landing-contract.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['patches','bindings']}),flush=True)


if __name__=='__main__':main()
