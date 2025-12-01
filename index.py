import nextcord
from nextcord.ext import commands
import requests
from datetime import datetime

client = commands.Bot()
TOKEN = ""

@client.event
async def on_ready():
  print(f"{client.user.name} online")
  await client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.listening, name=f"{len(client.guilds)} servers"))


@client.slash_command(name="code-check")
async def code_check(interaction, code):
    requests.post("", json={"embeds":[{"title":f"{interaction.user.display_name} used /code-check {code}"}]})
    await interaction.response.send_message(".")
    await interaction.delete_original_message()

    token = requests.post("https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token", headers={"Authorization":"basic MzRhMDJjZjhmNDQxNGUyOWIxNTkyMTg3NmRhMzZmOWE6ZGFhZmJjY2M3Mzc3NDUwMzlkZmZlNTNkOTRmYzc2Y2Y="}, data={"grant_type":"client_credentials"}).json()
    headers = {"Authorization": f"Bearer {token['access_token']}"}
    data = requests.post(f"https://coderedemption-public-service-prod.ol.epicgames.com/coderedemption/api/shared/accounts/82b671e0d9b84f3cbe17dcd429ff102d/redeem/{code.replace('-', '')}/evaluate", headers=headers).json()

    if not "numericErrorCode" in data:
        product_data = requests.get(f"https://catalog-public-service-prod06.ol.epicgames.com/catalog/api/shared/bulk/offers?id={data['consumptionMetadata']['offerId']}&locale=fr&contry=FR", headers=headers).json()
        embed = nextcord.Embed(title=None, color=0x29a6d8)
        embed.add_field(name="Code", value=str(code).replace("-", "").upper()[:-5] + "XXXXX", inline=False)
        embed.add_field(name="Status Du Code", value=data["codeStatus"], inline=False)
        embed.add_field(name="Nom", value=product_data[data["consumptionMetadata"]["offerId"]]["title"], inline=False)
        embed.add_field(name="Description", value=product_data[data["consumptionMetadata"]["offerId"]]["description"], inline=False)

        if "startDate" in data:
            embed.add_field(name="Date/Heure de début", value=nextcord.utils.format_dt(datetime.strptime(data["startDate"], "%Y-%m-%dT%H:%M:%S.%fZ"), style="f"), inline=False)
        if "endDate" in data:
            embed.add_field(name="Date/Heure de fin", value=nextcord.utils.format_dt(datetime.strptime(data["endDate"], "%Y-%m-%dT%H:%M:%S.%fZ"), style="f"), inline=False)

        embed.add_field(name="Utilisation", value=f"**{data['completedCount']} ➤ {data['maxNumberOfUses']}**", inline=False)
    else:
        if data["numericErrorCode"] == 19007:
            embed = nextcord.Embed(title="Code introuvable", color=0xe3382c)
        elif data["numericErrorCode"] == 19010:
            embed = nextcord.Embed(title="Code utilisé", color=0xe3382c)
        elif data["numericErrorCode"] == 19005:
            embed = nextcord.Embed(title="Code expiré", color=0xe3382c)
        else:
            embed = nextcord.Embed(title=data["ErrorMessage"], color=0xe3382c)
    await interaction.followup.send(embed=embed)
    
    print(data)
  
client.run(TOKEN)
