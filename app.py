import os
import threading
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from facebook_comment_clicker import FacebookCommentClicker

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Clave secreta para sesiones

# Configuración de usuarios (en un escenario real, usarías una base de datos)
USERS = {
    'admin': generate_password_hash('password')
}

# Variable global para manejar el estado de la ejecución
current_thread = None
execution_log = []

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in USERS and check_password_hash(USERS[username], password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Credenciales inválidas')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/run_script', methods=['POST'])
def run_script():
    global current_thread

    # Validar que el usuario esté autenticado
    #if 'username' not in session:
    #    return jsonify({'status': 'error', 'message': 'No autenticado'}), 401

    # Obtener parámetros del formulario
    urls = request.form.get('urls', '').split(',')
    scroll_count = int(request.form.get('scroll_count', 100))
    click_delay = float(request.form.get('click_delay', 2))

    # Limpiar el log de ejecución anterior
    global execution_log
    execution_log.clear()

    def script_thread():
        global execution_log
        clicker = FacebookCommentClicker(urls=urls, scroll_count=scroll_count, click_delay=click_delay)
        
        # Sobreescribir el método de logging para guardar en memoria
        original_logger = clicker.logger
        
        class MemoryLogger:
            def info(self, message):
                execution_log.append({'type': 'info', 'message': message})
                original_logger.info(message)
            
            def error(self, message):
                execution_log.append({'type': 'error', 'message': message})
                original_logger.error(message)
        
        clicker.logger = MemoryLogger()
        
        try:
            clicker.run()
        except Exception as e:
            execution_log.append({'type': 'error', 'message': str(e)})

    # Iniciar el script en un hilo separado
    current_thread = threading.Thread(target=script_thread)
    current_thread.start()

    return jsonify({'status': 'running', 'message': 'Script iniciado'})

@app.route('/script_status')
def script_status():
    if current_thread is None:
        return jsonify({'status': 'not_running'})
    
    return jsonify({
        'status': 'running' if current_thread.is_alive() else 'completed',
        'log': execution_log
    })

if __name__ == '__main__':

    app.run(host="0.0.0.0", port=5000, debug= False)

