import os
import json
from google.oauth2 import service_account
import gspread

def handler(request):
    if request.method != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({'status': 'error', 'message': 'Método não permitido'})
        }

    try:
        data = request.json
        required_fields = ['nome', 'sobrenome', 'email', 'telefone', 'mercado_apostas', 'trabalha_trafego']
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'status': 'error', 'message': f'Campo {field} é obrigatório'})
                }

        creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        creds_dict = json.loads(creds_json)
        creds = service_account.Credentials.from_service_account_info(
            creds_dict, scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
        )
        sheet_id = os.getenv('SHEET_ID')
        sheet_name = 'Dados'
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id).worksheet(sheet_name)

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
            # timestamp
            __import__('datetime').datetime.utcnow().isoformat()
        ]
        sheet.append_row(row_data)

        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'success', 'message': 'Dados salvos na planilha com sucesso!'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'status': 'error', 'message': f'Erro ao processar os dados: {str(e)}'})
        }
