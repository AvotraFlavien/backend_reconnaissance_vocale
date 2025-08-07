class FormServices : 
    def __init__(self, form = []):
        self.form = form
        
    def PresentKey(self, data = [], form = []):
        existeKey = []
        for cle in data.keys():
            for element in form : 
                if cle == element[0] : 
                    existeKey.append({cle : data[cle]})
            # break

        if existeKey == None or existeKey == [] : 
            return False
        return existeKey
    
    
    def VerifiedRequired(self, data,form = []) :
        for key, _, is_required in form:
            if is_required and key not in data:
                return (f"{key} est requis")
        return False
            
    def VerifiedForm(self, data) :
        VerifiedRequired = self.VerifiedRequired(data, self.form)
        if VerifiedRequired != False :
            return VerifiedRequired
        
        existKey = self.PresentKey(data, self.form)
        if existKey == False :
            return "Veillez compléter le formulaire"
        
        for item in existKey :
            for key, type, is_required in self.form :
                if key in item : 
                    print(item[key])
                    if not isinstance(item[key], type) : 
                        return f"{item} doit être de type {type}"
                    if is_required and item[key] == "":
                        return f"{item} ne doit pas être null"

        return True
    
    def VerificationPassword(self, password, confirmation):
        if len(password) < 8 :
            return f"Le mot de passe doit être plus de 8 caractères"
         
        elif password != confirmation :
            return "Bien confirmer votre mot de passe"
        
        else :
            return True