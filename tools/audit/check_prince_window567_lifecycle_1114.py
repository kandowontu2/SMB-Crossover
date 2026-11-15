"""Leased source-array lifecycle units, not ROM transport or native proof."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import current_prince_body_research_ae66_1114 as Current
import check_prince_window567_render_1114 as Render

N,W,Frames=Render.N,Render.W,Render.Frames


def snapshot(m):
    bank=W.address(m.bundle,'CurrentCHRBank');mode=W.address(m.bundle,'X5ChrMode')
    return dict(character=N.get(m,'SelectedCharacter'),variant=N.get(m,'MarioVariant'),
        lives=N.get(m,'NumberofLives'),engine=N.get(m,'GameEngineSubroutine'),
        mode=list(m[mode:mode+8]),banks=list(m[bank:bank+8]),latches=m.chr_latches[:],
        hp=m.ram[2][0x6cf],pose=m.ram[2][0x617],guard_active=m.ram[2][0x6e0])


def run(raw):
    current=Current.normalize(raw,kind='bt-service-ae66');reference=current.referenceF11
    parts,_=Render.arrays(reference);oldparts=Render.Packet.extract(reference)[1]
    grant=json.loads(Render.GRANT.read_bytes());mounts=[];native=N.NesMPU
    class CPU(native):
        def step(self):
            m=self.memory
            if self.pc==0xbbc1 and m.rawtags[1]==3:
                first=bytes(m.ram[3][0x1c40:0x1c43])==bytes.fromhex('ac04bd')
                if first:
                    for row in grant['envelopes']:
                        bank=3 if row['stream']==0 else 2;lo=row['live_PC']&8191;size=row['bytes'];offset=row['offset']
                        assert bytes(m.ram[bank][lo:lo+size])==oldparts[row['stream']][offset:offset+size]
                        m.ram[bank][lo:lo+size]=parts[row['stream']][offset:offset+size]
                    prior=snapshot(m)
                    mounts.append(dict(PC=self.pc,SP=self.sp,before_first_publisher=True,
                        native0_before_Prince_mode=prior['mode'][0],native0_before_Prince_bank=prior['banks'][0]))
                for row in grant['envelopes']:
                    bank=3 if row['stream']==0 else 2;lo=row['live_PC']&8191
                    assert bytes(m.ram[bank][lo:lo+row['bytes']])==parts[row['stream']][row['offset']:row['offset']+row['bytes']]
            return super().step()
    def idle(m,count,*,cold=False):
        for _ in range(count):m.controller_pad=0;Frames.frame(m,cold=cold,whole_pass=True)
        N.invoke(m,'X5PublishChr',a=0,x=0,y=0)
    def native_world(m):
        q=snapshot(m);assert q['mode'][1:5]==[0]*4 and q['latches'][1:5]==[16,17,18,19],q
        return q
    with patch.object(N,'NesMPU',CPU):
        m,opening=Render.cold(reference);idle(m,8);cold=native_world(m)
        assert mounts and cold['mode'][5]==129
        assert(cold['mode'][0],cold['banks'][0])==(mounts[0]['native0_before_Prince_mode'],mounts[0]['native0_before_Prince_bank'])
        same=N.fork(m);N.invoke(same,'LoadAreaPointer',a=0,x=0,y=0);idle(same,8)
        area=native_world(same);assert area['mode'][5]==129
        # Explicit compiled death-entry unit: this is not an earned injury or
        # a gameplay clear. No health, actor, position or terrain is supplied.
        death=N.fork(m);N.invoke(death,'KillPlayer',a=0,x=0,y=0);death_entry=snapshot(death)
        lives=N.get(death,'NumberofLives');death_samples=[]
        for tick in range(480):
            idle(death,1,cold=True)
            if tick%60==0:death_samples.append(dict(Main=tick+1,**snapshot(death)))
            if N.get(death,'NumberofLives')<lives and N.get(death,'GameEngineSubroutine')==8:break
        death_end=native_world(death)
        death_completed=death_end['lives']==lives-1 and death_end['engine']==8
        alternates=[]
        for cycles in(0,2):
            bundle=dict(W.Symbols.bundle(),raw=reference);prior=N.Bus;N.Bus=W.ControllerBus
            try:alt=W.UI.seed(bundle,29)
            finally:N.Bus=prior
            for _ in range(cycles):W.UI.key(alt,32)
            selected=N.get(alt,'SelectedCharacter');assert selected==37
            start=W.UI.key(alt,16)
            N.invoke(alt,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
            N.invoke(alt,'PauseRoutine',a=0)
            for tick in range(700):
                if tuple(N.get(alt,name)for name in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
                alt.controller_pad=0;Frames.frame(alt,cold=True,whole_pass=True)
            else:raise AssertionError('Compiled Shinobi alternate cold bound')
            idle(alt,8);alternates.append(dict(compiled_Select_cycles=cycles,Main_parser=tick,**snapshot(alt)))
    q=dict(passed=death_completed,input=current.metadata(),opening=opening,
        source_array_mount_events=mounts,cold_before_first_publisher=cold,same_area_LoadAreaPointer=area,
        compiled_death_entry=death_entry,compiled_death_terminal=death_end,death_samples=death_samples,
        death_lives_respawn_completed=death_completed,compiled_Shinobi_alternates=alternates,
        scope='Three leased arrays mounted before first BBC1 only; compiled source CPU lifecycle units; no ROM transport or physical cadence proof',
        ROM_composed=False,Mesen=False,gameplay_seeds=0,outputs=0)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Source lifecycle attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
