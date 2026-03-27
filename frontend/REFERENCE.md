<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Qurultai — Council of AI Agents</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #F8F5F0;
      --bg-warm: #F3EDE5;
      --card: #FFFFFF;
      --fg: #1A1714;
      --fg-muted: #6B6560;
      --accent: #8B2942;
      --accent-soft: rgba(139, 41, 66, 0.08);
      --gold: #B8860B;
      --gold-soft: rgba(184, 134, 11, 0.12);
      --border: rgba(139, 41, 66, 0.1);
      --radius: 32px;
      --radius-sm: 20px;
    }

    * {
      box-sizing: border-box;
    }

    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: var(--bg);
      color: var(--fg);
      margin: 0;
      min-height: 100vh;
    }

    h1, h2, h3, .display {
      font-family: 'Instrument Serif', serif;
    }

    /* Traditional Kazakh ornament background */
    .ornament-pattern {
      position: fixed;
      inset: 0;
      pointer-events: none;
      opacity: 0.04;
      background-image: url("data:image/svg+xml,%3Csvg width='180' height='180' viewBox='0 0 180 180' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' stroke='%238B2942' stroke-width='1'%3E%3C!-- Qoshqar muyiz (ram horn) --%3E%3Cpath d='M90 20 Q120 40 90 70 Q60 40 90 20'/%3E%3Cpath d='M90 110 Q120 130 90 160 Q60 130 90 110'/%3E%3C!-- Qus qanaty (bird wings) --%3E%3Cpath d='M20 90 Q40 60 70 90 Q40 120 20 90'/%3E%3Cpath d='M110 90 Q130 60 160 90 Q130 120 110 90'/%3E%3C!-- Central diamond --%3E%3Cpath d='M90 70 L110 90 L90 110 L70 90 Z'/%3E%3Ccircle cx='90' cy='90' r='8'/%3E%3C/g%3E%3C/svg%3E");
      background-size: 180px 180px;
    }

    /* Syrmak border pattern */
    .syrmak-border {
      background-image: url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 20 Q10 10 20 20 Q30 30 40 20' fill='none' stroke='%238B2942' stroke-width='2' opacity='0.15'/%3E%3Cpath d='M0 20 Q10 30 20 20 Q30 10 40 20' fill='none' stroke='%23B8860B' stroke-width='1' opacity='0.1'/%3E%3C/svg%3E");
      background-size: 40px 40px;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
      width: 6px;
    }
    ::-webkit-scrollbar-track {
      background: transparent;
    }
    ::-webkit-scrollbar-thumb {
      background: var(--border);
      border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: var(--accent);
    }

    /* Animations */
    @keyframes slide-in-right {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }

    @keyframes slide-out-right {
      from { transform: translateX(0); opacity: 1; }
      to { transform: translateX(100%); opacity: 0; }
    }

    @keyframes fade-up {
      from { opacity: 0; transform: translateY(16px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @keyframes pulse-gold {
      0%, 100% { box-shadow: 0 0 0 0 rgba(184, 134, 11, 0.4); }
      50% { box-shadow: 0 0 0 8px rgba(184, 134, 11, 0); }
    }

    .animate-slide-in {
      animation: slide-in-right 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    .animate-slide-out {
      animation: slide-out-right 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    .message-animate {
      animation: fade-up 0.5s ease-out backwards;
    }

    .pulse-gold {
      animation: pulse-gold 2s ease-in-out infinite;
    }

    /* Reference chip */
    .reference-chip {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 12px;
      background: var(--gold-soft);
      color: var(--gold);
      border-radius: 100px;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
    }
    .reference-chip:hover {
      background: var(--gold);
      color: white;
    }

    /* Badge */
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 14px;
      border-radius: 100px;
      font-size: 13px;
      font-weight: 500;
    }

    /* Agent stance colors */
    .stance-support { background: rgba(34, 139, 34, 0.1); color: #228B22; }
    .stance-cautious { background: rgba(184, 134, 11, 0.1); color: #B8860B; }
    .stance-critical { background: rgba(139, 41, 66, 0.1); color: #8B2942; }
    .stance-neutral { background: rgba(107, 101, 96, 0.1); color: #6B6560; }

    /* Focus states */
    *:focus-visible {
      outline: 2px solid var(--accent);
      outline-offset: 2px;
    }

    /* Reduced motion */
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
      }
    }

    /* Panel transitions */
    .panel-overlay {
      position: fixed;
      inset: 0;
      background: rgba(26, 23, 20, 0.3);
      backdrop-filter: blur(4px);
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.3s;
      z-index: 40;
    }
    .panel-overlay.active {
      opacity: 1;
      pointer-events: auto;
    }

    /* Decorative yurt top */
    .yurt-shanyrak {
      position: relative;
    }
    .yurt-shanyrak::before {
      content: '';
      position: absolute;
      top: -60px;
      left: 50%;
      transform: translateX(-50%);
      width: 120px;
      height: 60px;
      background: url("data:image/svg+xml,%3Csvg width='120' height='60' viewBox='0 0 120 60' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='60' cy='60' r='55' fill='none' stroke='%238B2942' stroke-width='1.5' opacity='0.2'/%3E%3Ccircle cx='60' cy='60' r='40' fill='none' stroke='%23B8860B' stroke-width='1' opacity='0.15'/%3E%3Ccircle cx='60' cy='60' r='25' fill='none' stroke='%238B2942' stroke-width='1' opacity='0.1'/%3E%3Cpath d='M60 5 L60 20' stroke='%23B8860B' stroke-width='2' opacity='0.2'/%3E%3Cpath d='M40 25 L60 5 L80 25' fill='none' stroke='%238B2942' stroke-width='1.5' opacity='0.15'/%3E%3C/svg%3E") no-repeat center bottom;
      pointer-events: none;
    }

  </style>
</head>
<body>
  <div class="ornament-pattern"></div>
  
  <!-- Main Layout -->
  <div class="min-h-screen flex flex-col relative">
    
    <!-- Header -->
    <header class="sticky top-0 z-30 bg-[--bg]/90 backdrop-blur-md border-b border-[--border]">
      <div class="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-4">
          <!-- Logo: Shanyrak-inspired -->
          <div class="w-12 h-12 relative">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
              <circle cx="24" cy="24" r="20" stroke="currentColor" stroke-width="1.5" class="text-[--accent]" opacity="0.3"/>
              <circle cx="24" cy="24" r="14" stroke="currentColor" stroke-width="1.5" class="text-[--gold]" opacity="0.5"/>
              <circle cx="24" cy="24" r="8" stroke="currentColor" stroke-width="1.5" class="text-[--accent]"/>
              <path d="M24 4 L24 10" stroke="currentColor" stroke-width="2" class="text-[--gold]"/>
              <path d="M12 12 L18 18" stroke="currentColor" stroke-width="1.5" class="text-[--accent]" opacity="0.5"/>
              <path d="M36 12 L30 18" stroke="currentColor" stroke-width="1.5" class="text-[--accent]" opacity="0.5"/>
              <circle cx="24" cy="24" r="2" fill="currentColor" class="text-[--accent]"/>
            </svg>
          </div>
          <div>
            <h1 class="text-2xl font-normal tracking-tight">Qurultai</h1>
            <p class="text-[--fg-muted] text-sm">AI Council Platform</p>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <button
            id="view-council-btn"
            class="flex items-center gap-2 px-5 py-2.5 bg-[--accent] text-white rounded-[--radius-sm] font-medium text-sm hover:opacity-90 transition-all"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/>
            </svg>
            View Council Debate
          </button>
        </div>
      </div>
    </header>

    <!-- Main Chat Area -->
    <main class="flex-1 flex flex-col max-w-4xl mx-auto w-full px-6 py-8">

      <!-- Welcome Section -->
      <div class="text-center mb-12 yurt-shanyrak">
        <div class="inline-flex items-center gap-2 px-4 py-2 bg-[--accent-soft] rounded-full text-[--accent] text-sm font-medium mb-6">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
          7 AI Agents Ready to Deliberate
        </div>
        <h2 class="text-5xl font-normal mb-4 leading-tight">Welcome to the Council</h2>
        <p class="text-xl text-[--fg-muted] max-w-2xl mx-auto leading-relaxed">
          Submit your policy question or upload a document. The council of AI agents will analyze, debate, and deliver a comprehensive recommendation.
        </p>
      </div>

      <!-- Chat Messages -->
      <div class="flex-1 space-y-6 mb-6" id="chat-messages">
        <!-- Messages will be rendered here -->
      </div>

      <!-- Input Area -->
      <div class="sticky bottom-6">
        <div class="bg-[--card] rounded-[--radius] shadow-lg shadow-black/5 border border-[--border] overflow-hidden">
          <!-- File upload area -->
          <div class="p-4 border-b border-[--border] flex items-center gap-3">
            <button class="flex items-center gap-2 px-4 py-2 bg-[--bg-warm] rounded-xl text-sm font-medium hover:bg-[--bg] transition-colors">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"/>
              </svg>
              Attach Document
            </button>
            <span class="text-sm text-[--fg-muted]">PDF, DOCX, TXT supported</span>
          </div>

          <!-- Text input -->
          <div class="p-4">
            <textarea
              id="user-input"
              class="w-full bg-transparent text-lg resize-none outline-none placeholder:text-[--fg-muted] min-h-[80px]"
              placeholder="Describe your policy question or decision to analyze..."
              rows="3"
            ></textarea>
          </div>

          <div class="px-4 pb-4 flex items-center justify-between">
            <div class="flex items-center gap-2 text-sm text-[--fg-muted]">
              <kbd class="px-2 py-1 bg-[--bg-warm] rounded text-xs font-mono">Enter</kbd>
              <span>to send</span>
            </div>
            <button
              id="send-btn"
              class="px-6 py-3 bg-[--accent] text-white rounded-[--radius-sm] font-semibold text-base hover:opacity-90 transition-opacity flex items-center gap-2"
            >
              <span>Summon Council</span>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="22" y1="2" x2="11" y2="13"/>
                <polygon points="22 2 15 22 11 13 2 9 22 2"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

    </main>

    <!-- Panel Overlay -->
    <div class="panel-overlay" id="panel-overlay"></div>

    <!-- Right Panel: Council Debate -->
    <aside
      id="council-panel"
      class="fixed top-0 right-0 h-full w-[520px] bg-[--bg] border-l border-[--border] shadow-2xl z-50 flex flex-col transform translate-x-full"
    >
      <!-- Panel Header -->
      <div class="p-6 border-b border-[--border] bg-[--card]">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-2xl font-normal">Council Debate</h2>
          <button
            id="close-panel-btn"
            class="w-10 h-10 rounded-full bg-[--bg-warm] flex items-center justify-center hover:bg-[--bg] transition-colors"
            aria-label="Close panel"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <!-- Topic being debated -->
        <div class="p-4 bg-[--accent-soft] rounded-[--radius-sm]">
          <p class="text-sm text-[--fg-muted] mb-1">Current Topic</p>
          <p class="font-medium text-base" id="debate-topic">Urban Development Framework 2025-2030</p>
        </div>
      </div>

      <!-- Debate Messages -->
      <div class="flex-1 overflow-y-auto p-6 space-y-5" id="debate-messages">
        <!-- Debate messages will be rendered here -->
      </div>

      <!-- Panel Footer -->
      <div class="p-4 border-t border-[--border] bg-[--card]">
        <button class="w-full py-3 px-4 bg-[--gold] text-white rounded-[--radius-sm] font-semibold text-base hover:opacity-90 transition-opacity flex items-center justify-center gap-2">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
          Conclude Debate
        </button>
      </div>
    </aside>

  </div>

  <script>
    // ==================== DATA ====================
    
    const councilAgents = [
      { 
        id: 1, 
        name: 'Ministry of Economy', 
        role: 'Fiscal Impact Analyst',
        stance: 'cautious',
        avatar: 'ME',
        color: '#8B2942'
      },
      { 
        id: 2, 
        name: 'Ministry of Ecology', 
        role: 'Environmental Compliance',
        stance: 'support',
        avatar: 'EC',
        color: '#228B22'
      },
      { 
        id: 3, 
        name: 'Construction Agency', 
        role: 'Infrastructure Specialist',
        stance: 'neutral',
        avatar: 'CA',
        color: '#5B7BB3'
      },
      { 
        id: 4, 
        name: 'Legal Department', 
        role: 'Constitutional Review',
        stance: 'critical',
        avatar: 'LD',
        color: '#B8860B'
      },
      { 
        id: 5, 
        name: 'Public Health Authority', 
        role: 'Health Impact Assessor',
        stance: 'support',
        avatar: 'PH',
        color: '#9D6B4A'
      },
      { 
        id: 6, 
        name: 'Regional Governance', 
        role: 'Local Implementation',
        stance: 'neutral',
        avatar: 'RG',
        color: '#6B5B8A'
      },
      { 
        id: 7, 
        name: 'Cultural Heritage Board', 
        role: 'Heritage Preservation',
        stance: 'cautious',
        avatar: 'CH',
        color: '#8A6B5B'
      }
    ];

    const documentReferences = [
      { id: 'ref-1', title: 'Land Code Article 39', type: 'Legal Document', pages: '12-14' },
      { id: 'ref-2', title: 'Budget Allocation Report 2024', type: 'Financial Report', pages: '8-10' },
      { id: 'ref-3', title: 'Environmental Impact Assessment', type: 'Technical Report', pages: '23-27' },
      { id: 'ref-4', title: 'Urban Development Master Plan', type: 'Policy Document', pages: '45-52' },
      { id: 'ref-5', title: 'Public Consultation Guidelines', type: 'Regulatory Framework', pages: '5-7' }
    ];

    // Main chat messages
    let chatMessages = [
      {
        id: 1,
        type: 'system',
        content: 'Salem! I am your Qurultai coordinator. Submit your policy question, and I will convene the council of AI agents to analyze it from multiple ministerial perspectives.',
        timestamp: new Date(Date.now() - 300000)
      }
    ];

    // Debate messages (agent discussions)
    let debateMessages = [
      {
        id: 1,
        phase: 'position',
        agent: councilAgents[0],
        content: 'From a fiscal perspective, the proposed framework requires 847 billion KZT investment over 5 years. This represents 2.3% of annual budget allocation. My primary concern is the ROI timeline extending beyond standard evaluation periods.',
        references: [documentReferences[1]],
        timestamp: new Date(Date.now() - 600000)
      },
      {
        id: 2,
        phase: 'position',
        agent: councilAgents[1],
        content: 'The environmental provisions are robust. The framework aligns with our 2050 carbon neutrality commitments. I particularly support the green zone requirements and sustainable construction mandates.',
        references: [documentReferences[2]],
        timestamp: new Date(Date.now() - 580000)
      },
      {
        id: 3,
        phase: 'position',
        agent: councilAgents[3],
        content: 'I must raise a constitutional concern. Article 39 of the Land Code requires minimum 30-day public consultation for agricultural land rezoning. The current proposal shows only 14 days. This creates legal vulnerability.',
        references: [documentReferences[0], documentReferences[4]],
        timestamp: new Date(Date.now() - 560000)
      },
      {
        id: 4,
        phase: 'response',
        agent: councilAgents[2],
        content: 'Legal raises a valid point. From infrastructure perspective, our analysis confirms utilities can support Phases 1-2 through 2027. Phase 3 requires the new water treatment facility.',
        references: [documentReferences[3]],
        timestamp: new Date(Date.now() - 540000)
      },
      {
        id: 5,
        phase: 'response',
        agent: councilAgents[0],
        content: 'If we extend consultation as Legal suggests, we can reallocate Phase 1 budget to establish proper consultation infrastructure. This could strengthen public buy-in by 15-20%.',
        references: [documentReferences[1], documentReferences[4]],
        timestamp: new Date(Date.now() - 520000)
      },
      {
        id: 6,
        phase: 'consensus',
        agent: councilAgents[3],
        content: 'Agreed. I recommend the framework explicitly reference Article 39 compliance procedures as an appendix. This provides legal shielding. I can draft the language within 48 hours.',
        references: [documentReferences[0]],
        timestamp: new Date(Date.now() - 500000)
      }
    ];

    // ==================== RENDERING ====================

    function renderChatMessages() {
      const container = document.getElementById('chat-messages');
      container.innerHTML = chatMessages.map((msg, index) => {
        if (msg.type === 'system') {
          return `
            <div class="message-animate flex gap-4" style="animation-delay: ${index * 100}ms">
              <div class="flex-shrink-0">
                <div class="w-12 h-12 rounded-full bg-[--accent-soft] flex items-center justify-center">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="text-[--accent]">
                    <circle cx="24" cy="24" r="20" stroke="currentColor" stroke-width="1.5" class="text-[--accent]" opacity="0.3"/>
                    <circle cx="24" cy="24" r="8" stroke="currentColor" stroke-width="1.5" class="text-[--accent]"/>
                    <circle cx="24" cy="24" r="2" fill="currentColor" class="text-[--accent]"/>
                  </svg>
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-3 mb-2">
                  <span class="font-semibold text-lg">Qurultai Coordinator</span>
                  <span class="text-sm text-[--fg-muted]">${formatTime(msg.timestamp)}</span>
                </div>
                <div class="bg-[--card] rounded-[--radius] p-6 shadow-sm border border-[--border]">
                  <p class="text-lg leading-relaxed">${msg.content}</p>
                </div>
              </div>
            </div>
          `;
        } else if (msg.type === 'user') {
          return `
            <div class="message-animate flex gap-4 justify-end" style="animation-delay: ${index * 100}ms">
              <div class="max-w-[80%]">
                <div class="flex items-center gap-3 mb-2 justify-end">
                  <span class="text-sm text-[--fg-muted]">${formatTime(msg.timestamp)}</span>
                  <span class="font-semibold text-lg">You</span>
                </div>
                <div class="bg-[--accent] text-white rounded-[--radius] p-6">
                  <p class="text-lg leading-relaxed">${msg.content}</p>
                </div>
              </div>
              <div class="flex-shrink-0">
                <div class="w-12 h-12 rounded-full bg-[--gold-soft] flex items-center justify-center">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-[--gold]">
                    <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                </div>
              </div>
            </div>
          `;
        } else if (msg.type === 'summary') {
          return `
            <div class="message-animate" style="animation-delay: ${index * 100}ms">
              <div class="bg-[--card] rounded-[--radius] p-8 shadow-sm border border-[--border] border-t-4 border-t-[--gold]">
                <div class="flex items-center gap-3 mb-6">
                  <div class="w-10 h-10 rounded-full bg-[--gold-soft] flex items-center justify-center">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-[--gold]">
                      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                      <polyline points="14 2 14 8 20 8"/>
                      <line x1="16" y1="13" x2="8" y2="13"/>
                      <line x1="16" y1="17" x2="8" y2="17"/>
                    </svg>
                  </div>
                  <div>
                    <h3 class="text-xl font-semibold">Council Resolution</h3>
                    <p class="text-sm text-[--fg-muted]">Generated summary</p>
                  </div>
                </div>
                
                <div class="prose prose-lg max-w-none mb-6">
                  ${msg.content}
                </div>

                <div class="border-t border-[--border] pt-6">
                  <p class="text-sm font-medium mb-3">Download Report</p>
                  <div class="flex flex-wrap gap-2">
                    <button class="download-btn px-4 py-2 bg-[--bg-warm] rounded-xl text-sm font-medium hover:bg-[--bg] transition-colors flex items-center gap-2" data-format="pdf">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                        <path d="M14 2v6h6"/>
                      </svg>
                      PDF
                    </button>
                    <button class="download-btn px-4 py-2 bg-[--bg-warm] rounded-xl text-sm font-medium hover:bg-[--bg] transition-colors flex items-center gap-2" data-format="html">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="16 18 22 12 16 6"/>
                        <polyline points="8 6 2 12 8 18"/>
                      </svg>
                      HTML
                    </button>
                    <button class="download-btn px-4 py-2 bg-[--bg-warm] rounded-xl text-sm font-medium hover:bg-[--bg] transition-colors flex items-center gap-2" data-format="md">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                        <path d="M9 15l2-2 2 2"/>
                        <path d="M9 11l2 2 2-2"/>
                      </svg>
                      Markdown
                    </button>
                    <button class="download-btn px-4 py-2 bg-[--bg-warm] rounded-xl text-sm font-medium hover:bg-[--bg] transition-colors flex items-center gap-2" data-format="txt">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                        <line x1="16" y1="13" x2="8" y2="13"/>
                        <line x1="16" y1="17" x2="8" y2="17"/>
                      </svg>
                      Text
                    </button>
                  </div>
                </div>
              </div>
            </div>
          `;
        }
      }).join('');
      
      container.scrollTop = container.scrollHeight;
    }

    function renderDebateMessages() {
      const container = document.getElementById('debate-messages');
      
      let html = `
        <div class="text-center mb-6">
          <div class="inline-flex items-center gap-2 px-3 py-1.5 bg-[--gold-soft] rounded-full text-sm font-medium text-[--gold]">
            <span class="w-2 h-2 rounded-full bg-[--gold] pulse-gold"></span>
            Live Debate
          </div>
        </div>
      `;
      
      let currentPhase = null;
      
      debateMessages.forEach((msg, index) => {
        // Add phase divider
        if (msg.phase !== currentPhase) {
          currentPhase = msg.phase;
          const phaseLabels = {
            'position': 'Initial Positions',
            'response': 'Cross-Examination',
            'consensus': 'Building Consensus'
          };
          html += `
            <div class="flex items-center gap-3 my-6">
              <div class="h-px flex-1 bg-[--border]"></div>
              <span class="text-xs text-[--fg-muted] uppercase tracking-wider font-medium">${phaseLabels[currentPhase]}</span>
              <div class="h-px flex-1 bg-[--border]"></div>
            </div>
          `;
        }
        
        const stanceClass = `stance-${msg.agent.stance}`;
        const stanceLabels = {
          'support': 'Supportive',
          'cautious': 'Cautious',
          'critical': 'Critical',
          'neutral': 'Neutral'
        };
        
        html += `
          <div class="message-animate bg-[--card] rounded-[--radius-sm] p-5 shadow-sm border border-[--border]" style="animation-delay: ${index * 80}ms">
            <div class="flex items-start gap-3 mb-3">
              <div class="w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold flex-shrink-0" style="background: ${msg.agent.color}15; color: ${msg.agent.color}">
                ${msg.agent.avatar}
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="font-semibold">${msg.agent.name}</span>
                  <span class="badge ${stanceClass} text-xs">${stanceLabels[msg.agent.stance]}</span>
                </div>
                <p class="text-sm text-[--fg-muted]">${msg.agent.role}</p>
              </div>
              <span class="text-xs text-[--fg-muted]">${formatTime(msg.timestamp)}</span>
            </div>
            
            <p class="text-base leading-relaxed mb-3">${msg.content}</p>
            
            ${msg.references && msg.references.length > 0 ? `
              <div class="pt-3 border-t border-[--border]">
                <p class="text-xs text-[--fg-muted] mb-2 flex items-center gap-1">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                  </svg>
                  References
                </p>
                <div class="flex flex-wrap gap-2">
                  ${msg.references.map(ref => `
                    <button class="reference-chip" data-ref-id="${ref.id}" onclick="showReference('${ref.id}')">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/>
                        <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/>
                      </svg>
                      ${ref.title}
                    </button>
                  `).join('')}
                </div>
              </div>
            ` : ''}
          </div>
        `;
      });
      
      container.innerHTML = html;
      container.scrollTop = container.scrollHeight;
    }

    // ==================== HELPERS ====================

    function formatTime(date) {
      return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
    }

    function showReference(refId) {
      const ref = documentReferences.find(r => r.id === refId);
      if (!ref) return;
      
      // Create modal
      const modal = document.createElement('div');
      modal.className = 'fixed inset-0 z-[100] flex items-center justify-center p-6';
      modal.innerHTML = `
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" onclick="this.parentElement.remove()"></div>
        <div class="relative bg-[--card] rounded-[--radius] p-8 max-w-lg w-full shadow-2xl animate-slide-in">
          <button onclick="this.parentElement.parentElement.remove()" class="absolute top-4 right-4 w-8 h-8 rounded-full bg-[--bg-warm] flex items-center justify-center hover:bg-[--bg] transition-colors">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
          <div class="flex items-start gap-4 mb-4">
            <div class="w-12 h-12 rounded-xl bg-[--gold-soft] flex items-center justify-center flex-shrink-0">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="text-[--gold]">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-semibold mb-1">${ref.title}</h3>
              <p class="text-[--fg-muted]">${ref.type}</p>
            </div>
          </div>
          <div class="bg-[--bg] rounded-xl p-4 mb-4">
            <p class="text-sm text-[--fg-muted] mb-1">Referenced Pages</p>
            <p class="font-semibold text-lg">${ref.pages}</p>
          </div>
          <div class="flex gap-2">
            <button class="flex-1 py-2.5 bg-[--accent] text-white rounded-xl font-medium text-sm hover:opacity-90 transition-opacity">
              Open Full Document
            </button>
            <button class="py-2.5 px-4 bg-[--bg-warm] rounded-xl font-medium text-sm hover:bg-[--bg] transition-colors">
              Copy Citation
            </button>
          </div>
        </div>
      `;
      document.body.appendChild(modal);
    }

    // ==================== PANEL CONTROLS ====================

    const panelOverlay = document.getElementById('panel-overlay');
    const councilPanel = document.getElementById('council-panel');
    const viewCouncilBtn = document.getElementById('view-council-btn');
    const closePanelBtn = document.getElementById('close-panel-btn');

    function openPanel() {
      councilPanel.classList.remove('translate-x-full');
      councilPanel.classList.add('animate-slide-in');
      panelOverlay.classList.add('active');
      renderDebateMessages();
    }

    function closePanel() {
      councilPanel.classList.add('animate-slide-out');
      panelOverlay.classList.remove('active');
      setTimeout(() => {
        councilPanel.classList.remove('animate-slide-out');
        councilPanel.classList.add('translate-x-full');
      }, 300);
    }

    viewCouncilBtn.addEventListener('click', openPanel);
    closePanelBtn.addEventListener('click', closePanel);
    panelOverlay.addEventListener('click', closePanel);

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closePanel();
    });

    // ==================== CHAT FUNCTIONALITY ====================

    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    function sendMessage() {
      const text = userInput.value.trim();
      if (!text) return;
      
      // Add user message
      chatMessages.push({
        id: chatMessages.length + 1,
        type: 'user',
        content: text,
        timestamp: new Date()
      });
      
      renderChatMessages();
      userInput.value = '';
      
      // Simulate system response
      setTimeout(() => {
        chatMessages.push({
          id: chatMessages.length + 1,
          type: 'system',
          content: 'The council has been convened. The agents are now analyzing your query from their respective ministerial perspectives. Click "View Council Debate" to observe the deliberation in real-time.',
          timestamp: new Date()
        });
        renderChatMessages();
      }, 1500);
      
      // Simulate summary after delay
      setTimeout(() => {
        chatMessages.push({
          id: chatMessages.length + 1,
          type: 'summary',
          content: `
            <h4 class="text-lg font-semibold mb-3">Executive Summary</h4>
            <p class="mb-4">Based on the council's deliberation, the following recommendations have emerged with high consensus:</p>
            <ol class="list-decimal list-inside space-y-3 mb-4">
              <li><strong>Extend Public Consultation Period</strong> — Increase from 14 to 30 days minimum to ensure Article 39 compliance.</li>
              <li><strong>Establish Consultation Infrastructure</strong> — Reallocate 2.4B KZT from Phase 1 budget.</li>
              <li><strong>Add Environmental Provisions</strong> — Include Ile-Alatau buffer zone protections.</li>
            </ol>
            <p class="text-[--fg-muted]">Consensus level: <span class="text-[--success] font-medium">High</span> (6/7 agents in agreement)</p>
          `,
          timestamp: new Date()
        });
        renderChatMessages();
      }, 4000);
    }

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    // Download buttons
    document.addEventListener('click', (e) => {
      if (e.target.closest('.download-btn')) {
        const format = e.target.closest('.download-btn').dataset.format;
        alert(`Downloading report as ${format.toUpperCase()}...`);
      }
    });

    // ==================== INITIALIZATION ====================

    document.addEventListener('DOMContentLoaded', () => {
      renderChatMessages();
    });
  </script>
</body>
</html>
