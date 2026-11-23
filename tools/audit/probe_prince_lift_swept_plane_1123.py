"""Exact lift candidate: translated falling Worker/collision evidence only.

No natural-route, candidate-install or native claim. All fixtures stay in RAM;
the genuine source Fall, terrain contact, native platform and mapper run.
"""
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import compose_prince_oneup_lift_1123 as C
import replay_prince_oneup_lift_1123 as R

F, H, W, N = C.Lift.F, C.H, C.W, C.Lift.N


def swept_prototype(parent, image):
    """Append an unfunded raw1 diagnostic leaf; leave the frozen plan alone."""
    blob, labels, _, _, _ = C.Lift.plan(parent)
    assert C.extract(image)[0][3] == blob
    material = labels['Material']
    fields = F.symbols(parent)
    vector = W.address(dict(W.Symbols.bundle(),raw=parent),'FarcallJmpTarget_SMC') + 1
    far = W.address(dict(W.Symbols.bundle(),raw=parent),'FarCallCommon')
    # Existing Material starts with this15-byte nested native fallback call.
    assert blob[material-0xa000:material-0xa000+15] == bytes((
        0xa9,0xd1,0x8d,vector&255,vector>>8,0xa9,0xd6,0x8d,
        (vector+1)&255,(vector+1)>>8,0xa9,3,0x20,far&255,far>>8))
    wrapper = f'''MaterialSweep:
 php
 pha
 txa
 pha
 tya
 pha
 jsr Sweep
 bcs AcceptSweep
 pla
 tay
 pla
 tax
 pla
 plp
 lda #209
 sta ${vector:04x}
 lda #214
 sta ${vector+1:04x}
 lda #3
 jsr ${far:04x}
 jmp ${material+15:04x}
AcceptSweep:
 sta $c07f
 sta $c09b
 lda #0
 sta $c080
 sta $c09c
 lda #1
 sta $c09f
 pla
 tay
 pla
 tax
 pla
 plp
 lda #1
 rts
'''
    sweep = F.ASM.split('Support:\n',1)[1]
    sweep = R.P.G.First.once(sweep,''' lda Player_State
 ora Player_Y_Speed
 jne Fail
''',''' lda $c085
 ora $c087
 jne Fail
 lda $c618
 cmp #3
 beq FallingMode
 cmp #4
 jne Fail
FallingMode:
 lda $c084
 sec
 sbc $c086
 bcc BadMotion
 beq BadMotion
 cmp #29
 bcc MotionOK
BadMotion:
 jmp Fail
MotionOK:
''')
    sweep = R.P.G.First.once(sweep,''' txa
 cmp PlatformCollisionFlag,x
 bne Next
 lda Player_Y_Position
 clc
 adc #32
 bcs Next
 cmp Enemy_Y_Position,x
 bne Next
''',''' lda $c086
 cmp Enemy_Y_Position,x
 bcc PlaneAfterOld
 beq PlaneAfterOld
 jmp Next
PlaneAfterOld:
 lda $c084
 cmp Enemy_Y_Position,x
 bcc Next
''')
    code, newlabels = C.Lift.assemble(wrapper+'Sweep:\n'+sweep,fields,0xa000+len(blob))
    out = bytearray(blob+code)
    at = material-0xa000
    out[at:at+3] = bytes((0x4c,newlabels['MaterialSweep']&255,newlabels['MaterialSweep']>>8))
    return bytes(out),newlabels


def load_prototype(m, blob):
    out = N.fork(m)
    out.ram[1][:len(blob)] = blob
    return out


