import json
import uuid
import os
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename

from flask import Flask, render_template, request, redirect, url_for, jsonify

from engine.recommender import get_recommendations

app = Flask(__name__)

DATA_DIR = Path(__file__).resolve().parent / "data"
CLIENTS_DIR = DATA_DIR / "clients"
CLIENTS_DIR.mkdir(parents=True, exist_ok=True)

UPLOAD_FOLDER = Path(__file__).resolve().parent / "static" / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_image(file):
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
        try:
            file.save(UPLOAD_FOLDER / unique_filename)
            return unique_filename
        except OSError:
            return None
    return None


def load_json(filename):
    with open(DATA_DIR / filename, "r") as f:
        return json.load(f)


def load_client(client_id):
    path = CLIENTS_DIR / f"{client_id}.json"
    if not path.exists():
        return None
    with open(path, "r") as f:
        return json.load(f)


def save_client(client):
    """Vercel uses a read-only filesystem. For the demo, we only 'save' in memory for the current session if needed, 
    but for true persistence on Vercel, you'd need a database like MongoDB or PostgreSQL."""
    path = CLIENTS_DIR / f"{client['id']}.json"
    try:
        with open(path, "w") as f:
            json.dump(client, f, indent=2)
    except OSError:
        # Silently fail on read-only filesystems (Vercel)
        pass


def list_clients():
    clients = []
    # Search both standard and hidden filenames for the demo
    for p in sorted(CLIENTS_DIR.glob("*.json")):
        try:
            with open(p, "r") as f:
                clients.append(json.load(f))
        except:
            continue
    return clients


def get_project(client, project_id):
    for proj in client.get("projects", []):
        if proj["id"] == project_id:
            return proj
    return None


