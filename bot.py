import discord
#import youtube_dl
#import nacl
import math
import datetime
import sqlite3
import random
import time
from sqlite3 import Error

TOKEN = ''

client = discord.Client()

conn = sqlite3.connect("currency.db")
cursor = conn.cursor()

'''
Class Troop lists all the troops currently available in the shop for purchase along with each troop's properties.

Type = Offensive or Defensive Troop
Name = Name of the Troop
Dmg = The amount of damage the troop does per second
Cost = How much the troop costs
Desc = Description of the Troop
curr = Currency needed to buy the troop (Bits or Iron)
'''

class Troop():
    def __init__(self, type, name, dmg, cost, desc, curr):
        self._type = type
        self._name = name
        self._dmg = dmg
        self._cost = cost
        self._desc = desc
        self._curr = curr

troops = [Troop("offensive", "Soldier", "1", "1000", "Infantry unit. Good for attacking in numbers.", "bits"), Troop("offensive", "Knight", "11", "10000", "Knights, as noble as they are, won't stop for anything to complete their objective.", "bits"), Troop("offensive", "Wizard", "125", "50", "Wizards shoot spells that can injure hundreds of enemies at a time.", "iron"), Troop ("offensive", "Commander", "1500", "500", "Commanders have an entire arsenal of Weapons of Mass Destruction and are not afraid to use them.","iron"), Troop("defensive", "Archer", "1", "1000", "Infantry unit. Good for defending in numbers.", "bits"), Troop("defensive", "Bishop", "11", "10000", "Bishops defend with their magical staffs.", "bits"), Troop("defensive", "Rook", "125", "50", "Rooks are beastly humans. It is said with their muscles they can stop hundreds of units.","iron"), Troop ("defensive", "Enforcer", "1500", "500","Enforcers can stop thousands of units with a clap of their hands, causing earth shattering earthquakes.", "iron")]

'''
Infiltration Method:

Used when a player infiltrates another person's base. Determines if the player is able to infiltrate the base or not depending 
on the player's offensive damage, the opponent's defensive damage, and the health of the opponent's wall.

wall = Opponent's Wall Health
odmg = Player's Offensive Damage
ddmg = Opponent's Defensive Damage

The player is able to infiltrate an opponent's base if [health - (odmg - ddmg*0) - (odmg - ddmg*(1))... until odmg-ddmg*n<=0
where n represents the player's nth attack] is lower or equal to 0. In other words, the opponent starts with a base health of
[health]. The player then attacks with [odmg] doing that much damage to the wall. Each turn the player's [odmg] is weakened by
the opponent's [ddmg], so the next attack the player does [odmg-ddmg] to the opponent's wall. This continues until the player's
[odmg] reaches 0. If the opponent's wall is destroyed, the player successfully infiltrated their base, but if not, the player
failed.
'''

def infiltration(wall, odmg, ddmg):
    if (odmg>0):
        wall -= odmg
        odmg -= ddmg
        if wall<=0:
            return True
        else:
            return infiltration(wall, odmg, ddmg)
    else:
        return False

'''
These next few functions use CRUD applications to manipulate user data.

userID = ID of the current user
currency = Number of bits
iron = Number of iron ingots
mtime = Cooldown timer for message reward every 60 seconds
health = Current health of the user's wall
maxhealth = Max health of the user's wall
gainBits = Number of bits the user gains for each message every 60 seconds
gainIron =  Number of iron ingots the user gains for each message every 60 seconds
odmg = Offensive Damage
ddmg = Defensive Damage
cooldowntime = The amount of time left until the user can be infiltrated again
cooldown = Boolean variable determining if the user is available to get infiltrated
'''

# Creates a table if a table already doesn't exist
def create_table():
    cursor.execute("CREATE TABLE IF NOT EXISTS currency(userID TEXT, currency INTEGER, iron INTEGER, time DATE, mtime DATE, health INTEGER, maxhealth INTEGER, gainBits INTEGER, gainIron INTEGER, odmg INTEGER, ddmg INTEGER, cooldowntime DATE, cooldown INTEGER)")

# Creates a row for a unique user with default values
def start_data(userID):
    cursor.execute("INSERT INTO currency VALUES(" + userID + ", 10000, 0, '" + str(datetime.datetime.now()) +"', '" + str(datetime.datetime.now()) +"', 1000, 1000, 10, 0, 0, 0, '" + str(datetime.datetime.now()) + "', 1)")
    conn.commit()

# Retrieves a specific value belonging to a unique user
def data_retrieve(userID, selection):
    cursor.execute("SELECT " + selection + " FROM currency WHERE userID = " + userID)
    data = cursor.fetchall()
    return data

# Edits the user's balance
def data_edit(userID, num, balance, balance2):
    cursor.execute("UPDATE currency SET currency = " + str(balance2 + int(balance*num)) + " WHERE userID = " + userID)
    conn.commit()

# Edits a specific value belonging to a unique user
def data_edita(userID, selection, new):
    cursor.execute("UPDATE currency SET " + selection + "= " + str(new) + " WHERE userID = " + userID)
    conn.commit()