def compact_plan(parent, width=32, logical_history=False, *, builder=None):
    assert width in (32, 48)
    if builder is None:
        builder = C.Lift.plan
    # The common typed-owner/actor search is shared by carried and swept
    # contacts. This is an additive in-memory alternate to the frozen plan.
    prefix = F.ASM.split('Material:\n',1)[0]
    text = prefix + '''Material:
 php
 pha
 txa
 pha
 tya
 pha
 jsr Support
 bcs MaterialAccept
 jsr Sweep
 bcs MaterialAccept
 pla
 tay
 pla
 tax
 pla
 plp
 jsr $bde2
 rts
MaterialAccept:
 sta $c07f
 sta $c09b
 lda #0
 sta $c080
 sta $c09c
 lda #1
 sta $c09f
 pla
 tay
 pla
 tax
 pla
 plp
 lda #1
 rts
Support:
 jsr Eligible
 bcc SupportNo
 lda Player_State
 ora Player_Y_Speed
 bne SupportNo
 jsr Actor
 bcc SupportNo
 txa
 cmp PlatformCollisionFlag,x
 bne SupportNo
 lda Player_Y_Position
 clc
 adc #32
 bcs SupportNo
 cmp Enemy_Y_Position,x
 bne SupportNo
 lda Enemy_Y_Position,x
 sec
 rts
SupportNo:
 clc
 rts
Sweep:
 jsr Eligible
 bcc SweepNo
 lda $c085
 ora $c087
 bne SweepNo
 lda $c618
 cmp #3
 beq SweepMode
 cmp #4
 bne SweepNo
SweepMode:
 lda $c084
 sec
 sbc $c086
 bcc SweepNo
 beq SweepNo
 cmp #29
 bcs SweepNo
 jsr Actor
 bcc SweepNo
 lda $c086
 cmp Enemy_Y_Position,x
 bcc SweepAfterOld
 beq SweepAfterOld
 bcs SweepNo
SweepAfterOld:
 lda $c084
 cmp Enemy_Y_Position,x
 bcc SweepNo
 lda Enemy_Y_Position,x
 sec
 rts
SweepNo:
 clc
 rts
Eligible:
 lda SelectedCharacter
 cmp #38
 bne EligibleNo
 lda GameEngineSubroutine
 cmp #8
 bne EligibleNo
 lda WorldNumber
 ora LevelNumber
 ora TimerControl
 ora GamePauseStatus
 bne EligibleNo
 lda AreaAddrsLOffset
 cmp #5
 bne EligibleNo
 lda AreaType
 cmp #1
 bne EligibleNo
 lda $c0ab
 cmp #167
 bne EligibleNo
 lda $c6cf
 beq EligibleNo
 lda Player_Y_HighPos
 cmp #1
 bne EligibleNo
 sec
 rts
EligibleNo:
 clc
 rts
Actor:
 ldx #5
ActorSlot:
 lda Enemy_Flag,x
 cmp #1
 bne ActorNext
 lda Enemy_ID,x
 cmp #37
 bne ActorNext
 lda Enemy_State,x
 bne ActorNext
 lda Enemy_Y_HighPos,x
 cmp #1
 bne ActorNext
 lda Enemy_BoundBoxCtrl,x
 cmp #5
 bne ActorNext
 lda Enemy_X_Position,x
 cmp #240
 bne ActorNext
 lda Enemy_PageLoc,x
 cmp #3
 bne ActorNext
 lda Player_X_Position
 clc
 adc #13
 tay
 lda Player_PageLoc
 adc #0
 pha
 tya
 sec
 sbc Enemy_X_Position,x
 tay
 pla
 sbc Enemy_PageLoc,x
 bne ActorNext
 cpy #43
 bcs ActorNext
 lda Enemy_Y_Position,x
 sec
 rts
ActorNext:
 dex
 bpl ActorSlot
 clc
 rts
'''
    once = F.Q.P.G.First.once
    if logical_history:
        # A carried player's animated bounding box can extend below the lift.
        # Save the supporting surface for the next foot sweep while the
        # physical-foot routine still computes the original visible pose.
        text = once(text, ' bcc ImportDone\n sec\n sbc $c611',
                    ' bcc ImportDone\n sta $c086\n sec\n sbc $c611')
        text = once(text, ' sta $c089\n lda #0\n sbc #0',
                    ' sta $c089\n lda #0\n sta $c087\n sbc #0')
        text = once(text, ' jsr $c312\n lda $c084\n sta $c086\n lda $c085\n sta $c087',
                    ' jsr $c312')
    if width == 32:
        with patch.object(F,'ASM',text):
            return builder(parent)

    text = once(text, ' lda Enemy_BoundBoxCtrl,x\n cmp #5',
                ' lda Enemy_BoundBoxCtrl,x\n cmp #6')
    text = once(text, ' cpy #43', ' cpy #59')
    text = once(text, ' lda $c086\n cmp Enemy_Y_Position,x\n bcc SweepAfterOld\n'
                ' beq SweepAfterOld\n bcs SweepNo\nSweepAfterOld:',
                ' lda Enemy_Y_Position,x\n cmp $c086\n bcc SweepNo')
    admission = C.Lift.Admission
    allocator = once(admission.ASM, ' lda #5\n sta Enemy_BoundBoxCtrl,x',
                     ' lda #6\n sta Enemy_BoundBoxCtrl,x')
    with patch.object(F, 'ASM', text), patch.object(admission, 'ASM', allocator):
        blob, labels, parts, packed, info = builder(parent)
    return blob, labels, parts, packed, dict(info, lift_width=width)


