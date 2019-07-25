import discord
import datetime
import sqlite3
import random
import time
from sqlite3 import Error

TOKEN = ''

client = discord.Client()

conn = sqlite3.connect("currency.db")
cursor = conn.cursor()

troops = []

class Troop():
    def __init__(self, type, name, dmg, cost, desc, curr):
        self._type = type
        self._name = name
        self._dmg = dmg
        self._cost = cost
        self._desc = desc
        self._curr = curr

def recursefib(wall, odmg, ddmg):
    if (odmg>0):
        wall -= odmg
        odmg -= ddmg
        if wall<=0:
            return True
        else:
            return recursefib(wall, odmg, ddmg)
    else:
        return False

def create_table():
    cursor.execute("CREATE TABLE IF NOT EXISTS currency(userID TEXT, currency INTEGER, iron INTEGER, time DATE, mtime DATE, health INTEGER, maxhealth INTEGER, gainBits INTEGER, gainIron INTEGER, odmg INTEGER, ddmg, INTEGER)")

def data_entry(userID):
    cursor.execute("INSERT INTO currency VALUES(" + userID + ", 10000, 0, '" + str(datetime.datetime.now()) +"', '" + str(datetime.datetime.now()) +"', 1000, 1000, 10, 0, 0, 0)")
    conn.commit()

def data_retrieve(userID):
    cursor.execute("SELECT currency FROM currency WHERE userID = " + userID)
    data = cursor.fetchall()
    return data

def data_retrievea(userID, selection):
    cursor.execute("SELECT " + selection + " FROM currency WHERE userID = " + userID)
    data = cursor.fetchall()
    return data

def data_edita(userID, selection, new):
    cursor.execute("UPDATE currency SET " + selection + "= " + str(new) + " WHERE userID = " + userID)
    conn.commit()

def data_edit(userID, num, balance, balance2):
    cursor.execute("UPDATE currency SET currency = " + str(balance2 + int(balance*num)) + " WHERE userID = " + userID)
    conn.commit()

def data_editdaily(userID, balance):
    cursor.execute("SELECT time FROM currency WHERE userID = " + userID)
    data2 = str(cursor.fetchall()).strip("[]")
    data2 = data2[2:len(data2)-3]
    if ((datetime.datetime.now() - datetime.datetime.strptime(data2, "%Y-%m-%d %H:%M:%S.%f")).days>=1):
        #print(str(datetime.datetime.now()))
        cursor.execute("UPDATE currency SET currency = " + str(int(str(data_retrieve(userID)).strip("[]")[1:len(balance)-2])+10000) + " WHERE userID = " + userID)
        cursor.execute("UPDATE currency SET time = '" + str(datetime.datetime.now()) + "' WHERE userID = " + userID)
        conn.commit()
        return "1"
    else:
        return (datetime.datetime.now() - datetime.datetime.strptime(data2, "%Y-%m-%d %H:%M:%S.%f")).seconds

