# Projeto-FootStats
Projeto desenvolvido por Vitor Hugo para a disciplina de topicos de informatica.
Este projeto tem como ojetivo coletar informações sobre as 5 principais ligas de futebol do mundo.
Fonte de dados :

http://api.football-data.org/

https://wiki.dbpedia.org/

# Processo de erredeificação
O Rdf final possui 20279 triplas
Foram criados os seguintes vocabularios:

location = País onde a liga é disputada 

timede = fazer o link entre os nos de time e liga

address = endereço do time

website = website do time

founded= ano de fundação do time

clubcolors = cores do time

ID = identificador de cada nó(liga,time e jogador)

jogadorde = link entre os nós de jogador e time

position = posição que o jogador atua

nationality = nacionalidade do jogador

number = numero da camisa do jogador

role = função do jogador



# Vocubularios
Os vocabulários utilizados no projeto são:

O RDF, para definir o RDF.type de cada liga e da definição geral;

FOAF é utilizado para definir os nomes e nick names do rdf e na definição geral, que é do tipo FOAF.Project;

Dublin Core, que é usado para descrições e pagina principal;

Foi criado um vocubulário local foot para definir outros termos, explicado acima.

