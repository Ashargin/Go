N=3
import cProfile
from Go_settings import*
def f() :
    import Go_IA_vs_IA
D=marshal.load(open('train_v1_'+str(N),'rb'))
cProfile.run('train()',sort='tottime')
