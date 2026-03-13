document.addEventListener("DOMContentLoaded", function () {
    var dmSlider = document.getElementById("digital_maturity");
    var dmVal = document.getElementById("dm-val");
    if (dmSlider && dmVal) {
        dmSlider.addEventListener("input", function () {
            dmVal.textContent = this.value;
        });
    }

    // Auto-open stage panel on page load
    // Priority: 1) Hash in URL, 2) Current stage from journey pipeline
    if (window.location.hash && window.location.hash.startsWith("#stage-panel-")) {
        var stageId = window.location.hash.replace("#stage-panel-", "");
        if (stageId && !isNaN(stageId)) {
            toggleStagePanel(parseInt(stageId), true); // true = scroll on hash navigation
        }
    } else {
        // Auto-open current stage if no hash present (but don't scroll on initial load)
        var currentStage = document.querySelector(".journey-stage.stage-current");
        if (currentStage) {
            var currentStageId = currentStage.getAttribute("data-stage-id");
            if (currentStageId) {
                toggleStagePanel(parseInt(currentStageId), false); // false = no scroll on initial load
            }
        }
    }
});

function toggleStagePanel(stageId, shouldScroll) {
    var panels = document.querySelectorAll(".stage-panel");
    var stages = document.querySelectorAll(".journey-stage-clickable");
    var targetPanel = document.getElementById("stage-panel-" + stageId);
    var targetStage = document.querySelector('[data-stage-id="' + stageId + '"]');

    if (!targetPanel) return;

    var isVisible = targetPanel.style.display !== "none";

    panels.forEach(function (p) { p.style.display = "none"; });
    stages.forEach(function (s) { s.classList.remove("stage-active"); });

    if (!isVisible) {
        // Show loading state first
        showAILoadingState(targetPanel);
        
        targetPanel.style.display = "block";
        if (targetStage) targetStage.classList.add("stage-active");
        
        // Simulate AI processing delay (800ms)
        setTimeout(function() {
            hideAILoadingState(targetPanel);
        }, 800);
        
        // Only scroll if explicitly requested (user click or hash navigation)
        if (shouldScroll !== false) {
            targetPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }
    }
}

function showAILoadingState(panel) {
    var recsGrid = panel.querySelector('.recommendations-grid');
    if (!recsGrid) return;
    
    // Store original content
    recsGrid.dataset.originalContent = recsGrid.innerHTML;
    
    // Show skeleton loading
    var skeletonHTML = `
        <div class="ai-analyzing">
            <div class="ai-icon">🧠</div>
            <div class="ai-message">L'IA analyse votre projet...</div>
            <div class="ai-progress-bar">
                <div class="ai-progress-fill"></div>
            </div>
        </div>
    `;
    
    recsGrid.innerHTML = skeletonHTML;
}

function hideAILoadingState(panel) {
    var recsGrid = panel.querySelector('.recommendations-grid');
    if (!recsGrid || !recsGrid.dataset.originalContent) return;
    
    // Restore original content with fade-in animation
    var originalContent = recsGrid.dataset.originalContent;
    recsGrid.innerHTML = originalContent;
    recsGrid.style.opacity = '0';
    
    setTimeout(function() {
        recsGrid.style.transition = 'opacity 0.4s ease-out';
        recsGrid.style.opacity = '1';
    }, 50);
    
    delete recsGrid.dataset.originalContent;
}

// =============================================================================
// AI Chat Assistant
// =============================================================================

function toggleChat() {
    var chatWindow = document.getElementById('ai-chat-window');
    var isVisible = chatWindow.style.display !== 'none';
    chatWindow.style.display = isVisible ? 'none' : 'flex';
    
    if (!isVisible && !chatWindow.dataset.initialized) {
        initializeChat();
        chatWindow.dataset.initialized = 'true';
    }
}

function initializeChat() {
    addChatMessage('ai', 'Bonjour! Je suis votre assistant innovation. Décrivez-moi votre situation ou défi, et je vous recommanderai les services les plus adaptés pour ce projet.');
}

function sendChatMessage() {
    var input = document.getElementById('chat-input');
    var message = input.value.trim();
    if (!message) return;
    
    addChatMessage('user', message);
    input.value = '';
    
    showTyping();
    fetchAIRecommendations(message);
}

function addChatMessage(sender, text, recommendations) {
    var messagesContainer = document.getElementById('chat-messages');
    var messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message chat-message-' + sender;
    
    if (sender === 'ai' && recommendations && recommendations.length > 0) {
        var html = '<strong>' + text + '</strong>';
        recommendations.forEach(function(service) {
            html += '<div class="service-recommendation">';
            html += '<div class="service-name">• ' + service.name + '</div>';
            html += '<div class="service-desc">' + service.description.substring(0, 120) + '...</div>';
            html += '</div>';
        });
        messageDiv.innerHTML = html;
    } else {
        messageDiv.textContent = text;
    }
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showTyping() {
    var typing = document.getElementById('typing-indicator');
    if (typing) typing.style.display = 'flex';
}

function hideTyping() {
    var typing = document.getElementById('typing-indicator');
    if (typing) typing.style.display = 'none';
}

async function fetchAIRecommendations(userMessage) {
    try {
        var response = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                message: userMessage,
                context: window.projectContext || {}
            })
        });
        
        var data = await response.json();
        hideTyping();
        addChatMessage('ai', data.response, data.recommendations);
    } catch (error) {
        hideTyping();
        addChatMessage('ai', 'Désolé, une erreur est survenue. Veuillez réessayer.');
        console.error('Chat error:', error);
    }
}

// Allow Enter to send message (Shift+Enter for new line)
document.addEventListener('DOMContentLoaded', function() {
    var chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        });
    }
});
