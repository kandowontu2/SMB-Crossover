"""Qualify actual Main weapon-tail forwarding, preserving all foreign owners."""
from pathlib import Path
import hashlib,itertools,json,re,subprocess,zipfile
import check_arthur_maturity_fix_1102_v12 as Q
from private_build_outputs_v1 import validate
from prepare_selected_native_packet_v1 import prepare
C=Q.C;P=Q.P;M=Q.M;R=P.R;O=P.O
BASE=R/'build/excitebike-pose-1101-v3/current3.nes'
SHA='37959000690d3f9fe596823fc0910e86b9fc977448779360d523751764248b0c'
SOURCE=R/'tools/reference/arthur_weapon_tail_1102_v15.s'


def main():
 assert P.sha(BASE)==SHA;old=C.scoped_load(BASE);raw=bytearray(old['raw']);slot=C.location(old,'ArOwnServices')+3*34
 off=lambda pc:16+70*8192+pc-0xa000
 ownlabels={n:int(a,16)for a,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(R/'build/arthur-camera-1101-v3/camera.lbl').read_text(),re.M)}
 set4,set18=ownlabels['ArOwnSet4'],ownlabels['ArOwnSet18'];assert raw[slot:slot+3]==bytes([0x4c,set18&255,set18>>8])
 assert raw[C.location(old,'ArOwnServices')+12:C.location(old,'ArOwnServices')+15]==bytes([0x4c,set4&255,set4>>8])
 prefix=raw[off(set4):off(set4)+9];assert prefix[0]==8 and prefix[3]==0x48 and prefix[6]==0x4c
 assert prefix[1:3]==bytes([0xa9,C.address(old,'ArHostShotContacts')&255])and prefix[4:6]==bytes([0xa9,C.address(old,'ArHostShotContacts')>>8])
 cc=R/'tools/Windows/cc65/bin';s=O/'weapon-tail.s';s.write_text(f'ArOwnSet4=${set4:04x}\n'+SOURCE.read_text());cfg=O/'weapon-tail.cfg';cfg.write_text('MEMORY{M:start=$bd66,size=3,file=%O;}SEGMENTS{WEAPON_TAIL:load=M,type=ro;}')
 for cmd in [[cc/'ca65.exe',s,'-o',O/'weapon-tail.o'],[cc/'ld65.exe','-C',cfg,O/'weapon-tail.o','-o',O/'weapon-tail.bin']]:
  cmd=list(map(str,cmd));validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
 entry=(O/'weapon-tail.bin').read_bytes();assert entry==bytes([0x4c,set4&255,set4>>8]);raw[slot:slot+3]=entry
 new=dict(old);new['raw']=bytes(raw);gold=dict(old);gr=bytearray(old['raw']);gr[off(set18):off(set18)+9]=prefix;gold['raw']=bytes(gr)
 def construct(b):
  m=C.seed(b);M.put(m,SelectedCharacter=32,ArHostReady=0,OperMode_Task=3,DisableScreenFlag=1,Mirror_PPUMASK=0,CurrentPlayer=0,NumberofLives=2)
  M.invoke(m,'HuFresh');assert M.get(m,'ArHostReady')==167 and M.get(m,'ArR_053A')==64
  return m
 initial=[construct(b)for b in [old,new,gold]];foreign=0
 for rawid,flag in itertools.product([i for i in range(39)if i!=32],[0x20,0x31,0x61,0xa9]):
  pair=[]
  for base in initial[:2]:
   m=M.fork(base);M.put(m,SelectedCharacter=rawid,AreaType=1)
   z=M.invoke(m,'ProcFireball_Bubble',a=85,x=0,y=0,p=flag);pair.append((m,z))
  Q.same(*pair[0],*pair[1],('foreign actual weapon/bubble caller',rawid,flag));foreign+=1
 print('Foreign actual ProcFireball_Bubble parity',foreign,flush=True)
 with zipfile.ZipFile(R/'build/_recovery/legacy-sources-2026-10-31.zip')as z:
  ix={q['path']:q for q in json.loads(z.read('index.json'))};item=ix['arthur-physical-clock-v2/joint/union.s'];union=z.read('objects/'+item['sha256']).decode()
 routes=re.findall(r'\.proc (Hu\w+)\n sta SafecallA_SMC\+1\n php\n tya\n pha\n ldy #(\d+)',union);assert len(routes)==36 and dict((int(i),n)for n,i in routes)[34]=='HuWeaponTail';rows=0
 for name,index in routes:
  if int(index)==34:continue
  for flag in [0x20,0x31,0x61,0xa9]:
   pair=[]
   for base in initial[:2]:
    m=M.fork(base);z=M.invoke(m,name,a=0,x=0,y=0,p=flag);pair.append((m,z))
   Q.same(*pair[0],*pair[1],('other owned row',index,name,flag));rows+=1
 print('All other35 owned rows exact',rows,flush=True)
 names=['ProcFireball_Bubble','NrObjectWeaponTail','HuWeaponTail','HuWeapons','ArHostShotContacts','ArNativeShotContact','HandleEnemyFBallCol','ArNativeLance']
 points={Q.point(old,n):n for n in names};active={};cls=M.NesMPU;step=cls.step;cuts={}
 def record(c):
  if c.pc>=0x8000:
   bank=c.memory.rawtags[(c.pc-0x8000)//8192];n=points.get((bank,c.pc))
   if n:active[n]=active.get(n,0)+1
   if c.memory.bundle is new and bank==198 and(c.pc==0xbd66 or set4<=c.pc<set4+9 or ownlabels['ArOwnStoreNormal']<=c.pc<ownlabels['ArOwnStoreProbe']):cuts.setdefault((c.pc,c.sp),(M.fork(c.memory),C.state(c)))
  return step(c)
 cls.step=record;pipeline=0;proofrows=[]
 try:
  for enemy,face,page,flag in itertools.product([0,6,2,0x2d],[1,2],[0,1],[0x20,0x61]):
   pair=[];visits=[]
   for base in initial[1:]:
    m=M.fork(base);player=page*256+(247 if face==1 else 70);target=(player+(53 if face==1 else -53))&65535;camera=(player-120)&65535
    M.put(m,Player_X_Position=player&255,Player_PageLoc=player>>8,Player_Y_Position=176,Player_Y_HighPos=1,ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8,PlayerFacingDir=face,ObjectOffset=0,AreaType=1,WorldNumber=0,BowserHitPoints=5,CurrentBankC=191);m[0x5116]=191
    for name,value in [('Enemy_Flag',1),('Enemy_ID',enemy),('Enemy_State',0),('Enemy_X_Position',target&255),('Enemy_PageLoc',target>>8),('Enemy_Y_Position',184 if enemy==6 else 176),('Enemy_Y_HighPos',1)]:m[C.address(old,name)]=value
    M.invoke(m,'ArHostImport');M.invoke(m,'ArStep',a=face,x=0)
    active.clear();trajectory=[];reached=False
    for age in range(24):
     keys=64 if age%6<2 else 0;M.invoke(m,'ArStep',a=keys,x=0)
     trajectory.append([age,*[M.get(m,'ArR_05AF',1)+256*M.get(m,'ArR_0583',1),M.get(m,'ArR_0509',1)]])
     z=M.invoke(m,'ProcFireball_Bubble',a=85,x=0,y=0,p=flag)
     if active.get('HandleEnemyFBallCol',0):reached=True;break
    assert reached and active.get('HuWeaponTail')and active.get('ArHostShotContacts')and active.get('ArNativeShotContact'),('Missing actual source/native pipeline',enemy,face,page,active)
    assert not active.get('HuWeapons'), 'The unrelated public row4 is not actual Main ingress'
    if enemy in [0,6]:assert M.get(m,'Enemy_State')&32
    elif enemy==2:assert not M.get(m,'Enemy_State')&32
    else:assert M.get(m,'BowserHitPoints')==4
    pair.append((m,z));visits.append(dict(active))
   Q.same(*pair[0],*pair[1],('actual sourceB weapon/native caller',enemy,face,page,flag));assert visits[0]==visits[1]
   pipeline+=1;proofrows.append(dict(enemy=enemy,facing=face,page=page,flags=flag,calls=visits[0],source_updates=len(trajectory),shot_first_last=[trajectory[0],trajectory[-1]]))
 finally:cls.step=step
 print('Actual sourceB/Main/native hit pipeline',pipeline,flush=True)
 for kind,(m0,s)in itertools.product(['IRQ','lag-NMI'],cuts.values()):
  m=M.fork(m0);c=cls(memory=m,pc=s[0]);c.pc,c.a,c.x,c.y,c.p,c.sp=s;before=C.state(c);smc=bytes(m[0x15a:0x17b]);live=bytes(m[0x101+c.sp:0x200]);maps=m.rawtags[:]
  expected_ram=[bytearray(v)for v in m0.ram]
  # The genuine physical NMI clock must advance its authenticated mailbox,
  # even while Main is interrupted. Predict its exact original3-byte effect;
  # do not demand frozen time or broadly exclude the private cache.
  if kind=='lag-NMI' and expected_ram[2][0x1fd4]==167 and expected_ram[2][0x1fd3]==M.get(m0,'CurrentPlayer'):
   phase=(expected_ram[2][0x1fd0]-1)&255
   if phase==0:phase=3;expected_ram[2][0x1fd1]=1
   expected_ram[2][0x1fd0]=phase
   expected_ram[2][0x1fd2]=M.get(m0,'SavedJoypad1Bits',M.get(m0,'CurrentPlayer'))
  if kind=='IRQ':c.irq()
  else:c.nmi()
  for _ in range(100000):
   if C.state(c)==before:break
   assert m[c.pc]!=0,(kind,hex(before[0]),'BRK');c.step()
  else:raise AssertionError((kind,hex(before[0]),'ISR bound'))
  assert bytes(m[0x15a:0x17b])==smc and bytes(m[0x101+c.sp:0x200])==live and m.rawtags==maps and m.ram==expected_ram,(kind,hex(before[0]),'ISR preserved state',maps,m.rawtags,[(hex(i),m0[i],m[i])for i in range(0x15a,0x17b)if m0[i]!=m[i]],[(j,i,a,b)for j in range(4)for i,(a,b)in enumerate(zip(expected_ram[j],m.ram[j]))if a!=b][:5])
 assert cuts
 delta=[dict(file_offset=i,old=a,new=b)for i,(a,b)in enumerate(zip(old['raw'],new['raw']))if a!=b];assert len(delta)==2 and [v['file_offset']for v in delta]==[slot+1,slot+2]
 digest=hashlib.sha256(new['raw']).hexdigest();q=dict(passed=True,source_CPU_only=True,native=False,base_sha256=SHA,proposed_candidate_sha256=digest,only_physical_PRG_bank=70,owned_policy_row=34,owned_CPU_half_open=['BD66','BD69'],delta=delta,foreign_actual_weapon_bubble_cases=foreign,other35_Arthur_public_policy_full_state_cases=rows,actual_source_B_original_native_hit_cases=pipeline,source_B_cases=proofrows,IRQ_lag_NMI_cuts=2*len(cuts),no_new_PRG_CHR_RAM=True,scope='Actual ProcFireball_Bubble -> NrObjectWeaponTail -> HuWeaponTail34 -> existing Arthur row4 worker, followed by original native air-bubble continuation. Exact AXYP/all application/cache/WRAM/palette/mapper parity against independent existing row4 transport copied at former row34 transport address. Synthetic legal enemy placements; genuine sourceB shot spawn/motion and actual native Goomba/Koopa/Buzzy/Bowser consumers. No native/whole-stage claim.',bindings={str(p.relative_to(R)):P.sha(p)for p in [Path(__file__),SOURCE,BASE,O/'weapon-tail.bin',R/'build/arthur-camera-1101-v3/camera.lbl',Path(Q.__file__)]})
 proof=O/'weapon-tail-CPU.json';proof.write_text(json.dumps(q,indent=2)+'\n')
 rom=O/'weapon-tail-candidate.nes';rom.write_bytes(new['raw'])
 for ext in ['.dbg','.lbl']:rom.with_suffix(ext).write_bytes(BASE.with_suffix(ext).read_bytes())
 ref=O/'weapon-ingress/controller.lua';t=ref.read_text();oldnames="{'NrWeapons','HuWeapons','ArHostShotContacts'";assert t.count(oldnames)==1;t=t.replace(oldnames,"{'ProcFireball_Bubble','NrObjectWeaponTail','HuWeaponTail','NrWeapons','HuWeapons','ArHostShotContacts'",1)
 prepare(O/'weapon-tail-native',rom,t,[Path(__file__),SOURCE,ref,proof],expected=digest,timeout=150,allow_interactive=True,scope='Exactly unchanged genuine firstenemy stop/shoot controls and native enemy hit/no-life-loss assertion; read-only actualtail34 ingress and sourcecontact/returnC/shotlifetime observers added. Earlier native missing-ingress negative retained. No RAM/sourcephysics/BBox/stage/helper changes.')
 print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','source_B_cases']}))


if __name__=='__main__':main()
