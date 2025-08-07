from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

from flask import Flask, jsonify, request, make_response, render_template, session, send_file
# from flask_restful import Resource, Api
from Services.UserServices.UserServices import UserServices
from Services.FormServices.FormServices import FormServices
from Services.QuacServices.QuacServices import QuacServices
from Services.HistoriqueServices.HistoriquesServices import HistoriquesServices
from Databases.env import Connector
from flask_mysqldb import MySQL
from Helper.Helper import Helpers
import traceback
import os
from Services.TranslationServices.TranslationServices import Transcription
from flask_cors import CORS


from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from datetime import datetime, timedelta


app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CORS(app) 

app.config['SECRET_KEY'] = '9d40bf12b5704f7099227fafc117283f'
app.config['UPLOADED_AUDIO_DEST'] = 'public/audio'
connexion = Connector('localhost', 'root', '', 'voice', app).ConnexionDatabase()
jwt = JWTManager(app)
MAX_DURATION_SECONDS = 10 * 60  # 10 minutes in seconds
# Import model
model_directory = "Model/anglais/"
processor_anglais = Wav2Vec2Processor.from_pretrained(model_directory)
model_anglais = Wav2Vec2ForCTC.from_pretrained(model_directory)

model_fr = "Model/français/"
processor_français = Wav2Vec2Processor.from_pretrained(model_fr)
model_français = Wav2Vec2ForCTC.from_pretrained(model_fr)

@app.route('/api/createUser', methods=['POST'])
def createUser():  
    try:
        
        form = [
            ("nom", str, True), ("prenom", str, True), ("email", str, True), ("password", str, True), 
            ("profile_path", str, False)
               ]
        requestForm = FormServices(form)
        req = request.get_json()
        
        verification = requestForm.VerifiedForm(req)
        if verification == True :
            print("mide")
            verificationPassword = requestForm.VerificationPassword(
                req.get("password"), 
                req.get("password_confirmation")
            )
            objet = UserServices(connexion)
            if verificationPassword == True and objet.MailExiste(req.get("email")) == True:    
                user = objet.InsertUser(req)
                return jsonify(message=f"Utilisateur {user} est inséré avec succès"), 200
            elif verificationPassword != True:
                resultat = verificationPassword
                return jsonify(message=resultat), 400
            else:
                resultat = objet.MailExiste(req.get("email"))
                return jsonify(message=resultat), 400
           
        return jsonify(message=verification), 400
    except Exception as e:
        traceback.print_exc()
        return "Bad Request: Invalid Key in Form Data", 400

@app.route('/api/authentification', methods=['POST'])
def Authentification() :
    req = request.get_json()
    form = [("email", str, True), ("password", str, True)]
    requestForm = FormServices(form)
    verification = requestForm.VerifiedForm(req)
    
    if verification == True :
        userS = UserServices(connexion)
        existe = userS.UserExiste(req.get("email"))
        if existe["email"] == [] or existe["email"] == None :
            return jsonify(message="Email introuvable"), 401
        
        reponse = userS.PasswordMitovy(req.get("password"), existe["password"][0], existe["key_pass"][0], existe["iv"][0])
        print(reponse)
        if reponse :
            session["online"] = True
            token = create_access_token(identity=existe, expires_delta=timedelta(seconds=90000))
            # token = jwt.encode({
            #     "user": existe, 
            #     "expiration": str(datetime.utcnow() + timedelta(seconds=3600))
                
            # }, app.config['SECRET_KEY']
            #                 )
            return jsonify({'user': existe , 'token' : token}),200
        else :
            return jsonify({'erreurs' : "mot de passe invalide"}), 400
            
    else :
        return jsonify({'erreur': "Utilisateur inconnu veuillez se reconnecter"}),400


