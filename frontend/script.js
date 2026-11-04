const API_URL = "http://127.0.0.1:8000/api/expenses";
let expenseChart = null;
let editingId = null; 
let allExpenses = []; // Holds all fetched expenses for client-side filtering

// Set default date to today in the form
document.getElementById('date').valueAsDate = new Date();

async function loadDashboard() {
    try {
        const response = await fetch(API_URL, {
            credentials: "include"
        });
        
        if (response.status === 401) {
            window.location.href = "login.html";
            return;
        }

        allExpenses = await response.json();
        
        updateMetrics(allExpenses);
        filterAndRenderTable();
        updateChart(allExpenses);
    } catch (error) {
        console.error("Error loading dashboard data:", error);
    }
}

function updateMetrics(expenses) {
    const totalSpent = expenses.reduce((sum, item) => sum + item.amount, 0);
    const totalCount = expenses.length;

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

// Filters expenses based on search input and category dropdown, then renders table
function filterAndRenderTable() {
    const searchQuery = document.getElementById("searchFilter").value.toLowerCase();
    const selectedCategory = document.getElementById("categoryFilter").value;

    const filtered = allExpenses.filter(exp => {
        const matchesSearch = exp.title.toLowerCase().includes(searchQuery);
        const matchesCategory = selectedCategory === "" || exp.category === selectedCategory;
        return matchesSearch && matchesCategory;
    });

    updateTable(filtered);
}

function updateTable(expenses) {
    const tbody = document.getElementById("expenseTableBody");
    tbody.innerHTML = "";

    if (expenses.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #7f8c8d; padding: 20px;">No matching transactions found.</td></tr>`;
        return;
    }

    expenses.forEach(exp => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><strong>${exp.title}</strong></td>
            <td><span class="badge">${exp.category}</span></td>
            <td>${exp.date}</td>
            <td class="text-right"><strong>$${exp.amount.toFixed(2)}</strong></td>
            <td class="text-right">
                <button onclick="editExpense(${exp.id}, '${exp.title}', ${exp.amount}, '${exp.category}', '${exp.date}')" style="background: none; border: none; color: #3498db; cursor: pointer; font-size: 0.85rem; margin-right: 8px; font-weight: 600;">Edit</button>
                <button onclick="deleteExpense(${exp.id})" style="background: none; border: none; color: #e74c3c; cursor: pointer; font-size: 0.85rem; font-weight: 600;">Delete</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function updateChart(expenses) {
    const ctx = document.getElementById("expenseChart").getContext("2d");

    const categoryTotals = {};
    expenses.forEach(exp => {
        categoryTotals[exp.category] = (categoryTotals[exp.category] || 0) + exp.amount;
    });

    const labels = Object.keys(categoryTotals);
    const data = Object.values(categoryTotals);

    if (expenseChart) {
        expenseChart.destroy();
    }

    expenseChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: ['#3498db', '#2ecc71', '#e67e22', '#e74c3c', '#9b59b6', '#95a5a6'],
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

// Event Listeners for Filters
document.getElementById("searchFilter").addEventListener("input", filterAndRenderTable);
document.getElementById("categoryFilter").addEventListener("change", filterAndRenderTable);

// Function to delete an expense
async function deleteExpense(id) {
    if (!confirm("Are you sure you want to delete this transaction?")) return;

    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: "DELETE",
            credentials: "include"
        });

        if (response.ok) {
            loadDashboard();
        } else {
            alert("Failed to delete transaction.");
        }
    } catch (error) {
        console.error("Error deleting expense:", error);
    }
}

// Function to populate form for editing
function editExpense(id, title, amount, category, date) {
    editingId = id;
    document.getElementById("title").value = title;
    document.getElementById("amount").value = amount;
    document.getElementById("category").value = category;
    document.getElementById("date").value = date;

    const submitBtn = document.querySelector("#expenseForm button[type='submit']");
    submitBtn.textContent = "Update Transaction";
    submitBtn.style.backgroundColor = "#e67e22";
}

// Handle Form Submission (Handles both Create & Update)
document.getElementById("expenseForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const expenseData = {
        title: document.getElementById("title").value,
        amount: parseFloat(document.getElementById("amount").value),
        category: document.getElementById("category").value,
        date: document.getElementById("date").value
    };

    let url = API_URL;
    let method = "POST";

    if (editingId !== null) {
        url = `${API_URL}/${editingId}`;
        method = "PUT";
    }

    try {
        const response = await fetch(url, {
            method: method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(expenseData),
            credentials: "include"
        });

        if (response.ok) {
            document.getElementById("expenseForm").reset();
            document.getElementById('date').valueAsDate = new Date();
            editingId = null;
            
            const submitBtn = document.querySelector("#expenseForm button[type='submit']");
            submitBtn.textContent = "Add Transaction";
            submitBtn.style.backgroundColor = "#3498db";

            loadDashboard();
        } else {
            alert("Failed to save transaction.");
        }
    } catch (error) {
        console.error("Error submitting form:", error);
    }
});

// Load data on page load
loadDashboard();