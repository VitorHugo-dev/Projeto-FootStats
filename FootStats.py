import requests
import json
import time
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import DC, FOAF, RDF


# consultar dbpedia para obeter descricao sobre as ligas
def getLeagueDesc(url, title):
    try:
        data = requests.get(url)
        jsonData = json.loads(data.content)

        temp = jsonData["http://dbpedia.org/resource/"+title]["http://dbpedia.org/ontology/abstract"]
        for x in temp:
            if (x["lang"] == "pt"):
                desc = x["value"]

        baseData = []
        baseData.append(title)
        baseData.append(desc)
        baseData.append(url)

        return baseData

    except Exception as e:
        print("\nError, caused by: " + str(e))

# consultar api e devolver dados sobre a liga
def getCompetitionData(id):
    try:
        count = 0
        urlBase = "http://api.football-data.org/v2/competitions/"
        headers = {'X-Auth-Token':  '6e1cf7d0fba84518992380ceb5776f46'}
        competitionData = []
        teams = []
        players = []

        data = requests.get(urlBase + str(id), headers=headers)
        jsonData = json.loads(data.content)
        time.sleep(6)
        count = count + 1

        competitionData = {
            "ID": jsonData["id"],
            "NAME": jsonData["name"],
            "CODE": jsonData["code"],
            "LOCATION": jsonData["area"]["name"]
        }

        teamData = requests.get(urlBase + str(id) + "/teams",headers=headers)
        jsonTeamData = json.loads(teamData.content)
        time.sleep(6)

        count = count + 1

        if (jsonTeamData["teams"] != []):
            for team in jsonTeamData["teams"]:
                t = {
                    "ID": team["id"],
                    "NAME": team["name"],
                    "SHORTNAME": team["tla"],
                    "ADDRESS": team["address"],
                    "WEBSITE": team["website"],
                    "FOUNDED": team["founded"],
                    "CLUBCOLORS": team["clubColors"]
                }
                time.sleep(6)
                squadData = requests.get("http://api.football-data.org/v2/teams/" + str(team["id"]), headers=headers)
                jsonsquadData = json.loads(squadData.content)
                count = count + 1
                player = []
                if (jsonsquadData["squad"] != []):
                    for squad in jsonsquadData["squad"]:
                        s = {
                            "ID": squad["id"],
                            "NAME": squad["name"],
                            "POSITION": squad["position"],
                            "NATIONALITY": squad["nationality"],
                            "NUMBER": squad["shirtNumber"],
                            "ROLE": squad["role"]
                        }
                        player.append(s)
                t["PLAYERS"] = player
                teams.append(t)

            competitionData["TEAMS"] = teams


        return competitionData
    except Exception as e:
        print("\nError, caused by: " + str(e))


# Função que monta o grafo
def graphGenerator(premierLeagueData, ligue1Data, bundesligaData,seriaAData,laLigaData):
    g = Graph()
    foot = Namespace("https://footstats.com.br/#")
    dbpedia = Namespace("http://dbpedia.org/page/")
