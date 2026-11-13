// INDUS-X Client Application Controller
document.addEventListener("DOMContentLoaded", () => {
    let activeScenario = 1; // Default to Scenario 1 (Missing Bolt)
    let currentRole = "QUALITY_ENGINEER";
    let activeIncidentId = "QI-0041";
    let activeEventSource = null;
    let isSplitMode = false;

    // DOM Elements
    const scenarioBtns = document.querySelectorAll(".scenario-btn");
    const runBtn = document.getElementById("runScenarioBtn");
    const perturbationSelect = document.getElementById("perturbationSelect");
    const roleSelector = document.getElementById("roleSelector");
    const liveFeedImg = document.getElementById("liveFeedImg");
    const videoPlaceholder = document.getElementById("videoPlaceholder");
    const hudDefectBadge = document.getElementById("hudDefectBadge");
    const q1StatusTag = document.getElementById("q1StatusTag");

    // Quadrant 2 Elements
    const q2Card = document.getElementById("q2Card");
    const rawDetectionsVal = document.getElementById("rawDetectionsVal");
    const consolidatedVal = document.getElementById("consolidatedVal");
    const noiseReductionVal = document.getElementById("noiseReductionVal");
    const activeIncId = document.getElementById("activeIncId");
    const activeDefectBadge = document.getElementById("activeDefectBadge");
    const activeIncDesc = document.getElementById("activeIncDesc");
    const activeIncConf = document.getElementById("activeIncConf");
    const blockIndexText = document.getElementById("blockIndexText");
    const prevHashText = document.getElementById("prevHashText");
    const currHashText = document.getElementById("currHashText");
    const provenanceBadge = document.getElementById("provenanceBadge");
    const verifyLedgerBtn = document.getElementById("verifyLedgerBtn");
    const simulateTamperBtn = document.getElementById("simulateTamperBtn");

    // Quadrant 3 Elements
    const slaAgentBriefText = document.getElementById("slaAgentBriefText");
    const btnApproveQuarantine = document.getElementById("btnApproveQuarantine");
    const btnRejectQuarantine = document.getElementById("btnRejectQuarantine");
    const roleGateHint = document.getElementById("roleGateHint");

    // Quadrant 4 Elements
    const macroPatternText = document.getElementById("macroPatternText");
    const vendorXScore = document.getElementById("vendorXScore");
    const vendorXBar = document.getElementById("vendorXBar");
    const tpRateVal = document.getElementById("tpRateVal");
    const feedbackBtns = document.querySelectorAll(".feedback-btn");

    // Modal Elements
    const tamperModal = document.getElementById("tamperModal");
    const modalTitle = document.getElementById("modalTitle");
    const modalBody = document.getElementById("modalBody");
    const closeModalBtn = document.getElementById("closeModalBtn");
    const modalOkBtn = document.getElementById("modalOkBtn");
    const modalResetBtn = document.getElementById("modalResetBtn");
    const toggleSplitBtn = document.getElementById("toggleSplitBtn");
    const splitBtnText = document.getElementById("splitBtnText");

    // ─────────────────────────────────────────────────────────────
    // 1. Scenario Selection
    // ─────────────────────────────────────────────────────────────
    scenarioBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            scenarioBtns.forEach(b => {
                b.classList.remove("active-scenario", "btn-primary");
                b.classList.add("btn-secondary");
            });
            btn.classList.add("active-scenario", "btn-primary");
            btn.classList.remove("btn-secondary");
            activeScenario = parseInt(btn.dataset.scenario, 10);
            updatePreScenarioState(activeScenario);
        });
    });

    function updatePreScenarioState(scenarioId) {
        if (scenarioId === 0) {
            hudDefectBadge.textContent = "ALL FASTENERS LOCKED";
            hudDefectBadge.className = "mono-font text-[10px] bg-emerald-950/80 px-2 py-0.5 rounded text-emerald-400 border border-emerald-800/40";
        } else if (scenarioId === 1) {
            hudDefectBadge.textContent = "SLOT C: ABSENT (TESTING)";
            hudDefectBadge.className = "mono-font text-[10px] bg-rose-950/80 px-2 py-0.5 rounded text-rose-400 border border-rose-800/40";
        } else if (scenarioId === 2) {
            hudDefectBadge.textContent = "SLOT C: WRONG CLASS";
            hudDefectBadge.className = "mono-font text-[10px] bg-amber-950/80 px-2 py-0.5 rounded text-amber-400 border border-amber-800/40";
        } else if (scenarioId === 3) {
            hudDefectBadge.textContent = "SURFACE ANOMALY";
            hudDefectBadge.className = "mono-font text-[10px] bg-rose-950/80 px-2 py-0.5 rounded text-rose-400 border border-rose-800/40";
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 2. Stream & Execution Controller
    // ─────────────────────────────────────────────────────────────
    runBtn.addEventListener("click", async () => {
        const perturbation = perturbationSelect.value;
        runBtn.disabled = true;
        runBtn.innerHTML = `<span class="animate-spin mr-1">⚙</span> Streaming...`;
        q1StatusTag.textContent = "INSPECTING";
        q1StatusTag.className = "tech-badge badge-amber";

        videoPlaceholder.classList.add("hidden");
        liveFeedImg.classList.remove("hidden");

        // Close any prior SSE stream
        if (activeEventSource) {
            activeEventSource.close();
        }

        // Start SSE stream for video transit
        const streamUrl = `/api/inspect/stream/${activeScenario}?perturbation=${perturbation}`;
        activeEventSource = new EventSource(streamUrl);

        activeEventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            liveFeedImg.src = `data:image/jpeg;base64,${data.frame_base64}`;

            if (data.current_defect) {
                rawDetectionsVal.textContent = `${data.raw_detections_count} frames`;
                hudDefectBadge.textContent = `ALERT: ${data.current_defect}`;
                hudDefectBadge.className = "mono-font text-[10px] bg-rose-950/80 px-2 py-0.5 rounded text-rose-400 border border-rose-800/40 animate-pulse";
            }
        };

        activeEventSource.onerror = () => {
            activeEventSource.close();
        };

        // Concurrently run backend full pipeline execution
        try {
            const res = await fetch(`/api/inspect/run/${activeScenario}?perturbation=${perturbation}`, {
                method: "POST"
            });
            const result = await res.json();
            
            // Wait slightly so video stream finishes naturally
            setTimeout(() => {
                applyExecutionResults(result);
                runBtn.disabled = false;
                runBtn.innerHTML = `<i data-lucide="play" class="w-3.5 h-3.5 fill-white"></i><span>Execute Test Run</span>`;
                q1StatusTag.textContent = "COMPLETE";
                q1StatusTag.className = "tech-badge badge-green";
                lucide.createIcons();
            }, 1400);

        } catch (err) {
            console.error(err);
            runBtn.disabled = false;
            runBtn.innerHTML = `<i data-lucide="play" class="w-3.5 h-3.5 fill-white"></i><span>Execute Test Run</span>`;
            q1StatusTag.textContent = "ERROR";
            q1StatusTag.className = "tech-badge badge-red";
        }
    });

    function applyExecutionResults(result) {
        if (result.status === "PASS") {
            rawDetectionsVal.textContent = "0 raw";
            consolidatedVal.textContent = "0 Incidents";
            noiseReductionVal.textContent = "100%";
            activeIncId.textContent = "QI-NONE";
            activeDefectBadge.textContent = "NOMINAL_PASS";
            activeDefectBadge.className = "tech-badge badge-green";
            activeIncDesc.textContent = "All 4 fastener coordinates confirmed seated per CAD grid.";
            activeIncConf.textContent = "99.4%";
            slaAgentBriefText.textContent = "Assembly verified fully compliant with BOM tolerances. No contractual SLA action required.";
            return;
        }

        // Defect Scenario
        activeIncidentId = result.incident_id;
        rawDetectionsVal.textContent = `${result.raw_frame_count} frames`;
        consolidatedVal.textContent = `1 Record (${result.incident_id})`;
        noiseReductionVal.textContent = `${result.noise_reduction_pct}%`;
        
        activeIncId.textContent = result.incident_id;
        activeDefectBadge.textContent = result.defect_type;
        activeDefectBadge.className = result.defect_type === "WRONG_COMPONENT" ? "tech-badge badge-amber" : "tech-badge badge-red";
        activeIncDesc.textContent = `Consolidated across ${result.raw_frame_count} raw camera detections into 1 tamper-sealed record.`;
        activeIncConf.textContent = `${(result.confidence_avg * 100).toFixed(1)}%`;

        // Hash Block
        if (result.provenance_block) {
            blockIndexText.textContent = `Block #${result.provenance_block.block_index} (Sealed)`;
            prevHashText.textContent = result.provenance_block.prev_hash.substring(0, 24) + "...";
            currHashText.textContent = result.provenance_block.curr_hash.substring(0, 24) + "...";
        }

        // SLA Brief
        if (result.sla_dossier) {
            slaAgentBriefText.textContent = `"${result.sla_dossier.reasoning_summary}"`;
        }

        // Supplier Intelligence
        if (result.supplier_intelligence) {
            vendorXScore.textContent = `${result.supplier_intelligence.normalized_risk_score} / 100 [CRITICAL]`;
            vendorXBar.style.width = `${result.supplier_intelligence.normalized_risk_score}%`;
            macroPatternText.textContent = result.supplier_intelligence.pattern_description;
        }

        // Update Breadcrumb
        document.getElementById("brInc").textContent = result.incident_id;
    }

    // ─────────────────────────────────────────────────────────────
    // 3. Role-Based Access Control (RBAC) Switcher
    // ─────────────────────────────────────────────────────────────
    roleSelector.addEventListener("change", (e) => {
        currentRole = e.target.value;
        enforceRBAC();
    });

    function enforceRBAC() {
        if (currentRole === "OPERATOR") {
            btnApproveQuarantine.classList.add("btn-disabled");
            btnApproveQuarantine.disabled = true;
            btnRejectQuarantine.classList.add("btn-disabled");
            btnRejectQuarantine.disabled = true;
            roleGateHint.innerHTML = `<i data-lucide="lock" class="w-3 h-3 text-rose-400"></i><span class="text-rose-400">Locked: Requires Quality Engineer (Tier 2)</span>`;
        } else if (currentRole === "QUALITY_ENGINEER") {
            btnApproveQuarantine.classList.remove("btn-disabled");
            btnApproveQuarantine.disabled = false;
            btnRejectQuarantine.classList.remove("btn-disabled");
            btnRejectQuarantine.disabled = false;
            roleGateHint.innerHTML = `<i data-lucide="check" class="w-3 h-3 text-emerald-400"></i><span class="text-emerald-400">QE Authorized: 1-Click Batch Quarantine</span>`;
        } else if (currentRole === "PLANT_MANAGER") {
            btnApproveQuarantine.classList.remove("btn-disabled");
            btnApproveQuarantine.disabled = false;
            btnRejectQuarantine.classList.remove("btn-disabled");
            btnRejectQuarantine.disabled = false;
            roleGateHint.innerHTML = `<i data-lucide="award" class="w-3 h-3 text-cyan-400"></i><span class="text-cyan-400">Executive Authorized: Full Financial & Legal Sign-Off</span>`;
        }
        lucide.createIcons();
    }

    // Initial RBAC check
    enforceRBAC();

    // ─────────────────────────────────────────────────────────────
    // 4. Governance Action Execution
    // ─────────────────────────────────────────────────────────────
    btnApproveQuarantine.addEventListener("click", async () => {
        try {
            const res = await fetch(`/api/governance/${activeIncidentId}/decide`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    action: "APPROVE_QUARANTINE",
                    role: currentRole,
                    actor_name: currentRole === "PLANT_MANAGER" ? "R. Patel (Director)" : "S. Chen (Lead QE)",
                    notes: "Confirmed CAD tolerance failure at Slot C. Batch B-042 quarantined."
                })
            });
            const data = await res.json();
            if (data.success) {
                alert(`✅ GOVERNANCE DECISION SEALED: Batch B-042 placed on Quarantine Hold.\nSigned into Chain of Custody by ${data.authorized_by}.`);
                btnApproveQuarantine.innerHTML = `✓ Batch Quarantined`;
                btnApproveQuarantine.classList.add("btn-disabled");
                btnApproveQuarantine.disabled = true;
            } else {
                alert(`❌ Action Blocked: ${data.detail || data.error}`);
            }
        } catch (e) {
            console.error(e);
        }
    });

    btnRejectQuarantine.addEventListener("click", async () => {
        const notes = prompt("Enter engineering override notes for rejecting containment:");
        if (!notes) return;
        try {
            const res = await fetch(`/api/governance/${activeIncidentId}/decide`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    action: "REJECT_QUARANTINE",
                    role: currentRole,
                    actor_name: "Lead Engineer",
                    notes: notes
                })
            });
            const data = await res.json();
            alert(`Override Recorded: Status updated to ${data.new_status}`);
        } catch (e) {
            console.error(e);
        }
    });

    // ─────────────────────────────────────────────────────────────
    // 5. Cryptographic Provenance & Tamper Demonstration
    // ─────────────────────────────────────────────────────────────
    verifyLedgerBtn.addEventListener("click", async () => {
        try {
            const res = await fetch("/api/provenance/verify");
            const data = await res.json();
            
            modalTitle.innerHTML = `<i data-lucide="shield-check" class="w-4 h-4 text-emerald-400"></i> Cryptographic Ledger Verification`;
            if (data.valid) {
                modalBody.innerHTML = `
                    <div class="text-emerald-400 font-bold mb-1">✓ INTEGRITY VERIFICATION CONFIRMED</div>
                    <div>All <span class="font-bold text-white">${data.total_blocks}</span> append-only blocks were recomputed from GENESIS_BLOCK to H_n.</div>
                    <div class="bg-[#090d15] p-2 rounded text-[11px] text-slate-400 mt-2 border border-[#192233]">
                        No broken SHA-256 links detected. Digital chain of custody is legally sound.
                    </div>
                `;
                provenanceBadge.textContent = "✓ LEDGER VERIFIED";
                provenanceBadge.className = "tech-badge badge-green";
                q2Card.classList.remove("breach-alert-active");
            } else {
                modalTitle.innerHTML = `<i data-lucide="shield-alert" class="w-4 h-4 text-rose-500"></i> SECURITY INTEGRITY BREACH!`;
                modalBody.innerHTML = `
                    <div class="text-rose-400 font-bold mb-1">🚨 INTEGRITY BREACH DETECTED AT BLOCK #${data.breached_block_id}</div>
                    <div class="text-slate-300">A historical database record has been illegally modified by an external actor!</div>
                    <div class="bg-[#240e15] p-2 rounded text-[11px] text-rose-200 mt-2 border border-rose-900/60 font-mono">
                        <div>EXPECTED: ${data.expected_hash}</div>
                        <div>DETECTED: ${data.found_hash}</div>
                    </div>
                    <div class="text-[11px] text-rose-400 mt-1">Chain of custody is invalidated from Block #${data.breached_block_id} onwards.</div>
                `;
                provenanceBadge.textContent = "🚨 INTEGRITY BREACH";
                provenanceBadge.className = "tech-badge badge-red";
                q2Card.classList.add("breach-alert-active");
            }
            tamperModal.classList.remove("hidden");
            lucide.createIcons();
        } catch (e) {
            console.error(e);
        }
    });

    simulateTamperBtn.addEventListener("click", async () => {
        try {
            const res = await fetch("/api/provenance/simulate-tamper", { method: "POST" });
            const data = await res.json();
            
            // Automatically trigger verification to illustrate live detection
            setTimeout(() => {
                verifyLedgerBtn.click();
            }, 300);
        } catch (e) {
            console.error(e);
        }
    });

    modalResetBtn.addEventListener("click", async () => {
        try {
            await fetch("/api/provenance/repair", { method: "POST" });
            tamperModal.classList.add("hidden");
            provenanceBadge.textContent = "✓ LEDGER VERIFIED";
            provenanceBadge.className = "tech-badge badge-green";
            q2Card.classList.remove("breach-alert-active");
            alert("Ledger hashes recalibrated and reset to pristine state.");
        } catch (e) {
            console.error(e);
        }
    });

    closeModalBtn.addEventListener("click", () => tamperModal.classList.add("hidden"));
    modalOkBtn.addEventListener("click", () => tamperModal.classList.add("hidden"));

    // ─────────────────────────────────────────────────────────────
    // 6. Operator Feedback Loop (Learn Stage)
    // ─────────────────────────────────────────────────────────────
    feedbackBtns.forEach(btn => {
        btn.addEventListener("click", async () => {
            const verdict = btn.dataset.verdict;
            try {
                const res = await fetch(`/api/incidents/${activeIncidentId}/feedback`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ verdict })
                });
                const data = await res.json();
                tpRateVal.textContent = `${data.accuracy_metrics.confirmed_true_positives_pct}%`;
                btn.classList.add("bg-blue-600", "text-white");
                setTimeout(() => btn.classList.remove("bg-blue-600", "text-white"), 1200);
            } catch (e) {
                console.error(e);
            }
        });
    });

    // ─────────────────────────────────────────────────────────────
    // 7. Split Comparison Mode Toggle (Dumb vs Smart)
    // ─────────────────────────────────────────────────────────────
    toggleSplitBtn.addEventListener("click", () => {
        isSplitMode = !isSplitMode;
        if (isSplitMode) {
            splitBtnText.textContent = "Normal Command Center";
            toggleSplitBtn.classList.replace("btn-secondary", "btn-primary");
            alert("Split Mode Active:\nComparing Standard Hackathon CV (Left: 27 Raw Alerts, No Hash, No Automation) vs INDUS-X (Right: 1 Consolidated Incident, SHA-256 Sealed, Diverter Pulsed, Contract Cited).");
        } else {
            splitBtnText.textContent = "Split Mode (Dumb vs Smart)";
            toggleSplitBtn.classList.replace("btn-primary", "btn-secondary");
        }
    });

    // Load initial scenario pre-display
    updatePreScenarioState(1);
});