# Daily reward. Gives the user 10 000 bits everyday.
def data_editdaily(userID, balance):
    cursor.execute("SELECT time FROM currency WHERE userID = " + userID)
    data2 = str(cursor.fetchall()).strip("[]")
    data2 = data2[2:len(data2)-3]
    if ((datetime.datetime.now() - datetime.datetime.strptime(data2, "%Y-%m-%d %H:%M:%S.%f")).days>=1):
        #print(str(datetime.datetime.now()))
        cursor.execute("UPDATE currency SET currency = " + str(int(str(data_retrieve(userID, "currency")).strip("[]")[1:len(balance)-2])+10000) + " WHERE userID = " + userID)
        cursor.execute("UPDATE currency SET time = '" + str(datetime.datetime.now()) + "' WHERE userID = " + userID)
        conn.commit()
        return "1"
    else:
        return (datetime.datetime.now() - datetime.datetime.strptime(data2, "%Y-%m-%d %H:%M:%S.%f")).seconds

# Cooldown for getting infiltrated. A cooldown determining the user is able to be attacked or not.
def data_cooldown(userID):
    cursor.execute("SELECT cooldowntime FROM currency WHERE userID = " + userID)
    data2 = str(cursor.fetchall()).strip("[]")
    data2 = data2[2:len(data2)-3]
    cursor.execute("SELECT cooldown FROM currency WHERE userID = " + userID)
    data3 = str(cursor.fetchall()).strip("[]")
    data3 = int(data3[1:len(data3)-2])
    if (data3==0 or (datetime.datetime.now()-datetime.datetime.strptime(data2, "%Y-%m-%d %H:%M:%S.%f")).days>=1):
        return "1"
    else:
        return (datetime.datetime.now() - datetime.datetime.strptime(data2, "%Y-%m-%d %H:%M:%S.%f")).seconds

# Edits the cooldown of the user so they cannot be infiltrated in the next 24 hours
def data_editcooldown(userID):
    cursor.execute("UPDATE currency SET cooldown = 1 WHERE userID = " + userID)
    cursor.execute("UPDATE currency SET cooldowntime = " + datetime.datetime.now() + " WHERE userID = " + userID)
    cursor.commit()

# Edits the cooldown of the message reward the timer as well as reward the user with their message reward
def data_message(userID, balance, curiron, bits, iron):
    cursor.execute("SELECT mtime FROM currency WHERE userID = " + userID)
    data2 = str(cursor.fetchall()).strip("[]")
    data2 = data2[2:len(data2)-3]
    now = datetime.datetime.now()
    prev = datetime.datetime.strptime(data2, "%Y-%m-%d %H:%M:%S.%f")
    if ((now-prev).total_seconds()>=60.00):
        cursor.execute("UPDATE currency SET currency = " + str(int(balance[1:len(balance)-2])+int(bits[1:len(bits)-2])) + " WHERE userID = " + userID)
        cursor.execute("UPDATE currency SET iron = " + str(int(curiron[1:len(curiron)-2])+int(iron[1:len(iron)-2])) + " WHERE userID = " + userID)
        cursor.execute("UPDATE currency SET mtime = '" + str(now) + "' WHERE userID = " + userID)
        conn.commit()
        return "1"
'''
# Coroutines for Joining and Leaving Voice Channel
global voice
async def summon(message):
    global voice
    channel = message.author.voice.channel
    voice = await channel.connect()

async def leave():
    await voice.disconnect()

async def play(url):
    pass
'''

'''
Before Registration:
        elif (message.content[3:len(message.content)]=="music"):
            embed = discord.Embed(title = "Music", description = "Everything to do with music.", color = 0x45F4E9)
            embed.set_footer(text = "Listen to music while destroying your enemies. All commands begin with ec!")
            await channel.send(embed = embed)
'''

#balance = str(balance2 + int(balance*num))

