from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import init_db, get_db_connection

app = FastAPI(title="Expense Tracker API")

# Enable CORS so your frontend can communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
init_db()

# Pydantic model for request validation
class ExpenseCreate(BaseModel):
    title: str
    amount: float
    category: str
    date: str

@app.post("/api/expenses")
def add_expense(expense: ExpenseCreate):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (title, amount, category, date) VALUES (?, ?, ?, ?)",
            (expense.title, expense.amount, expense.category, expense.date)
        )
        conn.commit()
        conn.close()
        return {"message": "Expense added successfully", "data": expense.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/expenses")
def get_expenses():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        # Convert rows to a clean list of dictionaries
        expenses = [dict(row) for row in rows]
        return expenses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))