from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3307,
        user="root",
        password="Blessy@143",
        database="hr_connect"
    )


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "HR Connect Backend is running successfully!"
    })


@app.route("/api/health", methods=["GET"])
def health():
    conn = None

    try:
        conn = get_db_connection()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "HR Connect backend and MySQL database are connected"
        })

    except Exception as e:

        if conn and conn.is_connected():
            conn.close()

        return jsonify({
            "status": "error",
            "message": "Database connection failed",
            "error": str(e)
        }), 500


@app.route("/api/employees", methods=["GET"])
def get_employees():

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT employee_id,
                   full_name,
                   email,
                   department,
                   designation
            FROM employees
            WHERE role = %s
            ORDER BY employee_id
        """

        cursor.execute(query, ("employee",))

        employees = cursor.fetchall()

        return jsonify({
            "success": True,
            "employees": employees
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Unable to fetch employees",
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conn and conn.is_connected():
            conn.close()


@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Please provide login details"
        }), 400

    role = data.get("role")
    password = data.get("password")
    employee_id = data.get("employee_id")

    if role not in ["employee", "hr"]:
        return jsonify({
            "success": False,
            "message": "Invalid role"
        }), 400

    if not employee_id:
        return jsonify({
            "success": False,
            "message": "Employee ID is required"
        }), 400

    if not password:
        return jsonify({
            "success": False,
            "message": "Password is required"
        }), 400

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT id,
                   employee_id,
                   full_name,
                   email,
                   department,
                   designation,
                   role
            FROM employees
            WHERE employee_id = %s
              AND password = %s
              AND role = %s
        """

        cursor.execute(
            query,
            (employee_id, password, role)
        )

        user = cursor.fetchone()

        if user:

            return jsonify({
                "success": True,
                "message": "Login successful",
                "user": user
            }), 200

        return jsonify({
            "success": False,
            "message": "Invalid login details"
        }), 401

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Database error",
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conn and conn.is_connected():
            conn.close()


@app.route("/api/employee/<employee_id>/dashboard", methods=["GET"])
def employee_dashboard(employee_id):

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Employee details
        cursor.execute(
            """
            SELECT employee_id,
                   full_name,
                   email,
                   department,
                   designation,
                   DATE_FORMAT(joining_date, '%%Y-%%m-%%d') AS joining_date
            FROM employees
            WHERE employee_id = %s
              AND role = %s
            """,
            (employee_id, "employee")
        )

        employee = cursor.fetchone()

        if not employee:

            return jsonify({
                "success": False,
                "message": "Employee not found"
            }), 404


        # Attendance
        cursor.execute(
            """
            SELECT
                DATE_FORMAT(attendance_date, '%%Y-%%m-%%d') AS attendance_date,
                TIME_FORMAT(check_in, '%%H:%%i:%%s') AS check_in,
                TIME_FORMAT(check_out, '%%H:%%i:%%s') AS check_out,
                status
            FROM attendance
            WHERE employee_id = %s
            ORDER BY attendance_date DESC
            """,
            (employee_id,)
        )

        attendance = cursor.fetchall()


        # Payroll
        cursor.execute(
            """
            SELECT
                salary_month,
                CAST(basic_salary AS CHAR) AS basic_salary,
                CAST(allowances AS CHAR) AS allowances,
                CAST(deductions AS CHAR) AS deductions,
                CAST(net_salary AS CHAR) AS net_salary,
                payment_status,
                DATE_FORMAT(paid_on, '%%Y-%%m-%%d') AS paid_on
            FROM payroll
            WHERE employee_id = %s
            ORDER BY id DESC
            """,
            (employee_id,)
        )

        payroll = cursor.fetchall()


        # Leave requests
        cursor.execute(
            """
            SELECT
                leave_type,
                DATE_FORMAT(start_date, '%%Y-%%m-%%d') AS start_date,
                DATE_FORMAT(end_date, '%%Y-%%m-%%d') AS end_date,
                reason,
                status,
                DATE_FORMAT(applied_on, '%%Y-%%m-%%d %%H:%%i:%%s') AS applied_on
            FROM leave_requests
            WHERE employee_id = %s
            ORDER BY id DESC
            """,
            (employee_id,)
        )

        leave_requests = cursor.fetchall()


        # Performance
        cursor.execute(
            """
            SELECT
                review_period,
                CAST(rating AS CHAR) AS rating,
                feedback,
                DATE_FORMAT(reviewed_on, '%%Y-%%m-%%d %%H:%%i:%%s') AS reviewed_on
            FROM performance_evaluations
            WHERE employee_id = %s
            ORDER BY id DESC
            """,
            (employee_id,)
        )

        performance = cursor.fetchall()


        # Documents
        cursor.execute(
            """
            SELECT *
            FROM employee_documents
            WHERE employee_id = %s
            ORDER BY id DESC
            """,
            (employee_id,)
        )

        documents = cursor.fetchall()


        return jsonify({
            "success": True,
            "employee": employee,
            "attendance": attendance,
            "payroll": payroll,
            "leave_requests": leave_requests,
            "performance": performance,
            "documents": documents
        }), 200


    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Unable to fetch employee dashboard",
            "error": str(e)
        }), 500


    finally:

        if cursor:
            cursor.close()

        if conn and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    app.run(debug=True)