@client.event
async def on_message(message):
    embed = discord.Embed(color=0x45F4E9)
    channel = message.channel
    balance = str(data_retrieve(str(message.author.id), "currency")).strip("[]")

    # We do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.author.bot:
        return

    '''
        Commands:
        
        ec!start = Gives the user all the information needed to create his own base
        ec!help = Lists all commands
        ec!base = Lists commands related to the user's base (rankwall, info, etc.)
        ec!mini = Lists commands related to minigames (dice, coin, steal, etc.)
        ec!register = Registers the user and gives them a base
        ec!info = Displays the user's stats
        ec!dice = The user can roll a dice. If they win their bet multipliess by 6. They lose their bet if they lose.
        ec!coin = The user can throw a coin. If they win their bet multiplies by 2. They lose their bet if they lose.
        ec!daily = Gives the user 10 000 bits daily if they message at least once a day.
        ec!steal = The user can attempt to steal from another player with a 1/3 chance of success. Bet doubles if 
        successful; otherwise, the user will lose their bet to the person they are targeting.
        ec!rankwall = Allows the user to upgrade their wall so it has more health
        ec!rankbits = Allows the user to upgrade their message reward's bits, so everytime they meesage every 60 seconds
        they get more bits
        ec!rankiron = Allows the user to upgrade their message reward's iron, so everytime they message every 60 seconds
        they get more iron.
        ec!shop = Displays the shop and all the troops that can be purchased
        ec!infiltrate = Allows the user to infiltrate another player's base to steal their goods
        ec!regen = Allows the user to pay bits to generate their wall health 
        ec!scan =  Allows the user to see some of the stats of another player's base
    '''

    # Catches all message that begin with ec!
    if message.content.startswith('ec!'):
        if (len(message.content)==8 and message.content[3:8] == "start"):
            embed.add_field(name = "Info", value = "When you register, you start out with 10,000 bits and a wall surronding your money with 1,000 health. You can upgrade your wall, buy defenses, or buy offenses to infiltrate other users' walls and steal their money. You can also play minigames to earn more money or upgrade existing forgeries to earn more or different types of currencies.")
            await channel.send(embed=embed)
        elif (message.content[3:len(message.content)]=="help"):
            embed = discord.Embed(title = "All Commands", description = "Speak every 60 seconds to get bits and iron. Use ec! befor each command.", color=0x45F4E9)
            embed.add_field(name = "Base Basics", value = "Do ec!base for more info about these commands.", inline = False)
            embed.add_field(name = "Minigames", value = "Do ec!mini for more info about these commands.", inline = False)
            #embed.add_field(name = "Music", value = "Do ec!music for more info about these commands", inline = False)
            #embed.set_footer(text = "Global Economy with Leaderboards.")
            await channel.send(embed = embed)
        elif (message.content[3:len(message.content)]=="base"):
            embed = discord.Embed(title = "Base Basics", description = "Everything to do with your base.", color = 0x45F4E9)
            embed.add_field(name="start", value="All the information needed to get started.", inline=False)
            embed.add_field(name="register", value="Register an account and earn 10000 bits instantly.", inline=False)
            embed.add_field(name="info", value="All the information about your wall, units, and potentital upgrades.",
                            inline=False)
            embed.add_field(name="rankwall", value="Increases the health of your wall.", inline = False)
            embed.add_field(name="rankbits", value="Increases the amount of bits you earn every minute.", inline = False)
            embed.add_field(name="rankiron", value="Increases the amount of iron you earn every minute.", inline = False)
            embed.add_field(name="infiltrate <user>",
                            value="Attemps to infiltrate the enemy user. If successful, you take half of their bits and iron. They lose all their troops. If unsuccessful, you lose all your offensive power.", inline = False)
            embed.add_field(name="regen <amount>",
                            value="Regens your wall by the amount specified. If over max health, restores the wall to max health. Cost is 1.5 units per unit of health.", inline = False)
            embed.add_field(name="shop", value = "The shop allows you to buy troops for defending against or initiating infiltrations on the enemy.", inline = False)
            embed.set_footer(text = "Start creating your base today using ec!register and join the global economy! All commands begin with ec!")
            await channel.send(embed = embed)
        elif (message.content[3:len(message.content)]=="mini"):
            embed = discord.Embed(title = "Minigames", description = "Everything to do with minigames.", color = 0x45F4E9)
            embed.add_field(name="coin <bet>", value="Flip a Coin. Replace <bet> with your bet. Win = 2x. Lose = 0x", inline = False)
            embed.add_field(name="dice <bet>", value="Roll a Dice. Replace <bet> with your bet. Win = 6x. Lose = 0x", inline = False)
            embed.add_field(name="steal <user> <bet>",
                            value="Steal from someone. Replace <user> with the user you want to steal from. Replace <bet> with your bet. 1/3 Success.", inline = False)
            embed.set_footer(text = "Fun minigames. All bets are in bits. All commands begin with ec!")
            await channel.send(embed = embed)
        elif (len(message.content)==11 and message.content[3:11] == "register"):
            balance = str(data_retrieve(str(message.author.id), "currency")).strip("[]")
            if balance[1:len(balance)-2]!="":
                embed.add_field(name = "Registration", value = "You already have an account!")
                await channel.send(embed = embed)
            else:
                start_data(str(message.author.id))
                embed.add_field(name = "Registration", value = "Sucessfully registered! {0.author.mention}".format(message))
                await channel.send(embed = embed)
        elif (balance[1:len(balance)-2]==""):
            embed.add_field(name = "Sorry", value = "Register an account using: ec!register")
            await channel.send(embed = embed)
        elif (len(message.content)==7 and message.content[3:7] == "info"):
            userID = str(message.author.id)
            health = str(data_retrieve(userID, "health")).strip("[]")
            maxhealth = str(data_retrieve(userID, "maxhealth")).strip("[]")
            balance = str(data_retrieve(userID, "currency")).strip("[]")
            iron = str(data_retrieve(userID, "iron")).strip("[]")
            offensive = str(data_retrieve(userID, "odmg")).strip("[]")
            defensive = str(data_retrieve(userID, "ddmg")).strip("[]")
            gainBits = str(data_retrieve(userID, "gainBits")).strip("[]")
            gainIron = str(data_retrieve(userID, "gainIron")).strip("[]")
            cooldown = ""
            if (data_cooldown(userID)=="1"):
                cooldown = 86400
            else:
                cooldown = data_cooldown(userID)
            embed.add_field(name = "Wall Health", value = "Looks like your wall is sitting at " + health[1:len(health)-2] + "/" + maxhealth[1:len(maxhealth)-2] + " health.")
            embed.add_field(name = "Balance", value = "Bits and Iron", inline = False)
            embed.add_field(name = "Bits", value = balance[1:len(balance)-2] + " bits", inline = True)
            embed.add_field(name = "Iron", value = iron[1:len(iron)-2] + " iron", inline = True)
            embed.add_field(name = "Troops", value = "Your offensive and defensive damage", inline = False)
            embed.add_field(name = "Offensive Damage", value = offensive[1:len(offensive)-2] + " offensive damage", inline = True)
            embed.add_field(name = "Defensive Damage", value = defensive[1:len(defensive)-2] + " defensive damage", inline = True)
            embed.add_field(name = "Income", value = "The amount of bits and iron you gain every minute you talk", inline = False)
            embed.add_field(name = "Bits", value = gainBits[1:len(gainBits)-2] + " bits/minute", inline = True)
            embed.add_field(name = "Iron", value = gainIron[1:len(gainIron)-2] + " iron/minute", inline = True)
            embed.add_field(name = "Cooldown", value = str(86400-cooldown) + " seconds", inline = False)
            embed.set_footer(text = "Check available upgrades by typing ec!upgrades")
            await channel.send(embed=embed)
        elif (len(message.content)>=7 and message.content[3:7] == "dice"):
            bet = int(message.content[7:len(message.content)])
            balance = str(data_retrieve(str(message.author.id), "currency")).strip("[]")
            balance = balance[1:len(balance) - 2]
            balance = int(balance)
            if (bet<=0):
                embed.add_field(name="Sorry", value="Your bet is not valid.")
                await channel.send(embed=embed)
            elif (balance>=bet):
                embed.add_field(name = "Dice Roll", value = "Rolling Dice...")
                embed.set_image(url = "https://media1.giphy.com/media/3oGRFlpAW4sIHA02NW/giphy.gif")
                message2 = await channel.send(embed = embed)
                time.sleep(3)
                await message2.delete()
                if (random.randint(1, 6) == 6):
                    embed = discord.Embed(color=0x45F4E9)
                    data_edit(str(message.author.id), 5, bet, balance)
                    embed.add_field(name="Congrats", value="You won " + str(bet * 6) + " bits.")
                    await channel.send(embed=embed)
                else:
                    embed = discord.Embed(color=0x45F4E9)
                    data_edit(str(message.author.id), 1, -bet, balance)
                    embed.add_field(name="You Suck", value="You just lost " + str(bet) + " bits.")
                    await channel.send(embed=embed)
            else:
                embed.add_field(name="Sorry", value="You do not have enough bits.")
                await channel.send(embed=embed)
        elif (len(message.content)>=7 and message.content[3:7] == "coin"):
            bet = int(message.content[7:len(message.content)])
            balance = str(data_retrieve(str(message.author.id), "currency")).strip("[]")
            balance = balance[1:len(balance)-2]
            balance = int(balance)
            if (bet<=0):
                embed.add_field(name = "Sorry", value = "Your bet is not valid.")
                await channel.send(embed = embed)
            elif (balance>=bet):
                embed.add_field(name = "Coin Flip", value = "Flipping Coin...")
                embed.set_image(url = "https://gifimage.net/wp-content/uploads/2017/10/coin-toss-gif.gif")
                message2 = await channel.send(embed = embed)
                time.sleep(3)
                await message2.delete()
                if (random.randint(0,1)):
                    embed = discord.Embed(color = 0x45F4E9)
                    data_edit(str(message.author.id), 1, bet, balance)
                    embed.add_field(name = "Congrats", value = "You won " + str(bet*2) + " bits.")
                    await channel.send(embed = embed)
                else:
                    embed = discord.Embed(color = 0x45F4E9)
                    data_edit(str(message.author.id), 1, -bet, balance)
                    embed.add_field(name = "You Suck", value = "You just lost " + str(bet) + " bits.")
                    await channel.send(embed = embed)
            else:
                embed.add_field(name = "Sorry", value = "You do not have enough bits.")
                await channel.send(embed = embed)
        elif (message.content[3:8] == "daily"):
            str2 = data_editdaily(str(message.author.id), balance)
            if (str2=="1"):
                embed.add_field(name = "Daily", value = "You have just received 10000 bits.")
                await channel.send(embed = embed)
            else:
                embed.add_field(name = "Daily", value = "You have to wait " + str(86400-str2) + " seconds before you can get your daily reward.")
                await channel.send(embed = embed)
        elif (len(message.content)>=8 and message.content[3:8]=="steal"):
            mentions = message.mentions
            if (len(mentions)>1):
                embed.add_field(name = "Sorry", value = "You can only steal from one person at a time.")
                await channel.send(embed = embed)
            else:
                otherID = str(mentions[0].id)
                otherbal = str(data_retrieve(otherID, "currency")).strip("[]")
                otherExists = True
                try:
                    otherbal = int(otherbal[1:len(otherbal)-2])
                except ValueError:
                    embed.add_field(name="Sorry", value="The person you are targeting doesn't have an account.")
                    await channel.send(embed=embed)
                    otherExists = False
                userID = str(message.author.id)
                balance = str(data_retrieve(userID, "currency")).strip("[]")
                balance = int(balance[1:len(balance)-2])
                bet = int(message.content.split(" ")[2])
                if otherExists:
                    if userID == otherID:
                        embed.add_field(name = "Sorry", value = "You can't steal from yourself silly.")
                        await channel.send(embed = embed)
                    elif bet<=0:
                        embed.add_field(name = "Sorry", value = "You have to steal more than 0 bits.")
                        await channel.send(embed = embed)
                    elif bet>otherbal:
                        embed.add_field(name = "Sorry", value = "You can't steal more than the person has unfortunately.")
                        await channel.send(embed = embed)
                    elif bet>balance:
                        embed.add_field(name = "Sorry", value = "You need to have as many bits as you are going to steal. Extra security, you know.")
                        await channel.send(embed = embed)
                    else:
                        embed.add_field(name = "Thievery", value = "Attempting to Steal...")
                        embed.set_image(url = "http://i.imgur.com/gP9sN.gif")
                        message2 = await channel.send(embed = embed)
                        time.sleep(5)
                        await message2.delete()
                        if random.randint(0,3)==1:
                            data_edit(otherID, -1, bet, otherbal)
                            data_edit(userID, 1, bet, balance)
                            embed = discord.Embed(color = 0x45F4E9)
                            embed.add_field(name = "Nice", value = "You just stole " + str(bet) + " bits from your friend.")
                            await channel.send(embed = embed)
                        else:
                            data_edit(otherID, 1, bet, otherbal)
                            data_edit(userID, -1, bet, balance)
                            embed = discord.Embed(color = 0x45F4E9)
                            embed.add_field(name = "Unlucky", value = "Your friend has caught you. You run away but your friend snatches " + str(bet) + " bits from you in the process.")
                            await channel.send(embed = embed)
        elif (message.content[3:len(message.content)]=="rankwall"):
            health = str(data_retrieve(str(message.author.id), "health")).strip("[]")
            health = health[1:len(health) - 2]
            health = int(health)
            health *= 2
            userID = str(message.author.id)
            balance = str(data_retrieve(str(message.author.id), "currency")).strip("[]")
            balance = balance[1:len(balance) - 2]
            balance = int(balance)
            if (balance>=health*25):
                data_edita(userID, "health", health)
                data_edita(userID, "maxhealth", health)
                data_edita(userID, "currency", balance-health*25)
                embed = discord.Embed(color = 0x45F4E9)
                embed.add_field(name = "Upgraded", value = "Your wall now has a max health of " + str(health))
                await channel.send(embed = embed)
            else:
                embed = discord.Embed(color = 0x45F4E9)
                embed.add_field(name = "Sorry", value = "You need " + str(health*25-balance) + " more bits to upgrade your wall.")
                await channel.send(embed = embed)
        elif (message.content[3:len(message.content)]=="rankbits"):
            userID = str(message.author.id)
            balance = str(data_retrieve(str(message.author.id), "currency")).strip("[]")
            balance = balance[1:len(balance) - 2]
            balance = int(balance)
            gainbits = str(data_retrieve(str(message.author.id), "gainBits")).strip("[]")
            gainbits = gainbits[1:len(gainbits)-2]
            gainbits = int(gainbits)
            gainbits *= 2
            if (balance>=gainbits*25):
                data_edita(userID, "gainBits", gainbits)
                data_edita(userID, "currency", balance - gainbits * 25)
                embed = discord.Embed(color = 0x45F4E9)
                embed.add_field(name = "Upgraded", value = "You gain " + str(gainbits) + " bits now when you speak every minute.")
                await channel.send(embed = embed)
            else:
                embed = discord.Embed(color = 0x45F4E9)
                embed.add_field(name = "Sorry", value = "You need " + str(gainbits*25-balance) + " more bits to upgrade the amount of bits you generate.")
                await channel.send(embed = embed)
        elif (message.content[3:len(message.content)]=="rankiron"):
            userID = str(message.author.id)
            balance = str(data_retrieve(str(message.author.id), "currency")).strip("[]")
            balance = balance[1:len(balance) - 2]
            balance = int(balance)
            iron = str(data_retrieve(str(message.author.id), "iron")).strip("[]")
            iron = iron[1:len(str(balance))-2]
            iron = int(iron)
            gainiron = str(data_retrieve(str(message.author.id), "gainIron")).strip("[]")
            gainiron = gainiron[1:len(str(gainiron)) - 2]
            gainiron = int(gainiron)
            gainiron *= 2
            gainiron += 1
            if (gainiron * 5000 >= 1000000):
                if (iron >= gainiron * 25):
                    data_edita(userID, "gainIron", gainiron)
                    data_edita(userID, "iron", iron - gainiron * 25)
                    embed = discord.Embed(color=0x45F4E9)
                    embed.add_field(name="Upgraded", value="You gain " + str(gainiron) + " iron now when you speak every minute.")
                    await channel.send(embed=embed)
                else:
                    embed = discord.Embed(color=0x45F4E9)
                    embed.add_field(name="Sorry", value="You need " + str(gainiron * 25 - iron) + " more iron to upgrade the amount of iron you generate.")
                    await channel.send(embed=embed)
            elif (balance >= gainiron * 5000):
                data_edita(userID, "gainIron", gainiron)
                data_edita(userID, "currency", balance - gainiron * 5000)
                embed = discord.Embed(color=0x45F4E9)
                embed.add_field(name="Upgraded", value="You gain " + str(gainiron) + " iron now when you speak every minute.")
                await channel.send(embed=embed)
            else:
                embed = discord.Embed(color=0x45F4E9)
                embed.add_field(name="Sorry", value="You need " + str(gainiron * 5000 - balance) + " more bits to upgrade the amount of iron you generate.")
                await channel.send(embed=embed)
        elif (message.content[3:len(message.content)]=="shop"):
            defensive = ""
            offensive = ""
            for troop in troops:
                if troop._type == "defensive":
                    if defensive == "":
                        defensive = troop._name
                    else:
                        defensive += ", " + troop._name
                else:
                    if offensive == "":
                        offensive = troop._name
                    else:
                        offensive += ", " + troop._name
            embed = discord.Embed(color = 0x45F4E9)
            embed.add_field(name = "Shop", value = "Buy defensive troops here to protect your base, or buy offensive troops to infiltrate others.")
            embed.add_field(name = "Defensive", value = defensive)
            embed.add_field(name = "Offensive", value = offensive)
            embed.set_footer(text="Type ec!<troop name> to learn more.")
            await channel.send(embed=embed)
        elif (message.content[3:13]=="infiltrate"):
            mentions = message.mentions
            if (len(mentions)>1):
                embed = discord.Embed(color = 0x45F4E9)
                embed.add_field(name = "Sorry", value = "Please mention only one user.")
                await channel.sned(embed=embed)
            elif (len(mentions)==1):
                otherID = str(mentions[0].id)
                otherbal = str(data_retrieve(otherID, "currency")).strip("[]")
                otherExists = True
                try:
                    otherbal = int(otherbal[1:len(otherbal) - 2])
                except ValueError:
                    embed = discord.Embed(color = 0x45F4E9)
                    embed.add_field(name="Sorry", value="The person you are targeting doesn't have an account.")
                    await channel.send(embed=embed)
                    otherExists = False
                userID = str(message.author.id)
                if (otherID==userID):
                    embed = discord.Embed(color = 0x45F4E9)
                    embed.add_field(name = "Sorry", value = "You can't target yourself.")
                    await channel.send(embed=embed)
                else:
                    balance = str(data_retrieve(userID, "currency")).strip("[]")
                    balance = int(balance[1:len(balance) - 2])
                    iron = str(data_retrieve(userID, "iron")).strip("[]")
                    iron = int(iron[1:len(iron) - 2])
                    if otherExists:
                        if (data_cooldown(otherID)=="1"):
                            data_editcooldown(otherID)
                            data_edita(userID, "cooldown", 0)
                            otheriron = str(data_retrieve(otherID, "iron")).strip("[]")
                            otheriron = int(otheriron[1:len(otheriron) - 2])
                            enemyhealth = str(data_retrieve(otherID, "health")).strip("[]")
                            enemyhealth = int(enemyhealth[1:len(enemyhealth) - 2])
                            offen = str(data_retrieve(userID, "odmg")).strip("[]")
                            offen = int(offen[1:len(offen) - 2])
                            defen = str(data_retrieve(otherID, "ddmg")).strip("[]")
                            defen = int(defen[1:len(defen) - 2])
                            if infiltration(enemyhealth, offen, defen):
                                maxhealth = str(data_retrieve(otherID, "maxhealth")).strip("[]")
                                maxhealth = int(maxhealth[1:len(maxhealth) - 2])
                                data_edita(userID, "currency", balance + otherbal // 2)
                                data_edita(userID, "iron", iron + otheriron // 2)
                                data_edita(otherID, "currency", otherbal - otherbal // 2)
                                data_edita(otherID, "iron", otheriron - otheriron // 2)
                                data_edita(otherID, "odmg", 0)
                                data_edita(otherID, "ddmg", 0)
                                data_edita(otherID, "health", maxhealth)
                                embed = discord.Embed(color=0x45F4E9)
                                embed.add_field(name="Success",
                                                value="You successfully infiltrated the enemy base, earning " + str(
                                                    otherbal // 2) + " bits and " + str(
                                                    otheriron // 2) + " iron. All enemy troops have died as a result.")
                                await channel.send(embed=embed)
                            else:
                                data_edita(userID, "odmg", 0)
                                embed = discord.Embed(color=0x45F4E9)
                                embed.add_field(name="Failure",
                                                value="You failed to infiltrate the enemy base, losing all your offensive troops.")
                                await channel.send(embed=embed)
                        else:
                            embed = discord.Embed(color =0x45F4E9)
                            embed.add_field(name = "Sorry", value = "You have to wait " + str(86400-data_cooldown(otherID)) + " seconds before you can attack this base.")
                            await channel.send(embed=embed)
            else:
                embed = discord.Embed(color = 0x45F4E9)
                embed.add_field(name = "Sorry", value = "Please mention the user you want to target.")
                await channel.send(embed=embed)
        elif (message.content[3:8]=="regen"):
            userID = str(message.author.id)
            balance = str(data_retrieve(userID, "currency")).strip("[]")
            balance = balance[1:len(balance) - 2]
            balance = int(balance)
            health = str(data_retrieve(userID, "health")).strip("[]")
            health = int(health[1:len(health)-2])
            maxhealth = str(data_retrieve(userID, "maxhealth")).strip("[]")
            maxhealth = int(maxhealth[1:len(maxhealth)-2])
            valid = True
            try:
                regen = int(message.content[9: len(message.content)])
            except ValueError:
                embed = discord.Embed(embed = 0x45F4E9)
                embed.add_field(name = "Sorry", value = "Please enter a valid number for the amount of health you wish to regen")
                await channel.send(embed=embed)
                valid = False
            if valid:
                if (regen==0):
                    embed = discord.Embed(embed=0x45F4E9)
                    embed.add_field(name="Sorry", value="Please enter a valid number for the amount of health you wish to regen")
                    await channel.send(embed=embed)
                if (maxhealth-health==0):
                    embed = discord.Embed(embed = 0x45F4E9)
                    embed.add_field(name = "Sorry", value = "Your wall is at full health.")
                    await channel.send(embed=embed)
                else:
                    if regen+health>maxhealth:
                        regen = maxhealth-health
                    if (int(math.floor(regen * 1.5)) > balance):
                        embed = discord.Embed(embed=0x45F4E9)
                        embed.add_field(name="Sorry", value="You don't have enough money to regen your wall that much.")
                        await channel.send(embed=embed)
                    else:
                        data_edita(userID, "currency", balance-int(math.floor(regen * 1.5)))
                        data_edita(userID, "health", health+regen)
                        embed.add_field(name = "Success", value = "The health of your wall is now " + str(health+regen))
                        await channel.send(embed=embed)
        elif (message.content[3:7]=="scan"):
            mentions = message.mentions
            if (len(mentions) > 1):
                embed = discord.Embed(color=0x45F4E9)
                embed.add_field(name="Sorry", value="Please mention only one user.")
                await channel.sned(embed=embed)
            elif (len(mentions) == 1):
                otherID = str(mentions[0].id)
                otherbal = str(data_retrieve(otherID, "currency")).strip("[]")
                otherExists = True
                try:
                    otherbal = int(otherbal[1:len(otherbal) - 2])
                except ValueError:
                    embed = discord.Embed(color=0x45F4E9)
                    embed.add_field(name="Sorry", value="The person you are scanning doesn't have an account.")
                    await channel.send(embed=embed)
                    otherExists = False
                userID = str(message.author.id)
                if (otherExists):
                    if (otherID!=userID):
                        otheriron = str(data_retrieve(otherID, "iron")).strip("[]")
                        otheriron = int(otheriron[1:len(otheriron) - 2])
                        enemyhealth = str(data_retrieve(otherID, "health")).strip("[]")
                        enemyhealth = int(enemyhealth[1:len(enemyhealth) - 2])
                        maxhealth = str(data_retrieve(otherID, "maxhealth")).strip("[]")
                        maxhealth = int(maxhealth[1:len(maxhealth) - 2])
                        cooldown = ""
                        if (data_cooldown(otherID)=="1"):
                            cooldown = 86400
                        else:
                            cooldown = data_cooldown(otherID)
                        embed = discord.Embed(color=0x45F4E9)
                        embed.add_field(name="Wall Health", value="Looks like their wall is sitting at " + str(enemyhealth) + "/" + str(maxhealth) + " health.")
                        embed.add_field(name="Balance", value="Bits and Iron", inline=False)
                        embed.add_field(name="Bits", value=str(otherbal) + " bits", inline=True)
                        embed.add_field(name="Iron", value=str(otheriron) + " iron", inline=True)
                        embed.add_field(name="Troops", value="Your offensive and defensive damage", inline=False)
                        embed.add_field(name="Offensive Damage", value="??? offensive damage",
                                        inline=True)
                        embed.add_field(name="Defensive Damage", value="??? defensive damage",
                                        inline=True)
                        embed.add_field(name = "Cooldown", value = str(86400-cooldown) + " seconds", inline = False)
                        embed.set_footer(text=str(mentions[0].name) + "'s Base")
                        await channel.send(embed=embed)
                    else:
                        embed = discord.Embed(color=0x45F4E9)
                        embed.add_field(name = "Sorry", value = "You can't scan yourself.")
                        await channel.send(embed=embed)
                else:
                    embed = discord.Embed(color=0x45F4E9)
                    embed.add_field(name = "Sorry", value = "The base you are trying to scan doesn't exist.")
                    await channel.send(embed=embed)
            else:
                embed = discord.Embed(color=0x45F4E9)
                embed.add_field(name="Sorry", value="Please mention the user you want to scan.")
                await channel.send(embed=embed)
        '''
        elif (message.content[3:9]=="summon"):
            await summon(message)
        elif (message.content[3:8]=="leave"):
            await leave()
        '''
        for troop in troops:
            if (message.content[3:len(message.content)]==troop._name):
                embed = discord.Embed(color = 0x45F4E9)
                embed.add_field(name = troop._name, value = troop._desc)
                embed.add_field(name = "Type", value = troop._type.capitalize(), inline = False)
                embed.add_field(name = "Cost", value = troop._cost + " " + troop._curr, inline = False)
                embed.add_field(name = "Damage", value = troop._dmg + " units/second", inline = False)
                embed.add_field(name = "Buy?", value = "Type \"ec!" + troop._name + " buy <quantity>\" to buy a <quantity> number of " + troop._name.lower() + "s", inline = False)
                await channel.send(embed=embed)
            if (message.content[3:int(7+len(troop._name))]==str(troop._name + " buy")):
                userID = str(message.author.id)
                balance = str(data_retrieve(str(message.author.id), "currency")).strip("[]")
                balance = balance[1:len(balance) - 2]
                balance = int(balance)
                iron = str(data_retrieve(str(message.author.id), "iron")).strip("[]")
                iron = iron[1:len(iron) - 2]
                iron = int(iron)
                quantity = int(message.content[int(7+len(troop._name)):len(message.content)])
                ddmg = str(data_retrieve(str(message.author.id), "ddmg")).strip("[]")
                ddmg = ddmg[1:len(ddmg)-2]
                ddmg = int(ddmg)
                odmg = str(data_retrieve(str(message.author.id), "odmg")).strip("[]")
                odmg = odmg[1:len(odmg)-2]
                odmg = int(odmg)
                if (troop._curr=="iron"):
                    if (iron>=int(troop._cost)*quantity):
                        data_edita(userID, "iron", iron-int(troop._cost)*quantity)
                        if (troop._type == "defensive"):
                            data_edita(userID, "ddmg", ddmg + int(troop._dmg)*quantity)
                        else:
                            data_edita(userID, "odmg", odmg + int(troop._dmg)*quantity)
                        embed = discord.Embed(color = 0x45F4E9)
                        embed.add_field(name = "Congrats", value = "You just purchased " + str(quantity) + " " + troop._name + "s for " + str(int(troop._cost)*quantity) + " " + troop._curr + ".")
                        await channel.send(embed = embed)
                    else:
                        embed = discord.Embed(color = 0x45F4E9)
                        embed.add_field(name = "Sorry", value = "You need " + str(int(troop._cost)*quantity-iron) + " more " + troop._curr + " to purchase " + str(quantity) + " of this troop.")
                        await channel.send(embed = embed)
                else:
                    if (balance>=int(troop._cost)*quantity):
                        data_edita(userID, "currency", balance-int(troop._cost)*quantity)
                        if (troop._type == "defensive"):
                            data_edita(userID, "ddmg", ddmg + int(troop._dmg)*quantity)
                        else:
                            data_edita(userID, "odmg", odmg + int(troop._dmg)*quantity)
                        embed = discord.Embed(color = 0x45F4E9)
                        embed.add_field(name = "Congrats", value = "You just purchased " + str(quantity) + " " + troop._name + "s for " + str(int(troop._cost)*quantity) + " " + troop._curr + ".")
                        await channel.send(embed = embed)
                    else:
                        embed = discord.Embed(color = 0x45F4E9)
                        embed.add_field(name = "Sorry", value = "You need " + str(int(troop._cost)*quantity-balance) + " more " + troop._curr + " to purchase " + str(quantity) + " of this troop.")
                        await channel.send(embed = embed)
    #Users get message awards every minute
    curiron = str(data_retrieve(str(message.author.id), "iron")).strip("[]")
    bits = str(data_retrieve(str(message.author.id), "gainBits")).strip("[]")
    iron = str(data_retrieve(str(message.author.id), "gainIron")).strip("[]")
    data_message(str(message.author.id), balance, curiron, bits, iron)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(activity=discord.Game(name='ec!help'))

create_table()
client.run(TOKEN)
