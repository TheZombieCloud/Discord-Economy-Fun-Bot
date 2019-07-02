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


def create_table():
    cursor.execute("CREATE TABLE IF NOT EXISTS currency(userID TEXT, currency INTEGER, time DATE, mtime DATE)")

def data_entry(userID):
    cursor.execute("INSERT INTO currency VALUES(" + userID + ", 10000, '" + str(datetime.datetime.now()) +"', '" + str(datetime.datetime.now()) +"')")
    conn.commit()

def data_retrieve(userID):
    cursor.execute("SELECT currency FROM currency WHERE userID = " + userID)
    data = cursor.fetchall()
    return data

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

def data_rmess(userID, balance):
    cursor.execute("SELECT mtime FROM currency WHERE userID = " + userID)
    data2 = str(cursor.fetchall()).strip("[]")
    data2 = data2[2:len(data2)-3]
    now = datetime.datetime.now()
    prev = datetime.datetime.strptime(data2, "%Y-%m-%d %H:%M:%S.%f")
    if ((now-prev).total_seconds()>=30.00):
        cursor.execute("UPDATE currency SET currency = " + str(int(str(data_retrieve(userID)).strip("[]")[1:len(balance)-2])+10) + " WHERE userID = " + userID)
        cursor.execute("UPDATE currency SET mtime = '" + str(now) + "' WHERE userID = " + userID)
        conn.commit()
        return "1"

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    balance = str(data_retrieve(str(message.author.id))).strip("[]")
    embed = discord.Embed(color = 0x45F4E9)
    channel = message.channel

    #Reward user for typing every 30 seconds
    #if (balance[1:len(balance)-2]!=""):
        #data_editdaily(str(message.author.id), 30, 5)

    if message.author == client.user:
        return

    if message.author.bot:
        return

    if message.content.startswith('ec!'):
        if (len(message.content)==11 and message.content[3:11] == "register"):
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
        elif (message.content[3:len(message.content)]=="rankup"):
            pass
        elif (message.content[3:len(message.content)]=="help"):
            embed.add_field(name = "All Commands", value = "Speak every 30 seconds to get free bits. Use ec! before each command.")
            embed.add_field(name = "register", value = "Register an account and earn 10000 bits instantly.")
            embed.add_field(name = "balance", value = "This command allows you to check your balance.")
            embed.add_field(name = "coin <bet>", value = "Flip a Coin. Replace <bet> with your bet. Win = 2x. Lose = 0x")
            embed.add_field(name = "dice <bet>", value = "Roll a Dice. Replace <bet> with your bet. Win = 6x. Lose = 0x")
            embed.add_field(name = "steal <user> <bet>", value = "Steal from someone. Replace <user> with the user you want to steal from. Replace <bet> with your bet. 1/3 Success.")
            await channel.send(embed = embed)
    # Get bits every 30 seconds
    str2 = data_rmess(str(message.author.id), balance)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(activity=discord.Game(name='ec!help'))

create_table()
client.run(TOKEN)
