"""Failure locals for the narrowly scoped audio successor; no wider mask."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import check_prince_transition_interrupts_audio_1115 as Audio
import trace_prince_transition_interrupt_failure_1115 as Detail

PIN='c5682faa088f3cb8d50f56e5b836cf580862d9e42cd3d7467fcc4034ec01702e'


def run(raw):
    assert sha256(Path(Audio.__file__).read_bytes()).hexdigest()==PIN
    try:q=Audio.run(raw)
    except AssertionError as error:
        frames=[];tb=error.__traceback__;probe=None;validation=None
        while tb:
            f=tb.tb_frame;frames.append(dict(function=f.f_code.co_name,line=tb.tb_lineno,file=f.f_code.co_filename))
            if f.f_code.co_name=='interrupt':probe=f.f_locals
            if f.f_code.co_name=='validate':validation=f.f_locals
            tb=tb.tb_next
        assert probe is not None,('No reached interrupt frame',frames)
        try:Detail.fail(*(probe[key]for key in('cpu','m','before','after','regs','left','right','protected','kind','base')))
        except Detail.DetailedDifference as captured:q=captured.q
        q['scoped_audio_successor_source_SHA256']=PIN;q['exception_frames']=frames[-4:]
        q['square1_actual_writer_events']=getattr(probe['c'],'square1_writes',[])
        q['remaining_native_differences_after_declared_masks']=q.pop('native_difference_after_existing7DA_mask')
        if validation:q['validation_values']={key:validation[key]for key in('old','new','row')if key in validation}
        q['scoped_successor_passed']=False
    else:q['scoped_successor_passed']=True
    q['failure_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Audio scope diagnostic attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