def data_rmess(userID, balance, curiron, bits, iron):
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

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    balance = str(data_retrieve(str(message.author.id))).strip("[]")
    curiron = str(data_retrievea(str(message.author.id), "iron")).strip("[]")
    bits = str(data_retrievea(str(message.author.id), "gainBits")).strip("[]")
    iron = str(data_retrievea(str(message.author.id), "gainIron")).strip("[]")
    embed = discord.Embed(color = 0x45F4E9)
    channel = message.channel

    if message.author == client.user:
        return

    if message.author.bot:
        return

    if message.content.startswith('ec!'):
        if (len(message.content)==8 and message.content[3:8] == "start"):
            embed.add_field(name = "Info", value = "When you register, you start out with 10,000 bits and a wall surronding your money with 1,000 health. You can upgrade your wall, buy defenses, or buy offenses to infiltrate other users' walls and steal their money. You can also play minigames to earn more money or upgrade existing forgeries to earn more or different types of currencies.")
            await channel.send(embed=embed)
        elif (message.content[3:len(message.content)]=="help"):
            embed.add_field(name = "All Commands", value = "Speak every 60 seconds to get bits and iron. Use ec! before each command.")
            embed.add_field(name = "start", value = "All the information needed to get started.")
            embed.add_field(name = "register", value = "Register an account and earn 10000 bits instantly.")
            embed.add_field(name = "balance", value = "This command allows you to check your balance.")
            embed.add_field(name = "info", value = "All the information about your wall, units, and potentital upgrades.")
            embed.add_field(name = "rankwall", value = "Increases the health of your wall.")
            embed.add_field(name = "rankbits", value = "Increases the amount of bits you earn every minute.")
            embed.add_field(name = "rankiron", value = "Increases the amount of iron you earn every minute.")
            embed.add_field(name = "infiltrate <user>", value = "Attemps to infiltrate the enemy user. If successful, you take half of their bits and iron. They lose all their troops. If unsuccessful, you lose all your offensive power.")
            embed.add_field(name = "coin <bet>", value = "Flip a Coin. Replace <bet> with your bet. Win = 2x. Lose = 0x")
            embed.add_field(name = "dice <bet>", value = "Roll a Dice. Replace <bet> with your bet. Win = 6x. Lose = 0x")
            embed.add_field(name = "steal <user> <bet>", value = "Steal from someone. Replace <user> with the user you want to steal from. Replace <bet> with your bet. 1/3 Success.")
            await channel.send(embed = embed)
        elif (len(message.content)==11 and message.content[3:11] == "register"):
            balance = str(data_retrieve(str(message.author.id))).strip("[]")
            if balance[1:len(balance)-2]!="":
                embed.add_field(name = "Registration", value = "You already have an account!")
                await channel.send(embed = embed)
            else:
                data_entry(str(message.author.id))
                embed.add_field(name = "Registration", value = "Sucessfully registered! {0.author.mention}".format(message))
                await channel.send(embed = embed)
        elif (balance[1:len(balance)-2]==""):
            embed.add_field(name = "Sorry", value = "Register an account using: ec!register")
            await channel.send(embed = embed)
        elif (len(message.content)==7 and message.content[3:7] == "info"):
            health = str(data_retrievea(str(message.author.id), "health")).strip("[]")
            embed.add_field(name = "Wall Health", value = "Looks like your wall is sitting at " + health[1:len(health)-2] + " health.")
            await channel.send(embed=embed)
        elif (len(message.content)==10 and message.content[3:10] == "balance"):
            balance = str(data_retrieve(str(message.author.id))).strip("[]")
            if balance[1:len(balance)-2]=="":
                embed.add_field(name = "Balance", value = 'Register an account using \"ec!register\"')
                await channel.send(embed = embed)
            else:
                embed.add_field(name = "Balance", value = "You have " + balance[1:len(balance)-2] + " bits.")
                await channel.send(embed=embed)
        elif (len(message.content)>=7 and message.content[3:7] == "dice"):
            bet = int(message.content[7:len(message.content)])
            balance = str(data_retrieve(str(message.author.id))).strip("[]")
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
            balance = str(data_retrieve(str(message.author.id))).strip("[]")
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
                otherbal = str(data_retrieve(otherID)).strip("[]")
                otherExists = True
                try:
                    otherbal = int(otherbal[1:len(otherbal)-2])
                except ValueError:
                    embed.add_field(name="Sorry", value="The person you are targeting doesn't have an account.")
                    await channel.send(embed=embed)
                    otherExists = False
                userID = str(message.author.id)
                balance = str(data_retrieve(userID)).strip("[]")
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
            health = str(data_retrievea(str(message.author.id), "health")).strip("[]")
            health = health[1:len(health) - 2]
            health = int(health)
            health *= 2
            userID = str(message.author.id)
            balance = str(data_retrieve(str(message.author.id))).strip("[]")
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
            balance = str(data_retrieve(str(message.author.id))).strip("[]")
            balance = balance[1:len(balance) - 2]
            balance = int(balance)
            gainbits = str(data_retrievea(str(message.author.id), "gainBits")).strip("[]")
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
            balance = str(data_retrieve(str(message.author.id))).strip("[]")
            balance = balance[1:len(balance) - 2]
            balance = int(balance)
            iron = str(data_retrieve(str(message.author.id), "iron")).strip("[]")
            iron = iron[1:len(balance)-2]
            iron = int(iron)
            gainiron = str(data_retrievea(str(message.author.id), "gainIron")).strip("[]")
            gainiron = gainiron[1:len(gainiron) - 2]
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
            embed.add_field(name = "Shop", value = "Buy defensive troops here to protect your base, or buy offensive troops to infiltrate others. Type ec!<troop name> to learn more.")
            embed.add_field(name = "Defensive", value = defensive)
            embed.add_field(name = "Offensive", value = offensive)
            await channel.send(embed=embed)
        elif (message.content[3:13]=="infiltrate"):
            mentions = message.mentions()
            if (len(mentions)>1):
                embed = discord.Embed(color = 0x45F4E9)
                embed.add_field(name = "Sorry", value = "Please mention only one user.")
                await channel.sned(embed=embed)
            elif (len(mentions)==1):
                otherID = str(mentions[0].id)
                otherbal = str(data_retrieve(otherID)).strip("[]")
                otherExists = True
                try:
                    otherbal = int(otherbal[1:len(otherbal) - 2])
                except ValueError:
                    embed.add_field(name="Sorry", value="The person you are targeting doesn't have an account.")
                    await channel.send(embed=embed)
                    otherExists = False
                userID = str(message.author.id)
                balance = str(data_retrieve(userID)).strip("[]")
                balance = int(balance[1:len(balance) - 2])
                iron = str(data_retrievea(userID, "iron")).strip("[]")
                iron = int(iron[1:len(iron)-2])
                if otherExists:
                    otheriron = str(data_retrievea(otherID, "iron")).strip("[]")
                    otheriron = int(otheriron[1:len(otheriron)-2])
                    enemyhealth = str(data_retrievea(otherID, "health")).strip("[]")
                    enemyhealth = int(enemyhealth[1:len(enemyhealth)-2])
                    offen = str(data_retrievea(userID, "odmg")).strip("[]")
                    offen = int(offen[1:len(offen)-2])
                    defen = str(data_retrievea(otherID, "ddmg")).strip("[]")
                    defen = int(defen[1:len(defen)-2])
                    if recursefib(enemyhealth, offen, defen):
                        data_edita(userID, "currency", balance+otherbal//2)
                        data_edita(userID, "iron", iron + otheriron//2)
                        data_edita(otherID, "currency", otherbal - otherbal//2)
                        data_edita(otherID, "iron", otheriron - otheriron//2)
                        data_edita(otherID, "odmg", 0)
                        data_edita(otherID, "ddmg", 0)
                        embed = discord.Embed(color = 0x45F4E9)
                        embed.add_field(name = "Success", value = "You successfully infiltrated the enemy base, earning " + str(otherbal//2) + " bits and " + str(otheriron//2) + " iron. All enemy troops have died as a result.")
                        await channel.send(embed=embed)
                    else:
                        data_edita(userID, "odef", 0)
                        embed = discord.Embed(color = 0x45F4E9)
                        embed.add_field(name = "Failure", value = "You failed to infiltrate the enemy base, losing all your offensive troops.")
                        await channel.send(embed=embed)
            else:
                embed = discord.Embed(color = 0x45F4E9)
                embed.add_field(name = "Sorry", value = "Please mention the user you want to target.")
                await channel.send(embed=embed)
        for troop in troops:
            if (message.content[3:len(message.content)]==troop._name):
                embed = discord.Embed(color = 0x45F4E9)
                embed.add_field(name = troop._name, value = troop._desc)
                embed.add_field(name = "Type", value = troop._type)
                embed.add_field(name = "Cost", value = troop._cost + " " + troop._curr)
                embed.add_field(name = "Damage", value = troop._cost + "/s")
                embed.add_field(name = "Buy?", value = "Type \"ec!" + troop._name + " buy\" to buy " + troop._name)
                await channel.send(embed=embed)
            if (message.content[3:len(message.content)]==str(troop._name + " buy")):
                userID = str(message.author.id)
                balance = str(data_retrieve(str(message.author.id))).strip("[]")
                balance = balance[1:len(balance) - 2]
                balance = int(balance)
                iron = str(data_retrieve(str(message.author.id), "iron")).strip("[]")
                iron = iron[1:len(balance) - 2]
                iron = int(iron)
                if (troop._curr=="iron"):
                    if (iron>=troop._cost):
                        data_edita(userID, "iron", iron-troop._cost)
                        if (troop._type == "defensive"):
                            data_edita(userID, "ddmg", int(data_retrievea(userID, "ddmg"))+troop._dmg)
                        else:
                            data_edita(userID, "odmg", int(data_retrievea(userID, "odmg")) + troop._dmg)
                        embed = discord.Embed(color = 0x45F4E9)
                        embed.add_field(name = "Congrats", value = "You just purchased " + troop._name + " for " + troop._cost + " " + troop._curr + ".")
                        await channel.send(embed = embed)
                    else:
                        embed = discord.Embed(color = 0x45F4E9)
                        embed.add_field(name = "Sorry", value = "You need " + str(troop._cost-iron) + " more " + troop._curr + " to purchase this troop.")
                        await channel.send(embed = embed)
                else:
                    if (balance>=troop.cost):
                        data_edita(userID, "currency", balance-troop._cost)
                        if (troop._type == "defensive"):
                            data_edita(userID, "ddmg", int(data_retrievea(userID, "ddmg")) + troop._dmg)
                        else:
                            data_edita(userID, "odmg", int(data_retrievea(userID, "odmg")) + troop._dmg)
                        embed = discord.Embed(color = 0x45F4E9)
                        embed.add_field(name = "Congrats", value = "You just purchased " + troop._name + " for " + troop._cost + " " + troop._curr + ".")
                        await channel.send(embed = embed)
                    else:
                        embed = discord.Embed(color = 0x45F4E9)
                        embed.add_field(name = "Sorry", value = "You need " + str(troop._cost-balance) + " more " + troop._curr + " to purchase this troop.")
                        await channel.send(embed = embed)
    # Get bits every minute
    str2 = data_rmess(str(message.author.id), balance, curiron, bits, iron)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(activity=discord.Game(name='ec!help'))

create_table()
client.run(TOKEN)
