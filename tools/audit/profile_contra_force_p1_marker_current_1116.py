"""Actual6a3/ffbb idle/Right source attribution; no physical cadence claim."""
from collections import Counter
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import json
import contra_force_p1_work_marker_model_1116 as M

C,P,N=M.C,M.P,M.N


def profile(raw):
    parent=M.parent(raw);z,_=C.Plan.inputs(parent)
    q=deepcopy(P.bindings(z['reference']));q['bundle']=M.symbols(raw)
    carrier=raw[P.CHR+935*1024:P.CHR+959*1024];q['carrier']=carrier
    for(tag,pc),point in q['points'].items():
        if tag in(1,2,3):point['bytes']=list(carrier[(tag-1)*8192+(pc&8191):(tag-1)*8192+(pc&8191)+8])
        else:point['bytes']=list(raw[point['source_file']:point['source_file']+8])
    count=Counter();base=N.NesMPU
    class Invariant(base):
        def step(self):
            m=self.memory
            if self.pc==0xbe53 and m.rawtags[1]==3 and C.H(raw)==C.CANDIDATE:
                marker=m.ram[2][0x2df]
                if marker&192==128:
                    assert not any(m[514+i*4]&24 for i in range(64)),'Actual no-work phase contains hidden/visible OAM tag'
                    count['no_work_all64_tagfree']+=1
                elif marker&192==192:count['full_work']+=1
                else:count['no_phase']+=1
            return super().step()
    def bindings(image):assert image is raw;return q
    with patch.object(P,'bindings',bindings),patch.object(P,'cold',M.cold),patch.object(N,'NesMPU',Invariant):
        result=P.profile(raw,False)
    result.pop('actual_bc5_CPU_and_private_carrier',None)
    result.update(actual_ROM_CPU_SHA256=C.H(raw),actual_private_payload_SHA256=C.H(carrier),
        truthful_current_hook_bytes_rebound_only=True,candidate_marker_invariant_counts=dict(count),
        prior_profile_code_unchanged=True,new_game_PC_redirects_or_state_seeds=0)
    for phase in result['phases']:
        assert not phase['unclosed_scopes']and not phase['nonlocal_unwinds']
        assert phase['calls']==phase['returns']
        phase.pop('hot_instruction_totals',None)
        phase.pop('mapped_cycles',None)
    return result


if __name__=='__main__':
    raw=C.load_current_image();candidate,_=C.proposal(raw)
    def deny(*a,**kw):raise AssertionError('Source profile attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        before=profile(raw);after=profile(candidate)
    rows=[]
    for a,b in zip(before['phases'],after['phases'],strict=True):
        assert a['phase']==b['phase']and a['calls']==b['calls']
        n=a['calls']['GameLoop']
        rows.append(dict(phase=a['phase'],Main=n,parent_Main_cycles=a['inclusive_excluding_ISR']['GameLoop']/n,
            candidate_Main_cycles=b['inclusive_excluding_ISR']['GameLoop']/n,
            saving_perMain=(a['inclusive_excluding_ISR']['GameLoop']-b['inclusive_excluding_ISR']['GameLoop'])/n,
            parent_P1Late_exclusive=a['innermost_exclusive']['CfP1LateEntry']/n,
            candidate_P1Late_exclusive=b['innermost_exclusive']['CfP1LateEntry']/n))
    q=dict(parent=before,candidate=after,matched_source_costs=rows,outputs=0,native_Mesen=False,physical_cadence_not_qualified=True)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
