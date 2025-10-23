from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>Production System - Perusahaan XYZ</h1>
    <p>Employee Management Portal</p>
    <div>
        <a href="/employees">Data Karyawan</a> | 
        <a href="/payroll">Penggajian</a> |
        <a href="/reports">Laporan</a>
    </div>
    '''

@app.route('/employees')
def employees():
    return jsonify({"status": "success", "data": "Employee database"})

@app.route('/payroll')
def payroll():
    return jsonify({"status": "success", "data": "Payroll system"})

@app.route('/reports')
def reports():
    return jsonify({"status": "success", "data": "Financial reports"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
