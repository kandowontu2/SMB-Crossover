"""Capture the source Sophia landing NSF independently of any route proof."""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];D=R/'build/verification/root49-sophia-land-source-io'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 assert not D.exists();D.mkdir()
 base=R/'reference/crossover2/extracted';mi=base/'scripts/com/smbc/sound/MusicInfo.as';src=mi.read_text()
 m=re.search(r'SFX_SophiaLandSnd:Array = addSfx\(\[\[(\w+),NSF,(\d+),',src);assert m
 name,track=m[1],int(m[2]);assert track==46
 embed=base/('scripts/com/smbc/sound/MusicInfo_'+name+'.as')
 if not embed.exists():
  q=re.search(r'const '+name+r':Class = Games\.(\w+)\.(\w+);',src);assert q
  embed=base/('scripts/com/explodingRabbit/cross/games/Game'+q[1][0].upper()+q[1][1:]+'_'+q[2]+'.as')
 q=re.search(r'source="/_assets/([^"]+)"',embed.read_text());assert q
 asset=base/'binaryData'/q[1];raw=bytearray(asset.read_bytes());assert raw[:5]==b'NESM\x1a'and 1<=track<=raw[6]
 original=raw[7];raw[7]=track;nsf=D/'SophiaLand.nsf';nsf.write_bytes(raw)
 helper=R/'tools/reference/capture_expanded_audio.lua';wrapper=D/'capture-sophia-land-io.lua'
 wrapper.write_text('AUDIO_OUTPUT=[=['+(D/'apu.csv').as_posix()+']=]\nAUDIO_DPCM_OUTPUT=[=['+(D/'dpcm.csv').as_posix()+']=]\nAUDIO_BEGIN=0\nAUDIO_END=180\nAUDIO_NATIVE="nsf"\nAUDIO_FREEZE=false\ndofile([=['+helper.as_posix()+']=])\n')
 record=dict(status='PREPARED_SOURCE_NSF_CAPTURE',script_sha256=sha(__file__),source=dict(MusicInfo=str(mi.relative_to(R)),MusicInfo_sha256=sha(mi),embed=str(embed.relative_to(R)),embed_sha256=sha(embed),asset=str(asset.relative_to(R)),asset_sha256=sha(asset),track=track,original_start_track=original),capture_NSF_sha256=sha(nsf),helper_sha256=sha(helper),wrapper_sha256=sha(wrapper),scope='One exact source MusicInfo NSF track capture; not ROM route evidence. Landing callback integration and native output equivalence still required.',main_changed=False)
 (D/'binding.json').write_text(json.dumps(record,indent=2)+'\n')
 sys.path.insert(0,str(R/'tools'));import run_mesen
 result=run_mesen.run(wrapper,nsf,timeout=45)
 record.update(status='SOURCE_NSF_CAPTURE_COMPLETE'if result==0 else'FAIL_RETAINED',exit=result,files={p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in D.iterdir()if p.is_file()and p.name!='actual.json'})
 (D/'actual.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(dict(status=record['status'],exit=result)))
 raise SystemExit(result)


if __name__=='__main__':main()