def new_client_template():
    return {
        "id": str(uuid.uuid4())[:8],
        "name": "",
        "industry": "",
        "size": "",
        "region": "",
        "digital_maturity": 1,
        "client_background": "",
        "image": "",
        "projects": [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }


def new_project_template():
    return {
        "id": str(uuid.uuid4())[:8],
        "name": "",
        "description": "",
        "current_stage": 1,
        "pain_points": [],
        "goals": [],
        "stakeholders": [],
        "notes": [],
        "suggestions_state": {},
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }


def _parse_stakeholders(form):
    names = form.getlist("sh_name")
    roles = form.getlist("sh_role")
    priorities = form.getlist("sh_priorities")
    stakeholders = []
    for i, name in enumerate(names):
        name = name.strip()
        if name:
            stakeholders.append({
                "name": name,
                "role": roles[i].strip() if i < len(roles) else "",
                "priorities": priorities[i].strip() if i < len(priorities) else ""
            })
    return stakeholders


def _parse_notes(form):
    notes = []
    existing_texts = form.getlist("existing_note_text")
    existing_ts = form.getlist("existing_note_ts")
    for i, text in enumerate(existing_texts):
        if text.strip():
            notes.append({
                "text": text.strip(),
                "timestamp": existing_ts[i] if i < len(existing_ts) else datetime.now().isoformat()
            })
    new_note = form.get("new_note", "").strip()
    if new_note:
        notes.insert(0, {
            "text": new_note,
            "timestamp": datetime.now().isoformat()
        })
    return notes


# -- Client Routes --

@app.route("/")
def dashboard():
    clients = list_clients()
    return render_template("dashboard.html", clients=clients)


@app.route("/client/new", methods=["GET", "POST"])
def new_client():
    if request.method == "POST":
        client = new_client_template()
        client["name"] = request.form.get("name", "").strip()
        client["industry"] = request.form.get("industry", "").strip()
        client["size"] = request.form.get("size", "").strip()
        client["region"] = request.form.get("region", "").strip()
        client["digital_maturity"] = int(request.form.get("digital_maturity", 1))
        client["client_background"] = request.form.get("client_background", "").strip()
        
        # Handle image upload
        if 'image' in request.files:
            image_file = request.files['image']
            saved_filename = save_uploaded_image(image_file)
            if saved_filename:
                client["image"] = saved_filename
        
        save_client(client)
        return redirect(url_for("client_profile", client_id=client["id"]))

    breadcrumbs = [
        {'label': 'Tableau de bord', 'url': url_for('dashboard')},
        {'label': 'Nouveau Client', 'url': None}
    ]
    return render_template("client_form.html", client=new_client_template(), is_new=True, breadcrumbs=breadcrumbs, back_url=url_for('dashboard'))


@app.route("/client/<client_id>", methods=["GET", "POST"])
def client_profile(client_id):
    client = load_client(client_id)
    if not client:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        client["name"] = request.form.get("name", "").strip()
        client["industry"] = request.form.get("industry", "").strip()
        client["size"] = request.form.get("size", "").strip()
        client["region"] = request.form.get("region", "").strip()
        client["digital_maturity"] = int(request.form.get("digital_maturity", 1))
        client["client_background"] = request.form.get("client_background", "").strip()
        client["updated_at"] = datetime.now().isoformat()
        save_client(client)
        return redirect(url_for("client_profile", client_id=client_id))

    stages = load_json("stages.json")
    breadcrumbs = [
        {'label': 'Tableau de bord', 'url': url_for('dashboard')},
        {'label': client['name'], 'url': None}
    ]
    return render_template("client_profile.html", client=client, stages=stages, breadcrumbs=breadcrumbs, back_url=url_for('dashboard'))


@app.route("/client/<client_id>/edit", methods=["GET", "POST"])
def edit_client(client_id):
    client = load_client(client_id)
    if not client:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        client["name"] = request.form.get("name", "").strip()
        client["industry"] = request.form.get("industry", "").strip()
        client["size"] = request.form.get("size", "").strip()
        client["region"] = request.form.get("region", "").strip()
        client["digital_maturity"] = int(request.form.get("digital_maturity", 1))
        client["client_background"] = request.form.get("client_background", "").strip()
        
        # Handle image upload
        if 'image' in request.files:
            image_file = request.files['image']
            saved_filename = save_uploaded_image(image_file)
            if saved_filename:
                client["image"] = saved_filename
        
        client["updated_at"] = datetime.now().isoformat()
        save_client(client)
        return redirect(url_for("client_profile", client_id=client_id))

    breadcrumbs = [
        {'label': 'Tableau de bord', 'url': url_for('dashboard')},
        {'label': f"Modifier {client['name']}", 'url': None}
    ]
    return render_template("client_form.html", client=client, is_new=False, breadcrumbs=breadcrumbs, back_url=url_for('client_profile', client_id=client_id))


@app.route("/client/<client_id>/delete", methods=["POST"])
def delete_client(client_id):
    path = CLIENTS_DIR / f"{client_id}.json"
    if path.exists():
        path.unlink()
    return redirect(url_for("dashboard"))


# -- Project Routes --

@app.route("/client/<client_id>/project/new", methods=["GET", "POST"])
def new_project(client_id):
    client = load_client(client_id)
    if not client:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        project = new_project_template()
        project["name"] = request.form.get("name", "").strip()
        project["description"] = request.form.get("description", "").strip()
        project["current_stage"] = int(request.form.get("current_stage", 1))

        pain_points = request.form.get("pain_points", "")
        project["pain_points"] = [p.strip() for p in pain_points.split(",") if p.strip()]

        goals = request.form.get("goals", "")
        project["goals"] = [g.strip() for g in goals.split(",") if g.strip()]

        project["stakeholders"] = _parse_stakeholders(request.form)
        project["notes"] = _parse_notes(request.form)

        client.setdefault("projects", []).append(project)
        client["updated_at"] = datetime.now().isoformat()
        save_client(client)
        return redirect(url_for("project_view", client_id=client_id, project_id=project["id"]))

    stages = load_json("stages.json")
    breadcrumbs = [
        {'label': 'Tableau de bord', 'url': url_for('dashboard')},
        {'label': client['name'], 'url': url_for('client_profile', client_id=client_id)},
        {'label': 'Nouveau Projet', 'url': None}
    ]
    return render_template("project_form.html", client=client, project=new_project_template(), is_new=True, stages=stages, breadcrumbs=breadcrumbs, back_url=url_for('client_profile', client_id=client_id))


@app.route("/client/<client_id>/project/<project_id>")
def project_view(client_id, project_id):
    client = load_client(client_id)
    if not client:
        return redirect(url_for("dashboard"))

    project = get_project(client, project_id)
    if not project:
        return redirect(url_for("client_profile", client_id=client_id))

    stages = load_json("stages.json")

    sibling_projects = [p for p in client.get("projects", []) if p["id"] != project_id]
    suggestions_state = project.get("suggestions_state", {})

    stage_recs = {}
    for stage in stages:
        recs = get_recommendations(
            project, stage["id"],
            client_context=client,
            sibling_projects=sibling_projects,
            top_n=5
        )
        for rec in recs:
            item_id = rec["catalog_item"]["id"]
            key = f"{stage['id']}_{item_id}"
            rec["status"] = suggestions_state.get(key, "suggested")
        stage_recs[stage["id"]] = recs

    breadcrumbs = [
        {'label': 'Tableau de bord', 'url': url_for('dashboard')},
        {'label': client['name'], 'url': url_for('client_profile', client_id=client_id)},
        {'label': project['name'], 'url': None}
    ]
    return render_template(
        "project_view.html",
        client=client,
        project=project,
        stages=stages,
        stage_recs=stage_recs,
        breadcrumbs=breadcrumbs,
        back_url=url_for('client_profile', client_id=client_id)
    )


@app.route("/client/<client_id>/project/<project_id>/edit", methods=["GET", "POST"])
def edit_project(client_id, project_id):
    client = load_client(client_id)
    if not client:
        return redirect(url_for("dashboard"))

    project = get_project(client, project_id)
    if not project:
        return redirect(url_for("client_profile", client_id=client_id))

    if request.method == "POST":
        project["name"] = request.form.get("name", "").strip()
        project["description"] = request.form.get("description", "").strip()
        project["current_stage"] = int(request.form.get("current_stage", project.get("current_stage", 1)))

        pain_points = request.form.get("pain_points", "")
        project["pain_points"] = [p.strip() for p in pain_points.split(",") if p.strip()]

        goals = request.form.get("goals", "")
        project["goals"] = [g.strip() for g in goals.split(",") if g.strip()]

        project["stakeholders"] = _parse_stakeholders(request.form)
        project["notes"] = _parse_notes(request.form)

        project["updated_at"] = datetime.now().isoformat()
        client["updated_at"] = datetime.now().isoformat()
        save_client(client)
        return redirect(url_for("project_view", client_id=client_id, project_id=project_id))

    stages = load_json("stages.json")
    breadcrumbs = [
        {'label': 'Tableau de bord', 'url': url_for('dashboard')},
        {'label': client['name'], 'url': url_for('client_profile', client_id=client_id)},
        {'label': f"Modifier {project['name']}", 'url': None}
    ]
    return render_template("project_form.html", client=client, project=project, is_new=False, stages=stages, breadcrumbs=breadcrumbs, back_url=url_for('project_view', client_id=client_id, project_id=project_id))


@app.route("/client/<client_id>/project/<project_id>/advance", methods=["POST"])
def advance_stage(client_id, project_id):
    client = load_client(client_id)
    if not client:
        return redirect(url_for("dashboard"))

    project = get_project(client, project_id)
    if not project:
        return redirect(url_for("client_profile", client_id=client_id))

    current = project.get("current_stage", 1)
    new_stage = current
    if current < 7:
        new_stage = current + 1
        project["current_stage"] = new_stage
        project["updated_at"] = datetime.now().isoformat()
        client["updated_at"] = datetime.now().isoformat()
        save_client(client)

    # Redirect without hash - panel will auto-open to current stage without scrolling
    return redirect(url_for("project_view", client_id=client_id, project_id=project_id))


@app.route("/client/<client_id>/project/<project_id>/delete", methods=["POST"])
def delete_project(client_id, project_id):
    client = load_client(client_id)
    if not client:
        return redirect(url_for("dashboard"))

    client["projects"] = [p for p in client.get("projects", []) if p["id"] != project_id]
    client["updated_at"] = datetime.now().isoformat()
    save_client(client)
    return redirect(url_for("client_profile", client_id=client_id))


# -- Stage Detail --

@app.route("/client/<client_id>/project/<project_id>/stage/<int:stage_id>")
def stage_detail(client_id, project_id, stage_id):
    client = load_client(client_id)
    if not client:
        return redirect(url_for("dashboard"))

    project = get_project(client, project_id)
    if not project:
        return redirect(url_for("client_profile", client_id=client_id))

    stages = load_json("stages.json")
    stage = next((s for s in stages if s["id"] == stage_id), None)
    if not stage:
        return redirect(url_for("project_view", client_id=client_id, project_id=project_id))

    sibling_projects = [p for p in client.get("projects", []) if p["id"] != project_id]
    recommendations = get_recommendations(
        project, stage_id,
        client_context=client,
        sibling_projects=sibling_projects
    )

    suggestions_state = project.get("suggestions_state", {})
    for rec in recommendations:
        item_id = rec["catalog_item"]["id"]
        key = f"{stage_id}_{item_id}"
        rec["status"] = suggestions_state.get(key, "suggested")

    breadcrumbs = [
        {'label': 'Tableau de bord', 'url': url_for('dashboard')},
        {'label': client['name'], 'url': url_for('client_profile', client_id=client_id)},
        {'label': project['name'], 'url': url_for('project_view', client_id=client_id, project_id=project_id)},
        {'label': f"Étape {stage_id}: {stage['name']}", 'url': None}
    ]
    return render_template(
        "stage_detail.html",
        client=client,
        project=project,
        stage=stage,
        stages=stages,
        recommendations=recommendations,
        breadcrumbs=breadcrumbs,
        back_url=url_for('project_view', client_id=client_id, project_id=project_id)
    )


@app.route("/client/<client_id>/project/<project_id>/suggestion/<int:stage_id>/<item_id>", methods=["POST"])
def update_suggestion(client_id, project_id, stage_id, item_id):
    client = load_client(client_id)
    if not client:
        return jsonify({"error": "Client not found"}), 404

    project = get_project(client, project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    action = request.form.get("action", "suggested")
    key = f"{stage_id}_{item_id}"
    project.setdefault("suggestions_state", {})[key] = action
    project["updated_at"] = datetime.now().isoformat()
    client["updated_at"] = datetime.now().isoformat()
    save_client(client)

    # Redirect back to project view (unified single-page experience)
    return redirect(url_for("project_view", client_id=client_id, project_id=project_id) + f"#stage-panel-{stage_id}")


# -- Catalog --

@app.route("/catalog")
def catalog_browse():
    catalog = load_json("catalog.json")
    team = load_json("team.json")
    team_map = {t["id"]: t for t in team}
    stages = load_json("stages.json")

    stage_filter = request.args.get("stage", "")
    type_filter = request.args.get("type", "")

    filtered = catalog
    if stage_filter:
        stage_num = int(stage_filter)
        filtered = [i for i in filtered if stage_num in i["applicable_stages"]]
    if type_filter:
        filtered = [i for i in filtered if i["type"] == type_filter]

    for item in filtered:
        item["_team"] = [team_map[tid] for tid in item.get("team_ids", []) if tid in team_map]

    breadcrumbs = [
        {'label': 'Tableau de bord', 'url': url_for('dashboard')},
        {'label': 'Catalogue Innovation', 'url': None}
    ]
    return render_template(
        "catalog.html",
        catalog=filtered,
        stages=stages,
        stage_filter=stage_filter,
        type_filter=type_filter,
        breadcrumbs=breadcrumbs,
        back_url=url_for('dashboard')
    )


# -- AI Chat API --

@app.route("/api/chat", methods=["POST"])
def ai_chat():
    data = request.json
    user_message = data.get("message", "")
    context = data.get("context", {})
    
    recommendations = get_ai_recommendations_local(user_message, context)
    
    return jsonify({
        "response": recommendations["message"],
        "recommendations": recommendations["services"]
    })


def get_ai_recommendations_local(user_message, context):
    """Enhanced keyword matching with conversational response"""
    catalog = load_json("catalog.json")
    
    # Extract keywords from user message (simple approach)
    keywords = extract_keywords(user_message.lower())
    
    # Score services based on keyword match + context
    scored_services = []
    for item in catalog:
        if item["type"] != "service":
            continue
        
        score = 0
        
        # Match keywords with service tags
        for keyword in keywords:
            for tag in item.get("tags", []):
                if keyword in tag.lower():
                    score += 2
            # Also match in service name and description
            if keyword in item["name"].lower():
                score += 3
            if keyword in item["description"].lower():
                score += 1
        
        # Boost if applicable to current stage
        if context.get("stage") in item["applicable_stages"]:
            score += 4
        
        # Match with project pain points
        for pain in context.get("painPoints", []):
            pain_lower = pain.lower()
            for tag in item.get("tags", []):
                if pain_lower in tag.lower() or tag.lower() in pain_lower:
                    score += 3
        
        # Match with project goals
        for goal in context.get("goals", []):
            goal_lower = goal.lower()
            for tag in item.get("tags", []):
                if goal_lower in tag.lower() or tag.lower() in goal_lower:
                    score += 3
        
        if score > 0:
            scored_services.append({"service": item, "score": score})
    
    # Sort and take top 3
    scored_services.sort(key=lambda x: x["score"], reverse=True)
    top_services = scored_services[:3]
    
    # Build conversational response
    if top_services:
        service_count = len(top_services)
        message = f"Basé sur votre situation et le contexte du projet, je recommande {service_count} service{'s' if service_count > 1 else ''} particulièrement adapté{'s' if service_count > 1 else ''} :"
    else:
        message = "Je n'ai pas trouvé de services spécifiquement adaptés à cette situation. Pouvez-vous reformuler votre besoin ou ajouter plus de détails ?"
    
    return {
        "message": message,
        "services": [s["service"] for s in top_services]
    }


def extract_keywords(text):
    """Extract meaningful keywords from user message"""
    # Remove common French stop words
    stop_words = {
        'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'et', 'ou', 'mais',
        'est', 'sont', 'a', 'avec', 'pour', 'par', 'dans', 'sur', 'nous',
        'je', 'tu', 'il', 'elle', 'vous', 'ils', 'elles', 'ce', 'cette',
        'mon', 'ma', 'mes', 'ton', 'ta', 'tes', 'son', 'sa', 'ses',
        'avons', 'besoin', 'faire', 'faire', 'comment', 'quel', 'quelle',
        'qui', 'que', 'quoi', 'dont', 'où'
    }
    
    # Split and filter
    words = text.split()
    keywords = [w for w in words if len(w) > 3 and w not in stop_words]
    
    return keywords


if __name__ == "__main__":
    app.run(debug=True, port=5001)
