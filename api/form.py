import os
from flask import Flask, request, jsonify
from google.oauth2 import service_account
import gspread
from dotenv import load_dotenv
import json

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Configurações do Google Sheets
SHEET_ID = os.getenv('SHEET_ID')  # Nome da variável de ambiente correta
SHEET_NAME = 'Dados'  # Nome da aba/planilha

# Escopos necessários
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Autenticação
def get_google_sheet():
    # Obtém as credenciais da variável de ambiente
    creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    if not creds_json:
        raise ValueError("Variável de ambiente GOOGLE_CREDENTIALS_JSON não encontrada")
    
    # Converte a string JSON para um dicionário
    creds_dict = json.loads(creds_json)
    
    creds = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    return sheet

@app.route('/api/enviar_dados', methods=['POST'])
def receber_dados():
    try:
        # Recebe os dados do formulário
        data = request.get_json()
        
        # Validação básica dos dados
        required_fields = ['nome', 'sobrenome', 'email', 'telefone', 'mercado_apostas', 'trabalha_trafego']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'status': 'error', 'message': f'Campo {field} é obrigatório'}), 400
        
        # Prepara os dados para a planilha
        row_data = [
            data.get('nome', ''),
            data.get('sobrenome', ''),
            data.get('cpf', ''),
            data.get('email', ''),
            data.get('data_nascimento', ''),
            data.get('telefone', ''),
            data.get('mercado_apostas', ''),
            data.get('redes_sociais', ''),
            data.get('trabalha_trafego', ''),
            data.get('tipo_trafego', ''),
            data.get('porque_upbet', ''),
            data.get('considera', ''),
            # Adiciona timestamp automático
            gspread.utils.datetime_to_isoformat(gspread.utils.now())
        ]
        
        # Acessa a planilha e adiciona os dados
        sheet = get_google_sheet()
        sheet.append_row(row_data)
        
        return jsonify({
            'status': 'success',
            'message': 'Dados salvos na planilha com sucesso!'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao processar os dados: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)