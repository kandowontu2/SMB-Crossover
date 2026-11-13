"""Separate ordinary roof/low-exit jumps; frozen old full controls stay exact."""
import argparse
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json

import check_dkjr_descending_platform_1113 as D

T,Q,P,H=D.T,D.Q,D.P,D.H


def controller(raw,*,pipes=(1,),stop_after_pipe=None,early_roof=(),settled_source=False,observe_prior=False,cap_roof=False,descending_roof=(),early_ledge=False,native_gap_observer=False,departure_enemy_guard=False):
    assert pipes and all(i in(1,2,3,4)for i in pipes)and len(set(pipes))==len(pipes)
    assert all(i in(2,3)and i in pipes for i in early_roof)
    text=T.controller(raw,full=True)
    selected='('+ ' or '.join('index=='+str(i)for i in pipes)+')'
    boarding='player>=d-2'
    if early_roof:
        early='('+ ' or '.join('index=='+str(i)for i in early_roof)+')'
        height=' and y==cap-32'if cap_roof else''
        text=P.once(text," if phase=='cross'then",f''' if phase=='cross'and {early} and player>=pipe+4 and ram(2,0x6b)==1{height} then setPhase('roof')end
 if phase=='cross'then''')
        boarding=f'({early} and player>=pipe+4 or not {early} and player>=d-2)'
    text=P.once(text," elseif phase=='roof'and carried(d,down)then",f''' elseif phase=='roof'and {selected} and down and {boarding} and ram(2,0x6b)==1 then
  hold=updates+8;rearm=updates+47;remember('original-roof-jump',down);setPhase('jump-down',down)
 elseif phase=='roof'and carried(d,down)then''')
    text=P.once(text," if phase=='lower'and down then",f''' if phase=='lower'and down and {selected} and ram(2,0x6b)==1 and player>=d+9 and y>=160 and y<=176 then
  hold=updates+8;rearm=updates+47;remember('original-low-exit-jump',down);setPhase('depart',down)
 end
 if phase=='lower'and down then''')
    if settled_source:
        text=P.once(text,"  hold=updates+8;rearm=updates+47;remember('original-roof-jump',down);setPhase('jump-down',down)",
            "  if ram(2,0x6c)==1 then hold=updates+8;rearm=updates+47;remember('original-roof-jump',down);setPhase('jump-down',down)else right=false end")
        text=P.once(text,f" if phase=='lower'and down and {selected} and ram(2,0x6b)==1 and player>=d+9",
            f" if phase=='lower'and down and {selected} and ram(2,0x6b)==1 and ram(2,0x6c)==1 and player>=d+9")
    if observe_prior:
        text=P.once(text,'source=ram(2,0x6b),state=',
            'source=ram(2,0x6b),prior_source=ram(2,0x6c),jump_age=ram(2,0x7e),state=')
    if descending_roof:
        assert all(i in(2,3)and i not in pipes for i in descending_roof)
        selected_down='('+ ' or '.join('index=='+str(i)for i in descending_roof)+')'
        text=P.once(text,'if player>=edge and grounded and up-32==y and up>=cap-6 and up<=cap then',
            f"if player>=edge and grounded and up-32==y and up>=cap-6 and up<=cap and (not {selected_down} or (ram(2,0x6c)==1 and read(0x8f+births[tostring(u)].slot)<128))then")
        marker=" if phase=='roof'and index==4 and grounded and carried(d,down)then"
        text=P.once(text,marker,f''' if {selected_down} and down and (phase=='roof'or phase=='lower')then
  if phase=='roof'and carried(d,down)then setPhase('lower',down)end
  right=player<d+31
  if player>=d+31 and ram(2,0x6b)==1 and ram(2,0x6c)==1 and y==down-32 and down>=192 and down<=208 and priorTop[d]and down>=priorTop[d]then
   right=true;setPhase('depart',down)
  end
  bits=(right and 1 or 0)|(updates<hold and 128 or 0);priorTop[u],priorTop[d]=up,down;return
 end
'''+marker)
    if early_ledge:
        text=P.once(text,'if player>=1168 and player<1182 and not ledgeGoomba then',
            'if player>=1160 and player<1182 and ram(2,0x6b)==1 and ram(2,0x6c)==1 and y==176 and not ledgeGoomba then')
    if departure_enemy_guard:
        text=P.once(text," if phase=='depart'then\n  right=true",''' if phase=='depart'then
  if index==3 and ram(2,0x6b)==1 and ram(2,0x6c)==1 and y>=160 and y<=176 and updates>=rearm and nearEnemy(player)then
   hold=updates+8;rearm=updates+47;remember('third-departure-enemy-hop',down)
  end
  right=true''')
    if native_gap_observer:
        assert raw[16+71*8192+0xc18:16+71*8192+0xc1a]==bytes.fromhex('85bd')
        marker="emu.addMemoryCallback(guarded('original gap landing',function()"
        text=P.once(text,marker,'''local nativeGapSupport,nativeGapEntry,nativeGapOverlap
emu.addMemoryCallback(guarded('actual native gap dispatch',function()
 if not active()or not gap.takeoff or phase~='second-gap-jump'or not mapped(0xb98a,'nesPrgRom',0x198a)then return end
 local slot=emu.getState()['cpu.x']
 if not gap.birth or slot~=gap.birth.slot or not gapActor()then return end
 nativeGapEntry={Main=updates,slot=slot,footer=read(0x65b),x=x(),left=gapActor()}
end),emu.callbackType.exec,0xb98a)
emu.addMemoryCallback(guarded('actual native gap overlap',function()
 if not active()or not gap.takeoff or phase~='second-gap-jump'or not mapped(0x9a2c,'nesPrgRom',126*8192+0x1a2c)then return end
 local slot=emu.getState()['cpu.x'];local entry=nativeGapEntry
 if not entry or entry.Main~=updates or slot~=entry.slot or not gapActor()then return end
 local b,p=gapBox(slot),{read(0x658),read(0x659),read(0x65a),read(0x65b)}
 assert(b[3]-b[1]==48 and p[1]<=b[3]and b[1]<=p[3]and p[4]>=b[2]and p[4]-b[2]<6,
  'Actual original native overlap/top predicate')
 assert(x()==entry.x and gapActor()==entry.left and (p[4]==entry.footer or p[4]==entry.footer+2),
  'Actual compiled temporary footer sample')
 nativeGapOverlap={Main=updates,slot=slot,x=x(),left=gapActor(),entry_footer=entry.footer,sampled_box=p,bbox=b}
end),emu.callbackType.exec,0x9a2c)
emu.addMemoryCallback(guarded('actual native gap position',function()
 if not active()or not gap.takeoff or phase~='second-gap-jump'or not mapped(0xac18,'nesPrgRom',71*8192+0xc18)then return end
 local cpu=emu.getState();local slot=cpu['cpu.x']
 if not gap.birth or slot~=gap.birth.slot or not gapActor()then return end
 local b,p=gapBox(slot),{read(0x658),read(0x659),read(0x65a),read(0x65b)}
 assert(read(0x74a)==0 and read(0x10+slot)==1 and read(0x17+slot)==0x28 and read(0x646+slot)==6,
  'Actual stock horizontal actor at native position')
 assert(read(0x566+slot)==slot and read(0xa5+slot)==1 and read(0xa4)==1 and cpu['cpu.a']+32==gapTop,
  'Actual native LPC passenger and pending Y store')
 local overlap=nativeGapOverlap
 assert(overlap and overlap.Main==updates and overlap.slot==slot and p[4]==overlap.entry_footer,
  'Same-update original native overlap and exact footer restoration')
 assert(x()-overlap.x==gapActor()-overlap.left and b[2]==overlap.bbox[2]and b[3]-b[1]==48,
  'Actual native horizontal passenger displacement')
 nativeGapSupport={Main=updates,slot=slot,left=gapActor(),x=x(),snapped_y=cpu['cpu.a'],bbox=b,player_bbox=p,
  original_overlap=overlap,kind='native-platform-position',flag=read(0x566+slot)}
end),emu.callbackType.exec,0xac18)
'''+marker)
        text=P.once(text," assert(p and p.Main==updates and p.x==player and gapActor(),'Gap landing has a live native plane in this update')",''' local native=nativeGapSupport
 local world_ok=p and p.Main==updates and p.x==player and gapActor()
 local native_ok=native and native.Main==updates and native.slot==gap.birth.slot and gapActor()==native.left
  and native.x==player and read(0xbd)==native.snapped_y and read(0x566+native.slot)==native.slot
 assert(world_ok or native_ok,'Gap landing has same-update actual source or native support')''')
        text=P.once(text,' gap.plane_at_landing=p',
            ' if world_ok then gap.plane_at_landing=p else gap.native_support_at_landing=native end')
        text=P.once(text,"assert(gap.land and gap.plane_at_landing,'Original landing on appended native top before the far bank')",
            "assert(gap.land and (gap.plane_at_landing or gap.native_support_at_landing),'Actual source/native platform landing before the far bank')")
    if stop_after_pipe is not None:
        assert stop_after_pipe in(1,2,3,4)
        gate=f'index>{stop_after_pipe}'if stop_after_pipe<4 else"phase=='to-gap'"
        text=P.once(text,'local function drive()\n',
            f"local function drive()\n if {gate} then finish(true,'ordinary-pipe-prefix-{stop_after_pipe}');return end\n")
    return text


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pipes',default='1');ap.add_argument('--stop-after-pipe',type=int)
    ap.add_argument('--early-roof',default='')
    ap.add_argument('--reuse-private',action='store_true')
    ap.add_argument('--settled-source',action='store_true');ap.add_argument('--observe-prior',action='store_true')
    ap.add_argument('--cap-roof',action='store_true')
    ap.add_argument('--descending-roof',default='')
    ap.add_argument('--early-ledge',action='store_true')
    ap.add_argument('--native-gap-observer',action='store_true')
    ap.add_argument('--departure-enemy-guard',action='store_true')
    ap.add_argument('--max-updates',type=int,default=12000)
    a=ap.parse_args();Q.T=T
    parent,candidate=T.load_inputs(reuse_private=a.reuse_private)
    _,seed=H.cold(parent,parent[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    text=controller(candidate,pipes=tuple(int(i)for i in a.pipes.split(',')),stop_after_pipe=a.stop_after_pipe,
        early_roof=tuple(int(i)for i in a.early_roof.split(',')if i),
        settled_source=a.settled_source,observe_prior=a.observe_prior,cap_roof=a.cap_roof,
        descending_roof=tuple(int(i)for i in a.descending_roof.split(',')if i),early_ledge=a.early_ledge,
        native_gap_observer=a.native_gap_observer,departure_enemy_guard=a.departure_enemy_guard)
    m=Q.mounted(seed,candidate)
    with redirect_stdout(io.StringIO()):result=P.B.route(m,candidate,a.max_updates,controller_text=text)
    r=result.get('receipt',{})
    print('DKJR_ORDINARY_LOW_EXIT '+json.dumps(dict(candidate_SHA256=T.PIN,
        controller_SHA256=sha256(text.encode()).hexdigest(),pipes=a.pipes,stop_after_pipe=a.stop_after_pipe,early_roof=a.early_roof,
        settled_source=a.settled_source,observed_prior=a.observe_prior,
        descending_roof=a.descending_roof,
        early_ledge=a.early_ledge,
        native_gap_observer=a.native_gap_observer,
        departure_enemy_guard=a.departure_enemy_guard,
        passed=result['passed'],logical_updates=result['logical_updates'],final=result['final'],
        reason=r.get('reason'),crossings=r.get('crossings'),events=r.get('events'),
        births=r.get('births'),carries=r.get('carries'),injury=r.get('injury'),
        native_actors=[dict(slot=i,id=Q.N.get(m,'Enemy_ID',i),x=Q.N.get(m,'Enemy_X_Position',i)+256*Q.N.get(m,'Enemy_PageLoc',i),
            y=Q.N.get(m,'Enemy_Y_Position',i),state=Q.N.get(m,'Enemy_State',i))for i in range(6)if Q.N.get(m,'Enemy_Flag',i)],
        receipt_SHA256=sha256(json.dumps(r,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        script_RAM_writes=False,ROM_written=False,outputs_written=0,physical_cadence_claim=False),
        separators=(',',':')),flush=True)
    assert result['passed'],'Ordinary-control route did not meet its unchanged or explicitly partial endpoint.'


if __name__=='__main__':main()
