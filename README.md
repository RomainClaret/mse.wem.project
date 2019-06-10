# mse.wem.project
Web Mining at Master of Engineering (MSE), Switzerland

Auteurs: Romain Claret, Dorian Magnin & Damien Rochat


## Contexte et objectifs du projet

Le site arXiv.org permet d’obtenir des articles numériques en accès libre. Le site a été créé en 1991 dans le but d'echanger des preprints dans le domaine de la physique. Il est aujourd'hui géré par la Cornell University Library et il héberge des preprints, postprints et des articles du domaine publique.

Il y a aujourd'hui **1'519'310 soumissions** dans des champs divers et variés tels que la physique, les mathématiques, l'informatique, la biologie, la finance, les statistiques ou encore l'économie.

Actuellement, arXiv.org propose un champs de recherche avec quelques filtres, ce qu'il n'est pas idéal pour découvrir des articles qui pourraient potentiellement nous intéresser. Le but de ce projet est donc de développer une petite interface qui va permettre de recevoir des recommandation d'articles, en fonction d'un article donné.

Les objects sont :

1. Récupérer et stocker les données de arXiv.org
2. Mettre en place un système de recommandation
3. Classer les articles recommandés
4. Développer une interface simple pour l'utiliser le système de recommandation
5. Afficher des statistiques sur les données depuis l'interface
6. Exécuter les différents services dans une infrastructure Docker

## Données (sources, quantité, pré-traitement, description)

arXiv.org met à disposition une API gratuite permettant de récupérer les articles au format XML. Celle-ci possède les mêmes fonctions que le moteur de recherche du site.

Ci-dessous, la description des différents champs retournés par l'API.

| Champs               | Description                                             |
| -------------------- | ------------------------------------------------------- |
| **title**            | Titre de l'article                                      |
| **id**               | Url de l'article, au format http://arxiv.org/abs/id     |
| published            | Date de première soumission de l'article (version 1)    |
| updated              | Date de soumission de la versiona actuelle de l'article |
| **summary**          | Résumé de l'article                                     |
| **author**           | Nom des différents auteurs de l'article                 |
| **link**             | Liens vers l'article (PDF)                              |
| **category**         | Catégories de l'article (catégories arXiv, ACM et MSC)  |
| **primary_category** | Catégorie arXiv principale de l'article                 |
| affiliation          | Affiliation de l'auteur (université, société, etc.)     |
| journal_ref          | Référence de journal si existant                        |
| doi                  | URL DOI si existant                                     |

Les champs en gras sont ceux qui sont utilisés pour ce projet.

Seuls les articles de la catégorie **Computer Sciences **sont récupérés. Cela représente un total de **180'644 publications**, **194 catégories** et **205'782 auteurs**.

## Planification, répartition du travail
Voici les différentes milestones du projet :

- Créer le crawler pour l'API arXiv.org
- Stocker les données dans un fichier CSV de référence
- Mettre en place le classement par similarité de Neo4j

- Mettre en place le classement avec le modèle LDA
- Mettre en place l'interface graphique

Ci-dessous, la liste des différentes tâches réalisées par chacun des membres du groupe. Il est à noter que certainent tâches ont été réalisées par plusieurs personnes.

Damien :

- Création du fichier CSV de référence
- Mise en place et utilisation de Neo4j

Dorian :

- Mise en place de l'interface graphique 
- Back-end pour gérer les API REST

Romain :

- Crawling de l'API
- Mise en place et utilisation du modèle LDA

## Fonctionnalités / Cas d’utilisation
Une des principales fonctionnalités que permet l’application c’est le faite de pouvoir donné une URL et 
de rechercher les articles qui ressemble à l’article donner par l’URL. 
L’application permet aussi d’avoir des graphiques sur les catégories qui sont liées aux articles remontés. 
Il est aussi possible d'afficher deux autres graphiques. 
Un pour le nombre total d'articles et un autre pour voir qu'elles sont les catégories les plus utilisées



## Techniques, algorithmes et outils

#### Algorithme de recommandation

Le système de recommandation utilise le modèle LDA afin de retourner les N articles les plus similaires en terme de contenu (basé sur le titre et le résumé), ensuite la base de données Neo4j calcule les similarités entre ces articles et celui recherché en comparant leur liens (auteurs et catégories).

##### Modèle LDA

##### Neo4j

Neo4j est une base de données permettant de stocker des données de types graphe. Les publications, les auteurs et les catégories sont stockés comme des sommets. Les liens sont ensuite ajoutés entre chacun d'eux, selon les données reçues.

![neo4j-graph](./images/neo4j-graph.png)

Les liens permettent ensuite de comparer les relations communes entre plusieurs noeuds, avec un algorithme de similarité. C'est l'algorithe de Jaccard qui a été utilisé dans ce cas. Celui-ci va comparer les sommets voisins de plusieurs sommets donnés et produire un résultat représentant la similarité, cette valeur est comprise dans l'intervalle $[0,1]$.

En résumé, plus deux publications auront d'auteurs et de catégories en commun, plus leur similarité sera élevée.

#### Interface utilisateur

Pour la création du site web, nous avons utilisé différentes technologies qui sont suivantes :

- Flask est un Framework pour le web développé en Python et qui permet de mettre en place une gestion des API REST.
- Angular qui est un Framework développé en TypeScript et qui permet de réaliser une interface Web. 
  Ces différents composants ont été utilisé avec Angular : 
  - ng-chartjs permet de réaliser les graphiques.
  - Material qui fournit des composants de conception matérielle pour Angular.
  - Bluma qui est un Framework CSS qui facilite la mise en place de la structure d’un page Web.

#### Infrastructure Docker

Docker a aussi été utilisé pour créer les trois serveurs dont nous avions besoin :

- Un serveur pour Neo4J
- Un serveur pour Flask (partie backend)
- Un serveur pour Angular (partie frontend)

Pour tester l’application avec Docker, il suffit de se rendre à la racine du projet (où se trouve le fichier `docker-compose.yml` et d'exécuter la commande suivante `docker-compose up` qui va créer les images nécessaires.

## Améliorations et prochaines étapes

#### Pondération des relations dans Neo4j

Actuellement, le calcule de similarité entre deux sommets du graphe Neo4j donne la même importance aux auteurs et aux catégories. Une amélioration pourrait être de donner plus de poids à la catégorie principale, aux auteurs et moins de poids aux catégories secondaires.

#### Précalculation des similarité

Neo4j permet de calculer la similarité entre tous les sommets, selon la même fonction qu'actuellement utilisée. Cependant, il s'agit d'une opération très importante. Prendre le temps de précalculer toutes les similarités entre les publications permettrait de gagner du temps lors des requêtes. Il faudra par contre prévoir de calculer les nouvelles similarités lors de la mise à jour du graphe (par exemple lors de l'ajout d'une nouvelle publication).


## Conclusion
L'utilisation de Docker nous a permis de monter en compétence avec cette technologie
La réalisation de chose simple n’est jamais si simple.
La mise en place de l'infrastructure prend toujours plus de temps que prévu.
C'est une fois que tout est en place que nous venons plus productifs. 
Il ne faut donc jamais sous estimer cette partie
