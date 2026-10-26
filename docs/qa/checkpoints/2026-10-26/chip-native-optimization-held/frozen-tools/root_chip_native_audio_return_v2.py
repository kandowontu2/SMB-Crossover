"""Regress the real outer return-bank fault found by the native startup run."""
from pathlib import Path
import hashlib
import itertools
import json
from check_tmnt_render_oa import load,address
from check_tmnt_audio_fallback_oc import execute

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')


def run(b,mode=0,variant=0,flags=0x20,phase=0):
    seed=dict(SelectedCharacter=14,OperMode=int(phase!=7),CdVariant=variant,
              CrossoverBehaviorVersion=mode,CurrentBank=215,CurrentBankC=166,
              XgAudioCharacter=255,GamePauseStatus=int(phase==4),
              AreaMusicQueue=[1,0,4,128,0,64,1,0][phase],
              EventMusicQueue=[0,4,0,0,64,8,0,0][phase])
    c,m=execute(b,'AudioUpdate',seed,flags=flags)
    return c,m


def intact(b,c,m):
    return m[address(b,'CurrentBank')]==215 and m.banks[1]==87 and c.sp==255


def main():
    exp=D/'root-chip-native-adapter-v6';out=exp/'outer-return-v1'
    assert not out.exists();out.mkdir()
    before=load(D/'root-chip-native-adapter-v4/candidate.nes');after=load(exp/'candidate.nes')
    c,m=run(before)
    assert not intact(before,c,m),'Original native-found fault must still be reproduced'
    negative=dict(expected_bank_shadow=215,actual_bank_shadow=m[address(before,'CurrentBank')],
                  expected_physical_A=87,actual_physical_A=m.banks[1])
    count=0
    for mode,var,flags,phase in itertools.product([0,1],[0,1],[0x20,0x21,0x60,0x61,0xe0,0xe1],range(8)):
        c,m=run(after,mode,var,flags,phase)
        assert intact(after,c,m),(mode,var,flags,phase,m.banks,m[address(after,'CurrentBank')])
        assert all(m[address(after,name)]==0 for name in ['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos'])
        count+=1
    proof=dict(passed=True,accepted=False,native_run=False,
               candidate_ROM_sha256=hashlib.sha256((exp/'candidate.nes').read_bytes()).hexdigest(),
               original_failed_ROM_sha256=hashlib.sha256(before['raw']).hexdigest(),
               original_fault_reproduced_and_rejected=negative,actual_whole_AudioUpdate_returns=count,
               numeric_modes=[0,1],Chip_Dale_variants=[0,1],cold_pause_silence_event_title=True,
               foreground_bank_shadow_physical_A_stack_and_player_coordinates_exact=True,
               checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               limits='Actual outer-call return regression only. Native corrected-startup/cadence remains unrun.')
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))


if __name__=='__main__':main()
