"""Typed, no-growth SMB2 source/passability plus native flag handoff."""
from hashlib import sha256
import json
import re

import check_smb2_flag_handoff_1113 as Check
from compose_metal_head_bridge_1112 import assemble_segments

PIN=Check.PIN
PROBE_AT=971064
WORLD_AT=973246
PROBE_SIZE=174
WORLD_SIZE=207
PROBE_SHA='339793404b889bb222919af51d6c138cf67a2837ebf195510a37a39c1a56a8a9'
WORLD_SHA='e7aab226f1ac2d644dbf04ad3d6e9a0bd5147fb202dfb18c264386361af68798'


def source_recipe(raw):
    W=Check.W;b=dict(W.Symbols.bundle(),raw=raw)
    measured=Check.measure(raw)if sha256(raw).hexdigest()==PIN else None
    names=('R0','R1','R2','R4','R5','R6','R7','S2X','S2Y','S2Page','S2YPage','S2ProbeDirection',
        'S2HeadX','S2HeadPage','S2HeadY','S2Math0','S2DF011','S2DF055','GetBlockBufferAddr','MTileAttribute',
        'AreaType','BlockBounceTimer','S2MainCell','PlayerHeadCollision','S2MainVelocity','Player_Y_Position',
        'BlockBufferColli_Side','HandleClimbing','GameEngineSubroutine','CheckForCoinMTiles','HandleCoinMetatile',
        'S2Air','S2Held','Up_Down_Buttons','HandlePipeEntry')
    constants={n:W.address(b,n)for n in names}
    origins=dict(S2_FLAG_PROBE=0xb128,S2_FLAG_WORLD=0xb9ae)
    assert W.location(b,'S2NativeTileProbe')==PROBE_AT and W.location(b,'S2MainWorld')==WORLD_AT
    assert W.address(b,'S2GroundInteraction')==0xb1d6 and W.address(b,'S2MainPickup')==0xba7d
    source=Check.SOURCE.read_text();code,labels=assemble_segments(source,origins,constants)
    assert len(code['S2_FLAG_PROBE'])==PROBE_SIZE and labels['S2FlagSharedReturn']==0xb1d5
    assert len(code['S2_FLAG_WORLD'])<=WORLD_SIZE
    new=dict(probe=code['S2_FLAG_PROBE'],world=code['S2_FLAG_WORLD'].ljust(WORLD_SIZE,b'\xea'))
    # Reproduce the entire original probe+RTS from the same owning source.
    old_probe=source.split('.segment "S2_FLAG_WORLD"')[0]
    before='cmp #$23\n bcc ProbeOtherTile\n cmp #$27\n bcc ProbeFlagEmpty\nProbeOtherTile:'
    assert old_probe.count(before)==1
    old_probe=old_probe.replace(before,'cmp #$23\n beq ProbeEmpty\n cmp #$26\n beq ProbeEmpty')
    old_probe=old_probe.replace('ProbeFlagEmpty:\n sec\n','')+'\n rts\n'
    old_probe=assemble_segments(old_probe,{'S2_FLAG_PROBE':0xb128},constants)[0]['S2_FLAG_PROBE']
    # The original MainWorld compilation is independently rebuilt from its
    # actual source; only the one ca65 long branch needs explicit expansion.
    text=(Check.R/'src/smb2_roster_main_v2.s').read_text()
    old_world=text.split('.proc S2MainWorld',1)[1].split('.endproc',1)[0]
    old_world=old_world.replace('jne Done','beq OldWorldVisible\n jmp Done\nOldWorldVisible:')
    old_world=old_world.replace('#MTILE_BUMP|MTILE_CLIMB','#6')
    lines=[]
    for line in old_world.splitlines():
        line=line.split(';',1)[0].strip()
        if not line:continue
        found=re.match(r'^(\w+):(.*)$',line)
        if found:lines.append(found[1]+':');line=found[2].strip()
        if line.startswith('.byte'):
            line='.byte '+','.join('$%02x'%int(v.strip())for v in line[5:].split(','))
        if line:lines.append(line)
    old_world=assemble_segments('.segment "S2_FLAG_WORLD"\n'+'\n'.join(lines),
        {'S2_FLAG_WORLD':0xb9ae},constants)[0]['S2_FLAG_WORLD']
    assert len(old_probe)==PROBE_SIZE and sha256(old_probe).hexdigest()==PROBE_SHA
    assert len(old_world)==WORLD_SIZE and sha256(old_world).hexdigest()==WORLD_SHA
    return dict(probe=old_probe,world=old_world),new,dict(source_SHA256=sha256(source.encode()).hexdigest(),
        probe_bytes=PROBE_SIZE,world_bytes=len(code['S2_FLAG_WORLD']),world_padding=WORLD_SIZE-len(code['S2_FLAG_WORLD']),
        labels=labels,measured=measured,new_RAM_bytes=0,new_ROM_bytes=0)


def proposal(raw):
    assert sha256(raw).hexdigest()==PIN
    old,new,info=source_recipe(raw);out=bytearray(raw)
    for name,at,n in(('probe',PROBE_AT,PROBE_SIZE),('world',WORLD_AT,WORLD_SIZE)):
        assert raw[at:at+n]==old[name]
        out[at:at+n]=new[name]
    candidate=bytes(out)
    info.update(parent_SHA256=PIN,ROM_SHA256=sha256(candidate).hexdigest(),
        changed_bytes=sum(a!=b for a,b in zip(raw,candidate,strict=True)),
        allowed_spans=[[PROBE_AT,PROBE_SIZE],[WORLD_AT,WORLD_SIZE]],ROM_length_unchanged=True)
    return candidate,info


def inverse(raw):
    old,new,_=source_recipe(raw);out=bytearray(raw)
    for name,at,n in(('probe',PROBE_AT,PROBE_SIZE),('world',WORLD_AT,WORLD_SIZE)):
        assert raw[at:at+n]==new[name]
        out[at:at+n]=old[name]
    parent=bytes(out);assert sha256(parent).hexdigest()==PIN
    assert proposal(parent)[0]==raw
    return parent


if __name__=='__main__':
    raw=Check.load_input();image,q=proposal(raw);assert inverse(image)==raw
    q.pop('measured',None);q.pop('labels',None)
    print(json.dumps(dict(passed=True,**q,exact_inverse=True,outputs=0,Mesen_run=False)),flush=True)
