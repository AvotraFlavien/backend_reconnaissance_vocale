from Services.RequetServices import RequetesServices
from Helper.Helper import Helpers
import random

class UserServices:
    table = "user"
    helper = Helpers()
    def __init__(self, mysql):
        self.request = RequetesServices.RequetesServices(mysql)
    
    def InsertUser(self, data):
        profile = [
            "/Public/profile/profile1.jpg", 
            "/Public/profile/profile2.jpg",
            "/Public/profile/profile3.jpg"
        ]
        generation = self.helper.EncodePassword(data["password"])
        data["password"] = generation[0]["password"]
        data["key_pass"] = generation[0]["key_pass"]
        data["iv"] = generation[0]["iv"]
        data["profile_path"] = random.choice(profile)
        return self.request.inserer_donnees(self.table, data)
        
    
    def MailExiste(self, email):
        colonnes_a_selectionner = ["email"]
        conditions_de_filtrage = {"email": email}
        result = self.request.Select_from_table(self.table, colonnes_a_selectionner, conditions_de_filtrage)
        if result == None or result == [] or result == "" or result == ():
            return True

        return "Email qui existe déjà"
    
    def UserExiste(self, email):
        colonnes_a_selectionner = ["id", "nom", "email", "password", "key_pass", "iv", "profile_path"]
        conditions_de_filtrage = {"email": email}
        result = self.request.Select_from_table2(self.table, colonnes_a_selectionner, conditions_de_filtrage)
        
        return result
    
    # def Connexion(self, )
    
    def PasswordMitovy(self, password_form, vrai_password, key_pass, iv):
        mdpEncoder = self.helper.DecodePasswordVerification(password_form, key_pass, iv)
        return vrai_password == mdpEncoder.decode()