@app.route("/api/importationFichier/<string:langue>", methods=["POST"])
@jwt_required()
def protected(langue):
    current_user = get_jwt_identity()
    
    if 'fichier' not in request.files:
        return jsonify({'message': 'Aucun fichier audio trouvé'}), 400

    fichier_audio = request.files['fichier']

    if fichier_audio.filename == '':
        return jsonify({'message': 'Nom de fichier vide'}), 400
    
    help = Helpers()
    ALLOWED_EXTENSIONS = {'mp3', 'wav', 'mp4'}
    if not help.allowed_file(fichier_audio.filename, ALLOWED_EXTENSIONS):
        return jsonify({'message': 'Type de fichier non autorisé'}), 400

    fichier_audio.save("public/fosika/" + fichier_audio.filename)
    inpt = "public/fosika/" + fichier_audio.filename
    out = "public/audio/" + fichier_audio.filename
    help.convert_mp3_to_wav(input_file=inpt, output_file=out, file_name=fichier_audio.filename)
    # Conversion 16000HZ
    otp = fichier_audio.filename.rsplit('.', 2)[0].lower()

    ou_file = f"{otp}.wav"
    help.ConversionHz("public/audio/" + ou_file, ou_file)
    
    
    # audio_duration = help.Get_audio_duration("public/audio/" + fichier_audio.filename)
    
    # if audio_duration > MAX_DURATION_SECONDS : 
    #     os.remove("public/audio/" + fichier_audio.filename)
    #     return jsonify({
    #         "message" : "Taille de l'audio plus de 10 minutes"
    #     }),400
    try:  
        if langue == "en" :
            prediction = help.TranscriptionTexte(
                "public/audio/" + ou_file, 
                processor_anglais, model_anglais
                )
            
            transcription = Transcription(connexion)
            data = {
                "id_user": current_user["id"][0],
                "parole_path": "public/audio/" + ou_file,
                "langue": 2,
                "prediction": prediction
            }
            trans = transcription.InsertTranscription(data)
            return jsonify({
                "trans": trans,
                'prediction': prediction,
                'audio' : "public/audio/" + ou_file
                }), 200   
        if langue == "fr" : 
            prediction = help.TranscriptionTexte(
                "public/audio/" + ou_file, 
                processor_français, model_français
                )
            
            transcription = Transcription(connexion)
            data = {
                "id_user": current_user["id"][0],
                "parole_path": "public/audio/" + ou_file,
                "langue": 1,
                "prediction": prediction
            }
            trans = transcription.InsertTranscription(data)
            return jsonify({
                "trans": trans,
                'prediction': prediction,
                'audio' : "public/audio/" + ou_file
                }), 200
    except Exception as e:
        app.logger.error(f"Erreur lors de l'ouverture du fichier : {str(e)}")
        return jsonify({'message': 'Erreur lors de l\'ouverture du fichier'}), 500

    return jsonify({"message": f"Hello, {current_user}! Cette route est protégée."}), 200
    

@app.route("/api/Historique/", methods=["GET"])
@jwt_required()
def Historique():
    user = get_jwt_identity()
    transcription = Transcription(connexion)
    condition = f"id_user = {user['id'][0]}"
    
    result = transcription.findAll([condition])
    return jsonify({"message" : result}),200


@app.route("/api/addFavori/<int:id_transcription>", methods=["PUT"])
@jwt_required()
def AddFavori(id_transcription) : 
    user = get_jwt_identity()
    transcription = Transcription(connexion)
    resp = transcription.IdTranslationExiste(id_transcription, user["id"][0])
    if resp == None or resp == ""  : 
        return jsonify({"message" : "Id introuvable"}), 401
    status = transcription.GetStatus(code="FAV")
    if resp[0]["favori"] == None or resp[0]["favori"] == "" : 
        modifier = transcription.ChangementStatus(id_transcription=id_transcription, valeur = status[0]["id"])
        return jsonify({"message": modifier}),200
    if resp[0]["favori"] != None or resp[0]["favori"] != "" :
        modifier = transcription.ChangementStatus(id_transcription=id_transcription, valeur = None)
        return jsonify({"message": modifier}),200

@app.route("/api/listeFavori", methods=["GET"])
@jwt_required()
def HistoriqueFavori():
    user = get_jwt_identity()
    transcription = Transcription(connexion)
    condition = f"favori = 3"
    condition2 = f"id_user = {user['id'][0]}"
     
    result = transcription.findAll([condition, condition2])
    return jsonify({"message" : result}),200


@app.route("/api/modifier/<int:id_transcription>", methods=["PUT"])
@jwt_required()
def ModifierTranscription(id_transcription):
    user = get_jwt_identity()
    
    form = [
                ("valeur", str, True)
           ]
    requestForm = FormServices(form)
    req = request.get_json()
        
    verification = requestForm.VerifiedForm(req)
    if verification == True :
        transcription = Transcription(connexion)
        condition = f"id = {id_transcription}"
        condition2 = f"id_user = {user['id'][0]}"
        
        result = transcription.findAll([condition, condition2])
        if result:
            valeur = req.get('valeur')
            update = transcription.UpdateTranslation(valeur, id_transcription)
            
    return jsonify({"message" : update}),200

