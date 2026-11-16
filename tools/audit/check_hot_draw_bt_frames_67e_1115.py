"""Ordinary mounted current67/candidate frame, family and route regressions."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import argparse,json
import compose_hot_draw_bt_67e_1115 as C
import replay_hot_draw_bt_67e_1115 as F
import hot_draw_bt_67e_model_1115 as Model
import check_battletoads_carry_current_1115 as Retained

W,N,Frames=Model.W,Model.N,Model.Frames


def compare(pair):
    Model.compare(pair)
    # Frames' real whole-pass stop is IdleLoop/SP253. Its outer return word
    # remains live at 01FE/01FF, above the preceding Main's dead call frames.
    assert bytes(pair[0][0x1fe:0x200])==bytes(pair[1][0x1fe:0x200]),'Live whole-pass caller word'


def series(pair,pad,count):
    costs=[[],[]];nmis=[[],[]];calls=[Counter(),Counter()];base=N.NesMPU;instances=[]
    main_points=[(((W.location(m.bundle,'GameLoop')-16)//8192)|128,W.address(m.bundle,'GameLoop'))for m in pair]
    class Probe(base):
        def __init__(self,*a,**kw):
            super().__init__(*a,**kw);self.side=0 if self.memory is pair[0]else 1
            assert self.memory is pair[self.side]
            self.kind='Main'if self.pc==W.address(self.memory.bundle,'IdleLoop')else'NMI';instances.append(self)
        def step(self):
            m=self.memory;tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            if(tag,self.pc)==main_points[self.side]:calls[self.side]['GameLoop']+=1
            if(tag,self.pc)==(194,0xb4a4):calls[self.side]['HotNew']+=1
            if(tag,self.pc)==(221,0xadc0):calls[self.side]['BtCheck']+=1
            return super().step()
    with patch.object(N,'NesMPU',Probe):
        for _ in range(count):
            for side,m in enumerate(pair):
                instances.clear();m.controller_pad=pad
                before=calls[side]['GameLoop'];costs[side].append(Frames.frame(m,whole_pass=True))
                assert calls[side]['GameLoop']-before==1,(main_points[side],calls[side],before)
                nmis[side].append(sum(c.processorCycles for c in instances if c.kind=='NMI'))
            compare(pair)
    return dict(Main=count,parent_mean_Main=sum(costs[0])/count,candidate_mean_Main=sum(costs[1])/count,
        Main_savings_histogram=dict(Counter(a-b for a,b in zip(*costs))),actual_calls=[dict(c)for c in calls],
        parent_mean_scheduled_NMI=sum(nmis[0])/count,candidate_mean_scheduled_NMI=sum(nmis[1])/count,
        exact_RAM_OAM_VRAM_PPU_maps_SMC_and_live_caller_word=True,
        each_iteration_one_actual_GameLoop=True,whole_pass_SP=253,previous_full_Main_global_floor=152)


def profile(parent,image):
    pair=[Model.cold(raw)for raw in(parent,image)];compare(pair);series(pair,0,4);rows=[]
    for phase,pad,count in(('idle',0,48),('Right',1,32)):
        q=series(pair,pad,count)
        assert q['Main_savings_histogram']=={499:count}
        assert q['parent_mean_scheduled_NMI']==q['candidate_mean_scheduled_NMI']
        assert q['actual_calls'][0]==q['actual_calls'][1]
        assert not any(N.get(pair[1],'Enemy_Flag',i)for i in range(6))
        q.update(phase=phase,x=N.get(pair[1],'Player_X_Position')+256*N.get(pair[1],'Player_PageLoc'),
            y=N.get(pair[1],'Player_Y_Position'),lives=N.get(pair[1],'NumberofLives'),active_enemies=0)
        rows.append(q);print('PROGRESS '+json.dumps(q),flush=True)
    return dict(phases=rows,genuine_Rash_compiled_cold=True,ordinary_idle_Right_only=True,
        source_scheduled_normal_Main_only=True,native_catchup_or_cadence_not_claimed=True,
        no_actor_health_position_terrain_or_ability_seeds=True)


def family_cold(raw,slot,cycles,name):
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(Model.symbols(raw),0)
    for bits in([4]*(slot//8)+[1]*(slot%8)+[32]*cycles):W.UI.key(m,bits)
    actual=W.UI.menu_name(m)[0];assert actual==name,(slot,cycles,name,actual)
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
        m.controller_pad=0;Frames.frame(m,cold=True)
    else:raise AssertionError(('Compiled foreign constructor bound',name))
    assert N.get(m,'NumberofLives')==2 and N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
    return m


def families(parent,image,wwf=True):
    names=('HULK HOGAN','TED DIBIASE','BAM BAM BIGELOW','HONKY TONK MAN','RANDY SAVAGE','ANDRE THE GIANT')
    specs=[(28,i,n)for i,n in enumerate(names)]if wwf else[(0,8,'MINI MARIO'),(0,9,'MEGA GIANT MARIO'),
        (7,1,'KARNOV'),(21,1,'FF WHITE MAGE'),(25,1,'BUB'),(25,2,'BOB'),(29,1,'PRINCE PERSIA')]
    rows=[]
    for slot,cycles,name in specs:
        pair=[family_cold(raw,slot,cycles,name)for raw in(parent,image)];compare(pair);phases=[]
        for phase,pad in(('idle',0),('Right',1)):
            q=series(pair,pad,4)
            if wwf:assert q['Main_savings_histogram']=={-8:4}
            q['phase']=phase;phases.append(q)
        rows.append(dict(name=name,compiled_menu_slot=slot,Select_cycles=cycles,
            SelectedCharacter=N.get(pair[1],'SelectedCharacter'),FmGroups=N.get(pair[1],'FmGroups'),phases=phases))
        print('PROGRESS '+json.dumps(dict(name=name,phases=phases)),flush=True)
    return dict(actual_compiled_Select_Start_families=rows,ordinary_idle_Right_only=True,
        no_actor_health_position_terrain_or_ability_seeds=True,source_costs_not_native_cadence=True,
        live108_and_ThShared_HotPlayerGraphics_Mini_helpers_unchanged=True)


def lifecycle(parent,image):
    pair=[Model.cold(raw)for raw in(parent,image)];compare(pair);phases=[]
    for phase,pad,count in(('walk',1,8),('pause_edge',16,1),('paused',0,64),('resume_edge',16,1),('resumed',0,8)):
        q=series(pair,pad,count);q.update(phase=phase,pause=N.get(pair[1],'GamePauseStatus'));phases.append(q)
        if phase=='paused':assert q['pause']&1
    assert not N.get(pair[1],'GamePauseStatus')&1
    retired=[N.fork(m)for m in pair]
    out=[N.invoke(m,'BtRetire')for m in retired]
    assert all(m.ram[3][0x1fe0]==0 for m in retired);compare(retired)
    death=[N.fork(m)for m in pair]
    out=[N.invoke(m,'HuDeathStart',a=33,p=0x21)for m in death]
    Research=Retained.Old.M.Research
    Research.compare(death,[dict(r,SP=224,minimum_SP=min(152,r['minimum_SP']))for r in out],'Owning HuDeathStart component')
    assert bytes(death[0][0x1e1:0x200])==bytes(death[1][0x1e1:0x200])
    following=series(death,0,8)
    return dict(ordinary_pause_resume=phases,actual_BtRetire_header_zero=True,
        owning_death_component='HuDeathStart API, not natural damage/pit death',following_death_Main=following,
        natural_death_respawn_continue_not_claimed=True,retire_and_death_data_outputs_equal=True)


def stage(parent,image,key):
    with patch.object(Retained,'Model',Model),patch.object(Retained,'F',F):q=Retained.stage(parent,image,key)
    assert q['actual_candidate_code']and q['normal_controls_only']
    return q


def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=('profile','wwf','foreign','lifecycle','rash','zitz'));args=ap.parse_args()
    raw=C.load_current_image();parent=F.parent(raw);image,_=C.proposal(parent)
    def deny(*a,**kw):raise AssertionError('Frame gate attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Carry.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):
        q={'profile':profile,'wwf':families,'foreign':lambda p,i:families(p,i,False),'lifecycle':lifecycle,
            'rash':lambda p,i:stage(p,i,'rash'),'zitz':lambda p,i:stage(p,i,'zitz')}[args.mode](parent,image)
    q.update(mode=args.mode,parent_SHA256=C.PIN,candidate_SHA256=C.CANDIDATE,actual_mounted_opcodes=True,
        source_only=True,outputs=0,Mesen_run=False)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)


if __name__=='__main__':main()
