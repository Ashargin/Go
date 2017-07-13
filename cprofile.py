import cProfile
from Go_settings import*
cProfile.run('train()',sort='tottime')
