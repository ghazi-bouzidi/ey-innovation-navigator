// Onboarding Tour Configuration
const ONBOARDING_STEPS = [
    {
        title: "Bienvenue sur Innovation Navigator 👋",
        text: "Votre copilote pour piloter les missions d'innovation client à travers 8 étapes structurées.\n\nDécouvrez comment l'IA vous aide à recommander les bons services au bon moment.",
        icon: "🎯",
        highlight: null
    },
    {
        title: "1️⃣ Créez vos Clients",
        text: "Commencez par enregistrer vos clients avec leur profil complet : secteur, région, maturité digitale.\n\nCes informations alimentent les recommandations IA.",
        icon: "👥",
        highlight: null
    },
    {
        title: "2️⃣ Créez des Projets Innovation",
        text: "Chaque projet suit un parcours en 8 étapes :\nKick-off → Diagnostic → Co-création → Prototypage → Vision → Livraison → Pilotage → Clôture\n\nCliquez sur une étape pour voir les services recommandés.",
        icon: "📋",
        highlight: null
    },
    {
        title: "3️⃣ Recommandations IA Intelligentes",
        text: "L'IA analyse automatiquement :\n✓ Vos pain points et objectifs\n✓ Le secteur et la maturité du client\n✓ L'étape actuelle du projet\n✓ Les services déjà utilisés\n\nElle recommande les services les plus pertinents avec un niveau de confiance (🟢 High / 🟡 Medium).",
        icon: "🧠",
        highlight: null
    },
    {
        title: "4️⃣ Posez vos Questions à l'IA 💬",
        text: "Besoin d'une recommandation spécifique ?\n\nCliquez sur le bouton AI en bas à droite dans n'importe quel projet pour demander :\n• \"Quels services pour améliorer l'engagement client ?\"\n• \"Comment accélérer le prototypage ?\"\n• \"Recommandations pour un secteur bancaire ?\"\n\nL'IA répond instantanément avec des suggestions adaptées.",
        icon: "💬",
        highlight: null
    }
];

let currentOnboardingStep = 0;

// Initialize onboarding on page load
document.addEventListener('DOMContentLoaded', function() {
    // Check if onboarding has been completed or skipped
    const onboardingCompleted = localStorage.getItem('onboarding_completed');
    const onboardingSkipped = localStorage.getItem('onboarding_skipped');
    
    // Show onboarding only on first visit
    if (!onboardingCompleted && !onboardingSkipped) {
        // Delay slightly to ensure page is fully loaded
        setTimeout(function() {
            showOnboarding();
        }, 500);
    }
});

// Show onboarding modal
function showOnboarding() {
    currentOnboardingStep = 0;
    const overlay = document.getElementById('onboarding-overlay');
    if (overlay) {
        overlay.style.display = 'flex';
        renderOnboardingStep(0);
    }
}

// Render a specific onboarding step
function renderOnboardingStep(stepIndex) {
    if (stepIndex < 0 || stepIndex >= ONBOARDING_STEPS.length) return;
    
    const step = ONBOARDING_STEPS[stepIndex];
    
    // Update title
    const titleEl = document.getElementById('onboarding-title');
    if (titleEl) titleEl.textContent = step.title;
    
    // Update text
    const textEl = document.getElementById('onboarding-text');
    if (textEl) textEl.textContent = step.text;
    
    // Update visual (icon)
    const visualEl = document.getElementById('onboarding-visual');
    if (visualEl) {
        visualEl.innerHTML = `<div class="onboarding-icon">${step.icon}</div>`;
    }
    
    // Update indicators
    const indicators = document.querySelectorAll('.onboarding-indicators .indicator');
    indicators.forEach((indicator, index) => {
        if (index === stepIndex) {
            indicator.classList.add('active');
        } else {
            indicator.classList.remove('active');
        }
    });
    
    // Update button text for last step
    const nextBtn = document.getElementById('onboarding-next');
    if (nextBtn) {
        if (stepIndex === ONBOARDING_STEPS.length - 1) {
            nextBtn.textContent = 'Terminer ✓';
        } else {
            nextBtn.textContent = 'Suivant →';
        }
    }
    
    // Apply highlight if specified (future enhancement)
    if (step.highlight) {
        const elementToHighlight = document.querySelector(step.highlight);
        if (elementToHighlight) {
            elementToHighlight.classList.add('onboarding-highlight');
        }
    }
}

// Move to next step
function nextOnboardingStep() {
    if (currentOnboardingStep < ONBOARDING_STEPS.length - 1) {
        currentOnboardingStep++;
        renderOnboardingStep(currentOnboardingStep);
    } else {
        // Last step - complete onboarding
        completeOnboarding();
    }
}

// Skip onboarding
function skipOnboarding() {
    localStorage.setItem('onboarding_skipped', 'true');
    closeOnboarding();
}

// Complete onboarding
function completeOnboarding() {
    localStorage.setItem('onboarding_completed', 'true');
    closeOnboarding();
}

// Close onboarding modal
function closeOnboarding() {
    const overlay = document.getElementById('onboarding-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
    
    // Remove any highlights
    document.querySelectorAll('.onboarding-highlight').forEach(el => {
        el.classList.remove('onboarding-highlight');
    });
}

// Restart onboarding (for help button)
function restartOnboarding() {
    // Clear localStorage flags
    localStorage.removeItem('onboarding_completed');
    localStorage.removeItem('onboarding_skipped');
    
    // Show onboarding
    showOnboarding();
}

// Close on ESC key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const overlay = document.getElementById('onboarding-overlay');
        if (overlay && overlay.style.display === 'flex') {
            skipOnboarding();
        }
    }
});

// Close on overlay click (outside modal)
document.addEventListener('click', function(e) {
    const overlay = document.getElementById('onboarding-overlay');
    if (e.target === overlay) {
        skipOnboarding();
    }
});
