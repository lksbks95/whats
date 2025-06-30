from . import db

class Setting(db.Model):
    __tablename__ = 'settings'
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Setting {self.key}>'
