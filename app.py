from flask import Flask, render_template, request, redirect, url_for, flash
from db import execute_query, execute_one

app = Flask(__name__)
app.secret_key = 'imc_secret_key_2026'


def calcular_imc(peso, altura):
    return round(peso / (altura ** 2), 2)

def classificacao(imc):
    if imc < 18.5: 
        classificacao = 'Abaixo do peso'
    elif imc < 25:
        classificacao = 'Peso normal'
        
    ##Adicionar as demais classificações
    else:
        classificacao = 'Erro calculo IMC'

    return classificacao

@app.route('/')
def index():
    sql = '''
CREATE TABLE IF NOT EXISTS calculos (
    id_calculos BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    peso DECIMAL(6,2) NOT NULL,
    altura DECIMAL(5,2) NOT NULL,

    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deletado_em DATETIME NOT NULL
);
'''
    resultado = execute_query(sql, fetch=True)
    print(resultado)
    
    return render_template('index.html')


@app.route('/resultados')
def resultados():
    
    try: 

        sql = "SELECT * FROM calculos WHERE deletado_em IS NULL;"

        calculos = execute_query(sql, fetch=True)

        if calculos is None:
            calculos = []

    except Exception as e:
        flash(f'Erro ao buscar','danger')
        app.logger.error(f'Erro no ISELECT: {e}')
        return redirect(url_for('resultados'))
        

    return render_template('resultados.html', calculos=calculos, total=len(calculos), calcular = calcular_imc, classificacao = classificacao)


@app.route('/calcular', methods=['GET', 'POST'])
def calcular():
##.strip() apaga os espaços 
    if request.method == 'POST':
        nome = request.form.get('nome','Não foi enviado um nome!').strip()
        peso = request.form.get('peso').strip()
        altura = request.form.get('altura').strip()

        peso = float(peso)
        altura = float(altura)

        try:
            ##Cria o script SQL para ser enviado, %s é cada valor
            sql = 'INSERT INTO calculos(nome, peso, altura) VALUES (%s, %s, %s);'
            
            ##Passa o SQL + os parametros que aqui são os dados em uma lista 
            execute_query(sql, (nome, peso, altura))
            
            ##Gera a notificação de sucesso
            flash(f'Produto[{nome}]cadastrado com sucesso','success')

            ##Leva a tela de resultados
            return redirect(url_for('resultados'))
        
        except Exception as e:
            flash(f'Erro ao salvar!','danger')
            app.logger.error(f'Erro no INSERT: {e}')
            return redirect(url_for('calcular'))
        
        
       
      # flash(f'Olá {nome}, seu IMC é: {imc} - Classificação: {classificacao}', 'success') 
  
    return render_template('formulario.html')


@app.route('/calcular/editar/<int:id>', methods=['GET', 'POST'])
def editar_imc(id):

    dados = execute_one('SELECT * FROM calculos WHERE id_calculos = %s', (id,))
    # print(dados)

    if request.method == 'POST':
        try:
            nome = request.form.get('nome','Não foi enviado um nome!').strip()
            peso = request.form.get('peso').strip()
            altura = request.form.get('altura').strip()

            peso = float(peso)
            altura = float(altura)

            valores = (nome, peso, altura, id)

            sql = '''
                UPDATE calculos set
                nome = %s, 
                peso = %s,
                altura = %s
                WHERE id_calculos = %s;
            '''

            execute_query(sql, valores)

            flash(f'IMC Atualizado com sucesso!', 'Warning')
            return redirect(url_for('resultados'))
        
        except Exception as e:
            flash(f'Erro ao atualizar: {e}', 'danger')
            return render_template('formulario.html', dados=dados)

    return render_template('formulario.html', dados=dados)


if __name__ == '__main__':
    app.run(debug=True)
