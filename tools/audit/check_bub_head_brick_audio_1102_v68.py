"""Source-bound shatter noise clock extension to the retained67 negative.

Only the genuine async native Noise_SfxLenCounter is additionally compared
as a tracked audio output. Nested IRQ must preserve it literally.
"""
import argparse,inspect,json
from pathlib import Path
import check_bub_head_brick_nested_1102_v67 as V
from check_tmnt_render_oa import location
H,N,O,R,sha=V.H,V.N,V.O,V.R,V.sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['gather','replay'],required=True)
    parser.add_argument('--form',choices=['small','powered']);args=parser.parse_args()
    negative=O/'head-projection-v67-brick-noise-negative.json'
    if not negative.exists():
        prior=O/'head-projection-v57-unexpected-state.json';x=json.loads(prior.read_text())
        assert x['native_differences']==[dict(address=0x7dc,old=0,new=31)]
        negative.write_bytes(prior.read_bytes())
    original_text,original_env=H.text,H.env
    original_state,original_audio,original_seed=H.state,H.audio,V.B.seed
    original_bindings=V.bindings
    def state(m):
        result=list(original_state(m));native=bytearray(result[4]);native[0x7dc-0x200]=0
        result[4]=bytes(native);return tuple(result)
    def audio(m):return(*original_audio(m),m[0x7dc])
    def sites(b):
        result=H.P.audio_sites(b)
        assert H.address(b,'Noise_SfxLenCounter')==0x7dc
        for prefix in['GuestSharedSfx::','SoundEngine::']:
            for suffix,delta,code in [('PlayBrickShatter',2,'8ddc07'),('DecrementSfx3Length',0,'cedc07')]:
                name=prefix+suffix;pc=H.address(b,name)+delta;at=location(b,name)+delta
                assert b['raw'][at:at+3]==bytes.fromhex(code),(name,delta)
                result[(((at-16)//8192)|128,pc)]=(name,delta,code)
        return result
    def seed(*a):
        H.state,H.audio=original_state,original_audio
        try:return original_seed(*a)
        finally:H.state,H.audio=state,audio
    def bindings():
        return {**original_bindings(),**{str(f.relative_to(R)):sha(f)for f in[Path(__file__),negative,R/'src/music_drivers/vanilla_sfx.s']}}
    text=original_text
    replacements={
        "['8dd807','ced807','8dda07','8ddb07','eedb07']":"['8dd807','ced807','8dda07','8ddb07','eedb07','8ddc07','cedc07']",
        'audio_before==(0,0,0)and':'audio_before==(0,0,0,0)and',
        "audio_after[2]in[0,1],('Unexpected actual first bump/grow audio clock transition'":"audio_after[2]in[0,1]and audio_after[3]in[0,31],('Unexpected actual first bump/grow/shatter audio clock transition'",
        "O/'head-projection-v57-unexpected-state.json'":"O/'head-projection-v68-unexpected-state.json'",
    }
    for before,after in replacements.items():assert text.count(before)==1,before;text=text.replace(before,after)
    H.text=text;H.env=dict(original_env,state=state,audio=audio,audio_sites=sites)
    H.state,H.audio=state,audio;V.B.seed=seed;V.bindings=bindings
    try:
        # Keep the failed67 source/receipt immutable; the only output-path
        # change is the distinct68 successor name. Real run/assertions are
        # the same except exact bound fourth native sound clock ownership.
        fn=V.gather if args.phase=='gather'else V.replay
        source=inspect.getsource(fn).replace('head-projection-v67-','head-projection-v68-')
        env=dict(V.__dict__);exec(compile(source,str(Path(__file__)),'exec'),env)
        env[fn.__name__]()if args.phase=='gather'else env[fn.__name__](args.form=='powered')
    finally:
        H.text,H.env=original_text,original_env;H.state,H.audio=original_state,original_audio
        V.B.seed=original_seed;V.bindings=original_bindings


if __name__=='__main__':main()
