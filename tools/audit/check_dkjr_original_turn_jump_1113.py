"""Qualify the donor's real backward-facing Right+A control, without seeds."""
import json
import argparse
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'reference'))
import dkjr_original_cpu_1102_v1 as D


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--current',action='store_true')
    args=ap.parse_args()
    c,opening=D.active();history=[];bounds=[]
    def observe(cpu):
        mem=cpu.memory
        if cpu.pc==0xd2e4:
            pointer=mem[0xc369+cpu.x]+256*mem[0xc36a+cpu.x]
            bounds.append(dict(source=mem[0x6b],facing=mem[0x6d],direction=mem[0x54],
                pointer=pointer,offsets=list(mem[pointer:pointer+4])))
    for age in range(16):
        D.frame(c,2,observe)
        history.append(dict(pad=2,**D.state(c)))
        if c.memory[0x6b]==1 and c.memory[0x6d]==0:break
    else:raise AssertionError('Ordinary original Left did not establish grounded facing0')
    for _ in range(12):
        D.frame(c,129,observe)
        history.append(dict(pad=129,**D.state(c)))
    actual=[r for r in bounds if r['source']==3 and r['facing']==0 and r['direction']==4]
    assert actual and all(q['pointer']==0xc38d and q['offsets']==[5,0,24,15]for q in actual),actual
    print('DKJR_ORIGINAL_TURN_JUMP '+json.dumps(dict(original_SHA256=D.SHA,
        opening_NMI_epochs=opening,backward_facing_right_jump_admitted=True,
        actual_original_bounds=actual[:4],ordinary_control_history=history,
        source_or_ROM_seeds=False,outputs_written=0,
        scope='Original NROM instructions with untimed PPU-ready model. No SMB stair or physical cadence qualification.'),separators=(',',':')),flush=True)
    if args.current:
        import check_dkjr_final_stair_branches_1113 as B
        parent,candidate=B.T.load_inputs();e73=B.T.Old.reverse(parent)
        _,seed=B.H.cold(e73,e73[B.P.B.COOKIE_AT:B.P.B.COOKIE_AT+16])
        model=B.Q.mounted(seed,candidate);seen=[];trail=[]
        for opening_wait in range(160):
            s=B.state(model)
            if s['y']==176 and s['source_state']==s['prior']==1 and s['state']==0:break
            B.Q.frame(model,0)
        else:raise AssertionError(('Current opening did not naturally settle',B.state(model)))
        def native_observe(mem,cpu):
            if mem.rawtags[1]==3 and cpu.pc==B.P.T.RECT_START and cpu.a==0 and mem.ram[2][0x6b]==3:
                pointer=mem.ram[2][2]+256*mem.ram[2][3]
                seen.append(dict(source=mem.ram[2][0x6b],facing=mem.ram[2][0x6d],
                    direction=mem.ram[2][0x54],pointer=pointer,offsets=list(mem[pointer:pointer+4])))
        for _ in range(8):
            B.Q.frame(model,2,native_observe)
            if model.ram[2][0x6b]==1 and model.ram[2][0x6d]==0:break
        else:raise AssertionError(('Current ordinary Left did not establish facing0',B.state(model)))
        for _ in range(8):
            B.Q.frame(model,129,native_observe);trail.append(B.state(model))
        actual=[q for q in seen if q['facing']==0 and q['direction']==4]
        assert actual and all(q['offsets']==[5,0,24,15]for q in actual),seen
        print('DKJR_CURRENT_TURN_JUMP '+json.dumps(dict(candidate_SHA256=B.T.PIN,
            natural_neutral_opening_updates=opening_wait,
            actual_compiled_bounds=actual[:4],history=trail,source_or_native_seeds=False,
            outputs_written=0,scope='Genuine current cold opening plus ordinary Left/Right+A. No stair or physical cadence qualification.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
