import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_json(filename):
    with open(DATA_DIR / filename, "r") as f:
        return json.load(f)


def get_recommendations(project, stage_id, client_context=None, sibling_projects=None, top_n=5):
    catalog = load_json("catalog.json")
    team = load_json("team.json")
    team_map = {t["id"]: t for t in team}

    pain_points = [p.lower() for p in project.get("pain_points", [])]
    goals = [g.lower() for g in project.get("goals", [])]
    client_industry = ""
    if client_context:
        client_industry = client_context.get("industry", "").lower()
    client_keywords = set(pain_points + goals)

    applied_across_projects = set()
    if sibling_projects:
        for sib in sibling_projects:
            for key, status in sib.get("suggestions_state", {}).items():
                if status == "applied":
                    parts = key.split("_", 1)
                    if len(parts) == 2:
                        applied_across_projects.add(parts[1])

    scored = []
    for item in catalog:
        if stage_id not in item["applicable_stages"]:
            continue

        score = 10.0
        matched_tags = []
        tags = set(t.lower() for t in item.get("tags", []))
        overlap = client_keywords & tags
        score += len(overlap) * 5.0
        matched_tags.extend(list(overlap))

        industries = [i.lower() for i in item.get("industries", [])]
        if "all" in industries or client_industry in industries:
            score += 3.0
        if client_industry in industries and client_industry != "all":
            score += 2.0

        cross_project_note = None
        if item["id"] in applied_across_projects:
            score += 4.0
            cross_project_note = "Déjà engagé dans un autre projet pour ce client."
            matched_tags.append("multi-projet")

        reasoning = _build_reasoning(item, overlap, client_industry, stage_id, cross_project_note)
        linked_team = [team_map[tid] for tid in item.get("team_ids", []) if tid in team_map]

        # Calculate confidence percentage (max possible score ~29)
        max_possible_score = 29.0
        confidence = min(100, int((score / max_possible_score) * 100))
        confidence_level = (
            "high" if confidence >= 65 else
            "medium" if confidence >= 45 else
            "low"
        )

        scored.append({
            "catalog_item": item,
            "score": score,
            "confidence": confidence,
            "confidence_level": confidence_level,
            "matched_tags": matched_tags[:4],  # Limit to 4 tags
            "reasoning": reasoning,
            "team_members": linked_team,
            "status": "suggested"
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_n]


def _build_reasoning(item, keyword_overlap, client_industry, stage_id, cross_project_note=None):
    parts = []
    parts.append(f"Recommandé pour l'étape {stage_id} selon l'applicabilité.")

    if keyword_overlap:
        kw_list = ", ".join(keyword_overlap)
        parts.append(f"Correspond aux axes du client : {kw_list}.")

    industries = [i.lower() for i in item.get("industries", [])]
    if client_industry and client_industry in industries:
        parts.append(f"Directement pertinent pour le secteur {client_industry}.")

    if cross_project_note:
        parts.append(cross_project_note)

    type_labels = {
        "framework": "C'est un framework structuré qui fournit méthodologie et guidance.",
        "tool": "C'est un outil opérationnel déployable directement.",
        "service": "C'est une prestation de service menée par des consultants spécialisés.",
        "asset": "C'est un asset propriétaire développé par l'équipe innovation."
    }
    if item.get("type") in type_labels:
        parts.append(type_labels[item["type"]])

    return " ".join(parts)
