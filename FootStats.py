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
            "NAME_COMPETITION": jsonData["name"],
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
                    "NAME_TEAM": team["name"],
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
                            "NAME_PLAYER": squad["name"],
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

# premire league
    g.add((foot.Competition, RDF.type, FOAF.Project))
    g.add((foot.a + str(premierLeagueData["ID"]) + str("CP"), RDF.type, Literal("competition")))
    g.add((foot.a + str(premierLeagueData["ID"]) + str("CP"), DC.description, Literal(premierLeagueData["DESC"][1])))
    g.add((foot.a + str(premierLeagueData["ID"]) + str("CP"), DC.homepage, Literal(premierLeagueData["DESC"][2])))
    g.add((foot.a + str(premierLeagueData["ID"]) + str("CP"), FOAF.firstname, Literal(premierLeagueData["NAME_COMPETITION"])))
    g.add((foot.a + str(premierLeagueData["ID"]) + str("CP"), FOAF.nick, Literal(premierLeagueData["CODE"])))
    g.add((foot.a + str(premierLeagueData["ID"]) + str("CP"), foot.location, Literal(premierLeagueData["LOCATION"])))
    for x in premierLeagueData["TEAMS"]:
        g.add((foot.a + str(x["ID"]) + str("TP"), RDF.type, Literal("team")))
        g.add((foot.a + str(x["ID"]) + str("TP"), foot.timede, Literal(premierLeagueData["DESC"][0])))
        g.add((foot.a + str(x["ID"]) + str("TP"), FOAF.firstname,Literal(x["NAME_TEAM"])))
        g.add((foot.a + str(x["ID"]) + str("TP"), foot.nick, Literal(x["SHORTNAME"])))
        g.add((foot.a + str(x["ID"]) + str("TP"), foot.address, Literal(x["ADDRESS"])))
        g.add((foot.a + str(x["ID"]) + str("TP"), foot.website, Literal(x["WEBSITE"])))
        g.add((foot.a + str(x["ID"]) + str("TP"), foot.founded, Literal(x["FOUNDED"])))
        g.add((foot.a + str(x["ID"]) + str("TP"), foot.clubcolors, Literal(x["CLUBCOLORS"])))
        for p in x["PLAYERS"]:
            g.add((foot.a + str(p["ID"]) + str("JP"), foot.jogadorde, Literal(x["NAME_TEAM"])))
            g.add((foot.a + str(p["ID"]) + str("JP"), FOAF.firstname, Literal(p["NAME_PLAYER"])))
            g.add((foot.a + str(p["ID"]) + str("JP"), foot.position, Literal(p["POSITION"])))
            g.add((foot.a + str(p["ID"]) + str("JP"), foot.nationality, Literal(p["NATIONALITY"])))
            g.add((foot.a + str(p["ID"]) + str("JP"), foot.number, Literal(p["NUMBER"])))
            g.add((foot.a + str(p["ID"]) + str("JP"), foot.role, Literal(p["ROLE"])))



    mountLaLiga(foot, g, laLigaData)

    mountBundesliga(bundesligaData, foot, g)

    mountLigue1(foot, g, ligue1Data)

    mountSerieA(foot, g, seriaAData)


    g.bind("foot", foot)
    g.bind("foaf", FOAF)
    g.bind("dc", DC)

    try:
        g.serialize(destination=f"FootStats.ttl", format="turtle")
        print("\nGraph created successfully!")

    except Exception as e:
        print("\nError, caused by: " + str(e))


def mountSerieA(foot, g, seriaAData):
    # serie A
    g.add((foot.Competition, RDF.type, FOAF.Project))
    g.add((foot.a + str(seriaAData["ID"]) + str("CS"), RDF.type, Literal("competition")))
    g.add((foot.a + str(seriaAData["ID"]) + str("CS"), DC.description, Literal(seriaAData["DESC"][1])))
    g.add((foot.a + str(seriaAData["ID"]) + str("CS"), DC.homepage, Literal(seriaAData["DESC"][2])))
    g.add((foot.a + str(seriaAData["ID"]) + str("CS"), FOAF.firstname, Literal(seriaAData["NAME_COMPETITION"])))
    g.add((foot.a + str(seriaAData["ID"])+ str("CS"), FOAF.nick, Literal(seriaAData["CODE"])))
    g.add((foot.a + str(seriaAData["ID"]) + str("CS"), foot.location, Literal(seriaAData["LOCATION"])))
    for x in seriaAData["TEAMS"]:
        g.add((foot.a + str(x["ID"]) + str("TS"), RDF.type, Literal("team")))
        g.add((foot.a + str(x["ID"]) + str("TS"), foot.timede, Literal(seriaAData["DESC"][0])))
        g.add((foot.a + str(x["ID"]) + str("TS"), FOAF.firstname, Literal(x["NAME_TEAM"])))
        g.add((foot.a + str(x["ID"]) + str("TS"), FOAF.nick, Literal(x["SHORTNAME"])))
        g.add((foot.a + str(x["ID"]) + str("TS"), foot.address, Literal(x["ADDRESS"])))
        g.add((foot.a + str(x["ID"]) + str("TS"), foot.website, Literal(x["WEBSITE"])))
        g.add((foot.a + str(x["ID"]) + str("TS"), foot.founded, Literal(x["FOUNDED"])))
        g.add((foot.a + str(x["ID"]) + str("TS"), foot.clubcolors, Literal(x["CLUBCOLORS"])))
        for p in x["PLAYERS"]:
            g.add((foot.a + str(p["ID"]) + str("PS"), foot.jogadorde, Literal(x["NAME_TEAM"])))
            g.add((foot.a + str(p["ID"]) + str("PS"), FOAF.firstname, Literal(p["NAME_PLAYER"])))
            g.add((foot.a + str(p["ID"]) + str("PS"), foot.position, Literal(p["POSITION"])))
            g.add((foot.a + str(p["ID"]) + str("PS"), foot.nationality, Literal(p["NATIONALITY"])))
            g.add((foot.a + str(p["ID"]) + str("PS"), foot.number, Literal(p["NUMBER"])))
            g.add((foot.a + str(p["ID"]) + str("PS"), foot.role, Literal(p["ROLE"])))


