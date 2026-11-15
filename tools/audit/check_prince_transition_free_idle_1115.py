"""Fresh actual idle controls and authentic automatic-draw rule, source only."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json,re
import check_prince_transition_model_1115 as Model
import prince_original_cpu_1101_v1 as Donor

N,Frames=Model.N,Model.Frames


def episode(model,report,ticks):
    labels=json.loads((Model.Body.R/'build/prince-actor-1101-v1/native-labels-v153.json').read_text())
    decode=labels.get('PpN_5_839F')
    if decode is None:
        text=(Model.Body.R/'build/prince-actor-1101-v1/contact-core.lbl').read_text()
        matches={int(value,16)for value in re.findall(r'^al ([0-9a-fA-F]+) \.?PpN_5_839F$',text,re.M)}
        assert len(matches)==1;decode=next(iter(matches))
    initial=Model.state(model);settle=[]
    for step in range(600):
        s=Model.state(model)
        assert not s['guard']and not s['uid'],'No opponent while settling genuine earned pickup'
        if s['pose']==15 and s['action']==0 and model.ram[2][0x618]==0 and model.ram[2][0x6c0]==0:break
        model.controller_pad=0;Frames.frame(model,whole_pass=True)
        if step%40==0:settle.append(dict(Main=step+1,**Model.state(model)))
    else:raise AssertionError('Fresh real idle not reached; controls not tested')
    ready=Model.state(model);cases=[];base=N.NesMPU
    for name in('idle','B','A','Down','B_then_A','B_and_Down'):
        m=N.fork(model);trace=[];last=None;reads=[];current_step=0;requested=0
        class CPU(base):
            def step(self):
                if self.memory is m and self.pc==decode and m.rawtags[1]==3:
                    reads.append(dict(Main=current_step+1,requested=requested,native=N.get(m,'SavedJoypad1Bits'),source=m.ram[2][0x40a]))
                return super().step()
        with patch.object(N,'NesMPU',CPU):
            for current_step in range(96):
                requested=0
                if name=='B':requested=64
                elif name=='A'and current_step<12:requested=128
                elif name=='Down'and current_step<12:requested=4
                elif name=='B_then_A':requested=64 if current_step<32 else 128 if current_step<44 else 0
                elif name=='B_and_Down'and current_step<12:requested=68
                m.controller_pad=requested;Frames.frame(m,whole_pass=True);s=Model.state(m)
                assert s['hp']>0 and s['lives']==2
                assert not s['guard']and not s['uid'],'Actual no-target controls remain separate from re-admission'
                key=tuple(s[k]for k in('sword','marker','action','pose','x','y','hp'))
                if key!=last:trace.append(dict(Main=current_step+1,pad=requested,**s));last=key
        assert reads,'Actual original input decoder not reached'
        expected=0 if name=='idle' else 64 if name in('B','B_then_A') else 128 if name=='A' else 4 if name=='Down' else 68
        assert any(row['source']==expected for row in reads),('Requested buttons never reached actual decoder',name)
        if name=='B_then_A':assert any(row['source']==128 for row in reads)
        cases.append(dict(buttons=name,actual_Main=96,decoded_input_reads=reads[:3]+reads[-3:],
            full_decoded_input_SHA256=sha256(json.dumps(reads,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            actions=sorted({r['action']for r in trace}),sword_states=sorted({r['sword']for r in trace}),
            terminal=Model.state(m),trace=trace[:2]+trace[-4:]if len(trace)>6 else trace,
            full_trace_excluding_marker_SHA256=sha256(json.dumps([{k:v for k,v in r.items()if k!='marker'}for r in trace],sort_keys=True,separators=(',',':')).encode()).hexdigest()))
    return dict(initial_actual_pickup=initial,prefix_Main=ticks,neutral_Main_to_fresh_idle=step,settle=settle,
        actual_fresh_idle=ready,input_decoder_PC=decode,cases=cases)


def run(raw):
    donor=Donor.donor();bank5=donor[16+5*16384:16+6*16384];bank7=donor[-16384:]
    assert bank5[0x8992-0x8000:0x899e-0x8000]==bytes.fromhex('adee06c901d00beeee06a937')
    assert bank7[0xf0cf-0xc000:0xf0d4-0xc000]==bytes.fromhex('ade006f03c')
    records=[]
    for transition in(False,True):
        def stop(m,tick):
            s=Model.state(m)
            return s['sword']==1 and not s['guard']and not s['uid']and s['hp']>0 and N.get(m,'GameEngineSubroutine')==8
        q=Model.run(raw,full=True,limit=4000,transition=transition,frame_observer=stop,after_route=episode)
        assert q['checkpoint_reached']and not q['full_route_completed']
        records.append(dict(transition219=transition,component=q['after_route_component']))
    for a,b in zip(records[0]['component']['cases'],records[1]['component']['cases'],strict=True):
        assert a['buttons']==b['buttons']and a['full_trace_excluding_marker_SHA256']==b['full_trace_excluding_marker_SHA256'],('Actual control behavior changed',a['buttons'])
    q=dict(passed=True,models=records,matched_actual_control_traces_except_request=True,
        original_donor_SHA256=Donor.SHA,original_draw_rule='F0CF requires active opponent before898B;8992 requires sword1 then8999 increments to2',
        free_draw_or_attack_qualification=False,no_gameplay_seeds=True,full_stage_qualified=False,outputs=0,Mesen=False)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Fresh idle source control attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
