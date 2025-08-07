
import pandas as pd
class RequetesServices :
    def __init__(self, mysql):
        self.mysql = mysql
        
    def inserer_donnees(self, table, data):
        try:
            conn = self.mysql.connection
            cursor = conn.cursor()

            # Obtenir les noms des colonnes de la table depuis la base de données
            cursor.execute(f"DESCRIBE {table}")
            table_columns = [column[0] for column in cursor.fetchall()]  # Utilisez [0] pour accéder à la première colonne

            # Filtrer les clés du dictionnaire pour inclure uniquement celles qui correspondent aux colonnes de la table
            filtered_data = {key: data[key] for key in data.keys() if key in table_columns}

            # Construction de la requête SQL préparée
            cols = ', '.join(filtered_data.keys())
            placeholders = ', '.join(['%s'] * len(filtered_data))
            insert_query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"

            # Paramètres de la requête préparée
            values = tuple(filtered_data.values())

            # Exécution de la requête préparée
            cursor.execute(insert_query, values)
            conn.commit()
            
            inserted_id = cursor.lastrowid
            cursor.close()
            return True, inserted_id
        except Exception as e:
            return False, str(e)
        
    def Select_from_table(self, table, columns=None, conditions=None):
        try:
            conn = self.mysql.connection
            cursor = conn.cursor()

            # Construction de la clause SELECT
            if columns is None:
                select_clause = "*"
            else:
                select_clause = ", ".join(columns)

            # Construction de la clause WHERE si des conditions sont fournies
            where_clause = ""
            values = ()
            if conditions:
                where_clause = "WHERE " + " AND ".join([f"{key}=%s" for key in conditions.keys()])
                values = tuple(conditions.values())
                
            select_query = f"SELECT {select_clause} FROM {table} {where_clause}"

            # Exécution de la requête
            cursor.execute(select_query, values)

            # Récupération des résultats
            results = cursor.fetchall()

            cursor.close()
            return results
        except Exception as e:
            print("Erreur lors de la requête SELECT :", str(e))
        return []

    def Select_from_table2(self, table, columns=None, conditions=None):
        try:
            conn = self.mysql.connection
            cursor = conn.cursor()

            # Construction de la clause SELECT
            if columns is None:
                select_clause = "*"
            else:
                select_clause = ", ".join(columns)

            # Construction de la clause WHERE si des conditions sont fournies
            where_clause = ""
            values = ()
            if conditions:
                where_clause = "WHERE " + " AND ".join([f"{key}=%s" for key in conditions.keys()])
                values = tuple(conditions.values())

            select_query = f"SELECT {select_clause} FROM {table} {where_clause}"

            # Exécution de la requête
            cursor.execute(select_query, values)

            # Récupération des résultats
            results = cursor.fetchall()

            # Récupération des noms de colonnes
            column_names = [desc[0] for desc in cursor.description]

            cursor.close()

            # Création du dictionnaire de résultats
            results_dict = {}
            for i, column_name in enumerate(column_names):
                results_dict[column_name] = [row[i] for row in results]

            return results_dict

        except Exception as e:
            print(f"Une erreur s'est produite : {str(e)}")
            return None
        
    def SelectAll(self, table):
        try:    
            conn = self.mysql.connection
            cursor = conn.cursor()
            query = f"SELECT * FROM {table}"
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            
            df = pd.DataFrame(result, columns=["id", "id_user", "parole_path", "langue", "prediction", "favori"])
            formatted_results = df.to_dict(orient="records")
                    
            return formatted_results
        except Exception as e:
            print(f"Une erreur s'est produite : {str(e)}")
            return str(e)
    def execute_query_and_return_json(self, table_name, selected_columns, columns_mapping, conditions=None, order_by=None):
        try:
            conn = self.mysql.connection
            cursor = conn.cursor()

            columns_str = ", ".join(selected_columns)
            query = f"SELECT {columns_str} FROM {table_name}"

            if conditions:
                conditions_str = " AND ".join(conditions)
                query += f" WHERE {conditions_str}"

            if order_by:
                order_by_str = ", ".join(order_by)
                query += f" ORDER BY {order_by_str}"

            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()

            df = pd.DataFrame(results, columns=columns_mapping.keys())
            df.rename(columns=columns_mapping, inplace=True)
            formatted_results = df.to_dict(orient="records")

            return formatted_results
        except Exception as e:
            print(f"Une erreur s'est produite : {str(e)}")
            return {"error": str(e)}
            
    def update_column_value(self, table_name, update_column, new_value, conditions=None):
        try:
            conn = self.mysql.connection
            cursor = conn.cursor()

            query = f"UPDATE {table_name} SET {update_column} = %s"

            if conditions:
                conditions_str = " AND ".join(conditions)
                query += f" WHERE {conditions_str}"

            cursor.execute(query, (new_value,))
            conn.commit()
            cursor.close()

            return {"success": f"The value of {update_column} has been updated to {new_value}"}
        except Exception as e:
            print(f"Une erreur s'est produite : {str(e)}")
            return {"error": str(e)}