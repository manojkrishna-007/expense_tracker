const API_URL = "http://127.0.0.1:8000/api/expenses";
let expenseChart = null;

// Set default date to today in the form
document.getElementById('date').valueAsDate = new Date();

async function loadDashboard() {
    try {
        const response = await fetch(API_URL);
        const expenses = await response.json();
        
        updateMetrics(expenses);
        updateTable(expenses);
        updateChart(expenses);
    } catch (error) {
        console.error("Error loading dashboard data:", error);
    }
}

function updateMetrics(expenses) {
    const totalSpent = expenses.reduce((sum, item) => sum + item.amount, 0);
    const totalCount = expenses.length;

    // Calculate top category
    let topCat = "-";
    if (totalCount > 0) {
        const catCounts = {};
        expenses.forEach(exp => {
            catCounts[exp.category] = (catCounts[exp.category] || 0) + exp.amount;
        });
        topCat = Object.keys(catCounts).reduce((a, b) => catCounts[a] > catCounts[b] ? a : b);
    }

    document.getElementById("totalSpent").textContent = `$${totalSpent.toFixed(2)}`;
    document.getElementById("totalCount").textContent = totalCount;
    document.getElementById("topCategory").textContent = topCat;
}

function updateTable(expenses) {
    const tbody = document.getElementById("expenseTableBody");
    tbody.innerHTML = "";

    if (expenses.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="px-6 py-4 text-center text-slate-400">No transactions recorded yet.</td></tr>`;
        return;
    }

    expenses.forEach(exp => {
        const tr = document.createElement("tr");
        tr.className = "hover:bg-slate-50 transition-colors";
        tr.innerHTML = `
            <td class="px-6 py-4 font-medium text-slate-900">${exp.title}</td>
            <td class="px-6 py-4"><span class="bg-slate-100 text-slate-700 text-xs px-2.5 py-1 rounded-full font-medium">${exp.category}</span></td>
            <td class="px-6 py-4 text-slate-500">${exp.date}</td>
            <td class="px-6 py-4 text-right font-semibold text-slate-900">$${exp.amount.toFixed(2)}</td>
        `;
        tbody.appendChild(tr);
    });
}

function updateChart(expenses) {
    const ctx = document.getElementById("expenseChart").getContext("2d");

    // Aggregate amounts by category
    const categoryTotals = {};
    expenses.forEach(exp => {
        categoryTotals[exp.category] = (categoryTotals[exp.category] || 0) + exp.amount;
    });

    const labels = Object.keys(categoryTotals);
    const data = Object.values(categoryTotals);

    if (expenseChart) {
        expenseChart.destroy(); // Destroy previous instance to avoid visual bugs on update
    }

    expenseChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#64748b'],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Handle Form Submission
document.getElementById("expenseForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const expenseData = {
        title: document.getElementById("title").value,
        amount: parseFloat(document.getElementById("amount").value),
        category: document.getElementById("category").value,
        date: document.getElementById("date").value
    };

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(expenseData)
        });

        if (response.ok) {
            document.getElementById("title").value = "";
            document.getElementById("amount").value = "";
            loadDashboard(); // Refresh metrics, table, and charts dynamically
        } else {
            alert("Failed to save transaction.");
        }
    } catch (error) {
        console.error("Error submitting form:", error);
    }
});

// Load data on page load
loadDashboard();