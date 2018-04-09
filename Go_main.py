from Go_settings import* ###initialisation###
print('Taille du goban?')
N=int(input())
var=settings(N)
print(' ')
print('Noir ou Blanc?') #se quel côté le joueur humain joue-t-il?
humain=input()
while humain not in ('Noir','noir','Noirs','noirs','Blanc','blanc','Blancs','blancs') :
    print('Joueur non reconnu.')
    humain=input()
if humain in ('Noir','noir','Noirs','noirs') :
    humain=1
elif humain in ('Blanc','blanc','Blancs','blancs') :
    humain=2
IA=3-humain
print(' ')
print('Handicap?') #si on veut ajouter un handicap
handicap=int(input())
c_handicap=0
D=marshal.load(open('learned_dicts\train_v1_'+str(var.N),'rb')) #on récupère les tests qu'on a déja faits
D_comp=marshal.load(open('learned_dicts\train_v1_'+str(var.N)+'_comp','rb'))
while var.Cases!=[] and c_handicap<handicap-1 : ###phase d'handicap###
    if humain==1 :
        print(' ')
        coup_humain(var,humain)
    else :
        coup_IA=coup_IA_comp(var,IA,D,D_comp)
        print(' ')
        print('IA : '+str(coup_IA))
        show_goban(var.P)
    c_handicap=c_handicap+1
while var.Cases!=[] : ###déroulement de la partie###
    if humain==1 : #si le joueur humain joue Noir
        print(' ')
        coup_humain(var,1) #coup du joueur
        if len(var.Cases)>=1 : #s'il reste une case vide pour l'IA
            coup_IA=coup_IA_comp(var,2,D,D_comp) #coup de l'IA
            print('IA : '+str(coup_IA))
            show_goban(var.P)
    else : #si le joueur humain joue Blanc
        coup_IA=coup_IA_comp(var,1,D,D_comp) #coup de l'IA
        print(' ')
        print('IA : '+str(coup_IA))
        show_goban(var.P)
        if len(var.Cases)>=1 : #s'il reste une case vide sur le joueur
            coup_humain(var,2) #coup du joueur
Area=area(var.P) ###comptage des fois et gagnant###
print(' ')
print('Area : '+str(Area[0])+' - '+str(Area[1]))
print('Komi : '+str(var.Komi[var.N]))
Score=[Area[0],Area[1]+var.Komi[var.N]]
print('Score final : '+str(Score[0])+' - '+str(Score[1]))
if Score[0]>Score[1] :
    print('Noir gagne')
elif Score[0]<Score[1] :
    print('Blanc gagne')
else :
    print('Egalité') #en pratique ce cas n'arrive pas à cause du komi qui n'est volontairement pas entier