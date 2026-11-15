"""Exact219 source model over owning590 CPU; optional leased body arrays."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse,json
import current_prince_transition_590_1115 as Current
import research_prince_opponent_absence_1114 as Research
import compose_prince_body_world_1114 as Body
import replay_prince_body_earned_wait_stage_1114 as Frozen
import check_prince_natural_sword_1113 as Game
import check_bub_current_budget_1113 as Frames

N,W=Game.N,Game.W
GRANT=Body.R/'docs/qa/allocations/prince-opponent-transition-model-1115.json'
GRANT_SHA='28505a17bab65541abde00900a4fa9c82ad1cd047579f13a306919191e307864'


def state(m):
    s=m.ram[2]
    return dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=N.get(m,'Player_Y_Position'),
        hp=s[0x6cf],lives=N.get(m,'NumberofLives'),sword=s[0x6ee],marker=s[0x6de],
        guard=s[0x6e0],uid=s[0x61c],pose=s[0x617],action=s[0x616],facing=s[0x615],guard_facing=s[0x623])


def run(raw,*,full=False,limit=8500,transition=True,controller_transform=None,frame_observer=None,after_route=None):
    current=Current.normalize(raw,kind='prince-graphics-590')
    data=GRANT.read_bytes();assert sha256(data).hexdigest()==GRANT_SHA;grant=json.loads(data)
    assert sha256(Path(Research.__file__).read_bytes()).hexdigest()==grant['proposal_source_SHA256']
    proposal=Research.importer_plan(current.referenceAE)
    assert sha256(proposal['new']).hexdigest()==grant['proposed_SHA256']
    # The existing historical image is only a frozen input-controller/array
    # dependency. Its ROM bytes are never used by the owning CPU model.
    historical,_=Body.proposal(current.reference1daca);body_parts=Body.Build.Old.Packet.extract(historical)[1]
    text=Frozen.controller(historical,brick_runup=True,combat=True)
    assert sha256(text.encode()).hexdigest()=='a69e9bba0d95df765efcaeddb047e5ff6838a79276237f1bc2aac398046eecef'
    oldcookie=historical[Current.Graphics.Packet.COOKIE:Current.Graphics.Packet.COOKIE+16].hex()
    newcookie=raw[Current.Graphics.Packet.COOKIE:Current.Graphics.Packet.COOKIE+16].hex()
    assert text.count(oldcookie)==1;text=text.replace(oldcookie,newcookie,1)
    assert text.count(Body.digest(historical))==1;text=text.replace(Body.digest(historical),Body.digest(raw),1)
    if controller_transform is not None:text=controller_transform(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','saveState','loadState'))
    Frozen.LuaRuntime().compile(text)
    body_grant=Body.allocation();native=N.NesMPU;owner=None;stage=-1;pending_decode=None
    mounted=[];returns=[];pending_proxy=None;first_publish=None
    def apply(m,bank,pc,new,oldsha,name):
        lo=pc&8191;before=bytes(m.ram[bank][lo:lo+len(new)])
        assert sha256(before).hexdigest()==oldsha,(name,hex(pc),'Source-model preimage differs')
        m.ram[bank][lo:lo+len(new)]=new;mounted.append(dict(name=name,bank=bank,PC=pc,bytes=len(new),new_SHA256=sha256(new).hexdigest()))
    class CPU(native):
        def step(self):
            nonlocal owner,stage,pending_decode,pending_proxy,first_publish
            m=self.memory
            if self.pc==0xc000 and m.rawtags[2]==2:
                owner=m;stage+=1;assert stage<3
                if stage==1:
                    span=body_grant['decoded_spans'][0];lo,hi=span['decoded_half_open']
                    apply(m,3,span['live_CPU_half_open'][0],body_parts[0][lo:hi],span['preimage_SHA256'],'leased449World')
                if stage==2:
                    if transition:apply(m,2,Research.START,proposal['new'],grant['preimage_SHA256'],'transition219')
                    ret=m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1
                    pending_decode=(ret,(self.sp+2)&255)
            if m is owner and pending_decode==(self.pc,self.sp):
                span=body_grant['decoded_spans'][1];lo,hi=span['decoded_half_open']
                # Third stream is still STAGED here. Its real cold80-byte
                # down-copy subsequently transports the granted Prepare.
                apply(m,2,0xc100+lo,body_parts[2][lo:hi],span['preimage_SHA256'],'leased180PrepareStaged')
                pending_decode=None
            if m is owner and self.pc==0xbbc1 and m.rawtags[1]==3 and first_publish is None:
                assert len(mounted)==(3 if transition else 2)and pending_decode is None
                cookie=raw[Current.Graphics.Packet.COOKIE:Current.Graphics.Packet.COOKIE+16]
                assert all(bytes(m.ram[b][0x1fe0:0x1ff0])==cookie for b in(2,3))
                parts=Current.Graphics.Packet.extract(raw)[1]
                for row in Current.Graphics.allocation()['decoded_envelopes']:
                    bank=3 if row['stream']==0 else 2;pc=(0xa000 if bank==3 else 0xc800)+row['offset']
                    assert bytes(m.ram[bank][pc&8191:(pc&8191)+row['bytes']])==parts[row['stream']][row['offset']:row['offset']+row['bytes']]
                span=body_grant['decoded_spans'][1];pc=span['live_CPU_half_open'][0]
                assert sha256(bytes(m.ram[2][pc&8191:(pc&8191)+180])).hexdigest()==span['proposed_SHA256']
                first_publish=dict(PC=self.pc,SP=self.sp,both_current_cookies=True,all_qualified_graphics_exact=True,live_Prepare180_exact=True)
            if m is owner and self.pc==Research.START and m.rawtags[2]==2:
                assert sha256(bytes(m.ram[2][Research.START&8191:Research.END&8191])).hexdigest()==grant['proposed_SHA256'if transition else'preimage_SHA256']
                ret=m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1
                pending_proxy=(ret,(self.sp+2)&255,state(m))
            if m is owner and pending_proxy and(self.pc,self.sp)==pending_proxy[:2]:
                before=pending_proxy[2];after=state(m)
                if before['guard']!=after['guard']or before['uid']!=after['uid']:
                    returns.append(dict(before=before,after=after))
                    assert len(returns)<96
                pending_proxy=None
            return super().step()
    with patch.object(N,'NesMPU',CPU),patch.object(Game,'proof_parent',lambda image:raw if image==raw else (_ for _ in()).throw(AssertionError('Wrong owning model'))):
        model,opening=Game.cold(raw)
        assert model.bundle['raw']==raw and stage==2 and first_publish
        q=dict(passed=True,input=current.metadata(),lease_SHA256=GRANT_SHA,opening=opening,model_only_mounts=mounted,
            first_actual_publication=first_publish,controller_SHA256=sha256(text.encode()).hexdigest(),
            actual_CPU_ROM_SHA256=sha256(model.bundle['raw']).hexdigest(),combined_ROM_composed=False,outputs=0,Mesen=False)
        if full:
            actual=Frames.frame;ticks=0;cold_class=type(model)
            class CheckpointReached(Exception):pass
            def frame(m,*args,**kwargs):
                nonlocal ticks
                result=actual(m,whole_pass=True);ticks+=1
                if ticks%500==0:print(json.dumps(dict(event='transition-current-model',Main=ticks,**state(m)),separators=(',',':')),flush=True)
                if frame_observer is not None and frame_observer(m,ticks):raise CheckpointReached()
                return result
            checkpoint=False
            try:
                with patch.object(Game,'controller',lambda image:text),patch.object(Game.Frames,'frame',frame):proof=Game.route(model,raw,limit)
            except CheckpointReached:proof=dict(passed=False,scope='Declared genuine CPU checkpoint, not a full-stage clear');checkpoint=True
            finally:model.__class__=cold_class
            proof.pop('events',None);proof.pop('sword_trace',None)
            if isinstance(proof.get('flower'),dict):proof['flower']={k:v for k,v in proof['flower'].items()if k!='trace'}
            q.update(passed=proof['passed']or checkpoint,full_route_completed=proof['passed'],checkpoint_reached=checkpoint,
                proof=proof,actual_opponent_transitions=returns,terminal=state(model),transition_model=transition,
                scope='Owning590 compiled cold plus only root-leased body449/Prepare180/transition219 arrays; ordinary frozen inputs')
            if after_route is not None:q['after_route_component']=after_route(model,q,ticks)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--full',action='store_true');p.add_argument('--limit',type=int,default=8500);a=p.parse_args()
    def deny(*args,**kwargs):raise AssertionError('Source model attempted file output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes(),full=a.full,limit=a.limit)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
