import random
import os

class Card:
    # initialise function of class
    def __init__(self, Ccolour, Ctype):
        self.colourCodes = ["31", "32", "33", "34", "37"]
        self.colour = Ccolour
        self.ctype = Ctype
        self.colourize()
    
    # set the correct colourCode value for the card depending on its colour
    def colourize(self):
        match self.colour:
            case "Red": self.colourCode = self.colourCodes[0]
            case "Green": self.colourCode = self.colourCodes[1]
            case "Yellow": self.colourCode = self.colourCodes[2]
            case "Blue": self.colourCode = self.colourCodes[3]
            case _: self.colourCode = self.colourCodes[4]
        
    # display all the information of the card
    def display(self):
        # make sure the colour code is correct
        self.colourize()
        return "\033[1;" + str(self.colourCode) + "m" + str(self.colour) + " " + str(self.ctype) + "\033[0m"
        
class Player:
    # intitlaise function of class
    def __init__(self, name: str):
        self.hand = []
        self.name = name
        self.score = 0

    # a function to print the hand if the class in a concise 
    # way so that teh format is the same every time
    def printHand(self):
        print("You have:")
        for i in range(len(self.hand)):
            print(" " + self.hand[i].display())
            
    # sort for less then
    def __lt__(self, other):
        return self.score < other.score
    

# a function that initialises the Uno deck
def SetupDeck():
    # initialise varaibles needed
    colours = ["Red", "Green", "Yellow", "Blue"]
    cardTypes = [1, 2, 3, 4, 5, 6, 7, 8, 9, "Reverse", "Skip", "Pickup Two"]
    extraCards = ["Wild", "Wild Plus Four"]
    deck = []

    # create the deck, adding 1 zero of each colour, and 2 of every other type
    for col in range(len(colours)):
        deck.append(Card(colours[col], 0))
        for typ in range(len(cardTypes)):
            for i in range(2):
                deck.append(Card(colours[col], cardTypes[typ]))

    # add to the deck the 4 wild cards of each type
    for i in range(len(extraCards)):
        for j in range(4):
            deck.append(Card("\b", extraCards[i]))

    return deck

# a function that runs the code for the wild cards, so it changes there colour with the user input
def wildCardTypeFunctionality(playingCard: Card):
    # change colour
    newColour = input("What colour would you like to change to? (R/Y/G/B): ").upper()
    # error check input
    while newColour not in {"R","Y","G","B"}:
        print("That is not a correct awnser")
        print("Please try again")
        newColour = input("What colour would you like to change to? (R/Y/G/B): ").upper()
    # match player input to corresponding colour
    match newColour:
        case "R":  playingCard.colour = "Red"
        case "Y":  playingCard.colour = "Yellow"
        case "G":  playingCard.colour = "Green"
        case "B":  playingCard.colour = "Blue"
    playingCard.colourize()
    return playingCard