def wide_plan(parent):
    return compact_plan(parent, width=48)


def hold_plane_plan(parent):
    return compact_plan(parent, width=48, logical_history=True)


def direct(m, address):
    b = m.bundle
    target = W.address(b,'FarcallJmpTarget_SMC')+1
    m[target:target+2] = address.to_bytes(2,'little')
    return F.private(m,W.address(b,'FarCallCommon'),a=1)


def negatives(seed, blob, labels, width=32):
    base = load_prototype(fixture(seed),blob)
    box = 6 if width == 48 else 5
    F.slot(base, 'Enemy_BoundBoxCtrl', box)
    base.ram[2][0x84:0x88] = bytes((198,0,187,0))
    assert direct(N.fork(base),labels['Sweep'])['regs'][3]&1
    checks = (
        ('rising',0x84,180),('stationary',0x84,187),
        ('plane-already-above-old-foot',0x86,193),('not-yet-at-plane',0x84,191),
        ('oversized-step',0x86,100),('current-out-of-live-plane',0x85,1),
        ('previous-out-of-live-plane',0x87,1),('non-falling-mode',0x618,2),
        ('unready',0xab,0),('dead',0x6cf,0),
    )
    done = []
    for name,offset,value in checks:
        m = N.fork(base);m.ram[2][offset]=value
        before = bytes(m.ram[2])
        q = direct(m,labels['Sweep'])
        assert not q['regs'][3]&1 and bytes(m.ram[2])==before,name
        assert m.rawtags[1:3]==[3,2],name
        done.append(name)
    checks = (
        ('foreign-owner','SelectedCharacter',37,None),
        ('wrong-stage','LevelNumber',1,None),('wrong-area','AreaAddrsLOffset',4,None),
        ('underwater','AreaType',0,None),('paused','GamePauseStatus',1,None),
        ('timer','TimerControl',1,None),('not-playing','GameEngineSubroutine',7,None),
        ('player-off-plane','Player_Y_HighPos',2,None),
        ('inactive','Enemy_Flag',0,5),('non-exclusive','Enemy_Flag',2,5),
        ('wrong-actor','Enemy_ID',6,5),('wrong-state','Enemy_State',64,5),
        ('actor-off-plane','Enemy_Y_HighPos',2,5),('wrong-width','Enemy_BoundBoxCtrl',11-box,5),
        ('wrong-left','Enemy_X_Position',239,5),('wrong-page','Enemy_PageLoc',4,5),
    )
    for name,field,value,slot in checks:
        m = N.fork(base)
        if slot is None:N.put(m,**{field:value})
        else:F.slot(m,field,value,slot)
        before = bytes(m.ram[2]);q=direct(m,labels['Sweep'])
        assert not q['regs'][3]&1 and bytes(m.ram[2])==before,name
        done.append(name)
    for name,x in (('left-no-overlap',994),('right-no-overlap',1006+width)):
        m=N.fork(base);N.put(m,Player_X_Position=x&255,Player_PageLoc=x>>8)
        before=bytes(m.ram[2]);q=direct(m,labels['Sweep'])
        assert not q['regs'][3]&1 and bytes(m.ram[2])==before,name
        done.append(name)
    return dict(rejected=done,readonly_source_fields=True,maps_restored=True)


