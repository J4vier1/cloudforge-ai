const sampleCsv = `vm_name,application_name,environment,business_owner,technical_owner,operating_system,os_version,current_platform,datacenter_location,target_cloud,target_region,cpu_cores,memory_gb,storage_gb,disk_count,average_cpu_percent,peak_cpu_percent,average_memory_percent,peak_memory_percent,average_disk_iops,average_disk_throughput_mbps,network_in_mbps,network_out_mbps,criticality,uptime_requirement,rpo_minutes,rto_minutes,backup_policy,maintenance_window,uses_active_directory,domain_joined,requires_static_ip,requires_vpn_connectivity,internet_access_required,listening_ports,dependency_flows,compliance_requirements,migration_notes
erp-app-01,ERP,prod,Finance,IT Operations,windows,Windows Server 2019,VMware,Mexico City DC1,azure,eastus,8,32,500,3,55,82,68,91,1200,80,25,18,high,99.9%,60,240,"Daily, 30 days","Sunday 01:00-04:00",true,true,true,true,false,"443;3389","erp-app-01->sql-prod-01:1433;erp-app-01->dc-01:389;erp-app-01->fileserver-01:445",ISO 27001,Requires vendor validation before cutover
sql-prod-01,ERP Database,prod,Finance,DBA Team,windows,Windows Server 2019,VMware,Mexico City DC1,azure,eastus,16,64,2048,6,62,88,74,93,5500,240,40,35,mission_critical,99.95%,15,120,"Hourly, 35 days","Sunday 00:00-03:00",true,true,true,true,false,"1433;3389","sql-prod-01->dc-01:389;erp-app-01->sql-prod-01:1433",ISO 27001,Requires database backup validation and performance testing
vpn-gw-01,VPN Gateway,prod,Network,Network Operations,linux,Ubuntu Server 22.04,Hyper-V,Mexico City DC1,huawei,la-santiago,4,16,200,2,72,91,64,78,600,45,90,120,high,99.9%,60,180,"Daily, 14 days","Saturday 23:00-02:00",false,false,true,true,true,"500;4500;22","vpn-gw-01->firewall-01:500;vpn-gw-01->firewall-01:4500",Internal Security Policy,Validate VPN tunnels and routing before migration
ad-dc-01,Active Directory,prod,IT,Identity Team,windows,Windows Server 2022,VMware,Mexico City DC1,azure,eastus,4,16,250,2,35,65,58,76,700,35,20,20,mission_critical,99.95%,15,120,"System state daily, 30 days","Sunday 02:00-05:00",true,true,true,true,false,"53;88;135;389;445;636;3389","ad-dc-01->dns-forwarder-01:53;all-prod-subnets->ad-dc-01:389",Internal Security Policy,Plan identity migration carefully and validate DNS dependency
web-dev-01,Customer Portal,dev,Digital,App Team,linux,Ubuntu Server 22.04,VMware,Mexico City DC1,azure,eastus,2,8,100,1,28,55,42,67,250,20,15,30,low,95%,1440,1440,"Weekly, 14 days","Any weekday after 19:00",false,false,false,false,true,"80;443;22","web-dev-01->api-dev-01:8080",None,Good candidate for rehost or containerization pilot`;

const state = {
  response: null,
  filter: "all",
  selectedVm: null,
};

const elements = {
  apiStatus: document.querySelector("#apiStatus"),
  inventoryFile: document.querySelector("#inventoryFile"),
  fileName: document.querySelector("#fileName"),
  loadSampleBtn: document.querySelector("#loadSampleBtn"),
  exportJsonBtn: document.querySelector("#exportJsonBtn"),
  exportCsvBtn: document.querySelector("#exportCsvBtn"),
  totalRows: document.querySelector("#totalRows"),
  validRows: document.querySelector("#validRows"),
  invalidRows: document.querySelector("#invalidRows"),
  avgReadiness: document.querySelector("#avgReadiness"),
  resultSummary: document.querySelector("#resultSummary"),
  resultsBody: document.querySelector("#resultsBody"),
  detailTitle: document.querySelector("#detailTitle"),
  detailSubtitle: document.querySelector("#detailSubtitle"),
  detailContent: document.querySelector("#detailContent"),
  toast: document.querySelector("#toast"),
  filters: document.querySelectorAll(".filter"),
};

