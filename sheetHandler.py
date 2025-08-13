import pandas as pd

class sheetHandler():

    def __init__(self, row):
        self.row = row
        self.documento_cliente_coluna = 0
        self.razao_social_cliente_coluna = 1
        self.data_prevista_inicio_coluna = 2
        self.cep_coluna = 3
        self.logradouro_coluna = 4
        self.numero_coluna = 5
        self.bairro_coluna = 6
        self.codigo_becus_coluna = 7

        self.sheet_path = 'assets/art_sheet.xlsx'
        self.df = self.load_df()

    def load_df(self):
        df = pd.read_excel(self.sheet_path)
        df.dropna(how='all', inplace=True)
        return df

    def get_documento_cliente(self):
        return self.df.iloc[self.row, self.documento_cliente_coluna]
    
    def get_razao_social_cliente(self):
        return self.df.iloc[self.row, self.razao_social_cliente_coluna]
    
    def get_data_prevista_inicio(self):
        return self.df.iloc[self.row, self.data_prevista_inicio_coluna]
    
    def get_cep(self):
        return self.df.iloc[self.row, self.cep_coluna]
    
    def get_logradouro(self):
        return self.df.iloc[self.row, self.logradouro_coluna]
    
    def get_numero(self):
        return self.df.iloc[self.row, self.numero_coluna]
    
    def get_bairro(self):
        return self.df.iloc[self.row, self.bairro_coluna]

    def get_codigo_becus(self):
        return self.df.iloc[self.row, self.codigo_becus_coluna]
    
    def update_row(self):
        if self.row + 1 < len(self.df):
            # A próxima linha existe (índice válido)
            if pd.notna(self.df.iloc[self.row + 1, 0]):
                # E a célula da coluna 0 não está vazia
                self.row += 1
                return True
        return False


