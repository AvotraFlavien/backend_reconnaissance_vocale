from Services.RequetServices import RequetesServices
from Helper.Helper import Helpers
from Services.RequetServices import RequetesServices


class HistoriquesServices :
    table = "historique"
    def __init__(self, mysql) -> None:
        self.request = RequetesServices.RequetesServices(mysql)
    
    def InsertHistorique(self, data) : 
        return self.request.inserer_donnees(self.table, data)