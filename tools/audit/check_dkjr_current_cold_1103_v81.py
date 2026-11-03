"""Account for the sixteen intentional final header publications in80."""
import inspect
import json
from pathlib import Path
import check_dkjr_current_cold_1103_v80 as P


def main():
    text=inspect.getsource(P.main)
    old="            assert bytes(m.ram[3])==payload[:8192]"
    new="""            expected=bytearray(payload[:8192])
            expected[0x1fe0:0x1ff0]=bytes.fromhex(manifest['cookie'])
            assert bytes(m.ram[3])==bytes(expected)"""
    assert text.count(old)==1;text=text.replace(old,new)
    text=text.replace('native-current-cold-v80-CPU.json','native-current-cold-v81-CPU.json')
    text=text.replace('actual_DK_all8192_code_and2048_metadata_exact=True',
        'actual_DK_all8192_code_except16_committed_header_bytes_and2048_metadata_exact=True')
    text=text.replace("Path(__file__),Path(P.__file__)","Path(__file__),V80_PATH,Path(P.__file__)")
    env=dict(P.__dict__,__file__=__file__,V80_PATH=Path(P.__file__))
    exec(compile(text,__file__,'exec'),env);env['main']()


if __name__=='__main__':
    try:main()
    except Exception as error:
        (P.O/'native-current-cold-v81-negative.json').write_text(json.dumps(dict(passed=False,exception=repr(error),ROM_written=False,native_owner_admitted=False),indent=2)+'\n');raise
