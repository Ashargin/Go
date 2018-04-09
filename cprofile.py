import cProfile
from Go_settings import*
def test() :
    import Go_IA_vs_IA
cProfile.run('test()',sort='tottime')