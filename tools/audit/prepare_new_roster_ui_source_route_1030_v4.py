"""Preserve new-character UI services while skipping old Roll/Mac dispatch.

Assemble a tiny router into the existing122B gap before Dragon Power's fixed
A800 core. Preserve every old public entry and the original legacy branch.
"""
from pathlib import Path
import difflib,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import private_build_outputs_v1 as G
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
P=R/'build/current-character-composition-v2';O=R/'build/new-roster-ui-source-route-1030-v4'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    hp=P/'source-stage-handoff-v2.json';h=json.loads(hp.read_text())
    assert sha(hp)=='131d238ed8669a294d348dae2123557c8562b4bbe418e7fd76ab2fb5e4b7ee0a'
    for p,v in h['bindings'].items():assert sha(p)==v,p
    assert not O.exists();O.mkdir()
    b=scoped_load(P/'joint/candidate.nes');raw=bytearray(b['raw'])
    seg=next(s for s in b['segs'].values()if s['name'].strip('"')=='X5_BOUNCE')
    start=int(seg['start'],0)+int(seg['size'],0);assert start==0xa786
    bank=(location(b,'X5BounceUiDispatch')-16)//8192;assert bank==86
    symbols=['SelectedCharacter','InvHudActive','SafecallA_SMC','FarcallJmpTarget_SMC','FarCallCommon','NrUi','RlUiDispatch']
    const='\n'.join(f'{n} = ${address(b,n):04x}'for n in symbols)+'\n'
    banks={n:((location(b,n)-16)//8192)|128 for n in['NrUi','RlUiDispatch']}
    const+='\n'.join(f'{n}Bank = ${v:02x}'for n,v in banks.items())+'\n'
    (O/'exports.inc').write_text(const,newline='\n')
    header=''' .setcpu "6502X"
.include "exports.inc"
.macro Tail Target,Bank
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #Bank
 jmp FarCallCommon
.endmacro
.segment "UI_ROUTE"
.export X5NewRosterUiRoute
'''
    body='''.proc X5NewRosterUiRoute
 pla
 tax
 pla
 plp
 Tail NrUi,NrUiBank
.endproc
'''
    hud=address(b,'X5OwnInventoryUi::HudRead');legacy=address(b,'X5OwnInventoryUi::Legacy')
    assert legacy-hud==15
    hudbody='''.segment "HUD_READ"
 lda InvHudActive
 cpx #17
 bne HudDone
 lda #0
HudDone:clc
 rts
X5NewUiBridge:jmp X5NewRosterUiRoute
 nop
'''
    (O/'route.s').write_text(header+body+hudbody,newline='\n')
    (O/'route.cfg').write_text(f'MEMORY {{ ROM:start=${start:04x},size=${0xa800-start:x},type=ro,file="{(O/"route.bin").as_posix()}",bank=$56; HUD:start=${hud:04x},size=15,type=ro,file="{(O/"hud.bin").as_posix()}",bank=$56; }}\nSEGMENTS {{ UI_ROUTE:load=ROM,type=ro; HUD_READ:load=HUD,type=ro; }}\n',newline='\n')
    compiler=R/'tools/Windows/cc65/bin'
    commands=[('assemble',[str(compiler/'ca65.exe'),'--cpu','6502x','-g','-I',str(O),
        '--create-full-dep',str(O/'route.dep'),'-o',str(O/'route.o'),str(O/'route.s')]),
        ('link',[str(compiler/'ld65.exe'),'-C',str(O/'route.cfg'),'-o',str(O/'unused-primary.bin'),
        '--dbgfile',str(O/'route.dbg'),'-Ln',str(O/'route.lbl'),'-m',str(O/'route.map'),str(O/'route.o')])]
    for name,cmd in commands:
        guard=G.validate(cmd,O,cwd=R)
        r=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        (O/(name+'.json')).write_text(json.dumps(dict(command=cmd,guard=guard,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr),indent=2)+'\n',newline='\n')
        assert r.returncode==0,r.stderr
    code=(O/'route.bin').read_bytes();assert len(code)==22 and start+len(code)<=0xa800
    hudcode=(O/'hud.bin').read_bytes();assert len(hudcode)==15
    at=16+bank*8192+start-0xa000
    assert raw[at:at+len(code)]==bytes([255])*len(code)
    entry=address(b,'X5OwnInventoryUi::Legacy');off=location(b,'X5OwnInventoryUi::Legacy')
    assert raw[off:off+4]==bytes([0x68,0xaa,0x68,0x28])
    def tail(n):
        a=address(b,'SafecallA_SMC')+1;f=address(b,'FarcallJmpTarget_SMC');t=address(b,n);c=address(b,'FarCallCommon')
        return bytes([141,a&255,a>>8,169,t&255,141,(f+1)&255,(f+1)>>8,169,t>>8,141,(f+2)&255,(f+2)>>8,169,banks[n],76,c&255,c>>8])
    assert raw[off+4:off+22]==tail('RlUiDispatch')
    assert code[:4]==bytes([0x68,0xaa,0x68,0x28])and code[4:]==tail('NrUi')
    proc=location(b,'X5OwnInventoryUi');size=int(b['syms']['X5OwnInventoryUi']['size'],0)
    original=bytes(raw[proc:proc+size]);assert original.count(bytes([0xe0,20,0xb0]))==1
    branch=proc+original.index(bytes([0xe0,20,0xb0]))+2
    branchpc=address(b,'X5OwnInventoryUi')+branch-proc
    signed=lambda x:x if x<128 else x-256
    assert branchpc+2+signed(raw[branch+1])==entry
    bridge=hud+11;displacement=bridge-(branchpc+2);assert -128<=displacement<128
    raw[branch+1]=displacement&255
    hudoff=location(b,'X5OwnInventoryUi::HudRead');raw[hudoff:hudoff+15]=hudcode
    raw[at:at+len(code)]=code
    source=(P/'joint/src/x5_bounce.s').read_text();needle=' cpx #20\n bcs Legacy\n'
    assert source.count(needle)==1
    updated=source.replace(needle,' cpx #20\n bcs NewUiBridge\n')
    begin=updated.index('HudRead:\n',updated.index('.proc X5OwnInventoryUi'))
    end=updated.index('Legacy:\n',begin)
    updated=updated[:begin]+'''HudRead:
 lda InvHudActive
 cpx #17
 bne HudDone
 lda #0
HudDone:clc
 rts
NewUiBridge:jmp X5NewRosterUiRoute
 nop
'''+updated[end:]
    patchbody=body.replace(' pla\n tax\n',' plx\n',1).replace(' Tail NrUi,NrUiBank',' farcall NrUi,jmp')
    updated+='\n.pushseg\n.segment "X5_BOUNCE"\n'+patchbody+'.assert * <= $a800,error,"UI router must precede Dragon Power core"\n.popseg\n'
    (O/'x5_bounce.s').write_text(updated,newline='\n')
    (O/'source.patch').write_text(''.join(difflib.unified_diff(source.splitlines(True),updated.splitlines(True),fromfile='parent/joint/src/x5_bounce.s',tofile='candidate/joint/src/x5_bounce.s')),newline='\n')
    (O/'candidate.nes').write_bytes(raw);(O/'candidate.dbg').write_bytes((P/'joint/candidate.dbg').read_bytes())
    changes=[i for i,(a,z)in enumerate(zip(b['raw'],raw))if a!=z]
    assert all(i==branch+1 or hudoff<=i<hudoff+15 or at<=i<at+len(code)for i in changes)
    files={p for p in O.iterdir()if p.is_file()}|{Path(__file__),Path(G.__file__),hp,P/'joint/candidate.nes',P/'joint/candidate.dbg',P/'joint/src/x5_bounce.s'}
    proof=dict(status='PRIVATE_SOURCE_UI_ROUTE_CONTROLS_PENDING',native=False,admitted=False,
        candidate_sha256=sha(O/'candidate.nes'),parent_sha256=sha(P/'joint/candidate.nes'),
        router_PC=start,router_bank=bank,router_bytes=len(code),remaining_gap_before_DragonPower=0xa800-start-len(code),
        preserved_legacy_stub_PC=entry+4,bridge_PC=bridge,ROM_changed_bytes=len(changes),all_old_public_PCs_and_other_ROM_header_CHR_bytes_exact=True,
        legacy_Roll_Mac_UI_route_unchanged=True,
        no_new_memory_lease=True,actual_assembled_farcall_bodies_exact_to_original_macro=True,
        limits=['Exact current UI state/flags/wholeMain/vector parity and CPU measurement pending.',
            'Copied original DBG describes old entries; the separately linked router DBG describes the appended code.',
            'No readiness/native/download change.'],
        bindings={str(p.resolve()):sha(p)for p in sorted(files)})
    (O/'source-closure.json').write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(candidate=proof['candidate_sha256'],router_bytes=len(code),gap=proof['remaining_gap_before_DragonPower'])),flush=True)


if __name__=='__main__':main()