def continued_landing(m):
    rows=[];settled=0;contacts=0
    for tick in range(96):
        N.put(m,FrameCounter=(121+tick)&255,SavedJoypadBits=0,SavedJoypad1Bits=0,
              A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0)
        F.private(m,0xb36e)
        q=F.native_platform(m)
        s=m.ram[2]
        attached=q['flag']==5 and q['y']+32==q['top']
        contacts+=attached
        state=list(s[0x616:0x619])
        if not rows or state!=rows[-1]['source']:
            rows.append(dict(tick=tick,source=state,native=q))
        settled=settled+1 if attached and state==[0,15,0]else 0
        assert s[0x6cf]==5 and N.get(m,'NumberofLives')==2,rows
    assert settled>=25,rows
    return dict(updates=96,contacts=contacts,settled_final_contacts=settled,
                HP=5,lives=2,original_states=rows)


def held_fixture(seed):
    m=fixture(seed);s=m.ram[2]
    F.slot(m,'Enemy_Y_Position',194)
    F.slot(m,'PlatformCollisionFlag',5)
    N.put(m,Player_Y_Position=162,Player_State=0,Player_Y_Speed=0)
    s[0x611]=s[0x8b]=114;s[0x88]=4;s[0x617]=106;s[0x4e2]=13
    s[0x84:0x88]=bytes((195,0,195,0))
    return m


def fixture(seed):
    m = F.scene(seed, x=1016, top=192)
    N.put(m, Player_Y_Position=155, Player_Y_HighPos=1,
          Player_State=2, Player_Y_Speed=11,
          SavedJoypadBits=0, SavedJoypad1Bits=0, A_B_Buttons=0,
          Left_Right_Buttons=0, Up_Down_Buttons=0)
    s = m.ram[2]
    for at, value in ((0x611,107),(0x8b,107),(0x88,3),(0x89,77),
                      (0x8a,0),(0x616,18),(0x617,104),(0x618,4),
                      (0xa6,3),(0x4e1,0),(0x4e2,9),(0x6db,0),
                      (0x4d4,0),(0x6da,0),(0x6dd,0)):
        s[at] = value
    s[0x84:0x88] = bytes((187,0,187,0))
    assert s[0xab] == 167 and s[0x6cf] == 5
    return m


