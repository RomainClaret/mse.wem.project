# mse.wem.project
Semester Project - Web Mining at Master of Engineering (MSE), Switzerland


## Contexte et objectifs du projet

Le but du projet est d’aller chercher des données sur le site arXiv.org qui a été créé en 1991 et qui a évolué au fil du temps. Car il a été déplacé en 2001 à l’université de Cornell. Ce site permet ’obtenir des archives numériques en accès libre et il fournit une API qui permet d’obtenir ces données.
Le but principal c’est de pouvoir recherche des articles qui sont similaires à un autre article. Pour réaliser ce but, nous avons défini des objectifs qui sont les suivants :
1. Aller chercher les données et les sauvegarder
2. Réussir à trouver des articles similaires.
3. Réaliser une interface utilisateur pour la recherche d’article similaire
4. Utiliser Docker pour faire tourner tous les serveurs que l’on a besoin.


## Données (sources, quantité, évtl. pré-traitement, description)

## Planification, répartition du travail
Pour la réparation du travail, nous avons essentiellement partagé ce projet en trois et avancé parallèlement.
* Une partie a consisté à aller chercher les données sur le site et de créer un fichier csv qui contient les données trouvées. 
* Une autre partie à consister à utiliser Neo4J pour travailler ces données et de pouvoir réaliser certaines statistiques et permettre de pouvoir répondre rechercher des articles similaires. 
*Pour la troisième partie, il s’agissait de réaliser un site internet qui permet de rechercher et afficher ces articles. Il a aussi été choisi de pouvoir afficher des statistiques sur les catégories des articles. Pour que ce site fonctionne il a aussi fallu mettre en place docker.


## Fonctionnalités / cas d’utilisation

## Techniques, algorithmes et outils utilisés (aussi en lien avec votre exposé)

Pour la création du site web, nous avons utilisé les différentes technologies :
* Flask qui un Framework développé en Python et qui permet de mettre en place une gestion des API REST
* Angular qui est un Framework développé en typeScript et permet de réaliser une interface web. Ces différents composants ont été utilisé avec Angular : 
  * ng-chartjs permet de réaliser les graphiques
  * Material qui fournit des composants de conception matérielle pour Angular  
  * Bluma qui est un Framework CSS qui facilite la mise en place de la structure d’un page web


## Conclusion
