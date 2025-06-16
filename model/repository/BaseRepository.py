from sqlalchemy.orm import Session

class BaseRepository:
    def __init__(self, session: Session, model):
        self.session = session
        self.model = model

    def get(self, id):
        return self.session.get(self.model, id)

    def getAll(self):
        return self.session.query(self.model).all()

    def add(self, entity):
        self.session.add(entity)

    def update(self, entity):
        self.session.merge(entity)

    def delete(self, entity):
        self.session.delete(entity)

    def filter(self, **kwargs):
        return self.session.query(self.model).filter_by(**kwargs)

    def get_last_row(self):
        return self.session.query(self.model).order_by(self.model.time.desc()).first()
