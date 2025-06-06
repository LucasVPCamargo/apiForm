from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import sqlite3
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Configurações
        DB_PATH = '/tmp/dados_formulario.db'  # Usando /tmp no Vercel
        
        # 1. Verificar tamanho do conteúdo
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            # 2. Parse dos dados JSON
            dados = json.loads(post_data)
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'error',
                'message': 'Formato JSON inválido'
            }).encode())
            return
        
        # 3. Validar campos obrigatórios
        required_fields = [
            'nome', 'sobrenome', 'email', 'telefone',
            'mercado_apostas', 'trabalha_trafego',
            'porque_upbet', 'considera'
        ]
        
        missing_fields = [field for field in required_fields if field not in dados or not dados[field]]
        if missing_fields:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'error',
                'message': f'Campos obrigatórios faltando: {", ".join(missing_fields)}'
            }).encode())
            return
        
        # 4. Preparar dados para o banco
        dados_db = {
            'nome': dados.get('nome', ''),
            'sobrenome': dados.get('sobrenome', ''),
            'cpf': dados.get('cpf', ''),
            'email': dados.get('email', ''),
            'data_nascimento': dados.get('data_nascimento', ''),
            'telefone': dados.get('telefone', ''),
            'mercado_apostas': dados.get('mercado_apostas', ''),
            'redes_sociais': dados.get('redes_sociais', ''),
            'trabalha_trafego': dados.get('trabalha_trafego', ''),
            'tipo_trafego': dados.get('tipo_trafego', ''),
            'porque_upbet': dados.get('porque_upbet', ''),
            'considera': dados.get('considera', ''),
            'data_cadastro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 5. Conexão com o banco de dados
        try:
            # Criar banco de dados se não existir
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Criar tabela se não existir
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS formularios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    sobrenome TEXT NOT NULL,
                    cpf TEXT,
                    email TEXT NOT NULL,
                    data_nascimento TEXT,
                    telefone TEXT NOT NULL,
                    mercado_apostas TEXT NOT NULL,
                    redes_sociais TEXT,
                    trabalha_trafego TEXT NOT NULL,
                    tipo_trafego TEXT,
                    porque_upbet TEXT NOT NULL,
                    considera TEXT NOT NULL,
                    data_cadastro TEXT NOT NULL
                )
            ''')
            
            # Inserir dados
            cursor.execute('''
                INSERT INTO formularios (
                    nome, sobrenome, cpf, email, data_nascimento, telefone,
                    mercado_apostas, redes_sociais, trabalha_trafego, tipo_trafego,
                    porque_upbet, considera, data_cadastro
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dados_db['nome'], dados_db['sobrenome'], dados_db['cpf'],
                dados_db['email'], dados_db['data_nascimento'], dados_db['telefone'],
                dados_db['mercado_apostas'], dados_db['redes_sociais'],
                dados_db['trabalha_trafego'], dados_db['tipo_trafego'],
                dados_db['porque_upbet'], dados_db['considera'],
                dados_db['data_cadastro']
            ))
            
            conn.commit()
            conn.close()
            
            # Resposta de sucesso
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'success',
                'message': 'Dados salvos com sucesso!'
            }).encode())
            
        except Exception as e:
            # Resposta de erro
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'error',
                'message': f'Erro ao salvar dados: {str(e)}'
            }).encode())