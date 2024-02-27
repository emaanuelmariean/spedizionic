from flask import Flask, render_template, request, redirect, url_for, send_file, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spedizioni.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Spedizione(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destinatario = db.Column(db.String(150), nullable=False)
    descrizione = db.Column(db.String(300), nullable=False)
    data = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    nome_utente = db.Column(db.String(100), nullable=False)
    seriale_pc = db.Column(db.String(100), nullable=False)
    modello_pc = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    consegnato = db.Column(db.Boolean, default=False)

def create_database():
    with app.app_context():
        db.create_all()

@app.route('/')
def index():
    spedizioni = Spedizione.query.order_by(Spedizione.data.desc()).all()
    # Conta le spedizioni per categoria
    spedizioni_generali = Spedizione.query.filter_by(categoria="Generale").count()
    spedizioni_smartpaper = Spedizione.query.filter_by(categoria="Smartpaper").count()

    return render_template('index.html', spedizioni=spedizioni, spedizioni_generali=spedizioni_generali, spedizioni_smartpaper=spedizioni_smartpaper)



@app.route('/esporta_excel')
def esporta_excel():
    categoria_selezionata = request.args.get('categoria', 'Tutte')
    # Logica per selezionare le spedizioni
    if categoria_selezionata == 'Tutte':
        spedizioni = Spedizione.query.all()
    else:
        spedizioni = Spedizione.query.filter_by(categoria=categoria_selezionata).all()
    
    # Prepara i dati per l'export
    spedizioni_lista = [{
        'Destinatario': spedizione.destinatario,
        'Descrizione': spedizione.descrizione,
        'Data': spedizione.data.strftime('%Y-%m-%d'),
        'Nome Utente': spedizione.nome_utente,
        'Seriale PC': spedizione.seriale_pc,
        'Modello PC': spedizione.modello_pc,
        'Categoria': spedizione.categoria,
        'Consegnato': 'Sì' if spedizione.consegnato else 'No'
    } for spedizione in spedizioni]
    
    df = pd.DataFrame(spedizioni_lista)
    
    # Crea la directory se non esiste
    directory = 'exported_files'
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    filename = f'spedizioni_{categoria_selezionata}.xlsx'
    filepath = os.path.join(directory, filename)
    df.to_excel(filepath, index=False)
    
    return send_file(filepath, as_attachment=True)





@app.route('/calendario')
def calendario():
    spedizioni = Spedizione.query.all()
    spedizioni_data = [
        {
            'title': spedizione.descrizione,
            'start': spedizione.data.strftime('%Y-%m-%d'),
            'destinatario': spedizione.destinatario,
            'consegnato': spedizione.consegnato,
            'nome_utente': spedizione.nome_utente,
            'seriale_pc': spedizione.seriale_pc,
            'modello_pc': spedizione.modello_pc,
            'categoria': spedizione.categoria,
            'color': '#28a745' if spedizione.consegnato else '#dc3545'  # Verde se consegnato, altrimenti rosso
        } for spedizione in spedizioni
    ]
    return render_template('calendario.html', spedizioni_data=spedizioni_data)


@app.route('/modifica_spedizione', methods=['POST'])
def modifica_spedizione():
    id_spedizione = request.form.get('id_spedizione')
    destinatario = request.form.get('destinatario')
    descrizione = request.form.get('descrizione')
    categoria = request.form.get('categoria')
    serialePc = request.form.get('seriale')
    modelloPc = request.form.get('modello')
    nomeUtente = request.form.get('nome_utente')
    data = request.form.get('data')

    # Cerca la spedizione esistente nel database
    spedizione = Spedizione.query.get_or_404(id_spedizione)

    # Aggiorna i campi della spedizione
    spedizione.destinatario = destinatario
    spedizione.descrizione = descrizione
    spedizione.categoria = categoria
    spedizione.seriale_pc = serialePc
    spedizione.modello_pc = modelloPc
    spedizione.nome_utente = nomeUtente
    spedizione.data = datetime.strptime(data, '%Y-%m-%d')

    # Salva le modifiche nel database
    db.session.commit()

    return redirect(url_for('index'))




@app.route('/aggiungi', methods=['POST'])
def aggiungi_spedizione():
    if request.method == 'POST':
        spedizione_data = request.form
        nuova_spedizione = Spedizione(
            destinatario=spedizione_data['destinatario'],
            descrizione=spedizione_data['descrizione'],
            data=datetime.strptime(spedizione_data['data'], '%Y-%m-%d'),
            nome_utente=spedizione_data['nome_utente'],
            seriale_pc=spedizione_data['seriale'],
            modello_pc=spedizione_data['modello'],
            categoria=spedizione_data['categoria']
        )
        db.session.add(nuova_spedizione)
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/consegna/<int:id>')
def consegna_spedizione(id):
    spedizione = Spedizione.query.get_or_404(id)
    spedizione.consegnato = True
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/cancella/<int:id>')
def cancella_spedizione(id):
    spedizione_da_cancellare = Spedizione.query.get_or_404(id)
    db.session.delete(spedizione_da_cancellare)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/ricerca', methods=['GET'])
def ricerca_spedizioni():
    data_inizio = request.args.get('data_inizio')
    data_fine = request.args.get('data_fine')
    if data_inizio and data_fine:
        spedizioni = Spedizione.query.filter(
            Spedizione.data >= datetime.strptime(data_inizio, '%Y-%m-%d'),
            Spedizione.data <= datetime.strptime(data_fine, '%Y-%m-%d')
        ).order_by(Spedizione.data.desc()).all()
        return render_template('index.html', spedizioni=spedizioni)
    else:
        # Se non sono specificate le date, potresti voler reindirizzare l'utente o mostrare un messaggio
        return render_template('index.html', spedizioni=[], no_data=True)

@app.route('/toggle_consegna/<int:id>')
def toggle_consegna(id):
    spedizione = Spedizione.query.get_or_404(id)
    spedizione.consegnato = not spedizione.consegnato # Inverte lo stato di consegna
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/categoria/<nome_categoria>')
def mostra_categoria(nome_categoria):
    spedizioni = Spedizione.query.filter_by(categoria=nome_categoria).order_by(Spedizione.data.desc()).all()
    # Puoi passare anche i conteggi delle categorie se vuoi mantenerli aggiornati nella sidebar
    spedizioni_generali = Spedizione.query.filter_by(categoria="Generale").count()
    spedizioni_smartpaper = Spedizione.query.filter_by(categoria="Smartpaper").count()
    return render_template('index.html', spedizioni=spedizioni, spedizioni_generali=spedizioni_generali, spedizioni_smartpaper=spedizioni_smartpaper)



if __name__ == '__main__':
    app.run(debug=True)