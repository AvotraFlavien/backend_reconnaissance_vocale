import torch
from transformers import DistilBertTokenizer, DistilBertForQuestionAnswering
import spacy
import re

class QuacServices :
    
    def __init__(self, model_path) :
        self.model_path = model_path
        self.tokenizer = DistilBertTokenizer.from_pretrained(model_path)
        self.model = DistilBertForQuestionAnswering.from_pretrained(model_path)
        self.nlp = spacy.load("en_core_web_sm")
    
    def extract_entities_using_distilbert(self, context):
        # Tokeniser le texte en utilisant le tokenizer DistilBERT
        tokens = self.tokenizer(context, return_tensors="pt", padding=True, truncation=True)

        # Faire la prédiction d'entités nommées avec le modèle DistilBERT
        with torch.no_grad():
            output = self.model(**tokens)

        # Obtenir les prédictions de l'entité "start" et "end"
        start_logits, end_logits = output.start_logits, output.end_logits

        # Trouver les entités avec les scores maximaux
        start_idx = start_logits.argmax()
        end_idx = end_logits.argmax()

        # Extraire l'entité à partir des indices
        entity = self.tokenizer.convert_tokens_to_string(self.tokenizer.convert_ids_to_tokens(tokens.input_ids[0][start_idx:end_idx+1]))
        print(entity)
        return entity
    
    def separate_titles_and_content(self, text):
        lines = text.split("\n")
        titles = []
        content = []

        for line in lines:
            # Utilisez une expression régulière pour identifier les titres (par exemple, lignes en majuscules ou en gras)
            if re.match(r'^\*\*.*\*\*$', line.strip()) or re.match(r'^[A-Z\s]+$', line.strip()):
                titles.append(line)
            else:
                content.append(line)

        return titles, content
    
    
    def generate_questions(self, context, num_questions=3):
        questions = []

        # Extraction des entités nommées à l'aide de spaCy
        doc = self.nlp(context)
        entities = [(ent.text, ent.label_) for ent in doc.ents]

        # Mapping de mots interrogatifs aux types d'entités
        wh_words_mapping = {
            "Who": ["PERSON"],
            "When": ["DATE", "TIME"],
            "Where": ["LOC", "GPE", "NORP"],
            "Why": [],
            "How": [],
            "What": []
        }

        # Générer des questions basées sur chaque entité avec un type correspondant
        for entity, entity_type in entities:
            # Vérifier si l'entité est une date ou un nombre
            if entity_type in ["DATE", "TIME", "CARDINAL"]:
                continue  # Ignorer cette entité

            # Trouver le mot interrogatif approprié pour le type d'entité
            wh_word = None
            for wh, entity_types in wh_words_mapping.items():
                if entity_type in entity_types:
                    wh_word = wh
                    break

            # Si aucun mot interrogatif approprié n'est trouvé, utilisez "What"
            if wh_word is None:
                wh_word = "What"

            # Utiliser "is" ou "are" dans la question en fonction du mot interrogatif
            verb = "is" if wh_word == "Who" else "are"

            question = f"{wh_word} {verb} '{entity}' ?"
            questions.append(question)

            # Si vous avez atteint le nombre souhaité de questions, sortez de la boucle
            if len(questions) == num_questions:
                break

        return questions
    
     
    
    
