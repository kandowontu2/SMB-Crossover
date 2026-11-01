"""Add conditional original Doki physics to the current S2 module; no admission."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from private_build_outputs_v1 import validate
from prepare_cv3_dmc_mirror import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
O=R/'build/doki-current-component-1101-v1';S=O/'src'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
write=lambda p,s:p.write_text(s,encoding='utf-8',newline='\n')


def once(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b,1)


def main():
    assert not(O/'source-stage.json').exists()
    base=O/'baseline-edited-inputs.json';names=['smb2_roster_core.s','smb2_roster_native.inc','smb2_roster_objects_native.inc']
    if not base.exists():
        q=json.loads((O/'assembly-controls.json').read_text());assert q['passed']
        for f,h in q['bindings'].items():assert sha(f)==h,f
        save(base,{n:(S/n).read_text()for n in names})
    original=json.loads(base.read_text());q=json.loads((R/'build/doki-original-physics-audit-1031-v2/audit.json').read_text());assert q['passed']
    mama=next(c for c in q['stats']if c['name']=='Mama')['Doki'][6:12]
    core=original[names[0]]
    # A mode bit in the existing scene key distinguishes both lineages even
    # when their native actor ID is identical. Preserve the original X/Y.
    core=once(core,' ora AreaAddrsLOffset\n rts',''' ora AreaAddrsLOffset
 pha
 txa
 pha
 lda S2Variant
 and #4
 cmp #4
 pla
 tax
 pla
 bcc :+
 ora #$80
:
 rts''')
    core=once(core,' cmp #4\n bcc Valid',' cmp #8\n bcc Valid').replace(' cpx #4\n bcc :+',' cpx #8\n bcc :+')
    core=once(core,'VariantNative:.byte 0,3,2,1\nStatOffset:.byte 0,23,46,69','VariantNative:.byte 0,3,2,1,0,1,2,3\nStatOffset:.byte 0,23,46,69,0,69,46,23\nDokiMamaJumps:.byte '+','.join(str(v)for v in mama))
    core=once(core,' cpx #23\n bcc Stats',''' cpx #23
 bcc Stats
 lda S2Variant
 cmp #7
 bne :+
 ldx #5
DokiStats:
 lda DokiMamaJumps,x
 sta S2Stats+6,x
 dex
 bpl DokiStats
:
'''.rstrip())
    core=once(core,' lda S2Health\n cmp #$10\n lda #0\n bcs Size\n lda #1\nSize:sta S2Size',''' lda S2Variant
 and #4
 bne DokiBig
 lda S2Health
 cmp #$10
 lda #0
 bcs Size
 lda #1
 bne Size
DokiBig:lda #0
Size:sta S2Size''')
    core=once(core,'.proc S2HandlePlayerState\n','.proc S2HandlePlayerState\n lda S2Variant\n and #4\n bne Dispatch\n')
    write(S/names[0],core)
    native=original[names[1]]
    native=once(native,'S2N8D77: lda S2NativeCharacter','''S2N8D77:
 lda S2Variant
 and #4
 bne S2N8DB1
 lda S2NativeCharacter''')
    native=once(native,'S2N8DE0: lda S2Stats+17,y','''S2N8DE0:
 lda S2Variant
 and #4
 beq DokiClampUSA
 lda S2Stats+17,y
 cmp S2VX
 bpl :+
 sta S2VX
:
 lda S2Stats+20,y
 cmp S2VX
 bmi :+
 sta S2VX
:
 jmp S2N8E05
DokiClampUSA:lda S2Stats+17,y''')
    write(S/names[1],native)
    obj=original[names[2]]
    obj=once(obj,'S2O9636: ldy S2Animation','''S2O9636:
 pha
 lda S2Variant
 and #4
 beq DokiCarryUSA
 pla
 ldx S2Animation
 cpx #4
 clc
 bne :+
 adc #8
:
 php
 ldx S2Source12
 ldy S2ObjectLift,x
 clc
 adc DokiCarryLo-1,y
 sta S2Y+1,x
 lda S2ProbeDirection
 adc DokiCarryHi-1,y
 plp
 adc #0
 sta S2YPage+1,x
 jmp S2CarryGeometryReturn
DokiCarryUSA:pla
 ldy S2Animation''')
    obj+='\n.pushseg\n.segment "PARODIUS_BELLS"\nDokiCarryLo:.byte $fb,$ff,0,8,12,24,26\nDokiCarryHi:.byte $ff,$ff,0,0,0,0,0\n.popseg\n'
    write(S/names[2],obj)
    build=json.loads((O/'component-build.json').read_text())['command'];link=json.loads((O/'link.json').read_text())['command'];attempts=[]
    for attempt in range(12):
        guard=validate(build,O,cwd=R);run=subprocess.run(build,cwd=R,capture_output=True,text=True);attempts.append(dict(returncode=run.returncode,stderr=run.stderr))
        if run.returncode==0:break
        repairs=re.findall(r'([^\r\n]+):(\d+): Error: Range error',run.stderr);assert repairs,run.stderr
        by={}
        for file,line in repairs:by.setdefault(Path(file),[]).append(int(line)-1)
        for path,rows in by.items():
            assert path.parent==S,path;lines=path.read_text().splitlines()
            for i in rows:
                match=re.search(r'\bb(cc|cs|eq|ne|pl|mi|vc|vs)\b',lines[i]);assert match,lines[i]
                lines[i]=lines[i][:match.start()]+'j'+match[1]+lines[i][match.end():]
            write(path,'\n'.join(lines)+'\n')
    else:raise AssertionError('Bounded branch repair')
    save(O/'doki-component-build.json',dict(command=build,guard=guard,attempts=attempts))
    guard=validate(link,O,cwd=R);run=subprocess.run(link,cwd=R,capture_output=True,text=True)
    save(O/'doki-link.json',dict(command=link,guard=guard,returncode=run.returncode,stderr=run.stderr));assert run.returncode==0,run.stderr
    p=O/'candidate.dbg';keep={'version','info','file','lib','mod','seg','scope','sym'};p.write_bytes(b''.join(l for l in p.read_bytes().splitlines(keepends=True)if l.split(b'\t',1)[0].decode('ascii')in keep));prepare(R,O/'candidate.nes')
    b=scoped_load(O/'candidate.nes');assert address(b,'S2HudCoreEnd')<=0xc000
    refs=[Path(__file__),base,R/'build/doki-original-physics-audit-1031-v2/audit.json',O/'candidate.nes',O/'candidate.dbg',O/'candidate.cfg',*[S/n for n in names]]
    save(O/'port-assembly.json',dict(passed=True,source=True,native=False,installed=False,candidate=sha(O/'candidate.nes'),Doki_internal_variants=[4,5,6,7],names=['Imajin','Lina','Papa','Mama'],new_global_or_ZP_bytes=0,source_code_end=address(b,'S2HudCoreEnd'),spare_core_bytes=0xc000-address(b,'S2HudCoreEnd'),
        scope='Conditional original Mama stats, no B boost, no Luigi air animation, fixed carry coordinates, always-large/no USA shrink transition. Original four USA modes remain selected by the unchanged menu. Doki art/menu/admission and runtime CPU/native checks still pending.',bindings={str(p.resolve()):sha(p)for p in refs}))
    print(json.dumps(dict(source_assembled=True,candidate=sha(O/'candidate.nes'),spare_core_bytes=0xc000-address(b,'S2HudCoreEnd'),native=False,installed=False)))


if __name__=='__main__':main()