def observe(m):
    s = m.ram[2]
    sites = {0xa022:'Fall',0xa5d9:'Terrain',0xa6f6:'Material-call',
             0xa70b:'Material-gateway',0xa05f:'Material-raw1',
             0xd6d1:'Original-fallback',0xbde2:'WorldMaterial',
             0xc312:'PhysicalFoot',0xb3bd:'After-terrain',
             0xb3c0:'Copy-OldFoot-low',0xb3c6:'Copy-OldFoot-high'}
    rows, writers, state_writers = [], [], []
    base = N.NesMPU

    class Spy(base):
        def step(self):
            pc = self.pc
            tag = m.rawtags[(pc-0x8000)//8192] if pc >= 0x8000 else None
            if pc in sites and ((tag in (2,3) and pc != 0xa05f) or (tag == 1 and pc == 0xa05f)):
                rows.append(dict(site=sites[pc],PC=hex(pc),bank=tag,
                    foot=int.from_bytes(s[0x84:0x86],'little'),
                    prior=int.from_bytes(s[0x86:0x88],'little'),
                    action_pose_mode=list(s[0x616:0x619]),sourceY=s[0x611],
                    plane=list(s[0x7f:0x81]),floor=list(s[0x9b:0xa0])))
            old = bytes(s[0x86:0x88])
            old_state = bytes(s[0x616:0x619])
            result = super().step()
            if old != bytes(s[0x86:0x88]):
                writers.append(dict(PC=hex(pc),bank=tag,before=old.hex(),after=bytes(s[0x86:0x88]).hex()))
            if old_state != bytes(s[0x616:0x619]):
                state_writers.append(dict(PC=hex(pc),bank=tag,before=list(old_state),after=list(s[0x616:0x619])))
            return result

    with patch.object(N,'NesMPU',Spy):
        worker = F.private(m,0xb36e)
    at = W.address(m.bundle,'ChkForTopCollision')
    top = W.address(m.bundle,'BoundingBox_UL_YPos')
    bottom = W.address(m.bundle,'BoundingBox_DR_YPos')
    collision = []

    class NativeSpy(base):
        def step(self):
            if self.pc == at:
                collision.append(dict(player_bottom=m[bottom],platform_top=m[top+self.y],
                    difference=(m[bottom]-m[top+self.y])&255,
                    foot=int.from_bytes(s[0x84:0x86],'little'),
                    prior=int.from_bytes(s[0x86:0x88],'little'),X=self.x,Y=self.y))
            return super().step()

    with patch.object(N,'NesMPU',NativeSpy):
        native = F.native_platform(m)
    return dict(worker=worker,source=rows,old_foot_writers=writers,state_writers=state_writers,
                native_top_tests=collision,native=native,
                final_source=dict(foot=int.from_bytes(s[0x84:0x86],'little'),
                    prior=int.from_bytes(s[0x86:0x88],'little'),
                    action_pose_mode=list(s[0x616:0x619]),HP=s[0x6cf]))


def wide_test(parent, planner):
    image, overlay = C.compose(parent, planner)
    blob, labels, _, _, _ = planner(parent)
    seed = R.cold(image, overlay)
    for _ in range(12):
        seed.controller_pad = 0
        R.Engine.Frames.frame(seed, cold=True)

    fresh = fixture(seed)
    F.slot(fresh, 'Enemy_BoundBoxCtrl', 6)
    landed = observe(fresh)
    assert landed['native']['flag'] == 5 and landed['final_source']['foot'] == 192
    assert landed['final_source']['action_pose_mode'][0] == 17
    held = held_fixture(seed)
    F.slot(held, 'Enemy_BoundBoxCtrl', 6)
    history = None
    if planner == hold_plane_plan:
        direct_import = N.fork(held)
        F.private(direct_import, 0xb3d1)
        history = dict(foot=direct_import.ram[2][0x84], previous=direct_import.ram[2][0x86])
        assert history == dict(foot=195, previous=194)
    carried = observe(held)
    assert carried['native']['flag'] == 5 and carried['final_source']['action_pose_mode'][0] == 17
    continued = continued_landing(fresh)
    rejected = negatives(seed, blob, labels, width=48)
    report = dict(ROM=H(image), width=48, fresh=landed['native'], held=carried['native'],
                  continued=continued, rejected=rejected, outputs=0)
    if history is not None:
        report['held_import_history'] = history
    digest = H(json.dumps(report, sort_keys=True, separators=(',', ':')).encode())
    print('PRINCE WIDE LIFT SOURCE ' + json.dumps(dict(report, receipt=digest),
                                                  separators=(',', ':')), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wide-lift', action='store_true')
    parser.add_argument('--hold-plane', action='store_true')
    args = parser.parse_args()
    parent = R.P.G.ROM.read_bytes()
    assert H(parent) == C.PARENT
    image, overlay = C.compose(parent)
    def deny(*a,**k):raise AssertionError('Swept-plane probe attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        if args.wide_lift or args.hold_plane:
            wide_test(parent, hold_plane_plan if args.hold_plane else wide_plan)
            return
        seed = R.cold(image,overlay)
        for _ in range(12):seed.controller_pad=0;R.Engine.Frames.frame(seed,cold=True)
        result = observe(fixture(seed))
        assert any(r['site']=='Material-gateway' and r['foot']==198 and r['prior']==187
                   for r in result['source'])
        assert result['native_top_tests'][0]['difference'] == 6
        assert result['native']['flag'] == 255
        prototype, labels = swept_prototype(parent,image)
        fixed = observe(load_prototype(fixture(seed),prototype))
        assert fixed['native']['flag']==5 and fixed['final_source']['foot']==192
        assert fixed['final_source']['action_pose_mode'][0]==17
        assert {r['PC']for r in fixed['state_writers']}=={'0xa352','0xa365'}
        assert all(r['bank']==3 for r in fixed['state_writers'])
        rejected = negatives(seed,prototype,labels)
        compact, compact_labels, compact_parts, compact_packed, compact_info = compact_plan(parent)
        compact_fixture = C.Lift.load_fixture(fixture(seed),compact,compact_parts)
        compact_result = observe(compact_fixture)
        assert compact_result['native']['flag']==5 and compact_result['final_source']['foot']==192
        assert compact_result['final_source']['action_pose_mode'][0]==17
        assert compact_result['state_writers']==fixed['state_writers']
        compact_rejected = negatives(seed,compact,compact_labels)
        assert rejected == compact_rejected
        regressions = C.Lift.gateway_units(seed,compact,compact_labels,compact_parts)
        continued=continued_landing(compact_fixture)
        held=C.Lift.load_fixture(held_fixture(seed),compact,compact_parts)
        held_result=observe(held)
        assert held_result['final_source']['action_pose_mode'][0]==17
        assert {r['PC']for r in held_result['state_writers']}=={'0xa352','0xa365'}
        assert held_result['native']['flag']==5
    report = dict(passed=True,parent=H(parent),candidate=H(image),
                  translated_fixture=True,natural_or_native_claim=False,
                  result=result,prototype=dict(bytes=len(prototype),SHA256=H(prototype),
                      entries={k:hex(v)for k,v in labels.items()if k in('MaterialSweep','Sweep')},
                      result=fixed,unfunded_RAM_fixture=True,rejections=rejected),
                  compact=dict(bytes=len(compact),SHA256=H(compact),packed=len(compact_packed[3]),
                      actual_loader478_spare=compact_info['remaining_by_cold_worker_bytes'][480]+2,
                      entries={k:hex(v)for k,v in compact_labels.items()if k in('Material','Support','Sweep','Actor','Eligible')},
                      result=compact_result,rejections=compact_rejected,regressions=regressions,
                      continued_original_landing=continued,held_carry=held_result,
                      complete_cold_or_route_not_claimed=True),outputs=0)
    digest = H(json.dumps(report,sort_keys=True,separators=(',',':')).encode())
    print('PRINCE_LIFT_SWEPT_PLANE '+json.dumps(dict(passed=True,SHA256=digest,
        parent=H(parent),candidate=H(image),original_plane=result['native_top_tests'],
        compact={k:v for k,v in report['compact'].items()if k not in('result','held_carry')},
        compact_landing=dict(final=compact_result['final_source'],writers=compact_result['state_writers'],
            native=compact_result['native']),
        held_landing=dict(final=held_result['final_source'],writers=held_result['state_writers'],
            native=held_result['native'],provider=[r for r in held_result['source']if r['site']=='Material-gateway']),
        translated_fixture=True,natural_or_native_claim=False,outputs=0),separators=(',',':')),flush=True)


if __name__ == '__main__':main()
