import math
import random
import pygame


width=800
height=600
numPlatforms=40
sizeFrame=5
slowMo=0.004

colorBG=(0,0,0)
colorPlat1=(40,200,100)
colorPlat2=(120,250,180)
colorBut=(250,30,30)
colorBode=(255,255,255)


def dessineNouvellePlateforme(win,cestLeBut):
    if cestLeBut:
        couleur = colorBut
    else:
        couleur = (
            random.randint ( colorPlat1[0], colorPlat2[0] ),
            random.randint ( colorPlat1[1], colorPlat2[1] ),
            random.randint ( colorPlat1[2], colorPlat2[2] )
        )
    larg = random.randint ( width//20, width//6 )
    x1 = random.randint ( sizeFrame, width-sizeFrame-larg )
    x2 = x1+larg
    y = random.randint ( sizeFrame+height//20, height-sizeFrame-height//15-larg//5 )
    while (x1 < x2):
        pygame.draw.line ( win, couleur, (x1,y), (x2,y) )
        x1 = x1 + random.randint(0,3)
        x2 = x2 - random.randint(0,3)
        y=y+1


def dessinePlatformes(win):
    for n in range(numPlatforms):
        dessineNouvellePlateforme ( win, n==(numPlatforms-1) ) # le tout dernier sera le But


def dessineFrame(win):
    pygame.draw.rect ( win, colorPlat1, ((0,0),(sizeFrame,height)) )
    pygame.draw.rect ( win, colorPlat1, ((width-sizeFrame,0),(sizeFrame,height)) )
    pygame.draw.rect ( win, colorPlat1, ((0,0),(width,sizeFrame)) )
    pygame.draw.rect ( win, colorPlat1, ((0,height-sizeFrame),(width,sizeFrame)) )


def getCollisions(win,x,y):
    coll=[[0,0,0],[0,0,0],[0,0,0]]
    numCollisions=0
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            couleurPixel = win.get_at((x+dx,y+dy))
            if (not (couleurPixel==colorBG)):
                numCollisions = numCollisions+1
                coll[dx+1][dy+1]=1
                if (couleurPixel==colorBut):
                    coll[dx+1][dy+1]=2
    return ( numCollisions, coll )

                
def bodeAvance ( win, bode, vitesse ):
    # efface l'ancienne position
    pygame.draw.rect ( win, colorBG, ((int(bode[0])-1,int(bode[1])-1),(3,3)) )

    bode[0] = bode[0]+vitesse[0]*slowMo;
    bode[1] = bode[1]-vitesse[1]*slowMo; # moins vitesse, au lieu de plus, parce que les ordonnees montent vers en bas

    collisions = getCollisions ( win, int(bode[0]), int(bode[1]) )

    if (collisions[0] > 0):
        # revient `a la position de depart
        bode[0] = bode[0]+vitesse[0]*slowMo*-1;
        bode[1] = bode[1]-vitesse[1]*slowMo*-1;
    
    pygame.draw.rect ( win, colorBode, ((int(bode[0])-1,int(bode[1])-1),(3,3)) )    

    return collisions


def touteLaColonne(coll,x):
    return (coll[x][0] > 0) and (coll[x][1] > 0) and (coll[x][2] > 0)


def touteLaLigne(coll,y):
    return (coll[0][y] > 0) and (coll[1][y] > 0) and (coll[2][y] > 0)


def unDeLaLigne(coll,y,min=1):
    return (coll[0][y] >= min) or (coll[1][y] >= min) or (coll[2][y] >= min)


def bodeJump ( win, bode, vitesse ):
    clock = pygame.time.Clock()
    finJeu=False
    finJump=False

    while (not finJump):
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: 
                finJeu=True
                finJump=True

        vitesse[1] = vitesse[1]-8.5*slowMo # gravite
        collisions = bodeAvance ( win, bode, vitesse )

        if (collisions[0] > 0):
            vitesseTotale = math.sqrt ( vitesse[0]*vitesse[0] + vitesse[1]*vitesse[1] )
            if (
                touteLaColonne ( collisions[1], 0 )
                or
                touteLaColonne ( collisions[1], 2 )
            ):
                # rebond dans un mur lateral
                vitesse[0]=-vitesse[0]

            elif (touteLaLigne ( collisions[1], 0 )):
                # rebond dans le plafond
                vitesse[1]=-vitesse[1]

            elif (collisions[1][0][0] > 0):
                # coin haut a gauche
                vitesse[0] = abs(vitesse[0])*0.4
                vitesse[1] = 0

            elif (collisions[1][2][0] > 0):
                # coin haut a droite
                vitesse[0] = -abs(vitesse[0])*0.4
                vitesse[1] = 0

            elif (unDeLaLigne ( collisions[1], 2 )):
                # par terre
                if (vitesseTotale < 12):
                    # il s'arrete
                    finJump = True
                    finJeu = (unDeLaLigne ( collisions[1], 2, 2 ))
                else:
                    # rebond par terre
                    vitesse[0] = vitesse[0]*0.7;
                    vitesse[1] = -vitesse[1]*0.7;

            else:
                # autre collision...
                if (vitesseTotale < 1):
                    finJump=True
                else:
                    vitesse[0] = 0
                    vitesse[1] = 0

        pygame.display.flip()
        clock.tick(500//slowMo)

    return finJeu


def choisirPositionInitiale(win):
    cherche=True
    while (cherche):
        p = [ 
            random.randint(sizeFrame+10,width-sizeFrame-10), 
            random.randint(height-height//4,height-height//10) 
        ]
        collisions = getCollisions ( win, int(p[0]), int(p[1]) )
        cherche = (collisions[0] > 0)
    return p


def main():
    pygame.init()
    win=pygame.display.set_mode((width,height))

    dessineFrame(win)
    dessinePlatformes(win)
    pygame.display.flip()

    finJeu=False

    bode = choisirPositionInitiale(win)
    finJeu = bodeJump ( win, bode, [5,0] ) # laisse tomber
    numTirs = 0

    while (not finJeu):
        numTirs = numTirs+1
        angle = float ( input ( "Tir #"+str(numTirs)+" - Angle : " ) )
        linearSpeed = float ( input ( "Vitesse : " ) )
        linearSpeed = ((linearSpeed / 100) ** 0.5) * 100 # ajuste quadratico para vitesse 50 subir metade da vitesse 100

        if (linearSpeed > 200):
            linearSpeed = 200
        
        finJeu = bodeJump (
            win,
            bode,
            [
                math.cos(math.radians(angle))*linearSpeed,
                math.sin(math.radians(angle))*linearSpeed
            ]
        )

    print ( 'THE END !!!' )
    input ( "Appuyez sur Enter..." )

    pygame.quit()


main()
