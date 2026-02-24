# Site Vitrine — Soulcraft

---

## Identite

- **Nom** : Soulcraft
- **Tagline** : "Des logiciels faits sur mesure."
- **Auteur** : Souleymane Diallo
- **Base** : Gatineau, QC — Canada
- **Contact** : diallosouleymanetaka@gmail.com | 514 431 1634

---

## Design System — Palette complete

### Palette principale

| Usage | Couleur | HEX |
|-------|---------|-----|
| Background principal | Noir profond | `#0A0A0B` |
| Surfaces / cards | Gris tres fonce | `#141416` |
| Primaire (liens, accents) | Bleu electrique | `#4F8CFF` |
| CTA principal | Orange vif | `#F59E0B` |
| Succes | Vert | `#10B981` |

### Couleurs secondaires

**Bleu profond structurant :**

| Usage | HEX |
|-------|-----|
| Hover bleu / profondeur | `#2563EB` |
| Fond secondaire bleu | `#1E293B` |

→ Utilise pour : sections alternees, header sticky, hover boutons bleus, elements techniques

**Gris froid moderne :**

| Usage | HEX |
|-------|-----|
| Texte secondaire | `#9CA3AF` |
| Bordures fines | `#2A2A2E` |
| Background alternatif doux | `#1F1F23` |

→ Utilise pour : hierarchie claire, eviter le noir massif, creer du relief subtil

**Accents premium (max 5% du design) :**

| Usage | HEX |
|-------|-----|
| Accent cuivre (sur mesure / artisan) | `#C08457` |
| Accent bleu acier | `#3B82F6` |
| Accent violet technique (IA) | `#7C3AED` |

### Regle d'equilibre

| Part | Couleur |
|------|---------|
| 50% | Noir / surfaces sombres |
| 25% | Gris froid |
| 15% | Bleu electrique |
| 7% | Orange CTA |
| 3% | Vert / accents premium |

### Palette emotionnelle

| Couleur | Ce qu'elle communique |
|---------|----------------------|
| Noir profond | Serieux, controle, maitrise |
| Bleu electrique | Technologie moderne |
| Orange | Action, decision |
| Vert | Validation, fiabilite |
| Gris froid | Structure, maturite |
| Cuivre | Artisanat, sur mesure |
| Violet | IA, innovation technique |

### Gradient IA (ViralFlow, badges "IA powered")
```css
linear-gradient(135deg, #4F8CFF 0%, #7C3AED 100%)
```

### Tokens Tailwind (voir config complete dans la section Stack technique)
```ts
// Utilisation dans les composants :
// bg-background, bg-surface, bg-surface-alt, bg-surface-blue
// text-primary, text-text-secondary
// border-border
// bg-cta hover:bg-cta-hover (boutons orange)
// text-primary hover:text-primary-hover (liens bleus)
// bg-success (badges "En ligne")
// text-accent-copper, text-accent-violet (accents premium)
```

### Typographie

| Usage | Police | Poids |
|-------|--------|-------|
| Titres (H1-H3) | Manrope | Bold (700) |
| Corps de texte | Inter | Regular (400) |
| Labels / badges | Inter | Medium (500) |
| Chiffres animes | Manrope | ExtraBold (800) |

### Effets premium Soulcraft

- Texture noise tres fine sur le background (`opacity: 0.03`)
- Glow bleu subtil derriere les screenshots produits (`box-shadow: 0 0 60px rgba(79, 140, 255, 0.15)`)
- Ombres douces sur les cards (`box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3)`)
- Pas d'ombres Material exagerees

---

## Structure persuasive du site

Framework : **Probleme → Preuve → Promesse → Passage a l'action**

Chaque section repond a une question dans la tete du visiteur.

```
soultaka.com
├── / .......................... Landing persuasive (one-page + sections ancrees)
│   ├── #hero ................. "C'est qui ? Il fait quoi ?"
│   ├── #probleme ............. "Il comprend MON probleme ?"
│   ├── #chiffres ............. "Il est credible ?"
│   ├── #produits ............. "Il a deja fait quoi ?"
│   ├── #methode .............. "Comment il travaille ?"
│   ├── #promesses ............ "Qu'est-ce qu'il me garantit ?"
│   ├── #preuves .............. "D'autres lui font confiance ?"
│   └── #contact .............. "OK, je le contacte."
├── /produits/{slug} .......... Pages detail de chaque produit
├── /a-propos ................. Parcours + philosophie
└── /contact .................. Formulaire complet
```

