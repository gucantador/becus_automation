from datetime import datetime
from . import db


class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default="")
    tanque = db.Column(db.String(100), nullable=True)
    quantidade = db.Column(db.String(3), nullable=True)
    unidade = db.Column(db.String(100), nullable=False)
    capex = db.Column(db.String(50), nullable=True)
    cidade = db.Column(db.String(100), nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    link_google_drive = db.Column(db.String(255), nullable=False)
    becus_id = db.Column(db.String(100), nullable=False)
    bairro = db.Column(db.String(100), nullable=True)
    cnpj = db.Column(db.String(14), nullable=True)

    # novos campos
    estado = db.Column(db.String(2), nullable=True)  # SP, RJ, etc.
    cep = db.Column(db.String(20), nullable=True)
    numero = db.Column(db.String(20), nullable=True)
    logradouro = db.Column(db.String(255), nullable=True)

    projetos = db.relationship('Projeto', backref='cliente', lazy=True)

    def __repr__(self):
        return f"<Cliente {self.unidade} ({self.id})>"

    def to_dict(self, include_projetos=False):
        data = {
            "id": self.id,
            "tanque": self.tanque,
            "unidade": self.unidade,
            "capex": self.capex,
            "cidade": self.cidade,
            "observacoes": self.observacoes,
            "link_google_drive": self.link_google_drive,
            "becus_id": self.becus_id,
            "estado": self.estado,
            "cep": self.cep,
            "numero": self.numero,
            "logradouro": self.logradouro,
            "quantidade": self.quantidade,
            "cnpj": self.cnpj,
            "name": self.name
        }
        if include_projetos:
            data["projetos"] = [p.to_dict() for p in self.projetos]
        return data


class Projeto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    solicitacao = db.Column(db.Date, nullable=False)
    prazo = db.Column(db.Date, nullable=False)
    visita = db.Column(db.Date, nullable=True)
    desenhista = db.Column(db.String(100), nullable=True)
    timestamp_inicio = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    timestamp_final = db.Column(db.DateTime, nullable=True)
    revisor = db.Column(db.String(100), nullable=True)
    data_entrega = db.Column(db.Date, nullable=False)
    art = db.Column(db.Boolean, nullable=True)
    status = db.Column(db.String(50), nullable=True)

    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)

    # novos relacionamentos
    correcoes = db.relationship('Correcao', backref='projeto', lazy=True, cascade="all, delete-orphan")
    observacoes = db.relationship('Observacao', backref='projeto', lazy=True, cascade="all, delete-orphan")
    history = db.relationship('History', backref='project', lazy=True)

    def __repr__(self):
        return f"<Projeto {self.solicitacao} ({self.id})>"

    def to_dict(self, include_cliente=True, include_history=False, include_correcoes=True, include_observacoes=True):
        data = {
            "id": self.id,
            "solicitacao": self.solicitacao,   # string normal
            "prazo": self.prazo.isoformat() if self.prazo else None,   # Date -> string ISO
            "visita": self.visita,  # string normal
            "desenhista": self.desenhista,
            "timestamp_inicio": self.timestamp_inicio.isoformat() if self.timestamp_inicio else None,
            "timestamp_final": self.timestamp_final.isoformat() if self.timestamp_final else None,
            "revisor": self.revisor,
            "data_entrega": self.data_entrega.isoformat() if self.data_entrega else None,  # Date -> string ISO
            "art": self.art,
            "status": self.status,
            "cliente_id": self.cliente_id,
        }
        if include_cliente:
            data["cliente"] = self.cliente.to_dict()
        if include_history:
            data["history"] = [h.to_dict(include_user=True) for h in self.history]
        if include_correcoes:
            data["correcoes"] = [c.to_dict() for c in self.correcoes]
        if include_observacoes:
            data["observacoes"] = [o.to_dict(include_user=True) for o in self.observacoes]
        return data


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100))
    role = db.Column(db.String(50))
    password = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<User {self.name} {self.last_name or ''} ({self.id})>"

    def to_dict(self, include_history=False):
        data = {
            "id": self.id,
            "name": self.name,
            "last_name": self.last_name,
            "role": self.role,
            "password": self.password,
            "username": self.username
        }
        if include_history:
            data["history"] = [h.to_dict() for h in self.history]
        return data


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projeto.id'), nullable=False)

    user = db.relationship('User', backref='history')

    def __repr__(self):
        return f"<History {self.action} ({self.timestamp})>"

    def to_dict(self, include_user=False, include_project=False):
        data = {
            "id": self.id,
            "action": self.action,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "user_id": self.user_id,
            "project_id": self.project_id
        }
        if include_user:
            data["user"] = self.user.to_dict()
        if include_project:
            data["project"] = self.project.to_dict()
        return data
    

class Unidades(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


    def __repr__(self):
        return f"<Unidade {self.name} ({self.id})>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }


class Correcao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.Text, nullable=False)
    status = db.Column(db.Boolean, default=False, nullable=False)

    projeto_id = db.Column(db.Integer, db.ForeignKey('projeto.id'), nullable=False)

    def __repr__(self):
        return f"<Correcao {self.descricao[:20]}... ({'OK' if self.corrigida else 'PENDENTE'})>"

    def to_dict(self):
        return {
            "id": self.id,
            "descricao": self.descricao,
            "status": self.status
        }


class Observacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comentario = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    projeto_id = db.Column(db.Integer, db.ForeignKey('projeto.id'), nullable=False)

    user = db.relationship('User')

    def __repr__(self):
        return f"<Observacao {self.comentario[:20]}... ({self.id})>"

    def to_dict(self, include_user=False):
        data = {
            "id": self.id,
            "comentario": self.comentario,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id
        }
        if include_user:
            data["user"] = self.user.to_dict()
        return data