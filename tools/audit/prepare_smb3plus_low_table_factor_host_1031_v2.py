"""Source-only lossless M3 low-table factor on installed01a4; no ability code."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare
P=R/'build/smb3plus-current66-source-1031-v2';C=P/'joint'
O=R/'build/smb3plus-low-table-factor-host-1031-v2';J=O/'joint'
PROPOSAL=R/'build/smb3plus-low-table-factor-proposal-1031-v1/proposal.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def save(p,q):write(p,json.dumps(q,indent=2)+'\n')


def main():
    assert not O.exists()
    h=json.loads((R/'docs/qa/checkpoints/2026-10-31/smb3plus-current66-source-v1/handoff.json').read_text(encoding='utf-8'))
    for n,v in h['bindings'].items():assert sha(n)==v,n
    proposal=json.loads(PROPOSAL.read_text(encoding='utf-8'))
    for n,v in proposal['bindings'].items():assert sha(n)==v,n
    assert sha(C/'candidate.nes')==h['candidate']=='01a40d4019ae00220c7279c9ab8d4f6f25afb44af1612a6a1483a257448f0fa9'
    old=scoped_load(C/'candidate.nes')
    shutil.copytree(C,J)
    def rt(s):return s.replace(str(C),str(J)).replace(C.as_posix(),J.as_posix())
    for p in J.rglob('*'):
        if p.is_file()and p.suffix in['.s','.inc','.cfg']:write(p,rt(p.read_text(encoding='utf-8')))
    art=J/'src/smb3_mario_art.inc';text=art.read_text(encoding='utf-8')
    arrays={int(m[1]):list(map(int,m[2].split(',')))for m in re.finditer(r'M3Form(\d)ChrLo: \.byte ([0-9,]+)',text)}
    assert set(arrays)=={0,1,2,3,4,6};arrays[5]=[v+4 for v in arrays[3]]
    offsets=proposal['offsets'];assert offsets==[0,4,4,244,0,248,252]
    assert all(len(v)==81 for v in arrays.values())
    assert all((base+offsets[f])&255==v for f in range(7)for base,v in zip(arrays[0],arrays[f]))
    reclaimed=[]
    for f in[1,2,3,4,6]:
        pat=rf'M3Form{f}ChrLo: \.byte ([0-9,]+)\n';match=re.search(pat,text);assert match
        if f==1:
            body='M3Form1ChrLo:\nMbChrOffsets:.byte '+','.join(map(str,offsets))+'\n .res 74,$ea\n'
        else:body=f'M3Form{f}ChrLo:\n .res 81,$ea\n'
        text=text[:match.start()]+body+text[match.end():]
        reclaimed.append(dict(form=f,start=address(old,f'M3Form{f}ChrLo')+(7 if f==1 else 0),bytes=74 if f==1 else 81))
    for suffix,op in[('Lo','<'),('Hi','>')]:
        pat=rf'M3ChrLoTable{suffix}: \.byte [^\n]+\n';match=re.search(pat,text);assert match
        body=f'M3ChrLoTable{suffix}: .byte '+','.join([op+'M3Form0ChrLo']*7)+'\n'
        text=text[:match.start()]+body+text[match.end():]
    write(art,text)
    render=J/'src/smb3_mario_render.s';text=render.read_text(encoding='utf-8')
    start=text.index('::MbFloatReadChrLow:\n');end=text.index('::MbStatusNameOffsets:',start)
    original=text[start:end]
    # Sole genuine caller already clamps X to0..6 before both pointer stores,
    # and never changes X before JSR. Use that real typed input rather than
    # the proposal's redundant unclamped reload of M3RenderForm.
    body='''::MbFloatReadChrLow:
 php
 lda (R0),y
 clc
 adc MbChrOffsets,x
 sta SmChrBank
 plp
 rts
 .res 23-(*-MbFloatReadChrLow),$ea
'''
    assert ' ldx M3RenderForm\n cpx #7\n bcc :+\n ldx #0\n:lda M3ChrLoTableLo,x\n sta R0\n lda M3ChrLoTableHi,x\n sta R1\n ldy M3RenderFrame\n jsr MbFloatReadChrLow' in text
    assert text.count('jsr MbFloatReadChrLow')==1
    text=text[:start]+body+text[end:];write(render,text)
    logs=[]
    def run(n,cmd):
        proof=validate(cmd,J,cwd=R);z=subprocess.run(cmd,cwd=R,text=True,capture_output=True)
        p=O/(n+'.json');save(p,dict(command=cmd,validation=proof,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr));logs.append(p)
        assert z.returncode==0,(n,z.stderr)
    for n in['main','union']:
        cmd=[rt(x)for x in json.loads((P/(n+'-build.json')).read_text(encoding='utf-8'))['command']]
        run(n+'-build',cmd)
    cmd=[rt(x)for x in json.loads((P/'final-link.json').read_text(encoding='utf-8'))['command']];run('final-link',cmd)
    prepare(R,J/'candidate.nes');new=scoped_load(J/'candidate.nes')
    allowed=set()
    for f in[1,2,3,4,6]:
        at=location(old,f'M3Form{f}ChrLo');allowed.update(range(at,at+81))
    for n,size in[('MbFloatReadChrLow',23),('M3ChrLoTableLo',7),('M3ChrLoTableHi',7)]:
        at=location(old,n);allowed.update(range(at,at+size))
    delta={i for i,(a,b)in enumerate(zip(old['raw'],new['raw']))if a!=b}
    assert delta<=allowed
    assert old['raw'][:16]==new['raw'][:16]and old['raw'][16+128*8192:]==new['raw'][16+128*8192:]
    removed={'M3Palette::MbFloatLowOriginal','M3Palette::MbFloatLowStore'}
    for n,s in old['syms'].items():
        if s.get('type')!='lab':continue
        if n in removed:assert n not in new['syms'];continue
        assert n in new['syms']and address(old,n)==address(new,n),(n,'public/following PC moved')
    for n in['M3Form0ChrLo','M3Form5ChrLo']:
        at=location(old,n);assert old['raw'][at:at+81]==new['raw'][at:at+81],n
    for n in['bowser.bin','ram3.bin','code.bin','data.bin','ff-cookie.bin','bt/cache.bin','bt/cookie.bin','bowser/cookie.bin']:
        assert sha(C/n)==sha(J/n),n
    q=dict(status='PRIVATE_LOW_TABLE_FACTOR_SOURCE_CONTROLS_PENDING_NO_FREE_SPACE_CLAIM',
        candidate=sha(J/'candidate.nes'),parent=sha(C/'candidate.nes'),source=True,native=False,installed=False,
        header_CHR_and_other_payloads_exact=True,changed_bytes=len(delta),offsets=offsets,
        helper_actual_bytes=12,helper_reserved_bytes=23,
        actual_input_contract='Only actual M3SetFrame caller: X=clampedM3RenderForm0..6,Y=clampedframe0..80,R0/R1 pointsbaseForm0. X/Y and allP preserved, resultA/SmChrBank exact.',
        proposal_correction='22B proposal reloaded unclamped M3RenderForm; actual sole caller already supplies clampedX.12B typed-input body avoids invalid-form regression and extra stackX.',
        removed_private_helper_labels=sorted(removed),all_other_existing_labels_exact=True,
        candidate_unconsumed_spans=reclaimed,potential_reclaim_bytes=sum(x['bytes']for x in reclaimed),
        span_available_for_abilities=False,reason='Must finish real consumer/pointer/9072 graphics/sourcepixel/current68/ISR proofs before ownership of reclaimed bytes is qualified.',
        original_helper_source=original,new_helper_source=body,
        bindings={str(p.resolve()):sha(p)for p in[Path(__file__),R/'tools/audit/prepare_smb3plus_low_table_factor_host_1031_v1.py',R/'build/smb3plus-low-table-factor-host-1031-v1/preparation-negative.json',PROPOSAL,
            R/'docs/qa/checkpoints/2026-10-31/smb3plus-current66-source-v1/handoff.json',
            J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'private.cfg',art,render,*logs]})
    save(O/'source-stage.json',q);print(json.dumps({k:v for k,v in q.items()if k not in['bindings','original_helper_source','new_helper_source']}))


if __name__=='__main__':main()