---

## Page d'accueil `/` — Section par section

---

### Section 1 — HERO `#hero`
> "C'est qui ? Pourquoi je resterais sur cette page ?"

**Fond :** `#0A0A0B` avec texture noise subtile (`opacity: 0.03`)

**Layout :** Centree, grande typographie

**Titre principal (H1) — Manrope Bold, blanc `#FFFFFF` :**
"Votre metier merite un vrai logiciel. Pas un tableur Excel."

- Le mot **"vrai logiciel"** en bleu `#4F8CFF`
- Le mot **"tableur Excel"** barre, en gris `#9CA3AF`

**Sous-titre — Inter Regular, gris `#9CA3AF` :**
"Je conçois des logiciels sur mesure pour les entreprises de terrain — construction, maintenance, services. Vous m'expliquez votre metier, je livre le produit."

**Signature — Inter Medium, gris `#9CA3AF` :**
Souleymane Diallo · Soulcraft · Gatineau, Canada

**2 CTA :**
- Primaire : bouton plein `#F59E0B`, hover `#D97706`, texte noir
  → "Voir ce que j'ai construit" → #produits
- Secondaire : bouton outline bleu `#4F8CFF`, hover fond `#1E293B`
  → "Discuter de votre projet" → #contact

**Visuel :** Mockup flottant des 3 produits avec glow bleu subtil derriere
(`box-shadow: 0 0 80px rgba(79, 140, 255, 0.12)`)

---

### Section 2 — PROBLEME `#probleme`
> "Il comprend ma realite ?"

**Fond :** `#141416`
**Bordure top :** `1px solid #2A2A2E`

**Titre — Manrope Bold, blanc :**
"Vous gerez votre business avec des outils qui n'ont pas ete conçus pour vous."

**3 colonnes — les douleurs :**

Chaque colonne :
- Fond card : `#1F1F23`
- Bordure : `1px solid #2A2A2E`
- Hover : fond `#1E293B`, bordure `#4F8CFF`

| Icone (bleu `#4F8CFF`) | Douleur (blanc) | Detail (gris `#9CA3AF`) |
|-------------------------|-----------------|-------------------------|
| Icone document | **Devis sur Excel** | Vous perdez 2h par devis. Erreurs de calcul, oublis de lignes, mise en page bancale. Vos clients reçoivent un PDF qui ne fait pas pro. |
| Icone localisation | **Equipes sur WhatsApp** | Vos techniciens sont sur le terrain, vous ne savez pas ou ils sont. Les rapports arrivent en retard ou jamais. |
| Icone cible | **Marketing a l'aveugle** | Vous postez du contenu sans savoir ce qui marche. Pas de donnees, pas de methode, pas de resultats previsibles. |

**Transition — Inter, blanc, centree :**
"Ces problemes, je les ai etudies. Et j'ai construit les solutions."

---

### Section 3 — CHIFFRES CLES `#chiffres`
> "C'est du serieux ou c'est un debutant ?"

**Fond :** `#0A0A0B`

**Titre — Manrope Bold, blanc :**
"Ce que les chiffres disent."

**4 blocs en ligne :**

Chaque bloc :
- Chiffre : Manrope ExtraBold (800), taille 4rem, bleu `#4F8CFF`
- Label : Inter Regular, gris `#9CA3AF`
- Animation : compteur qui monte au scroll (0 → valeur)
- Separateur entre blocs : ligne verticale `#2A2A2E`

| Chiffre | Label |
|---------|-------|
| **3** | Produits en production |
| **15 000+** | Lignes de code metier |
| **6** | Technologies maitrisees |
| **4 sem.** | Pour livrer un MVP |

---

### Section 4 — PRODUITS `#produits`
> "Montre-moi ce que tu sais faire."

**Fond :** `#141416`

**Titre — Manrope Bold, blanc :**
"3 logiciels. 3 problemes resolus. En production."

**3 cartes produit :**

Chaque carte :
- Fond : `#1F1F23`
- Bordure : `1px solid #2A2A2E`
- Hover : bordure `#4F8CFF`, translateY(-4px), ombre `0 8px 32px rgba(0,0,0,0.4)`
- Screenshot en haut avec glow bleu subtil

