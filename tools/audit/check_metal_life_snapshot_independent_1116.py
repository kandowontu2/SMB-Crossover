"""Independent detached byte/source/arithmetic review; no emulator imports."""
from hashlib import sha256
from pathlib import Path
import json
import re
import zipfile

R=Path(__file__).resolve().parents[2]
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN='7c0f7902e5ef17ff552c2ce36ba08534fdd48f00fddc62a54834df18e68f3c98'
PACKET=R/'docs/qa/checkpoints/2026-11-02/metal-reservation-v42/inputs.zip'
PACKET_SHA='f1548d2f32972aa150939ab9b33ab829aa4f19f60013cf813031ac21888724e9'
PREDICTED='00bb2664647a4ef47b5dfa01c96d50549581d215a33d19a2a6390d1e09078e21'
OLD_COOKIE=bytes.fromhex('a7232e7f64f1695d30762600e8451a6c')
H=lambda b:sha256(b).hexdigest()


def review(raw):
    assert H(raw)==PIN and H(PACKET.read_bytes())==PACKET_SHA
    with zipfile.ZipFile(PACKET)as z:
        members={n:z.read(n)for n in('component.s','component.lbl','native-cookie.bin','native-auth.bin','native-finish.bin')}
    source=members['component.s'].decode();labels={n:int(a,16)for a,n in re.findall(
        r'^al ([0-9a-fA-F]+) \.(\S+)[ \t\r]*$',members['component.lbl'].decode(),re.M)}
    actor_pages=(247,248,249,250,827,828,829,830);render_pages=(831,500,494)
    carrier=lambda pages:b''.join(raw[1048592+p*1024:1048592+(p+1)*1024]for p in pages)
    actor,renderer,extra=carrier(actor_pages),carrier(render_pages),carrier((499,))
    assert (labels['Ms12Movement'],labels['Ms12NeedConstructor'],labels['Ms12BeforeStep'],labels['Ms12Fresh'])==(0xd476,0xd4af,0xd4e8,0xd58b)
    assert renderer[0x7a7:0x7af].hex()=='ad5f07cd3ec8f039'
    assert renderer[0x7e2:0x7e8].hex()=='ad5f078d3ec8'
    assert renderer[0x88b:0x892].hex()=='a9008d00c83860'
    branch,old,new=0xd4ad,bytes.fromhex('f039'),bytes.fromhex('1036')
    assert branch+2+old[1]==0xd4e8 and branch+2+new[1]==0xd4e5
    assert renderer[branch-0xcd00:branch-0xcd00+2]==old
    revised=renderer[:branch-0xcd00]+new+renderer[branch-0xcd00+2:]
    cookie=bytes((0xa7,35,47))+sha256(b'Metal earned-life snapshot 1116\0'+OLD_COOKIE+actor+revised+extra).digest()[:13]
    assert cookie.hex()=='a7232fc62354dfbde732156cd49e287a'
    file=1048592+render_pages[(branch-0xcd00)//1024]*1024+(branch-0xcd00)%1024
    spans=[(file,old,new)]
    for name,bank,offset in(('auth',25,0x1f9e),('finish',99,0x176e)):
        old_component=members['native-'+name+'.bin'];at=16+bank*8192+offset
        assert old_component.count(members['native-cookie.bin'])==1
        index=old_component.index(members['native-cookie.bin'])
        assert raw[at:at+len(old_component)]==old_component.replace(members['native-cookie.bin'],OLD_COOKIE)
        assert raw[at+index:at+index+16]==OLD_COOKIE
        spans.append((at+index,OLD_COOKIE,cookie))
    digest=sha256();cursor=0
    for at,old_part,new_part in sorted(spans):
        assert at>=cursor and raw[at:at+len(old_part)]==old_part
        digest.update(raw[cursor:at]);digest.update(new_part);cursor=at+len(old_part)
    digest.update(raw[cursor:]);assert digest.hexdigest()==PREDICTED
    # Only a detached renderer fragment is revised. No whole candidate image
    # is created, mounted, executed, serialized or supplied to an emulator.
    assert [i for i,(a,b)in enumerate(zip(renderer,revised))if a!=b]==[0x7ad,0x7ae]
    references=[(i+1,line.strip())for i,line in enumerate(source.splitlines())if re.search(r'\bMs12Lives\b|\$c83e\b',line,re.I)]
    assert [v for _,v in references]==['Ms12Lives=$c83e','cmp Ms12Lives','sta Ms12Lives']
    literals=[]
    for name,start,data in(('actor',0xa000,actor[:0x1fe0]),('renderer',0xcd00,renderer),('extra',0xd900,extra)):
        for i in range(len(data)-1):
            if data[i:i+2]==bytes.fromhex('3ec8'):literals.append(dict(role=name,operand_PC=start+i,prefix=data[max(0,i-1):i+2].hex()))
    assert literals==[dict(role='renderer',operand_PC=0xd4ab,prefix='cd3ec8'),dict(role='renderer',operand_PC=0xd4e6,prefix='8d3ec8')],literals
    move=source[source.index('Ms12Movement:'):source.index('Ms12Camera:')]
    assert re.search(r'lda \$c800\s+cmp #\$a7\s+bne Ms12NeedConstructor\s+lda CurrentPlayer\s+cmp Ms12Player\s+bne Ms12NeedConstructor\s+lda NumberofLives\s+cmp Ms12Lives\s+beq Ms12BeforeStep',move)
    before=source[source.index('Ms12BeforeStep:'):source.index('Ms12MoveRejected:')]
    assert before.lstrip().startswith('Ms12BeforeStep:\n jsr Ms24HurtTick')
    tick=source[source.index('Ms24HurtTick:'):source.index('Ms24Frozen:')]
    assert tick.startswith('Ms24HurtTick:\n lda GamePauseStatus\n and #1\n bne Ms24Phase')
    assert 'Ms12Lives'not in tick
    assert 'MsRS=$c81a' in source and 'MsSmc=$c826'in source
    assert 'ldx #7\n:lda R0,x\n sta MsRS+4,x'in source
    assert 'ldx #7\n:lda MsRS+4,x'in source
    assert 'Ms12Player=$c83d'in source and 'Ms12Effect=$c83f'in source
    assert not re.search(r'\bMs12(?:Lives|Player|Effect)\b[^\n;]*,[xy]',source,re.I)
    assert 'ConstructClear:\n .repeat 8,I\n sta MsState+I*$100,x\n .endrepeat'in source
    # Mathematical classifier only: CMP sets N from the byte subtraction;
    # no signed-V interpretation or emulated instructions are used here.
    classifications={'nonnegative_modulo':0,'negative_modulo':0};edge=[]
    for saved in range(256):
        for live in range(256):
            delta=(live-saved)&255;accept=not bool(delta&128)
            classifications['nonnegative_modulo'if accept else'negative_modulo']+=1
            if live in(saved,(saved+1)&255,(saved-1)&255):
                assert accept==(live!=((saved-1)&255))
        for step in(-1,0,1):
            live=(saved+step)&255
            if saved in(0,127,128,255):edge.append(dict(saved=saved,live=live,step=step,store=((live-saved)&128)==0))
    return dict(passed=True,detached=True,actual_parent_SHA256=H(raw),candidate_digest_only=PREDICTED,
        reviewed_initial_plan_SHA256='0126682f1901806a350d44f2d1c43eebf072f3ac9d8649c4dd223887d0fbf046',
        compact_packet_SHA256=PACKET_SHA,component_source_SHA256=H(members['component.s']),
        actor_SHA256=H(actor),renderer_SHA256=H(renderer),extra499_SHA256=H(extra),
        proposed_renderer_SHA256=H(revised),proposed_cookie=cookie.hex(),
        exact_spans=[dict(file=at,bytes=len(a),old_hex=a.hex(),new_hex=b.hex(),old_SHA256=H(a),new_SHA256=H(b))for at,a,b in spans],
        snapshot_source_references=references,current_literal_operands=literals,
        unchanged_ready_player_Fresh_guards=True,indexed_save_max_address='C825',SMC_save_range='C826..C828',
        constructor_clear_range='C000..C7FF (does not reach C83E)',
        first_callee_overwrites_NZ='Ms24HurtTick LDA GamePauseStatus / AND1; then explicit SEC/CLC returns',
        incoming_V_not_consumed_by_new_branch=True,public_AXYP_restoration_requires_source_gate=True,
        arithmetic_pairs=65536,classifications=classifications,all256_equal_plusminus1=True,wrap_edges=edge,
        accepted_delta_domain='00..7F; 80..FF constructs. Off-contract large modulo changes remain ambiguous, not exact signed ordering.',
        equal_path_added_cycles=4,CPU_or_menu_executed=False,ROM_overlay=False,whole_candidate_created=False,outputs=0)


if __name__=='__main__':
    q=review(ROM.read_bytes());text=json.dumps(q,sort_keys=True,separators=(',',':'))
    print('METAL_LIFE_INDEPENDENT '+text,flush=True)
    print('METAL_LIFE_INDEPENDENT_SHA256 '+H(text.encode()),flush=True)
