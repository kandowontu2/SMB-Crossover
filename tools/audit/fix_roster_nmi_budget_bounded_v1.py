"""Keep actual roster palette/name packets inside the NMI rendering window."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from private_build_outputs_v1 import validate
from link_pit_rygar_sophia_audit_cpu import scoped_load
from prepare_cv3_dmc_mirror import prepare
from prepare_contra_force_p1_coherent_cart_v2 import native_abi
P=R/'build/ready76-visible';O=R/'build/ready76-menu-fixed'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')


def main():
    assert not(O/'source-stage.json').exists();O.mkdir(exist_ok=True)
    assert sha(P/'candidate.nes')=='d1c4973cf69702ba02d83706aadda72a2a63a6f0cec6018ec5fa63735ff75393'
    parent=json.loads((P/'source-stage.json').read_text())
    for path,h in parent['bindings'].items():assert sha(path)==h,path
    source=next(Path(p)for p in parent['bindings']if p.endswith('menu_vram_budget.s'))
    text=source.read_text()
    old=' jsr MenuMergePaletteRuns\n';assert text.count(old)==1
    text=text.replace(old,old+' jsr MenuPruneUnusedPalette2\n',1)
    # These four targets are all within this71-byte procedure. Use real
    # short branches, funding the new accepted packet shapes in its old lease.
    head,tail=text.split('; Exact supported native menu command shapes.',1)
    for old,new,count in [(' jne Restore',' bne Restore',3),(' jcc Restore',' bcc Restore',1)]:
        assert head.count(old)==count;head=head.replace(old,new)
    text=head+'; Exact supported native menu command shapes.'+tail
    old=''' cmp #$11
 beq Three
 cmp #$19
 beq Three
 cmp #$1d
 jne Invalid
Three:'''
    new=''' cmp #$11
 beq Three
 cmp #$15
 beq Three
 cmp #$19
 beq Three
 cmp #$1d
 jne Invalid
Three:'''
    assert text.count(old)==1;text=text.replace(old,new,1)
    old=''' cmp #3
 jne Invalid
 beq Advance
Body:'''
    new=''' cmp #3
 beq Advance
 cmp #7
 jne Invalid
 lda VRAM_Buffer1+1,x
 and #7
 cmp #1                       ; only11/7 or19/7, both within sprite colors
 jne Invalid
 beq Advance
Body:'''
    assert text.count(old)==1;text=text.replace(old,new,1)
    worker='''
; A portrait publishes its OAM and palette together. No other actors are
; present on this page. Keep every palette2/3 write if even one visible OAM
; part uses either palette; otherwise those projectile/outline colors cannot
; affect the displayed portrait and need not consume the NMI write budget.
.proc MenuPruneUnusedPalette2
 ldx #0
Oam:
 lda Sprite_Data,x
 cmp #240
 bcs NextOam
 lda Sprite_Data+2,x
 and #2
 bne Done
NextOam:
 txa
 clc
 adc #4
 tax
 bne Oam
 ldx #0
Packet:
 cpx VRAM_Buffer1_Offset
 bcs Done
 lda VRAM_Buffer1,x
 cmp #$3f
 bne Next
 lda VRAM_Buffer1+1,x
 cmp #$19
 beq Remove
 cmp #$1d
 bne Next
Remove:
 lda VRAM_Buffer1+2,x
 clc
 adc #3
 sta R1
 jsr MenuDeleteBytes
 jmp Packet
Next:
 lda VRAM_Buffer1+2,x
 tay
 inx
 inx
 inx
Bytes:
 inx
 dey
 bne Bytes
 jmp Packet
Done:rts
.endproc
'''
    end='.popseg\n.endif';assert text.count(end)==1
    # ca65's segment table is already full. The existing bank42 body remainder
    # ends atBAE9, leaving103 actual bytes before this menu's fixedBB50 entry.
    text=text.replace(end,'.popseg\n.pushseg\n.segment "MM_BODY_PARTIAL"\n.assert *=$bae9,lderror,"Menu helper uses only the existing103-byte gap"\n'+worker+'\n.assert *<=$bb50,lderror,"Keep the fixed menu entry"\n'+end,1)
    (O/'menu_vram_budget.s').write_text(text,encoding='utf-8',newline='\n')
    def run(name,cmd):
        cmd=list(map(str,cmd));guard=validate(cmd,O,cwd=R)
        for item in guard['outputs']:Path(item['path']).parent.mkdir(parents=True,exist_ok=True)
        result=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        save(O/(name+'.json'),dict(command=cmd,guard=guard,returncode=result.returncode,stderr=result.stderr));assert result.returncode==0,result.stderr
    cmd=json.loads((P/'main-build.json').read_text())['command'][:];cmd[1:1]=['-I',str(O)]
    for flag,name in [('-o','main.o'),('-l','main.lst'),('--create-full-dep','main.dep')]:
        if flag in cmd:cmd[cmd.index(flag)+1]=str(O/name)
    run('main-build',cmd)
    outputs={};count=0
    def redirect(m):
        nonlocal count
        if m[1]in['','%O']:return m[0]
        count+=1;p=O/'sideoutputs'/(f'{count:03d}-'+Path(m[1]).name);outputs[Path(m[1]).name]=p
        return 'file="'+p.as_posix()+'"'
    config=re.sub(r'file\s*=\s*"([^"\r\n]*)"',redirect,(P/'candidate.cfg').read_text())
    (O/'candidate.cfg').write_text(config)
    link=json.loads((P/'final-link.json').read_text())['command'][:];link[link.index(str(P/'main.o'))]=str(O/'main.o')
    for flag,name in [('-C','candidate.cfg'),('-o','candidate.nes'),('-Ln','candidate.lbl'),('-m','candidate.map')]:
        if flag in link:link[link.index(flag)+1]=str(O/name)
    link[link.index('--ld-args')+1]='--dbgfile,'+str(O/'candidate.dbg');run('final-link',link)
    path=O/'candidate.dbg';data=path.read_bytes();keep={'version','info','file','lib','mod','seg','scope','sym'}
    path.write_bytes(b''.join(s for s in data.splitlines(keepends=True)if s.split(b'\t',1)[0].decode('ascii')in keep))
    save(O/'debug-format.json',dict(full_bytes=len(data),full_sha256=hashlib.sha256(data).hexdigest(),compact_bytes=path.stat().st_size,compact_sha256=sha(path)))
    prepare(R,O/'candidate.nes')
    before,after=[scoped_load(p/'candidate.nes')for p in[P,O]]
    changes=[i for i,(a,z)in enumerate(zip(before['raw'],after['raw']))if a!=z]
    assert changes and all(16+0x42*8192<=i<16+0x43*8192 for i in changes)
    assert native_abi(before)==native_abi(after)
    for name in ['kernel.bin','state.bin','final-a1.bin','final-c2.bin','final-a3.bin']:
        old=next(p for p in(P/'sideoutputs').iterdir()if p.name.endswith(name));current=next(p for n,p in outputs.items()if n.endswith(name))
        assert old.read_bytes()==current.read_bytes(),name
    refs={Path(__file__),source,P/'source-stage.json',P/'main-build.json',P/'final-link.json'}
    dep=(O/'main.dep').read_text().split(':\t',1)[1].split('\n',1)[0]
    refs|={Path(x.replace('\\ ',' '))for x in re.split(r'(?<!\\)\s+',dep)if x}
    refs|={Path(p)for p in link if p.endswith('.o')};refs|={p for p in O.rglob('*')if p.is_file()}
    save(O/'source-stage.json',dict(passed=True,source=True,native=False,installed=False,candidate=sha(O/'candidate.nes'),parent=sha(P/'candidate.nes'),private_playable=76,
        changed_native_bytes=len(changes),only_PRG_bank=66,all_CHR_and_selected_images_exact=True,
        defect='17 menu transitions enabled rendering on visible scanlines0..3. Accept real3F15/3 and3F11/7 packets, remove the static hint, and omit palette2/3 updates only when the actual published OAM uses neither.',
        bindings={str(p.resolve()):sha(p)for p in refs}))
    print(json.dumps(dict(candidate=sha(O/'candidate.nes'),changed_bytes=len(changes),only_PRG_bank=66)))


if __name__=='__main__':main()