#### Carte 1 — Devis BTP
- **Screenshot** mockup navigateur
- **Probleme** (gris `#9CA3AF`) : "Les artisans perdent 2h par devis sur Excel."
- **Solution** (blanc) : "Dictez vos travaux → l'IA genere un devis PDF pro en 2 minutes."
- **Badge** : pastille `#10B981` + texte "En ligne" en vert
- **Tags** (fond `#1E293B`, texte `#4F8CFF`, border-radius pill) : Angular · FastAPI · GPT-4o · PDF
- **CTA** : lien bleu `#4F8CFF` → /produits/devis-btp

#### Carte 2 — GestionIntervention
- **Probleme :** "Les techniciens sont injoignables, les rapports n'arrivent jamais."
- **Solution :** "Dispatch, suivi GPS temps reel, rapports automatiques depuis le terrain."
- **Tags :** Angular · .NET · SignalR · Leaflet
- **CTA :** → /produits/gestion-intervention

#### Carte 3 — ViralFlow
- **Probleme :** "Creer du contenu viral prend trop de temps sans garantie."
- **Solution :** "Importez une video → score de viralite IA → contenus generes pour chaque plateforme."
- **Tags** (avec gradient IA `#4F8CFF → #7C3AED` sur le badge "IA powered") : Angular · FastAPI · Claude + GPT · Stripe
- **CTA :** → /produits/viralflow

---

### Section 5 — METHODE `#methode`
> "Concretement, comment ça se passe ?"

**Fond :** `#0A0A0B`

**Titre — Manrope Bold, blanc :**
"Du probleme au produit en 4 etapes."

**Timeline verticale :**
- Ligne verticale : `2px solid #2A2A2E`
- Pastille d'etape : cercle `#4F8CFF` (etape active) ou `#2A2A2E` (a venir)
- Numero d'etape : Manrope ExtraBold, bleu `#4F8CFF`
- Chaque etape revele au scroll (fade-in + slide-up)

| # | Titre (blanc) | Detail (gris `#9CA3AF`) | Duree (bleu `#4F8CFF`) |
|---|---------------|-------------------------|------------------------|
| 01 | **Ecouter** | Appel de 30 min. Vous m'expliquez votre metier, vos irritants, ce que vous faites a la main. Je ne parle pas de technologie. | Jour 1 |
| 02 | **Concevoir** | Je vous livre un document clair : ce que le logiciel fera, comment il fonctionnera, combien ça coute. Pas de jargon. | Semaine 1 |
| 03 | **Construire** | Je developpe, vous voyez l'avancement chaque semaine. Vous testez, on ajuste ensemble. | Semaines 2-6 |
| 04 | **Livrer** | Votre logiciel est en ligne, deploye, fonctionnel. Formation equipe + support inclus. | Semaine 6-8 |

**Sous la timeline — Inter, blanc, centree :**
"Pas de cahier des charges de 50 pages. Pas de reunions inutiles. On avance."

---

### Section 6 — PROMESSES `#promesses`
> "Qu'est-ce qu'il me garantit ?"

**Fond :** `#1E293B` (fond bleu fonce — section qui se demarque visuellement)
**Bordure top :** accent cuivre `1px solid rgba(192, 132, 87, 0.3)`

**Titre — Manrope Bold, blanc :**
"Mes engagements. Noir sur blanc."

**4 blocs en grille 2x2 :**

Chaque bloc :
- Fond : `rgba(255, 255, 255, 0.05)` (glassmorphism leger)
- Bordure : `1px solid #2A2A2E`
- Icone : bleu `#4F8CFF` ou vert `#10B981`

| Icone (couleur) | Promesse (blanc) | Detail (gris `#9CA3AF`) |
|-----------------|-----------------|-------------------------|
| Eclair (`#F59E0B`) | **MVP en 4 a 8 semaines** | Pas 6 mois, pas "on verra". Un produit utilisable en moins de 2 mois. |
| Cle (`#4F8CFF`) | **Le code est a vous** | Proprietaire de tout. Code source, base de donnees, hebergement. Zero dependance. |
| Fusee (`#10B981`) | **Deploiement inclus** | Je ne livre pas un zip par email. En ligne, sur votre serveur, avec HTTPS et sauvegardes. |
| Poignee de main (`#C08457`) | **Satisfait ou on corrige** | Si le produit ne correspond pas au plan valide ensemble, je corrige sans frais. |

---

### Section 7 — PREUVES `#preuves`
> "D'autres lui font confiance ?"

**Fond :** `#141416`

