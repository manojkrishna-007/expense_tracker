from fastapi import FastAPI, HTTPException, Response, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import init_db, get_db_connection
from auth import hash_password, verify_password, create_session_token, verify_session_token

app = FastAPI(title="Money Manager API with Auth")

# Fixed CORS middleware to properly handle preflight and credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500", "http://127.0.0.1:3000", "http://localhost:3000", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

# --- Schemas ---
class UserAuth(BaseModel):
    username: str
    password: str

class ExpenseCreate(BaseModel):
    title: str
    amount: float
    category: str
    date: str

# --- Security Dependency Guard ---
def get_current_user_id(request: Request) -> int:
    session_token = request.cookies.get("session")
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    user_id = verify_session_token(session_token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")
    
    return user_id

# --- Auth Endpoints ---
@app.post("/api/register")
def register(user: UserAuth):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE username = ?", (user.username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_pwd = hash_password(user.password)
    cursor.execute("INSERT INTO users (username, hashed_password) VALUES (?, ?)", (user.username, hashed_pwd))
    conn.commit()
    conn.close()
    
    return {"message": "User registered successfully"}

@app.post("/api/login")
def login(user: UserAuth, response: Response):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, hashed_password FROM users WHERE username = ?", (user.username,))
    row = cursor.fetchone()
    conn.close()
    
    if not row or not verify_password(user.password, row["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate signed session token and set HTTP-only cookie
    token = create_session_token(row["id"])
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,  # Protects against XSS token theft
        samesite="lax",
        secure = False,
        max_age=86400
    )
    return {"message": "Logged in successfully"}

@app.post("/api/logout")
def logout(response: Response):
    response.delete_cookie("session")
    return {"message": "Logged out successfully"}

# --- Protected Expense Endpoints (Scoped to user_id) ---
@app.post("/api/expenses")
def add_expense(expense: ExpenseCreate, user_id: int = Depends(get_current_user_id)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (user_id, title, amount, category, date) VALUES (?, ?, ?, ?, ?)",
        (user_id, expense.title, expense.amount, expense.category, expense.date)
    )
    conn.commit()
    conn.close()
    return {"message": "Expense added successfully"}

@app.get("/api/expenses")
def get_expenses(user_id: int = Depends(get_current_user_id)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, amount, category, date FROM expenses WHERE user_id = ? ORDER BY id DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

@app.put("/api/expenses/{expense_id}")
def update_expense(expense_id: int, expense: ExpenseCreate, user_id: int = Depends(get_current_user_id)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE expenses 
        SET title = ?, amount = ?, category = ?, date = ? 
        WHERE id = ? AND user_id = ?
        """,
        (expense.title, expense.amount, expense.category, expense.date, expense_id, user_id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Expense not found or unauthorized")
        
    return {"message": "Expense updated successfully"}

@app.delete("/api/expenses/{expense_id}")
def delete_expense(expense_id: int, user_id: int = Depends(get_current_user_id)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user_id))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Expense not found or unauthorized")
        
    return {"message": "Expense deleted successfully"}