def mountBundesliga(bundesligaData, foot, g):
    # bundesliga
    g.add((foot.Competition, RDF.type, FOAF.Project))
    g.add((foot.a + str(bundesligaData["ID"]) + str("CB"), RDF.type, Literal("competition")))
    g.add((foot.a + str(bundesligaData["ID"]) + str("CB"), DC.description, Literal(bundesligaData["DESC"][1])))
    g.add((foot.a + str(bundesligaData["ID"]) + str("CB"), DC.homepage, Literal(bundesligaData["DESC"][2])))
    g.add((foot.a + str(bundesligaData["ID"]) + str("CB"), FOAF.firstname, Literal(bundesligaData["NAME_COMPETITION"])))
    g.add((foot.a + str(bundesligaData["ID"]) + str("CB"), FOAF.nick, Literal(bundesligaData["CODE"])))
    g.add((foot.a + str(bundesligaData["ID"]) + str("CB"), foot.location, Literal(bundesligaData["LOCATION"])))
    for x in bundesligaData["TEAMS"]:
        g.add((foot.a + str(x["ID"]) + str("TB"), RDF.type, Literal("team")))
        g.add((foot.a + str(x["ID"]) + str("TB"), foot.timede, Literal(bundesligaData["DESC"][0])))
        g.add((foot.a + str(x["ID"]) + str("TB"), FOAF.firstname, Literal(x["NAME_TEAM"])))
        g.add((foot.a + str(x["ID"]) + str("TB"), FOAF.nick, Literal(x["SHORTNAME"])))
        g.add((foot.a + str(x["ID"]) + str("TB"), foot.address, Literal(x["ADDRESS"])))
        g.add((foot.a + str(x["ID"]) + str("TB"), foot.website, Literal(x["WEBSITE"])))
        g.add((foot.a + str(x["ID"]) + str("TB"), foot.founded, Literal(x["FOUNDED"])))
        g.add((foot.a + str(x["ID"]) + str("TB"), foot.clubcolors, Literal(x["CLUBCOLORS"])))
        for p in x["PLAYERS"]:
            g.add((foot.a + str(p["ID"]) + str("PB"), foot.jogadorde, Literal(x["NAME_TEAM"])))
            g.add((foot.a + str(p["ID"]) + str("PB"), FOAF.firstname, Literal(p["NAME_PLAYER"])))
            g.add((foot.a + str(p["ID"]) + str("PB"), foot.position, Literal(p["POSITION"])))
            g.add((foot.a + str(p["ID"]) + str("PB"), foot.nationality, Literal(p["NATIONALITY"])))
            g.add((foot.a + str(p["ID"]) + str("PB"), foot.number, Literal(p["NUMBER"])))
            g.add((foot.a + str(p["ID"]) + str("PB"), foot.role, Literal(p["ROLE"])))


