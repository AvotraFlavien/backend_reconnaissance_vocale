from Services.RequetServices import RequetesServices
from Helper.Helper import Helpers
from Services.RequetServices import RequetesServices

class Transcription :
    table = "translation"
    def __init__(self, mysql) -> None:
        self.request = RequetesServices.RequetesServices(mysql)
    
    def InsertTranscription(self, data) : 
        return self.request.inserer_donnees(self.table, data)
    
    def findAll(self, conditions = []):
        # colonnes_a_selectionner = ["*"]
        # conditions_de_filtrage = {}
        # result = self.request.Select_from_table2(self.table, colonnes_a_selectionner, conditions_de_filtrage)
        # result = self.request.SelectAll(self.table)
        # return result
    
        order_by = ["id DESC"] 
        table_name = "translation"
        selected_columns = ["id_user", "parole_path", "id", "prediction", "langue"]
        columns_mapping = {"id_user": "id_user", "parole_path": "parole_path", "id": "id", "prediction": "prediction", "langue": "langue"}
        # conditions = ["id_user = 1", "parole_path LIKE 'public%'"]   
        
        result = self.request.execute_query_and_return_json(table_name, selected_columns, columns_mapping, conditions, order_by)
        return result
    
    
    def UpdateTranslation(self, valeur, id_transcription):
        result = self.request.update_column_value("translation", "prediction", valeur, [f"id = {id_transcription}"])
        return result
    
    def IdTranslationExiste(self, id, id_user) : 
        table_name = "translation"
        selected_columns = ["id", "id_user", "parole_path", "prediction", "favori"]
        conditions = [f"id = {id}" ,f"id_user = {id_user}"]   
        # , "id_user": id_user
        columns_mapping = {"id": "id", "id_user": "id_user", "parole_path": "parole_path", "prediction": "prediction", "favori": "favori"}
        result = self.request.execute_query_and_return_json(table_name, selected_columns, columns_mapping, conditions)
        if result == None or result == [] or result == "" or result == ():
            return None
        return result
    
    def GetStatus(self, code) : 
        table_name = "statut"
        selected_columns = ["id", "name", "code"]
        condition = [f"code = '{code}'"]
        columns_mapping = {"id": "id", "name": "name", "code": "code"}
        result = self.request.execute_query_and_return_json(table_name, selected_columns, columns_mapping, condition)
        if result == None or result == [] or result == "" or result == ():
            return None
        return result
    
    def ChangementStatus(self, id_transcription, valeur):
        # status = self.GetStatus(code)
        # if status == None or status == "":
        #     return None
        table_name = "translation"
        colonne = 'favori'
        
         
        conditions=[f'id = {id_transcription}']
        result = self.request.update_column_value(table_name, colonne, valeur, conditions)
        return result