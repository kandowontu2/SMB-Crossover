"""Sparse, private bat animation/timing repair; never installs or launches Mesen."""
from pathlib import Path
import configparser,difflib,gzip,csv,hashlib,json,subprocess,sys

R=Path(__file__).resolve().parents[2];B=R/'build'
BASE=B/'smb-crossover-mmc5-expanded.nes'
EXPECTED='bdf9ca2bfe69ee93ca85f1b5e5319e474d9f01aa641c79a58cd9bd602253c40e'
ORIGINAL=Path('C:/NES/StarTropics (USA).nes')
ORIGINAL_SHA='ff20d5e9600565ae61e4eae6594c9f1e55e2a748a46bba0c88285140420a219a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
SOURCE_PIPELINE={}
sys.path.insert(0,str(R/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load

def source_frames():
    """Run the actual source interpreter, with its one known bank-select leaf stubbed."""
    from py65.devices.mpu6502 import MPU
    assert sha(ORIGINAL)==ORIGINAL_SHA
    raw=ORIGINAL.read_bytes()[16:16+262144];result={}
    # Genuine source input caller: native Right bit1 -> direction2; native
    # Left bit2 -> direction3. Neighbor deltas are +1/-1 respectively.
    for buttons,want,delta in [(1,2,1),(2,3,255)]:
        mem=[0]*65536;mem[0xa000:0xc000]=raw[27*8192:28*8192]
        m=MPU(memory=mem);m.memory[0xd2]=buttons;m.pc=0xa348;m.sp=251;m.memory[0x1fc]=254;m.memory[0x1fd]=63
        while m.pc!=0x3fff:m.step()
        assert m.memory[0x37]==want and mem[0xa324+want]==delta
    for face in (2,3):
        mem=[0]*65536
        mem[0xa000:0xc000]=raw[26*8192:27*8192]
        mem[0xc000:0xe000]=raw[18*8192:19*8192]
        # FF30 only selects the already mapped source data bank18; its mapper
        # side effects/timing are outside this isolated interpreter contract.
        mem[0xff30]=0x60
        m=MPU(memory=mem);m.memory[0x60]=0x90|face;m.memory[0x185]=194
        rows=[]
        for tick in range(31):
            m.pc=0xaca4;m.sp=251;m.memory[0x1fc]=254;m.memory[0x1fd]=63
            steps=0
            while m.pc!=0x3fff:
                assert 0xa000<=m.pc<0xc000 or m.pc==0xff30,hex(m.pc)
                m.step();steps+=1;assert steps<5000
            rows.append(dict(tick=tick,state=m.memory[0x60],timer=m.memory[0x61],
                script_offset=m.memory[0x62],damage=m.memory[0x66],
                y=m.memory[0x6c],tile=m.memory[0x6d],attribute=m.memory[0x6e],x=m.memory[0x6f]))
        assert all(r['state']for r in rows[:30])and rows[30]['state']==0
        assert [r['tick']for r in rows if r['damage']]==list(range(8,16))
        assert all(rows[i]['tile']==rows[0]['tile']and rows[i]['attribute']==rows[0]['attribute']for i in range(8))
        assert all((rows[i]['tile'],rows[i]['attribute'])==(rows[18]['tile'],rows[18]['attribute'])for i in range(19,30))
        result[str(face)]=rows
        # Also execute the genuine B-edge admission and body interpreter,
        # which overlaps the weapon timeline and retains its lock one further
        # update after the weapon disappears. No manually invented delay.
        mem=[0]*65536;mem[0xc000:0xe000]=raw[18*8192:19*8192];mem[0xff30]=0x60
        m=MPU(memory=mem)
        for at,value in {0x38:face,0xd7:128,0x182:0x90,0x184:0xc0,0x185:194,0x187:1,0x188:8}.items():m.memory[at]=value
        def call(bank,pc):
            m.memory[0xa000:0xc000]=raw[bank*8192:(bank+1)*8192];m.pc=pc;m.sp=251;m.memory[0x1fc]=254;m.memory[0x1fd]=63
            steps=0
            while m.pc!=0x3fff:
                assert 0xa000<=m.pc<0xc000 or m.pc==0xff30,hex(m.pc)
                m.step();steps+=1;assert steps<5000
        call(27,0xa079);assert m.memory[0x770]==0xc0|face
        action=[]
        for tick in range(32):
            call(27,0xa55f);call(26,0xaca4)
            action.append(dict(tick=tick,body_state=m.memory[0x770],body_flags=m.memory[0x771],weapon_state=m.memory[0x60],damage=m.memory[0x66],tile=m.memory[0x6d],attribute=m.memory[0x6e]))
        assert all(r['body_state']for r in action[:31])and action[31]['body_state']==0
        assert [(r['weapon_state'],r['damage'],r['tile'],r['attribute'])for r in action[:31]]==[(r['state'],r['damage'],r['tile'],r['attribute'])for r in rows]
        SOURCE_PIPELINE[str(face)]=action
    # Retained real source execution independently agrees at EVERY bat frame,
    # including repeated windup and final hold, not just four unique tiles.
    old=[]
    with gzip.open(R/'build/mike-kd-private/original-weapons-c.csv.gz','rt')as f:
        for row in csv.DictReader(f):
            frame=int(row['frame'])
            if 893<=frame<=922:
                o=bytes.fromhex(row['oam']);old.append((frame,o[38*4+1],o[38*4+2]))
    assert len(old)==30
    assert [(t,a)for _,t,a in old]==[(r['tile'],r['attribute'])for r in result['2'][:30]]
    return result

HELPERS='''
; Authenticated source interpreter:8 windup,8 damaging,3 recovery motion,
; 11 recovery hold; clear on tick30. ShotAge1 corresponds to source tick0.
; SMB reach/terrain and body-relative coordinates remain existing adaptations.
.proc JnBatBeginAttack
 lda #1
 sta JnAttack
 lda #0
 sta JnHitMask
 php
 pha
 lda JnWeapon
 cmp #4
 bne Normal
 pla
 plp
 jsr JnRelease
 jmp JnWeapons::Active
Normal:
 pla
 plp
 jmp JnWeapons::Active
.endproc
.proc JnBatReleaseIfDue
 php
 pha
 lda JnWeapon
 cmp #4
 beq AlreadyVisible
 pla
 plp
 jmp JnRelease
AlreadyVisible:
 pla
 plp
 rts
.endproc
.proc JnBatAttackLimit
 lda JnWeapon
 cmp #4
 bne Normal
 lda JnAttack
 cmp #33
 jmp JnBatAttackLimitContinue
Normal:
 lda JnAttack
 cmp #19
 jmp JnBatAttackLimitContinue
.endproc
.proc JnBatContactIfActive
 php
 pha
 lda JnShotKind,x
 cmp #4
 bne Normal
 lda JnShotAge,x
 cmp #9
 bcc Inactive
 cmp #17
 bcs Inactive
Normal:
 pla
 plp
 jmp JnShotEnemies
Inactive:
 pla
 plp
 rts
.endproc
.proc JnBatSelectRecord
 php
 lda JnShotKind,x
 cmp #4
 bne Legacy
 lda JnShotAge,x
 beq Legacy
 cmp #31
 bcs Legacy
 tya
 pha
 lda JnShotAge,x
 sec
 sbc #1
 tay
 lda JnShotVX,x
 bne Velocity
 lda PlayerFacingDir
 cmp #2
 beq Left
 bne Lookup
Velocity:
 bpl Lookup
Left:
 tya
 clc
 adc #30
 tay
Lookup:
 lda JnBatRecordLo,y
 sta R0
 lda JnBatRecordHi,y
 sta R1
 pla
 tay
 plp
 lda R1
 jmp JnBatRecordSelected
Legacy:
 plp
 lda JnShotAllLo,y
 sta R0
 lda JnShotAllHi,y
 sta R1
 jmp JnBatRecordSelected
.endproc
'''

def main():
    assert sha(BASE)==EXPECTED
    frames=source_frames();b=scoped_load(BASE);changed={}
    old=(R/'src/mike_jones_weapons.s').read_text();new=old
    pairs=[('Begin:lda #1\n sta JnAttack\n lda #0\n sta JnHitMask','Begin:jmp JnBatBeginAttack\n .res 7,$ea'),
        (' jsr JnRelease\nAge:',' jsr JnBatReleaseIfDue\nAge:'),
        ('Age:inc JnAttack\n lda JnAttack\n cmp #19','Age:inc JnAttack\n jmp JnBatAttackLimit\n .res 2,$ea\n::JnBatAttackLimitContinue:'),
        (' jsr JnShotEnemies\nNext:',' jsr JnBatContactIfActive\nNext:'),
        ('Bat:\n lda JnShotAge,x\n cmp #12','Bat:\n lda JnShotAge,x\n cmp #31')]
    for a,z in pairs:assert new.count(a)==1,a;new=new.replace(a,z)
    changed['src/mike_jones_weapons.s']=new
    old=(R/'src/mike_jones_render.s').read_text();a=' lda JnShotAllLo,y\n sta R0\n lda JnShotAllHi,y\n sta R1';assert old.count(a)==1
    changed['src/mike_jones_render.s']=old.replace(a,' jmp JnBatSelectRecord\n .res 7,$ea\n::JnBatRecordSelected:').replace('.popseg',HELPERS+'\n.popseg')
    old=(R/'src/mike_jones_art.inc').read_text();rows=[];records={};names=[]
    for face in (2,3):
        for row in frames[str(face)][:30]:
            key=(row['tile']-28,row['attribute'])
            if key not in records:records[key]='JnBatNativeRecord'+str(len(records))
            names.append(records[key])
    for (tile,attr),name in records.items():rows.append(name+':.byte 4,'+str(tile)+','+str(attr)+',0,0')
    rows+=['JnBatRecordLo:.byte '+','.join('<'+n for n in names),'JnBatRecordHi:.byte '+','.join('>'+n for n in names)]
    assert old.count('.popseg')==1
    changed['src/mike_jones_art.inc']=old.replace('.popseg','; Exact source tiles/HV, existing SMB-relative record origin.\n'+'\n'.join(rows)+'\n.popseg')
    paths={}
    for name,text in changed.items():
        p=B/('mike_bat_'+Path(name).name);p.write_text(text,newline='\n');paths[name]=p
    wrapper=(R/'src/mike_jones.s').read_text()
    for name,p in paths.items():wrapper=wrapper.replace('"'+Path(name).name+'"','"'+p.name+'"')
    wrap=B/'mike_bat_family.s';wrap.write_text(wrapper,newline='\n')
    ep=B/'mike_bat_entrypoint.s';s=(R/'src/entrypoint.s').read_text();assert s.count('.include "mike_jones.s"')==1
    ep.write_text(s.replace('.include "mike_jones.s"','.include "'+wrap.name+'"'),newline='\n')
    c=B/'mike_bat_main.c';c.write_bytes((R/'src/main.c').read_bytes())
    def build(mapper=None,control=False):
        cfg=configparser.ConfigParser();cfg.optionxform=str;cfg.read(R/'build_options.ini')
        defs={k:v for s in cfg.values()for k,v in s.items()};defs.update(MAPPER_MMC3=str(int(mapper=='mmc3')),MAPPER_MMC5=str(int(mapper!='mmc3')),ENABLE_CROSSOVER='1')
        if mapper:defs.pop('ENABLE_MMC5_EXPANDED',None)
        else:defs['ENABLE_MMC5_EXPANDED']='1'
        out=B/('mike_bat'+('_'+mapper if mapper else '')+('_control'if control else'')+'.nes')
        cmd=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C',str(R/('smb1base.cfg'if mapper else'smb1base-mmc5-expanded.cfg')),
            '--ld-args','--dbgfile,'+str(out.with_suffix('.dbg')),'--include-dir',str(R),'--asm-include-dir',str(B),'--asm-include-dir',str(R/'src'),'--asm-include-dir',str(R),'--bin-include-dir',str(R),'-m',str(out.with_suffix('.map')),'-Ln',str(out.with_suffix('.lbl')),'-o',str(out)]
        for k,v in defs.items():cmd+=['--asm-define',k+'='+v,'-D',k+'='+v]
        cmd +=[str(c),str(R/'src/entrypoint.s'if control else ep)];z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);out.with_suffix('.build.log').write_text(z.stdout+z.stderr);assert z.returncode==0,z.stdout+z.stderr
        if not mapper:
            sys.path.insert(0,str(R/'tools'));from prepare_cv3_dmc_mirror import prepare;prepare(R,out)
        return out,cmd
    out,cmd=build();nb=scoped_load(out);raw=out.read_bytes()
    extents=[]
    for name in ['MIKE_GFX','MIKE_COMBAT']:
        og=next(g for g in b['segs'].values()if g.get('name')=='"'+name+'"');ng=next(g for g in nb['segs'].values()if g.get('name')=='"'+name+'"')
        start=int(og['ooffs'],0);end=start+int(og['size'],0);newend=int(ng['ooffs'],0)+int(ng['size'],0)
        assert int(ng['ooffs'],0)==start and newend>end
        assert b['raw'][end:newend]==b'\xff'*(newend-end)
        for g in b['segs'].values():
            if 'ooffs'in g:
                at,size=int(g['ooffs'],0),int(g['size'],0)
                assert not(size and at<newend and end<at+size)
        extents.append(dict(segment=name,physical_bank=(start-16)//8192,old_end=int(og['start'],0)+int(og['size'],0),append_bytes=newend-end,parent_FF_and_unowned=True))
    diff={k:sum(x!=y for x,y in zip(b['raw'][16+k*8192:16+(k+1)*8192],raw[16+k*8192:16+(k+1)*8192]))for k in range(128)};diff={k:v for k,v in diff.items()if v}
    assert set(diff)<={97,98};assert b['raw'][:16]==raw[:16]and b['raw'][16+128*8192:]==raw[16+128*8192:]
    # Genuine old labels remain at the same compiled PC. All new helpers are
    # appended; replaced source spans retain their literal assembled widths.
    from check_tmnt_render_oa import address,location
    moved=[]
    assert not[n for n in b['syms']if n.startswith('Jn')and n not in nb['syms']]
    for n in b['syms']:
        if n.startswith('Jn')and n in nb['syms']and 'seg'in b['syms'][n]and 'seg'in nb['syms'][n]:
            if address(b,n)!=address(nb,n)or location(b,n)!=location(nb,n):moved.append(n)
    assert not moved,moved
    ordinary={}
    for mapper in ('mmc3','mmc5'):
        p,_=build(mapper);control,_=build(mapper,True);ordinary[mapper]=dict(path=str(p),sha256=sha(p),fresh_control=str(control),fresh_control_sha256=sha(control));assert p.read_bytes()==control.read_bytes()
    patch=[]
    for n,t in changed.items():patch+=difflib.unified_diff((R/n).read_text().splitlines(True),t.splitlines(True),fromfile='bdf9/'+n,tofile='private/'+n)
    pp=B/'mike_bat.patch';pp.write_text(''.join(patch),newline='\n')
    put(B/'mike_bat_build.json',dict(passed=True,native_run=False,parent_sha256=EXPECTED,candidate_sha256=sha(out),ROM=str(out),command=cmd,
        changed_banks=diff,old_Jn_labels_moved=moved,CHR_header_exact=True,ordinary=ordinary,declared_append_extents=extents,
        changed_source={n:dict(path=str(p),sha256=sha(p))for n,p in paths.items()},patch_sha256=sha(pp),
        source_ROM_sha256=ORIGINAL_SHA,original_frames=frames,original_admission_body_weapon_pipeline=SOURCE_PIPELINE,
        contract='Actual original interpreter ticks0..29 visible, damage8..15, clear30. Candidate ShotAge1..30 maps ticks0..29; only bat timing and tile/HV record selection change. Existing SMB reach, collision geometry and record origin are explicit adaptations. Original visible-line CHR/palette parity remains unproved.'))
    print(json.dumps(dict(candidate_sha256=sha(out),changed_banks=diff,ordinary=ordinary)))

if __name__=='__main__':main()
