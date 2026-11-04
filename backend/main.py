from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import init_db, get_db_connection

app = FastAPI(title="Money Manager API")

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
        
        expenses = [dict(row) for row in rows]
        return expenses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/expenses/{expense_id}")
def update_expense(expense_id: int, expense: ExpenseCreate):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE expenses 
            SET title = ?, amount = ?, category = ?, date = ? 
            WHERE id = ?
            """,
            (expense.title, expense.amount, expense.category, expense.date, expense_id)
        )
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        
        if rows_affected == 0:
            raise HTTPException(status_code=404, detail="Expense not found")
            
        return {"message": "Expense updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/expenses/{expense_id}")
def delete_expense(expense_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        
        if rows_affected == 0:
            raise HTTPException(status_code=404, detail="Expense not found")
            
        return {"message": "Expense deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))