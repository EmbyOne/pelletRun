import pygame as pg, time, random
pg.init()

width = 1000
height = 800
screen = pg.display.set_mode([width, height])
pg.display.set_caption("Pellet Run!")

#images for player & pellets
#sanImg = pg.image.load("sanic.png")
#sanImg = pg.transform.scale(sanImg, (200, 150))
sanImg = pg.image.load("heart.png")
sanImg = pg.transform.scale(sanImg, (50, 50))

pelletImg = pg.image.load('opo.png')
pelletImg = pg.transform.scale(pelletImg, (10, 10))


pg.mixer.init()# for toons
toonsList = ['ness.mp3', 'btp.ogg', 'gmr.mp3', 'wng.mp3',]
track = 0
hitSound = pg.mixer.Sound("hit.wav")


pg.font.init()# for text
sans = pg.font.Font('ComicSansMS3.ttf', 54)


clock = pg.time.Clock()


class Sanic(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = sanImg
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()

        self.x = 500
        self.y = 200

        self.rect.left = self.x
        self.rect.right = self.x + 50

        self.rect.top = self.y
        self.rect.bottom = self.y + 50

        self.step = 1
        
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
        
    def move(self, deltatime):
        keys = pg.key.get_pressed()
        
        if keys[pg.K_UP] | keys[pg.K_w] and self.y > 0:
            self.y -= self.step * deltatime
        if keys[pg.K_DOWN] | keys[pg.K_s] and self.y < height- 52:
            self.y += self.step * deltatime
        if keys[pg.K_LEFT] | keys[pg.K_a] and self.x > 0:
            self.x -= self.step * deltatime
        if keys[pg.K_RIGHT] | keys[pg.K_d] and self.x < width - 52:
            self.x += self.step * deltatime

        self.rect.update(self.x, self.y, 50, 50)

class Pellet(pg.sprite.Sprite):
    def __init__(self, targetCords):
        super().__init__()
        self.image = pelletImg
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        
        self.speed = 0.5

        #makes the pellet spawn on the edge of the screen
        if random.choice([0, 1]) == 0:
            self.x = random.choice([-1, width+1])
            self.y = random.randint(0, height+1)
        else:
            self.x = random.randint(0, width+1)
            self.y = random.choice([-1, height+1])


        #Find direction vector between enemy and player.
        vec = pg.math.Vector2(targetCords[0] - self.x, targetCords[1] - self.y)
        pg.math.Vector2.scale_to_length(vec, 2500)

        self.targetVec = vec


    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
        

    def move(self, deltatime):
        #normalize the vector for incremental movement
        vec = pg.math.Vector2.normalize(self.targetVec)

        #Move along this normalized vector
        self.x += vec[0] * self.speed * deltatime
        self.y += vec[1] * self.speed * deltatime

        self.rect.update(self.x, self.y, 10, 10)

highScore = 0


#### STARTING MENU ####
#toons
pg.mixer.music.load('ness.mp3')
pg.mixer.music.play(-1)
jam = True

screen.fill([0, 0, 0])
over = sans.render('Pellet Run !', True, [0,225,225])
play = sans.render('PLAY', True, [225,225,225])
screen.blit(over, over.get_rect(center=(width/2, 300)))
screen.blit(sanImg, sanImg.get_rect(center=(width/2, 400)))
playRect = play.get_rect(center=(width/2, 500))
screen.blit(play, playRect)
pg.display.flip()

e = False
while True:
    for i in pg.event.get():
        if i.type == pg.QUIT:
            pg.quit()
        if i.type == pg.KEYDOWN:
            if i.key == pg.K_m:
                if jam == True:
                    pg.mixer.music.pause()
                else:
                    pg.mixer.music.unpause()
                jam = not jam
            if i.key == pg.K_p:
                track += 1
                if track >= len(toonsList):
                    track = 0 
                pg.mixer.music.load(toonsList[track])
                pg.mixer.music.play(-1)
            if i.key == pg.K_SPACE: e = True; break
        if i.type == pg.MOUSEBUTTONDOWN and i.button == 1:
            if playRect.collidepoint(i.pos): e = True; break
    if e: break
#### STARTING MENU ####

track = 1
while True:
    end = False
    sanic = Sanic()

    #toons
    if jam == True:
        pg.mixer.music.load(toonsList[track])
        pg.mixer.music.play(-1)


    #pellet stuff?
    pelletCount = 0
    pellets = pg.sprite.Group()


    #score logic
    multiplier = score = oldTime = 0
    startTime = int(time.time())

    haram = []
    while True:
        #time stuff
        deltatime = clock.tick(60)

        #key stuff 
        for i in pg.event.get():
            if i.type == pg.QUIT:
                pg.quit()
            if i.type == pg.KEYDOWN:
                if i.key == pg.K_m:
                    if jam == True:
                        pg.mixer.music.pause()
                    else:
                        pg.mixer.music.unpause()
                    jam = not jam
                if i.key == pg.K_p:
                    track += 1
                    if track >= len(toonsList):
                        track = 0 
                    pg.mixer.music.load(toonsList[track])
                    pg.mixer.music.play(-1)

        #multiplier stuff & add new pellets
        timePlayed = int((time.time() - startTime))
        #print(timePlayed)

        #this spawns a new pellet every 3 seconds
        if timePlayed % 3 == 0 and timePlayed not in haram:
            multiplier += 1
            pelletCount += 1
            globals()[f'pelletNr{pelletCount}'] = Pellet(sanic.rect.center)
            pellets.add(globals()[f'pelletNr{pelletCount}'])
            haram.append(timePlayed)

        #score
        if timePlayed - oldTime >= 1:
            score += 1 * multiplier
            oldTime = timePlayed


        #move and draw entities
        screen.fill([0, 0, 0])
        #write le score
        scour = sans.render('Score: ' + str(score), True, [225,225,225])
        screen.blit(scour, (25, 15))
        sanic.move(deltatime)
        sanic.draw(screen)


        for index, pellet in enumerate(pellets):
            #this recreates the pellet if it gets out of bounds
            if pellet.x < -1 or pellet.x > width+1 or pellet.y < -1 or pellet.y > height+1:
                pelletName = pellets.sprites()[index]
                pellets.remove(pelletName)
                globals()[f'{pelletName}'] = Pellet(sanic.rect.center)
                pellets.add(globals()[f'{pelletName}'])

            pellet.move(deltatime)
            pellet.draw(screen)

            #Collision shite & new game
            if pg.sprite.collide_mask(pellet, sanic):
                hitSound.play()
                #change high score
                if score > highScore: highScore = score
                #text for endscreen
                screen.fill([0, 0, 0])
                over = sans.render('GAME OVER!', True, [225,0,0])
                scour = sans.render('Score: {} High Score: {}'.format(score, highScore), True, [225,225,225])
                tryagain = sans.render('Try Again ', True, [225,225,225])
                screen.blit(over, over.get_rect(center=(width/2, 300)))
                screen.blit(scour, scour.get_rect(center=(width/2, 400)))
                tryRect = tryagain.get_rect(center=(width/2, 500))
                screen.blit(tryagain, tryRect)
                pg.display.flip()
                
                #more key stuff cause i'm lazy
                e = False
                while True:
                    for i in pg.event.get():
                        if i.type == pg.QUIT:
                            pg.quit()
                        if i.type == pg.KEYDOWN:
                            if i.key == pg.K_m:
                                if jam == True:
                                    pg.mixer.music.pause()
                                else:
                                    pg.mixer.music.unpause()
                                jam = not jam
                            if i.key == pg.K_p:
                                track += 1
                                if track >= len(toonsList):
                                    track = 0 
                                pg.mixer.music.load(toonsList[track])
                                pg.mixer.music.play(-1)
                            if i.key == pg.K_SPACE: e = True; break
                        if i.type == pg.MOUSEBUTTONDOWN and i.button == 1:
                            if tryRect.collidepoint(i.pos): e = True; break
                    if e: break
                #end of endscreen xd
                end = True; break
        if end == True: break    
        #draw stuff
        pg.display.flip()