@app.route('/upload/<string:langue>', methods=['POST'])
@jwt_required()
def upload_audio(langue):
    try:
        current_user = get_jwt_identity()
        uploaded_file = request.files['audio']
        if uploaded_file.filename != '':
            uploaded_file.save("public/fosika/" + uploaded_file.filename)
            inpt = "public/fosika/" + uploaded_file.filename
            out = "public/audio/" + uploaded_file.filename
            help = Helpers()
            help.convert_mp3_to_wav(input_file=inpt, output_file=out, file_name=uploaded_file.filename)
            # Conversion 16000HZ
            otp = uploaded_file.filename.rsplit('.', 2)[0].lower()

            ou_file = f"{otp}.wav"
            help.ConversionHz("public/audio/" + ou_file, ou_file)
            
            try:  
                if langue == "en" :
                    prediction = help.TranscriptionTexte(
                        "public/audio/" + ou_file, 
                        processor_anglais, model_anglais
                        )
                    
                    transcription = Transcription(connexion)
                    data = {
                        "id_user": current_user["id"][0],
                        "parole_path": "public/audio/" + ou_file,
                        "langue": 2,
                        "prediction": prediction
                    }
                    trans = transcription.InsertTranscription(data)
                    return jsonify({
                        "trans": trans,
                        'prediction': prediction,
                        'audio' : "public/audio/" + ou_file
                        }), 200   
                if langue == "fr" : 
                    prediction = help.TranscriptionTexte(
                        "public/audio/" + ou_file, 
                        processor_français, model_français
                        )
                    
                    transcription = Transcription(connexion)
                    data = {
                        "id_user": current_user["id"][0],
                        "parole_path": "public/audio/" + ou_file,
                        "langue": 1,
                        "prediction": prediction
                    }
                    trans = transcription.InsertTranscription(data)
                    return jsonify({
                        "trans": trans,
                        'prediction': prediction,
                        'audio' : "public/audio/" + ou_file
                        }), 200
            except Exception as e:
                app.logger.error(f"Erreur lors de l'ouverture du fichier : {str(e)}")
                return jsonify({'message': 'Erreur lors de l\'ouverture du fichier'}), 500

    except Exception as e:
        return 'Une erreur est survenue lors de la sauvegarde de l\'enregistrement audio.', 500




# BRYAN
@app.route("/api/generateQuestion", methods=["POST"])
@jwt_required()
def GenerateQuestion():
    form = [
            ("nombre_question", int, True), ("type_questions", int, True) ,("contexte", str, True)
           ]
    
    requestForm = FormServices(form)
    req = request.get_json()
        
    verification = requestForm.VerifiedForm(req)
    if verification == True :
        current_user = get_jwt_identity()
        model_path = "Model/distilbertasa-cutsomes/"
        quacServices = QuacServices(model_path)
        
        context = ""f"{req.get('contexte')}"""
        
        titles, content = quacServices.separate_titles_and_content(context)
        entities = quacServices.extract_entities_using_distilbert(" ".join(content))

        questions = []
        if entities:
            num_questions_to_generate = req.get('nombre_question')
            generated_questions = quacServices.generate_questions(" ".join(content), num_questions_to_generate)

            for i, question in enumerate(generated_questions, start=1):
                historique = HistoriquesServices(connexion)
                
                data = {
                    "id_user": current_user["id"][0],
                    "questions_genere": question,
                    "type_questions": req.get('type_questions'),
                    
                }
                trans = historique.InsertHistorique(data)
                print(trans)
                questions.append(question)
            # else:
            #     return jsonify({"message" : "Aucune entité pertinente trouvée dans le contenu."}),400
        
        return jsonify({"message" : questions}),200        
    return jsonify({"message" : verification}),200


@app.route("/api/importFichierPdf", methods=["POST"])
@jwt_required()
def ImportFichierPdf():
    current_user = get_jwt_identity()
    
    if 'fichier' not in request.files:
        return jsonify({'message': 'Aucun fichier trouvé'}), 400

    fichier = request.files['fichier']

    if fichier.filename == '':
        return jsonify({'message': 'Nom de fichier vide'}), 400
    
    help = Helpers()
    ALLOWED_EXTENSIONS = {'pdf'}
    if not help.allowed_file(fichier.filename, ALLOWED_EXTENSIONS):
        return jsonify({'message': 'Type de fichier non autorisé'}), 400
    
    fichier.save("public/pdf/" + fichier.filename)
    help = Helpers()
    
    getText = help.Get_text_pdf("public/pdf/" + fichier.filename)
    
    model_path = "Model/distilbertasa-cutsomes/"
    quacServices = QuacServices(model_path)
        
    context = ""f"{getText}"""
    # return jsonify({"context" : context})
    titles, content = quacServices.separate_titles_and_content(context)
    entities = quacServices.extract_entities_using_distilbert(" ".join(content))
 
    questions = []
    if entities:
        # req.get('nombre_question')
        num_questions_to_generate = 20
        generated_questions = quacServices.generate_questions(" ".join(content), num_questions_to_generate)

        for i, question in enumerate(generated_questions, start=1):
            historique = HistoriquesServices(connexion)
                
            data = {
                    "id_user": current_user["id"][0],
                    "questions_genere": question,
                    "type_questions": 5,
                    # req.get('type_questions')
                    
            }
            trans = historique.InsertHistorique(data)
            print(trans)
            questions.append(question)
 
        return jsonify({"question" : questions}),200
    return jsonify({"response" : {"text" : getText} })
    
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")