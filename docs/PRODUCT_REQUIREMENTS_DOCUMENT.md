📄 PRODUCT REQUIREMENTS DOCUMENT

Produit : Application de génération de devis par commande vocale pour artisans BTP

🎯 Vision & Objectif Produit

Permettre aux artisans du BTP de générer un devis professionnel complet en moins d’une minute, directement depuis leur smartphone ou ordinateur, via commande vocale ou texte, avec une mise en page instantanée et personnalisée à leur entreprise.

Objectifs principaux :

Réduire le temps administratif de 80%

Accélérer l’envoi des devis

Améliorer le taux de signature

Professionnaliser l’image de l’artisan

👤 Persona Cible
👨‍🔧 Thomas – Artisan plombier indépendant (38 ans)

1 à 3 salariés

8 à 12 devis/semaine

Travaille principalement sur chantier

Fait ses devis le soir

Utilise Excel / Word

Peu structuré sur l’administratif

Motivations

Gagner du temps

Envoyer plus vite ses devis

Paraître plus professionnel

Éviter les erreurs de calcul

Freins

Peur des outils complexes

Manque de temps pour paramétrer

Sensibilité au prix

💥 Problème
Aujourd’hui :

Prise de notes manuelle

Re-saisie le soir

Calcul TVA et totaux

Copie des mentions légales

Export PDF

Envoi par email

⏱ 20 à 40 minutes par devis
📉 Charge mentale
📉 Risque d’erreurs
📉 Retards d’envoi → perte de clients

💡 Solution

Une application web/mobile permettant :

Dictée vocale intelligente

Structuration automatique des lignes

Calcul automatique TVA & totaux

Prévisualisation en temps réel

Génération PDF professionnel personnalisé

Promesse produit :

“Parlez. Votre devis est prêt.”

1️⃣ Génération intelligente de devis (MVP)

🎙 Commande vocale

⌨️ Saisie texte

🧠 Extraction automatique :

Matériel

Main d’œuvre

Quantité

Prix unitaire

TVA

📊 Calcul automatique :

Sous-total

TVA

Total TTC

📄 Génération PDF

2️⃣ Prévisualisation en direct (Live Preview)

Interface en deux colonnes :

Gauche :

Saisie vocale / texte

Édition rapide des lignes

Droite :

Prévisualisation en temps réel du devis

Mise à jour automatique des totaux

Rendu professionnel type PDF

Effet attendu :

Les lignes apparaissent au fur et à mesure

Les totaux se recalculent instantanément

L’utilisateur visualise immédiatement le résultat final

3️⃣ Paramétrage Entreprise (NOUVELLE FONCTIONNALITÉ)

Section “Paramètres” accessible depuis le dashboard.

🏢 Informations entreprise

Logo (upload image)

Nom de l’entreprise

Adresse complète

Téléphone

Email

SIRET / N° TVA

🏦 Informations bancaires

Nom de la banque

IBAN

BIC

Titulaire du compte

Affichage automatique dans le bas du devis.

🛡 Assurance

Nom de l’assureur

Numéro de police

Type de couverture

Date de validité

Mention intégrée automatiquement dans le devis.

📜 Conditions générales

Bloc texte personnalisable

Conditions de paiement (ex : 30% acompte)

Délais d’exécution

Pénalités de retard

Clause de validité du devis

Ces informations sont :

Injectées automatiquement dans chaque devis

Modifiables manuellement au besoin

4️⃣ Historique & gestion

Sauvegarde automatique des brouillons

Historique des devis

Duplication d’un devis existant

🧠 Parcours utilisateur
Première utilisation

Création du compte

Paramétrage entreprise (logo, banque, assurance, conditions)

Sauvegarde

Création d’un devis

Clique “Nouveau devis”

Écran 2 colonnes s’affiche

Dictée ou saisie texte

L’IA structure automatiquement

La preview à droite s’actualise en direct

Vérification rapide

Clique “Générer PDF”

Envoi par email / WhatsApp

⏱ Temps cible : < 60 secondes

🖥 Frontend : Angular
Architecture UI

Écran principal en 2 colonnes :

Colonne gauche	Colonne droite
Input vocal / texte	Preview devis live
Édition lignes	Rendu HTML stylisé
Paramètres TVA	Totaux dynamiques

🐍 Backend : FastAPI (Python)

🔄 Communication temps réel

Option recommandée : WebSocket

Envoi des modifications incrémentales

Retour du quote_draft structuré

Mise à jour immédiate de la preview

📊 Indicateurs de succès (KPIs)
Produit

Temps moyen de création

% devis < 1 minute

