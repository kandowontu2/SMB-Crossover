from pathlib import Path
import sys,re,json,hashlib,concurrent.futures,argparse
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'));import run_mesen
base=ROOT/'reference/crossover2/extracted';src=(base/'scripts/com/smbc/sound/MusicInfo.as').read_text();out=ROOT/'build/reference-remaining-sfx';out.mkdir(exist_ok=True)
names=['LinkShootArrow','LinkSetBomb','LinkBombExplode','SimonThrowDagger','SimonCross','SimonHolyWaterExplode','SimonStopWatch','RyuArtOfFireWheel','RyuFireDrgonBall','RyuJumpSlash','RyuThrowSmallStar','RyuThrowBigStar','SamusShootMissile','SamusScrewAttack','SophiaMissile','BillLaser','BillFlare','SophiaBulletExplode','SophiaHitEnemy','SophiaKillEnemy','LinkTakeDamage','SimonTakeDamage','RyuTakeDamage','RyuJump']
parser=argparse.ArgumentParser(description='Capture pinned Crossover 2.02 NSF effects; existing IDs stay in order.')
parser.add_argument('--effects',nargs='+',choices=names,help='Capture only these effects; preserve other existing CSV captures.')
args=parser.parse_args()
plan={}
for name in names:
 m=re.search('SFX_'+name+r'Snd:Array = addSfx\(\[\[(\w+),NSF,(\d+),',src);assert m,name
 ep=base/('scripts/com/smbc/sound/MusicInfo_'+m[1]+'.as')
 if not ep.exists():
  g=re.search(r'const '+m[1]+r':Class = Games\.(\w+)\.(\w+);',src);ep=base/('scripts/com/explodingRabbit/cross/games/Game'+g[1][0].upper()+g[1][1:]+'_'+g[2]+'.as')
 embed=ep.read_text();asset=re.search(r'source="/_assets/([^"]+)"',embed)[1];source=base/'binaryData'/asset
 plan[name]={'source':source.relative_to(ROOT).as_posix(),'track':int(m[2]),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
def run(name):
 item=plan[name];data=bytearray((ROOT/item['source']).read_bytes());data[7]=item['track'];nsf=out/(name+'.nsf');nsf.write_bytes(data);script=out/(name+'.lua');script.write_text(f'AUDIO_OUTPUT=[=[{(out/(name+".csv")).as_posix()}]=]\nAUDIO_DPCM_OUTPUT=[=[{(out/(name+"-dpcm.csv")).as_posix()}]=]\nAUDIO_BEGIN=0\nAUDIO_END=180\nAUDIO_NATIVE="nsf"\nAUDIO_FREEZE=false\ndofile([=[{(ROOT/"tools/reference/capture_expanded_audio.lua").as_posix()}]=])\n');return name,run_mesen.run(script,nsf,timeout=30)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for n,r in pool.map(run,args.effects or names):assert r==0,n
(out/'source.json').write_text(json.dumps(plan,indent=2)+'\n')
