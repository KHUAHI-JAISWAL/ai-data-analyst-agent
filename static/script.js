document.addEventListener("DOMContentLoaded", function () {

    const fileInput = document.getElementById("csvFile");
    const runBtn = document.getElementById("runBtn");
    const fileName = document.getElementById("fileName");

    // Enable button when file selected
    fileInput.addEventListener("change", function () {
        if (fileInput.files.length > 0) {
            runBtn.disabled = false;
            fileName.innerText = fileInput.files[0].name;
        }
    });

    // Run pipeline
    window.runPipeline = async function () {
        const file = fileInput.files[0];

        if (!file) {
            alert("Please select a file first!");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch("/analyze", {
                method: "POST",
                body: formData
            });

            if (!res.ok) {
                const text = await res.text();
                console.error("Server Error:", text);
                alert("Server Error! Check terminal ⚠️");
                return;
            }

            const data = await res.json();
            console.log("Response:", data);

            if (data.error) {
                alert("Error: " + data.error);
                return;
            }

            alert("Processing Done ✅");

            // ✅ SHOW INSIGHTS
            const insightList = document.getElementById("insightList");
            if (insightList && data.insights) {
                insightList.innerHTML = "";
                data.insights.forEach(i => {
                    const li = document.createElement("li");
                    li.innerText = i;
                    insightList.appendChild(li);
                });
            }

            // 🔥 SHOW CHARTS
            const chartsGrid = document.getElementById("chartsGrid");
            if (chartsGrid && data.charts && data.charts.length > 0) {
                chartsGrid.innerHTML = "";

                data.charts.forEach(chart => {
                    const img = document.createElement("img");
                    img.src = `/charts/${chart}`;
                    img.style.width = "100%";
                    img.style.marginTop = "15px";
                    img.style.borderRadius = "10px";
                    img.style.boxShadow = "0 4px 10px rgba(0,0,0,0.2)";
                    chartsGrid.appendChild(img);
                });
            }

            // 🔥 SHOW STATS TABLE
            const statsBody = document.getElementById("statsBody");
            if (statsBody && data.numeric_stats) {
                statsBody.innerHTML = "";

                data.numeric_stats.forEach(stat => {
                    const row = `
                        <tr>
                            <td>${stat.column}</td>
                            <td>${stat.mean}</td>
                            <td>${stat.median}</td>
                            <td>${stat.std}</td>
                            <td>${stat.min}</td>
                            <td>${stat.max}</td>
                            <td>${stat.range}</td>
                        </tr>
                    `;
                    statsBody.innerHTML += row;
                });
            }

            // 🔥 SHOW AGENT LOGS
            if (data.agent_logs) {
                document.getElementById("log-clean").innerHTML =
                    data.agent_logs.cleaning.join("<br>");

                document.getElementById("log-analysis").innerHTML =
                    data.agent_logs.analysis.join("<br>");

                document.getElementById("log-insight").innerHTML =
                    data.agent_logs.insights.join("<br>");
            }

            // ✅ SHOW RESULTS SECTION
            document.getElementById("resultsSection").classList.remove("hidden");

        } catch (err) {
            console.error("Fetch Error:", err);
            alert("Network / Server error ❌");
        }
    };

    // 🔥 TAB SWITCH FUNCTION (VERY IMPORTANT)
    window.showTab = function (tabId, event) {

        // Hide all panels
        const panels = document.querySelectorAll(".log-panel");
        panels.forEach(p => p.classList.add("hidden"));

        // Show selected panel
        const activePanel = document.getElementById(tabId);
        if (activePanel) {
            activePanel.classList.remove("hidden");
        }

        // Remove active class from all tabs
        const tabs = document.querySelectorAll(".tab");
        tabs.forEach(t => t.classList.remove("active"));

        // Add active class to clicked tab
        event.target.classList.add("active");
    };

});