def mountLigue1(foot, g, ligue1Data):
    # ligue 1
    g.add((foot.Competition, RDF.type, FOAF.Project))
    g.add((foot.a + str(ligue1Data["ID"]) + str("CL1"), RDF.type, Literal("competition")))
    g.add((foot.a + str(ligue1Data["ID"]) + str("CL1"), DC.description, Literal(ligue1Data["DESC"][1])))
    g.add((foot.a + str(ligue1Data["ID"]) + str("CL1"), DC.homepage, Literal(ligue1Data["DESC"][2])))
    g.add((foot.a + str(ligue1Data["ID"]) + str("CL1"), FOAF.firstname, Literal(ligue1Data["NAME_COMPETITION"])))
    g.add((foot.a + str(ligue1Data["ID"]) + str("CL1"), FOAF.nick, Literal(ligue1Data["CODE"])))
    g.add((foot.a + str(ligue1Data["ID"]) + str("CL1"), foot.location, Literal(ligue1Data["LOCATION"])))
    for x in ligue1Data["TEAMS"]:
        g.add((foot.a + str(x["ID"]) + str("TL1"), RDF.type, Literal("team")))
        g.add((foot.a + str(x["ID"]) + str("TL1"), foot.timede, Literal(ligue1Data["DESC"][0])))
        g.add((foot.a + str(x["ID"]) + str("TL1"), FOAF.firstname, Literal(x["NAME_TEAM"])))
        g.add((foot.a + str(x["ID"]) + str("TL1"), FOAF.nick, Literal(x["SHORTNAME"])))
        g.add((foot.a + str(x["ID"]) + str("TL1"), foot.address, Literal(x["ADDRESS"])))
        g.add((foot.a + str(x["ID"]) + str("TL1"), foot.website, Literal(x["WEBSITE"])))
        g.add((foot.a + str(x["ID"]) + str("TL1"), foot.founded, Literal(x["FOUNDED"])))
        g.add((foot.a + str(x["ID"]) + str("TL1"), foot.clubcolors, Literal(x["CLUBCOLORS"])))
        for p in x["PLAYERS"]:
            g.add((foot.a + str(p["ID"]) + str("PL1"), foot.jogadorde, Literal(x["NAME_TEAM"])))
            g.add((foot.a + str(p["ID"]) + str("PL1"), FOAF.firstname, Literal(p["NAME_PLAYER"])))
            g.add((foot.a + str(p["ID"]) + str("PL1"), foot.position, Literal(p["POSITION"])))
            g.add((foot.a + str(p["ID"]) + str("PL1"), foot.nationality, Literal(p["NATIONALITY"])))
            g.add((foot.a + str(p["ID"]) + str("PL1"), foot.number, Literal(p["NUMBER"])))
            g.add((foot.a + str(p["ID"]) + str("PL1"), foot.role, Literal(p["ROLE"])))


def mountLaLiga(foot, g, laLigaData):
    # la liga
    g.add((foot.Competition, RDF.type, FOAF.Project))
    g.add((foot.a + str(laLigaData["ID"]) + str("CLL"), RDF.type, Literal("competition")))
    g.add((foot.a + str(laLigaData["ID"]) + str("CLL"), DC.description, Literal(laLigaData["DESC"][1])))
    g.add((foot.a + str(laLigaData["ID"])+ str("CLL"), DC.homepage, Literal(laLigaData["DESC"][2])))
    g.add((foot.a + str(laLigaData["ID"])+ str("CLL"), FOAF.firstname, Literal(laLigaData["NAME_COMPETITION"])))
    g.add((foot.a + str(laLigaData["ID"])+ str("CLL"), FOAF.nick, Literal(laLigaData["CODE"])))
    g.add((foot.a + str(laLigaData["ID"])+ str("CLL"), foot.location, Literal(laLigaData["LOCATION"])))
    for x in laLigaData["TEAMS"]:
        g.add((foot.a + str(x["ID"]) + str("TLL"), RDF.type, Literal("team")))
        g.add((foot.a + str(x["ID"]) + str("TLL"), foot.timede, Literal(laLigaData["DESC"][0])))
        g.add((foot.a + str(x["ID"]) + str("TLL"), FOAF.firstname, Literal(x["NAME_TEAM"])))
        g.add((foot.a + str(x["ID"]) + str("TLL"), FOAF.nick, Literal(x["SHORTNAME"])))
        g.add((foot.a + str(x["ID"]) + str("TLL"), foot.address, Literal(x["ADDRESS"])))
        g.add((foot.a + str(x["ID"]) + str("TLL"), foot.website, Literal(x["WEBSITE"])))
        g.add((foot.a + str(x["ID"]) + str("TLL"), foot.founded, Literal(x["FOUNDED"])))
        g.add((foot.a + str(x["ID"]) + str("TLL"), foot.clubcolors, Literal(x["CLUBCOLORS"])))
        for p in x["PLAYERS"]:
            g.add((foot.a + str(p["ID"]) + str("JLL"), foot.jogadorde, Literal(x["NAME_TEAM"])))
            g.add((foot.a + str(p["ID"]) + str("JLL"), FOAF.firstname, Literal(p["NAME_PLAYER"])))
            g.add((foot.a + str(p["ID"]) + str("JLL"), foot.position, Literal(p["POSITION"])))
            g.add((foot.a + str(p["ID"]) + str("JLL"), foot.nationality, Literal(p["NATIONALITY"])))
            g.add((foot.a + str(p["ID"]) + str("JLL"), foot.number, Literal(p["NUMBER"])))
            g.add((foot.a + str(p["ID"]) + str("JLL"), foot.role, Literal(p["ROLE"])))


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