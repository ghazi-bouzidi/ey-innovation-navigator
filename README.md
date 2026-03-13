# Innovation Navigator

A comprehensive innovation management platform for EY consultants to guide client engagements through an 8-stage innovation journey, with AI-powered service recommendations and team collaboration features.

## Overview

Innovation Navigator helps EY teams:
- Manage client innovation projects across 8 structured stages
- Get personalized service recommendations based on client context
- Track team assignments and service engagement
- Navigate a comprehensive catalog of innovation services, frameworks, tools, and assets

## Features

### 🎯 Client & Project Management
- Multi-client portfolio management
- Project tracking with current stage indicators
- Rich client profiling (industry, region, digital maturity)
- Stakeholder and notes management

### 🚀 8-Stage Innovation Journey
1. **Kick-off & Cadrage** - Scope and setup
2. **Diagnostic & Discovery** - Assessment and insights
3. **Co-création & Idéation** - Collaborative ideation
4. **Priorisation Stratégique** - Strategic prioritization
5. **Restitution & Feuille de Route** - Roadmap delivery
6. **Livrables Client** - Final deliverables
7. **Formation & Transfert** - Training and handoff
8. **Clôture & Continuité** - Closure and follow-on

### 🤖 AI-Powered Recommendations
- Context-aware service recommendations per stage
- Tag-based matching with client pain points and goals
- Industry-specific filtering
- Cross-project knowledge boost
- Team member suggestions with availability

### 📚 Innovation Catalog
- **17 consolidated services** across Strategy, Design, Brand, Immersive, and Delivery
- **6 frameworks** (Value Proposition Canvas, Service Blueprint, Double Diamond, etc.)
- **4 tools** (Figma, Adobe Creative Suite, Factory.AI)
- **2 proprietary assets** (NEXUS Digital, Transfopoly)

### 👥 Team Management
- Real team member profiles with expertise areas
- Automatic team assignment based on service type
- Availability tracking

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3 (Inter typography), Vanilla JavaScript
- **Data**: JSON file-based storage
- **Deployment**: Standalone Flask server

## Installation

### Prerequisites
- Python 3.9+

### Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/ey-innovation-navigator.git
cd ey-innovation-navigator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create the clients data directory:
```bash
mkdir -p data/clients
```

4. Run the application:
```bash
python app.py
```

5. Open your browser to `http://localhost:5001`

## Project Structure

```
ey-innovation-navigator/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── data/
│   ├── catalog.json       # Innovation services catalog
│   ├── stages.json        # 8 journey stages
│   ├── team.json          # Team member profiles
│   └── clients/           # Client data (gitignored)
├── engine/
│   └── recommender.py     # Recommendation engine
├── static/
│   ├── css/
│   │   └── style.css      # Modern minimal styling
│   ├── js/
│   │   └── app.js         # Client-side interactions
│   └── EY Logo.svg        # Brand assets
└── templates/             # Jinja2 templates
    ├── base.html
    ├── dashboard.html
    ├── client_*.html
    ├── project_*.html
    └── catalog.html
```

## Usage

### Creating a Client
1. Navigate to Dashboard
2. Click "+ Nouveau Client"
3. Fill in client details (sector, region, digital maturity, background)
4. Save

### Creating a Project
1. Open a client profile
2. Click "+ Nouveau Projet"
3. Define project name, description, pain points, and goals
4. Add stakeholders and notes
5. Save

### Navigating the Journey
- Click on any stage in the journey pipeline to view recommendations
- Each stage shows:
  - Typical activities
  - Innovation focus
  - Personalized service recommendations with team assignments
- Use "Engager", "Favori", or "Écarter" to track service status
- Click "Avancer à l'étape suivante" to progress through stages

### Browsing the Catalog
- Visit "Catalogue Innovation" from the navigation
- Filter by Type (Service/Framework/Tool/Asset) or Stage
- View all 29 innovation offerings with team assignments

## Team

- **Ghazi Bouzidi** - Responsable Product & Service Innovation
- **Nayrouz Ben Cheikh Ahmed** - Responsable Stratégie Expérience
- **Imad Benhamou** - Responsable Design UX/UI
- **Sarah Ben Khlifa** - Responsable Stratégie Marketing
- **Sarah Manoubi** - Spécialiste Facilitation Immersive
- **Mustapha Ayari** - Spécialiste Immersif & Prototypage Rapide

## Contributing

This is an internal EY project. For contributions or questions, please contact the project maintainers.

## License

© 2026 EY. All rights reserved.

## Acknowledgments

Built with modern web standards and the Inter typography system for a clean, professional experience.
