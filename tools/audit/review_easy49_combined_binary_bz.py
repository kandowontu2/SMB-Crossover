from pathlib import Path
import importlib.util,json,math,hashlib
R=Path('.').resolve();H=R/'build/verification/agent49-bill-advanced-parity-h';A=H.parent/'root49-easy-advanced-union-ap/source';G=H.parent/'agent49-enemy-geometry-advanced-g/candidate-c2';S=H.parent/'root49-easy-combined-bq/source'
sp=importlib.util.spec_from_file_location('im',R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def raw(im,name,count,scope=None):
 h=im.hook(name,scope);return im.raw[h['rom_offset']:h['rom_offset']+count]
rows={}
for mp in ['mmc3','mmc5']:
 old=m.Image(A/f'build/smb-crossover-{mp}.nes');new=m.Image(S/f'build/smb-crossover-{mp}.nes');g=m.Image(G/f'smb-crossover-{mp}.nes');aa={x['name']:x for x in old.segs.values()};bb={x['name']:x for x in new.segs.values()};audio=[];tails=[]
 for n,v in aa.items():
  w=bb[n]
  if v['type']=='bss':assert(v['start'],v['size'])==(w['start'],w['size']),n
  if ('AUDIO'in n or 'DPCM'in n or n=='MUSIC'or n.startswith('XG_MUSIC'))and v.get('type')=='ro'and'ooffs'in v:
   assert(v['start'],v['size'],v['ooffs'])==(w['start'],w['size'],w['ooffs']),n
   assert old.raw[v['ooffs']:v['ooffs']+v['size']]==new.raw[w['ooffs']:w['ooffs']+w['size']],n;audio.append(n)
 for n in [n for n in bb if n=='BILL_COLD'or n.startswith('BILL_ORBIT_')]:
  v=bb[n];assert old.raw[v['ooffs']:v['ooffs']+v['size']]==b'\xff'*v['size'],n;tails.append({k:v[k]for k in ['name','start','size','ooffs']})
 assert old.raw[:16]==new.raw[:16]
 for n,v in old.ram.items():assert new.ram[n]==v,n
 for n in ['RosterDrawShots']:
  a=old.sym(n);b=new.sym(n);assert a['size']==b['size'];assert raw(old,n,a['size'])==raw(new,n,b['size']),n
 for side in ['Right','Left']:
  for axis in ['XLo','XHi','YLo','YHi']:
   n='BillFlare'+side+axis
   p=raw(new,n,240)if n!='BillFlareLeftXLo'else raw(new,n+'Prefix',96)+raw(new,n+'Tail',144)
   q=raw(g,n,240)if n!='BillFlareLeftXLo'else raw(g,n+'Prefix',96)+raw(g,n+'Tail',144)
   assert p==q,n
 # Every compiled source scalar through4096, independent iterative double order.
 scalar=0;minimum_round_distance=1
 for side in ['Right','Left']:
  angle=-1 if side=='Right'else-math.pi/2;delta=11/30 if side=='Right'else-11/30
  expected=[[],[],[],[]]
  for k in range(4096):
   vals=[4096*math.cos(angle),4096*math.sin(angle)];x,y=[math.floor(v+.5)for v in vals]
   minimum_round_distance=min(minimum_round_distance,*[abs((v-math.floor(v))-.5)for v in vals]);angle+=delta
   for a,v in zip(expected,[x&255,(x>>8)&255,y&255,(y>>8)&255]):a.append(v)
  for j,axis in enumerate(['XLo','XHi','YLo','YHi']):
   first=raw(new,'BillFlare'+side+axis,240)if not(side=='Left'and axis=='XLo')else raw(new,'BillFlareLeftXLoPrefix',96)+raw(new,'BillFlareLeftXLoTail',144)
   seq=first+raw(new,'BillFlareExtended'+side+axis,144)
   for k in range(29):seq+=raw(new,'BillFlareLate'+str(k),1024)[(0 if side=='Right'else 512)+j*128:(0 if side=='Right'else 512)+(j+1)*128]
   assert seq==bytes(expected[j]),(mp,side,axis);scalar+=len(seq)
 rows[mp]={'ROM_sha256':sha(new.path),'header_exact':True,'old_RAM_symbols_exact':len(old.ram),'RAM_segments_exact':True,'audio_RO_byte_address_exact':audio,'new_code_and_data_replace_only_FF':tails,'U_RosterDrawShots_exact':True,'old240_scalar_bytes_exact':1920,'all_source_scalar_bytes_exact':scalar,'minimum_iterative_scalar_round_boundary_distance':minimum_round_distance,'CHR_exact_vs_AP_K':new.raw[16+512*1024:]==(H/f'candidate-ap-k/smb-crossover-{mp}.nes').read_bytes()[16+512*1024:]}
 assert rows[mp]['CHR_exact_vs_AP_K']
seven=['bass_metasprites.inc','chr_map_mmc3.inc','chr_map_mmc5.inc','megaman_injury_art.inc','megaman_metasprites.inc','ordinary_body_layout_art.inc','player_outline_flags.inc']
generated={n:{'AP':sha(A/'src'/n),'after_actual_generators':sha(S/'src'/n)}for n in seven};assert all(x['AP']==x['after_actual_generators']for x in generated.values())
report={'status':'PASS','maps':rows,'seven_generated_parent_AP_byte_exact':generated,'scope':'Actual compiled BQ. Original240 and all4096 scalar vectors compared with independent iterative source-angle oracle. Old RAM/header/audio/U renderer and all new FF-only placements; no claim native area-command extent clamps camera.'}
(H.parent/'root49-easy-combined-bq/binary-review-bz.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':'PASS','scalar_bytes_per_mapper':32768,'audio_segments_per_mapper':[len(x['audio_RO_byte_address_exact'])for x in rows.values()],'new_tail_bytes_per_mapper':[sum(x['size']for x in row['new_code_and_data_replace_only_FF'])for row in rows.values()]}))