async function checkApi() {
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error("Health check failed");
    elements.apiStatus.textContent = "Healthy";
  } catch {
    elements.apiStatus.textContent = "Unavailable";
  }
}

async function uploadInventory(file) {
  const formData = new FormData();
  formData.append("file", file);

  setBusy(true);
  try {
    const response = await fetch("/api/v1/inventory/upload", {
      method: "POST",
      body: formData,
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Inventory upload failed");
    }
    state.response = payload;
    state.selectedVm = firstValidAssessment(payload);
    render();
    showToast(`Processed ${payload.valid_rows} valid rows`);
  } catch (error) {
    showToast(error.message);
  } finally {
    setBusy(false);
  }
}

function render() {
  const validAssessments = getAssessments();
  const filtered = validAssessments.filter((assessment) => {
    return state.filter === "all" || assessment.risk_level === state.filter;
  });

  elements.totalRows.textContent = state.response?.total_rows ?? 0;
  elements.validRows.textContent = state.response?.valid_rows ?? 0;
  elements.invalidRows.textContent = state.response?.invalid_rows ?? 0;
  elements.avgReadiness.textContent = calculateAverageReadiness(validAssessments);
  elements.resultSummary.textContent = state.response
    ? `${filtered.length} VMs visible from ${validAssessments.length} assessed workloads.`
    : "Upload an inventory to generate results.";

  elements.exportJsonBtn.disabled = !state.response;
  elements.exportCsvBtn.disabled = !state.response;

  renderTable(filtered);
  renderDetail(state.selectedVm);
}

function renderTable(assessments) {
  if (!assessments.length) {
    elements.resultsBody.innerHTML = `<tr><td colspan="8" class="empty">No rows match the current filter.</td></tr>`;
    return;
  }

  elements.resultsBody.innerHTML = assessments
    .map((assessment) => {
      const selected = state.selectedVm?.vm_name === assessment.vm_name ? "selected" : "";
      return `
        <tr class="${selected}" data-vm="${escapeHtml(assessment.vm_name)}">
          <td><strong>${escapeHtml(assessment.vm_name)}</strong></td>
          <td>${escapeHtml(assessment.application_name || "-")}</td>
          <td>${escapeHtml(assessment.target_cloud)} / ${escapeHtml(assessment.target_region || "-")}</td>
          <td><span class="risk ${assessment.risk_level}">${escapeHtml(assessment.risk_level)}</span></td>
          <td><span class="score">${assessment.readiness_score}</span></td>
          <td>${assessment.recommended_sizing.cpu_cores}</td>
          <td>${assessment.recommended_sizing.memory_gb} GB</td>
          <td>${assessment.recommended_sizing.storage_gb} GB</td>
        </tr>
      `;
    })
    .join("");
}

function renderDetail(assessment) {
  if (!assessment) {
    elements.detailTitle.textContent = "VM detail";
    elements.detailSubtitle.textContent = "Select a VM from the results table.";
    elements.detailContent.className = "detail-empty";
    elements.detailContent.textContent = "No VM selected.";
    return;
  }

  elements.detailTitle.textContent = assessment.vm_name;
  elements.detailSubtitle.textContent = `${assessment.application_name || "Unassigned application"} · ${assessment.target_cloud}`;
  elements.detailContent.className = "";
  elements.detailContent.innerHTML = `
    <div class="detail-section">
      <div class="detail-kpis">
        <div class="mini-kpi"><span>Risk</span><strong>${escapeHtml(assessment.risk_level)}</strong></div>
        <div class="mini-kpi"><span>Readiness</span><strong>${assessment.readiness_score}</strong></div>
        <div class="mini-kpi"><span>Strategy</span><strong>${escapeHtml(assessment.migration_strategy)}</strong></div>
      </div>
    </div>
    <div class="detail-section">
      <h2>Recommended sizing</h2>
      <ul class="detail-list">
        <li>${assessment.recommended_sizing.cpu_cores} CPU cores</li>
        <li>${assessment.recommended_sizing.memory_gb} GB memory</li>
        <li>${assessment.recommended_sizing.storage_gb} GB storage</li>
      </ul>
    </div>
    <div class="detail-section">
      <h2>Recommendations</h2>
      <ul class="detail-list">${assessment.recommendations.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
    </div>
    <div class="detail-section">
      <h2>Next steps</h2>
      <ul class="detail-list">${assessment.next_steps.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
    </div>
  `;
}

function getAssessments() {
  return (state.response?.results || [])
    .map((item) => item.assessment)
    .filter(Boolean);
}

function firstValidAssessment(payload) {
  return payload.results.find((item) => item.assessment)?.assessment || null;
}

function calculateAverageReadiness(assessments) {
  if (!assessments.length) return 0;
  const total = assessments.reduce((sum, item) => sum + item.readiness_score, 0);
  return Math.round(total / assessments.length);
}

function exportJson() {
  if (!state.response) return;
  downloadFile("migration-assessment.json", JSON.stringify(state.response, null, 2), "application/json");
}

function exportCsv() {
  const rows = getAssessments();
  if (!rows.length) return;

  const header = [
    "vm_name",
    "application_name",
    "target_cloud",
    "target_region",
    "risk_level",
    "readiness_score",
    "recommended_cpu",
    "recommended_memory_gb",
    "recommended_storage_gb",
  ];
  const lines = rows.map((item) =>
    [
      item.vm_name,
      item.application_name || "",
      item.target_cloud,
      item.target_region || "",
      item.risk_level,
      item.readiness_score,
      item.recommended_sizing.cpu_cores,
      item.recommended_sizing.memory_gb,
      item.recommended_sizing.storage_gb,
    ]
      .map(csvEscape)
      .join(",")
  );

  downloadFile("migration-assessment-summary.csv", [header.join(","), ...lines].join("\n"), "text/csv");
}

function downloadFile(fileName, content, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  link.click();
  URL.revokeObjectURL(url);
}

function setBusy(isBusy) {
  elements.loadSampleBtn.disabled = isBusy;
  elements.inventoryFile.disabled = isBusy;
}

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.add("show");
  window.setTimeout(() => elements.toast.classList.remove("show"), 2800);
}

function csvEscape(value) {
  const stringValue = String(value);
  if (stringValue.includes(",") || stringValue.includes('"') || stringValue.includes("\n")) {
    return `"${stringValue.replaceAll('"', '""')}"`;
  }
  return stringValue;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

elements.inventoryFile.addEventListener("change", (event) => {
  const file = event.target.files?.[0];
  if (!file) return;
  elements.fileName.textContent = file.name;
  uploadInventory(file);
});

elements.loadSampleBtn.addEventListener("click", () => {
  const file = new File([sampleCsv], "sample-inventory.csv", { type: "text/csv" });
  elements.fileName.textContent = file.name;
  uploadInventory(file);
});

elements.exportJsonBtn.addEventListener("click", exportJson);
elements.exportCsvBtn.addEventListener("click", exportCsv);

elements.resultsBody.addEventListener("click", (event) => {
  const row = event.target.closest("tr[data-vm]");
  if (!row) return;
  state.selectedVm = getAssessments().find((assessment) => assessment.vm_name === row.dataset.vm) || null;
  render();
});

elements.filters.forEach((button) => {
  button.addEventListener("click", () => {
    elements.filters.forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    state.filter = button.dataset.filter;
    render();
  });
});

checkApi();
render();
