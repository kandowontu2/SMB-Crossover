"""Finite real-assembly mixed Goku rendering controls; no native/host admission."""
from pathlib import Path
import argparse,hashlib,itertools,json,re,sys,traceback
import prepare_dragon_power_mixed_render_v2 as P
import dragon_power_component_v1 as B
import dragon_power_art_v1 as A
from dragon_power_host_controls_v1 import execute,decoded
import dragon_power_host_controls_v1 as H
sys.path.insert(0,str(P.R/'tools/audit'))
from sunny_integrated_controls_v1 import scoped_load,address,location,seed,run
from verify_native_relocation import NesMPU

R=P.R;OUT=P.OUT;BASE=P.PARENT.with_suffix('.nes').read_bytes()
PARENT=scoped_load(P.PARENT.with_suffix('.nes'))
SMC=next((int(d['start'],0),int(d['ooffs'],0),int(d['size'],0))for line in P.PARENT.with_suffix('.dbg').read_text().splitlines()
         if line.startswith('seg\t')and 'name="SMCCODE"'in line for d in[dict(re.findall(r'(\w+)=("[^"]*"|[^,\r\n]+)',line))])
H.Memory.smc=SMC # Exact pinned parent SMC extent consumed by the inherited IRQ runner.

def bundle(folder):
    s=B.labels(P.PARENT.with_suffix('.lbl'));s.update(B.labels(folder/'component.lbl'))
    for line in (folder/'component.dbg').read_text().splitlines():
        if line.startswith('sym\t'):
            n=re.search(r'name="(Dp[^"]+)"',line);v=re.search(r'val=0x([0-9A-Fa-f]+)',line)
            if n and v:s[n[1]]=int(v[1],16)
    return dict(s=s,code=(folder/'component.bin').read_bytes(),art=(folder/'art.bin').read_bytes(),chr=(folder/'chr.bin').read_bytes(),folder=folder)

