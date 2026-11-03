"""Finish typed head/cold policies and freeze only the direct new source proof."""
import hashlib,json,re,zipfile
from pathlib import Path
import check_bub_head_projection_1102_v56 as H
import check_bub_original_upgrades_1102_v49 as Base
from py65.devices.mpu6502 import MPU
from check_tmnt_render_oa import location
O,Q,N,address,R,sha=H.O,H.Q,H.N,H.address,H.R,H.sha

def main():
    # Historical v49 reads the installed Downloads baseline. It has since
    # advanced legitimately; bind only that old helper input to the existing
    # exact read-only9cf cartridge, without editing frozen source or live ROM.
    baseline=O/'combined-current-landing.nes'
    assert sha(baseline)=='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'
    original_path=Base.Path
    def pinned_path(value):
        return baseline if str(value).replace('\\','/').lower()=='c:/users/kando/downloads/smb-crossover-latest-wip-mmc5.nes'else original_path(value)
    Base.Path=pinned_path
    try:old,b,route,q,p,image=H.bundle()
    finally:Base.Path=original_path
    proofs=[O/n for n in['head-projection-v56-CPU.json','head-projection-v57-ISR.json','head-projection-v60-NMI-I1.json','head-projection-v63-pending-map.json','head-projection-v64-nested.json','head-projection-v66-brick-profiles.json','head-projection-v68-brick-nested-small.json','head-projection-v68-brick-nested-powered.json']]
    for f in proofs:
        x=json.loads(f.read_text());assert x['passed']and x['memory_ROM_SHA256']==p['memory_ROM_SHA256']
        for name,digest in x['bindings'].items():assert sha(R/name)==digest,name
    noise_sites=[]
    for prefix in['GuestSharedSfx::','SoundEngine::']:
        for suffix,delta,code in [('PlayBrickShatter',2,'8ddc07'),('DecrementSfx3Length',0,'cedc07')]:
            name=prefix+suffix;pc=address(b,name)+delta;at=location(b,name)+delta
            assert b['raw'][at:at+3]==bytes.fromhex(code)
            noise_sites.append(dict(name=name,CPU=pc,physical_PRG=(at-16)//8192,hex=code))
    # Close old compiled readers of the reused telemetry byte as well as the
    # v56 writer census. Full-index overlaps are only the six-slot proxy token
    # arrays (Y=16*slot, slot<6), so no preexisting operation reads C3EF.
    bases={'BB_VECTORS':0xa000,'BB_IMPORTS':0xa080,'BB_CODE':0xa100,'BB_HOST':0xb540,'BB_ACTOR_HOLE':0xa071,'BB_BOX_HOLE':0xa0b0,'BB_SOUND_HOLE':0xb53a,'BB_VISIBLE_ADMISSION':0xa074,'CODE':0xb2b5}
    readers=[]
    for role in['source','native','head']:
        segment=None
        for line in(O/f'head-writers-v56-{role}.lst').read_text().splitlines():
            match=re.match(r'^([0-9a-fA-F]{6})r?\s+\d+\s+(.*)$',line)
            if not match:continue
            text=match[2].split(';',1)[0];seg=re.search(r'\.segment\s+"([^"]+)"',text)
            if seg:segment=seg[1]
            if not re.match(r'^[0-9a-fA-F]{2}(?:\s|$)',text):continue
            ins=re.search(r'\b(lda|ldx|ldy|cmp|cpx|cpy|adc|sbc|and|ora|eor|bit)\s+(.+)',text,re.I)
            if not ins:continue
            pc=bases[segment]+int(match[1],16)
            if role=='native'and q['labels']['BbNativeCeilingHit']<=pc<q['labels']['BbNativeCeilingHit']+7:continue
            mn,mode=MPU.disassemble[image[pc-0xa000]];assert mn.lower()==ins[1].lower(),(role,hex(pc),mn,ins[1])
            if mode not in['abs','abx','aby']:continue
            operand=int.from_bytes(image[pc-0xa000+1:pc-0xa000+3],'little');hi=operand+(255 if mode in['abx','aby']else 0)
            if operand<=0xc3ef<=hi:
                domain=None
                if role=='native':
                    if mode=='aby'and 0xc320<=operand<=0xc329:domain=dict(register='Y',values=[i*16 for i in range(6)],maximum_address=operand+80,source='Actual six native slots, indices helper and CPX6 bound already writer-qualified56.')
                    else:
                        assert mode=='abx'and operand in[0xc309,0xc3b0],(role,hex(pc),mn,mode,hex(operand),line)
                        # Exact four-byte snapshot/bbox copy, with LDX3 at
                        # its sole fallthrough ingress and DEX/BPL -9 tail.
                        code=image[pc-0xa000-2:pc-0xa000+9]
                        assert code[:5]==bytes([0xa2,3,0xbd,operand&255,operand>>8])
                        assert code[5]==0x9d and code[8:]==bytes.fromhex('ca10f7'),code.hex()
                        domain=dict(register='X',values=[3,2,1,0],maximum_address=operand+3,exact_loop_hex=code.hex())
                else:assert role=='head'and mode=='abs'and operand==0xc3ef
                readers.append(dict(role=role,CPU=pc,mode=mode,operand=operand,actual_index_domain=domain))
    assert any(x['role']=='head'for x in readers)and not any(x['role']=='source'for x in readers)
    # Source state, sprite packets and native coordinates stay exact during
    # the real ceiling response; only genuine native block/item effects differ.
    paired=0
    for identity in[0,1]:
        pair=[H.H.H.arena(bb,route,identity)[0]for bb in[old,b]]
        for epoch in range(55):
            for m in pair:
                keys=128 if 1<=epoch<26 else 0
                N.put(m,FrameCounter=epoch,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
                N.invoke(m,'GameCoreRoutine',x=0,y=0)
            a,z=pair
            assert a.ram[2][:0x300]==z.ram[2][:0x300],(identity,epoch,'original full actor/bubble/sprite state')
            assert[N.get(a,n)for n in['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_Y_Speed','NumberofLives']]==[N.get(z,n)for n in['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_Y_Speed','NumberofLives']],(identity,epoch,'native source-export coordinates')
            paired+=1
    # Every foreign raw follows unchanged code; new branch is private raw39.
    foreign=0
    for char in range(39):
        seeds=[Q.Q.fresh(bb,route,0)for bb in[old,b]]
        for flags in[0x21,0x71]:
            pair=[N.fork(m)for m in seeds];outs=[]
            for m in pair:
                N.put(m,SelectedCharacter=char);outs.append(N.invoke(m,'HuHead',a=83,x=7,y=14,p=flags))
            assert[outs[0][n]for n in['A','X','Y','P']]==[outs[1][n]for n in['A','X','Y','P']],(char,flags)
            assert bytes(pair[0][3:11])==bytes(pair[1][3:11])and bytes(pair[0][0x15a:0x17b])==bytes(pair[1][0x15a:0x17b])and pair[0].ram[2][:1024]==pair[1].ram[2][:1024]and pair[0].rawtags==pair[1].rawtags,(char,flags)
            foreign+=1
    bad=0
    for identity in[0,1]:
        seed=Q.Q.fresh(b,route,identity)
        for bank in[2,3]:
            for offset in range(16):
                m=N.fork(seed);m.ram[bank][0x1fe0+offset]^=1;m.ram[2][0x3ef]=0xf5
                before=bytes(m.ram[2][:1024]);out=N.invoke(m,'HuHead',a=83,x=7,y=14,p=0x71)
                assert not out['P']&1 and bytes(m.ram[2][:1024])==before
                bad+=1
    C=Q.Q.C;cold=[];art=b['raw'][1048592+441*1024:1048592+442*1024]
    for label,fault in[('cold',None),('code-readback',(3,2048)),('helper-readback',(2,0x1320)),('WRAM-protected','locked')]:
        m=C.ready(b);N.put(m,SelectedCharacter=39)
        if fault=='locked':m.protection=[0,0]
        elif fault:m.corrupt_at=fault
        scratch=bytes(m[3:11]);maps=m.rawtags[:];locked_before=[bytes(bank)for bank in m.ram]if fault=='locked'else None;out=C.call(m,0xae00)
        assert bytes(m[3:11])==scratch and m.rawtags==maps
        if fault is None:
            assert out['P']&1 and bytes(m.ram[3][:0x1fe0])==image[:0x1fe0]and bytes(m.ram[3][0x1ff0:])==image[0x1ff0:]
            assert bytes(m.ram[2][0x1000:0x1400])==art
            before=m.ppu_reads;writes=len(m.ram_writes);C.call(m,0xae00);assert m.ppu_reads==before and len(m.ram_writes)==writes
        elif fault=='locked':
            assert not out['P']&1 and[bytes(bank)for bank in m.ram]==locked_before
            assert m.ram[2][0x1fe0]!=167 and m.ram[3][0x1fe0]!=167
        else:assert not out['P']&1 and m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0,(label,out,m.ram[2][0x1fe0],m.ram[3][0x1fe0],m.corrupt_at,m.protection)
        cold.append(dict(case=label,carry=bool(out['P']&1),PPU_reads=m.ppu_reads))
    # Actual foreign retirement invalidates code/state authentication before
    # another owner can read pending. Reload+Fresh clears it, not menu guesses.
    retired=[]
    for identity in[0,1]:
        m=Q.Q.fresh(b,route,identity);m.ram[2][0x3ef]=0xf5;N.put(m,SelectedCharacter=0)
        C.call(m,0xae0b);assert m.ram[2][0x304]==0 and m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0
        N.put(m,SelectedCharacter=39);source=bytes(m.ram[2][:1024]);out=N.invoke(m,'HuHead',a=83,x=7,y=14,p=0x71)
        assert not out['P']&1 and bytes(m.ram[2][:1024])==source
        N.put(m,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255)
        assert C.call(m,0xae00)['P']&1
        N.put(m,FmGroups=128 if identity else 0);N.invoke(m,'HuFresh',x=0,y=0)
        assert m.ram[2][0x3ef]==0 and m.ram[2][0x304]==167 and m.ram[2][0x300]==identity
        retired.append(dict(identity=identity,foreign_retire_invalidates_both_headers=True,reloaded_fresh_pending_zero=True))
    # New gap and raw39 cookie are the only differences; all other roster,
    # Sunny, menu, shared router and native entry bytes remain literal exact.
    patches=[]
    for row in p['private_patches']:
        pc=row['CPU'];page=H.H.H.PAGES[(pc-0xa000)//1024];at=1048592+page*1024+(pc-0xa000)%1024
        patches.append(dict(file_offset=at,old=row['old'],new=row['new'],role=row['role']))
    at=q['cookie_offset'];patches.append(dict(file_offset=at,old=old['raw'][at:at+16].hex(),new=p['cookie'],role='Existing authenticated raw39 cookie'))
    raw=bytearray(old['raw']);changed=sum(a!=v for a,v in zip(raw,b['raw']))
    for row in patches:
        at=row['file_offset'];before=bytes.fromhex(row['old']);after=bytes.fromhex(row['new']);assert raw[at:at+len(before)]==before;raw[at:at+len(after)]=after
    assert bytes(raw)==b['raw']
    sources=[R/'tools/audit'/n for n in['measure_bub_deferred_head_1102_v54.py','measure_bub_head_projection_1102_v55.py','check_bub_head_projection_1102_v56.py','check_bub_head_interrupts_1102_v57.py','check_bub_head_nmi_i1_1102_v60.py','diagnose_bub_head_post_maps_1102_v62.py','check_bub_head_pending_map_1102_v63.py','check_bub_head_nested_phases_1102_v64.py','resume_bub_head_nested_1102_v65.py','check_bub_head_brick_profiles_1102_v66.py','check_bub_head_brick_nested_1102_v67.py','check_bub_head_brick_audio_1102_v68.py','freeze_bub_head_projection_1102_v59.py']]
    outputs=[O/n for n in['deferred-head-v54.s','deferred-head-v54.cfg','deferred-head-v54.bin','deferred-head-v54.lbl','deferred-head-v54-negative.json','head-projection-v55.s','head-projection-v55.cfg','head-projection-v55.bin','head-projection-v55.lbl','head-projection-v55-image.bin','head-projection-v55.json','head-projection-v56-CPU.json','head-projection-v57-negative.json','head-projection-v57-ISR.json','head-projection-v60-NMI-I1.json','head-projection-v62-map-negative.json','head-projection-v63-pending-map.json','head-projection-v64-gather-0.json','head-projection-v64-gather-1.json','head-projection-v64-nested.json','head-projection-v66-brick-profiles.json','head-projection-v67-brick-noise-negative.json','head-projection-v68-brick-gather.json','head-projection-v68-brick-nested-small.json','head-projection-v68-brick-nested-powered.json','head-writers-v56-source.lst','head-writers-v56-native.lst','head-writers-v56-head.lst']]
    result=dict(passed=True,CPU_qualified=True,ROM_written=False,installed=False,native_qualified=False,
        base_ROM_SHA256=H.H.PIN,expected_memory_ROM_SHA256=p['memory_ROM_SHA256'],cookie=p['cookie'],patches=patches,changed_bytes=changed,
        historical_helper_base=dict(path=str(baseline.relative_to(R)),SHA256=sha(baseline),scope='Only49 historical helper Downloads read rebound to existing exact9cf; all reconstructed b7e2/cc7b hashes strict, frozen sources and actual Downloads unchanged.'),
        source_gap_bytes=107,source_gap_remaining=538,root_startup_leaf_reserved_half_open=[0xb320,0xb32a],uncommitted_gap_after_root_reservation=528,pending_byte_compiled_reader_domains=readers,source_contact_original_state_coordinate_pairs=paired,foreign_actual_head_AXYP_scratch_SMC_maps_cases=foreign,bad_header_rejections=bad,cold=cold,retirement=retired,
        plain_brick_native_audio_clock_addresses=[0x7d8,0x7da,0x7db,0x7dc],plain_brick_noise_writer_preimages=noise_sites,
        receipt_wording_correction='68 inherits67 printed scope saying three audio clocks. Actual68 state/audio functions and all FF/nested comparisons track four:07D8/07DA/07DB/07DC. Completed receipts are retained unchanged; noise0to31 is admitted only at the four exact native writer sites listed here, and every IRQ/resumed foreground must preserve the real four-clock output.',
        scope='Source-owned head ABI projection, not a jump/velocity constant change. Actual source attempt142/source sweep159 returns native R4=14,DY-2,tileC1,row70,pointer03D5; unchanged native caller performs genuine block transaction after resident envelope returns. R0/R1 untouched,R3 actual tile,NZ tile-exact,X0,Y original adder. Real old clamp/source actors/bubbles/sprites/43px jump remain unchanged. No new pages, RAM byte allocation, shared ingress or foreign behavior. C3EF reuses retired telemetry; C3C8/C9/C382/C3CB remain exact through all intermediate movement/proxy/scroll/bbox queries. The normal later HuDraw occurs after head consumption. Cold/readback/auth/foreign retirement and real IRQ/FFlag/nested native IRQ proved; all additional post-head instructions with live bump/grow queues included. Root must still qualify earned emergence/maturity/collection and both gameplay routes in Mesen.',
        retained_negatives=['v54 deep native call inside retained resident envelope overwrites software farcall at SP121.','v57 first oracle excluded only07DA; actual native bump/grow clocks07D8/07DB advance, now exact writer-bound/tracked.','v62 next-op-only mapper oracle rejects actual original BankPRGC cache publication followed by LDA8D/STA5116; exact two-instruction pending bus proof63, with all other windows strict.','v67 shatter exposes genuine native noise clock07DC 0to31 through exact PlayBrickShatter/DecrementSfx3Length;68 tracks it, requires IRQ and resumed foreground preserve actual value.'],
        bindings={str(f.relative_to(R)):sha(f)for f in sources+outputs})
    receipt=O/'head-projection-v59-qualified.json';receipt.write_text(json.dumps(result,indent=2)+'\n')
    files=sources+outputs+[receipt];archive=O/'head-source-v59.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for f in files:z.write(f,str(f.relative_to(R)).replace('\\','/'))
    commit=O/'head-source-commit-files-v59.txt';commit.write_text('\n'.join(str(f.relative_to(R)).replace('\\','/')for f in sources)+'\n')
    frozen=dict(passed=True,archive=str(archive.relative_to(R)),archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,members={str(f.relative_to(R)):sha(f)for f in files},commit_files=str(commit.relative_to(R)),qualified_receipt=str(receipt.relative_to(R)),qualified_receipt_SHA256=sha(receipt),ROM_written=False,native=False)
    (O/'head-source-v59.json').write_text(json.dumps(frozen,indent=2)+'\n');print(json.dumps({k:result[k]for k in['passed','CPU_qualified','expected_memory_ROM_SHA256','changed_bytes','source_contact_original_state_coordinate_pairs','foreign_actual_head_AXYP_scratch_SMC_maps_cases','bad_header_rejections','cold','retirement']}));print(json.dumps({k:frozen[k]for k in['archive_SHA256','archive_bytes','qualified_receipt_SHA256']}))

if __name__=='__main__':main()