Nombre moyen de devis / semaine

Business

Taux de conversion devis → facture

Rétention à 30 jours

Taux d’activation (paramétrage complété)

Marketing

Taux de complétion vidéo démo

Leads générés

Coût d’acquisition


🏗️ Structure du Projet (Core / Features / Shared + Environment)

L'application suit une structure modulaire stricte pour optimiser le lazy-loading et l’isolation des responsabilités.
structure du projet angular src/
├── environment/                # Variables d'environnement
│   ├── environment.ts          # Développement
│   └── environment.prod.ts     # Production
│
├── app/
│   ├── core/                   # Importé UNE SEULE fois
│   │   ├── api/                # Client HTTP, base URL, helpers
│   │   ├── auth/               # Guards, interceptors, auth
│   │   └── realtime/           # WebSocket / SSE (live parsing)
│   │
│   ├── features/
│   │   ├── quote/
│   │   │   ├── components/
│   │   │   │   ├── compose/
│   │   │   │   ├── input/
│   │   │   │   ├── editor/
│   │   │   │   └── preview/
│   │   │   ├── models/
│   │   │   ├── services/
│   │   │   └── state/
│   │   │
│   │   ├── company/
│   │   │   ├── components/
│   │   │   │   ├── settings/
│   │   │   │   ├── banking/
│   │   │   │   ├── insurance/
│   │   │   │   └── terms/
│   │   │   ├── models/
│   │   │   ├── services/
│   │   │   └── state/
│   │   │
│   │   └── dashboard/
│   │       ├── components/
│   │       ├── models/
│   │       └── services/
│   │
│   └── shared/
│       ├── ui/
│       ├── pipes/
│       ├── directives/
│       └── utils/


📏 Nomenclature & Style de Code
🚫 Suppression des suffixes

Contrairement aux conventions Angular classiques, nous n’utilisons pas de suffixes dans les noms de classes et de fichiers.

❌ Mauvais : ListClientComponent dans list-client.component.ts
✅ Bon : ListClient dans list-client.ts

Exemples projet :

✅ QuoteCompose dans quote-compose.ts

✅ QuoteData dans quote-data.ts

✅ QuoteStore dans quote-store.ts

✅ CompanySettingsForm dans company-settings-form.ts

Les fichiers .html et .scss suivent le nom du composant, sans suffixe.

🔧 Linting

Le projet utilise ESLint pour garantir la qualité du code.

Commande :

ng add angular-eslint


Règles attendues :

code formaté et cohérent

pas de any sauf cas justifié

méthodes courtes et lisibles

components de taille raisonnable (si un composant grossit → découpage)

🧩 Architecture des Composants (Smart & Dumb)

Nous utilisons le pattern Smart-Container / Dumb-Presenter.

1) 🧠 Smart Components (Containers)

Composants “cerveaux” responsables de la logique métier.

Responsabilités :

Injecter les services

Gérer les appels API / WS

Gérer la navigation

Orchestrer le state via store Signals

Contraintes :

🚫 Pas de input() / output()

HTML minimal (composition de presenters)

Pas de logique d’affichage complexe

Si un fichier dépasse une taille raisonnable → découper

Exemples :

QuoteCompose

CompanySettings

DashboardHome

2) 🎨 Dumb Components (Presenters)

Composants “visuels” dédiés à l’affichage.

Responsabilités :

Afficher les données via input()

Émettre des événements via output()

Contraintes :

🚫 Aucune injection de service

Aucune logique métier

Réutilisables et testables

Exemples projet :

QuoteInputPanel

LineItemsEditor

QuotePreview

CompanyInfoForm

BankingForm

InsuranceForm

TermsForm

🧠 Standards de Développement (Instructions d’implémentation)
✅ Signals obligatoires

Utiliser les Angular Signals pour l’état local et la réactivité :

signal

computed

effect

➡️ Les stores des features (features/*/state/) sont la source de vérité.

✅ Control Flow Angular 17+

Utiliser la nouvelle syntaxe :

@if

@for

@switch

✅ Data Access

Les services features/*/services/ doivent retourner :

Observable ou

Signal (si conversion faite côté store)

Règle :

Les presenters ne consomment jamais directement les services.

Seuls les Smart / Stores consomment les services.

⚡ Temps réel : Live Preview obligatoire (Quote)

Le devis doit se prévisualiser en direct à droite.

Communication recommandée

✅ WebSocket (FastAPI) via core/realtime/

Fallback : HTTP + debounce (si nécessaire)

Règles UI

La preview doit réagir instantanément aux updates du draftQuote.

Afficher un état :

parsing

ready

warning

error