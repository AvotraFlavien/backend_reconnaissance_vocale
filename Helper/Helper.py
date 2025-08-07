import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import base64
from moviepy.editor import AudioFileClip
import soundfile as sf
import torch
from scipy import signal
import PyPDF2
import re
import unidecode
from scipy import signal
from moviepy.editor import *
import subprocess

class Helpers : 
        def __init__(self) -> None:
                pass
            
            
        def TranscriptionTexte(self, audio_file_path, processor, model) : 
            # Chargez le fichier audio
            audio_input, _ = sf.read(audio_file_path)

            # Effectuez une transcription
            inputs = processor(audio_input, return_tensors="pt")
            with torch.no_grad():
                logits = model(**inputs).logits

            # Obtenez la transcription
            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = processor.batch_decode(predicted_ids)
            print(transcription)
            
            return transcription
        
        # def ConversionHz(self, path_file):            
        #     input_file = path_file

        #     # Chemin du fichier de sortie
        #     output_file = path_file
            
        #     # Charger le fichier WAV d'origine
        #     data, samplerate = sf.read(input_file)

        #     # Si le fichier WAV d'origine est stéréo, convertir en mono en moyennant les canaux
        #     if data.ndim == 2:
        #         data = (data[:, 0] + data[:, 1]) / 2.0

        #     # Ré-échantillonner à une fréquence d'échantillonnage de 22 050 Hz
        #     target_sample_rate = 16000
        #     resampled_data = signal.resample(data, int(len(data) * target_sample_rate / samplerate))

        #     # Convertir en PCM 16 bits
        #     pcm_data = (resampled_data * 32767).astype('int16')

        #     # Écrire le fichier WAV de sortie en utilisant les paramètres souhaités
        #     sf.write(output_file, pcm_data, target_sample_rate, 'PCM_16')

        #     return True
        
        

        def convert_mp3_to_wav(self,input_file, output_file, file_name):
            # Charger le fichier MP3 en utilisant MoviePy
            audio = AudioFileClip(input_file)
            
            # Convertir le fichier audio en WAV
            output = file_name.rsplit('.', 2)[0].lower()
            # output_file = output+".wav"
            output_file = f"public/audio/{output}.wav"
            return audio.write_audiofile(output_file, codec='pcm_s16le', ffmpeg_params=["-ac", "1"])
 
        
        def conv(self, input_file, output_file):
            # Utiliser FFmpeg pour convertir le fichier MP3 en WAV avec les spécifications requises
            ffmpeg_cmd = [
                'ffmpeg',  # Chemin vers l'exécutable FFmpeg
                '-i', input_file,  # Fichier d'entrée MP3
                '-ar', '1600',  # Fréquence d'échantillonnage de 1600 Hz
                '-ac', '1',  # Mono (1 canal audio)
                '-acodec', 'pcm_s16le',  # Format PCM
                output_file  # Fichier de sortie WAV
            ]

            try:
                # Exécuter la commande FFmpeg
                subprocess.run(ffmpeg_cmd, check=True)
                return True  # La conversion s'est terminée avec succès
            except subprocess.CalledProcessError as e:
                print("Erreur lors de la conversion : ", e)
                return False  # Erreur lors de la conversion

        
        
        def ConversionHz(self, path_file, filename):
            input_file = path_file

            # Charger le fichier audio d'origine (peut être mp3, wav, etc.)
            data, samplerate = sf.read(input_file)

            # Si le fichier audio d'origine est stéréo, convertir en mono en moyennant les canaux
            if data.ndim == 2:
                data = (data[:, 0] + data[:, 1]) / 2.0

            # Ré-échantillonner à une fréquence d'échantillonnage de 16 000 Hz
            target_sample_rate = 16000
            resampled_data = signal.resample(data, int(len(data) * target_sample_rate / samplerate))

            # Convertir en PCM 16 bits
            pcm_data = (resampled_data * 32767).astype('int16')

            # Créer un fichier WAV en utilisant le format PCM 16 bits
            file = filename.rsplit('.', 2)[0].lower()
            output_file = "public/audio/"+file+".wav"  # Spécifiez le chemin de sortie correct

            # Écrire le fichier WAV de sortie en utilisant les paramètres souhaités
            sf.write(output_file, pcm_data, target_sample_rate, format='WAV', subtype='PCM_16')

            return True
        
        def GenerationKeyIv(self) : 
            key = secrets.token_bytes(16)  # Génère 16 octets aléatoires (128 bits)
            iv = secrets.token_bytes(16)  # Génère 16 octets aléatoires (128 bits)
            return (key, iv)
        
        def decrypt(self, ciphertext, key, iv):
            backend = default_backend()
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
            decryptor = cipher.decryptor()
            unpadder = padding.PKCS7(128).unpadder()
            decrypted_padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            plaintext = unpadder.update(decrypted_padded_plaintext) + unpadder.finalize()
            return plaintext

        def encrypt(self, plaintext, key, iv):
            backend = default_backend()
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
            encryptor = cipher.encryptor()
            padder = padding.PKCS7(128).padder()
            padded_plaintext = padder.update(plaintext.encode('utf-8')) + padder.finalize()
            ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
            return ciphertext
            
        def EncodePassword(self, password) : 
            keyIv = self.GenerationKeyIv()
            passEnc = self.encrypt(password, keyIv[0], keyIv[1])
             
            return [
                    {
                        "key_pass": base64.b64encode(keyIv[0]), "iv": base64.b64encode(keyIv[1]),
                        "password": base64.b64encode(passEnc)
                    }
                   ] 
        
        def DecodePasswordVerification(self, password, key, iv):
            passEnc = self.encrypt(password, base64.b64decode(key.encode()), base64.b64decode(iv.encode()))
            return base64.b64encode(passEnc)
            
        
        def allowed_file(self, filename, ALLOWED_EXTENSIONS):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


        def Get_audio_duration(self, filepath):
            try:
                audio = AudioFileClip(filepath)
                return audio.duration
            except Exception as e:
                return None
            
    
        def Get_text_pdf(self, pdf_path):
            text = ""
            with open(pdf_path, "rb") as pdf_file:
                pdf = PyPDF2.PdfReader(pdf_path)
            for page in pdf.pages:
                text += page.extract_text()
            print(text)
            return text
        
        # def Get_text_pdf(self, files):
        #     with open(files, 'rb') as file:
        #         reader = PyPDF2.PdfReader(file)

        #         # Extraction du texte
        #         text = ""
        #         for page_number in range(len(reader.pages)):
        #             page = reader.pages[page_number]
        #             text += page.extract_text()

        #         # Convertir le texte en minuscules
        #         texte = text.lower()

        #         # Remplacer les caractères non alphabétiques par des espaces
        #         texte_propre = re.sub(r'[^a-zàâäéèêëîïôöùûüç"?!]+', ' ', texte)
        #     return texte_propre


