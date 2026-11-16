"""Focused owning9826 paired IRQ/busyNMI at shared owner reload, Mini/Sonic."""
from pathlib import Path
from unittest.mock import patch
import inspect,json
import replay_mini_weapon_owner_twoshot_a2_1116 as F
import current_sonic_mini_owner_9826_1116 as Sonic
import check_mini_weapon_owner_interrupts_1116 as Previous

C,N,W=F.C,F.N,F.W
BASE_SHA='c2f6e53b98d0881558256ac3e57ea5907acb74189725daf41a12bddea0c5f958'

TAIL='''    class CPU(base):
        def step(self):
            m=self.memory
            if self.pc in(0xb53c,0xb53f)and m.rawtags[1]==207 and m.bundle.get('raw')is raw and N.get(m,'OperMode')==1 and N.get(m,'GameEngineSubroutine')==8 and N.get(m,'NmiDisable')==255:
                owner=N.get(m,'SelectedCharacter');key=(owner,self.pc)
                if owner in(41,43)and key not in seen:
                    seen.add(key);assert not self.p&4,'Actual shared caller must admit IRQ'
                    endpoint={(0x82be,252),(0x82d0,252)}
                    pair(self,'IRQ',endpoint);pair(self,'busyNMI',endpoint)
                    cuts.append(dict(PC=self.pc,SP=self.sp,P=self.p,owner=owner,power=N.get(m,'PlayerStatus'),scope='Actual Main with unchanged NmiDisableFF'))
            return super().step()
    with patch.object(N,'NesMPU',CPU):
        mini,mini_opening=F.Current.cold(raw,True)
        sonic,sonic_opening=Sonic.cold(raw,'sonic')
        for _ in range(4):sonic.controller_pad=0;Sonic.Frames.frame(sonic,whole_pass=True)
    assert seen=={(owner,pc)for owner in(41,43)for pc in(0xb53c,0xb53f)},seen
    assert counts['IRQ']==counts['busyNMI']==4 and continuations==8
    q=dict(passed=True,ROM_SHA256=C.CANDIDATE,paired_interrupt_counts=dict(counts),reached_contexts=cuts,
        minimum_ISR_SP=minimum,complete_actual_Main_return_continuations=continuations,
        exact_parent_native_audio_effects=True,no_native_RAM_allowlist=True,no_owned_code_ISR_reads=True,
        SMC_scratch_maps_private_and_above_entry_stack_preserved=True,Mini_cold=mini_opening,Sonic_cold=sonic_opening,
        native_effects=[dict(kind=k[0],address=k[1],before=k[2],after=k[3],cases=v)for k,v in sorted(effects.items())],
        unchanged_e32f_large_matrix_not_repeated=True,outputs=0,Mesen=False,
        scope='Actual combined owner41/43 Main cuts at new sharedLDA and followingCMP, paired unchangeda2 ISR effects plus exact uninterruptedcandidate continuation; no artificial NmiDisable state, no deepestISR/hardware cadence claim')
    q['receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q
'''

def run(parent):
    assert C.H(Path(Previous.__file__).read_bytes())==BASE_SHA
    prefix=inspect.getsource(Previous.run).split('    class CPU(base):',1)[0]
    env=dict(Previous.__dict__,F=F,C=C,N=N,W=W,Sonic=Sonic,__file__=__file__)
    exec(compile(prefix+TAIL,'<focusedactual9826 sharedowner pairedIRQ>','exec'),env);return env['run'](parent)

if __name__=='__main__':
    def deny(*a,**kw):raise AssertionError('Combined IRQ smoke attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(C.ROM.read_bytes())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
