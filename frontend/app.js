"use strict";

async function checkSystem() {
    const connectionLabel = document.getElementById("connection-label");
    const systemStatus = document.getElementById("system-status");
    const statusDot = document.querySelector(".status-dot");

    try {
        const response = await fetch("/api/health");
        if (!response.ok) throw new Error("Health check failed");

        const data = await response.json();
        const appName = data.app || data.application || "LYRA AI STUDIO";

        connectionLabel.textContent = "Backend terhubung";
        systemStatus.textContent = `${appName} v${data.version} · Online`;
        statusDot.classList.add("online");
    } catch (error) {
        connectionLabel.textContent = "Backend tidak tersedia";
        systemStatus.textContent = "Backend connection failed";
        statusDot.classList.remove("online");
        console.error("LYRA health check error:", error);
    }
}

async function loadEngines() {
    try {
        const response = await fetch("/api/engines");
        if (!response.ok) throw new Error("Could not load engine registry");

        const data = await response.json();
        console.info("LYRA engine registry:", data);
    } catch (error) {
        console.error("LYRA engine registry error:", error);
    }
}

function setupEngineButtons() {
    document.querySelectorAll("[data-engine]").forEach((button) => {
        button.addEventListener("click", () => {
            const engine = button.dataset.engine;
            alert(
                `${engine.toUpperCase()} ENGINE\n\n` +
                "Modul ini belum diaktifkan. Status integrasi dapat diperiksa di Engine Registry."
            );
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    checkSystem();
    loadEngines();
    setupEngineButtons();
});