# premire league
    g.add((foot.Competition, RDF.type, FOAF.Project))
    g.add((foot.a + str(premierLeagueData["ID"]), RDF.type, Literal("competition")))
    g.add((foot.a + str(premierLeagueData["ID"]), DC.description, Literal(premierLeagueData["DESC"][1])))
    g.add((foot.a + str(premierLeagueData["ID"]), DC.homepage, Literal(premierLeagueData["DESC"][2])))
    g.add((foot.a + str(premierLeagueData["ID"]), FOAF.firstname, Literal(premierLeagueData["NAME"])))
    g.add((foot.a + str(premierLeagueData["ID"]), FOAF.nick, Literal(premierLeagueData["CODE"])))
    g.add((foot.a + str(premierLeagueData["ID"]), foot.location, Literal(premierLeagueData["LOCATION"])))
    for x in premierLeagueData["TEAMS"]:
        g.add((foot.a + str(x["ID"]), RDF.type, Literal("team")))
        g.add((foot.a + str(x["ID"]), foot.timede, Literal(premierLeagueData["DESC"][0])))
        g.add((foot.a + str(x["ID"]), FOAF.firstname,Literal(x["NAME"])))
        g.add((foot.a + str(x["ID"]), foot.nick, Literal(x["SHORTNAME"])))
        g.add((foot.a + str(x["ID"]), foot.address, Literal(x["ADDRESS"])))
        g.add((foot.a + str(x["ID"]), foot.website, Literal(x["WEBSITE"])))
        g.add((foot.a + str(x["ID"]), foot.founded, Literal(x["FOUNDED"])))
        g.add((foot.a + str(x["ID"]), foot.clubcolors, Literal(x["CLUBCOLORS"])))
        for p in x["PLAYERS"]:
            g.add((foot.a + str(p["ID"]), foot.jogadorde, Literal(x["NAME"])))
            g.add((foot.a + str(p["ID"]), FOAF.firstname, Literal(p["NAME"])))
            g.add((foot.a + str(p["ID"]), foot.position, Literal(p["POSITION"])))
            g.add((foot.a + str(p["ID"]), foot.nationality, Literal(p["NATIONALITY"])))
            g.add((foot.a + str(p["ID"]), foot.number, Literal(p["NUMBER"])))
            g.add((foot.a + str(p["ID"]), foot.role, Literal(p["ROLE"])))


    #la liga
    g.add((foot.Competition, RDF.type, FOAF.Project))
    g.add((foot.a + str(laLigaData["ID"]), RDF.type, Literal("competition")))
    g.add((foot.a + str(laLigaData["ID"]), DC.description, Literal(laLigaData["DESC"][1])))
    g.add((foot.a + str(laLigaData["ID"]), DC.homepage, Literal(laLigaData["DESC"][2])))
    g.add((foot.a + str(laLigaData["ID"]), FOAF.firstname, Literal(laLigaData["NAME"])))
    g.add((foot.a + str(laLigaData["ID"]), FOAF.nick, Literal(laLigaData["CODE"])))
    g.add((foot.a + str(laLigaData["ID"]), foot.location, Literal(laLigaData["LOCATION"])))
    for x in laLigaData["TEAMS"]:
        g.add((foot.a + str(x["ID"]), RDF.type, Literal("team")))
        g.add((foot.a + str(x["ID"]), foot.timede, Literal(laLigaData["DESC"][0])))
        g.add((foot.a + str(x["ID"]), FOAF.firstname,Literal(x["NAME"])))
        g.add((foot.a + str(x["ID"]), FOAF.nick, Literal(x["SHORTNAME"])))
        g.add((foot.a + str(x["ID"]), foot.address, Literal(x["ADDRESS"])))
        g.add((foot.a + str(x["ID"]), foot.website, Literal(x["WEBSITE"])))
        g.add((foot.a + str(x["ID"]), foot.founded, Literal(x["FOUNDED"])))
        g.add((foot.a + str(x["ID"]), foot.clubcolors, Literal(x["CLUBCOLORS"])))
        for p in x["PLAYERS"]:
            g.add((foot.a + str(p["ID"]), foot.jogadorde, Literal(x["NAME"])))
            g.add((foot.a + str(p["ID"]), FOAF.firstname, Literal(p["NAME"])))
            g.add((foot.a + str(p["ID"]), foot.position, Literal(p["POSITION"])))
            g.add((foot.a + str(p["ID"]), foot.nationality, Literal(p["NATIONALITY"])))
            g.add((foot.a + str(p["ID"]), foot.number, Literal(p["NUMBER"])))
            g.add((foot.a + str(p["ID"]), foot.role, Literal(p["ROLE"])))

    # bundesliga
    g.add((foot.Competition, RDF.type, FOAF.Project))
    g.add((foot.a + str(bundesligaData["ID"]), RDF.type, Literal("competition")))
    g.add((foot.a + str(bundesligaData["ID"]), DC.description, Literal(bundesligaData["DESC"][1])))
    g.add((foot.a + str(bundesligaData["ID"]), DC.homepage, Literal(bundesligaData["DESC"][2])))
    g.add((foot.a + str(bundesligaData["ID"]), FOAF.firstname, Literal(bundesligaData["NAME"])))
    g.add((foot.a + str(bundesligaData["ID"]), FOAF.nick, Literal(bundesligaData["CODE"])))
    g.add((foot.a + str(bundesligaData["ID"]), foot.location, Literal(bundesligaData["LOCATION"])))
    for x in bundesligaData["TEAMS"]:
        g.add((foot.a + str(x["ID"]), RDF.type, Literal("team")))
        g.add((foot.a + str(x["ID"]), foot.timede, Literal(bundesligaData["DESC"][0])))
        g.add((foot.a + str(x["ID"]), FOAF.firstname, Literal(x["NAME"])))
        g.add((foot.a + str(x["ID"]), FOAF.nick, Literal(x["SHORTNAME"])))
        g.add((foot.a + str(x["ID"]), foot.address, Literal(x["ADDRESS"])))
        g.add((foot.a + str(x["ID"]), foot.website, Literal(x["WEBSITE"])))
        g.add((foot.a + str(x["ID"]), foot.founded, Literal(x["FOUNDED"])))
        g.add((foot.a + str(x["ID"]), foot.clubcolors, Literal(x["CLUBCOLORS"])))
        for p in x["PLAYERS"]:
            g.add((foot.a + str(p["ID"]), foot.jogadorde, Literal(x["NAME"])))
            g.add((foot.a + str(p["ID"]), FOAF.firstname, Literal(p["NAME"])))
            g.add((foot.a + str(p["ID"]), foot.position, Literal(p["POSITION"])))
            g.add((foot.a + str(p["ID"]), foot.nationality, Literal(p["NATIONALITY"])))
            g.add((foot.a + str(p["ID"]), foot.number, Literal(p["NUMBER"])))
            g.add((foot.a + str(p["ID"]), foot.role, Literal(p["ROLE"])))


    # ligue 1
    g.add((foot.Competition, RDF.type, FOAF.Project))
    g.add((foot.a + str(ligue1Data["ID"]), RDF.type, Literal("competition")))
    g.add((foot.a + str(ligue1Data["ID"]), DC.description, Literal(ligue1Data["DESC"][1])))
    g.add((foot.a + str(ligue1Data["ID"]), DC.homepage, Literal(ligue1Data["DESC"][2])))
    g.add((foot.a + str(ligue1Data["ID"]), FOAF.firstname, Literal(ligue1Data["NAME"])))
    g.add((foot.a + str(ligue1Data["ID"]), FOAF.nick, Literal(ligue1Data["CODE"])))
    g.add((foot.a + str(ligue1Data["ID"]), foot.location, Literal(ligue1Data["LOCATION"])))
    for x in ligue1Data["TEAMS"]:
        g.add((foot.a + str(x["ID"]), RDF.type, Literal("team")))
        g.add((foot.a + str(x["ID"]), foot.timede, Literal(ligue1Data["DESC"][0])))
        g.add((foot.a + str(x["ID"]), FOAF.firstname, Literal(x["NAME"])))
        g.add((foot.a + str(x["ID"]), FOAF.nick, Literal(x["SHORTNAME"])))
        g.add((foot.a + str(x["ID"]), foot.address, Literal(x["ADDRESS"])))
        g.add((foot.a + str(x["ID"]), foot.website, Literal(x["WEBSITE"])))
        g.add((foot.a + str(x["ID"]), foot.founded, Literal(x["FOUNDED"])))
        g.add((foot.a + str(x["ID"]), foot.clubcolors, Literal(x["CLUBCOLORS"])))
        for p in x["PLAYERS"]:
            g.add((foot.a + str(p["ID"]), foot.jogadorde, Literal(x["NAME"])))
            g.add((foot.a + str(p["ID"]), FOAF.firstname, Literal(p["NAME"])))
            g.add((foot.a + str(p["ID"]), foot.position, Literal(p["POSITION"])))
            g.add((foot.a + str(p["ID"]), foot.nationality, Literal(p["NATIONALITY"])))
            g.add((foot.a + str(p["ID"]), foot.number, Literal(p["NUMBER"])))
            g.add((foot.a + str(p["ID"]), foot.role, Literal(p["ROLE"])))

    # serie A
    g.add((foot.Competition, RDF.type, FOAF.Project))
    g.add((foot.a + str(seriaAData["ID"]), RDF.type, Literal("competition")))
    g.add((foot.a + str(seriaAData["ID"]), DC.description, Literal(seriaAData["DESC"][1])))
    g.add((foot.a + str(seriaAData["ID"]), DC.homepage, Literal(seriaAData["DESC"][2])))
    g.add((foot.a + str(seriaAData["ID"]), FOAF.firstname, Literal(seriaAData["NAME"])))
    g.add((foot.a + str(seriaAData["ID"]), FOAF.nick, Literal(seriaAData["CODE"])))
    g.add((foot.a + str(seriaAData["ID"]), foot.location, Literal(seriaAData["LOCATION"])))
    for x in seriaAData["TEAMS"]:
        g.add((foot.a + str(x["ID"]), RDF.type, Literal("team")))
        g.add((foot.a + str(x["ID"]), foot.timede, Literal(seriaAData["DESC"][0])))
        g.add((foot.a + str(x["ID"]), FOAF.firstname, Literal(x["NAME"])))
        g.add((foot.a + str(x["ID"]), FOAF.nick, Literal(x["SHORTNAME"])))
        g.add((foot.a + str(x["ID"]), foot.address, Literal(x["ADDRESS"])))
        g.add((foot.a + str(x["ID"]), foot.website, Literal(x["WEBSITE"])))
        g.add((foot.a + str(x["ID"]), foot.founded, Literal(x["FOUNDED"])))
        g.add((foot.a + str(x["ID"]), foot.clubcolors, Literal(x["CLUBCOLORS"])))
        for p in x["PLAYERS"]:
            g.add((foot.a + str(p["ID"]), foot.jogadorde, Literal(x["NAME"])))
            g.add((foot.a + str(p["ID"]), FOAF.firstname, Literal(p["NAME"])))
            g.add((foot.a + str(p["ID"]), foot.position, Literal(p["POSITION"])))
            g.add((foot.a + str(p["ID"]), foot.nationality, Literal(p["NATIONALITY"])))
            g.add((foot.a + str(p["ID"]), foot.number, Literal(p["NUMBER"])))
            g.add((foot.a + str(p["ID"]), foot.role, Literal(p["ROLE"])))

    g.bind("dbpedia", dbpedia)
    g.bind("foot", foot)
    g.bind("foaf", FOAF)
    g.bind("dc", DC)

    try:
        g.serialize(destination=f"FootStats.ttl", format="turtle")
        print("\nGraph created successfully!")

    except Exception as e:
        print("\nError, caused by: " + str(e))

