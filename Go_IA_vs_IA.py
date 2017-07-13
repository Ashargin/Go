N=2 ###initialisation###
n_parties=100000
joueur1='v1_comp' #à choisir parmi ('alea','v1','v1_comp','v1_train','v2','v2_comp','v2_train')
joueur2='v1_comp'
n_sim=50
n_sim_min=5000
alea=0
from Go_settings import*
joueur=1
c=0
if joueur1 in ('v1','v1_comp','v1_train') :
    version1='v1'
else :
    version1='v2'
if joueur2 in ('v1','v1_comp','v1_train') :
    version2='v1'
else :
    version2='v2'
D1=marshal.load(open('train_'+version1+'_'+str(N),'rb'))
D_comp1=marshal.load(open('train_'+version1+'_'+str(N)+'_comp','rb'))
if joueur1=='v1_train' :
    D_prev1={}
elif joueur1=='v2_train' :
    D_prev1=marshal.load(open('train_v1_'+str(N),'rb'))
D2=marshal.load(open('train_'+version2+'_'+str(N),'rb'))
D_comp2=marshal.load(open('train_'+version2+'_'+str(N)+'_comp','rb'))
if joueur2=='v1_train' :
    D_prev2={}
elif joueur2=='v2_train' :
    D_prev2=marshal.load(open('train_v1_'+str(N),'rb'))
def coup(player,n_joueur) :
    if player=='alea':
        if n_joueur==1 :
            return(lambda *args: coup_IA_alea(var,joueur)) #et ça dépend aussi de joueur
        elif n_joueur==2 :
            return(lambda *args: coup_IA_alea(var,3-joueur))
    elif  player in ('v1','v2') :
        if n_joueur==1 :
            return(lambda *args: coup_IA(var,joueur,D1))
        elif n_joueur==2 :
            return(lambda *args: coup_IA(var,3-joueur,D2))
    elif player in ('v1_comp','v2_comp') :
        if n_joueur==1 :
            return(lambda *args: coup_IA_comp(var,joueur,D1,D_comp1))
        elif n_joueur==2 :
            return(lambda *args: coup_IA_comp(var,3-joueur,D2,D_comp2))
    elif player=='train' :
        if n_joueur==1 :
            return(lambda *args: coup_IA_train(version1,var,joueur,n_sim,n_sim_min,D1,D_prev1,alea))
        elif n_joueur==2 :
            return(lambda *args: coup_IA_train(version2,var,3-joueur,n_sim,n_sim_min,D2,D_prev2,alea))
fonction1=coup(joueur1,1)
fonction2=coup(joueur2,2)
for i in range(n_parties) :
    var=settings(N)
    if joueur==1:
      def player_begin():
          fonction1()
      def other_player():
          fonction2()
    elif joueur==2:
        def player_begin():
            fonction2()
        def other_player():
            fonction1()
    while var.Cases!=[] :
        player_begin()
        if len(var.Cases)>=1 :
            other_player()      
    Area=area(var.P) ###comptage des fois et gagnant###
    Score=[Area[0],Area[1]+var.Komi[var.N]]
    if Score[0]>Score[1] and joueur==1 or Score[1]>Score[0] and joueur==2 :
        c=c+1
    joueur=3-joueur #pour alterner le joueur qui joue en premier
print('Joueur 1 gagne '+str(c)+' parties sur '+str(n_parties)+' ('+str(100*c/n_parties)+'%).')

#tests : en x3 :
#alea vs alea : 1060 parties par seconde
#v1 vs v1 : 15.43 parties par seconde (sans load)
#v1_comp vs v1_comp : 379 parties par seconde (sans load)
#v1_train vs v1_train : 0.12 parties par seconde
#Actuellement : v1 vs alea : 94,4% de victoire en 2x2, 98% en 3x3