**Titre — Manrope Bold, blanc :**
"Preuve par l'action."

**3 blocs horizontaux :**

Chaque bloc :
- Fond : `#1F1F23`
- Bordure gauche : `3px solid` + couleur d'accent

| Bordure | Preuve (blanc) | Detail (gris `#9CA3AF`) |
|---------|---------------|-------------------------|
| Vert `#10B981` | **Devis BTP est en ligne** | Pas une maquette Figma. Un vrai produit, accessible maintenant sur devis-btp.soultaka.com |
| Bleu `#4F8CFF` | **Code visible sur GitHub** | Vous pouvez inspecter la qualite. Rien a cacher. github.com/soultaka19 |
| Cuivre `#C08457` | **3 industries couvertes** | Construction, maintenance, marketing. Des problemes differents, une methode eprouvee. |

**Emplacement temoignages (phase 2) :**
*(Quand disponibles, ajouter ici des cartes citations avec photo, nom, role, entreprise)*

---

### Section 8 — CONTACT `#contact`
> "OK, comment on commence ?"

**Fond :** `#0A0A0B`
**Decoration :** glow orange subtil derriere le formulaire (`box-shadow: 0 0 100px rgba(245, 158, 11, 0.08)`)

**Titre — Manrope Bold, blanc :**
"Vous avez un metier. J'ai la methode."

**Sous-titre — Inter, gris `#9CA3AF` :**
"Appel decouverte de 30 minutes — gratuit, sans engagement."

**Layout :** 2 colonnes (formulaire + infos)

**Colonne gauche — Formulaire :**
- Champs : fond `#141416`, bordure `#2A2A2E`, focus bordure `#4F8CFF`
- Labels : Inter Medium, blanc
- Champs :
  - Nom
  - Email
  - Secteur (select : Construction / Maintenance / Services / Autre)
  - Message ("Decrivez votre probleme en 2 phrases")
- Bouton : plein `#F59E0B`, hover `#D97706`, texte noir, Manrope Bold
  → "Planifier un appel"
- Micro-reassurance (sous le bouton, gris `#9CA3AF`, petite taille) :
  "Reponse sous 24h. Pas de spam, pas de newsletter."

**Colonne droite — Coordonnees :**
- Fond : `#141416`, border-radius, bordure `#2A2A2E`
- Icone email (bleu) + diallosouleymanetaka@gmail.com
- Icone telephone (bleu) + 514 431 1634
- Icone GitHub (bleu) + github.com/soultaka19
- Icone LinkedIn (bleu) + (a ajouter)

---

## Pages secondaires

### `/produits/devis-btp`

**Structure persuasive : Probleme → Solution → Demo → Resultat → CTA**

**1. Hero produit**
- Fond : `#0A0A0B`
- Titre : "Devis BTP" — Manrope Bold, blanc
- Tagline : "Dictez vos travaux. L'IA genere le devis." — Inter, gris `#9CA3AF`
- Screenshot pleine largeur avec glow bleu
- CTA orange : "Essayer en ligne" → devis-btp.soultaka.com
- Badge vert `#10B981` : "En ligne"

**2. Le probleme**
- Fond : `#141416`
- "Un artisan passe en moyenne 2h par devis. Erreurs de calcul, oublis de postes, mise en page approximative. Le client reçoit un PDF qui ne donne pas confiance."

**3. La solution — fonctionnalites**
- Fond : `#0A0A0B`
- Grille de 6 feature cards (fond `#1F1F23`, icone bleu `#4F8CFF`)
- Saisie vocale ou texte en francais
- Parsing IA : unites (m², u, h, forfait), TVA auto
- Generation PDF professionnel en 1 clic
- Gestion clients et historique devis
- Dashboard avec statistiques
- Infos entreprise, assurance, RIB

**4. Le resultat**
- Fond : `#1E293B` (bleu fonce — impact visuel)
- "Un devis professionnel en 2 minutes au lieu de 2 heures."
- Visuel avant/apres : Excel brouillon → PDF propre

**5. Stack technique**
- Fond : `#141416`
- Tags (fond `#1E293B`, texte `#4F8CFF`) : Angular 21 · FastAPI · PostgreSQL · GPT-4o-mini · WeasyPrint · Docker · Caddy

**6. CTA**
- Fond : `#0A0A0B`
- Bouton orange : "Essayer maintenant" → devis-btp.soultaka.com
- Lien bleu : "Me contacter pour un logiciel similaire" → /contact