def main():
    try:
        urlPrimierLeague = "http://dbpedia.org/data/Premier_League.json"
        idPrimierLeague = "2021"
        titlePrimeirLeague = "Premier_League"
        urlLigue1 = "http://dbpedia.org/data/Ligue_1.json"
        idLigue1 = "2015"
        titleLigue1 = "Ligue_1"
        urlLaLiga = "http://dbpedia.org/data/La_Liga.json"
        idLaLiga = "2014"
        titleLaLiga = "La_Liga"
        urlBundesliga = "http://dbpedia.org/data/Bundesliga.json"
        idBundesliga = "2002"
        titleBundesliga= "Bundesliga"
        urlSerieA = "http://dbpedia.org/data/Serie_A.json"
        idSerieA = "2019"
        titleSerieA = "Serie_A"

# popular descricoes das ligas a partir da dbpedia
        premierLeagueDesc = getLeagueDesc(urlPrimierLeague, titlePrimeirLeague)
        ligue1Desc = getLeagueDesc(urlLigue1, titleLigue1)
        bundesligaDesc = getLeagueDesc(urlBundesliga, titleBundesliga)
        seriaADesc = getLeagueDesc(urlSerieA, titleSerieA)
        laLigaDesc = getLeagueDesc(urlLaLiga, titleLaLiga)


# popular dados das ligas a partir da api
        premierLeagueData = getCompetitionData(idPrimierLeague)
        premierLeagueData["DESC"]= premierLeagueDesc
        ligue1Data = getCompetitionData(idLigue1)
        ligue1Data["DESC"] = ligue1Desc
        bundesligaData = getCompetitionData(idBundesliga)
        bundesligaData["DESC"] = bundesligaDesc
        seriaAData = getCompetitionData(idSerieA)
        seriaAData["DESC"] = seriaADesc
        laLigaData = getCompetitionData(idLaLiga)
        laLigaData["DESC"] = laLigaDesc

        graphGenerator(premierLeagueData, ligue1Data, bundesligaData,seriaAData,laLigaData)
    except Exception as e:
        print("\nError, caused by: " + str(e))


# Iniciando o programa
main()