# a function that sets up the game, so it creates the discard and draw pile and deals hands
def StartRound(deck: list, players: list, handSize: int, direction: int, playerTurn: int):
    # draw pile
    drawPile = []
    # have at least one deck
    drawPile += deck
    # add another deck for every six people
    for i in range(len(players) // 6):
        drawPile += deck
        
    # shuffle the deck
    random.shuffle(drawPile)
    
    # discard Pile
    discardPile = []
    # add the top card of the draw pile to the discard pile
    discardPile.append(drawPile.pop(0))
    
    # have each player draw the amount of card in a hand, effectively dealing the cards
    for i in range(len(players)):
        Draw(players[i], drawPile, discardPile, handSize)
            
    # clear the screen
    print("\033c")
    
    # print who the first player is
    print("The first player is \033[1m" + players[playerTurn].name + "\033[0m")
    
    # check if the card in the discard pile is a card with a special action assinged to it and if so play it 
    print("The first card is a " + discardPile[0].display())
    playerTurn, direction = SpecialPlayCard(players, players[0], discardPile, drawPile, playerTurn, discardPile[0], direction)
    
    return drawPile, discardPile, direction, playerTurn

# function for when the first card is played, where they have slightly different effects
def SpecialPlayCard(players: list, play: Player, DiscardPile: list, DrawPile: list, playerTurn: int, playingCard: Card, direction: int):
    # check for special ability cards
    match playingCard.ctype:
        case "Reverse":
            # else reverse the direction if it is more than two players
            print("The direction of play is reversed")
            direction *= -1
            
        case "Skip":
            # add one to the player turn, skipping this players turn
            print("\033[1m" + players[playerTurn].name + "\'s\033[0m turn was skipped")
            playerTurn = PlayerTurnIncrement(playerTurn, direction, players)
            
        case "Pickup Two":
            # make the first player pickup two cards and skip their turn
            print("\033[1m" + players[playerTurn].name + "\033[0m picks up 2 cards and misses their turn")
            Draw(players[playerTurn], DrawPile, DiscardPile, 2)
            playerTurn = PlayerTurnIncrement(playerTurn, direction, players)
            
        case "Wild":
            # have the card use its specific function from before
            playingCard = wildCardTypeFunctionality(playingCard)
            print("the new colour of play is " + "\033[1;" + str(playingCard.colourCode) + "m" + playingCard.colour + "\033[0m")
                
        case "Wild Plus Four":
            # do the same as the wild card
            
            # change colour
            playingCard = wildCardTypeFunctionality(playingCard)
            print("the new colour of play is " + "\033[1;" + str(playingCard.colourCode) + "m" + playingCard.colour + "\033[0m")
    
    return playerTurn, direction
# increase the value of player turn by one or negative one, also add a range to it, 
# so if it exceeds the amoutn of player that it goes back to the bottom vice versa
def PlayerTurnIncrement(playerTurn, direction, players: list):
    playerTurn += 1 * direction
    if playerTurn >= len(players):
        playerTurn = 0
    if playerTurn < 0:
        playerTurn = len(players) - 1
    return playerTurn

# a function that deals with adding the amount of cards specified 
# to a specified players hand and when the deck runs out it adds all but 
# the top card of the discard pile to the draw pile and then shuffles the draw pile
def Draw(play: Player, DrawPile: list, DiscardPile : list, amount: int = 1):
    # if enough cards to just normally draw, then do that and return
    if len(DrawPile) > amount:
        for i in range(amount):
            play.hand.append(DrawPile.pop(0))
        return
    
    # else shuffle first
    
    # save top card of discard pile but put the rest back in the draw pile
    topCard = DiscardPile.pop(0)
    DrawPile += DiscardPile
    DiscardPile = []
    DiscardPile.append(topCard)
    
    # Shuffle the draw pile and then draw the cards
    random.shuffle(DrawPile)
    Draw(play, DrawPile, DiscardPile, amount)
    
# a function that deals with the playing of cards and their specific abilities
def PlayCard(players: list, play: Player, DiscardPile: list, DrawPile: list, playerTurn: int, playingCard: Card, direction: int):
    # check for special ability of card
    match playingCard.ctype:
        case "Reverse":
            # if it is a two player game, have the player take another turn
            if len(players) == 2: 
                print("You can play your turn again")
                playerTurn -= 1
            else:
                # else reverse the direction if it is more than two players
                print("You reversed the direction of play")
                direction *= -1
            
        case "Skip":
            # add one to the player turn, skipping the next players turn
            playerTurn = PlayerTurnIncrement(playerTurn, direction, players)
            print("You skipped \033[1m" + players[playerTurn].name + "\'s\033[0m turn")
            
        case "Pickup Two":
            # make the next player pickup two cards and skip their turn
            playerTurn = PlayerTurnIncrement(playerTurn, direction, players)
            print("\033[1m" + players[playerTurn].name + "\033[0m picks up 2 cards and misses their turn")
            Draw(players[playerTurn], DrawPile, DiscardPile, 2)
            
        case "Wild":
            # have the card use its specific function from before
            playingCard = wildCardTypeFunctionality(playingCard)
            print("the new colour of play is " + "\033[1;" + str(playingCard.colourCode) + "m" + playingCard.colour + "\033[0m")
                
        case "Wild Plus Four":
            # do the same as the wild card, but also 
            # have the next player draw four cards and skip their turn
            
            # skip players turn
            playerTurn = PlayerTurnIncrement(playerTurn, direction, players)
            print("\033[1m" + players[playerTurn].name + "\033[0m draws four cards and misses their turn")
            # add four to players hand 
            Draw(players[playerTurn], DrawPile, DiscardPile, 4)
            # change colour
            playingCard = wildCardTypeFunctionality(playingCard)
            print("the new colour of play is " + "\033[1;" + str(playingCard.colourCode) + "m" + playingCard.colour + "\033[0m")
    
    # play the card into the discard pile
    DiscardPile.insert(0, playingCard)
    try:
        # remove it from the players hand
        play.hand.remove(playingCard)
    except: False
    
    return playerTurn, direction
    
# each players turn
def Turn(players: list, play: Player, DiscardPile: list, DrawPile: list, playerTurn: int, direction: int):
    print("Press Enter to start \033[1m"  + players[playerTurn].name + "'s\033[0m turn")
    input()

	# display discard pile
    print("Discard Pile: ")
    topCard = DiscardPile[0]
    print(topCard.display())
    
    print("-" * 20) # prints line to seperate sections

	# display hand sizes of other players
    print("Others: ")
    for i in range(len(players)):
        if players[i] != play:
            # print string
            print("\033[1m" + players[i].name + "\033[0m has " + str(len(players[i].hand)) + " card", end="")
            # if multiple cards print an s
            if len(players[i].hand) != 1:   print("s", end = "")
            # add new line at the end
            print()

    print("-" * 20) # prints line to seperate sections

	# display hand
    print("Hand: ")
    play.printHand()

    print("-" * 20) # prints line to seperate sections
    
    # prints out a list of possible action that the player can take of all cards 
    # that can be played and that they can draw a card
    print("Possible Actions: ")
    actions = []
    for j in play.hand:
        if j.colour == topCard.colour or j.ctype == topCard.ctype or j.colour == "\b":
            actions.append(j)
            print(str(len(actions)) + ": You can play your " + j.display())
    print(str(len(actions) + 1) + ": draw a card")
    
    # input players action out of their possible actions, this input is the 
    # number that correspondes to the action list from earlier
    actionNum = input("Please input one of the numbers next to an action to fulfill it: ")
    while True:
        # error checking the player input
        try:
            actionNum = int(actionNum)
            if actionNum < 1 or actionNum > (len(actions) + 1):
                raise IndexError
            break
        
        except ValueError: 
            # didn't input a thing string that can be converted to an int
            print("That isn't a whole number")
            actionNum = input("Please input one of the numbers next to an action to fulfill it: ")
        
        except IndexError: 
            # range error
            print(f"The action numbers go from 1-{len(actions) + 1}, the number {actionNum} is not in this range")
            actionNum = input("Please input one of the numbers next to an action to fulfill it: ")
        
        except: 
            # something unexpected went wrong
            print("Something went wrong")
            actionNum = input("Please input one of the numbers next to an action to fulfill it: ")
    actionNum -= 1
    # if they chose to play a card then play it
    if len(actions) > 0 and actionNum  < len(actions):
        print("You played: " + actions[actionNum].display())
        playerTurn, direction = PlayCard(players, play, DiscardPile, DrawPile, playerTurn, actions[actionNum], direction)
    else:
        # they chose to draw
        print("You have chosen to draw a card")
        Draw(play, DrawPile, DiscardPile)
        print("You drew a " + play.hand[len(play.hand) - 1].display())
        
    # return final values
    return playerTurn, direction

# congragulate the winner and possibly setup the next match
def WIN(players):
    Max = 0
	# check who is the winner by finding the maximum score
    for i in players:
        if i.score > Max:
            Max = i.score
            play = i
    print("Congratulations \033[1m"  + play.name + "\033[0m for winning, with a score of " + str(Max))
    # do they want to play another round
    Another = input("Do you want to play another game? (Y/N): ")
    if Another.lower() == "n" or Another.lower() == "no":
        print("click Enter to escape the program")
        input()
        os._exit(0)
    # if they didn't input 'n', 'N', 'no', 'No', 'nO', or 'NO' then play another game 

# calculate the score for the plaayer who won the round based on what everyone else drew
def CalculateScore(players: list):
    Score = 0
    for i in players:
        for j in i.hand:
            add = 0
            match j.ctype:
                # different values to add for each type of card
                case "Wild Plus Four": add = 50
                case "Wild": add = 50
                case "Reverse": add = 20
                case "Skip": add = 20
                case "Plus Two": add = 20
                # if number card, face value of the card is the value
                case _: add = j.ctype	
            Score += add
    return Score 

# setup the players and their usernames
def setUpPlayers():
    # initialize the player list that stores the players
    playerNum = input("How many players are there: ")

    # error trapping
    while True:
        try:
            # int and range
            playerNum = int(playerNum)
            # range check on player number
            if playerNum <= 1:
                raise ZeroDivisionError
            # confirm if over or equal to 10 people, that that is the number wanted
            if playerNum >= 10:
                print("Due to having greater than or equal to 10 players (", playerNum, "), input the number again for confirmation")
                secondNum = int(input("Confirmation number: "))
                if secondNum != playerNum:
                    raise TabError
            break
        except ValueError: 
            # not int
            print("That isn't a whole number")
           
        except ZeroDivisionError: 
            # wrong range
            print("The number of players should be greater then one")
            
        except TabError:
            # confirmation number was incorrect
            print("The confirmation number wasn't the same so please try the whole proccess again")
        except: 
            # something else
            print("Something went wrong")
        playerNum = input("How many players are there: ")
    
    players = []
    playersUserNames = []
    
    # User name assigner
    for i in range(playerNum):
        print("Please hand to player " + str(i + 1))
        while True:
            # input
            name = input("please input your username: ").strip()
            # error checking
            # not blank
            if name == "":
                print("blank space is not a name")
            # if the name is already chosen
            elif name in playersUserNames: 
                print("Someone else already has this name")
            # else get out of while loop
            else: break
        # add to players and save the user name to check that other don't use the same name later
        players.append(Player(name))
        playersUserNames.append(name)

    
    return players

# the main game loop
def Game(deck, players, DrawPile, DiscardPile, StartHandSize, winningAmount, playerTurn, direction):
    # for each player check if anyone has won
    for play in range(len(players)):
        # check if a player has won the round
        if len(players[play].hand) == 0:
            # calculate score
            calculatedScore = CalculateScore(players)
            players[play].score +=  calculatedScore
            #congraulations
            print("Well Done \033[1m" + players[play].name + "\033[0m for winning the round with a score of " + str(calculatedScore))
            print("For a new overall score of " + str(players[play].score))
            print("That creates a new leader board of:")
            #create leaderboard
            sortedPlayer = sorted(players, reverse = True)
            [print("\033[1m" + i.name + "\033[0m - " + str(i.score)) for i in sortedPlayer]
            
            # check if a player has won the entire game
            if players[play].score >= winningAmount:
                WIN(players)
                players = setUpPlayers()
                direction = 1
                DrawPile, DiscardPile, direction, playerTurn = StartRound(deck, players, StartHandSize, direction, playerTurn)
                Game(deck, players, DrawPile, DiscardPile, StartHandSize, winningAmount, playerTurn, direction)
                return
            
            Another = input("Would you like to play another round? (Y/N): ")
            # reset game for next round
            if Another.upper() == "Y":
                # start next round and initialize variables
                playerTurn = random.randrange(0, len(players) - 1)
                direction = 1
                drawPile, discardPile, direction, playerTurn = StartRound(deck, players, StartHandSize, direction, playerTurn)
                playerTurn = PlayerTurnIncrement(playerTurn, direction, players)
            # if player doesnt want to play again than calculate winner
            else:
                WIN(players)
                players = setUpPlayers()
                direction = 1
                DrawPile, DiscardPile, direction, playerTurn = StartRound(deck, players, StartHandSize, direction, playerTurn)

    playerTurn, direction = Turn(players, players[playerTurn], DiscardPile, DrawPile, playerTurn, direction)

    # check if the player needs to say 'UNO', and if the are incorrect have them draw two cards
    IsUno = input("Press Enter to end your turn or say UNO if necessary: ")
    if IsUno.lower() == "uno" and len(players[playerTurn].hand) != 1:
        print("you said Uno at an incorrect time, draw two cards")
        Draw(players[playerTurn], DrawPile, DiscardPile, 2)
    elif len(players[playerTurn].hand) == 1 and IsUno.lower() != "uno":
        print("You didn\'t say Uno, draw two cards")
        Draw(players[playerTurn], DrawPile, DiscardPile, 2)
        
    # go to the next players turn
    print("\033c") # clear screen between turns
    # dipslay if the last person said 'UNO'
    if IsUno.lower() == "uno":
        print("\033[1m" + players[playerTurn].name  + "\033[0m said UNO")
    playerTurn = PlayerTurnIncrement(playerTurn, direction, players)
    # repeat game loop
    Game(deck, players, DrawPile, DiscardPile, StartHandSize, winningAmount, playerTurn, direction)

# main module, I would suggest reading this first and every time a module is called 
# go up to look at what the module does so that it is more understandable on why the function 
# is there when reading it the first time
def MAIN():
    # set up players
    players = setUpPlayers()
    # initialize other variables
    startHandSize = 7
    direction = 1
    winningAmount = 500
    playerTurn = 0
    
    # call setup functions
    deck = SetupDeck()
    drawPile, discardPile, direction, playerTurn = StartRound(deck, players, startHandSize, direction, playerTurn)
    
	# start the game loop
    Game(deck, players, drawPile, discardPile, startHandSize, winningAmount, playerTurn, direction)

# display the title page
def titlePage():
    print("UUUUUUUU     UUUUUUUU  NNNNNNNN        NNNNNNNN       OOOOOOOOO     ")
    print("U::::::U     U::::::U  N:::::::N       N::::::N     OO:::::::::OO   ")
    print("U::::::U     U::::::U  N::::::::N      N::::::N   OO:::::::::::::OO ")
    print("UU:::::U     U:::::UU  N:::::::::N     N::::::N  O:::::::OOO:::::::O")
    print(" U:::::U     U:::::U   N::::::::::N    N::::::N  O::::::O   O::::::O")
    print(" U:::::D     D:::::U   N:::::::::::N   N::::::N  O:::::O     O:::::O")
    print(" U:::::D     D:::::U   N:::::::N::::N  N::::::N  O:::::O     O:::::O")
    print(" U:::::D     D:::::U   N::::::N N::::N N::::::N  O:::::O     O:::::O")
    print(" U:::::D     D:::::U   N::::::N  N::::N:::::::N  O:::::O     O:::::O")
    print(" U:::::D     D:::::U   N::::::N   N:::::::::::N  O:::::O     O:::::O")
    print(" U:::::D     D:::::U   N::::::N    N::::::::::N  O:::::O     O:::::O")
    print(" U::::::U   U::::::U   N::::::N     N:::::::::N  O::::::O   O::::::O")
    print(" U:::::::UUU:::::::U   N::::::N      N::::::::N  O:::::::OOO:::::::O")
    print("  UU:::::::::::::UU    N::::::N       N:::::::N   OO:::::::::::::OO ")
    print("    UU:::::::::UU      N::::::N        N::::::N     OO:::::::::OO   ")
    print("      UUUUUUUUU        NNNNNNNN         NNNNNNN       OOOOOOOOO")
    print("\n\n\n")

# if this is not an imported module than run the game immediately
if __name__ == "__main__":
    # set title of cmd to be UNO
    os.system("title " + "UNO")
    # turn on colour in teh command prompt if it is disabled
    os.system('')
    # title page display
    titlePage()
    # menu text
    print("-" * 20)
    print("This is the card game Uno constructed in python")
    print("If at anytime you are lost on how to play please look at the documentation provided")
    print("in the documentation word document, right underneath the testing tables")
    print("(If you want to quit at any time simply press \'ctr + c\')")
    print("-" * 20)
    # start
    MAIN()