---

### `/produits/gestion-intervention`

Meme structure, couleurs identiques, contenu adapte :
- **Probleme :** "Vos techniciens sont sur 5 chantiers. Vous gerez par telephone. Les rapports arrivent en retard, incomplets, ou jamais."
- **Solution :** Dispatch intelligent, carte GPS temps reel, rapports terrain, gestion equipements, notifications SignalR
- **Resultat :** "Visibilite totale sur vos operations. Chaque intervention documentee, chaque technicien localise."
- **Stack :** Angular 21 · .NET 10 · SignalR · SQL Server · Leaflet · PrimeNG

---

### `/produits/viralflow`

Meme structure, avec accent violet IA :
- Badge special "IA powered" avec gradient `#4F8CFF → #7C3AED`
- **Probleme :** "Vous produisez du contenu a l'aveugle. Pas de donnees, production lente, impossible de scaler."
- **Solution :** Import video → score viralite IA multi-criteres → generation multi-plateforme (Reels, TikTok, LinkedIn, YouTube)
- **Resultat :** "Du contenu optimise pour chaque plateforme, genere en minutes au lieu d'heures."
- **Stack :** Angular · FastAPI · PostgreSQL · Redis · Celery · Claude + GPT · Stripe · FFmpeg

---

### `/a-propos`

**Fond :** alternance `#0A0A0B` / `#141416`

**Titre — Manrope Bold, blanc :**
"Souleymane Diallo"

**Intro — Inter, gris `#9CA3AF` :**
"Je ne suis pas une agence. Je suis un concepteur de produits. Je travaille seul, en direct avec vous, sans intermediaire. Chaque logiciel que je construis resout un probleme que j'ai etudie sur le terrain."

**Parcours :** (a completer par Souleymane)

**Philosophie — 3 blocs (fond `#1F1F23`, bordure gauche cuivre `#C08457`) :**
1. **"Le meilleur logiciel est celui qu'on ne remarque pas."** — Il fait le travail, simplement. Pas de 200 fonctionnalites. Juste celles dont vous avez besoin.
2. **"Les marches ennuyeux paient mieux que les idees sexy."** — Construction, maintenance, services : des gens qui travaillent, qui ont de l'argent, et qui ont besoin d'outils.
3. **"Livrer bat planifier."** — Un produit imparfait en ligne vaut mieux qu'un produit parfait dans un PowerPoint.

**Competences — grille (fond `#1F1F23`, icone bleu) :**

| Domaine | Technologies |
|---------|-------------|
| Frontend | Angular 21, PrimeNG, Material, Tailwind, SCSS |
| Backend | FastAPI (Python), ASP.NET Core (.NET 10) |
| Donnees | PostgreSQL, SQL Server, Redis |
| IA | OpenAI GPT-4o, Anthropic Claude, function calling |
| Infrastructure | Docker, VPS, Caddy, Cloudflare |
| Temps reel | SignalR, WebSocket |
| Paiement | Stripe |

---

### `/contact`

Meme contenu que #contact de l'accueil, version pleine page avec :

- Formulaire complet (memes styles)
- Carte de localisation Gatineau, QC (style dark `#141416`)
- FAQ rapide (fond `#1F1F23`, bordure `#2A2A2E`) :
  - "Combien coute un MVP ?" → "Entre 3 000$ et 15 000$ selon la complexite. On en parle lors de l'appel."
  - "Vous travaillez avec des clients hors Canada ?" → "Oui. Francais, anglais, a distance."
  - "Je n'ai qu'une idee vague, c'est trop tot ?" → "Non. L'appel decouverte sert exactement a ça."

---

## Harmonisation visuelle — Resume par section

| Section | Fond | Accent principal | Element distinctif |
|---------|------|-----------------|-------------------|
| Hero | `#0A0A0B` + noise | `#4F8CFF` mots cles | Glow bleu derriere mockups |
| Probleme | `#141416` | `#4F8CFF` icones | Cards `#1F1F23` avec hover bleu |
| Chiffres | `#0A0A0B` | `#4F8CFF` chiffres | Compteurs animes |
| Produits | `#141416` | `#10B981` badges | Cards hover avec elevation |
| Methode | `#0A0A0B` | `#4F8CFF` numeros | Timeline verticale |
| Promesses | `#1E293B` | Multi-couleur icones | Fond bleu fonce — rupture visuelle |
| Preuves | `#141416` | Bordure gauche coloree | 3 couleurs d'accent |
| Contact | `#0A0A0B` | `#F59E0B` bouton | Glow orange subtil |

