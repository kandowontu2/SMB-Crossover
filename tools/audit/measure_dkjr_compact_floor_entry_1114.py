"""Measure DK floor/entry context factoring; no ROM or RAM composition."""
import ast
from hashlib import sha256
import json
from pathlib import Path

import measure_dkjr_floor_entry_handlers_1114 as Original

S,F,G=Original.S,Original.F,Original.G
P,H,W=G.P,G.H,G.W
ORIGINAL_SHA='043936a8d95b09438b9bc43ede4148e14674042a4dea82dc0f3604162918bb9c'


def sources():
    data=Path(Original.__file__).read_bytes();assert sha256(data).hexdigest()==ORIGINAL_SHA
    tree=ast.parse(data);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='measure')
    literals={n.targets[0].id:ast.literal_eval(n.value)for n in fn.body
        if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)
        and n.targets[0].id in ('entry','floor')}
    entry,floor=literals['entry'],literals['floor']
    first=''' lda OperMode
 cmp #1
 bne DropNo
 lda OperMode_Task
 cmp #3
 bne DropNo
 lda $c04a
 cmp #1
 bne DropNo
 lda GameEngineSubroutine
 eor #8
 ora TimerControl
 ora DisableCollisionDet
 ora JumpspringAnimCtrl
 ora SwimmingFlag
 ora $c068
 bne DropNo
'''
    high=''' lda Player_Y_HighPos
 cmp #1
 bne DropNo
'''
    # Identical admitted context; move the high-byte comparison before the
    # entrance/state checks. No mutable field or call intervenes in either.
    context=first.replace('DropNo','ContextNo')+high.replace('DropNo','ContextNo')
    context='''
.segment "CONTEXT"
MeasuredEndpointContext:
'''+context+''' sec
 rts
ContextNo:
 clc
 rts
'''
    entry=P.once(entry,first,' jsr MeasuredEndpointContext\n bcc DropNo\n')
    entry=P.once(entry,high,'')
    # Keep the cached original body on the native pending-fall coordinates
    # without advancing source physics or publishing constructed-ready2.
    entry=P.once(entry,' jsr FarCallCommon\n clc\n rts',
        ' jsr FarCallCommon\n jsr DkjrNativeImportAnchor\n clc\n rts')
    floor_first=''' lda OperMode
 cmp #1
 bne FloorDone
 lda OperMode_Task
 cmp #3
 bne FloorDone
 lda $c8fe
 cmp #2
 bne FloorDone
 lda $c04a
 cmp #1
 bne FloorDone
 lda GameEngineSubroutine
 eor #8
 ora TimerControl
 ora DisableCollisionDet
 ora JumpspringAnimCtrl
 ora SwimmingFlag
 ora $c068
 bne FloorDone
 lda Player_Y_HighPos
 cmp #1
 bne FloorDone
'''
    floor=P.once(floor,floor_first,''' jsr MeasuredEndpointContext
 bcc FloorDone
 lda $c8fe
 cmp #2
 bne FloorDone
''')
    _,old=F.load_inputs();_,labels=Original.Life.closure(old)
    b=W.Symbols.bundle()
    names=('OperMode','OperMode_Task','GameEngineSubroutine','PlayerEntranceCtrl',
        'Player_State','Player_Y_HighPos','Player_Y_Position','TimerControl',
        'Player_X_Position','Player_PageLoc','ScreenLeft_X_Pos','ScreenLeft_PageLoc',
        'DisableCollisionDet','JumpspringAnimCtrl','SwimmingFlag',
        'FarcallJmpTarget_SMC','FarCallCommon')
    defs=''.join(f'{name}=${W.address(b,name):x}\n'for name in names)
    for name in ('DkjrNativeImportAnchor','DkjrNativeCameraSync','DkjrNativeShiftCamera','DkjrNativeWorldBuild'):
        defs+=f'{name}=${labels[name]:x}\n'
    defs+=f'DkExistingAirLanding=${labels["CarryAccepted"]+7:x}\nCarryTop=$c8f5\n'
    pc=W.address(b,'MovePlayerVertically');offset=W.location(b,'MovePlayerVertically')
    defs+=f'NativeVertical=${pc:x}\nNativeVerticalBank=${((offset-16)//8192)|128:x}\n'
    return defs,entry+floor+context


def measure():
    defs,source=sources()
    names=('ENTRY','FLOOR','PREDICATE','VISIBLE','STATIC','CONTEXT')
    layout={name:(0x9000+512*i,256)for i,name in enumerate(names)}
    code=H.T.assemble(defs+source,layout)
    return dict(measurement_only=True,ROM_composed=False,RAM_changes=0,
        canonical_original_measure_SHA256=ORIGINAL_SHA,
        blocks={name:dict(bytes=code['used'][name],measurement_origin=layout[name][0],
            generated_hex=code['images'][name].hex(),SHA256=sha256(code['images'][name]).hexdigest())for name in names},
        total_bytes=sum(code['used'].values()),original_total_bytes=338,
        all_original_context_fields_retained=True,static_and_fall_comparisons_unchanged=True,
        new_stage_or_pointer_domain_restrictions=False,outputs_written=0,
        scope='Virtual factoring measurement only. Predicate equivalence/ABI/IRQ, exact combined layout, ownership and grant remain open.')


if __name__=='__main__':
    print('DKJR_COMPACT_FLOOR_ENTRY '+json.dumps(measure(),separators=(',',':')),flush=True)
