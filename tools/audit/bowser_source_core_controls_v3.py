"""Both boss motion kernels, actual native1 gravity and original3 math."""
from pathlib import Path
P=Path(__file__).with_name('bowser_source_core_controls_v1.py')
s=P.read_text(encoding='utf-8').replace('build/bowser-source-core-v1','build/bowser-source-core-v2').replace("out=O/'controls.json'","out=O/'controls-v3.json'")
s='\n'.join(l for l in s.splitlines()if not "labels={n:int(v,16)for n,v in re.findall(r'^al"in l)+'\n'
s=s.replace("  q['measured']=",'''  from check_tmnt_render_oa import load,address,location
  host=R/'build/coherent62-lives-fixes-v1/joint';h=load(host/'candidate.nes');native=[0]*65536
  pc=address(h,'ImposeGravity');off=location(h,'ImposeGravity');bank=(off-16)//8192;win=pc&0xe000
  native[win:win+8192]=h['raw'][16+bank*8192:16+(bank+1)*8192]
  nativefields=['Player_YMoveForceFractional','SprObject_Y_Position','SprObject_Y_HighPos','SprObject_Y_MoveForce','SprObject_Y_Speed']
  projected=[0x6005,0x6009,0x600d,0x601d,0x6001];gravity=[]
  for vel,force,frac,pos,page in itertools.product([0xfe,0xff,0,1,2], [0,1,15,127,128,240,255], [0,1,15,127,128,240,255], [0,1,127,255], [0,255]):
   for name,at,val in zip(nativefields,projected,[frac,pos,page,force,vel]):native[address(h,name)]=new[at]=val
   native[address(h,'R0')]=15;native[address(h,'R2')]=2
   a,lo=call(native,pc,a=0,x=0,p=0x71);z,lz=call(new,labels['Bw1Gravity'],p=0x71)
   wanted=[native[address(h,n)]for n in nativefields];actual=[new[a]for a in projected]
   assert wanted==actual,(vel,force,frac,pos,page,wanted,actual)
   assert native[address(h,'R7')]==new[0x601e]
   gravity.append([vel,force,frac,pos,page,a.processorCycles,z.processorCycles])
  q['checks']['original_native1_Bowser_gravity']=dict(actual_native_pairs=len(gravity),allfive_projected_fields_and_sign_exact=True,parameters=dict(source='MoveEnemySlowVert -> ImposeGravity A0',down_force=15,maximum_integer_speed=2),rows=gravity)
  call(new,labels['Bw3Fresh']);new[0x6009]=176;new[0x6014]=1;one=[]
  for tick in range(180):
   keys=(1 if tick<100 else 2)|(128 if 20<=tick<28 else0)|(64 if tick<70 else0)
   c,low=call(new,labels['Bw1Step'],a=keys)
   one.append(dict(tick=tick,input=keys,x=new[0x6008]+new[0x600c]*256,y=new[0x6009]+new[0x600d]*256,ground=new[0x6014],face=new[0x6015],pose=new[0x6016],emit=new[0x6019],cycles=c.processorCycles))
  assert min(r['y']for r in one)<176 and one[-1]['ground']==1
  assert one[90]['x']>one[0]['x']and one[170]['x']<one[100]['x']
  assert sum(r['emit']for r in one)==1 and next(r['tick']for r in one if r['emit'])==31
  assert all(r['pose']in range(4)for r in one)
  q['checks']['actual_native1_controller_sequence']=dict(whole_steps=180,rows=one,source_mouth20_closing_emission=True)
  q['measured']=''')
s=s.replace('abstract_active_state_bytes=28','abstract_active_state_bytes=31').replace('SMB1_physics_implemented=False','SMB1_physics_implemented=True')
s=s.replace('else0','else 0')
exec(compile(s,str(P),'exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