---

## Stack technique du site

| Choix | Justification |
|-------|--------------|
| Next.js 15 (App Router) | SSR/SSG natif pour le SEO, React Server Components, performance optimale |
| Tailwind CSS 4 | Dark mode natif, tokens personnalises, coherent avec shadcn |
| shadcn/ui | Composants accessibles, stylises, copy-paste (pas de dependance lourde) |
| Framer Motion | Animations fluides (compteurs, fade-in, hover) |
| Deploy sur `soultaka.com` | VPS Hetzner via Caddy ou Vercel (gratuit pour sites statiques) |
| Formulaire contact | Resend (API route Next.js) ou EmailJS |
| Analytics | Plausible ou Umami (respect vie privee) |
| Fonts | next/font : Manrope + Inter (optimise, pas de FOUT) |

### Structure Next.js

```
soulcraft/
├── app/
│   ├── layout.tsx ............. Layout global (fonts, metadata, header, footer)
│   ├── page.tsx ............... Accueil (landing persuasive)
│   ├── produits/
│   │   ├── page.tsx ........... Liste produits (optionnel, redirect vers accueil)
│   │   ├── devis-btp/page.tsx
│   │   ├── gestion-intervention/page.tsx
│   │   └── viralflow/page.tsx
│   ├── a-propos/page.tsx
│   ├── contact/page.tsx
│   └── api/
│       └── contact/route.ts ... API route pour le formulaire (Resend)
├── components/
│   ├── ui/ .................... shadcn components (Button, Card, Badge, Input, etc.)
│   ├── sections/ .............. Sections de la landing
│   │   ├── hero.tsx
│   │   ├── problem.tsx
│   │   ├── stats.tsx
│   │   ├── products.tsx
│   │   ├── method.tsx
│   │   ├── promises.tsx
│   │   ├── proof.tsx
│   │   └── contact-section.tsx
│   ├── header.tsx
│   └── footer.tsx
├── lib/
│   └── utils.ts ............... cn() helper (shadcn)
├── tailwind.config.ts ......... Tokens Soulcraft
└── next.config.ts
```

### Composants shadcn utilises

| Composant | Usage |
|-----------|-------|
| `Button` | CTA primaire (orange), secondaire (outline bleu) |
| `Card` | Cartes produits, douleurs, promesses |
| `Badge` | Tags tech, "En ligne", "IA powered" |
| `Input` / `Textarea` | Formulaire contact |
| `Select` | Selecteur de secteur |
| `Separator` | Separation entre sections |
| `Accordion` | FAQ sur la page contact |

### Tailwind config (tokens Soulcraft)

```ts
// tailwind.config.ts
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#0A0A0B",
        surface: "#141416",
        "surface-alt": "#1F1F23",
        "surface-blue": "#1E293B",
        border: "#2A2A2E",
        primary: "#4F8CFF",
        "primary-hover": "#2563EB",
        cta: "#F59E0B",
        "cta-hover": "#D97706",
        success: "#10B981",
        "text-primary": "#FFFFFF",
        "text-secondary": "#9CA3AF",
        "accent-copper": "#C08457",
        "accent-steel": "#3B82F6",
        "accent-violet": "#7C3AED",
      },
      fontFamily: {
        heading: ["var(--font-manrope)", "sans-serif"],
        body: ["var(--font-inter)", "sans-serif"],
      },
      boxShadow: {
        "glow-blue": "0 0 60px rgba(79, 140, 255, 0.15)",
        "glow-orange": "0 0 100px rgba(245, 158, 11, 0.08)",
        "card": "0 4px 24px rgba(0, 0, 0, 0.3)",
        "card-hover": "0 8px 32px rgba(0, 0, 0, 0.4)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
```

---

## SEO & Meta

- **Title** : "Soulcraft — Des logiciels faits sur mesure"
- **Description** : "Souleymane Diallo conçoit des logiciels sur mesure pour la construction, la maintenance et les services. MVP en 4 semaines. Le code est a vous."
- **Keywords** : logiciel sur mesure, SaaS, construction, maintenance, Angular, FastAPI, Gatineau, Canada, MVP
- **OG Image** : Mockup des 3 produits sur fond `#0A0A0B` avec logo Soulcraft