class Memory:
    smc=SMC
    def __init__(self,b):
        self.b=b;self.s=b['s'];self.rom=bytearray(BASE);self.ram=bytearray(32768);self.bank=[126,86,85,127];self.log=[]
        for bank,off,data in[(86,0x800,b['code']),(85,0x900,b['art'])]:self.rom[16+bank*8192+off:16+bank*8192+off+len(data)]=data
        self.rom[1048592+788*1024:1048592+796*1024]=b['chr']
        at,off,n=SMC;self.ram[at:at+n]=BASE[off:off+n]
        for name,val in dict(CurrentBank=214,CurrentBankC=213,SelectedCharacter=24,NumberofLives=2,AreaType=1,
                             AreaAddrsLOffset=0,WorldNumber=0,Player_Y_Position=100,Player_Y_HighPos=1,
                             Player_X_Position=100,Player_PageLoc=0,Player_Rel_XPos=100,PlayerFacingDir=1,
                             GameEngineSubroutine=8,DpReady=68,DpLife=2,DpArea=32,DpWorld=0,DpHP=100).items():self.ram[self.s[name]]=val
        self.ram[0x5204]=128
    def __getitem__(self,a):
        if isinstance(a,slice):return bytes(self[i]for i in range(*a.indices(65536)))
        a&=65535;return self.ram[a]if a<32768 else self.rom[16+self.bank[(a-32768)//8192]*8192+(a&8191)]
    def __setitem__(self,a,v):
        if isinstance(a,slice):
            ids=list(range(*a.indices(65536)));assert len(ids)==len(v)
            for i,n in zip(ids,v):self[i]=n
            return
        a&=65535;v&=255;self.log.append((a,v))
        if a<32768:self.ram[a]=v
        if 0x5114<=a<=0x5117:self.bank[a-0x5114]=v&127

def put(m,**kw):
    for n,v in kw.items():m.ram[m.s[n]]=v
def get(m,n):return m.ram[m.s[n]]
def regs(c):return(c.a,c.x,c.y,c.p&0xcf,c.sp)
def record(b,index):
    a=b['art'];at=a[index]|a[66+index]<<8;off=at-0xc900;n=a[off];return at,[tuple(a[i:i+4])for i in range(off+1,off+1+n,4)],a[132+index]
def physical_page(m):return get(m,'CurrentCHRBank')+256*(get(m,'X5ChrMode')&3)
def page_for(b,pose,face):return record(b,(pose if pose<32 else 0)*2+int(bool(face&64)))[2]
def canonical_oam(m,offsets,page=None):
    page=(physical_page(m)-788)if page is None else page;out=[]
    for off in offsets:
        y,t,attr,x=m.ram[0x200+off:0x204+off]
        pattern=m.b['chr'][page*1024+(t&254)*16:page*1024+(t&254)*16+32]
        out.append((y,pattern.hex(),attr,x))
    return out
def call(m,name,**kw):
    if name in PARENT['syms']:
        pc=address(PARENT,name);bank=(location(PARENT,name)-16)//8192
        if pc>=0x8000:
            window=(pc-0x8000)//8192;m.bank[window]=bank
            if window in[1,2]:m.ram[m.s['CurrentBank'if window==1 else'CurrentBankC']]=bank|128
    else:pc=m.s[name];m.bank[1]=86
    return execute(m,pc,**kw)

def snapshots(m,c,old,new,index,oldpage,newpage):
    """Exact named relocation/CHR/tile changes, not a general RAM/flag mask."""
    ptr_old,parts_old,_=record(old,index);ptr_new,parts_new,_=record(new,index)
    assert len(parts_old)==len(parts_new)
    # These parts retain order, palette and coordinates, but use new tile IDs.
    assert [p[1:]for p in parts_old]==[p[1:]for p in parts_new]
    replacements={}
    for name in['SmPosePtr','R0']:
        a=m.s[name];replacements[a]=(ptr_old&255,ptr_new&255);replacements[a+1]=(ptr_old>>8,ptr_new>>8)
    replacements[m.s['SmChrBank']]=(20+oldpage,20+newpage)
    replacements[m.s['CurrentCHRBank']]=(20+oldpage,20+newpage)
    # Normalize only literal art-pointer/page/tile differences after checking
    # each actual value against its independent descriptor and renderer output.
    ram=bytearray(m.ram)
    for at,(ov,nv)in replacements.items():
        assert ram[at]in[ov,nv],('pointer/page value',hex(at),ram[at],ov,nv)
        ram[at]=ov
    slots=[(at-0x200)&252 for at,v in m.log if 0x200<=at<0x300]
    slots=sorted(set(slots));mapping={p[0]:q[0]for p,q in zip(parts_new,parts_old)}
    if m.b is new:
        for off in slots:
            at=0x201+off
            if any(p==at for p,v in m.log):assert ram[at]in mapping;ram[at]=mapping[ram[at]]
    writes=[]
    for at,v in m.log:
        if 0x100<=at<0x200:continue # RTS/JSR consumed slots carry actual moved PCs.
        if at in replacements:
            ov,nv=replacements[at];assert v==(nv if m.b is new else ov);v=ov
        elif m.b is new and 0x201<=at<0x300 and (at&3)==1:
            assert v in mapping;v=mapping[v]
        writes.append((at,v))
    return regs(c),bytes(ram[:0x100])+bytes(ram[0x200:]),tuple(m.bank),writes

def native_setup(m,area=1,outline=0):
    q=seed(PARENT,0);run(q,'X5ColdInit');run(q,'GetAreaType',a=area<<5)
    for n in['CurrentCHRBank','X5ChrMode']:
        for i in range(12):m.ram[m.s[n]+i]=q.m[address(PARENT,n)+i]
    for n in['X5WideChrActive','SsChrActive','InvHudActive','X5SpecialChrUpper','X5HudChrUpper','ReloadCHRBank']:
        m.ram[m.s[n]]=q.m[address(PARENT,n)]
    put(m,PlayerOutlinesOff=outline)

def publish(m):
    c,w,_=call(m,'X5PublishChr');upper=0;pages={}
    for at,v in m.log[-100:]:
        if at==0x5130:upper=v&3
        if 0x5120<=at<=0x512b:pages[at-0x5120]=v+upper*256
    assert len(pages)==12;return pages

def draw_native(m):
    # The host plan must establish genuine native C12 ownership. This typed
    # arena invokes the real native caller with that known owner; it does NOT
    # claim current raw24 CrossoverGraphicsBank already routes correctly.
    m.bank[2]=12;put(m,CurrentBankC=140,R3=0,ObjectOffset=0)
    for n,v in[('Enemy_MovingDir',1),('Enemy_X_Position',160),('Enemy_PageLoc',0),('Enemy_Y_Position',140),('Enemy_Y_HighPos',1)]:m.ram[m.s[n]]=v
    start=get(m,'CurrentOAMOffset');call(m,'DrawMetasprite',x=address(PARENT,'METASPRITE_GOOMBA_WALKING_1'),y=1);mid=get(m,'CurrentOAMOffset')
    for n,v in[('FloateyNum_Control',1),('FloateyNum_X_Pos',192),('FloateyNum_Y_Pos',128)]:m.ram[m.s[n]]=v
    call(m,'FloateyNumberRender',x=0);return start,mid,get(m,'CurrentOAMOffset')

def sprite_bitmap(m,pages,start,end):
    out=[]
    for i in range(start,end,4):
        y,t,a,x=m.ram[0x200+i:0x204+i];window=((t&1)*4096+(t&254)*16)//1024
        page=pages[window];off=(t&254)*16%1024;pat=m.rom[1048592+page*1024+off:1048592+page*1024+off+32]
        out.append((y,bytes(pat).hex(),a,x))
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert not a.output.exists()
    old,new=bundle(P.OLD),bundle(OUT);files=[Path(__file__),R/'tools/prepare_dragon_power_mixed_render_v2.py',
        R/'tools/dragon_power_host_controls_v1.py',R/'tools/dragon_power_art_v1.py',R/'tools/dragon_power_reference_v1.py',
        R/'tools/audit/sunny_integrated_controls_v1.py',R/'tools/audit/verify_native_relocation.py',OUT/'build-proof.json',
        R/'docs/qa/dragon-power-host-integration-plan-2026-10-28.json']
    files +=[f/p for f in[P.OLD,OUT]for p in['component.bin','component.dbg','component.lbl','art.bin','chr.bin']]
    proof=dict(passed=False,source_CPU_only=True,native_run=False,bindings={str(p.resolve()):P.sha(p)for p in files},checks={});ck=proof['checks']
    try:
        # Independent original executable source versus actual final CHR data.
        rows=[]
        for index in range(66):
            pose=index//2 if index<64 else 0;face=64*(index&1);wave=index>=64
            ptr,parts,page=record(new,index)
            for pg in(range(7)if wave else[page]):
                oam=[(100+p[2]&255,p[0],p[1],100+(p[3]if p[3]<128 else p[3]-256)&255)for p in reversed(parts)]
                source,_,_=A.pixels(pose,face,wave);want={(x,y+16):v for(x,y),v in source.items()}
                assert decoded(new['chr'],pg,oam)==want,('original palette-class pixels',index,pg)
            rows.append([index,len(parts),page])
        ck['original_source_pixels']=dict(passed=True,records=66,wave_records_all7_pages=True,both_faces=True,source_palette_classes_and_geometry_exact=True,parts_range=[min(r[1]for r in rows),max(r[1]for r in rows)])
        # All physical body/wave combinations in both genuine call orders.
        rows=[]
        for pose,face,shot,order in itertools.product(range(32),[0,64],[2,3],['body-shot','shot-body']):
            m=Memory(new);native_setup(m);put(m,DpPose=pose,DpAttribute=face,DpShotState=shot,DpShotX=180,DpShotY=116)
            pieces={}
            for kind in order.split('-'):
                start=get(m,'CurrentOAMOffset');call(m,'DpDrawBody'if kind=='body'else'DpDrawShots');end=get(m,'CurrentOAMOffset')
                pieces[kind]=[tuple(m.ram[i:i+4])for i in range(0x200+start,0x200+end,4)]
            pg=physical_page(m)-788;assert pg==page_for(new,pose,face)
            for kind,origin in[('body',(100,100)),('shot',(180,100))]:
                source,_,_=A.pixels(pose if kind=='body'else 0,face if kind=='body'else(0 if shot==2 else 64),kind=='shot')
                assert decoded(new['chr'],pg,pieces[kind],origin)=={(x,y+16):v for(x,y),v in source.items()},('mixed',pose,face,shot,order,kind,pg)
            assert all(not 0x4000<=at<=0x4017 for at,v in m.log)
            rows.append([pose,face,shot,order,len(pieces['body']),len(pieces['shot']),pg])
        ck['mixed_actual_full_draw_callers']=dict(passed=True,cases=len(rows),both_orders=True,all_32_body_poses_both_faces_both_wave_directions=True,final_published_body_page_matches_both_images=True,no_APU_DMA_writes=True)
        # Strict old/new caller state and ordered writes, with only exact named
        # data relocation/CHR/tile representation translations above.
        costs=[];n=0
        for index,flags,rotation,start,edge in itertools.product(range(66),[0x30,0x31,0x70,0xf9],[0,4,252],[0,192,236,252],[False,True]):
            pose=index//2 if index<64 else 6;face=64*(index&1);outs=[]
            for b in[old,new]:
                m=Memory(b);put(m,DpPose=pose,DpAttribute=face,GuestOamRotationActive=int(rotation!=0),RgOamRotation=rotation,CurrentOAMOffset=start)
                if edge:put(m,Player_Rel_XPos=0,Player_Y_Position=0)
                if index>=64:put(m,DpShotState=2 if index==64 else 3,DpShotX=0 if edge else 100,DpShotY=16 if edge else 116)
                m.log=[];c,_,_=call(m,'DpDrawBody'if index<64 else'DpDrawShots',a=91,x=177,y=93,p=flags)
                oldpage=record(old,index)[2];newpage=page_for(new,pose,face)
                outs.append(snapshots(m,c,old,new,index,oldpage,newpage));costs.append((index,b is new,c.processorCycles))
            assert outs[0]==outs[1],('full caller ABI/remaining RAM/ordered writes',index,flags,rotation,start,edge)
            n+=1
        diffs=[costs[i+1][2]-costs[i][2]for i in range(0,len(costs),2)]
        ck['old_new_full_caller_ABI']=dict(passed=True,cases=n,AXYP_SP_strict=True,all_other_application_RAM_ordered_writes_banks_5SMC_strict=True,
            exact_translations=['actual record pointer R0/R1 and SmPosePtr','SmChrBank and CurrentCHRBank0 to the selected real new page','literal per-record tile remap, exact original pattern/palette/XY'],
            consumed_JSR_RTS_stack_PC_slots='Different genuine moved component PCs; live return stack and SP separately checked by ISR controls',CPU_delta=[min(diffs),max(diffs)],body_CPU_delta=[min(diffs[:-192]),max(diffs[:-192])])
        # Actual full-capacity rejection: header+logical cursor overflow rejects
        # the entire record before any OAM write, independent of physical wrap.
        n=0
        for index in range(66):
            count=len(record(new,index)[1])*4
            for rotation in[0,4,252]:
                for start in[256-count,260-count,252]:
                    m=Memory(new);pose=index//2 if index<64 else 6;face=(index&1)*64
                    put(m,DpPose=pose,DpAttribute=face,CurrentOAMOffset=start,GuestOamRotationActive=int(rotation!=0),RgOamRotation=rotation,DpShotState=2 if index==64 else 3,DpShotX=100,DpShotY=116)
                    before=bytes(m.ram[0x200:0x300]);c,_,_=call(m,'DpDrawBody'if index<64 else'DpDrawShots')
                    assert not c.p&1 and get(m,'CurrentOAMOffset')==start and bytes(m.ram[0x200:0x300])==before,('true exhaustion',index,start,rotation)
                    n+=1
        ck['true_native_OAM_exhaustion']=dict(passed=True,cases=n,whole_record_rejected_at_logical_sum256_or_more=True,no_partial_OAM_or_cursor_advance=True,physical_rotation_wrap_preserved=True)
        # Actual hardware register publication, initialized native area profiles,
        # genuine native Goomba and score record callers. Not a host GameLoop.
        n=0
        for area,outline,pose,face,shot in itertools.product(range(4),[0,1],[0,5,15,26,31],[0,64],[2,3]):
            ref=Memory(new);native_setup(ref,area,outline);baselinepages=publish(ref);s0,s1,s2=draw_native(ref);expected=sprite_bitmap(ref,baselinepages,s0,s2)
            m=Memory(new);native_setup(m,area,outline);put(m,DpPose=pose,DpAttribute=face,DpShotState=shot,DpShotX=180,DpShotY=116)
            call(m,'DpDrawBody');call(m,'DpDrawShots');s0,s1,s2=draw_native(m);pages=publish(m)
            assert all(pages[i]==baselinepages[i]for i in range(1,12)),('world CHR owner',area,outline,pose,face,shot)
            assert sprite_bitmap(m,pages,s0,s2)==expected
            assert m.ram[m.s['X5ChrMode']+1:m.s['X5ChrMode']+12]==ref.ram[ref.s['X5ChrMode']+1:ref.s['X5ChrMode']+12]
            n+=1
        ck['native_world_score_mix']=dict(passed=True,cases=n,all4_areas_both_outlines=True,actual_Goomba_DrawMetasprite_and_FloateyNumberRender=True,actual_X5PublishChr_5130_and_all12_registers_decoded=True,all11_nonbody_windows_and_native_glyph_patterns_exact=True,native_C12_record_owner_explicit_not_current_raw24_dispatch_admission=True)
        # Genuine foreground raw24 rejection remains exact for every other ID.
        n=0
        for char,name in itertools.product([i for i in range(256)if i!=24],['DpGraphics','DpGraphicsBank','DpDrawBody','DpDrawShots','DpSetRecord','DpPublish','DpRender','DpPalettePointer']):
            outs=[]
            for b in[old,new]:
                m=Memory(b);put(m,SelectedCharacter=char);c,_,_=call(m,name,a=19,x=64,y=93,p=0x71)
                outs.append((regs(c),bytes(m.ram[:0x100])+bytes(m.ram[0x200:]),m.bank,[(at,v)for at,v in m.log if not 0x100<=at<0x200],c.processorCycles))
            assert outs[0]==outs[1],('foreign',char,name);n+=1
        ck['foreign_full_callers']=dict(passed=True,cases=n,AXYP_SP_application_RAM_ordered_writes_banks_cycles_exact=True)
        # Source IRQ at every reached component instruction for body and wave.
        n=0
        for name,face,shot in itertools.product(['DpDrawBody','DpDrawShots'],[0,64],[2,3]):
            m=Memory(new);put(m,DpPose=6,DpAttribute=face,DpShotState=shot,DpShotX=180,DpShotY=116)
            end,trace,_=call(m,name,p=0x30);before=bytes(m.ram);entries=sorted(set(pc for pc in trace if 0xa800<=pc<0xa800+len(new['code'])))
            for pc in entries:
                q=Memory(new);put(q,DpPose=6,DpAttribute=face,DpShotState=shot,DpShotX=180,DpShotY=116)
                c,_,obs=execute(q,q.s[name],inject=pc,p=0x30)
                assert obs and regs(c)==regs(end) and q.bank==m.bank
                assert q.ram[:0x100]==before[:0x100] and q.ram[0x200:]==before[0x200:],('IRQ remaining RAM',name,face,shot,hex(pc))
                n+=1
        ck['actual_parent_IRQ']=dict(passed=True,cases=n,full_six_flags_AXY_SP_PC_mapper_all5SMC_restored_at_injection=True,final_nonstack_RAM_OAM_banks_exact=True,NMI_not_claimed='No Goku shared AudioUpdate or regular NMI admission yet; actual parent IRQ source only')
        assert all(P.sha(p)==h for p,h in proof['bindings'].items());proof['passed']=True
        proof['limits']=['Source CPU/mapper and authentic original pattern-class evidence; no native PPU, scanline visibility, palette color fidelity or frame cadence claim.',
            'This unadmitted sparse component cannot execute a genuine raw24 host GameLoop; full caller means the complete compiled DpDrawBody/DpDrawShots -> FarCallCommon -> actual native MetaspriteRenderLoop chain.',
            'The Goku plan retains separate unresolved actor HP/block adapters, palette/UI, resident raw24 bank routing and atomic audio publication. No shared integration/adoption.']
    except Exception as e:proof.update(failure=repr(e),traceback=traceback.format_exc())
    a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=proof['passed'],failure=proof.get('failure'),checks=list(ck))))
    assert proof['passed']

if __name__=='__main__':main()
